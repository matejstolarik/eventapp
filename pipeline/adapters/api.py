"""api adapter: JSON API sources (strategy: strapi).

Each venue using this adapter must specify `strategy` in source_config.
Currently supports: `strapi` (Strapi v5 REST API, e.g. Bike Jesus).
"""
import datetime
import logging
import re

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_DESC_MAX = 1000


def _clean_description(val) -> "str | None":
    """Return plain-text description, stripped and truncated to 1000 chars."""
    if not isinstance(val, str) or not val.strip():
        return None
    text = re.sub(r"<[^>]+>", " ", val)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    for marker in (". ", "! ", "? "):
        pos = cut.rfind(marker)
        if pos > _DESC_MAX // 2:
            return cut[: pos + 1].strip()
    return cut.rsplit(" ", 1)[0] + "..."


def fetch(venue: dict, source_config: dict) -> list:
    strategy = source_config.get("strategy")
    if strategy == "strapi":
        return _fetch_strapi(venue, source_config)
    log.warning("%s [api]: unknown strategy '%s'", venue["id"], strategy)
    return []


# ── Strapi v5 REST API ─────────────────────────────────────────────────────────

def _fetch_strapi(venue: dict, source_config: dict) -> list:
    """Fetch events from a Strapi v5 REST API endpoint.

    Paginates until all events are retrieved.  Filters to yesterday–+180 days.
    Expected fields: Title, Date (YYYY-MM-DD), Tickets (nullable), Description,
    Subtitle, Tag, documentId (stable external id), id, stableId.

    No start_time: the Strapi response at bikejesus.com/api/events provides only
    a date, never a time.  start_time is left null for all events.
    """
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    base_url = source_config["url"].rstrip("/")
    page_size = int(source_config.get("page_size", 100))
    fetcher = make_fetcher(source_config)

    import json as _json

    all_events: list = []
    page = 1
    while True:
        url = f"{base_url}?pagination[page]={page}&pagination[pageSize]={page_size}"
        try:
            raw = fetcher.get(url)
        except LimitExceeded as exc:
            log.warning("%s [api/strapi]: %s", venue["id"], exc)
            break
        except Exception as exc:
            log.error("%s [api/strapi]: page %d failed: %s", venue["id"], page, exc)
            break

        try:
            data = _json.loads(raw)
        except _json.JSONDecodeError as exc:
            log.error("%s [api/strapi]: JSON parse error: %s", venue["id"], exc)
            break

        items = data.get("data", [])
        meta = data.get("meta", {})
        pagination = meta.get("pagination", {})

        for item in items:
            ev = _strapi_item_to_raw(item, venue, source_config)
            if ev is None:
                continue
            try:
                ev_date = datetime.date.fromisoformat(ev.date)
            except (ValueError, AttributeError):
                continue
            if yesterday <= ev_date <= cutoff:
                all_events.append(ev)

        page_count = pagination.get("pageCount", 1)
        if page >= page_count:
            break
        page += 1

    return all_events


def _strapi_item_to_raw(item: dict, venue: dict, source_config: dict) -> "RawEvent | None":
    title = (item.get("Title") or "").strip()
    if not title:
        return None

    date_str = (item.get("Date") or "").strip()
    if not date_str:
        return None
    # Validate date format
    try:
        datetime.date.fromisoformat(date_str)
    except ValueError:
        return None

    ticket_raw = item.get("Tickets") or ""
    ticket_url = ticket_raw.strip() or None

    external_id = item.get("documentId") or str(item.get("stableId") or item.get("id") or "")

    description = _clean_description(item.get("Description"))

    # sources[].url: bikejesus.com has no individual event pages; use venue website root.
    source_url = source_config.get("venue_url", "https://bikejesus.com")

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=date_str,
        start_time=None,
        end_time=None,
        doors_time=None,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        sold_out=None,
        room=None,
        ticket_url=ticket_url,
        image_url=None,
        description=description,
        description_source="source" if description else None,
        source={
            "type": "api",
            "url": source_url,
            "external_id": external_id,
            "section": source_config.get("section"),
        },
        flags=[],
        status="scheduled",
    )


def parse_strapi(venue: dict, source_config: dict, json_text: str) -> list:
    """Parse Strapi JSON response text (no HTTP; used in tests).

    Applies +180 day window filter.
    """
    import json as _json
    import datetime as _dt

    today = _dt.date.today()
    yesterday = today - _dt.timedelta(days=1)
    cutoff = today + _dt.timedelta(days=180)

    data = _json.loads(json_text)
    items = data.get("data", [])
    result = []
    for item in items:
        ev = _strapi_item_to_raw(item, venue, source_config)
        if ev is None:
            continue
        try:
            ev_date = _dt.date.fromisoformat(ev.date)
        except (ValueError, AttributeError):
            continue
        if yesterday <= ev_date <= cutoff:
            result.append(ev)
    return result
