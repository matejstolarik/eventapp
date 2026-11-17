"""
Deterministic event classification — layer 1 (no LLM).

Rule order (stops at the first rule that sets formats):
  1. override  – manual override from data/overrides.json (highest priority)
  2. source    – section from event source mapped to a format
  3. keyword   – keywords/patterns in event title mapped to concert/dj
  4. fallback  – 'music' if the event is known to be a music event but
                 concert/dj could not be determined; else leave formats empty

Venue defaults were removed (task 015): venue info is now AI context, not
a rule.  Events layer 1 cannot classify go to classify_ai (layer 2).

Configuration lives in the dicts below — no format values are hard-coded
inside the rule logic.

classification field:
  {"method": "manual"|"source"|"keyword", "confidence": float}
  null when layer 1 did not classify (AI layer will handle it)
"""

import re
import logging

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config: section → format
# None means "music event, live/dj still undetermined" — passes to next rules.
# ---------------------------------------------------------------------------
SECTION_MAP: dict[str, str | None] = {
    # music sections — format undetermined at this stage
    "hudba": None,
    "music": None,
    # explicit format sections (e.g. Roxy data-hashtags used as section)
    "concert": "concert",
    "dj": "dj",
    # theatre
    "divadlo": "theatre",
    "theatre": "theatre",
    "premiéra": "theatre",
    # film
    "film": "film",
    # quiz
    "kvíz": "quiz",
    "quiz": "quiz",
    # opening / vernissage
    "vernisáž": "opening",
    "opening": "opening",
    # dance
    "tanec": "dance",
    "dance": "dance",
    # talk (lecture, debate, discussion, book reading)
    "debata": "talk",
    "debate": "talk",
    "přednáška": "talk",
    "lecture": "talk",
    "konference": "talk",
    "conference": "talk",
    # workshop
    "workshop": "workshop",
    # stand-up (task 065: format renamed from "comedy")
    "comedy": "stand-up",
    "stand-up": "stand-up",
    # other
    "off-program": "other",
    "performance": "other",
}

# ---------------------------------------------------------------------------
# Config: keyword patterns for concert / dj detection in event title
# Case-insensitive.  At most one side must match; conflict → no assignment.
# ---------------------------------------------------------------------------
CONCERT_PATTERNS: list[str] = [
    r"\blive\b",          # "live", "LIVE" (keyword; format renamed to concert)
    r"/live\b",           # "/Live", "/LIVE"
    r"\(live\)",          # "(live)"
    r"\bF2\s+LIVE\b",     # "F2 LIVE" (Fuchs2 specific)
    r"\bkřest\b",         # album release show
    r"\bsupport\b",       # support act implies live headliner
    r"\btour\b",          # tour = live
    r"\+\s*kapela\b",     # "+ kapela"
]

DJ_PATTERNS: list[str] = [
    r"\bdj\s+set\b",      # "DJ set", "dj set"
    r"\bb2b\b",           # B2B
    r"\bw/",              # "w/" (with, DJ context, e.g. "Artist w/ DJ")
    r"\bresidents\b",     # residents night
    r"\bresidency\b",     # residency
    r"\ball\s+night\s+long\b",
    r"\brave\b",          # rave events = DJ
    r"\bnights?\b",       # "night" / "nights" in club context
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Renamed format codes (old -> new): task 065 comedy -> stand-up.  Applied to
# previous events, model answers, manual values and the output.
RENAMED_FORMATS = {"comedy": "stand-up"}


def rename_formats(fmts: list | None) -> list:
    out = []
    for f in fmts or []:
        f = RENAMED_FORMATS.get(f, f)
        if f not in out:
            out.append(f)
    return out


def rename_format_fields(ev: dict) -> dict:
    """formats + primary_format with renamed codes (new dict if changed)."""
    fmts, pf = ev.get("formats"), ev.get("primary_format")
    if not (set(fmts or []) & set(RENAMED_FORMATS) or pf in RENAMED_FORMATS):
        return ev
    ev = dict(ev)
    if fmts is not None:
        ev["formats"] = rename_formats(fmts)
    if pf in RENAMED_FORMATS:
        ev["primary_format"] = RENAMED_FORMATS[pf]
    return ev


def classify_events(
    events: list[dict],
    venues: list[dict],
    overrides: list[dict] | None = None,
) -> list[dict]:
    """Classify formats for all events in-place and return them."""
    venues_map = {v["id"]: v for v in venues}
    overrides = overrides or []

    for event in events:
        venue = venues_map.get(event["venue_id"], {})
        _classify_one(event, venue, overrides)

    return events


def _classify_one(event: dict, venue: dict, overrides: list[dict]) -> None:
    """Apply classification rules to a single event dict (mutates in-place)."""
    # Skip events that already have formats set by an adapter
    if event.get("formats"):
        if not event.get("classification"):
            event["classification"] = {"method": "source", "confidence": 1.0}
        return

    title = event.get("title", "")
    # Collect sections from all sources (deduplicated, lowercased)
    sections = list(dict.fromkeys(
        s.get("section", "").lower()
        for s in event.get("sources", [])
        if s.get("section")
    ))
    section = sections[0] if sections else None
    venue_id = event.get("venue_id", "")
    start_time = event.get("start_time")

    # --- Rule 0: manual override -------------------------------------------
    fmt_list, matched_override = _apply_override(event, overrides)
    if matched_override:
        event["formats"] = fmt_list
        event["classification"] = {"method": "manual", "confidence": 1.0}
        return

    # Track whether we know this is a music event (for fallback)
    is_music_event = False

    # --- Rule 1: section from source ----------------------------------------
    if section and section in SECTION_MAP:
        mapped = SECTION_MAP[section]
        if mapped is not None:
            # Definite non-music format (theatre, film, quiz, etc.)
            event["formats"] = [mapped]
            event["classification"] = {"method": "source", "confidence": 1.0}
            return
        # mapped is None → confirmed music event, live/dj undetermined
        is_music_event = True

    # If no section but venue only does music → assume music
    if not is_music_event and _is_music_only_venue(venue):
        is_music_event = True

    # --- Rule 2: keywords in title ------------------------------------------
    concert_hit = _matches_any(title, CONCERT_PATTERNS)
    dj_hit = _matches_any(title, DJ_PATTERNS)

    if concert_hit and not dj_hit:
        event["formats"] = ["concert"]
        event["classification"] = {"method": "keyword", "confidence": 0.9}
        return
    if dj_hit and not concert_hit:
        event["formats"] = ["dj"]
        event["classification"] = {"method": "keyword", "confidence": 0.9}
        return
    if concert_hit and dj_hit:
        # Both signals present — event is both a concert and a club night
        event["formats"] = ["concert", "dj"]
        event["classification"] = {"method": "keyword", "confidence": 0.8}
        return

    # --- Rule 3 (venue defaults) removed in task 015 ------------------------
    # Venue context is now passed to AI layer instead of being used as a rule.

    # --- Rule 4: fallback ----------------------------------------------------
    if is_music_event:
        event["formats"] = ["music"]
        # No classification set — AI layer will determine the actual format
    # else: formats stays empty, classification stays null


MUSIC_FORMATS = frozenset({"concert", "dj", "music", "party"})


def venue_genre_ids(events: list[dict]) -> set[str]:
    """Task 063: ids of events whose genres come from the venue (layer 1:
    ``classification.method`` manual / source with genres).  Computed before
    the AI layers; their genres win over AI genres (unchanged rule), even
    when the AI type now wins over the venue category (docs/ai-rules.md B7)."""
    return {e["id"] for e in events if e.get("genres")
            and (e.get("classification") or {}).get("method") in ("manual", "source")}


def apply_commercial_clubs(events: list[dict], venues: list[dict]) -> list[dict]:
    """Task 053: in a venue with ``commercial_club: true`` every music event is
    a party.  Deterministic venue rule (layer 1, no AI decision).

    Runs after the AI layer so that AI still supplies genres for these events
    but cannot remove ``party``.  "music" is replaced by "party"; concert/dj
    stay as formats.  Task 058 (docs/ai-rules.md B5): ``party`` is always
    added, ``primary_format`` = "party" unless the AI decided "dj" (a known,
    named DJ as headliner, e.g. SLVL at EPIC) -- then "dj" stays primary.
    Manual overrides are left untouched.
    """
    commercial = {v["id"] for v in venues if v.get("commercial_club") is True}
    for ev in events:
        if ev.get("venue_id") not in commercial:
            continue
        if (ev.get("classification") or {}).get("method") == "manual":
            continue
        fmts = ev.get("formats") or []
        if not any(f in MUSIC_FORMATS for f in fmts):
            continue
        new = [f for f in fmts if f != "music"]
        if "party" not in new:
            new.append("party")
        ev["formats"] = new
        by_ai = (ev.get("classification") or {}).get("method") in ("llm", "llm+web")
        if not (by_ai and ev.get("primary_format") == "dj" and "dj" in new):
            ev["primary_format"] = "party"
    return events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_override(event: dict, overrides: list[dict]) -> tuple[list[str], bool]:
    """Return (formats_list, True) if an override matches, else ([], False)."""
    eid = event.get("id", "")
    title = event.get("title", "").lower()
    venue_id = event.get("venue_id", "")

    for ov in overrides:
        if "id" in ov and ov["id"] == eid:
            return _formats_from_override(ov), True
        if "venue_id" in ov and ov["venue_id"] == venue_id:
            needle = ov.get("title_contains", "")
            if needle and needle.lower() in title:
                return _formats_from_override(ov), True
    return [], False


def _formats_from_override(ov: dict) -> list[str]:
    """Extract formats list from override dict."""
    fmts = ov.get("formats", [])
    if isinstance(fmts, list):
        return fmts
    if isinstance(fmts, str):
        return [fmts] if fmts else []
    return []


def _is_music_only_venue(venue: dict) -> bool:
    """True for venues that only do music events (no mixed programs)."""
    types = venue.get("type") or []
    music_types = {"concert-club", "dance-club", "dj-bar", "jazz-club", "concert-hall"}
    culture_types = {"culture-center", "cinema"}
    has_music = any(t in music_types for t in types)
    has_culture = any(t in culture_types for t in types)
    # Pure music venue = has music type but NOT a culture center / cinema
    return has_music and not has_culture


def _matches_any(text: str, patterns: list[str]) -> bool:
    """Return True if text matches any of the regex patterns (case-insensitive)."""
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False
