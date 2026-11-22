import datetime
import json
import logging
import os
import pathlib
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

from pipeline import first_load
from pipeline.adapters import rss as rss_adapter
from pipeline.adapters import jsonld as jsonld_adapter
from pipeline.adapters import html as html_adapter
from pipeline.adapters import api as api_adapter
from pipeline.adapters import poster as poster_adapter
from pipeline import poster_merge
from pipeline.normalize import normalize_event
from pipeline.dedup import dedup_events
from pipeline.checks import run_checks
from pipeline.classify import (classify_events, apply_commercial_clubs, rename_format_fields,
                               venue_genre_ids)
from pipeline.classify_ai import classify_events_ai
from pipeline.detail_enrich import enrich_missing_details
from pipeline.enrich_ai import enrich_events_ai, genre_tables
from pipeline import research_store
from pipeline import manual as manual_mod
from pipeline.genres import finalize_genres, load_aliases, load_hierarchy
from pipeline.price import parse_price
from pipeline.thumbs import generate_venue_images, generate_event_images, event_detail_size
from pipeline.fetch import USER_AGENT
from pipeline import run_summary

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
            "api": api_adapter, "poster": poster_adapter}
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


def venue_image_problems(venues_out: list[dict]) -> list[dict]:
    """Active venues without a usable image (task 085): [{id, reason}],
    reason "no_image_url" or "download_failed" (image_card is null)."""
    out = []
    for v in venues_out:
        if not v.get("active", True):
            continue
        if not v.get("image_url"):
            out.append({"id": v["id"], "reason": "no_image_url"})
        elif not v.get("image_card"):
            out.append({"id": v["id"], "reason": "download_failed", "url": v["image_url"]})
    return out


def _prune_state(state: dict, events: list[dict]) -> dict:
    ids = {e["id"] for e in events}
    state["detail_checked"] = {k: v for k, v in (state.get("detail_checked") or {}).items()
                               if k in ids}
    state["detail_image"] = {k: v for k, v in (state.get("detail_image") or {}).items()
                             if k in ids}
    state["status_checked"] = {k: v for k, v in (state.get("status_checked") or {}).items()
                               if k in ids}
    # task 085: adapter detail caches of venues that are no longer active
    active = {e["venue_id"] for e in events}
    state["adapter_detail"] = {k: v for k, v in (state.get("adapter_detail") or {}).items()
                               if v and k in active}
    return state


def _migrate_event(e: dict) -> dict:
    """Apply in-place migrations for schema changes (run once on load)."""
    # live → concert rename (task 019, 2026-11-08)
    fmts = e.get("formats")
    if fmts and "live" in fmts:
        e = dict(e)
        e["formats"] = ["concert" if f == "live" else f for f in fmts]
    # comedy -> stand-up (task 065, 2026-11-18): cached formats keep the new code
    return rename_format_fields(e)


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
                # task 085: parsed detail pages kept between runs per venue
                cache = state.setdefault("adapter_detail", {}).setdefault(venue["id"], {})
                raw_events = adapter.fetch(venue, {**source, "detail_cache": cache})
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
    # task 090: an HTML event replaces the same event from a monthly poster
    events, poster_stats = poster_merge.merge(events, previous)
    if poster_stats["poster"] or poster_stats["replaced"]:
        log.info("poster events: %d, replaced by HTML: %d", poster_stats["poster"],
                 poster_stats["replaced"])
    events = classify_events(events, venues, overrides)
    manual = manual_mod.load()          # task 060: data/manual.json
    events, _ = manual_mod.apply_manual(events, manual, today)
    # task 062: DeepSeek budget shared by AI classification and AI enrichment
    # (per run and per calendar month, recorded in pipeline_state.json)
    ai_budget = None
    if (os.environ.get("ENRICH_PROVIDER") or "").strip().lower() == "deepseek" \
            and loaded_state is not None:
        from pipeline.deepseek import daily_budget
        ai_budget = daily_budget(state, today)
        ai_budget.add(poster_adapter.take_spend())     # task 090: poster readings this run
        log.info("DeepSeek budget this run: $%.4f (month spent before $%.4f)",
                 ai_budget.limit, ai_budget.month_spent_before)
    keep_genres = venue_genre_ids(events)  # task 063: before the AI changes the type
    events, ai_stats = classify_events_ai(events, venues, previous_list, budget=ai_budget,
                                          today=today)
    page_texts: dict[str, str] = {}
    events, enrich_stats = enrich_missing_details(events, previous, venues, check_prices=True,
                                                  state=state, today=today,
                                                  page_texts=page_texts)
    approved_aliases = load_aliases(GENRE_ALIASES_PATH)
    research = research_store.load(today)      # task 059: stored AI research
    try:
        events, web_stats = enrich_events_ai(events, venues, previous,
                                             state if loaded_state is not None else None,
                                             today, page_texts=page_texts,
                                             aliases=approved_aliases, research=research,
                                             budget=ai_budget, keep_genres=keep_genres)
    except Exception as exc:   # never stop the daily run
        log.warning("AI enrichment failed: %s", exc)
        web_stats = {"skipped": f"error: {exc}"[:200], "warnings": []}
    if ai_budget is not None:
        from pipeline.deepseek import record_spend
        cost = record_spend(state, today, ai_budget)
        web_stats["budget"] = {"run_limit_usd": ai_budget.limit,
                               "run_spent_usd": round(ai_budget.spent, 4),
                               "month": cost["month"], "month_spent_usd": cost["usd"]}
    # task 074: DeepSeek account balance after the AI step (alert below $0.20)
    if (os.environ.get("ENRICH_PROVIDER") or "").strip().lower() == "deepseek":
        try:
            from pipeline.deepseek import balance_usd
            web_stats["balance_usd"] = balance_usd()
            log.info("DeepSeek balance: %s USD", web_stats["balance_usd"])
        except Exception as exc:   # never stop the daily run
            log.warning("DeepSeek balance not available: %s", exc)
    try:
        web_stats["research_bytes"] = research_store.save(research, today)
    except OSError as exc:
        log.warning("research store not written: %s", exc)
    # commercial-club rule last: EPIC music events are always party (task 053)
    events = apply_commercial_clubs(events, venues)
    # task 060: manual additions win over AI and source (again, after the AI step)
    events, manual_stats = manual_mod.apply_manual(events, manual, today)
    events, link_stats = manual_mod.apply_artist_links(events, manual, today)
    web_stats["manual"] = {**manual_stats, **link_stats}
    # task 058: renamed genre codes (r-n-b -> rnb), also in cached values;
    # task 065: no umbrella-only codes (alternative), C7 parent removal
    hierarchy = load_hierarchy()
    for i, ev in enumerate(events):
        ev = events[i] = rename_format_fields(ev)      # task 065: comedy -> stand-up
        if ev.get("genres"):
            ev["genres"] = finalize_genres(ev["genres"], hierarchy)
        # task 058 part 4: structured price from the (source or AI) price text
        ev["price"] = parse_price(ev.get("price_text"))
        if ev["price"] and ev.get("free") is None and ev["price"]["kind"] in ("free", "free_reservation"):
            ev["free"] = True
    events = run_checks(events, previous)

    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)

    # Venue images: image_thumb, and (task 082) image_card / image_detail /
    # image_detail_size, which the app shows when an event has no image
    venue_image_map = generate_venue_images(venues)
    # task 086: events of a venue's first load are not "new" in the app
    first_loaded = first_load.update(state, events, previous, today)
    venues_out = []
    for v in venues:
        ve = dict(v)
        ve["first_loaded"] = first_loaded.get(v.get("id"))
        ve.update(venue_image_map.get(v.get("id", ""), {}) or {
            "image_thumb": None, "image_card": None, "image_detail": None,
            "image_detail_size": None})
        venues_out.append(ve)
    # task 085: every active venue needs an image (the fallback of events
    # without a poster) -> alert when it has no image_url or no image_card
    venue_images_missing = venue_image_problems(venues_out)

    # Generate event thumbnails (image_thumb) and detail copies (image_detail, task 066)
    # task 067: listing image as fallback when the event-page image is broken
    fallbacks = {k: v["listing"] for k, v in (state.get("detail_image") or {}).items()
                 if isinstance(v, dict) and v.get("listing")}
    used_fallback: dict[str, str] = {}
    event_image_map = generate_event_images(events, fallbacks, used_fallback)
    events_out = []
    for ev in events:
        ev2 = dict(ev)
        if ev2.get("id") in used_fallback:
            ev2["image_url"] = used_fallback[ev2["id"]]
        thumb, detail = event_image_map.get(ev.get("id", ""), (None, None))
        ev2["image_thumb"] = thumb
        ev2["image_detail"] = detail
        # task 069: detail size so the event page can reserve the image space
        ev2["image_detail_size"] = event_detail_size(ev2["id"]) if detail else None
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

    # task 057: daily numbers for alerts and the weekly report
    try:
        summary = run_summary.build(events_out, previous, source_results, today, generated_at,
                                    ai_stats=ai_stats, web_stats=web_stats, proposals=proposals,
                                    warnings=capture.messages,
                                    venue_images_missing=venue_images_missing,
                                    simulate_zero=run_summary.simulate_zero_venue())
        log.info("Run summary written to %s", run_summary.save(summary))
    except Exception as exc:   # never stop the daily run
        log.warning("run summary not written: %s", exc)

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


def _dropped_kinds(dropped: list[str]) -> dict:
    """'<id>: genre x: why' -> {'genre': n, 'price': n, ...} (task 062)."""
    out: dict = {}
    for d in dropped:
        what = d.split(": ", 1)[-1]
        kind = what.split(" ", 1)[0].split(":", 1)[0].split("'", 1)[0]
        out[kind] = out.get(kind, 0) + 1
    return out


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
        f"- Manual (data/manual.json): series {(st.get('manual') or {}).get('series', 0)},"
        f" events {(st.get('manual') or {}).get('events', 0)},"
        f" Spotify attached {(st.get('manual') or {}).get('attached', 0)},"
        f" AI Spotify links dropped {(st.get('manual') or {}).get('ai_dropped', 0)}",
        f"- Dropped by guards (task 062): {_dropped_kinds(st.get('dropped') or [])};"
        f" to review (no description left, task 063): {len(st.get('review') or [])};"
        f" venue / hall in description (no review): {st.get('venue_in_description', 0)};"
        f" primary_format from stored research: {st.get('primary_from_research', 0)};"
        f" kept previous AI values (not processed): {st.get('kept_previous', 0)}",
        f"- DeepSeek budget: {st.get('budget') or '–'}",
        f"- Task 065: genres re-mapped from stored results (no API):"
        f" {len(st.get('genres_remapped') or [])}; cached descriptions dropped"
        f" (model set needs_review): {len(st.get('descriptions_dropped_review') or [])}",
        f"- Task 078: talk genres changed (from text, no API): {len(st.get('talk_genres') or [])}",
        f"- Re-run from stored research (no search): {st.get('from_research', 0)};"
        f" research files: {st.get('research_bytes') or '–'}",
        f"- Genre proposals (>= 3 events, not shown in the app): {len(proposals)}"
        + (": " + ", ".join(f"{p['name']} ({p['kind']}, {p['count']})" for p in proposals[:15])
           if proposals else ""),
        "",
    ]
    return lines


if __name__ == "__main__":
    main()
