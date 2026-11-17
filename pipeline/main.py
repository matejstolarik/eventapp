import datetime
import json
import logging
import os
import pathlib
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

from pipeline.adapters import rss as rss_adapter
from pipeline.adapters import jsonld as jsonld_adapter
from pipeline.adapters import html as html_adapter
from pipeline.adapters import api as api_adapter
from pipeline.normalize import normalize_event
from pipeline.dedup import dedup_events
from pipeline.checks import run_checks
from pipeline.classify import classify_events, apply_commercial_clubs
from pipeline.classify_ai import classify_events_ai
from pipeline.detail_enrich import enrich_missing_details
from pipeline.enrich_ai import enrich_events_ai, genre_tables
from pipeline.genres import load_aliases, rename_genres
from pipeline.price import parse_price
from pipeline.thumbs import generate_thumbs, generate_event_thumbs
from pipeline.fetch import USER_AGENT

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)


class _WarningCapture(logging.Handler):
    """Captures WARNING/ERROR records from pipeline.* loggers for the job summary."""
    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(self.format(record))

ADAPTERS = {"rss": rss_adapter, "jsonld": jsonld_adapter, "html": html_adapter,
            "api": api_adapter}
VENUES_PATH = pathlib.Path("data/venues.json")
OVERRIDES_PATH = pathlib.Path("data/overrides.json")
EVENTS_OUT = pathlib.Path("site/events.json")
STATE_OUT = pathlib.Path("site/pipeline_state.json")
GENRE_ALIASES_PATH = pathlib.Path("data/genre_aliases.json")
GENRE_ALIASES_OUT = pathlib.Path("site/genre_aliases.json")
GENRE_PROPOSALS_OUT = pathlib.Path("site/genre_proposals.json")
PRAGUE_TZ = ZoneInfo("Europe/Prague")


def load_previous_events() -> dict:
    """Load previous events for first_seen/last_seen tracking.

    In CI, fetches from the URL in PREVIOUS_EVENTS_URL env var (the published
    GitHub Pages address).  On first run the URL returns 404 — that is handled
    gracefully and the pipeline starts without state.

    Locally, falls back to the existing site/events.json file.
    """
    url = os.getenv("PREVIOUS_EVENTS_URL")
    if url:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            events = data.get("events", [])
            log.info("Previous events: %d loaded from %s", len(events), url)
            return {e["id"]: _migrate_event(e) for e in events}
        except Exception as exc:
            log.info("Previous events not available (%s) — starting without state", exc)
            return {}

    if not EVENTS_OUT.exists():
        return {}
    with EVENTS_OUT.open(encoding="utf-8") as f:
        data = json.load(f)
    return {e["id"]: _migrate_event(e) for e in data.get("events", [])}


def load_state() -> dict | None:
    """Load pipeline state kept between runs (task 054).

    The state file is published next to events.json on GitHub Pages
    (pipeline_state.json): detail-page price checks and the monthly AI search
    counter.  Returns {} when there is no state yet (HTTP 404 / no local file)
    and None when it could not be loaded for another reason — callers must
    then not spend limited resources (AI searches), because the counter is
    unknown.
    """
    url = os.getenv("PREVIOUS_EVENTS_URL")
    if url:
        state_url = url.rsplit("/", 1)[0] + "/" + STATE_OUT.name
        try:
            req = urllib.request.Request(state_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                state = json.loads(resp.read())
            log.info("Pipeline state loaded from %s", state_url)
            return state if isinstance(state, dict) else None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                log.info("Pipeline state not published yet — starting empty")
                return {}
            log.warning("Pipeline state not available (%s)", exc)
            return None
        except Exception as exc:
            log.warning("Pipeline state not available (%s)", exc)
            return None
    if not STATE_OUT.exists():
        return {}
    try:
        return json.loads(STATE_OUT.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("Pipeline state unreadable (%s)", exc)
        return None


def _prune_state(state: dict, events: list[dict]) -> dict:
    ids = {e["id"] for e in events}
    state["detail_checked"] = {k: v for k, v in (state.get("detail_checked") or {}).items()
                               if k in ids}
    return state


def _migrate_event(e: dict) -> dict:
    """Apply in-place migrations for schema changes (run once on load)."""
    # live → concert rename (task 019, 2026-11-08)
    fmts = e.get("formats")
    if fmts and "live" in fmts:
        e = dict(e)
        e["formats"] = ["concert" if f == "live" else f for f in fmts]
    return e


def main():
    capture = _WarningCapture()
    capture.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    logging.getLogger("pipeline").addHandler(capture)

    with VENUES_PATH.open(encoding="utf-8") as f:
        venues = json.load(f)

    overrides = []
    if OVERRIDES_PATH.exists():
        with OVERRIDES_PATH.open(encoding="utf-8") as f:
            overrides = json.load(f)

    previous = load_previous_events()
    loaded_state = load_state()
    state = dict(loaded_state or {})
    today = datetime.datetime.now(PRAGUE_TZ).date().isoformat()
    all_raw = []

    # Per-source results: (venue_id, source_label, event_count, warning)
    # warning is one of None / "zero_events" / "error"
    source_results: list[tuple] = []

    for venue in venues:
        if not venue.get("active", True):
            continue
        for source in venue.get("sources", []):
            adapter = ADAPTERS.get(source["type"])
            if adapter is None:
                log.warning("No adapter for source type '%s' (venue %s)", source["type"], venue["id"])
                source_results.append((venue["id"], source.get("type", "?"), 0, "error"))
                continue
            label = source.get("section") or source.get("strategy") or source["type"]
            try:
                raw_events = adapter.fetch(venue, source)
                count = len(raw_events)
                log.info("%s [%s]: %d events fetched", venue["id"], source["type"], count)
                warning = None
                if not raw_events:
                    log.warning("%s [%s]: 0 events — site layout may have changed",
                                venue["id"], source["type"])
                    warning = "zero_events"
                all_raw.extend(raw_events)
                source_results.append((venue["id"], label, count, warning))
            except Exception as exc:
                log.error("%s [%s]: %s", venue["id"], source["type"], exc)
                source_results.append((venue["id"], label, 0, "error"))

    previous_list = list(previous.values())
    events = [e for e in (normalize_event(r, previous) for r in all_raw) if e is not None]
    events = dedup_events(events)
    events = classify_events(events, venues, overrides)
    events, ai_stats = classify_events_ai(events, venues, previous_list)
    page_texts: dict[str, str] = {}
    events, enrich_stats = enrich_missing_details(events, previous, venues, check_prices=True,
                                                  state=state, today=today,
                                                  page_texts=page_texts)
    approved_aliases = load_aliases(GENRE_ALIASES_PATH)
    try:
        events, web_stats = enrich_events_ai(events, venues, previous,
                                             state if loaded_state is not None else None,
                                             today, page_texts=page_texts,
                                             aliases=approved_aliases)
    except Exception as exc:   # never stop the daily run
        log.warning("AI enrichment failed: %s", exc)
        web_stats = {"skipped": f"error: {exc}"[:200], "warnings": []}
    # commercial-club rule last: EPIC music events are always party (task 053)
    events = apply_commercial_clubs(events, venues)
    # task 058: renamed genre codes (r-n-b -> rnb), also in cached values
    for ev in events:
        if ev.get("genres"):
            ev["genres"] = rename_genres(ev["genres"])
        # task 058 part 4: structured price from the (source or AI) price text
        ev["price"] = parse_price(ev.get("price_text"))
        if ev["price"] and ev.get("free") is None and ev["price"]["kind"] in ("free", "free_reservation"):
            ev["free"] = True
    events = run_checks(events, previous)

    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)

    # Generate venue thumbnails; annotate each venue with image_thumb
    thumb_map = generate_thumbs(venues)
    venues_out = []
    for v in venues:
        ve = dict(v)
        ve["image_thumb"] = thumb_map.get(v.get("id", ""))
        venues_out.append(ve)

    # Generate event thumbnails; annotate each event with image_thumb
    event_thumb_map = generate_event_thumbs(events)
    events_out = []
    for ev in events:
        ev2 = dict(ev)
        ev2["image_thumb"] = event_thumb_map.get(ev.get("id", ""))
        events_out.append(ev2)

    generated_at = datetime.datetime.now(PRAGUE_TZ).isoformat()
    output = {
        "schema_version": 1,
        "generated_at": generated_at,
        "venues": venues_out,
        "events": events_out,
    }
    with EVENTS_OUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("Wrote %d events to %s", len(events_out), EVENTS_OUT)

    aliases, proposals = genre_tables(events_out, approved_aliases)
    GENRE_ALIASES_OUT.write_text(json.dumps(aliases, ensure_ascii=False, indent=1), encoding="utf-8")
    GENRE_PROPOSALS_OUT.write_text(json.dumps(proposals, ensure_ascii=False, indent=1),
                                   encoding="utf-8")

    state = _prune_state(state, events_out)
    state["updated_at"] = generated_at
    STATE_OUT.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

    new_total, new_per_venue = count_new_events(events_out, previous)
    log.info("New events: %d (per venue %s)", new_total, new_per_venue)

    _write_job_summary(source_results, events_out, generated_at, capture.messages, ai_stats,
                      enrich_stats, new_events=(new_total, new_per_venue, bool(previous)),
                      web_stats=web_stats, proposals=proposals)


def count_new_events(events: list[dict], previous: dict) -> tuple[int, dict[str, int]]:
    """Count events whose id was not in the previous run (task 052).

    Returns (total, {venue_id: count}) sorted by venue id.
    """
    per_venue: dict[str, int] = {}
    for e in events:
        if e["id"] not in previous:
            per_venue[e["venue_id"]] = per_venue.get(e["venue_id"], 0) + 1
    return sum(per_venue.values()), dict(sorted(per_venue.items()))


def _write_job_summary(source_results, events, generated_at, adapter_warnings=None,
                       ai_stats=None, enrich_stats=None, new_events=None,
                       web_stats=None, proposals=None):
    """Write a Markdown job summary to GITHUB_STEP_SUMMARY if running in CI."""
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    # Events per venue
    venue_counts: dict[str, int] = {}
    for e in events:
        venue_counts[e["venue_id"]] = venue_counts.get(e["venue_id"], 0) + 1

    # Collect warnings from source results
    warnings = [
        (vid, lbl, "0 events fetched")
        for vid, lbl, cnt, w in source_results if w == "zero_events"
    ] + [
        (vid, lbl, "source error / fetch failed")
        for vid, lbl, cnt, w in source_results if w == "error"
    ]

    # Quality flags
    flag_counts: dict[str, int] = {}
    for e in events:
        for flag in e.get("flags", []):
            flag_counts[flag] = flag_counts.get(flag, 0) + 1

    lines = [
        f"## Pipeline summary — {generated_at[:16]} Prague",
        "",
        "### Events per venue",
        "",
        "| Venue | Events |",
        "|---|---|",
    ]
    for vid, cnt in sorted(venue_counts.items()):
        lines.append(f"| {vid} | {cnt} |")

    lines += ["", f"**Total:** {len(events)} events", ""]

    if new_events is not None:
        new_total, new_per_venue, has_previous = new_events
        per = ", ".join(f"{v} {n}" for v, n in new_per_venue.items()) or "none"
        note = "" if has_previous else " — previous events unavailable, all counted as new"
        lines += [f"**New events:** {new_total} (per venue: {per}){note}", ""]

    all_warn_lines = [f"- `{vid}` [{lbl}]: {msg}" for vid, lbl, msg in warnings]
    if adapter_warnings:
        all_warn_lines += [f"- {w}" for w in adapter_warnings]

    if all_warn_lines:
        lines += ["### ⚠ Warnings", ""]
        lines += all_warn_lines
        lines.append("")
    else:
        lines += ["### Warnings", "", "None", ""]

    if flag_counts:
        lines += ["### Quality flags", ""]
        for flag, cnt in sorted(flag_counts.items()):
            lines.append(f"- `{flag}`: {cnt}")
        lines.append("")
    else:
        lines += ["### Quality flags", "", "None", ""]

    # Classification stats
    fmt_counts: dict[str, int] = {}
    method_counts: dict[str, int] = {}
    for e in events:
        for fmt in e.get("formats", []):
            fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
        cls = e.get("classification")
        m = cls.get("method") if cls else "null"
        method_counts[m] = method_counts.get(m, 0) + 1

    lines += ["### Classification", ""]
    lines += ["| Format | Count |", "|---|---|"]
    for fmt, cnt in sorted(fmt_counts.items()):
        lines.append(f"| {fmt} | {cnt} |")
    lines.append("")
    lines += ["| Method | Count |", "|---|---|"]
    for meth, cnt in sorted(method_counts.items()):
        lines.append(f"| {meth} | {cnt} |")
    lines.append("")

    if ai_stats:
        if ai_stats.get("skipped"):
            lines += [f"**AI layer:** skipped — {ai_stats.get('reason', '?')}", ""]
        else:
            cost = ai_stats.get("estimated_cost_usd", 0)
            lines += [
                "### AI layer (layer 2)",
                "",
                f"- Cache hits: {ai_stats.get('cache_hits', 0)}",
                f"- API calls: {ai_stats.get('api_calls', 0)}",
                f"- Errors: {ai_stats.get('errors', 0)}",
                f"- Input tokens: {ai_stats.get('total_input_tokens', 0):,}",
                f"- Output tokens: {ai_stats.get('total_output_tokens', 0):,}",
                f"- **Estimated cost: ${cost:.4f}**",
                "",
            ]

    # description / image_url coverage per venue
    desc_counts: dict[str, dict] = {}
    for e in events:
        vid = e["venue_id"]
        if vid not in desc_counts:
            desc_counts[vid] = {"desc": 0, "img": 0, "total": 0}
        desc_counts[vid]["total"] += 1
        if e.get("description"):
            desc_counts[vid]["desc"] += 1
        if e.get("image_url"):
            desc_counts[vid]["img"] += 1

    total_desc = sum(v["desc"] for v in desc_counts.values())
    total_img = sum(v["img"] for v in desc_counts.values())
    total_ev = len(events)

    lines += ["### description / image_url coverage", ""]
    lines += [f"**description:** {total_desc}/{total_ev} · "
              f"**image_url:** {total_img}/{total_ev}", ""]
    lines += ["| Venue | description | image_url |", "|---|---|---|"]
    for vid, d in sorted(desc_counts.items()):
        lines.append(f"| {vid} | {d['desc']}/{d['total']} | {d['img']}/{d['total']} |")
    lines.append("")

    if enrich_stats:
        lines += [
            "### Detail enrichment (task 021)",
            "",
            f"- New fetches: {enrich_stats.get('fetched', 0)}",
            f"- Cache hits: {enrich_stats.get('cache_hits', 0)}",
            f"- Skipped: {enrich_stats.get('skipped', 0)}",
            f"- Errors: {enrich_stats.get('errors', 0)}",
            f"- Price found on event page: {enrich_stats.get('price_found', 0)}",
            f"- Start time found on event page: {enrich_stats.get('time_found', 0)}",
            "",
        ]

    if web_stats is not None:
        lines += _web_summary_lines(web_stats, proposals or [])

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _web_summary_lines(st: dict, proposals: list) -> list[str]:
    """Job summary section of the AI enrichment with web search (task 054)."""
    lines = ["### AI enrichment with web search (task 054)", ""]
    for w in st.get("warnings") or []:
        lines.append(f"- ⚠ {w}")
    if st.get("skipped") and not st.get("enriched"):
        lines += [f"- Skipped: {st['skipped']}"]
    lines += [
        f"- Provider: {st.get('provider', '–')} {st.get('model', '')}",
        f"- **Searches this month: {st.get('month_searches', '?')} / {st.get('limit', '?')}**"
        f" (this run: {st.get('searches', 0)})",
        f"- **Run cost: ${st.get('cost_usd', 0):.4f}** (input {st.get('input_tokens', 0):,} /"
        f" output {st.get('output_tokens', 0):,} tokens)",
        f"- Events in 60 days: {st.get('window', 0)}, cached: {st.get('cached', 0)},"
        f" enriched now: {st.get('enriched', 0)}, errors: {st.get('errors', 0)},"
        f" waiting (limit): {st.get('skipped_limit', 0)},"
        f" waiting (timeout/stop): {st.get('skipped_timeout', 0)}",
        f"- Filled now: type changed {st.get('type_changed', 0)}, genres {st.get('genres', 0)},"
        f" price {st.get('price', 0)}, time {st.get('time', 0)},"
        f" description {st.get('description', 0)}, artists {st.get('artists', 0)},"
        f" Spotify {st.get('spotify', 0)}",
        f"- Prices dropped (not confirmed on the source page): {st.get('prices_dropped', 0)}",
        f"- Genre proposals (>= 3 events, not shown in the app): {len(proposals)}"
        + (": " + ", ".join(f"{p['name']} ({p['kind']}, {p['count']})" for p in proposals[:15])
           if proposals else ""),
        "",
    ]
    return lines


if __name__ == "__main__":
    main()
