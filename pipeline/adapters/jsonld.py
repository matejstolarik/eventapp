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
    strategy = source_config.get("strategy")
    if strategy == "mec_ajax":
        return _fetch_mec_ajax(venue, source_config)

    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [jsonld]: %s — returning 0 events", venue["id"], exc)
        return []
    if source_config.get("follow_links"):
        return _fetch_kasarna_details(venue, source_config, html, fetcher)
    return _fetch_listing_pages(venue, source_config, html, fetcher)


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


# ── MEC admin-ajax strategy (Čitárna Unijazz and any other MEC tile calendar) ──

def _fetch_mec_ajax(venue: dict, source_config: dict) -> list:
    """Fetch events from a WordPress site using the Modern Events Calendar (MEC)
    plugin tile view.  MEC renders months on demand via admin-ajax.php; we POST
    for the current month and the next `months_ahead` months and parse JSON-LD
    from each HTML response.

    Required source_config keys:
      ajax_url    – full URL to wp-admin/admin-ajax.php
      skin_id     – integer id of the MEC skin shortcode on the page
      url         – canonical listing URL (used as base for image resolution)
    Optional:
      months_ahead – how many months beyond the current one to fetch (default 1)

    Risk: if the site rebuilds and the skin_id changes, the adapter returns 0
    events.  This is caught by the existing "0 events" warning in main.py.
    """
    import requests as _requests
    from pipeline.fetch import _rate_limit, LimitExceeded, USER_AGENT

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    ajax_url = source_config["ajax_url"]
    skin_id = int(source_config["skin_id"])
    months_ahead = int(source_config.get("months_ahead", 1))
    fetcher = make_fetcher(source_config)

    # Build list of (year, month) starting from the current month
    months_to_fetch: list[tuple[int, int]] = []
    d = today.replace(day=1)
    for _ in range(months_ahead + 1):
        months_to_fetch.append((d.year, d.month))
        d = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)

    import time as _time

    all_events: list = []
    for year, month in months_to_fetch:
        fetcher._count += 1  # count the POST against the per-source request limit
        if fetcher._count > fetcher.max_requests:
            log.warning("%s [jsonld/mec_ajax]: max_requests reached", venue["id"])
            break
        if _time.monotonic() - fetcher._start > fetcher.timeout_secs:
            log.warning("%s [jsonld/mec_ajax]: timeout exceeded", venue["id"])
            break

        try:
            _rate_limit(ajax_url)
            resp = _requests.post(
                ajax_url,
                data={
                    "action": "mec_tile_load_month",
                    "mec_year": str(year),
                    "mec_month": f"{month:02d}",
                    "atts[id]": str(skin_id),
                    "navigator_click": "true",
                    "apply_sf_date": "0",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            resp.raise_for_status()
            month_html = resp.json().get("month", "")
        except Exception as exc:
            log.warning("%s [jsonld/mec_ajax]: %04d-%02d failed: %s",
                        venue["id"], year, month, exc)
            continue

        for ev in _parse_listing(venue, source_config, month_html):
            try:
                ev_date = datetime.date.fromisoformat(ev.date)
            except (ValueError, AttributeError):
                continue
            if yesterday <= ev_date <= cutoff:
                all_events.append(ev)

    if source_config.get("follow_details"):
        all_events = _fetch_mec_detail_times(venue, source_config, all_events, fetcher)

    return all_events


def _fetch_mec_detail_times(venue: dict, source_config: dict,
                             events: list, fetcher) -> list:
    """For each event in *events* fetch its detail page and fill start_time
    from the `.event-time` element (format: 'DD. MM. YYYY HH:MM').

    If the date on the detail page differs from the listing date a
    'date_conflict' flag is added.  Events whose detail URL is the listing
    URL itself (i.e. the JSON-LD had no individual URL) are left unchanged.
    On LimitExceeded the remaining events keep start_time=None and a warning
    is logged.
    """
    import dataclasses
    listing_url = source_config["url"]
    updated: list = []
    limit_hit = False
    for ev in events:
        if limit_hit:
            updated.append(ev)
            continue
        detail_url = ev.source.get("url")
        if not detail_url or detail_url == listing_url:
            updated.append(ev)
            continue
        try:
            html = fetcher.get(detail_url)
        except LimitExceeded as exc:
            log.warning("%s [jsonld/mec_ajax]: %s — remaining events will have no start_time",
                        venue["id"], exc)
            limit_hit = True
            updated.append(ev)
            continue
        except Exception as exc:
            log.warning("%s [jsonld/mec_ajax]: detail %s failed: %s", venue["id"], detail_url, exc)
            updated.append(ev)
            continue

        soup = BeautifulSoup(html, "html.parser")
        et_el = soup.select_one(".event-time")
        if not et_el:
            updated.append(ev)
            continue
        det_date, det_time = _parse_event_time_div(et_el.get_text(strip=True))
        if not det_time:
            updated.append(ev)
            continue
        flags = list(ev.flags)
        if det_date and det_date != ev.date:
            flags.append("date_conflict")
        updated.append(dataclasses.replace(ev, start_time=det_time, flags=flags))
    return updated


def _parse_event_time_div(text: str) -> "tuple[str | None, str | None]":
    """Parse '.event-time' text like '03. 11. 2026 19:00'.
    Returns (date_iso, time_str) or (None, None) if unparseable."""
    m = re.match(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\s+(\d{1,2}):(\d{2})", text.strip())
    if not m:
        return None, None
    day, month, year, hour, minute = (int(x) for x in m.groups())
    try:
        d = datetime.date(year, month, day)
    except ValueError:
        return None, None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None, None
    return d.isoformat(), f"{hour:02d}:{minute:02d}"


# ── listing strategy (MeetFactory, Čitárna) ───────────────────────────────────

def _fetch_listing_pages(venue: dict, source_config: dict, first_html: str,
                         fetcher) -> list:
    """Fetch all paginated listing pages (endless_more pattern) and return events.

    Stops when there is no more 'endless_more' link, the request limit is hit,
    or every event on the last page is beyond the +180-day window.
    """
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    base_url = source_config["url"]

    all_events: list = []
    html = first_html
    page = 1

    while True:
        events = _parse_listing(venue, source_config, html)
        for ev in events:
            try:
                ev_date = datetime.date.fromisoformat(ev.date)
            except (ValueError, AttributeError):
                all_events.append(ev)
                continue
            if yesterday <= ev_date <= cutoff:
                all_events.append(ev)

        soup = BeautifulSoup(html, "html.parser")
        more = soup.find("a", class_="endless_more")
        if not more:
            break

        # Stop early if all events on this page are beyond the cutoff
        page_dates = []
        for ev in events:
            try:
                page_dates.append(datetime.date.fromisoformat(ev.date))
            except (ValueError, AttributeError):
                pass
        if page_dates and min(page_dates) > cutoff:
            break

        page += 1
        next_url = f"{base_url}?page={page}"
        try:
            html = fetcher.get(next_url)
        except LimitExceeded as exc:
            log.warning("%s [jsonld]: %s — stopping pagination at page %d",
                        venue["id"], exc, page)
            break
        except Exception as exc:
            log.warning("%s [jsonld]: page %d failed: %s", venue["id"], page, exc)
            break

    return all_events


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
    for line in text.split("\n"):
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


