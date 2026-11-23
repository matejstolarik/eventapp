"""Keep the last known events of a failing source (task 092, Matej 2026-11-23).

Problem: when a source fails (download error, or 0 events although it had
events before), the venue was empty in the app although we knew its programme
from the previous run (Klub 007 returned 403 to GitHub from 2026-11-22).

Rule:
- A source is *failing* when its fetch raised an error, or it returned 0
  events and either the previous events.json had events of this source or the
  source was already failing in the previous run (state).
- For a failing source, every future event of that source from the previous
  published events.json is kept unchanged.  The previous events.json already
  contains events kept in earlier runs of the same outage, so nothing is lost
  over a multi-day outage.  No time limit: kept events drop out when their day
  has passed.  Nothing is added or corrected.
- A kept event gets `source_last_ok` = the day the source last returned it
  (its `last_seen`; an event kept before keeps its value).  Not shown in the app.
- A venue with a failing source gets `source_failing: true` in events.json;
  the app hides such a venue when it has no future event left.
- When the source returns events again, the state entry is removed and
  everything comes back on its own.

state["failing_sources"] = {"<venue_id>/<label>": "YYYY-MM-DD"}  (day the outage started)
"""

STATE_KEY = "failing_sources"


def source_label(source: dict) -> str:
    """Label of a source config, the same as in the run summary and alerts."""
    return source.get("section") or source.get("strategy") or source["type"]


def _matches(event: dict, source: dict) -> bool:
    """Does the event come from this source config?  Events keep only type
    (and section) of their source, so the match is by type + section."""
    for s in event.get("sources") or []:
        if s.get("type") != source.get("type"):
            continue
        if source.get("section") and s.get("section") != source.get("section"):
            continue
        return True
    return False


def keep_failing(venues: list, source_results: list, events: list, previous: dict,
                 state: dict, today: str) -> tuple[list, dict, set]:
    """Return (events to add, {"venue/label": kept count}, failing venue ids).

    source_results: [(venue_id, label, count, warning)] of this run, warning
    None / "zero_events" / "error"."""
    failing_before = dict(state.get(STATE_KEY) or {})
    failing_now: dict[str, str] = {}
    result = {(vid, label): (count, warning) for vid, label, count, warning in source_results}
    current_ids = {e["id"] for e in events}
    kept: list = []
    stats: dict[str, int] = {}
    failing_venues: set = set()

    for venue in venues:
        if not venue.get("active", True):
            continue
        for source in venue.get("sources", []):
            label = source_label(source)
            key = f"{venue['id']}/{label}"
            count, warning = result.get((venue["id"], label), (None, None))
            if count is None:
                continue
            prev_events = [e for e in previous.values()
                           if e.get("venue_id") == venue["id"] and _matches(e, source)]
            failing = warning == "error" or (
                count == 0 and (bool(prev_events) or key in failing_before))
            if not failing:
                continue
            failing_now[key] = failing_before.get(key) or today
            failing_venues.add(venue["id"])
            n = 0
            for e in prev_events:
                if (e.get("date") or "") < today or e["id"] in current_ids:
                    continue
                e2 = dict(e)
                e2["source_last_ok"] = e.get("source_last_ok") or e.get("last_seen")
                kept.append(e2)
                current_ids.add(e["id"])
                n += 1
            stats[key] = n

    state[STATE_KEY] = failing_now
    return kept, stats, failing_venues
