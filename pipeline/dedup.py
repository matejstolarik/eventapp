import re
import unicodedata


def dedup_events(events: list) -> list:
    """Remove near-duplicate events from the same venue on the same day."""
    seen = set()
    result = []
    for event in events:
        key = _dedup_key(event)
        if key not in seen:
            seen.add(key)
            result.append(event)
    return result


def _normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKD", title.lower())
    title = title.encode("ascii", "ignore").decode()
    title = re.sub(r"[^a-z0-9 ]", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def _dedup_key(event: dict) -> str:
    return f"{event['venue_id']}-{event['date']}-{_normalize_title(event['title'])}"
