import datetime

WINDOW_DAYS = 180


def run_checks(events: list) -> list:
    """Apply quality flags and filter out events outside the time window."""
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
            flags.append("date_suspicious")

        event["flags"] = flags
        if event_date >= yesterday:
            result.append(event)

    return result
