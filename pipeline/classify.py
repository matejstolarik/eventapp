"""
Deterministic event classification — layer 1 (no LLM).

Rule order (stops at the first rule that sets formats):
  1. override  – manual override from data/overrides.json (highest priority)
  2. source    – section from event source mapped to a format
  3. keyword   – keywords/patterns in event title mapped to live/dj
  4. venue     – venue+section default; time-based rule for mixed venues
  5. fallback  – 'music' if the event is known to be a music event but
                 live/dj could not be determined; else leave formats empty

Configuration lives in the dicts below — no format values are hard-coded
inside the rule logic.

classification field:
  {"method": "manual"|"source"|"keyword"|"venue", "confidence": float|null}
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
    # other
    "tanec": "other",
    "dance": "other",
    "debata": "other",
    "debate": "other",
    "přednáška": "other",
    "lecture": "other",
    "workshop": "other",
    "konference": "other",
    "conference": "other",
    "off-program": "other",
    "performance": "other",
}

# ---------------------------------------------------------------------------
# Config: keyword patterns for live / dj detection in event title
# Case-insensitive.  At most one side must match; conflict → no assignment.
# ---------------------------------------------------------------------------
LIVE_PATTERNS: list[str] = [
    r"\blive\b",          # "live", "LIVE"
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
# Config: venue + section defaults
# "*" = catch-all section.  Entries here set the final format when rules 1–3
# have not determined live/dj yet.
# ---------------------------------------------------------------------------
VENUE_DEFAULTS: dict[str, dict[str, str]] = {
    # Concerts, all formats; section "hudba" → live; other sections from SECTION_MAP
    "palac-akropolis": {
        "hudba": "live",
        "divadlo": "theatre",
        "off-program": "other",
    },
    # Concerts and theatre
    "meetfactory": {
        "hudba": "live",
        "divadlo": "theatre",
    },
    # Only concerts
    "forum-karlin": {"*": "live"},
    # Concerts, theatre, film, dance, talks, workshops
    "archa-plus": {
        "hudba": "live",
        "divadlo": "theatre",
        "film": "film",
        "tanec": "other",
        "debata": "other",
        "workshop": "other",
        "přednáška": "other",
        "performance": "other",
        "premiéra": "theatre",
    },
    # Jazz and experimental concerts only
    "citarna-unijazz": {"*": "live"},
    # DJ club; occasional live events detected by LIVE_PATTERNS above
    "fuchs2": {"*": "dj"},
    # DJ club; occasional live events detected by LIVE_PATTERNS above
    "cross-club": {"*": "dj"},
    # Kasárna: outdoor concerts, no DJ nights observed → live for all music
    "kasarna-karlin": {"*": "live"},
    # Bike Jesus: mixed (indie/shoegaze concerts + techno/house nights)
    # → time-based rule in VENUE_TIME_RULES; no catch-all default here
    "bike-jesus": {},
}

# ---------------------------------------------------------------------------
# Config: time-based rule for venues without a clear section default.
# start_time < threshold → "live";  >= threshold → "dj".
# Pattern: Prague concerts 19–21 h, DJ nights from 22 h.
# ---------------------------------------------------------------------------
VENUE_TIME_RULES: dict[str, str] = {
    "bike-jesus": "22:00",
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
    fmt, matched_override = _apply_override(event, overrides)
    if fmt is not None:
        event["formats"] = [fmt] if fmt else []
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
    live_hit = _matches_any(title, LIVE_PATTERNS)
    dj_hit = _matches_any(title, DJ_PATTERNS)

    if live_hit and not dj_hit:
        event["formats"] = ["live"]
        event["classification"] = {"method": "keyword", "confidence": 0.9}
        return
    if dj_hit and not live_hit:
        event["formats"] = ["dj"]
        event["classification"] = {"method": "keyword", "confidence": 0.9}
        return
    if live_hit and dj_hit:
        # Conflict — both keywords present; leave for venue rule
        pass

    # --- Rule 3: venue defaults + time rule ---------------------------------
    venue_defaults = VENUE_DEFAULTS.get(venue_id, {})
    # Try section-specific default, then catch-all
    fmt_venue = venue_defaults.get(section) if section else None
    if fmt_venue is None:
        fmt_venue = venue_defaults.get("*")

    if fmt_venue is not None:
        if fmt_venue in ("theatre", "film", "quiz", "opening", "other"):
            event["formats"] = [fmt_venue]
        elif fmt_venue in ("live", "dj"):
            event["formats"] = [fmt_venue]
        else:
            event["formats"] = [fmt_venue]
        event["classification"] = {"method": "venue", "confidence": 0.7}
        return

    # Time-based rule for mixed venues (e.g. bike-jesus)
    threshold = VENUE_TIME_RULES.get(venue_id)
    if threshold and start_time:
        if start_time < threshold:
            event["formats"] = ["live"]
            event["classification"] = {"method": "venue", "confidence": 0.6}
            return
        else:
            event["formats"] = ["dj"]
            event["classification"] = {"method": "venue", "confidence": 0.6}
            return

    # --- Rule 4: fallback ----------------------------------------------------
    if is_music_event:
        event["formats"] = ["music"]
        event["classification"] = {"method": "venue", "confidence": 0.5}
    # else: formats stays empty, classification stays null


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_override(event: dict, overrides: list[dict]):
    """Return (formats_value, True) if an override matches, else (None, False).

    formats_value may be a string (single format) or list, or [] for empty.
    """
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
    return None, False


def _formats_from_override(ov: dict):
    """Extract the first format string from override dict."""
    fmts = ov.get("formats", [])
    if isinstance(fmts, list) and fmts:
        return fmts[0]
    return ""


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
