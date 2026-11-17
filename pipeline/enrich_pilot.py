"""
Task 052 pilot: AI enrichment with web search — Claude vs. Gemini.

Run manually only (workflow .github/workflows/enrich-pilot.yml).  Does NOT
modify events.json or the daily run.  Writes results to a JSON file
(uploaded as a workflow artifact) and a Markdown summary to
GITHUB_STEP_SUMMARY.

For each of 20 selected events, each provider gets one request (one
"conversation") that may use at most 3 web searches and returns a structured
result: formats/genres (fixed lists), artists + Spotify artist URL, price,
start time, Czech description — each value with a source URL.

Mode A: the event data the pipeline already has (title, venue, date, source
URL, description from the source/detail page) is put into the prompt; the
model is told to search only for what is missing there.

Rules enforced in code (not only in the prompt):
  - ra.co is blocked in the Claude tool; any value whose source_url is on
    ra.co is discarded for both providers (Gemini cannot block domains).
  - price / start_time / spotify / description without source_url are dropped.
  - Spotify URL must match open.spotify.com/artist/<id>.
  - formats/genres outside the fixed lists are dropped.
  - Hard cap per provider: MAX_SEARCHES total web searches.

Environment:
  ANTHROPIC_API_KEY, GEMINI_API_KEY (either may be missing → provider skipped)
  PILOT_EVENTS_URL  (default: published events.json)
  PILOT_PROVIDERS   (default "claude,gemini")
  PILOT_OUT         (default "pilot-out/enrich_pilot.json")
"""

import datetime
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from pipeline.classify_ai import VALID_FORMATS, VALID_GENRES
from pipeline.fetch import USER_AGENT

log = logging.getLogger("pipeline.enrich_pilot")

PRAGUE_TZ = ZoneInfo("Europe/Prague")
DEFAULT_EVENTS_URL = "https://matejstolarik.github.io/eventapp/events.json"

N_EVENTS = 20
MAX_SEARCHES = 60          # per provider, whole pilot
MAX_SEARCHES_PER_EVENT = 3
BLOCKED_DOMAINS = ["ra.co"]

CLAUDE_MODEL = "claude-haiku-5-5"
CLAUDE_IN_PRICE = 0.10 / 1e6     # USD per input token
CLAUDE_OUT_PRICE = 0.50 / 1e6    # USD per output token
CLAUDE_SEARCH_PRICE = 10.0 / 1000  # USD per web search

GEMINI_MODEL = "gemini-2.5-flash-lite"   # free tier: grounding up to 500 RPD
GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              f"{GEMINI_MODEL}:generateContent")
GEMINI_DELAY_S = 6.0   # stay well under free-tier RPM

REQUIRED_VENUES = ["cross-club", "fuchs2", "bike-jesus", "palac-akropolis",
                   "meetfactory", "epic", "archa-plus"]
_MUSIC = {"concert", "dj", "party", "music"}
_PARTY_WORDS = re.compile(r"party|párty|night|rave|noc|club|klub|disco|techno", re.I)
_SPOTIFY_RE = re.compile(r"^https://open\.spotify\.com/(intl-[a-z]+/)?artist/[A-Za-z0-9]{22}")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


# ---------------------------------------------------------------------------
# Event selection
# ---------------------------------------------------------------------------

def suspicion_reasons(ev: dict) -> list[str]:
    """Why today's type/genre looks doubtful (empty list = looks fine)."""
    fmts = set(ev.get("formats") or [])
    reasons = []
    if not fmts or fmts <= {"music", "other"}:
        reasons.append("typ neurčený (music/other/prázdny)")
    if fmts & _MUSIC and not ev.get("genres"):
        reasons.append("hudobná akcia s prázdnymi žánrami")
    if "party" in fmts and not _PARTY_WORDS.search(ev.get("title", "")):
        reasons.append("party bez signálu v názve – môže byť koncert / dj")
    elif "party" in fmts:
        reasons.append("party – overiť podľa novej definície (komerčná párty vs. dj noc)")
    if "party" in fmts and "concert" in fmts:
        reasons.append("party + concert naraz")
    cls = ev.get("classification") or {}
    if cls.get("method") == "llm" and float(cls.get("confidence") or 1) < 0.7:
        reasons.append(f"nízka istota AI ({cls.get('confidence')})")
    return reasons


def select_events(events: list[dict], today: str, n: int = N_EVENTS) -> list[dict]:
    """Deterministic pick of n upcoming events without price.

    Round-robin over venues (required venues first); within a venue prefer
    suspicious events, then events without description, then formats not yet
    covered.  Returns copies with a 'pilot_reasons' list.
    """
    pool = [e for e in events
            if e.get("date", "") > today and not e.get("price_text")
            and e.get("status") != "cancelled"
            and not re.search(r"cancel|zrušen|vyprodáno|sold out", e.get("title", ""), re.I)]
    by_venue: dict[str, list[dict]] = {}
    for e in sorted(pool, key=lambda e: (e["date"], e["id"])):
        by_venue.setdefault(e["venue_id"], []).append(e)

    venues = [v for v in REQUIRED_VENUES if v in by_venue]
    venues += sorted(v for v in by_venue if v not in REQUIRED_VENUES)

    picked: list[dict] = []
    seen_formats: set[str] = set()
    n_susp = n_nodesc = 0

    def score(e):
        susp = bool(suspicion_reasons(e))
        nodesc = not e.get("description")
        new_fmt = bool(set(e.get("formats") or []) - seen_formats)
        return (susp and n_susp < 8, nodesc and n_nodesc < 7, new_fmt)

    round_ = 0
    strict = True   # after round 0, skip uninteresting optional venues
    while len(picked) < n and any(by_venue[v] for v in venues):
        before = len(picked)
        for v in venues:
            if len(picked) >= n:
                break
            if not by_venue[v]:
                continue
            best = max(by_venue[v], key=score)
            if (strict and round_ > 0 and v not in REQUIRED_VENUES
                    and not any(score(best))):
                continue
            by_venue[v].remove(best)
            reasons = suspicion_reasons(best)
            why = list(reasons)
            if not best.get("description"):
                why.append("bez popisu")
                n_nodesc += 1
            if reasons:
                n_susp += 1
            if not why:
                why.append("nový typ/podnik do vzorky")
            why.append("bez ceny")
            seen_formats |= set(best.get("formats") or [])
            picked.append({**best, "pilot_reasons": why})
        if len(picked) == before:
            strict = False
        round_ += 1
    return picked


# ---------------------------------------------------------------------------
# Prompt + output schema (shared by both providers)
# ---------------------------------------------------------------------------

_SYSTEM = f"""\
You enrich data about one event at a Prague venue. Accuracy matters more than \
completeness: leave a field empty (null / []) when you are not sure.

Rules:
- First use the EVENT DATA given to you (mode A). Search the web only for what \
is missing there. At most {MAX_SEARCHES_PER_EVENT} searches.
- Never use ra.co (Resident Advisor) as a source.
- formats: only from {sorted(VALID_FORMATS)}. "party" = a big commercial / \
mainstream party where people go for the atmosphere, not for specific music or \
a specific performer (commercial clubs, Erasmus/student parties, 80s/90s hits, \
open bar, mainstream themed nights). A club night focused on the music or the \
DJs is "dj", NOT "party". A band concert is "concert". Use "party" only with a \
clear signal and give the reason in party_reason.
- genres: only from {sorted(VALID_GENRES)}; [] if unsure.
- formats/genres: give source_url (page that supports it) or null if derived \
from the event text only; confidence 0-1.
- artists: performer names. spotify_url only an open.spotify.com/artist/... URL \
that literally appeared in your search results AND clearly is this artist; \
otherwise null.
- price: only if explicitly stated for THIS event and THIS date (e.g. \
"250 Kč", "200–350 Kč", "zdarma"), with source_url. Otherwise null.
- start_time: HH:MM, only if missing in EVENT DATA and explicitly stated, with \
source_url.
- description_cs: only if EVENT DATA has no description. 2-3 sentences in \
Czech, in your own words (do not copy), with source_urls.
- Every source_url must be a real page you saw (event data source or search \
result)."""

_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "formats": {"type": "array", "items": {"type": "string"}},
        "genres": {"type": "array", "items": {"type": "string"}},
        "type_source_url": {"type": ["string", "null"]},
        "type_confidence": {"type": "number"},
        "party_reason": {"type": ["string", "null"]},
        "artists": {"type": "array", "items": {"type": "string"}},
        "spotify": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "artist": {"type": "string"},
                    "url": {"type": "string"},
                    "source_url": {"type": ["string", "null"]},
                },
                "required": ["artist", "url"],
            },
        },
        "price": {"type": ["string", "null"]},
        "price_source_url": {"type": ["string", "null"]},
        "start_time": {"type": ["string", "null"]},
        "start_time_source_url": {"type": ["string", "null"]},
        "description_cs": {"type": ["string", "null"]},
        "description_source_urls": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    },
    "required": ["formats", "genres", "type_confidence", "artists", "price",
                 "start_time", "description_cs"],
}

_REPORT_TOOL = {
    "name": "report_enrichment",
    "description": "Report the final enrichment result for the event. Call exactly once, at the end.",
    "input_schema": _RESULT_SCHEMA,
}


def build_event_prompt(ev: dict, venue: dict) -> str:
    src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
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
        f"Source page: {src or '(none)'}",
        f"Description: {ev.get('description') or '(missing)'}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation (same for both providers)
# ---------------------------------------------------------------------------

def _blocked(url) -> bool:
    if not url:
        return False
    host = re.sub(r"^https?://", "", str(url)).split("/")[0].lower()
    return any(host == d or host.endswith("." + d) for d in BLOCKED_DOMAINS)


def validate_result(raw: dict, ev: dict, seen_urls: set[str] | None = None) -> dict:
    """Apply the pilot rules to a raw model result. Returns a clean dict with
    'dropped' listing what was removed and why."""
    dropped = []
    out: dict = {}

    def url_ok(url, field):
        if not url:
            return False
        if _blocked(url):
            dropped.append(f"{field}: ra.co source")
            return False
        return True

    fmts = [f for f in raw.get("formats") or [] if f in VALID_FORMATS]
    gens = [g for g in raw.get("genres") or [] if g in VALID_GENRES]
    bad = [x for x in (raw.get("formats") or []) + (raw.get("genres") or [])
           if x not in VALID_FORMATS and x not in VALID_GENRES]
    if bad:
        dropped.append(f"invalid formats/genres {bad}")
    type_src = raw.get("type_source_url")
    if type_src and _blocked(type_src):
        dropped.append("type: ra.co source")
        type_src = None
    out["formats"] = fmts
    out["genres"] = gens
    out["type_source_url"] = type_src
    out["type_is_estimate"] = not type_src
    out["type_confidence"] = raw.get("type_confidence")
    out["party_reason"] = raw.get("party_reason")
    if "party" in fmts and not raw.get("party_reason"):
        dropped.append("party: no party_reason")
        out["formats"] = [f for f in fmts if f != "party"]

    out["artists"] = [a for a in raw.get("artists") or [] if isinstance(a, str)][:10]
    spot = []
    for s in raw.get("spotify") or []:
        url = (s or {}).get("url") or ""
        if not _SPOTIFY_RE.match(url):
            dropped.append(f"spotify: not an artist URL ({url[:60]})")
            continue
        if seen_urls is not None and url.split("?")[0] not in seen_urls:
            dropped.append(f"spotify: URL not in search results ({url[:60]})")
            continue
        spot.append({"artist": s.get("artist"), "url": url.split("?")[0],
                     "source_url": s.get("source_url") or url})
    out["spotify"] = spot

    price, psrc = raw.get("price"), raw.get("price_source_url")
    if price and url_ok(psrc, "price"):
        out["price"], out["price_source_url"] = price, psrc
    else:
        if price:
            dropped.append("price: no valid source_url")
        out["price"] = out["price_source_url"] = None

    st, ssrc = raw.get("start_time"), raw.get("start_time_source_url")
    if st and ev.get("start_time"):
        dropped.append("start_time: event already has one")
        st = None
    if st and not _TIME_RE.match(str(st)):
        dropped.append(f"start_time: bad format {st}")
        st = None
    if st and url_ok(ssrc, "start_time"):
        out["start_time"], out["start_time_source_url"] = st, ssrc
    else:
        if st:
            dropped.append("start_time: no valid source_url")
        out["start_time"] = out["start_time_source_url"] = None

    desc = raw.get("description_cs")
    dsrc = [u for u in raw.get("description_source_urls") or [] if not _blocked(u)]
    if desc and ev.get("description"):
        dropped.append("description: event already has one")
        desc = None
    if desc and not dsrc:
        dropped.append("description: no source_urls")
        desc = None
    out["description_cs"] = desc
    out["description_source_urls"] = dsrc if desc else []
    out["notes"] = raw.get("notes")
    out["dropped"] = dropped
    return out


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------

def run_claude(events, venues_map, budget):
    import anthropic

    client = anthropic.Anthropic()
    tool_type = "web_search_20260209"
    results = []
    totals = {"input_tokens": 0, "output_tokens": 0, "searches": 0, "errors": 0}

    for ev in events:
        if totals["searches"] >= budget:
            results.append({"id": ev["id"], "skipped": "search budget reached"})
            continue
        prompt = build_event_prompt(ev, venues_map.get(ev["venue_id"], {}))
        max_uses = min(MAX_SEARCHES_PER_EVENT, budget - totals["searches"])
        messages = [{"role": "user", "content": prompt + "\n\nWhen done, call report_enrichment."}]
        rec = {"id": ev["id"], "searches": 0, "search_queries": [], "seen_urls": []}
        try:
            for _turn in range(4):   # pause_turn continuation
                tools = [
                    {"type": tool_type, "name": "web_search", "max_uses": max_uses,
                     "blocked_domains": BLOCKED_DOMAINS},
                    _REPORT_TOOL,
                ]
                try:
                    resp = client.messages.create(
                        model=CLAUDE_MODEL, max_tokens=4096,
                        output_config={"effort": "low"},
                        system=_SYSTEM, tools=tools, messages=messages,
                    )
                except anthropic.BadRequestError as exc:
                    if tool_type == "web_search_20260209" and "web_search" in str(exc):
                        log.warning("claude: %s not accepted, falling back to web_search_20250305", tool_type)
                        tool_type = "web_search_20250305"
                        continue
                    raise
                u = resp.usage
                totals["input_tokens"] += u.input_tokens
                totals["output_tokens"] += u.output_tokens
                stu = getattr(u, "server_tool_use", None)
                n_search = getattr(stu, "web_search_requests", 0) or 0 if stu else 0
                rec["searches"] += n_search
                totals["searches"] += n_search
                report = None
                for b in resp.content:
                    if b.type == "server_tool_use" and getattr(b, "name", "") == "web_search":
                        rec["search_queries"].append((b.input or {}).get("query"))
                    elif b.type == "web_search_tool_result":
                        content = b.content
                        if isinstance(content, list):
                            rec["seen_urls"] += [r.url for r in content if getattr(r, "url", None)]
                        else:
                            rec.setdefault("search_errors", []).append(
                                getattr(content, "error_code", str(content)))
                    elif b.type == "tool_use" and b.name == "report_enrichment":
                        report = b.input
                    elif b.type == "text" and getattr(b, "citations", None):
                        rec["seen_urls"] += [c.url for c in b.citations if getattr(c, "url", None)]
                if report is not None:
                    rec["raw"] = report
                    break
                if resp.stop_reason == "pause_turn":
                    messages.append({"role": "assistant", "content": resp.content})
                    continue
                if resp.stop_reason == "end_turn":
                    messages.append({"role": "assistant", "content": resp.content})
                    messages.append({"role": "user", "content": "Call report_enrichment now with your result."})
                    max_uses = 0
                    continue
                rec["error"] = f"stop_reason={resp.stop_reason}"
                break
            else:
                rec["error"] = "no report_enrichment after 4 turns"
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"
        if "raw" in rec:
            seen = {u.split("?")[0] for u in rec["seen_urls"]}
            rec["result"] = validate_result(rec["raw"], ev, seen)
        else:
            totals["errors"] += 1
        rec["tool_type"] = tool_type
        results.append(rec)
        log.info("claude %s: %d searches%s", ev["id"], rec.get("searches", 0),
                 f" ERROR {rec['error']}" if rec.get("error") else "")

    cost = (totals["input_tokens"] * CLAUDE_IN_PRICE + totals["output_tokens"] * CLAUDE_OUT_PRICE
            + totals["searches"] * CLAUDE_SEARCH_PRICE)
    totals["cost_usd"] = round(cost, 4)
    totals["model"] = CLAUDE_MODEL
    return results, totals


# ---------------------------------------------------------------------------
# Gemini (REST, stdlib only)
# ---------------------------------------------------------------------------

def _gemini_call(api_key: str, body: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        GEMINI_URL, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key,
                 "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")[:2000]


def _parse_json_text(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def run_gemini(events, venues_map, budget):
    api_key = os.environ["GEMINI_API_KEY"].strip()
    results = []
    totals = {"input_tokens": 0, "output_tokens": 0, "searches": 0, "errors": 0,
              "model": GEMINI_MODEL, "stopped": None}
    schema_hint = json.dumps(_RESULT_SCHEMA["properties"], ensure_ascii=False)

    for i, ev in enumerate(events):
        if totals["stopped"]:
            results.append({"id": ev["id"], "skipped": totals["stopped"]})
            continue
        if totals["searches"] >= budget:
            results.append({"id": ev["id"], "skipped": "search budget reached"})
            continue
        if i:
            time.sleep(GEMINI_DELAY_S)
        prompt = (build_event_prompt(ev, venues_map.get(ev["venue_id"], {}))
                  + "\n\nAnswer with ONLY one JSON object with these keys: " + schema_hint)
        body = {
            "systemInstruction": {"parts": [{"text": _SYSTEM}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048},
        }
        rec = {"id": ev["id"]}
        status, data = _gemini_call(api_key, body)
        if status != 200:
            rec["error"] = f"HTTP {status}: {data}"
            totals["errors"] += 1
            # Free-tier limit / grounding not allowed → stop the Gemini part
            if status in (429, 403) or (status == 400 and "search" in str(data).lower()):
                totals["stopped"] = f"stopped after HTTP {status}"
            results.append(rec)
            log.warning("gemini %s: HTTP %s", ev["id"], status)
            continue
        um = data.get("usageMetadata", {})
        totals["input_tokens"] += um.get("promptTokenCount", 0)
        totals["output_tokens"] += um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)
        cand = (data.get("candidates") or [{}])[0]
        gm = cand.get("groundingMetadata") or {}
        queries = gm.get("webSearchQueries") or []
        chunks = [c.get("web", {}) for c in gm.get("groundingChunks") or []]
        rec["searches"] = len(queries)
        rec["search_queries"] = queries
        rec["grounding_sources"] = [{"title": c.get("title"), "uri": c.get("uri")} for c in chunks]
        rec["ra_in_grounding"] = any("ra.co" == (c.get("title") or "").lower()
                                     or _blocked(c.get("uri")) for c in chunks)
        totals["searches"] += len(queries)
        text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []))
        raw = _parse_json_text(text)
        if raw is None:
            rec["error"] = f"no JSON in answer (finishReason={cand.get('finishReason')}): {text[:300]}"
            totals["errors"] += 1
        else:
            rec["raw"] = raw
            # Gemini only exposes redirect URIs for grounding chunks, so the
            # spotify check against seen URLs is done on the domain titles.
            res = validate_result(raw, ev, None)
            if res["spotify"] and not any("spotify" in (c.get("title") or "") for c in chunks):
                res["dropped"].append("spotify: no spotify.com page in grounding sources")
                res["spotify"] = []
            res["ra_in_grounding"] = rec["ra_in_grounding"]
            rec["result"] = res
        results.append(rec)
        log.info("gemini %s: %d searches%s", ev["id"], rec.get("searches", 0),
                 f" ERROR {rec['error'][:120]}" if rec.get("error") else "")

    totals["cost_usd_if_paid"] = round(totals["input_tokens"] * 0.10 / 1e6
                                       + totals["output_tokens"] * 0.40 / 1e6, 4)
    return results, totals


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_events(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _fmt(res: dict | None) -> str:
    if not res:
        return "—"
    s = ",".join(res["formats"]) + " / " + (",".join(res["genres"]) or "∅")
    return s + (" (odhad)" if res.get("type_is_estimate") else "")


def write_summary(path, selected, out):
    lines = ["## Enrich pilot (task 052)", ""]
    for prov in ("claude", "gemini"):
        t = out.get(prov, {}).get("totals")
        if t:
            lines.append(f"- **{prov}**: {json.dumps(t, ensure_ascii=False)}")
    lines += ["", "| # | Akcia | Dnes | Claude | Gemini |", "|---|---|---|---|---|"]
    by = {p: {r["id"]: r for r in out.get(p, {}).get("results", [])} for p in ("claude", "gemini")}
    for i, ev in enumerate(selected, 1):
        today = ",".join(ev.get("formats") or []) + " / " + (",".join(ev.get("genres") or []) or "∅")
        c = by["claude"].get(ev["id"], {})
        g = by["gemini"].get(ev["id"], {})
        lines.append(f"| {i} | {ev['venue_id']}: {ev['title'][:40]} | {today} | "
                     f"{_fmt(c.get('result')) if 'result' in c else c.get('error', c.get('skipped', '—'))[:60]} | "
                     f"{_fmt(g.get('result')) if 'result' in g else g.get('error', g.get('skipped', '—'))[:60]} |")
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    data = _load_events(os.environ.get("PILOT_EVENTS_URL", DEFAULT_EVENTS_URL))
    venues_map = {v["id"]: v for v in data.get("venues", [])}
    today = datetime.datetime.now(PRAGUE_TZ).date().isoformat()
    selected = select_events(data["events"], today)
    log.info("selected %d events", len(selected))

    providers = [p.strip() for p in os.environ.get("PILOT_PROVIDERS", "claude,gemini").split(",")]
    out: dict = {
        "generated_at": datetime.datetime.now(PRAGUE_TZ).isoformat(),
        "events_generated_at": data.get("generated_at"),
        "selected": [{k: ev.get(k) for k in ("id", "venue_id", "title", "date", "start_time",
                                              "formats", "genres", "artists", "price_text",
                                              "description", "classification", "sources",
                                              "pilot_reasons")} for ev in selected],
    }
    if "claude" in providers:
        if os.environ.get("ANTHROPIC_API_KEY", "").strip():
            res, tot = run_claude(selected, venues_map, MAX_SEARCHES)
            out["claude"] = {"results": res, "totals": tot}
        else:
            out["claude"] = {"totals": {"skipped": "ANTHROPIC_API_KEY not set"}}
    if "gemini" in providers:
        if os.environ.get("GEMINI_API_KEY", "").strip():
            res, tot = run_gemini(selected, venues_map, MAX_SEARCHES)
            out["gemini"] = {"results": res, "totals": tot}
        else:
            out["gemini"] = {"totals": {"skipped": "GEMINI_API_KEY not set"}}

    out_path = Path(os.environ.get("PILOT_OUT", "pilot-out/enrich_pilot.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("wrote %s", out_path)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        write_summary(os.environ["GITHUB_STEP_SUMMARY"], selected, out)


if __name__ == "__main__":
    main()
