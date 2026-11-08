"""HTML adapter for EPIC Prague (epicprague.com/program).

All events are on one page (no pagination).  Each event is a .program__item
div containing:
  - <time class="program__item-datetime" datetime="YYYY-MM-DD HH:MM">
  - <h2 class="program__item-heading"><a href="/program/ID/slug">Title<br></a>
  - .program__item-button-wrapper with Info and Vstupenky buttons;
    the ticket URL contains "tickets" in the href.

There are no hashtags or sections — formats are determined by AI layer 2.
Ticket URLs point to tickets.epicprague.com.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_BASE_URL = "https://www.epicprague.com"


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    listing_url = source_config["url"]
    try:
        html = fetcher.get(listing_url)
    except LimitExceeded as exc:
        log.warning("%s [html/epic]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/epic]: listing fetch failed: %s", venue["id"], exc)
        return []

    return parse_listing(venue, source_config, html, yesterday, cutoff)


def parse_listing(
    venue: dict,
    source_config: dict,
    html: str,
    yesterday: "datetime.date | None" = None,
    cutoff: "datetime.date | None" = None,
) -> list:
    """Parse the listing page HTML (no HTTP; used in tests)."""
    today = datetime.date.today()
    if yesterday is None:
        yesterday = today - datetime.timedelta(days=1)
    if cutoff is None:
        cutoff = today + datetime.timedelta(days=180)

    soup = BeautifulSoup(html, "html.parser")
    events = []
    for item in soup.select(".program__item"):
        ev = _parse_item(venue, item, yesterday, cutoff)
        if ev:
            events.append(ev)
    return events


# ── item parser ────────────────────────────────────────────────────────────────

def _parse_item(venue, item, yesterday, cutoff):
    # ── datetime ───────────────────────────────────────────────────────────
    time_el = item.select_one("time.program__item-datetime")
    if not time_el:
        return None
    dt_str = time_el.get("datetime", "")
    ev_date, start_time = _parse_datetime(dt_str)
    if ev_date is None:
        return None
    if ev_date < yesterday or ev_date > cutoff:
        return None

    # ── title ──────────────────────────────────────────────────────────────
    heading_el = item.select_one("h2.program__item-heading a")
    if not heading_el:
        return None
    # Strip the trailing <br> that wraps the text
    title = heading_el.get_text(strip=True)
    if not title:
        return None

    # ── detail URL ─────────────────────────────────────────────────────────
    detail_href = heading_el.get("href", "")
    if not detail_href:
        # Fall back to any <a> inside the item that links to /program/
        link = item.select_one("a[href^='/program/']")
        detail_href = link.get("href", "") if link else ""
    if not detail_href.startswith("http"):
        detail_href = urljoin(_BASE_URL, detail_href) if detail_href else _BASE_URL

    # ── ticket URL ─────────────────────────────────────────────────────────
    ticket_url = None
    for btn in item.select(".program__item-button-wrapper a[href]"):
        href = btn.get("href", "")
        if "ticket" in href.lower() and href.startswith("http"):
            ticket_url = href
            break

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=ev_date.isoformat(),
        start_time=start_time,
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
        source={
            "type": "html",
            "url": detail_href,
            "external_id": None,
            "section": None,
        },
        flags=[],
        status="scheduled",
    )


# ── helpers ────────────────────────────────────────────────────────────────────

def _parse_datetime(dt_str: str) -> "tuple[datetime.date | None, str | None]":
    """Parse 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD' into (date, time_str)."""
    dt_str = dt_str.strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?", dt_str)
    if not m:
        return None, None
    try:
        ev_date = datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None, None
    start_time = m.group(2) if m.group(2) else None
    return ev_date, start_time
