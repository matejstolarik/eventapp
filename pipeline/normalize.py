import datetime
import html
import logging
import re
import unicodedata

log = logging.getLogger(__name__)

# Detect "POSTPONED: title" and similar prefixes (EN / CZ / SK)
_POSTPONED_RE = re.compile(
    r"^(POSTPONED|ODLOŽENO|ODLOŽENÁ|ODLOŽEN[OA]|ODLOŽENÉ)\s*[:\-]?\s*",
    re.IGNORECASE,
)
# Detect "PŘESUNUTO DO venue / title" and similar (event moved to another venue)
_MOVED_RE = re.compile(
    r"^(PŘESUNUTO\s+DO|PRESUNUTO\s+DO|MOVED\s+TO)\b",
    re.IGNORECASE,
)


def _detect_postponed_moved(title: str) -> tuple[str, str]:
    """Return (action, clean_title).

    action:  ""          – normal event
             "postponed" – postponed without new date; prefix stripped from title
             "moved"     – moved to another venue; event should be excluded
    """
    if _MOVED_RE.match(title):
        return "moved", title
    m = _POSTPONED_RE.match(title)
    if m:
        return "postponed", title[m.end():].strip()
    return "", title


def normalize_event(raw_event, previous_events: dict = None) -> "dict | None":
    """Convert RawEvent to event dict, preserving id/first_seen from a previous run."""
    if previous_events is None:
        previous_events = {}

    raw_title = html.unescape(raw_event.title)
    action, clean_title = _detect_postponed_moved(raw_title)

    if action == "moved":
        log.info("skipped moved event: %s (venue %s)", raw_title, raw_event.venue_id)
        return None

    today = datetime.date.today().isoformat()
    # ID uses the cleaned title so postponed prefix doesn't affect the slug
    event_id = f"{raw_event.venue_id}-{raw_event.date}-{_slugify(clean_title)[:60]}"
    prev = previous_events.get(event_id)

    has_classification = bool(raw_event.formats or raw_event.genres)
    classification = {"method": "source", "confidence": None} if has_classification else None

    # Status priority: prefix detection > adapter > previous > default
    if action == "postponed":
        status = "postponed"
    elif raw_event.status == "cancelled":
        status = "cancelled"
    elif prev:
        status = prev.get("status", "scheduled")
    else:
        status = "scheduled"

    return {
        "id": event_id,
        "venue_id": raw_event.venue_id,
        "title": clean_title,
        "date": raw_event.date,
        "start_time": raw_event.start_time,
        "doors_time": raw_event.doors_time,
        "end_time": raw_event.end_time,
        "formats": raw_event.formats,
        "genres": raw_event.genres,
        "character": raw_event.character,
        "artists": raw_event.artists,
        "price_text": raw_event.price_text,
        "free": raw_event.free,
        "sold_out": raw_event.sold_out,
        "room": raw_event.room,
        "ticket_url": raw_event.ticket_url,
        "image_url": raw_event.image_url,
        "sources": [raw_event.source],
        "classification": classification,
        "first_seen": prev["first_seen"] if prev else today,
        "last_seen": today,
        "status": status,
        "flags": list(raw_event.flags),
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
