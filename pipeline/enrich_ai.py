"""
AI enrichment with web search in the daily run (task 054).

For events in the next WINDOW_DAYS days that are new or whose title changed
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

Provider: ENRICH_PROVIDER = "claude" (default) | "gemini".
"""

import concurrent.futures
import datetime
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
from pipeline.ai_rules import DECIDE_PROMPT, RESEARCH_PROMPT, RESEARCH_RETRY, RULES_ALL
from pipeline.genres import FILM_GENRES, STAGE_GENRES, map_genre

log = logging.getLogger(__name__)

WINDOW_DAYS = 60
MONTHLY_SEARCH_LIMIT = 400
MAX_SEARCHES_PER_EVENT = 3
MAX_WORKERS = 4
RUN_TIMEOUT_S = int(os.environ.get("ENRICH_TIMEOUT_S", "1500"))
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


def description_problems(text: str) -> list[str]:
    probs = []
    if "!" in text:
        probs.append("exclamation mark")
    if _EMOJI.search(text):
        probs.append("emoji")
    m = _BANNED.search(text)
    if m:
        probs.append(f"advertising phrase '{m.group(0)}'")
    return probs


def validate(raw: dict, ev: dict, seen_urls: set[str] | None,
             aliases: dict | None = None, allowed_urls: set[str] | None = None) -> dict:
    """Apply the rules to a raw model result -> clean dict + 'dropped'.

    aliases: approved raw genre -> our genre (data/genre_aliases.json).
    allowed_urls: if given (Gemini two-step), every source URL must be one of
    them (resolved search sources + event page), compared by canon_url()."""
    allowed = None if allowed_urls is None else {canon_url(u) for u in allowed_urls}

    def ok(url) -> bool:
        return _ok_url(url) and (allowed is None or canon_url(url) in allowed)
    aliases = {k.lower(): v for k, v in (aliases or {}).items()}
    dropped: list[str] = []
    out: dict = {}

    fmts = [f for f in raw.get("formats") or [] if f in VALID_FORMATS]
    if "party" in fmts and not _clean_text(raw.get("party_reason")):
        dropped.append("party: no party_reason")
        fmts = [f for f in fmts if f != "party"]
    out["formats"] = fmts
    pf = raw.get("primary_format")
    out["primary_format"] = pf if pf in fmts else None
    out["party_reason"] = _clean_text(raw.get("party_reason")) if "party" in fmts else None
    tsrc = raw.get("type_source_url")
    out["type_source_url"] = tsrc if ok(tsrc) else None
    try:
        out["type_confidence"] = max(0.0, min(1.0, float(raw.get("type_confidence") or 0.5)))
    except (TypeError, ValueError):
        out["type_confidence"] = 0.5

    is_music = bool(set(fmts) & _MUSIC_FORMATS)
    own_kind = "music" if is_music else "film" if "film" in fmts else (
        "stage" if set(fmts) & (_STAGE_FORMATS | {"performance"}) else None)
    # task 058: genres in order (main first); raw names are mapped only through
    # spelling variants + approved aliases, never to a parent genre.
    gens, cands, seen_raw = [], [], set()

    def add_raw(rawname, kind):
        rawname = _clean_text(rawname)
        if not rawname or (rawname.lower(), kind) in seen_raw:
            return
        seen_raw.add((rawname.lower(), kind))
        mapped = map_genre(rawname, kind, aliases) if kind else []
        if kind == own_kind and mapped:
            for g in mapped:
                if g not in gens:
                    gens.append(g)
            if [rawname.lower()] != mapped:
                cands.append({"raw": rawname.lower(), "kind": kind, "maps_to": mapped[0]})
        elif not mapped:
            cands.append({"raw": rawname.lower(), "kind": kind or "music", "maps_to": None})

    for g in raw.get("genres") or []:
        if isinstance(g, str):
            add_raw(g, own_kind)
    for c in raw.get("genre_candidates") or []:
        kind = (c or {}).get("kind") if (c or {}).get("kind") in ("music", "film", "stage") else "music"
        add_raw((c or {}).get("raw"), kind)
    out["genres"] = gens
    out["genre_candidates"] = cands
    facts = raw.get("genre_facts") if isinstance(raw.get("genre_facts"), dict) else {}
    out["genre_facts"] = {str(k): _clean_text(v) for k, v in facts.items() if _clean_text(v)}
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
    if clean and "cs" not in clean:
        dropped.append("descriptions: no Czech text")
        clean = {}
    if clean and not dsrc:
        dropped.append("descriptions: no source_urls")
        clean = {}
    if clean:
        probs = sorted({p for v in clean.values() for p in description_problems(v)})
        if probs:
            dropped.append(f"descriptions: {', '.join(probs)}")
            clean = {}
    out["descriptions"] = clean or None
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
    elif not re.search(r"zdarma|free|volny|zadarmo|dobrovoln", text):
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


def verify_price(ev: dict, res: dict, fetch=_fetch_page_text) -> tuple[bool, str]:
    url = res.get("price_source_url")
    if not _ok_url(url):
        return False, "no valid source_url"
    if _host(url).endswith("facebook.com"):
        return False, "facebook page is not fetched by the pipeline"
    try:
        page = fetch(url)
    except Exception as exc:
        return False, f"GET failed: {exc.__class__.__name__}"
    if not page:
        return False, "empty page"
    return price_on_page(page, res["price"], ev, res.get("artists") or [])


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


# Gemini two-step (task 058 part 1).  gemini-3.5-flash is the model named in
# the task; ENRICH_GEMINI_MODEL overrides it.  Prices per token (input, output
# incl. thinking), https://aistudio.google.com/docs/pricing, 2026-11-17.
GEMINI_PRICE_TABLE = {
    "gemini-3.1-flash-lite": (0.25 / 1e6, 1.50 / 1e6),
    "gemini-3.5-flash-lite": (0.30 / 1e6, 2.50 / 1e6),
    "gemini-3.6-flash": (0.75 / 1e6, 3.75 / 1e6),     # through 2026-12-31, then x2
    "gemini-3.8-flash": (0.75 / 1e6, 3.75 / 1e6),     # through 2026-12-31, then x2
}
GEMINI_SEARCH_PRICE = 14.0 / 1000    # after 5,000 free searches / month
GEMINI_RESERVE_SEARCHES = 12         # searches reserved per event for the monthly limit
MAX_SPOTIFY_PAGES = 5
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"


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
    """One GET of an open.spotify.com/artist page -> artist name (og:title)."""
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
    except requests.RequestException:
        return None
    m = (re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', r.text)
         or re.search(r"<title>([^<|]+)", r.text))
    return _clean_text(m.group(1)) if m else None


def name_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _norm(s or ""))


class _Gemini2:
    """Step 1: research with Google Search (no venue page text, so that the
    model searches).  Step 2: decision without search from the step-1 facts,
    the numbered sources and the venue page text."""
    name = "gemini"
    reserve = GEMINI_RESERVE_SEARCHES

    def __init__(self, model: str | None = None, resolve=resolve_redirect,
                 spotify_name=spotify_page_name, call=None):
        self.key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.model = (model or os.environ.get("ENRICH_GEMINI_MODEL", "").strip()
                      or "gemini-3.5-flash")
        pin, pout = GEMINI_PRICE_TABLE.get(self.model, GEMINI_PRICE_TABLE["gemini-3.6-flash"])
        self.prices = (pin, pout, 0.0)      # searches within the free 5,000 / month
        self.resolve = resolve
        self.spotify_name = spotify_name
        self._call = call or self._http

    def _http(self, body: dict) -> dict:
        req = urllib.request.Request(
            _GEMINI_URL.format(self.model), data=json.dumps(body).encode(), method="POST",
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

    @staticmethod
    def _usage(data: dict) -> tuple[int, int]:
        um = data.get("usageMetadata", {})
        return (um.get("promptTokenCount", 0) + um.get("toolUsePromptTokenCount", 0),
                um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0))

    def research(self, ev: dict, venue: dict) -> dict:
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        user = "\n".join([
            f"Event: {ev.get('title')}",
            f"Venue: {venue.get('name', ev['venue_id'])}, Prague"
            + (f" ({venue['website']})" if venue.get("website") else ""),
            f"Date: {ev.get('date')}",
            f"Event page at the venue: {src or '(none)'}",
        ])
        rec = {"text": "", "queries": [], "sources": [], "input_tokens": 0,
               "output_tokens": 0, "retried": False, "searched": False}
        chunks: list = []
        for attempt in range(2):
            prompt = user if attempt == 0 else user + "\n\n" + RESEARCH_RETRY
            data = self._call({
                "systemInstruction": {"parts": [{"text": RESEARCH_PROMPT}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 6000},
            })
            i, o = self._usage(data)
            rec["input_tokens"] += i
            rec["output_tokens"] += o
            cand = (data.get("candidates") or [{}])[0]
            gm = cand.get("groundingMetadata") or {}
            queries = gm.get("webSearchQueries") or []
            rec["queries"] += queries
            rec["text"] = "".join(p.get("text", "") for p in
                                  (cand.get("content") or {}).get("parts", []))
            chunks = [c.get("web") or {} for c in gm.get("groundingChunks") or []]
            if queries:
                rec["searched"] = True
                break
            rec["retried"] = True
        # resolve redirect sources; Spotify artist pages get one GET for the name
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
                if n_spotify < MAX_SPOTIFY_PAGES:
                    item["spotify_name"] = self.spotify_name(m.group(0))
                    n_spotify += 1
            rec["sources"].append(item)
        return rec

    def decide(self, ev: dict, venue: dict, page_text: str | None,
               research: dict) -> tuple[dict, int, int]:
        lines = [build_prompt(ev, venue, page_text), "", "RESEARCH FACTS (step 1)",
                 research["text"] or "(nothing found)", "", "SOURCES"]
        for n, s in enumerate(research["sources"], 1):
            extra = f" (Spotify artist page: {s['spotify_name']})" if s.get("spotify_name") else ""
            lines.append(f"[{n}] {s['title']}: {s['url']}{extra}")
        if not research["sources"]:
            lines.append("(none)")
        schema = json.dumps(_RESULT_SCHEMA["properties"], ensure_ascii=False)
        data = self._call({
            "systemInstruction": {"parts": [{"text": DECIDE_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": "\n".join(lines)
                          + "\n\nJSON keys (JSON schema of the values): " + schema}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8000,
                                 "responseMimeType": "application/json"},
        })
        i, o = self._usage(data)
        cand = (data.get("candidates") or [{}])[0]
        text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise RuntimeError(f"step 2: no JSON in answer ({cand.get('finishReason')})")
        return json.loads(m.group(0)), i, o

    def run_event(self, ev: dict, venue: dict, page_text: str | None, max_uses: int) -> dict:
        r = self.research(ev, venue)
        raw, i, o = self.decide(ev, venue, page_text, r)
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        allowed = {s["url"] for s in r["sources"]} | ({src} if src else set())
        return {
            "searches": len(r["queries"]),
            "input_tokens": r["input_tokens"] + i,
            "output_tokens": r["output_tokens"] + o,
            "seen_urls": [s["url"] for s in r["sources"]],
            "allowed_urls": allowed,
            "spotify_names": {s["url"]: s["spotify_name"] for s in r["sources"]
                              if s.get("spotify_name")},
            "searched": r["searched"],
            "research": r,
            "raw": raw,
        }


def make_provider():
    name = (os.environ.get("ENRICH_PROVIDER") or "claude").strip().lower()
    if name == "gemini":
        if not os.environ.get("GEMINI_API_KEY", "").strip():
            return None, "GEMINI_API_KEY not set"
        return _Gemini2(), None
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
    for field in ("formats", "genres", "price_text", "start_time", "artists", "artist_links"):
        key = field
        if field in enr and prev.get(key) is not None:
            vals[key] = prev[key]
    if "formats" in enr:
        vals["primary_format"] = prev.get("primary_format")
    if "description" in enr and prev.get("descriptions"):
        vals["descriptions"] = prev["descriptions"]
    return vals


def apply_enrichment(ev: dict, enr: dict, vals: dict, stats: dict | None = None) -> dict:
    """Apply AI values to empty fields only; source values win (their
    enrichment entry is dropped).  Returns a new event dict."""
    ev = dict(ev)
    enr = json.loads(json.dumps(enr))   # deep copy
    cls = ev.get("classification") or {}
    method = cls.get("method")

    def count(key):
        if stats is not None:
            stats[key] = stats.get(key, 0) + 1

    if "formats" in vals and method not in ("manual", "source"):
        new = vals["formats"]
        if set(new) != set(ev.get("formats") or []):
            count("type_changed")
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

    if "genres" in vals and (method not in ("manual", "source") or not ev.get("genres")):
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
    res["artist_links"] = kept


def process_result(ev: dict, rec: dict, model: str, today: str, aliases: dict | None,
                   price_fetch=_fetch_page_text) -> tuple[dict, dict]:
    """Validate one provider result, verify the price, build the enrichment."""
    seen = None if rec["seen_urls"] is None else {u.split("?")[0] for u in rec["seen_urls"]}
    res = validate(rec["raw"], ev, seen, aliases, rec.get("allowed_urls"))
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
        res["price_ok"], why = verify_price(ev, res, price_fetch)
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
                     aliases: dict | None = None) -> tuple[list[dict], dict]:
    """Enrich events in the window. Returns (events, stats)."""
    stats: dict = {"window": 0, "cached": 0, "to_enrich": 0, "enriched": 0, "errors": 0,
                   "skipped_limit": 0, "skipped_timeout": 0, "searches": 0,
                   "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
                   "prices_dropped": 0, "dropped": [], "warnings": []}
    page_texts = page_texts or {}
    venues_map = {v["id"]: v for v in venues}
    month = today[:7]

    # one-off manual re-run of chosen events (workflow_dispatch input reenrich_ids)
    force = {i.strip() for i in os.environ.get("ENRICH_FORCE_IDS", "").split(",") if i.strip()}
    todo, out_by_id = [], {}
    for ev in events:
        if not in_window(ev, today):
            # keep cached AI values of events enriched earlier (e.g. moved date)
            c = cached_enrichment(ev, previous)
            if c:
                out_by_id[ev["id"]] = apply_enrichment(
                    ev, c["enrichment"], values_from_enrichment(c["enrichment"], c["prev"]))
            continue
        stats["window"] += 1
        c = None if ev["id"] in force else cached_enrichment(ev, previous)
        if c:
            stats["cached"] += 1
            out_by_id[ev["id"]] = apply_enrichment(
                ev, c["enrichment"], values_from_enrichment(c["enrichment"], c["prev"]))
        else:
            todo.append(ev)
    stats["to_enrich"] = len(todo)

    if todo and provider is None:
        provider, why = make_provider()
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
                left = MONTHLY_SEARCH_LIMIT - counter["count"] - reserved[0]
                if left <= 0:
                    return ev["id"], {"skip": "limit"}
                max_uses = min(getattr(provider, "reserve", MAX_SEARCHES_PER_EVENT), left)
                reserved[0] += max_uses
            venue = venues_map.get(ev["venue_id"], {})
            try:
                if hasattr(provider, "run_event"):      # Gemini two-step (task 058)
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
            res, conv = process_result(ev, rec, provider.model, today, aliases, price_fetch)
            if res["price"] and not ev.get("price_text") and not res.get("price_ok"):
                stats["prices_dropped"] += 1
            if rec.get("searched") is False:
                stats["not_searched"] = stats.get("not_searched", 0) + 1
            for d in res["dropped"]:
                stats["dropped"].append(f"{ev['id']}: {d}")
            out_by_id[ev["id"]] = apply_enrichment(ev, conv["enrichment"], conv["values"], stats)
            stats["enriched"] += 1

        pin, pout, psearch = provider.prices
        stats["cost_usd"] = round(stats["input_tokens"] * pin + stats["output_tokens"] * pout
                                  + stats["searches"] * psearch, 4)
        if stats["skipped_limit"]:
            stats["warnings"].append(
                f"AI search limit {MONTHLY_SEARCH_LIMIT}/month reached: "
                f"{stats['skipped_limit']} events wait for next month")
        if stats["skipped_timeout"]:
            stats["warnings"].append(f"AI enrichment: {stats['skipped_timeout']} events not "
                                     f"processed (timeout/stop), next run continues")

    if counter is not None:
        stats["month_searches"] = counter["count"]
    stats["limit"] = MONTHLY_SEARCH_LIMIT
    for w in stats["warnings"]:
        log.warning("%s", w)
    out = [out_by_id.get(e["id"], e) for e in events]
    log.info("enrich_ai: window=%d cached=%d enriched=%d errors=%d searches=%d month=%s/%d cost=$%.4f",
             stats["window"], stats["cached"], stats["enriched"], stats["errors"],
             stats["searches"], stats.get("month_searches"), MONTHLY_SEARCH_LIMIT, stats["cost_usd"])
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
    aliases = dict(approved_aliases or {})
    unmapped: dict[tuple, list] = {}
    for ev in events:
        for c in (ev.get("enrichment") or {}).get("genre_candidates") or []:
            raw = c.get("raw")
            if not raw:
                continue
            if c.get("maps_to"):
                aliases.setdefault(raw, c["maps_to"])
            elif raw not in aliases:
                unmapped.setdefault((raw, c.get("kind", "music")), []).append(ev["id"])
    proposals = [{"name": raw, "kind": kind, "count": len(ids), "event_ids": ids[:5]}
                 for (raw, kind), ids in unmapped.items() if len(ids) >= PROPOSAL_MIN_EVENTS]
    proposals.sort(key=lambda p: (-p["count"], p["name"]))
    return dict(sorted(aliases.items())), proposals
