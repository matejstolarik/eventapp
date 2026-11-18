import datetime
import html
import logging
import re
import unicodedata

from pipeline import status_marks

log = logging.getLogger(__name__)

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
    Task 067: the marks come from pipeline.status_marks (shared by all
    sources); a cancelled / sold-out mark keeps the title as it is.
    """
    if _MOVED_RE.match(title):
        return "moved", title
    marks = status_marks.title_marks(title)
    if marks["status"] == "postponed":
        return "postponed", marks["title"]
    return "", title


def normalize_event(raw_event, previous_events: dict = None) -> "dict | None":
    """Convert RawEvent to event dict, preserving id/first_seen from a previous run."""
    if previous_events is None:
        previous_events = {}

    raw_title = html.unescape(raw_event.title)
    action, clean_title = _detect_postponed_moved(raw_title)
    marks = status_marks.title_marks(raw_title) if action != "moved" else {}

    if action == "moved":
        log.info("skipped moved event: %s (venue %s)", raw_title, raw_event.venue_id)
        return None

    today = datetime.date.today().isoformat()
    # ID uses the cleaned title so postponed prefix doesn't affect the slug
    event_id = f"{raw_event.venue_id}-{raw_event.date}-{_slugify(clean_title)[:60]}"
    prev = previous_events.get(event_id)

    has_classification = bool(raw_event.formats or raw_event.genres)
    classification = {"method": "source", "confidence": None} if has_classification else None

    # Status priority: title mark > adapter > previous > default
    if marks.get("status") == "cancelled":
        status = "cancelled"
    elif action == "postponed":
        status = "postponed"
    elif raw_event.status in ("cancelled", "postponed"):
        status = raw_event.status
    elif prev:
        status = prev.get("status", "scheduled")
    else:
        status = "scheduled"
    if marks.get("status"):
        log.info("status mark in title %r (%s): %s", raw_title, raw_event.venue_id,
                 marks["status"])
    if marks.get("status") == "rescheduled":
        # the source normally shows the new date already: only log
        log.warning("rescheduled (new date) mark in title %r (%s) — kept as %s",
                    raw_title, raw_event.venue_id, status)
    sold_out = raw_event.sold_out
    if marks.get("sold_out"):
        sold_out = True

    return {
        "id": event_id,
        "venue_id": raw_event.venue_id,
        "title": clean_title,
        "date": raw_event.date,
        "start_time": raw_event.start_time,
        "doors_time": raw_event.doors_time,
        "end_time": raw_event.end_time,
        "formats": raw_event.formats,
        "primary_format": None,
        "genres": raw_event.genres,
        "character": raw_event.character,
        "artists": raw_event.artists,
        "price_text": raw_event.price_text,
        "free": raw_event.free,
        "sold_out": sold_out,
        "room": raw_event.room,
        "ticket_url": raw_event.ticket_url,
        "image_url": raw_event.image_url,
        "description": raw_event.description,
        "description_source": raw_event.description_source,
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
