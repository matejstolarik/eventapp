import datetime
import json
import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [jsonld]: %s — returning 0 events", venue["id"], exc)
        return []
    if source_config.get("follow_links"):
        return _fetch_kasarna_details(venue, source_config, html, fetcher)
    return _parse_listing(venue, source_config, html)


def parse(venue: dict, source_config: dict, html: str) -> list:
    """Parse a listing page HTML string (no HTTP; used in tests)."""
    return _parse_listing(venue, source_config, html)


def parse_kasarna(venue: dict, source_config: dict, listing_html: str,
                  details_map: dict) -> list:
    """Parse Kasárna listing + pre-fetched detail pages (used in tests).

    details_map: {absolute_url: html_string}
    """
    from pipeline.fetch import Fetcher

    class _DictFetcher(Fetcher):
        def get(self, url, http_timeout=30):
            return details_map[url]

    return _fetch_kasarna_details(venue, source_config, listing_html, _DictFetcher())


# ── listing strategy (MeetFactory, Čitárna) ───────────────────────────────────

def _parse_listing(venue: dict, source_config: dict, html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    section = source_config.get("section")
    base_url = source_config["url"]
    events = []
    for item in _all_ld_items(soup):
        if not _is_event(item):
            continue
        ev = _ld_to_raw(item, venue, base_url, section)
        if ev:
            events.append(ev)
    return events


# ── detail-crawl strategy (Kasárna Karlín) ────────────────────────────────────

def _fetch_kasarna_details(venue: dict, source_config: dict, listing_html: str,
                           fetcher) -> list:
    soup = BeautifulSoup(listing_html, "html.parser")
    detail_lang = source_config.get("detail_lang", "en")
    base = _origin(source_config["url"])

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    DATE_IN_URL = re.compile(r"/(?:en|cs)/program/(\d{4})/(\d{2})/(\d{2})/")

    seen: set = set()
    events = []
    for a in soup.find_all("a", href=True):
        m = DATE_IN_URL.search(a["href"])
        if not m:
            continue
        try:
            url_date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        if url_date < yesterday or url_date > cutoff:
            continue

        detail_url = re.sub(r"/(?:en|cs)/program/", f"/{detail_lang}/program/",
                            urljoin(base, a["href"]))
        if detail_url in seen:
            continue
        seen.add(detail_url)

        try:
            detail_html = fetcher.get(detail_url)
        except LimitExceeded as exc:
            log.warning("%s [jsonld]: %s — stopping after %d events",
                        venue["id"], exc, len(events))
            break
        except Exception as exc:
            log.error("kasarna detail %s: %s", detail_url, exc)
            continue

        ev = _parse_kasarna_detail(venue, source_config, detail_url, url_date, detail_html)
        if ev:
            events.append(ev)
    return events


def _parse_kasarna_detail(venue: dict, source_config: dict,
                          detail_url: str, url_date: datetime.date,
                          html: str) -> "RawEvent | None":
    soup = BeautifulSoup(html, "html.parser")
    ld_events = [i for i in _all_ld_items(soup) if _is_event(i)]
    if not ld_events:
        return None
    ld = ld_events[0]

    ld_date = _parse_iso_date(_str_or_none(ld.get("startDate")) or "")
    flags: list = []
    if ld_date and ld_date != url_date:
        flags.append("date_conflict")
        # Check for MM/DD swap: url_date month and day transposed give ld_date
        if 1 <= url_date.day <= 12:
            try:
                swapped = datetime.date(url_date.year, url_date.day, url_date.month)
                if swapped == ld_date:
                    flags.append("date_suspicious")
            except ValueError:
                pass

    date_str = ld_date.isoformat() if ld_date else url_date.isoformat()

    # Time from page text — Kasárna's JSON-LD startDate time is wrong (shifted by 5-6 h
    # in winter/summer due to a timezone misconfiguration on their server).
    # The correct time appears as a standalone line in the page header.
    start_time = _kasarna_time_from_html(soup)

    title = _str_or_none(ld.get("name"))
    if not title:
        return None

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=date_str,
        start_time=start_time,
        end_time=None,
        doors_time=None,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        ticket_url=None,
        image_url=_resolve_image(ld.get("image"), detail_url),
        source={
            "type": "jsonld",
            "url": detail_url,
            "external_id": None,
            "section": source_config.get("section"),
        },
        flags=flags,
        status=_event_status(ld.get("eventStatus", "")),
    )


def _kasarna_time_from_html(soup: BeautifulSoup) -> "str | None":
    return _parse_time_line(soup.get_text(separator="\n"))


def _parse_time_line(text: str) -> "str | None":
    """Find the first standalone time line (HH:MM or H:MM AM/PM) in text.

    Kasárna also systematically displays dates as MM. DD. YYYY in HTML — do not
    use any date from page text; only URL and JSON-LD dates are reliable there.
    """
    TIME_24H = re.compile(r"^(\d{1,2}):(\d{2})$")
    TIME_AMPM = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", re.IGNORECASE)
    for line in text.split("\n")[:50]:
        line = line.strip()
        m = TIME_24H.match(line)
        if m:
            h, mn = int(m.group(1)), int(m.group(2))
            if 0 <= h <= 23 and 0 <= mn <= 59:
                return f"{h:02d}:{mn:02d}"
        m = TIME_AMPM.match(line)
        if m:
            h, mn, mer = int(m.group(1)), int(m.group(2)), m.group(3).upper()
            if mer == "PM" and h != 12:
                h += 12
            elif mer == "AM" and h == 12:
                h = 0
            if 0 <= h <= 23 and 0 <= mn <= 59:
                return f"{h:02d}:{mn:02d}"
    return None


# ── shared helpers ─────────────────────────────────────────────────────────────

def _ld_to_raw(item: dict, venue: dict, base_url: str,
               section: "str | None") -> "RawEvent | None":
    title = _str_or_none(item.get("name"))
    if not title:
        return None
    start = _str_or_none(item.get("startDate"))
    if not start:
        return None
    date_str = _parse_date_part(start)
    if not date_str:
        return None

    doors_time = _str_or_none(item.get("doorTime"))
    event_url = _str_or_none(item.get("url"))

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=date_str,
        start_time=None,  # listing-page startDate is date-only (MeetFactory, Čitárna)
        end_time=None,
        doors_time=doors_time,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        ticket_url=None,  # offers.url points to the event page, not ticket sales
        image_url=_resolve_image(item.get("image"), base_url),
        source={
            "type": "jsonld",
            "url": event_url or base_url,
            "external_id": None,
            "section": section,
        },
        flags=[],
        status=_event_status(item.get("eventStatus", "")),
    )


def _all_ld_items(soup: BeautifulSoup) -> list:
    items = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, ValueError):
            continue
        items.extend(_flatten_ld(data))
    return items


def _flatten_ld(data) -> list:
    if isinstance(data, list):
        result = []
        for item in data:
            result.extend(_flatten_ld(item))
        return result
    if isinstance(data, dict):
        if "@graph" in data:
            result = []
            for item in data["@graph"]:
                result.extend(_flatten_ld(item))
            return result
        return [data]
    return []


def _is_event(item: dict) -> bool:
    t = item.get("@type", "")
    return isinstance(t, str) and t.lower().endswith("event")


def _parse_date_part(s: str) -> "str | None":
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None


def _parse_iso_date(s: str) -> "datetime.date | None":
    date_str = _parse_date_part(s)
    if not date_str:
        return None
    try:
        return datetime.date.fromisoformat(date_str)
    except ValueError:
        return None


def _str_or_none(val) -> "str | None":
    if isinstance(val, str) and val.strip():
        return val.strip()
    return None


def _event_status(status_str) -> str:
    if isinstance(status_str, str) and "cancel" in status_str.lower():
        return "cancelled"
    return "scheduled"


def _resolve_image(image_val, base_url: str) -> "str | None":
    url = None
    if isinstance(image_val, str):
        url = image_val.strip() or None
    elif isinstance(image_val, dict):
        url = _str_or_none(image_val.get("url") or image_val.get("contentUrl"))
    if not url:
        return None
    if not url.startswith("http"):
        url = urljoin(f"{_origin(base_url)}/", url.lstrip("/"))
    return url


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


