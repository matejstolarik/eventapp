"""HTML adapter for Lucerna Music Bar (musicbar.cz/cs/program/, task 085).

The whole programme is on one page (#boxes_events a.program-item):
  .date strong        "Zítra<br>21/11" – day/month without a year
  span[data-start]    text = DOORS time, data-start = START time (verified in
                      083: Thom Artway listing 18:00, detail "Doors 18:00
                      Start 19:00"; they differ in 71 of 74 events)
  p                   title (whitespace collapsed); span.sold-out inside =
                      "– VYPRODÁNO" → sold_out = True, removed from the title
  .image img          300×300 image (static.goout.cloud, the venue's own site
                      is built by GoOut – allowed, Matej 2026-11-20)

The detail page's JSON-LD is invalid JSON (missing comma in "image"), so it
is not used.  The bigger og:image and the description come from the event
page via detail_enrich (once per event: pipeline.images rule + the source's
detail_desc_selector).

Year: the listing gives no year; a date before yesterday belongs to next
year (docs/data-model.md "Dátum bez roka").
"Soukromá akce" (private event) is not an event: skipped and logged.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_BASE = "https://musicbar.cz"
_DM_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})\b")
_TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")
_SKIP_TITLES = ("soukromá akce", "private event")


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/lucerna]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/lucerna]: listing fetch failed: %s", venue["id"], exc)
        return []
    return parse_listing(venue, source_config, html)


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """Parse the programme page (no HTTP; used in tests)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for item in soup.select("#boxes_events a.program-item"):
        ev = _parse_item(venue, item, today, yesterday, cutoff)
        if ev:
            events.append(ev)
    return events


def _parse_item(venue, item, today, yesterday, cutoff):
    href = (item.get("href") or "").strip()
    if not href:
        return None
    href = urljoin(_BASE, href)

    p = item.find("p")
    if p is None:
        return None
    sold_out = None
    for so in p.select(".sold-out"):
        sold_out = True
        so.extract()
    if item.select_one(".button.sold-out") is not None:
        sold_out = True
    title = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
    title = re.sub(r"\s+,", ",", title).strip(" –-")
    if not title:
        return None
    if title.lower() in _SKIP_TITLES:
        log.info("%s [html/lucerna] skipped: %s", venue["id"], title)
        return None

    strong = item.select_one(".date strong")
    m = _DM_RE.search(strong.get_text(" ", strip=True)) if strong else None
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    try:
        ev_date = datetime.date(today.year, month, day)
        if ev_date < yesterday:          # no year on the site: next year
            ev_date = datetime.date(today.year + 1, month, day)
    except ValueError:
        return None
    if ev_date < yesterday or ev_date > cutoff:
        return None

    span = item.select_one(".date span[data-start]")
    doors = start = None
    if span is not None:
        doors = _time(span.get_text(strip=True))
        start = _time(span.get("data-start") or "")
    if doors and doors == start:
        doors = None                       # same value: only the start is known

    img = item.select_one(".image img[src]")
    image_url = urljoin(_BASE, img["src"]) if img else None

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=ev_date.isoformat(),
        start_time=start,
        end_time=None,
        doors_time=doors,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        sold_out=sold_out,
        room=None,
        ticket_url=None,
        image_url=image_url,
        source={"type": "html", "url": href, "external_id": None, "section": None},
        flags=[],
        status="scheduled",
    )


def _time(text: str) -> "str | None":
    m = _TIME_RE.match(text or "")
    if not m:
        return None
    h, mn = int(m.group(1)), int(m.group(2))
    return f"{h:02d}:{mn:02d}" if h <= 23 and mn <= 59 else None
