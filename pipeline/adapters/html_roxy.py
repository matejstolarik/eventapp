"""HTML adapter for ROXY Prague (roxy.cz/club/).

The full programme is on one page.  Each event is an <a class="item"> link
with a data-hashtags attribute (pipe-separated, e.g. "#dj|#techno") and a
<time class="date" datetime="YYYY-MM-DD HH:MM"> element.

data-hashtags → formats mapping (first format-hashtag wins):
  #concert, #live → ["concert"]
  #dj             → ["dj"]
  #party          → ["dj", "party"]
  others          → let AI classify (formats=[])

The first format-hashtag is stored as sources[].section so classify.py and
the job summary can see it; genre-only hashtags (#techno, #house, …) are
logged at DEBUG level and not stored.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

# Hashtags that indicate a format; order matters (first match wins).
_FORMAT_HASHTAGS: dict[str, list[str]] = {
    "concert": ["concert"],
    "live":    ["concert"],   # old name, still used on site
    "dj":      ["dj"],
    "party":   ["dj", "party"],
}

_BASE_URL = "https://www.roxy.cz"


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    listing_url = source_config["url"]
    try:
        html = fetcher.get(listing_url)
    except LimitExceeded as exc:
        log.warning("%s [html/roxy]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/roxy]: listing fetch failed: %s", venue["id"], exc)
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
    for item in soup.select("a.item"):
        ev = _parse_item(venue, item, yesterday, cutoff)
        if ev:
            events.append(ev)
    return events


# ── item parser ────────────────────────────────────────────────────────────────

def _parse_item(venue, item, yesterday, cutoff):
    # ── detail URL ─────────────────────────────────────────────────────────
    href = item.get("href", "")
    if not href:
        return None
    if not href.startswith("http"):
        href = urljoin(_BASE_URL, href)

    # ── datetime from <time class="date" datetime="..."> ──────────────────
    time_el = item.select_one("time.date")
    if not time_el:
        return None
    dt_str = time_el.get("datetime", "")
    ev_date, start_time = _parse_datetime(dt_str)
    if ev_date is None:
        return None
    if ev_date < yesterday or ev_date > cutoff:
        return None

    # ── title from h2.title ───────────────────────────────────────────────
    title_el = item.select_one("h2.title")
    if not title_el:
        return None
    title = title_el.get_text(strip=True)
    if not title:
        return None

    # ── data-hashtags → formats + section ────────────────────────────────
    raw_tags = item.get("data-hashtags", "")
    formats, section = _parse_hashtags(raw_tags, venue["id"], title)

    return RawEvent(
        venue_id=venue["id"],
        title=title,
        date=ev_date.isoformat(),
        start_time=start_time,
        end_time=None,
        doors_time=None,
        formats=formats,
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=None,
        free=None,
        sold_out=None,
        room=None,
        ticket_url=None,
        image_url=None,
        source={
            "type": "html",
            "url": href,
            "external_id": None,
            "section": section,
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


def _parse_hashtags(raw: str, venue_id: str, title: str) -> "tuple[list[str], str | None]":
    """Return (formats, section) from a pipe-separated data-hashtags string."""
    tags = [t.strip().lstrip("#").lower() for t in raw.split("|") if t.strip().lstrip("#")]

    for tag in tags:
        if tag in _FORMAT_HASHTAGS:
            formats = _FORMAT_HASHTAGS[tag]
            section = tag if tag != "live" else "concert"  # normalise old name
            # Log non-format tags for context
            others = [t for t in tags if t not in _FORMAT_HASHTAGS]
            if others:
                log.debug("%s [html/roxy] '%s': genre tags %s", venue_id, title, others)
            return list(formats), section

    # No format hashtag found — let AI classify
    if tags:
        log.debug("%s [html/roxy] '%s': no format hashtag in %s", venue_id, title, tags)
    return [], None
