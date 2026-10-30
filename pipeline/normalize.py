import datetime
import re
import unicodedata


def normalize_event(raw_event, previous_events: dict = None) -> dict:
    """Convert RawEvent to event dict, preserving id/first_seen from a previous run."""
    if previous_events is None:
        previous_events = {}

    event_id = _make_id(raw_event)
    today = datetime.date.today().isoformat()
    prev = previous_events.get(event_id)

    has_classification = bool(raw_event.formats or raw_event.genres)
    classification = {"method": "source", "confidence": None} if has_classification else None

    return {
        "id": event_id,
        "venue_id": raw_event.venue_id,
        "title": raw_event.title,
        "date": raw_event.date,
        "start_time": raw_event.start_time,
        "end_time": raw_event.end_time,
        "formats": raw_event.formats,
        "genres": raw_event.genres,
        "character": raw_event.character,
        "artists": raw_event.artists,
        "price_text": raw_event.price_text,
        "free": raw_event.free,
        "ticket_url": raw_event.ticket_url,
        "image_url": raw_event.image_url,
        "sources": [raw_event.source],
        "classification": classification,
        "first_seen": prev["first_seen"] if prev else today,
        "last_seen": today,
        "status": prev.get("status", "scheduled") if prev else "scheduled",
        "flags": [],
    }


def _make_id(raw_event) -> str:
    slug = _slugify(raw_event.title)
    return f"{raw_event.venue_id}-{raw_event.date}-{slug[:60]}"


def _slugify(text: str) -> str:
    """Lowercase, strip diacritics via NFKD, keep only alphanumerics and hyphens."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")
