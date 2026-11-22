import datetime
import json
import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent
from pipeline import images, status_marks

log = logging.getLogger(__name__)


def fetch(venue: dict, source_config: dict) -> list:
    strategy = source_config.get("strategy")
    if strategy == "mec_ajax":
        return _fetch_mec_ajax(venue, source_config)
    if strategy == "wix_sitemap":
        return _fetch_wix_sitemap(venue, source_config)
    if strategy == "eventon":
        return _fetch_eventon(venue, source_config)

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


# ── Wix sitemap strategy (Fuchs2 and other Wix Events sites) ─────────────────

def _fetch_wix_sitemap(venue: dict, source_config: dict) -> list:
    """Fetch events from a Wix site by crawling its event-pages sitemap.

    Wix server-renders only the current/featured event in JSON-LD on the listing
    page; all other events are loaded via JavaScript.  The event-pages sitemap
    (event-pages-sitemap.xml) lists every event page URL with a <lastmod> date.

    Strategy:
    1. Fetch the sitemap XML.
    2. Keep only URLs whose <lastmod> is within the last `sitemap_days_back` days
       (default 90).  Events are typically added weeks before they happen, so
       recently-modified pages are almost always upcoming events.
    3. Fetch each event detail page and parse the JSON-LD Event object.
    4. Filter to the yesterday–+180 day window.

    Time check (Fuchs2 verified 2026-11-03): Wix JSON-LD includes the correct
    Prague local time in startDate (e.g. "2026-11-26T23:00:00+01:00").  Three
    events were verified: times match what is displayed on the page.  No timezone
    shift was detected (unlike Kasárna where JSON-LD times were wrong).

    Required source_config keys:
      sitemap_url  – URL of the event-pages sitemap
      url          – canonical listing page URL (used as fallback source url)
    Optional:
      sitemap_days_back – how many days back to look at lastmod (default 90)
      max_requests      – combined sitemap + detail fetches (default 60)
    """
    import xml.etree.ElementTree as ET

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    days_back = int(source_config.get("sitemap_days_back", 90))
    sitemap_cutoff = today - datetime.timedelta(days=days_back)

    sitemap_url = source_config["sitemap_url"]
    listing_url = source_config["url"]
    fetcher = make_fetcher(source_config)

    # Fetch sitemap
    try:
        sitemap_xml = fetcher.get(sitemap_url)
    except LimitExceeded as exc:
        log.warning("%s [jsonld/wix_sitemap]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [jsonld/wix_sitemap]: sitemap fetch failed: %s", venue["id"], exc)
        return []

    event_urls = _parse_wix_sitemap(sitemap_xml, sitemap_cutoff)
    log.info("%s [jsonld/wix_sitemap]: %d candidate URLs (lastmod >= %s)",
             venue["id"], len(event_urls), sitemap_cutoff)

    all_events: list = []
    section = source_config.get("section")
    for url in event_urls:
        try:
            html = fetcher.get(url)
        except LimitExceeded as exc:
            log.warning("%s [jsonld/wix_sitemap]: %s — stopping at %d events",
                        venue["id"], exc, len(all_events))
            break
        except Exception as exc:
            log.warning("%s [jsonld/wix_sitemap]: %s failed: %s", venue["id"], url, exc)
            continue

        page_soup = BeautifulSoup(html, "html.parser")
        for item in _all_ld_items(page_soup):
            if not _is_event(item):
                continue
            ev = _wix_ld_to_raw(item, venue, url, section)
            if ev is None:
                continue
            try:
                ev_date = datetime.date.fromisoformat(ev.date)
            except (ValueError, AttributeError):
                continue
            if yesterday <= ev_date <= cutoff:
                # Fallback: og:description / og:image when JSON-LD has none
                import dataclasses as _dc
                if not ev.description:
                    og_d = _og_meta(page_soup, "og:description")
                    if og_d:
                        ev = _dc.replace(ev, description=og_d, description_source="source")
                if not ev.image_url:
                    og_i = _og_meta(page_soup, "og:image")
                    if og_i and og_i.startswith("http"):
                        ev = _dc.replace(ev, image_url=og_i)
                all_events.append(ev)
                break  # one JSON-LD per Wix event page

    return all_events


def _parse_wix_sitemap(xml_text: str, since: datetime.date) -> list:
    """Parse a Wix event-pages sitemap and return URLs with lastmod >= since."""
    import xml.etree.ElementTree as ET
    NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        log.error("[jsonld/wix_sitemap]: sitemap XML parse error: %s", exc)
        return []

    urls = []
    for url_el in root.findall(f"{{{NS}}}url"):
        loc_el = url_el.find(f"{{{NS}}}loc")
        lastmod_el = url_el.find(f"{{{NS}}}lastmod")
        if loc_el is None:
            continue
        loc = (loc_el.text or "").strip()
        if not loc:
            continue
        if lastmod_el is not None:
            try:
                lm = datetime.date.fromisoformat((lastmod_el.text or "").strip()[:10])
                if lm < since:
                    continue
            except ValueError:
                pass
        urls.append(loc)
    return urls


def _wix_ld_to_raw(item: dict, venue: dict, page_url: str,
                   section: "str | None") -> "RawEvent | None":
    """Convert a Wix JSON-LD Event to RawEvent.

    Wix startDate includes Prague local time with correct UTC offset
    (e.g. +01:00 in winter, +02:00 in summer).  Time is extracted directly
    from the datetime string without any UTC conversion.
    """
    title = _str_or_none(item.get("name"))
    if not title:
        return None
    start_raw = _str_or_none(item.get("startDate"))
    if not start_raw:
        return None

    date_str, start_time = _parse_wix_datetime(start_raw)
    if not date_str:
        return None

    end_raw = _str_or_none(item.get("endDate"))
    _, end_time = _parse_wix_datetime(end_raw) if end_raw else (None, None)

    image_url = _resolve_image(item.get("image"), page_url)
    description = _clean_description(item.get("description"))

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=date_str,
        start_time=start_time,
        end_time=end_time,
        doors_time=None,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        sold_out=status_marks.ld_sold_out(item.get("offers")),
        room=None,
        ticket_url=None,
        image_url=image_url,
        description=description,
        description_source="source" if description else None,
        source={
            "type": "jsonld",
            "url": page_url,
            "external_id": None,
            "section": section,
        },
        flags=[],
        status=_event_status(item.get("eventStatus", "")),
    )


def _parse_wix_datetime(s: str) -> "tuple[str | None, str | None]":
    """Parse Wix ISO datetime like '2026-11-26T23:00:00+01:00'.

    Returns (date_iso, time_str) in Prague local time.  The offset in the
    string is the correct Prague offset (verified 2026-11-03 for Fuchs2):
    time is extracted directly without UTC conversion.
    """
    m = re.match(r"(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):\d{2}[+-]\d{2}:\d{2}", s.strip())
    if not m:
        # Fall back to date-only
        date_only = _parse_date_part(s)
        return date_only, None
    date_str = m.group(1)
    hour, minute = int(m.group(2)), int(m.group(3))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return date_str, None
    return date_str, f"{hour:02d}:{minute:02d}"


def parse_fuchs2(venue: dict, source_config: dict, html: str) -> list:
    """Parse a single Fuchs2 event detail page HTML (no HTTP; used in tests)."""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    section = source_config.get("section")
    page_url = source_config.get("url", "https://fuchs2.cz/events")
    result = []
    for item in _all_ld_items(BeautifulSoup(html, "html.parser")):
        if not _is_event(item):
            continue
        ev = _wix_ld_to_raw(item, venue, page_url, section)
        if ev is None:
            continue
        try:
            ev_date = datetime.date.fromisoformat(ev.date)
        except (ValueError, AttributeError):
            continue
        if yesterday <= ev_date <= cutoff:
            result.append(ev)
    return result


# ── MEC admin-ajax strategy (Čitárna Unijazz and any other MEC tile calendar) ──

def _fetch_mec_ajax(venue: dict, source_config: dict) -> list:
    """Fetch events from a WordPress site using the Modern Events Calendar (MEC)
    plugin tile view.  MEC renders months on demand via admin-ajax.php; we POST
    for the current month and the next `months_ahead` months and parse JSON-LD
    from each HTML response.

    Required source_config keys:
      ajax_url    – full URL to wp-admin/admin-ajax.php
      skin_id     – integer id of the MEC skin shortcode on the page, or
      atts_from_page – true: the calendar has no numeric skin id (Café V Lese,
                    task 089); the page at `url` is fetched once and its
                    `atts: "..."` string is sent instead of atts[id]
      url         – canonical listing URL (used as base for image resolution)
    Optional:
      months_ahead – how many months beyond the current one to fetch (default 1)
      ld_local_time – true: start_time = local part of the JSON-LD startDate
                    (Café V Lese writes Prague time with a wrong "+00:00" zone,
                    like O2; the zone is ignored, nothing is converted)

    Risk: if the site rebuilds and the skin_id changes, the adapter returns 0
    events.  This is caught by the existing "0 events" warning in main.py.
    """
    import requests as _requests
    from pipeline.fetch import _rate_limit, LimitExceeded, USER_AGENT

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    ajax_url = source_config["ajax_url"]
    months_ahead = int(source_config.get("months_ahead", 1))
    fetcher = make_fetcher(source_config)
    if source_config.get("atts_from_page"):
        try:
            atts = mec_atts_from_page(fetcher.get(source_config["url"]))
        except Exception as exc:
            log.warning("%s [jsonld/mec_ajax]: page fetch failed: %s", venue["id"], exc)
            return []
        if not atts:
            log.warning("%s [jsonld/mec_ajax]: no MEC atts on the page", venue["id"])
            return []
        base_data = atts
    else:
        base_data = {"atts[id]": str(int(source_config["skin_id"]))}

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
                data=mec_post_data(base_data, year, month),
                headers={"User-Agent": USER_AGENT,
                         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                timeout=30,
            )
            resp.raise_for_status()
            month_html = resp.json().get("month", "")
        except Exception as exc:
            log.warning("%s [jsonld/mec_ajax]: %04d-%02d failed: %s",
                        venue["id"], year, month, exc)
            continue

        for ev in parse_mec_month(venue, source_config, month_html):
            # Filter non-event announcements (e.g. "ZAVŘENO" / closed notices).
            # These appear as JSON-LD Event entries but are not actual events.
            if _is_closed_notice(ev.title):
                log.info("%s [jsonld/mec_ajax]: skipped non-event: %s", venue["id"], ev.title)
                continue
            try:
                ev_date = datetime.date.fromisoformat(ev.date)
            except (ValueError, AttributeError):
                continue
            if yesterday <= ev_date <= cutoff:
                all_events.append(ev)

    if source_config.get("follow_details"):
        all_events = _fetch_mec_detail_times(venue, source_config, all_events, fetcher)

    return all_events


def mec_atts_from_page(html: str) -> "str | None":
    """The url-encoded `atts: "..."` string of the MEC tile calendar script."""
    m = re.search(r'(?<![A-Za-z_])atts:\s*"([^"]+)"', html)
    return m.group(1) if m else None


def mec_post_data(base, year: int, month: int):
    """POST body for mec_tile_load_month: dict (skin id) or a url-encoded
    string (atts from the page, sent as the calendar's own JS sends it)."""
    if isinstance(base, str):
        return (f"action=mec_tile_load_month&mec_year={year}&mec_month={month:02d}&"
                f"{base}&apply_sf_date=0&navigator_click=true")
    data = {"action": "mec_tile_load_month", "mec_year": str(year),
            "mec_month": f"{month:02d}"}
    data.update(base)
    data.update({"navigator_click": "true", "apply_sf_date": "0"})
    return data


def parse_mec_month(venue: dict, source_config: dict, month_html: str) -> list:
    """Events of one MEC month response (no HTTP; used in tests)."""
    events = _parse_listing(venue, source_config, month_html)
    if not source_config.get("ld_local_time"):
        return events
    import dataclasses
    out = []
    soup = BeautifulSoup(month_html, "html.parser")
    starts = {}
    for item in _all_ld_items(soup):
        if _is_event(item):
            key = (_str_or_none(item.get("name")), _str_or_none(item.get("url")))
            starts.setdefault(key, _str_or_none(item.get("startDate")))
    for ev in events:
        raw = starts.get((ev.title, ev.source.get("url")))
        _, t = parse_loose_datetime(raw or "")
        out.append(dataclasses.replace(ev, start_time=t) if t else ev)
    return out


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

        # time
        det_time = None
        flags = list(ev.flags)
        et_el = soup.select_one(".event-time")
        if et_el:
            det_date, det_time = _parse_event_time_div(et_el.get_text(strip=True))
            if det_date and det_date != ev.date:
                flags.append("date_conflict")

        # description: .ct-text-block.event-content first (og:description is null for Čítárna)
        description = ev.description
        description_source = ev.description_source
        image_url = ev.image_url
        if not description:
            ct_el = soup.select_one(".ct-text-block.event-content")
            if ct_el:
                text = ct_el.get_text(separator=" ", strip=True)
                if text and len(text) >= 10:
                    description = text[:1000]
                    description_source = "source"
        if not description:
            og_d = _og_meta(soup, "og:description")
            if og_d:
                description = og_d
                description_source = "source"
        # task 066: the event's own image is the first slider image; og:image
        # is the site-wide photo and the JSON-LD image the logo (-> None).
        found, own = images.detail_image(venue["id"], html, detail_url)
        if found:
            image_url = own
        else:
            image_url = images.clean(venue["id"], image_url)

        updated.append(dataclasses.replace(
            ev,
            start_time=det_time if det_time else ev.start_time,
            flags=flags,
            description=description,
            description_source=description_source,
            image_url=image_url,
        ))
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
                         fetcher, today: datetime.date | None = None) -> list:
    """Fetch all paginated listing pages (endless_more pattern) and return events.

    Stops when there is no more 'endless_more' link, the request limit is hit,
    or every event on the last page is beyond the +180-day window.
    """
    if today is None:
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

    description = _clean_description(ld.get("description"))

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
        sold_out=status_marks.ld_sold_out(ld.get("offers")),
        ticket_url=None,
        image_url=_resolve_image(ld.get("image"), detail_url),
        description=description,
        description_source="source" if description else None,
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

def _is_closed_notice(title: str) -> bool:
    """Return True for non-event announcements from Čitárna Unijazz.

    Covers:
    - 'pro veřejnost ZAVŘENO' / 'CLOSED' — closed notices
    - 'otevřeno do HH:MM' — opening-hours notices (not events)
    """
    if not title:
        return False
    t = title.upper()
    if "ZAVŘENO" in t or "CLOSED" in t:
        return True
    # "otevřeno do" = operational notice about opening hours
    if "OTEVŘENO DO" in t:
        return True
    return False


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
    description = _clean_description(item.get("description"))

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
        sold_out=status_marks.ld_sold_out(item.get("offers")),
        ticket_url=None,  # offers.url points to the event page, not ticket sales
        image_url=_resolve_image(item.get("image"), base_url),
        description=description,
        description_source="source" if description else None,
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


_DESC_MAX = 1000


def _clean_description(val) -> "str | None":
    """Return plain-text description from a JSON-LD value, truncated to 1000 chars at sentence end."""
    if not isinstance(val, str):
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


def _event_status(status_str) -> str:
    """schema.org eventStatus -> RawEvent status (task 067: also postponed;
    EventRescheduled = new date already in startDate, only logged)."""
    st = status_marks.ld_status(status_str)
    if st in ("cancelled", "postponed"):
        return st
    if st == "rescheduled":
        log.info("jsonld: eventStatus %s — kept as scheduled", status_str)
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


def _og_meta(soup: BeautifulSoup, prop: str) -> "str | None":
    """Return content of a <meta property="og:…"> tag, truncated to 1000 chars."""
    el = soup.find("meta", property=prop)
    if not el:
        return None
    text = (el.get("content") or "").strip()
    if not text:
        return None
    return _clean_description(text)


def _origin(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"




# ── EventON strategy (Klub 007 Strahov, task 089) ─────────────────────────────

_LOOSE_DT_RE = re.compile(
    r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})(?:[T ](\d{1,2}):(\d{2}))?")
_PRICE_LINE_RE = re.compile(r"vstup|cena|entry|tickets?\b", re.I)


def parse_loose_datetime(s: str) -> "tuple[str | None, str | None]":
    """Date and local time from an ISO-like string, also when it is not valid
    ISO (EventON on Klub 007: "2026-12-3T19:00+1:00").  The zone is ignored:
    the local part is Prague time (nothing is converted through UTC)."""
    m = _LOOSE_DT_RE.match(s or "")
    if not m:
        return None, None
    try:
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None, None
    t = None
    if m.group(4) is not None:
        h, mn = int(m.group(4)), int(m.group(5))
        if h <= 23 and mn <= 59:
            t = f"{h:02d}:{mn:02d}"
    return d.isoformat(), t


def _fetch_eventon(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [jsonld/eventon]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [jsonld/eventon]: page fetch failed: %s", venue["id"], exc)
        return []
    return parse_eventon(venue, source_config, html)


def parse_eventon(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """EventON list on one page (no HTTP; used in tests).

    Each .eventon_list_event holds one JSON-LD Event and the subtitle
    (.evcal_event_subtitle, e.g. "Stoner Psych Rock") -> source.section (raw
    data for the classification, not a genre).  startDate = start; endDate time = end of
    the live music (web: "konec živé hudby je ve 22.00") -> end_time.  Price
    only from a description line like "Vstupné 300 Kč"."""
    import html as _html
    from pipeline.price import _AMOUNT_RE
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for box in soup.select(".eventon_list_event"):
        script = box.find("script", type="application/ld+json")
        if script is None:
            continue
        try:
            items = _flatten_ld(json.loads(script.string or ""))
        except (json.JSONDecodeError, ValueError):
            continue
        item = next((i for i in items if _is_event(i)), None)
        if item is None:
            continue
        title = _str_or_none(_html.unescape(item.get("name") or ""))
        date_str, start = parse_loose_datetime(_str_or_none(item.get("startDate")) or "")
        if not title or not date_str:
            continue
        d = datetime.date.fromisoformat(date_str)
        if d < yesterday or d > cutoff:
            continue
        url = _str_or_none(item.get("url")) or source_config["url"]
        if (url, date_str) in seen:
            continue
        seen.add((url, date_str))
        _, end = parse_loose_datetime(_str_or_none(item.get("endDate")) or "")
        if end == "23:59":
            end = None                      # EventON "until midnight" = no stated end
        desc_html = item.get("description") or ""
        price = None
        for line in BeautifulSoup(desc_html, "html.parser").get_text("\n").split("\n"):
            line = re.sub(r"\s+", " ", line).strip()
            if line and _PRICE_LINE_RE.search(line) and _AMOUNT_RE.search(line):
                price = line[:160]
                break
        sub_el = box.select_one(".evcal_event_subtitle")
        subtitle = re.sub(r"\s+", " ", sub_el.get_text(" ", strip=True)).strip() if sub_el else ""
        description = _clean_description(_html.unescape(desc_html))
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=date_str,
            start_time=start,
            end_time=end,
            doors_time=None,
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=[],
            price_text=price,
            free=None,
            sold_out=status_marks.ld_sold_out(item.get("offers")),
            ticket_url=None,
            image_url=_resolve_image(item.get("image"), url),
            description=description,
            description_source="source" if description else None,
            source={
                "type": "jsonld",
                "url": url,
                "external_id": _str_or_none(item.get("@id")),
                # subtitle (genre words / series name): raw data for the
                # classification, kept in the existing section field
                "section": subtitle or None,
            },
            flags=[],
            status=_event_status(item.get("eventStatus", "")),
        ))
    return out
