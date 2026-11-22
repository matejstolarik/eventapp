"""Day of a venue's first successful programme load (task 086, part 9).

The app marks an event "new" when its first_seen is within 7 days.  When a
venue is added, ALL its events get first_seen = the day of the first load,
so they would all look new although the venue announced them long ago.
Rule (Matej 2026-11-21): events of a venue's first load are not new; only
events that appear in later runs are.

state["venue_first_loaded"] = {venue_id: "YYYY-MM-DD" | None}
  date  = day of the first run in which the venue's source returned events
          (a venue whose first runs fail counts from the first success)
  None  = venue loaded before this rule existed (no restriction)
Published per venue as `first_loaded` in events.json; the app treats an
event as new only when first_seen > first_loaded (docs/data-model.md).
"""

STATE_KEY = "venue_first_loaded"

# Bootstrap (first run with the rule): venues of task 085, all first loaded
# on 2026-11-21 (Lucerna Music Bar, O2 arena, O2 universum in run
# 44840323600; Jazz Republic in run 44905208900).  Applies the rule to them
# retroactively, as Matej asked.
BOOTSTRAP = {
    "lucerna-music-bar": "2026-11-21",
    "o2-arena": "2026-11-21",
    "o2-universum": "2026-11-21",
    "jazz-republic": "2026-11-21",
}


def update(state: dict, events: list, previous: dict, today: str) -> dict:
    """Record today for venues loaded for the first time; returns the map."""
    first = state.get(STATE_KEY)
    if not isinstance(first, dict):
        first = {}
        for ev in (previous or {}).values():
            vid = ev.get("venue_id")
            if vid and vid not in first:
                first[vid] = BOOTSTRAP.get(vid)
        for vid, day in BOOTSTRAP.items():
            first.setdefault(vid, day)
    for ev in events:
        vid = ev.get("venue_id")
        if vid and vid not in first:
            first[vid] = today
    state[STATE_KEY] = first
    return first


def is_new(event: dict, first_loaded: "str | None", today: str, days: int = 7) -> bool:
    """Same rule as isNew() in web/src/core/search.ts (used for counts/tests)."""
    import datetime
    seen = event.get("first_seen")
    if not seen:
        return False
    if first_loaded and seen <= first_loaded:
        return False
    cutoff = datetime.date.fromisoformat(today) - datetime.timedelta(days=days - 1)
    return datetime.date.fromisoformat(seen) >= cutoff
