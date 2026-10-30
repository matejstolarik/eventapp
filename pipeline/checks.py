import datetime

WINDOW_DAYS = 180


def run_checks(events: list, previous_events: dict = None) -> list:
    """Apply quality flags and filter to the time window (yesterday to +180 days).

    Events beyond +180 days are silently excluded.
    date_suspicious is set only when a NEW event (not in previous_events) has a past date.
    """
    if previous_events is None:
        previous_events = {}

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=WINDOW_DAYS)

    result = []
    for event in events:
        flags = list(event.get("flags", []))
        try:
            event_date = datetime.date.fromisoformat(event["date"])
        except (ValueError, TypeError):
            flags.append("date_suspicious")
            event["flags"] = flags
            result.append(event)
            continue

        if event_date > cutoff:
            continue  # silently exclude; not an error, just outside the window

        is_new = event["id"] not in previous_events
        if is_new and event_date < yesterday:
            flags.append("date_suspicious")

        event["flags"] = flags
        if event_date >= yesterday:
            result.append(event)

    return result
