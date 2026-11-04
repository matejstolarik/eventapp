import datetime
import json
import logging
import os
import pathlib
import urllib.request
from zoneinfo import ZoneInfo

from pipeline.adapters import rss as rss_adapter
from pipeline.adapters import jsonld as jsonld_adapter
from pipeline.adapters import html as html_adapter
from pipeline.adapters import api as api_adapter
from pipeline.normalize import normalize_event
from pipeline.dedup import dedup_events
from pipeline.checks import run_checks
from pipeline.classify import classify_events

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
            req = urllib.request.Request(url, headers={"User-Agent": "eventapp-pipeline/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            events = data.get("events", [])
            log.info("Previous events: %d loaded from %s", len(events), url)
            return {e["id"]: e for e in events}
        except Exception as exc:
            log.info("Previous events not available (%s) — starting without state", exc)
            return {}

    if not EVENTS_OUT.exists():
        return {}
    with EVENTS_OUT.open(encoding="utf-8") as f:
        data = json.load(f)
    return {e["id"]: e for e in data.get("events", [])}


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

    events = [normalize_event(r, previous) for r in all_raw]
    events = dedup_events(events)
    events = classify_events(events, venues, overrides)
    events = run_checks(events, previous)

    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.datetime.now(PRAGUE_TZ).isoformat()
    output = {
        "schema_version": 1,
        "generated_at": generated_at,
        "venues": venues,
        "events": events,
    }
    with EVENTS_OUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("Wrote %d events to %s", len(events), EVENTS_OUT)

    _write_job_summary(source_results, events, generated_at, capture.messages)


def _write_job_summary(source_results, events, generated_at, adapter_warnings=None):
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

    with open(summary_path, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
