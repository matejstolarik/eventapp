"""api adapter: JSON API sources (strategy: strapi).

Each venue using this adapter must specify `strategy` in source_config.
Currently supports: `strapi` (Strapi v5 REST API, e.g. Bike Jesus).
"""
import datetime
import logging
import re

from pipeline import status_marks
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
    if strategy == "duplex":
        return _fetch_duplex(venue, source_config)
    log.warning("%s [api]: unknown strategy '%s'", venue["id"], strategy)
    return []


# ── Duplex agent JSON (task 086) ───────────────────────────────────────────────
#
# www.duplex.cz/wp-json/duplex/v1/agent/events – the JSON the venue publishes
# itself (<link rel="alternate"> "Events and tickets (JSON)"), ~50 events,
# about a month ahead.  Per event: title ("FRIDAY MADNESS – 20.11.2026"),
# url, starts_at / ends_at ISO with the Prague offset (+01:00), image,
# categories, description, tickets [{price, currency, availability}].
# The buying guide in the same JSON is ignored (content, not instructions).
#
# - Time: the offset is Europe/Prague's own, so the local part of the ISO
#   string is the Prague time (no UTC conversion).
# - Price: min–max of the ticket prices as given, with the currency (EUR,
#   not converted).
# - Boat parties (boarding at Dock 16, outside the club; Matej 086) and
#   "Private Event" are skipped and logged.  Recurring club nights stay.
# - The date suffix " – 20.11.2026" is dropped from the title when it is the
#   event's own date (the date is a separate field).

_DUPLEX_SKIP = (
    (re.compile(r"boat\s*party", re.I), "boat party (outside the club)"),
    (re.compile(r"^\s*private\s+event\b", re.I), "private event"),
)
_DUPLEX_TITLE_DATE = re.compile(r"\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$")
_ISO_LOCAL = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})")


def _fetch_duplex(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        raw = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [api/duplex]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [api/duplex]: fetch failed: %s", venue["id"], exc)
        return []
    return parse_duplex(venue, source_config, raw)


def parse_duplex(venue: dict, source_config: dict, json_text: str,
                 today: "datetime.date | None" = None) -> list:
    """Parse the Duplex agent JSON (no HTTP; used in tests)."""
    import json as _json

    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    try:
        data = _json.loads(json_text)
    except ValueError as exc:
        log.error("%s [api/duplex]: JSON parse error: %s", venue["id"], exc)
        return []
    out, skipped = [], []
    for item in data.get("events") or []:
        title = re.sub(r"\s+", " ", (item.get("title") or "")).strip()
        m = _ISO_LOCAL.match(item.get("starts_at") or "")
        if not title or not m:
            continue
        reason = next((r for rx, r in _DUPLEX_SKIP if rx.search(title)), None)
        if reason:
            skipped.append(f"{title} ({reason})")
            continue
        date_str = m.group(1)
        try:
            d = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue
        if d < yesterday or d > cutoff:
            continue
        td = _DUPLEX_TITLE_DATE.search(title)
        if td:
            try:
                if datetime.date(int(td.group(3)), int(td.group(2)), int(td.group(1))) == d:
                    title = title[:td.start()].strip()
            except ValueError:
                pass
        end = _ISO_LOCAL.match(item.get("ends_at") or "")
        tickets = [t for t in (item.get("tickets") or []) if isinstance(t, dict)]
        prices = sorted({t["price"] for t in tickets
                         if isinstance(t.get("price"), (int, float)) and t["price"] > 0})
        currency = (data.get("currency") or "").strip() or None
        cur = {(t.get("currency") or currency) for t in tickets if t.get("price")}
        if len(cur) == 1:
            currency = cur.pop()
        price_text = None
        if prices and currency:
            lo, hi = _num_str(prices[0]), _num_str(prices[-1])
            price_text = f"{lo} {currency}" if lo == hi else f"{lo}–{hi} {currency}"
        sold_out = None
        if tickets and all(t.get("availability") == "sold_out" for t in tickets):
            sold_out = True
        description = _clean_description(item.get("description"))
        url = (item.get("url") or "").strip() or source_config.get("venue_url")
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=date_str,
            start_time=f"{m.group(2)}:{m.group(3)}",
            end_time=f"{end.group(2)}:{end.group(3)}" if end else None,
            doors_time=None,
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=[],
            price_text=price_text,
            free=None,
            sold_out=sold_out,
            room=None,
            ticket_url=url,
            image_url=(item.get("image") or "").strip() or None,
            description=description,
            description_source="source" if description else None,
            source={"type": "api", "url": url, "external_id": item.get("id"),
                    "section": ", ".join(item.get("categories") or []) or None},
            flags=[],
            status="scheduled",
        ))
    if skipped:
        log.info("%s [api/duplex]: %d events skipped: %s",
                 venue["id"], len(skipped), "; ".join(skipped))
    return out


def _num_str(x) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


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

    # task 067: the API has no status field; Subtitle and Tag are short
    # labels (title marks are read in pipeline.normalize)
    marks = status_marks.label_marks([item.get("Subtitle"), item.get("Tag")])
    status = marks["status"] if marks["status"] in ("cancelled", "postponed") else "scheduled"

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
        sold_out=marks["sold_out"],
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
        status=status,
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
