"""Per-venue cache of parsed event detail pages (task 085).

main.py passes source_config["detail_cache"] = state["adapter_detail"][venue_id]
(a dict kept in site/pipeline_state.json).  An adapter fetches a detail page
only when the listing shows a new event, the event's listing data changed
(title / dates), or the page was checked DETAIL_RECHECK_DAYS days ago; then
it replaces the cache with the entries of this run's listing, so events that
left the listing drop out.

Entry: {"sig": str, "checked": "YYYY-MM-DD", "data": {...parsed values...}}
"""

import datetime

DETAIL_RECHECK_DAYS = 7


def signature(title: str, dates) -> str:
    return title.strip() + "|" + ",".join(str(d) for d in dates)


def needs_fetch(entry: "dict | None", sig: str, today: str) -> bool:
    if not entry or entry.get("sig") != sig or "data" not in entry:
        return True
    try:
        last = datetime.date.fromisoformat(entry.get("checked") or "")
    except ValueError:
        return True
    return (datetime.date.fromisoformat(today) - last).days >= DETAIL_RECHECK_DAYS


def replace(cache: dict, used: dict) -> None:
    """Keep only this run's entries (in place: the dict belongs to the state)."""
    cache.clear()
    cache.update(used)
