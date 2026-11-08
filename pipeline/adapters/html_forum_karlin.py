"""HTML adapter for Forum Karlín (forumkarlin.cz/program/).

Events are listed as .event blocks.  The listing includes a full date
(DD. MM. YYYY) but no start time; the detail page supplies both start time
(.datum .hodina) and optional doors time (#otevreni).

Ticket URLs come from #sellers .btn_static a on the detail page.  The first
link is used; if several sellers are listed all of them are listed in logs.

Sold-out / sticker state is read from .nalepka .msg on the listing card.

Detail pages are fetched for every event within the yesterday–+180 day window.
max_requests should cover 1 (listing) + number of in-window events.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_DATE_RE = re.compile(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    listing_url = source_config["url"]
    try:
        html = fetcher.get(listing_url)
    except LimitExceeded as exc:
        log.warning("%s [html/forum_karlin]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/forum_karlin]: listing fetch failed: %s", venue["id"], exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    listing_events = _parse_listing(venue, source_config, soup, yesterday, cutoff)

    # Fetch detail pages for start_time, doors_time and ticket_url
    result = []
    for ev in listing_events:
        detail_url = ev.source.get("url")
        if not detail_url:
            result.append(ev)
            continue
        try:
            detail_html = fetcher.get(detail_url)
        except LimitExceeded as exc:
            log.warning("%s [html/forum_karlin]: %s — remaining events have no time",
                        venue["id"], exc)
            result.append(ev)
            # append remaining without detail
            result.extend(listing_events[listing_events.index(ev) + 1:])
            break
        except Exception as exc:
            log.warning("%s [html/forum_karlin]: detail %s failed: %s",
                        venue["id"], detail_url, exc)
            result.append(ev)
            continue

        ev = _enrich_from_detail(ev, detail_html)
        result.append(ev)

    return result


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: datetime.date | None = None) -> list:
    """Parse the listing page (no HTTP; used in tests)."""
    if today is None:
        today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    return _parse_listing(venue, source_config, soup, yesterday, cutoff)


def parse_detail(ev, html: str):
    """Enrich a RawEvent from a detail page HTML (no HTTP; used in tests)."""
    return _enrich_from_detail(ev, html)


# ── listing parser ─────────────────────────────────────────────────────────────

def _parse_listing(venue, source_config, soup, yesterday, cutoff):
    section = source_config.get("section")
    events = []
    for card in soup.select(".event"):
        ev = _parse_card(venue, card, section, yesterday, cutoff)
        if ev:
            events.append(ev)
    return events


def _parse_card(venue, card, section, yesterday, cutoff):
    inner = card.select_one(".event_inner")
    if not inner:
        return None

    # ── title ──────────────────────────────────────────────────────────────
    title_el = inner.select_one("h3 a")
    if not title_el:
        return None
    title = title_el.get_text(strip=True)
    if not title:
        return None

    # ── detail URL ─────────────────────────────────────────────────────────
    detail_url = title_el.get("href") or (inner.select_one("a") and inner.select_one("a").get("href"))
    if not detail_url:
        return None
    if not detail_url.startswith("http"):
        detail_url = urljoin("https://www.forumkarlin.cz", detail_url)

    # ── date from .date text (DD. MM. YYYY) ────────────────────────────────
    date_el = inner.select_one(".date")
    if not date_el:
        return None
    # Remove the day-of-week span before parsing
    date_text = date_el.get_text(separator=" ").strip()
    m = _DATE_RE.search(date_text)
    if not m:
        return None
    try:
        ev_date = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None
    if ev_date < yesterday or ev_date > cutoff:
        return None

    # ── image ──────────────────────────────────────────────────────────────
    img_el = inner.select_one("img")
    image_url = img_el.get("src") if img_el else None

    # ── sold-out / sticker ─────────────────────────────────────────────────
    sold_out = None
    status = "scheduled"
    msg_el = inner.select_one(".nalepka .msg")
    if msg_el:
        msg = msg_el.get_text(separator=" ", strip=True).upper()
        if "VYPRODÁNO" in msg or "SOLD OUT" in msg:
            sold_out = True
        elif "ZRUŠENO" in msg or "CANCELLED" in msg:
            status = "cancelled"
        # "JIŽ BRZY" = not yet on sale; sold_out stays None

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=ev_date.isoformat(),
        start_time=None,    # filled from detail page
        end_time=None,
        doors_time=None,    # filled from detail page
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        sold_out=sold_out,
        room=None,
        ticket_url=None,    # filled from detail page
        image_url=image_url,
        source={
            "type": "html",
            "url": detail_url,
            "external_id": None,
            "section": section,
        },
        flags=[],
        status=status,
    )


# ── detail enrichment ──────────────────────────────────────────────────────────

def _enrich_from_detail(ev, html: str):
    import dataclasses
    soup = BeautifulSoup(html, "html.parser")

    # ── start time from .datum .hodina ─────────────────────────────────────
    start_time = None
    hodina_el = soup.select_one(".datum .hodina")
    if hodina_el:
        start_time = _parse_time(hodina_el.get_text(strip=True))

    # ── doors time from #otevreni ("Otevření dveří: HH:MM") ───────────────
    doors_time = None
    otevreni_el = soup.select_one("#otevreni")
    if otevreni_el:
        doors_time = _parse_time(otevreni_el.get_text())

    # ── ticket URL: first seller link in #sellers ──────────────────────────
    ticket_url = None
    sellers = soup.select("#sellers .btn_static a[href]")
    if sellers:
        first_href = sellers[0].get("href", "")
        if first_href.startswith("http"):
            ticket_url = first_href
        if len(sellers) > 1:
            extra = [s.get("href", "") for s in sellers[1:]]
            log.debug("%s [html/forum_karlin] %s: extra sellers: %s",
                      ev.venue_id, ev.title, extra)

    return dataclasses.replace(ev, start_time=start_time, doors_time=doors_time,
                               ticket_url=ticket_url)


# ── helpers ────────────────────────────────────────────────────────────────────

def _parse_time(text: str) -> "str | None":
    m = _TIME_RE.search(text)
    if not m:
        return None
    h, mn = int(m.group(1)), int(m.group(2))
    if 0 <= h <= 23 and 0 <= mn <= 59:
        return f"{h:02d}:{mn:02d}"
    return None
