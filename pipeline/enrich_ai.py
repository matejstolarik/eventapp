"""
AI enrichment with web search in the daily run (task 054).

For events in the next WINDOW_DAYS (180) days that are new or whose title changed
(cache: previous events.json, `enrichment.run.checked_at` + same title), one
AI request per event with web search:
  - verifies type (formats, primary_format) and genres,
  - fills a missing price, start time, artists, Spotify artist link,
  - writes a description in Czech + Slovak + English translation
    (`descriptions`), facts only, own words.

The event page text already fetched by detail_enrich is in the prompt; the
model searches only for what is missing (max MAX_SEARCHES_PER_EVENT).

Rules enforced in code (docs/data-model.md, "AI doplnenie"):
  - Values from the venue source win: AI fills only empty fields.  When the
    source later provides a value, the AI value and its enrichment entry go.
  - An ai_web value without source_url is not stored.  ra.co is never a source.
  - Price: one GET on its source_url; stored only if the page text contains
    the amount (or the free-entry word) AND the event title or main artist.
  - Spotify URL only if it appeared in the search results.
  - Monthly limit MONTHLY_SEARCH_LIMIT web searches (state["ai_searches"],
    kept between runs in site/pipeline_state.json).  Once reached, uncached
    events are skipped (processed next month).
  - Any provider error -> warning, pipeline continues without enrichment.

Provider: ENRICH_PROVIDER = "claude" (default).  "gemini" is refused in the
daily run (task 060): the Gemini API terms do not allow our use of Grounding
with Google Search (caching / analysing results, taking links from them).
The _Gemini2 class stays for the prompts and the research store (task 061).
"""

import concurrent.futures
import datetime
import html
import json
import logging
import os
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.request

import requests

from pipeline.classify_ai import VALID_FORMATS, VALID_GENRES
from pipeline.fetch import USER_AGENT, _rate_limit
from pipeline.ai_rules import (DECIDE_PROMPT, RESEARCH_PROMPT, RESEARCH_RETRY, RULES_ALL,
                               TRANSLATE_PROMPT)
from pipeline.ai_guards import (genre_supported, price_supported, strip_names, strip_no_info,
                                venue_mentions)
from pipeline.genres import (FILM_GENRES, STAGE_GENRES, TALK_GENRES, finalize_genres, map_genre,
                             talk_genres_from_text)
from pipeline.price import parse_price

log = logging.getLogger(__name__)

# task 085 (Matej 2026-11-20): full AI enrichment for the whole app window
# (180 days, was 60); an event enriched more than RECHECK_DAYS before its date
# that still misses price / genres / time is enriched once more when it gets
# within RECHECK_DAYS days (price and line-up are often published later).
WINDOW_DAYS = 180
RECHECK_DAYS = 60
_MUSIC_FORMATS = {"concert", "dj", "party", "music"}
MONTHLY_SEARCH_LIMIT = 400
MAX_SEARCHES_PER_EVENT = 3
MAX_WORKERS = 4
RUN_TIMEOUT_S = int(os.environ.get("ENRICH_TIMEOUT_S", "").strip() or "1500")
MAX_ERRORS_IN_A_ROW = 5
BLOCKED_DOMAINS = ["ra.co", "instagram.com"]   # task 058: Instagram never a source

# Genre lists and mapping: pipeline/genres.py (task 058 part 3).
_MUSIC_FORMATS = {"concert", "dj", "party", "music"}
_STAGE_FORMATS = {"theatre", "dance"}

CLAUDE_MODEL = "claude-haiku-5-5"
CLAUDE_PRICES = (0.10 / 1e6, 0.50 / 1e6, 10.0 / 1000)   # in, out per token; per search

_SPOTIFY_RE = re.compile(r"^https://open\.spotify\.com/(?:intl-[a-z]+/)?artist/[A-Za-z0-9]{22}")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_BANNED = re.compile(
    r"nezmeškejte|nenechte si|legendární|nezapomenuteln|unikátní zážitek|"
    r"nezmeškajte|nenechajte si|legendárn|nezabudnuteľn|jedinečný zážitok|"
    r"don't miss|unforgettable|legendary|unique experience", re.I)
_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")

SYSTEM_PROMPT = f"""You enrich data about one event at a Prague venue. Accuracy matters more than completeness: leave a field empty (null / []) when you are not sure. Never invent facts, dates, prices or URLs.

RESEARCH (docs/ai-rules.md A): read the EVENT DATA and EVENT PAGE TEXT, then search (at most {MAX_SEARCHES_PER_EVENT} searches): all performers; about every main performer who it is, where from, how they present themselves (band / DJ / producer / theatre company …), genre, releases; the event page (venue website, public Facebook event, presale) for price and time. Type, genres and description come from the SAME findings. Never use Instagram or ra.co (Resident Advisor).

{RULES_ALL}

Every source_url must be a real page you saw (the event page or a search result). Call report_enrichment exactly once at the end."""

_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "formats": {"type": "array", "items": {"type": "string", "enum": sorted(VALID_FORMATS)}},
        "primary_format": {"type": ["string", "null"]},
        "party_reason": {"type": ["string", "null"]},
        "type_source_url": {"type": ["string", "null"]},
        "type_confidence": {"type": "number"},
        "type_reason": {"type": ["string", "null"]},
        "genres": {"type": "array", "items": {"type": "string"},
                   "description": "ordered, main genre first"},
        "genre_facts": {"type": "object", "additionalProperties": {"type": "string"},
                        "description": "genre -> the found fact that supports it"},
        "needs_review": {"type": "boolean"},
        "genre_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "raw": {"type": "string"},
                    "kind": {"type": "string", "enum": ["music", "film", "stage"]},
                    "maps_to": {"type": ["string", "null"]},
                },
                "required": ["raw", "kind"],
            },
        },
        "artists": {"type": "array", "items": {"type": "string"}},
        "artists_source_url": {"type": ["string", "null"]},
        "spotify": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"artist": {"type": "string"}, "url": {"type": "string"}},
                "required": ["artist", "url"],
            },
        },
        "price": {"type": ["string", "null"]},
        "price_source_url": {"type": ["string", "null"]},
        "start_time": {"type": ["string", "null"]},
        "start_time_source_url": {"type": ["string", "null"]},
        "descriptions": {
            "type": ["object", "null"],
            "properties": {"cs": {"type": "string"}, "sk": {"type": "string"},
                           "en": {"type": "string"}},
        },
        "description_source_urls": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["formats", "primary_format", "genres", "type_confidence", "artists",
                 "price", "start_time", "descriptions"],
}

_REPORT_TOOL = {
    "name": "report_enrichment",
    "description": "Report the final enrichment result for the event. Call exactly once, at the end.",
    "input_schema": _RESULT_SCHEMA,
}


# ---------------------------------------------------------------------------
# Selection + cache
# ---------------------------------------------------------------------------

def in_window(ev: dict, today: str, days: int = WINDOW_DAYS) -> bool:
    end = (datetime.date.fromisoformat(today) + datetime.timedelta(days=days)).isoformat()
    return today <= ev.get("date", "") <= end and ev.get("status") != "cancelled"


def cached_enrichment(ev: dict, previous: dict) -> dict | None:
    """Enrichment from the previous run if the event was enriched with the
    same title; else None (needs a new AI request)."""
    prev = previous.get(ev["id"])
    if not prev:
        return None
    enr = prev.get("enrichment") or {}
    if not (enr.get("run") or {}).get("checked_at"):
        return None
    if prev.get("title") != ev.get("title"):
        return None
    return {"enrichment": enr, "prev": prev}


def needs_recheck(ev: dict, c: dict | None, today: str) -> bool:
    """Task 085: cached event to be enriched once more (see RECHECK_DAYS).

    True when the event is now within RECHECK_DAYS days, was enriched more
    than RECHECK_DAYS days before its date, was not re-checked yet
    (run.rechecked_from) and misses a price, genres (music events) or any
    time.  After the new run checked_at is within RECHECK_DAYS of the date,
    so it never repeats."""
    if not c:
        return False
    run = (c["enrichment"].get("run") or {})
    if run.get("rechecked_from"):
        return False
    try:
        date = datetime.date.fromisoformat(ev.get("date", ""))
        checked = datetime.date.fromisoformat(run.get("checked_at", ""))
        now = datetime.date.fromisoformat(today)
    except ValueError:
        return False
    if (date - now).days > RECHECK_DAYS or (date - checked).days <= RECHECK_DAYS:
        return False
    prev = c["prev"]
    no_price = not (ev.get("price_text") or prev.get("price_text") or ev.get("free")
                    or prev.get("free"))
    music = bool(_MUSIC_FORMATS & set(prev.get("formats") or ev.get("formats") or []))
    no_genres = music and not (prev.get("genres") or ev.get("genres"))
    no_time = not (ev.get("start_time") or prev.get("start_time")
                   or ev.get("doors_time") or prev.get("doors_time"))
    return no_price or no_genres or no_time


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

def build_prompt(ev: dict, venue: dict, page_text: str | None) -> str:
    src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
    orig = ev.get("description") if ev.get("description_source") != "ai" else None
    lines = [
        "EVENT DATA",
        f"Title: {ev.get('title')}",
        f"Venue: {venue.get('name', ev['venue_id'])} (Prague)"
        + (f", web {venue['website']}" if venue.get("website") else ""),
        f"Date: {ev.get('date')}",
        f"Start time: {ev.get('start_time') or '(missing)'}",
        f"Current formats: {ev.get('formats') or []}",
        f"Current genres: {ev.get('genres') or []}",
        f"Artists: {ev.get('artists') or '(missing)'}",
        f"Price: {ev.get('price_text') or '(missing)'}",
        f"Event page: {src or '(none)'}",
        f"Original description: {orig or '(missing)'}",
    ]
    if (ev.get("classification") or {}).get("method") == "manual":
        # task 060: known series / manual fix - do not spend searches on type and genres
        lines.append("Type and genres are FIXED by manual data: do not search for them and return "
                     "the current formats and genres unchanged; search only for the performers "
                     "of this evening and its description.")
    if page_text:
        lines += ["", "EVENT PAGE TEXT (fetched today)", page_text[:5000]]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _host(url) -> str:
    return re.sub(r"^https?://", "", str(url or "")).split("/")[0].lower()


def blocked(url) -> bool:
    h = _host(url)
    return any(h == d or h.endswith("." + d) for d in BLOCKED_DOMAINS)


def _ok_url(url) -> bool:
    return bool(url) and str(url).startswith("http") and not blocked(url)


def canon_url(url) -> str:
    u = re.sub(r"^https?://(www\.)?", "", str(url or "").strip().lower())
    return u.split("#")[0].rstrip("/")


def _clean_text(text) -> str | None:
    if not isinstance(text, str):
        return None
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def description_problems(text: str, names: list[str] | None = None) -> list[str]:
    """names: event title + artists; a '!' inside them (FIRE!) is no problem (task 062)."""
    probs = []
    if "!" in strip_names(text, names or []):
        probs.append("exclamation mark")
    if _EMOJI.search(text):
        probs.append("emoji")
    m = _BANNED.search(text)
    if m:
        probs.append(f"advertising phrase '{m.group(0)}'")
    return probs


def own_genre_kind(fmts) -> str | None:
    """Genre list of an event type: music / film / stage, None for others."""
    fmts = set(fmts or [])
    if fmts & _MUSIC_FORMATS:
        return "music"
    if "film" in fmts:
        return "film"
    return "stage" if fmts & (_STAGE_FORMATS | {"performance"}) else None


def genres_from_raw(raw_genres: list, raw_cands: list, genre_facts: dict | None,
                    own_kind: str | None, research_text: str | None, aliases: dict | None,
                    dropped: list, quote_fallback: bool = False,
                    trusted: set | None = None) -> tuple[list, list]:
    """Raw genre names of the model -> (our genres, genre_candidates).

    trusted: genres validated in an earlier run that keep their name (no
    second guard check; the venue page text may not be at hand).
    quote_fallback: a genre without its own genre_facts key takes all quotes
    (re-application to stored results, task 065: candidates had no quotes)."""
    # task 058: genres in order (main first); raw names are mapped only through
    # spelling variants + approved aliases, never to a parent genre.
    gens, cands, seen_raw = [], [], set()
    raw_of: dict = {}          # our genre -> raw names that mapped to it

    def add_raw(rawname, kind):
        rawname = _clean_text(rawname)
        if not rawname or (rawname.lower(), kind) in seen_raw:
            return
        seen_raw.add((rawname.lower(), kind))
        if kind is None:
            # task 065: an event without a music / film / stage type (talk,
            # other): a list genre counts as music (Jazzmánie -> jazz, before
            # 065 a "jazz" candidate with maps_to null); an unmapped name is no
            # proposal for any list ("educational narrative adventure game"
            # was a music candidate)
            mapped = map_genre(rawname, "music", aliases)
            if not mapped:
                dropped.append(f"genre {rawname.lower()}: event type has no genre list")
                return
            kind = "music"
        else:
            mapped = map_genre(rawname, kind, aliases)
        if not mapped and kind in ("film", "stage"):
            # task 058: culture events with musicians (rap musical Spitfire
            # Company & PAST) may also carry music genres
            mapped = map_genre(rawname, "music", aliases)
            kind = "music" if mapped else kind
        if mapped and set(mapped) <= TALK_GENRES:
            # task 078 (ai-rules C10): talk genres come only from phrases in the
            # event text / research (apply_talk_genres), never from the model
            dropped.append(f"genre {rawname.lower()}: talk genre only from text")
            return
        mapped = [g for g in mapped if g not in TALK_GENRES]
        if kind in (own_kind, "music") and mapped and (own_kind or kind == "music"):
            for g in mapped:
                raw_of.setdefault(g, []).append(rawname.lower())
                if g not in gens:
                    gens.append(g)
            if [rawname.lower()] != mapped:
                cands.append({"raw": rawname.lower(), "kind": kind, "maps_to": mapped[0]})
        elif not mapped:
            cands.append({"raw": rawname.lower(), "kind": kind or "music", "maps_to": None})

    for g in raw_genres:
        if isinstance(g, str):
            add_raw(g, own_kind)
    for c in raw_cands:
        kind = (c or {}).get("kind") if (c or {}).get("kind") in ("music", "film", "stage") else "music"
        add_raw((c or {}).get("raw"), kind)
    # task 062: every genre needs a quote with its name (ai-rules C2, C3)
    quotes = {k.lower(): v for k, v in (genre_facts or {}).items()}
    kept = []
    for g in gens:
        keys = [g, g.replace("-", " ")] + raw_of.get(g, [])
        quote = " ".join(quotes[k] for k in dict.fromkeys(keys) if k in quotes)
        if not quote and quote_fallback:
            quote = " ".join(quotes.values())
        if g in (trusted or ()):
            kept.append(g)
            continue
        ok_g, why = genre_supported(g, quote, research_text, aliases)
        if ok_g:
            kept.append(g)
        else:
            dropped.append(f"genre {g}: {why}")
    cands = [c for c in cands if c["maps_to"] is None or c["maps_to"] in kept]
    return finalize_genres(kept), cands     # task 065: C7, C8


def validate(raw: dict, ev: dict, seen_urls: set[str] | None,
             aliases: dict | None = None, allowed_urls: set[str] | None = None,
             research_text: str | None = None, venue: dict | None = None) -> dict:
    """Apply the rules to a raw model result -> clean dict + 'dropped'.

    aliases: approved raw genre -> our genre (data/genre_aliases.json).
    allowed_urls: if given (Gemini two-step), every source URL must be one of
    them (resolved search sources + event page), compared by canon_url().
    research_text: step-1 facts + venue page text (two-step providers); genres
    and the price need support in it (task 062, pipeline/ai_guards.py)."""
    allowed = None if allowed_urls is None else {canon_url(u) for u in allowed_urls}

    def ok(url) -> bool:
        return _ok_url(url) and (allowed is None or canon_url(url) in allowed)
    aliases = {k.lower(): v for k, v in (aliases or {}).items()}
    dropped: list[str] = []
    out: dict = {}

    from pipeline.classify import RENAMED_FORMATS, rename_formats
    fmts = [f for f in rename_formats(raw.get("formats")) if f in VALID_FORMATS]
    if "party" in fmts and not _clean_text(raw.get("party_reason")):
        dropped.append("party: no party_reason")
        fmts = [f for f in fmts if f != "party"]
    out["formats"] = fmts
    pf = RENAMED_FORMATS.get(raw.get("primary_format"), raw.get("primary_format"))
    out["primary_format"] = pf if pf in fmts else None
    out["party_reason"] = _clean_text(raw.get("party_reason")) if "party" in fmts else None
    tsrc = raw.get("type_source_url")
    out["type_source_url"] = tsrc if ok(tsrc) else None
    try:
        out["type_confidence"] = max(0.0, min(1.0, float(raw.get("type_confidence") or 0.5)))
    except (TypeError, ValueError):
        out["type_confidence"] = 0.5

    own_kind = own_genre_kind(fmts)
    facts = raw.get("genre_facts") if isinstance(raw.get("genre_facts"), dict) else {}
    out["genre_facts"] = {str(k): _clean_text(v) for k, v in facts.items() if _clean_text(v)}
    out["genres"], out["genre_candidates"] = genres_from_raw(
        raw.get("genres") or [], raw.get("genre_candidates") or [], out["genre_facts"],
        own_kind, research_text, aliases, dropped)
    out["type_reason"] = _clean_text(raw.get("type_reason"))
    out["needs_review"] = bool(raw.get("needs_review"))

    arts = [a.strip() for a in raw.get("artists") or [] if isinstance(a, str) and a.strip()][:10]
    asrc = raw.get("artists_source_url")
    if arts and not ok(asrc):
        dropped.append("artists: no valid source_url")
        arts, asrc = [], None
    out["artists"], out["artists_source_url"] = arts, asrc if arts else None

    links = []
    for s in raw.get("spotify") or []:
        url = (s or {}).get("url") or ""
        m = _SPOTIFY_RE.match(url)
        if not m:
            dropped.append(f"spotify: not an artist URL ({url[:60]})")
            continue
        if seen_urls is not None and not any(u.startswith(m.group(0)) for u in seen_urls):
            dropped.append(f"spotify: URL not in search results ({url[:60]})")
            continue
        links.append({"name": _clean_text(s.get("artist")) or (arts[0] if arts else None),
                      "spotify_url": m.group(0)})
    out["artist_links"] = links[:5]

    price, psrc = _clean_text(raw.get("price")), raw.get("price_source_url")
    if price and not ok(psrc):
        dropped.append("price: no valid source_url")
        price = None
    if price:
        ok_p, why = price_supported(price, research_text)   # task 062 (060 part 2)
        if not ok_p:
            dropped.append(f"price '{price}': {why}")
            price = None
    out["price"], out["price_source_url"] = price, psrc if price else None

    st, ssrc = _clean_text(raw.get("start_time")), raw.get("start_time_source_url")
    if st and not _TIME_RE.match(st):
        dropped.append(f"start_time: bad format {st}")
        st = None
    if st and not ok(ssrc):
        dropped.append("start_time: no valid source_url")
        st = None
    out["start_time"], out["start_time_source_url"] = st, ssrc if st else None

    descs = raw.get("descriptions") or {}
    dsrc = [u for u in raw.get("description_source_urls") or [] if ok(u)]
    clean = {k: _clean_text(descs.get(k)) for k in ("cs", "sk", "en")} if isinstance(descs, dict) else {}
    clean = {k: v for k, v in clean.items() if v}
    # task 063 (ai-rules F): no sentences about missing information.  Two-step
    # providers remove them before the translation (raw["no_info_removed"]);
    # here for one-step providers too: the Czech text is cleaned and the SK/EN
    # translations, which still contain them, are dropped.
    removed = [str(x) for x in raw.get("no_info_removed") or []]
    no_desc = bool(raw.get("no_info_empty"))
    if raw.get("needs_review") and (clean or raw.get("needs_review_no_desc")):
        # task 065 (ai-rules F, H): the model itself flagged the event for
        # review -> no AI description (cs, sk, en); price / time stay
        dropped.append("descriptions: model set needs_review, no description")
        clean, removed = {}, []
    if clean.get("cs"):
        cs, more = strip_no_info(clean["cs"])
        if more:
            removed += more
            clean = {"cs": cs} if cs else {}
            no_desc = no_desc or not cs
    for sent in removed:
        dropped.append(f"description_no_info: {sent}")
    if clean and "cs" not in clean:
        dropped.append("descriptions: no Czech text")
        clean = {}
    if clean and not dsrc:
        dropped.append("descriptions: no source_urls")
        clean = {}
    if clean:
        names = [ev.get("title") or ""] + (ev.get("artists") or []) + arts
        probs = sorted({p for v in clean.values() for p in description_problems(v, names)})
        if probs:
            dropped.append(f"descriptions: {', '.join(probs)}")
            clean = {}
    out["descriptions"] = clean or None
    out["review"] = []
    if no_desc:
        # task 063: only sentences about missing information -> no AI
        # description (rule H, review)
        dropped.append("description_no_info: nothing usable left, no description")
        out["needs_review"] = True
        out["review"].append("no description: only sentences about missing information")
    out["venue_mentions"] = []
    if clean and venue is not None:
        # task 063 (ai-rules F): venue / hall may be mentioned; counted in the
        # log only, no review (task 062 set needs_review)
        out["venue_mentions"] = venue_mentions(clean["cs"], venue)
    out["description_source_urls"] = dsrc if clean else []
    out["dropped"] = dropped
    return out


# ---------------------------------------------------------------------------
# Price check: one GET on the price source page
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text.replace(" ", " ")).lower()


def _amounts(price: str) -> list[str]:
    """Amounts of a price text (task 058: from the price parser, so dates,
    times and decimals like "1490.00 Kč" are not taken as amounts)."""
    p = parse_price(price)
    if p and p["min"] is not None:
        return sorted({str(int(v)) for v in (p["min"], p["max"]) if v is not None})
    if p:
        return []          # free / voluntary: checked by word
    nums = re.findall(r"\d[\d . ]*\d|\d", price)
    return [re.sub(r"[ . ]", "", n) for n in nums]


def _title_keys(ev: dict, artists: list[str]) -> list[str]:
    keys = []
    title = ev.get("title") or ""
    keys.append(title)
    head = re.split(r"\s[-–:+|/]\s|:|\+|\bw/|☆|►", title)[0]
    keys.append(head)
    keys += (ev.get("artists") or [])[:1] + artists[:1]
    out = []
    for k in keys:
        k = _norm(k).strip(" .,-")
        if len(k) >= 4 and k not in out:
            out.append(k)
    return out


def price_on_page(page: str, price: str, ev: dict, artists: list[str]) -> tuple[bool, str]:
    text = _norm(page)
    digits_text = re.sub(r"(?<=\d)[ . ](?=\d{3}\b)", "", text)
    amounts = _amounts(price)
    if amounts:
        missing = [a for a in amounts if not re.search(rf"(?<!\d){a}(?!\d)", digits_text)]
        if missing:
            return False, f"amount {missing} not on page"
    elif not re.search(r"zdarma|free|volny|zadarmo|dobrovoln|bez vstupneho|gratis", text):
        return False, "free-entry word not on page"
    if not any(k in text for k in _title_keys(ev, artists)):
        return False, "event title / artist not on page"
    return True, "ok"


def _fetch_page_text(url: str) -> str | None:
    from bs4 import BeautifulSoup
    try:
        _rate_limit(url)
    except Exception:
        pass
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return soup.get_text(" ")


# task 060: presale (ticket shop) hosts.  Their pages often draw the price
# with JavaScript (GoOut: "priceCents" loaded by the sale widget), so the
# amount is not in the HTML although the price is right.
PRESALE_HOSTS = ("goout.net", "smsticket.cz", "oazis.app", "ticketportal.cz", "ticketstream.cz")


def is_presale(url) -> bool:
    h = _host(url)
    return any(h == d or h.endswith("." + d) for d in PRESALE_HOSTS)


def _has_any_amount(page: str) -> bool:
    """True if the page text shows at least one price amount (number with a
    currency, or a free-entry word): the price part of the page was rendered."""
    p = parse_price(page[:200000])
    return bool(p and (p["min"] is not None or p["kind"] != "paid"))


def verify_price(ev: dict, res: dict, fetch=_fetch_page_text) -> tuple[bool, str, bool]:
    """One GET on the price source page -> (keep, why, verified).

    Page read and the amount is missing -> dropped.  Page not readable (GET
    error / 403, empty, or no amount at all = drawn by JavaScript) -> kept
    unverified (verified False) only on a presale host; a venue page that
    cannot be read -> dropped (task 060)."""
    url = res.get("price_source_url")
    if not _ok_url(url):
        return False, "no valid source_url", False
    if _host(url).endswith("facebook.com"):
        return False, "facebook page is not fetched by the pipeline", False
    presale = is_presale(url)
    try:
        page = fetch(url)
    except Exception as exc:
        why = f"GET failed: {exc.__class__.__name__}"
        return (True, f"presale page unreadable ({why})", False) if presale else (False, why, False)
    if not page or not page.strip():
        return (True, "presale page unreadable (empty)", False) if presale else (False, "empty page", False)
    if presale and not _has_any_amount(page):
        return True, "presale page unreadable (no amount in HTML, JavaScript)", False
    ok, why = price_on_page(page, res["price"], ev, res.get("artists") or [])
    return ok, why, ok


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

class ProviderStop(Exception):
    """The provider cannot be used any more in this run (credit, auth)."""


class _Claude:
    name = "claude"
    model = CLAUDE_MODEL
    prices = CLAUDE_PRICES

    def __init__(self):
        import anthropic
        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip(),
                                          max_retries=2)
        self.tool_type = "web_search_20260209"

    def run(self, prompt: str, max_uses: int) -> dict:
        anthropic = self._anthropic
        messages = [{"role": "user", "content": prompt + "\n\nWhen done, call report_enrichment."}]
        rec = {"searches": 0, "input_tokens": 0, "output_tokens": 0, "seen_urls": []}
        for _turn in range(4):
            tools = [_REPORT_TOOL]
            if max_uses > 0:
                tools.insert(0, {"type": self.tool_type, "name": "web_search",
                                 "max_uses": max_uses, "blocked_domains": BLOCKED_DOMAINS})
            try:
                resp = self.client.messages.create(
                    model=self.model, max_tokens=4096, output_config={"effort": "low"},
                    system=SYSTEM_PROMPT, tools=tools, messages=messages,
                )
            except anthropic.BadRequestError as exc:
                if self.tool_type == "web_search_20260209" and "web_search" in str(exc):
                    self.tool_type = "web_search_20250305"
                    continue
                if "credit" in str(exc).lower() or "billing" in str(exc).lower():
                    raise ProviderStop(str(exc)[:300])
                raise
            except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as exc:
                raise ProviderStop(str(exc)[:300])
            u = resp.usage
            rec["input_tokens"] += u.input_tokens
            rec["output_tokens"] += u.output_tokens
            stu = getattr(u, "server_tool_use", None)
            n = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
            rec["searches"] += n
            max_uses = max(0, max_uses - n)
            report = None
            for b in resp.content:
                if b.type == "web_search_tool_result" and isinstance(b.content, list):
                    rec["seen_urls"] += [r.url for r in b.content if getattr(r, "url", None)]
                elif b.type == "tool_use" and b.name == "report_enrichment":
                    report = b.input
                elif b.type == "text" and getattr(b, "citations", None):
                    rec["seen_urls"] += [c.url for c in b.citations if getattr(c, "url", None)]
            if report is not None:
                rec["raw"] = report
                return rec
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason == "pause_turn":
                continue
            messages.append({"role": "user", "content": "Call report_enrichment now with your result."})
            max_uses = 0
        raise RuntimeError("no report_enrichment after 4 turns")


# Gemini two-step (task 058 part 1, cost tuning task 059).  Step 1 research
# (Google Search), step 2 decision (no search, Czech description only),
# step 3 translation cs -> sk, en with the cheapest model.  Models and
# thinking levels per step are constructor arguments or env variables
# (ENRICH_GEMINI_MODEL / _RESEARCH_THINKING / _DECIDE_MODEL / _DECIDE_THINKING /
# _TRANSLATE_MODEL / _TRANSLATE_THINKING).  Prices per token (input, output
# incl. thinking, cached input), https://aistudio.google.com/docs/pricing,
# 2026-11-17.
GEMINI_PRICE_TABLE = {
    "gemini-3.1-flash-lite": (0.25 / 1e6, 1.50 / 1e6, 0.025 / 1e6),
    "gemini-3.5-flash-lite": (0.30 / 1e6, 2.50 / 1e6, 0.03 / 1e6),
    "gemini-3.6-flash": (0.75 / 1e6, 3.75 / 1e6, 0.075 / 1e6),   # through 2026-12-31, then x2
    "gemini-3.8-flash": (0.75 / 1e6, 3.75 / 1e6, 0.075 / 1e6),   # through 2026-12-31, then x2
}
GEMINI_PRICE_X2_FROM = {"gemini-3.6-flash": "2027-01-01", "gemini-3.8-flash": "2027-01-01"}
GEMINI_SEARCH_PRICE = 14.0 / 1000    # after 5,000 free searches / month
GEMINI_FREE_SEARCHES = 5000
GEMINI_RESERVE_SEARCHES = 6          # searches reserved per event for the monthly limit
GEMINI_DEFAULTS = {"model": "gemini-3.6-flash", "research_thinking": "low",
                   "decide_model": None, "decide_thinking": "medium",
                   "translate_model": "gemini-3.1-flash-lite", "translate_thinking": "minimal"}
MAX_SPOTIFY_PAGES = 5
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
_KWORB_RE = re.compile(r"^https?://(?:www\.)?kworb\.net/spotify/artist/([A-Za-z0-9]{22})")


def gemini_cost(model: str, inp: int, out: int, cached: int = 0, x2: bool = False) -> float:
    """USD for one call; x2 = the price from 2027-01-01 (Flash models double)."""
    pin, pout, pcache = GEMINI_PRICE_TABLE.get(model, GEMINI_PRICE_TABLE["gemini-3.6-flash"])
    f = 2 if x2 and model in GEMINI_PRICE_X2_FROM else 1
    return f * ((inp - cached) * pin + cached * pcache + out * pout)


def resolve_redirect(uri: str) -> str | None:
    """Grounding sources are vertexaisearch redirect URIs: one HEAD without
    following -> the target URL (the target site itself is not requested)."""
    if "grounding-api-redirect" not in (uri or ""):
        return uri or None
    try:
        r = requests.head(uri, allow_redirects=False, timeout=10,
                          headers={"User-Agent": USER_AGENT})
        loc = r.headers.get("Location")
        if not loc:
            r = requests.get(uri, allow_redirects=False, timeout=10,
                             headers={"User-Agent": USER_AGENT})
            loc = r.headers.get("Location")
        return loc or None
    except requests.RequestException:
        return None


def spotify_page_name(url: str) -> str | None:
    """One GET of an open.spotify.com/artist page -> artist name (og:title).
    None unless the page answers 200."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
    except requests.RequestException:
        return None
    m = (re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', r.text)
         or re.search(r"<title>([^<|]+)", r.text))
    return _clean_text(html.unescape(m.group(1))) if m else None


def name_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _norm(s or ""))


class _Gemini2:
    """Step 1: research with Google Search (no venue page text, so that the
    model searches).  Step 2: decision without search from the step-1 facts,
    the numbered sources and the venue page text.  Step 3: translation."""
    name = "gemini"
    reserve = GEMINI_RESERVE_SEARCHES

    def __init__(self, model: str | None = None, resolve=resolve_redirect,
                 spotify_name=spotify_page_name, call=None, **cfg):
        env = {k: os.environ.get(f"ENRICH_GEMINI_{k.upper()}", "").strip() or None
               for k in GEMINI_DEFAULTS}
        conf = {k: cfg.get(k) or env[k] or GEMINI_DEFAULTS[k] for k in GEMINI_DEFAULTS}
        if model:
            conf["model"] = model
        conf["decide_model"] = conf["decide_model"] or conf["model"]
        self.conf = conf
        self.key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = conf["model"]
        # run stats use the research model's prices; run_event also returns
        # the exact cost of all steps in cost_usd
        pin, pout, _ = GEMINI_PRICE_TABLE.get(self.model, GEMINI_PRICE_TABLE["gemini-3.6-flash"])
        self.prices = (pin, pout, 0.0)      # searches within the free 5,000 / month
        self.resolve = resolve
        self.spotify_name = spotify_name
        self._call = call or self._http

    @property
    def label(self) -> str:
        c = self.conf
        return (f"research {c['model']}/{c['research_thinking']}, decide "
                f"{c['decide_model']}/{c['decide_thinking']}, translate {c['translate_model']}")

    def _http(self, body: dict, model: str | None = None) -> dict:
        req = urllib.request.Request(
            _GEMINI_URL.format(model or self.model), data=json.dumps(body).encode(),
            method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": self.key,
                     "User-Agent": USER_AGENT})
        last = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as exc:
                msg = exc.read().decode("utf-8", "replace")[:300]
                if exc.code in (401, 402, 403, 404):   # 402: prepaid credit used up
                    raise ProviderStop(f"HTTP {exc.code}: {msg}")
                last = RuntimeError(f"HTTP {exc.code}: {msg}")
                if exc.code not in (429, 500, 503):
                    raise last
            except (urllib.error.URLError, TimeoutError) as exc:
                last = RuntimeError(f"network: {exc}")
            time.sleep(5 * (attempt + 1))
        raise last

    def _generate(self, model: str, thinking: str | None, body: dict) -> tuple[dict, dict]:
        gc = body.setdefault("generationConfig", {})
        if thinking:
            gc["thinkingConfig"] = {"thinkingLevel": thinking}
        try:
            data = self._call(body, model)
        except TypeError:                     # test doubles with call(body)
            data = self._call(body)
        um = data.get("usageMetadata", {})
        u = {"model": model, "thinking": thinking,
             "input_tokens": um.get("promptTokenCount", 0) + um.get("toolUsePromptTokenCount", 0),
             "cached_tokens": um.get("cachedContentTokenCount", 0),
             "output_tokens": um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0),
             "thoughts_tokens": um.get("thoughtsTokenCount", 0)}
        u["cost_usd"] = gemini_cost(model, u["input_tokens"], u["output_tokens"],
                                    u["cached_tokens"])
        return data, u

    @staticmethod
    def _text(data: dict) -> tuple[str, dict]:
        cand = (data.get("candidates") or [{}])[0]
        return "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", [])
                       if not p.get("thought")), cand

    def research(self, ev: dict, venue: dict) -> dict:
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        user = "\n".join([
            f"Event: {ev.get('title')}",
            f"Venue: {venue.get('name', ev['venue_id'])}, Prague"
            + (f" ({venue['website']})" if venue.get("website") else ""),
            f"Date: {ev.get('date')}",
            f"Event page at the venue: {src or '(none)'}",
        ])
        rec = {"text": "", "queries": [], "sources": [], "usage": [], "retried": False,
               "searched": False, "kworb": [], "model": self.conf["model"],
               "thinking": self.conf["research_thinking"]}
        chunks: list = []
        for attempt in range(2):
            prompt = user if attempt == 0 else user + "\n\n" + RESEARCH_RETRY
            data, u = self._generate(self.conf["model"], self.conf["research_thinking"], {
                "systemInstruction": {"parts": [{"text": RESEARCH_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4000},
            })
            rec["usage"].append(u)
            rec["text"], cand = self._text(data)
            gm = cand.get("groundingMetadata") or {}
            queries = gm.get("webSearchQueries") or []
            rec["queries"] += queries
            chunks = [c.get("web") or {} for c in gm.get("groundingChunks") or []]
            if queries:
                rec["searched"] = True
                break
            rec["retried"] = True
        # resolve redirect sources; Spotify artist pages get one GET for the
        # name.  kworb.net/spotify/artist/<ID> -> open.spotify.com/artist/<ID>
        # with one GET of the Spotify page (task 059; nothing fetched from kworb)
        seen, n_spotify = set(), 0
        for c in chunks:
            url = self.resolve(c.get("uri"))
            if not url or blocked(url) or canon_url(url) in seen:
                continue
            seen.add(canon_url(url))
            item = {"title": c.get("title") or _host(url), "url": url}
            m = _SPOTIFY_RE.match(url)
            if m:
                item["url"] = m.group(0)
                seen.add(canon_url(m.group(0)))
                if n_spotify < MAX_SPOTIFY_PAGES:
                    item["spotify_name"] = self.spotify_name(m.group(0))
                    n_spotify += 1
            rec["sources"].append(item)
            k = _KWORB_RE.match(url)
            if k and n_spotify < MAX_SPOTIFY_PAGES:
                sp = f"https://open.spotify.com/artist/{k.group(1)}"
                if canon_url(sp) in seen:
                    continue
                seen.add(canon_url(sp))
                name = self.spotify_name(sp)
                n_spotify += 1
                rec["kworb"].append({"kworb_url": url, "spotify_url": sp, "page_name": name})
                rec["sources"].append({"title": "Spotify artist page (ID from kworb.net)",
                                       "url": sp, "spotify_name": name, "via": "kworb"})
        return rec

    def decide(self, ev: dict, venue: dict, page_text: str | None,
               research: dict) -> tuple[dict, dict]:
        lines = [build_prompt(ev, venue, page_text), "", "RESEARCH FACTS (step 1)",
                 research["text"] or "(nothing found)", "", "SOURCES"]
        for n, s in enumerate(research["sources"], 1):
            extra = f" (Spotify artist page: {s['spotify_name']})" if s.get("spotify_name") else ""
            lines.append(f"[{n}] {s['title']}: {s['url']}{extra}")
        if not research["sources"]:
            lines.append("(none)")
        # static rules + schema first (system instruction) -> implicit cache
        data, u = self._generate(self.conf["decide_model"], self.conf["decide_thinking"], {
            "systemInstruction": {"parts": [{"text": DECIDE_PROMPT + "\n\nJSON keys (JSON "
                                             "schema of the values): " + _DECIDE_SCHEMA}]},
            "contents": [{"role": "user", "parts": [{"text": "\n".join(lines)}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8000,
                                 "responseMimeType": "application/json"},
        })
        text, cand = self._text(data)
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise RuntimeError(f"step 2: no JSON in answer ({cand.get('finishReason')})")
        return json.loads(m.group(0)), u

    def translate(self, cs: str) -> tuple[dict, dict]:
        data, u = self._generate(self.conf["translate_model"], self.conf["translate_thinking"], {
            "systemInstruction": {"parts": [{"text": TRANSLATE_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": cs}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 3000,
                                 "responseMimeType": "application/json"},
        })
        text, _ = self._text(data)
        m = re.search(r"\{.*\}", text, re.S)
        try:
            out = json.loads(m.group(0)) if m else {}
        except ValueError:
            out = {}
        return {k: out[k] for k in ("sk", "en") if isinstance(out.get(k), str)}, u

    def run_from_research(self, ev: dict, venue: dict, page_text: str | None,
                          r: dict) -> dict:
        """Steps 2 + 3 from a research record (new or stored); no search."""
        raw, u2 = self.decide(ev, venue, page_text, r)
        usage = [u2]
        descs = raw.get("descriptions") if isinstance(raw.get("descriptions"), dict) else None
        if descs and raw.get("needs_review"):
            # task 065 (ai-rules F, H): the model flagged the event for review
            # -> no description, no translation call
            raw["descriptions"] = None
            raw["needs_review_no_desc"] = True
        elif descs and isinstance(descs.get("cs"), str) and descs["cs"].strip():
            # task 063 (ai-rules F): sentences about missing information are
            # removed from the Czech text BEFORE the translation
            cs, removed = strip_no_info(descs["cs"])
            if removed:
                raw["no_info_removed"] = removed
            if cs:
                tr, u3 = self.translate(cs)
                usage.append(u3)
                raw["descriptions"] = {"cs": cs, **tr}
            else:
                raw["descriptions"] = None
                raw["no_info_empty"] = True
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        allowed = {s["url"] for s in r["sources"]} | ({src} if src else set())
        return _sum_usage({
            # task 062: genres and price need support in the facts / venue page
            "support_text": "\n".join([r.get("text") or "", page_text or "",
                                        ev.get("title") or "", ev.get("price_text") or ""]),
            "searches": 0,
            "seen_urls": [s["url"] for s in r["sources"]],
            "allowed_urls": allowed,
            "spotify_names": {s["url"]: s["spotify_name"] for s in r["sources"]
                              if s.get("spotify_name")},
            "kworb": r.get("kworb") or [],
            "searched": r["searched"],
            "research": r,
            "raw": raw,
            "steps": usage,
        })

    def run_event(self, ev: dict, venue: dict, page_text: str | None, max_uses: int) -> dict:
        r = self.research(ev, venue)
        rec = self.run_from_research(ev, venue, page_text, r)
        rec["searches"] = len(r["queries"])
        rec["steps"] = r["usage"] + rec["steps"]
        return _sum_usage(rec)


def _sum_usage(rec: dict) -> dict:
    steps = rec["steps"]
    rec["input_tokens"] = sum(u["input_tokens"] for u in steps)
    rec["output_tokens"] = sum(u["output_tokens"] for u in steps)
    rec["cached_tokens"] = sum(u["cached_tokens"] for u in steps)
    rec["cost_usd"] = sum(u["cost_usd"] for u in steps)
    return rec


# Step 2 schema without the sk / en descriptions (they come from step 3).
_DECIDE_SCHEMA = json.dumps(
    {k: (v if k != "descriptions" else {"type": ["object", "null"],
                                         "properties": {"cs": {"type": "string"}}})
     for k, v in _RESULT_SCHEMA["properties"].items()}, ensure_ascii=False)


def make_provider(budget=None):
    name = (os.environ.get("ENRICH_PROVIDER") or "claude").strip().lower()
    if name == "deepseek":
        # task 062: daily run with DeepSeek (variant A); budget per run / month
        if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
            return None, "DEEPSEEK_API_KEY not set"
        if budget is None:
            return None, "DeepSeek budget unavailable (pipeline state not loaded)"
        from pipeline.deepseek import _DeepSeek
        return _DeepSeek(budget=budget), None
    if name == "gemini":
        # task 060: never Gemini with the google_search tool in the daily run
        return None, ("ENRICH_PROVIDER=gemini refused: Gemini Grounding with Google Search "
                      "is not allowed for this use (Gemini API terms, task 060)")
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        return None, "ANTHROPIC_API_KEY not set"
    return _Claude(), None


# ---------------------------------------------------------------------------
# Applying results to events
# ---------------------------------------------------------------------------

def _prov(by: str, model: str, today: str, **kw) -> dict:
    d = {"by": by, "model": model, "checked_at": today}
    d.update({k: v for k, v in kw.items() if v is not None})
    return d


def result_to_enrichment(res: dict, model: str, today: str, searches: int,
                         price_ok: bool) -> dict:
    """Turn a validated result into the stored `enrichment` map plus values."""
    enr: dict = {"run": {"checked_at": today, "model": model, "searches": searches}}
    vals: dict = {}
    if res["formats"]:
        by = "ai_web" if res["type_source_url"] else "ai_text"
        enr["formats"] = _prov(by, model, today, source_url=res["type_source_url"],
                               confidence=round(res["type_confidence"], 2),
                               reason=res["party_reason"])
        vals["formats"] = res["formats"]
        vals["primary_format"] = res["primary_format"]
    if res["genres"]:
        by = "ai_web" if res["type_source_url"] else "ai_text"
        enr["genres"] = _prov(by, model, today, source_url=res["type_source_url"],
                              confidence=round(res["type_confidence"], 2))
        vals["genres"] = res["genres"]
    if res["genre_candidates"]:
        enr["genre_candidates"] = res["genre_candidates"]
    if res["price"] and price_ok:
        enr["price_text"] = _prov("ai_web", model, today, source_url=res["price_source_url"])
        if res.get("price_verified") is False:
            enr["price_text"]["verified"] = False   # task 060: presale page not readable
        vals["price_text"] = res["price"]
    if res["start_time"]:
        enr["start_time"] = _prov("ai_web", model, today, source_url=res["start_time_source_url"])
        vals["start_time"] = res["start_time"]
    if res["artists"]:
        enr["artists"] = _prov("ai_web", model, today, source_url=res["artists_source_url"])
        vals["artists"] = res["artists"]
    if res["artist_links"]:
        enr["artist_links"] = _prov("ai_web", model, today,
                                    source_url=res["artist_links"][0]["spotify_url"])
        vals["artist_links"] = res["artist_links"]
    if res["descriptions"]:
        enr["description"] = _prov("ai_web", model, today,
                                   source_urls=res["description_source_urls"])
        vals["descriptions"] = res["descriptions"]
    return {"enrichment": enr, "values": vals}


def values_from_enrichment(enr: dict, prev: dict) -> dict:
    """Recover the AI values of a cached event from the previous output."""
    vals = {}
    def ai(name):   # task 060: manual.json values are re-applied, never cached as AI
        return name in enr and (enr[name] or {}).get("by") != "manual"

    for field in ("formats", "genres", "price_text", "start_time", "artists"):
        key = field
        if ai(field) and prev.get(key) is not None:
            vals[key] = prev[key]
    if ai("formats"):
        vals["primary_format"] = prev.get("primary_format")
    if ai("description") and prev.get("descriptions") and not review_no_description(enr):
        vals["descriptions"] = prev["descriptions"]
    return vals


def review_no_description(enr: dict) -> bool:
    """Task 065 (ai-rules F, H): an event the model flagged for review keeps
    no AI description, also when it was stored before 065 (REVO: Z Gumy Do Gumy)."""
    return bool((enr.get("run") or {}).get("needs_review"))


def remap_stored_genres(ev: dict, enr: dict, vals: dict, record: dict | None,
                        page_text: str | None, aliases: dict | None) -> list | None:
    """Task 065: re-apply the genre lists, aliases and hierarchy to a cached
    result without an API call: the stored raw names (genre_candidates, the
    validated genres) are mapped again and new list genres pass the guard on
    the stored research (record facts + genre_facts, page / venue text).
    Changes `enr` / `vals` in place; returns the new genres or None (no
    research record / manual genres: unchanged)."""
    if not record or (enr.get("genres") or {}).get("by") == "manual":
        return None
    aliases = {k.lower(): v for k, v in (aliases or {}).items()}
    fmts = vals.get("formats") or ev.get("formats") or []
    own_kind = own_genre_kind(fmts)
    prev = list(vals.get("genres") or []) if "genres" in enr else []
    cands = enr.get("genre_candidates") or []
    by_target: dict = {}
    for c in cands:
        if c.get("maps_to"):
            by_target.setdefault(c["maps_to"], []).append(c)
    raw_cands = []
    for g in prev:
        raw_cands += [{"raw": c["raw"], "kind": c.get("kind") or "music"} for c in by_target.get(g, [])]
        raw_cands.append({"raw": g, "kind": own_kind or "music"})
    raw_cands += [c for c in cands if not c.get("maps_to")]
    trusted = {g for g in prev if g not in by_target}
    support = "\n".join(x for x in (record.get("facts"), page_text, ev.get("description")) if x)
    dropped: list = []
    gens, new_cands = genres_from_raw([], raw_cands, record.get("genre_facts") or {}, own_kind,
                                      support, aliases, dropped, quote_fallback=True,
                                      trusted=trusted)
    if gens:
        if "genres" not in enr:
            f = enr.get("formats") or {}
            run = enr.get("run") or {}
            enr["genres"] = _prov(f.get("by", "ai_web"), run.get("model") or f.get("model"),
                                  run.get("checked_at") or f.get("checked_at"),
                                  source_url=f.get("source_url"), confidence=f.get("confidence"))
        vals["genres"] = gens
    else:
        enr.pop("genres", None)
        vals.pop("genres", None)
    if new_cands:
        enr["genre_candidates"] = new_cands
    else:
        enr.pop("genre_candidates", None)
    return gens


def fill_primary_from_research(events: list[dict], research: dict | None) -> int:
    """Task 063: an event whose type stayed with the venue category (no AI
    formats in its enrichment, e.g. enriched before task 063) gets the
    ``primary_format`` the AI decided from the stored research record, when it
    is one of the event's formats.  No API call.  Returns the count."""
    n = 0
    for ev in events:
        rec = (research or {}).get(ev["id"])
        method = (ev.get("classification") or {}).get("method")
        # manual: formats stay as set by hand, only the missing primary is filled
        if not rec or ev.get("primary_format") or method not in ("source", "keyword", "manual"):
            continue
        from pipeline.classify import RENAMED_FORMATS
        pf = RENAMED_FORMATS.get(rec.get("primary_format"), rec.get("primary_format"))
        if "enrichment" not in ev or pf not in (ev.get("formats") or []):
            continue
        ev["primary_format"] = pf
        n += 1
    return n


def apply_talk_genres(events: list[dict], research: dict | None,
                      aliases: dict | None) -> list[str]:
    """Task 078 (ai-rules C10): talk genres from approved phrases in the
    title, description and the stored research facts (no API call), only for
    events with the `talk` format; other events lose them.  Manual genres stay.
    Talk genres go first when talk is the primary format.  Changes events in
    place; returns the ids of changed events."""
    changed = []
    for ev in events:
        enr = ev.get("enrichment") or {}
        if (enr.get("genres") or {}).get("by") == "manual":
            continue
        old = list(ev.get("genres") or [])
        rest = [g for g in old if g not in TALK_GENRES]
        found = []
        if "talk" in (ev.get("formats") or []):
            rec = (research or {}).get(ev["id"]) or {}
            found = talk_genres_from_text([ev.get("title"), ev.get("description"),
                                           rec.get("facts")], aliases)
        new = found + rest if ev.get("primary_format") == "talk" else rest + found
        if new == old:
            continue
        ev["genres"] = new
        if found and "genres" not in enr and not old:
            f = enr.get("formats") or {}
            ev.setdefault("enrichment", {})["genres"] = _prov(
                f.get("by", "ai_text"), f.get("model"), f.get("checked_at"),
                source_url=f.get("source_url"), confidence=f.get("confidence"))
        elif not new and "genres" in enr:
            enr.pop("genres")
        changed.append(ev["id"])
    return changed


def apply_enrichment(ev: dict, enr: dict, vals: dict, stats: dict | None = None,
                     keep_genres: bool | None = None) -> dict:
    """Apply AI values to empty fields only; source values win (their
    enrichment entry is dropped).  Returns a new event dict.

    Task 063 (docs/ai-rules.md B7): the AI type wins over the venue category
    (``source``) and keywords; only ``manual`` wins over the AI.  Genres are
    unchanged: venue genres win (keep_genres; default = method manual/source)."""
    ev = dict(ev)
    enr = json.loads(json.dumps(enr))   # deep copy
    cls = ev.get("classification") or {}
    method = cls.get("method")

    def count(key):
        if stats is not None:
            stats[key] = stats.get(key, 0) + 1

    if "formats" in vals and method != "manual":
        new = vals["formats"]
        if set(new) != set(ev.get("formats") or []):
            count("type_changed")
            if stats is not None:     # task 057: ids for the weekly report
                stats.setdefault("type_changed_ids", []).append(
                    {"id": ev.get("id"), "old": list(ev.get("formats") or []), "new": list(new)})
        ev["formats"] = new
        ev["primary_format"] = vals.get("primary_format") if vals.get("primary_format") in new else None
        f = enr["formats"]
        c = {"method": "llm+web" if f.get("by") == "ai_web" else "llm",
             "confidence": f.get("confidence", 0.5)}
        if f.get("reason"):
            c["reason"] = f["reason"]
        ev["classification"] = c
    elif "formats" in enr:
        enr.pop("formats")

    if keep_genres is None:
        keep_genres = method in ("manual", "source")
    if "genres" in vals and (not keep_genres or not ev.get("genres")):
        if vals["genres"] != (ev.get("genres") or []):
            count("genres")
        ev["genres"] = vals["genres"]
    elif "genres" in enr:
        enr.pop("genres")

    for field, stat in (("price_text", "price"), ("start_time", "time"), ("artists", "artists")):
        if field in vals and not ev.get(field):
            ev[field] = vals[field]
            count(stat)
        elif field in enr:
            enr.pop(field)   # source provides it (or nothing to apply)

    if vals.get("artist_links"):
        ev["artist_links"] = vals["artist_links"]
        count("spotify")
    else:
        enr.pop("artist_links", None)

    if vals.get("descriptions"):
        ev["descriptions"] = vals["descriptions"]
        count("description")
        if not ev.get("description"):
            ev["description"] = vals["descriptions"]["cs"]
            ev["description_source"] = "ai"
    else:
        enr.pop("description", None)

    if ("price_text" in enr and ev.get("free") is None
            and not re.search(r"\d", ev["price_text"])
            and re.search(r"zdarma|free|voln|zadarmo", ev["price_text"], re.I)):
        ev["free"] = True
    ev["enrichment"] = enr
    return ev


def check_spotify(res: dict, rec: dict) -> None:
    """Gemini two-step: a Spotify link stays only if its page was in the
    resolved search sources and the page's artist name is one of the event's
    artists (the model checked genre / country in step 2)."""
    names = rec.get("spotify_names")
    if names is None:
        return
    keys = {name_key(a) for a in res["artists"]}
    kept = []
    for link in res["artist_links"]:
        page = names.get(link["spotify_url"])
        if page and name_key(page) in keys:
            kept.append({"name": page, "spotify_url": link["spotify_url"]})
        else:
            res["dropped"].append(f"spotify: page name {page!r} not an event artist")
    # task 059: Spotify ID from a kworb.net search result, verified by one GET
    # of the Spotify page (200 + page name = an event artist without accents
    # and case).  Stored even when step 2 did not pick it.
    have = {link["spotify_url"] for link in kept}
    res["kworb"] = []
    for k in rec.get("kworb") or []:
        page = k.get("page_name")
        if not page:
            status = "rejected: page not 200 / no name"
        elif name_key(page) not in keys:
            status = f"rejected: page name {page!r} not an event artist"
        else:
            status = "ok"
            if k["spotify_url"] not in have:
                kept.append({"name": page, "spotify_url": k["spotify_url"]})
                have.add(k["spotify_url"])
        res["kworb"].append({**k, "status": status})
        if status != "ok":
            res["dropped"].append(f"spotify (kworb) {k['spotify_url']}: {status}")
    res["artist_links"] = kept[:5]


def process_result(ev: dict, rec: dict, model: str, today: str, aliases: dict | None,
                   price_fetch=_fetch_page_text, venue: dict | None = None) -> tuple[dict, dict]:
    """Validate one provider result, verify the price, build the enrichment."""
    seen = None if rec["seen_urls"] is None else {u.split("?")[0] for u in rec["seen_urls"]}
    res = validate(rec["raw"], ev, seen, aliases, rec.get("allowed_urls"),
                   rec.get("support_text"), venue)
    check_spotify(res, rec)
    searched = rec.get("searched", True)
    if not searched:
        # task 058: the model did not search -> not stored as ai_web
        res["dropped"].append("not searched: only type / genres kept (ai_text)")
        res["type_source_url"] = None
        for k in ("artists", "artist_links", "genre_candidates"):
            res[k] = []
        res["price"] = res["start_time"] = res["descriptions"] = None
    res["price_ok"] = False
    if res["price"] and not ev.get("price_text"):
        res["price_ok"], why, res["price_verified"] = verify_price(ev, res, price_fetch)
        if res["price_ok"] and not res["price_verified"]:
            log.info("enrich_ai %s: price '%s' from %s kept unverified: %s",
                     ev["id"], res["price"], res["price_source_url"], why)
        if not res["price_ok"]:
            log.info("enrich_ai %s: price '%s' from %s dropped: %s",
                     ev["id"], res["price"], res["price_source_url"], why)
            res["dropped"].append(f"price '{res['price']}': {why}")
    conv = result_to_enrichment(res, model, today, rec["searches"], res["price_ok"])
    run = conv["enrichment"]["run"]
    if not searched:
        run["searched"] = False
    if res.get("needs_review"):
        run["needs_review"] = True
    return res, conv


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def enrich_events_ai(events: list[dict], venues: list[dict], previous: dict,
                     state: dict | None, today: str,
                     page_texts: dict | None = None, provider=None,
                     price_fetch=_fetch_page_text,
                     aliases: dict | None = None,
                     research: dict | None = None,
                     budget=None,
                     keep_genres: set | None = None) -> tuple[list[dict], dict]:
    """Enrich events in the window. Returns (events, stats).

    research: stored research records (id -> record, task 059); new records
    of the Gemini provider are added to it.  ENRICH_FROM_RESEARCH = "all" or
    comma-separated ids re-runs step 2 from the stored facts (no search),
    ignoring the cache, for events in the window that have a record."""
    stats: dict = {"window": 0, "cached": 0, "to_enrich": 0, "enriched": 0, "errors": 0,
                   "skipped_limit": 0, "skipped_timeout": 0, "searches": 0,
                   "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
                   "prices_dropped": 0, "dropped": [], "warnings": []}
    page_texts = page_texts or {}
    venues_map = {v["id"]: v for v in venues}
    month = today[:7]
    # task 063: ids with venue genres (layer 1); main.py passes them because
    # classify_ai may already have replaced classification.method
    if keep_genres is None:
        from pipeline.classify import venue_genre_ids
        keep_genres = venue_genre_ids(events)

    def apply(ev, enr, vals, st=None):
        return apply_enrichment(ev, enr, vals, st, ev["id"] in keep_genres)

    stats["genres_remapped"] = []
    stats["descriptions_dropped_review"] = []

    def cached_values(ev, c):
        """Cached enrichment + values; task 065: genres re-mapped from the
        stored research (no API)."""
        enr = json.loads(json.dumps(c["enrichment"]))
        vals = values_from_enrichment(enr, c["prev"])
        if (c["prev"].get("descriptions") and "description" in enr
                and review_no_description(enr)):
            stats["descriptions_dropped_review"].append(ev["id"])
        old = list(vals.get("genres") or []) if "genres" in enr else []
        new = remap_stored_genres(ev, enr, vals, (research or {}).get(ev["id"]),
                                  page_texts.get(ev["id"]), aliases)
        if new is not None and new != old:
            stats["genres_remapped"].append({"id": ev["id"], "old": old, "new": new})
        return enr, vals

    # one-off manual re-run of chosen events (workflow_dispatch input reenrich_ids)
    force = {i.strip() for i in os.environ.get("ENRICH_FORCE_IDS", "").split(",") if i.strip()}
    # task 062: re-run all events of the next N days, ignoring the AI cache
    force_days = int(os.environ.get("ENRICH_FORCE_DAYS", "").strip() or 0)
    if force_days:
        last = (datetime.date.fromisoformat(today)
                + datetime.timedelta(days=min(force_days, WINDOW_DAYS))).isoformat()
        force |= {e["id"] for e in events if in_window(e, today) and e.get("date", "") <= last}
    redo_env = os.environ.get("ENRICH_FROM_RESEARCH", "").strip()
    redo_ids = {i.strip() for i in redo_env.split(",") if i.strip()}
    redo = {e["id"] for e in events if research and e["id"] in research
            and (redo_env.lower() == "all" or e["id"] in redo_ids)}
    stats["from_research"] = 0
    todo, out_by_id = [], {}
    recheck: dict[str, str] = {}      # task 085: id -> checked_at of the earlier run
    for ev in events:
        if not in_window(ev, today):
            # keep cached AI values of events enriched earlier (e.g. moved date)
            c = cached_enrichment(ev, previous)
            if c:
                out_by_id[ev["id"]] = apply(ev, *cached_values(ev, c))
            continue
        stats["window"] += 1
        c = None if ev["id"] in force or ev["id"] in redo else cached_enrichment(ev, previous)
        if needs_recheck(ev, c, today):       # task 085: once, within 60 days
            recheck[ev["id"]] = c["enrichment"]["run"]["checked_at"]
            c = None
        if c:
            stats["cached"] += 1
            out_by_id[ev["id"]] = apply(ev, *cached_values(ev, c))
        else:
            todo.append(ev)
    # task 085: nearest events first (the run budget may stop before the end)
    todo.sort(key=lambda e: (e.get("date", ""), e.get("start_time") or ""))
    stats["to_enrich"] = len(todo)
    stats["recheck"] = len(recheck)

    if todo and provider is None:
        provider, why = make_provider(budget)
        if provider is None:
            stats["skipped"] = why
            stats["warnings"].append(f"AI enrichment skipped: {why}")
            todo = []
    if todo and state is None:
        stats["warnings"].append("AI enrichment skipped: pipeline state (monthly search counter) "
                                 "could not be loaded")
        stats["skipped"] = "state unavailable"
        todo = []

    counter = None
    if state is not None:
        counter = state.get("ai_searches") or {}
        if counter.get("month") != month:
            counter = {"month": month, "count": 0}
        state["ai_searches"] = counter

    month_limit = getattr(provider, "monthly_search_limit", MONTHLY_SEARCH_LIMIT)
    if getattr(budget, "month_cap_ignored", False):
        month_limit = 10 ** 9           # task 089: task run, month limit ignored (int: JSON)
    if todo:
        stats["provider"], stats["model"] = provider.name, provider.model
        lock = threading.Lock()
        reserved = [0]
        stop = {"reason": None}
        errors_in_row = [0]
        deadline = time.monotonic() + RUN_TIMEOUT_S
        results: dict[str, dict] = {}

        def work(ev):
            with lock:
                if stop["reason"]:
                    return ev["id"], {"skip": "stopped"}
                if time.monotonic() > deadline:
                    return ev["id"], {"skip": "timeout"}
                left = month_limit - counter["count"] - reserved[0]
                if left <= 0:
                    return ev["id"], {"skip": "limit"}
                max_uses = min(getattr(provider, "reserve", MAX_SEARCHES_PER_EVENT), left)
                if ev["id"] in redo and hasattr(provider, "run_from_research"):
                    max_uses = 0                         # no search
                reserved[0] += max_uses
            venue = venues_map.get(ev["venue_id"], {})
            try:
                if max_uses == 0 and ev["id"] in redo:   # task 059: stored facts
                    from pipeline.research_store import to_research
                    rec = provider.run_from_research(ev, venue, page_texts.get(ev["id"]),
                                                     to_research(research[ev["id"]]))
                elif hasattr(provider, "run_event"):      # Gemini two-step (task 058)
                    rec = provider.run_event(ev, venue, page_texts.get(ev["id"]), max_uses)
                else:
                    rec = provider.run(build_prompt(ev, venue, page_texts.get(ev["id"])), max_uses)
                err = None
            except ProviderStop as exc:
                rec, err = None, exc
                with lock:
                    stop["reason"] = f"{provider.name}: {exc}"
            except Exception as exc:
                rec, err = None, exc
            with lock:
                reserved[0] -= max_uses
                if rec:
                    counter["count"] += rec["searches"]
                    stats["searches"] += rec["searches"]
                    stats["input_tokens"] += rec["input_tokens"]
                    stats["output_tokens"] += rec["output_tokens"]
                    if "cost_usd" in rec:
                        stats["exact_cost_usd"] = stats.get("exact_cost_usd", 0.0) + rec["cost_usd"]
                    errors_in_row[0] = 0
                else:
                    stats["errors"] += 1
                    errors_in_row[0] += 1
                    if errors_in_row[0] >= MAX_ERRORS_IN_A_ROW and not stop["reason"]:
                        stop["reason"] = f"{MAX_ERRORS_IN_A_ROW} errors in a row (last: {err!r})"[:300]
            if err:
                log.warning("enrich_ai %s: %s", ev["id"], str(err)[:200])
                return ev["id"], {"error": str(err)[:200]}
            return ev["id"], {"rec": rec}

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            for ev_id, r in pool.map(work, todo):
                results[ev_id] = r

        if stop["reason"]:
            stats["warnings"].append(f"AI enrichment stopped: {stop['reason']}")
        # sequential part: validation + price GET (one request at a time per site)
        for ev in todo:
            r = results.get(ev["id"], {})
            if r.get("skip") == "limit":
                stats["skipped_limit"] += 1
                continue
            if r.get("skip") in ("timeout", "stopped"):
                stats["skipped_timeout"] += 1
                continue
            rec = r.get("rec")
            if not rec:
                continue
            res, conv = process_result(ev, rec, provider.model, today, aliases, price_fetch,
                                       venues_map.get(ev["venue_id"], {}))
            if res["price"] and not ev.get("price_text") and not res.get("price_ok"):
                stats["prices_dropped"] += 1
            if rec.get("searched") is False:
                stats["not_searched"] = stats.get("not_searched", 0) + 1
            for d in res["dropped"]:
                stats["dropped"].append(f"{ev['id']}: {d}")
            for d in res.get("review") or []:
                stats.setdefault("review", []).append(f"{ev['id']}: {d}")
            if res.get("venue_mentions"):
                stats["venue_in_description"] = stats.get("venue_in_description", 0) + 1
            if ev["id"] in recheck:        # task 085: mark the one-off re-check
                conv["enrichment"].setdefault("run", {})["rechecked_from"] = recheck[ev["id"]]
                stats["rechecked"] = stats.get("rechecked", 0) + 1
            out_by_id[ev["id"]] = apply(ev, conv["enrichment"], conv["values"], stats)
            stats["enriched"] += 1
            if ev["id"] in redo and rec.get("searches") == 0:
                stats["from_research"] += 1
            if research is not None and rec.get("research"):
                from pipeline.research_store import record_from
                research[ev["id"]] = record_from(ev, rec, res, getattr(provider, "conf", {}),
                                                 today)

        pin, pout, psearch = provider.prices
        stats["cost_usd"] = round(stats["input_tokens"] * pin + stats["output_tokens"] * pout
                                  + stats["searches"] * psearch, 4)
        if "exact_cost_usd" in stats:        # Gemini: per-step models and cached tokens
            stats["cost_usd"] = round(stats.pop("exact_cost_usd"), 4)
        if stats["skipped_limit"]:
            stats["warnings"].append(
                f"AI search limit {month_limit}/month reached: "
                f"{stats['skipped_limit']} events wait for next month")
        if stats["skipped_timeout"]:
            stats["warnings"].append(f"AI enrichment: {stats['skipped_timeout']} events not "
                                     f"processed (timeout/stop), next run continues")

    # task 062: an event that was due but not processed (provider stopped:
    # HTTP 401/402, budget, outage, timeout) keeps its previous AI values
    kept = 0
    for ev in todo:
        if ev["id"] not in out_by_id:
            c = cached_enrichment(ev, previous)
            if c:
                out_by_id[ev["id"]] = apply(ev, *cached_values(ev, c))
                kept += 1
    stats["kept_previous"] = kept
    for r in stats["genres_remapped"]:
        log.info("enrich_ai %s: genres re-mapped (task 065) %s -> %s", r["id"], r["old"], r["new"])
    for i in stats["descriptions_dropped_review"]:
        log.info("enrich_ai %s: cached AI description dropped (needs_review, task 065)", i)
    if counter is not None:
        stats["month_searches"] = counter["count"]
    stats["limit"] = month_limit
    # task 062: dropped by guards, by kind (the job summary is not readable via API)
    kinds: dict = {}
    for d in stats["dropped"]:
        k = d.split(": ", 1)[-1].split(" ", 1)[0].split(":", 1)[0].split("'", 1)[0]
        kinds[k] = kinds.get(k, 0) + 1
    log.info("enrich_ai dropped by kind: %s; review: %d; venue / hall in description "
             "(no review, task 063): %d", kinds, len(stats.get("review") or []),
             stats.get("venue_in_description", 0))
    for w in stats["warnings"]:
        log.warning("%s", w)
    out = [out_by_id.get(e["id"], e) for e in events]
    stats["primary_from_research"] = fill_primary_from_research(out, research)
    stats["talk_genres"] = apply_talk_genres(out, research, aliases)
    log.info("enrich_ai: talk genres (task 078) changed on %d events", len(stats["talk_genres"]))
    log.info("enrich_ai: window=%d cached=%d enriched=%d errors=%d searches=%d month=%s/%d cost=$%.4f",
             stats["window"], stats["cached"], stats["enriched"], stats["errors"],
             stats["searches"], stats.get("month_searches"), month_limit, stats["cost_usd"])
    return out, stats


# ---------------------------------------------------------------------------
# Genre proposals (task 054 part 4a)
# ---------------------------------------------------------------------------

PROPOSAL_MIN_EVENTS = 3


def genre_tables(events: list[dict], approved_aliases: dict | None = None) -> tuple[dict, list]:
    """Aggregate genre_candidates of all events.

    Returns (aliases {raw: genre}, proposals [{name, kind, count, event_ids}])
    — proposals only for unmapped genres with >= PROPOSAL_MIN_EVENTS events.
    """
    from pipeline.genres import is_ignored, load_ignored
    ignored = load_ignored()          # task 065: rejected names are no proposals
    aliases = dict(approved_aliases or {})
    unmapped: dict[tuple, list] = {}
    for ev in events:
        for c in (ev.get("enrichment") or {}).get("genre_candidates") or []:
            raw = c.get("raw")
            if not raw or (not c.get("maps_to") and is_ignored(raw, c.get("kind"), ignored)):
                continue
            if c.get("maps_to"):
                aliases.setdefault(raw, c["maps_to"])
            elif raw not in aliases:
                unmapped.setdefault((raw, c.get("kind", "music")), []).append(ev["id"])
    proposals = [{"name": raw, "kind": kind, "count": len(ids), "event_ids": ids[:5]}
                 for (raw, kind), ids in unmapped.items() if len(ids) >= PROPOSAL_MIN_EVENTS]
    proposals.sort(key=lambda p: (-p["count"], p["name"]))
    return dict(sorted(aliases.items())), proposals
