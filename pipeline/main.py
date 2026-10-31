import datetime
import json
import logging
import pathlib
from zoneinfo import ZoneInfo

from pipeline.adapters import rss as rss_adapter
from pipeline.adapters import jsonld as jsonld_adapter
from pipeline.normalize import normalize_event
from pipeline.dedup import dedup_events
from pipeline.checks import run_checks

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

ADAPTERS = {"rss": rss_adapter, "jsonld": jsonld_adapter}
VENUES_PATH = pathlib.Path("data/venues.json")
EVENTS_OUT = pathlib.Path("site/events.json")
PRAGUE_TZ = ZoneInfo("Europe/Prague")


def load_previous_events() -> dict:
    if not EVENTS_OUT.exists():
        return {}
    with EVENTS_OUT.open(encoding="utf-8") as f:
        data = json.load(f)
    return {e["id"]: e for e in data.get("events", [])}


def main():
    with VENUES_PATH.open(encoding="utf-8") as f:
        venues = json.load(f)

    previous = load_previous_events()
    all_raw = []

    for venue in venues:
        if not venue.get("active", True):
            continue
        for source in venue.get("sources", []):
            adapter = ADAPTERS.get(source["type"])
            if adapter is None:
                log.warning("No adapter for source type '%s' (venue %s)", source["type"], venue["id"])
                continue
            try:
                raw_events = adapter.fetch(venue, source)
                log.info("%s [%s]: %d events fetched", venue["id"], source["type"], len(raw_events))
                if not raw_events:
                    log.warning("%s [%s]: 0 events — site layout may have changed", venue["id"], source["type"])
                all_raw.extend(raw_events)
            except Exception as exc:
                log.error("%s [%s]: %s", venue["id"], source["type"], exc)

    events = [normalize_event(r, previous) for r in all_raw]
    events = dedup_events(events)
    events = run_checks(events, previous)

    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(PRAGUE_TZ).isoformat(),
        "venues": venues,
        "events": events,
    }
    with EVENTS_OUT.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info("Wrote %d events to %s", len(events), EVENTS_OUT)


if __name__ == "__main__":
    main()
