"""HTML adapter for Archa+ (archa-plus.cz/cz/program/).

Events are listed in .program-item blocks.  The ISO date is embedded in the
detail URL; additional batches are fetched via /cz/program/load-more, which
returns JSON {html, nextDateFrom}.

Ticket states detected from the listing HTML:
  span.btn-soldout         → sold_out = True
  span.tag "vstup zdarma"  → free = True, sold_out = False
  button.goout-sale-button → sold_out = False (GoOut widget; no direct URL)
  a.btn-tickets "Připravujeme" → not yet on sale; sold_out = null

Program-section tags (stored in sources[].section):
  divadlo, hudba, film, tanec, debata, workshop
  All tags are logged at DEBUG level for classification reference (task 013).

External venues: Archa+ occasionally lists events at other buildings.  The
listing page does not expose venue info; detection requires detail fetches.
With check_venue=false (default) all listed events are kept.
"""

import datetime
import json
import logging
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

LOAD_MORE_URL = "https://archa-plus.cz/cz/program/load-more"

_SECTION_TAGS = frozenset({
    "divadlo", "hudba", "film", "tanec", "debata", "workshop",
    "přednáška", "konference", "kvíz", "vernisáž", "performance", "premiéra",
})

_DATE_IN_URL = re.compile(r"/(\d{4}-\d{2}-\d{2})-")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*$")


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    all_events: list = []

    # ── initial listing page ──────────────────────────────────────────────────
    listing_url = source_config["url"]
    try:
        html = fetcher.get(listing_url)
    except LimitExceeded as exc:
        log.warning("%s [html/archa]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/archa]: listing fetch failed: %s", venue["id"], exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    all_events.extend(_parse_listing(venue, source_config, soup, yesterday, cutoff))

    # next-date-from from the load-more button on the initial page
    next_date_from = _extract_next_date(soup)

    # ── load-more batches ─────────────────────────────────────────────────────
    while next_date_from:
        # Stop if next batch starts beyond the cutoff
        try:
            next_dt = datetime.date.fromisoformat(next_date_from)
        except ValueError:
            break
        if next_dt > cutoff:
            break

        load_url = f"{LOAD_MORE_URL}?dateFrom={next_date_from}"
        try:
            text = fetcher.get(load_url)
        except LimitExceeded as exc:
            log.warning("%s [html/archa]: load-more %s", venue["id"], exc)
            break
        except Exception as exc:
            log.warning("%s [html/archa]: load-more %s failed: %s",
                        venue["id"], next_date_from, exc)
            break

        try:
            data = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            log.warning("%s [html/archa]: load-more response is not JSON", venue["id"])
            break

        batch_html = data.get("html", "")
        batch_soup = BeautifulSoup(batch_html, "html.parser")
        all_events.extend(_parse_listing(venue, source_config, batch_soup, yesterday, cutoff))

        next_date_from = data.get("nextDateFrom") or None

    return all_events


def parse(venue: dict, source_config: dict, html: str) -> list:
    """Parse a listing HTML page or fragment (no HTTP; used in tests)."""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    return _parse_listing(venue, source_config, soup, yesterday, cutoff)


# ── page parser ───────────────────────────────────────────────────────────────

def _parse_listing(venue, source_config, soup, yesterday, cutoff):
    section_override = source_config.get("section")
    events = []
    for item in soup.select(".program-item"):
        ev = _parse_item(venue, item, section_override, yesterday, cutoff)
        if ev:
            events.append(ev)
    return events


def _parse_item(venue, item, section_override, yesterday, cutoff):
    # ── detail URL (carries the ISO date) ─────────────────────────────────
    link_el = (item.select_one(".program-image a")
               or item.select_one(".performance-title h2 a")
               or item.select_one(".performance-date h2 a"))
    if not link_el or not link_el.get("href"):
        return None
    detail_url = link_el["href"]
    if not detail_url.startswith("http"):
        detail_url = urljoin("https://archa-plus.cz", detail_url)

    # ── date from URL ──────────────────────────────────────────────────────
    m = _DATE_IN_URL.search(detail_url)
    if not m:
        return None
    try:
        ev_date = datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None
    if ev_date < yesterday or ev_date > cutoff:
        return None

    # ── title ──────────────────────────────────────────────────────────────
    title_el = item.select_one(".performance-title h2 a") or item.select_one(".performance-title h1")
    if not title_el:
        return None
    title = title_el.get_text(separator=" ", strip=True)
    title = re.sub(r"\s+", " ", title).strip()
    if not title:
        return None

    # ── time from .performance-date h2 a text ─────────────────────────────
    start_time = None
    date_el = item.select_one(".performance-date h2 a")
    if date_el:
        date_text = date_el.get_text(separator=" ")
        m_time = _TIME_RE.search(date_text.strip())
        if m_time:
            h, mn = int(m_time.group(1)), int(m_time.group(2))
            if 0 <= h <= 23 and 0 <= mn <= 59:
                start_time = f"{h:02d}:{mn:02d}"

    # ── image ──────────────────────────────────────────────────────────────
    img_el = item.select_one(".program-image img")
    image_url = None
    if img_el and img_el.get("src"):
        src = img_el["src"]
        image_url = urljoin("https://archa-plus.cz", src) if not src.startswith("http") else src

    # ── tags ───────────────────────────────────────────────────────────────
    tags = [el.get_text(strip=True) for el in item.select(".tags span.tag")]
    log.debug("%s [html/archa] %s: tags=%s", venue["id"], title, tags)

    # ── section: first tag matching known program sections ─────────────────
    section = section_override
    if section is None:
        for t in tags:
            if t.lower() in _SECTION_TAGS:
                section = t
                break

    # ── ticket status ──────────────────────────────────────────────────────
    sold_out = None
    free = None
    ticket_url = None
    status = "scheduled"

    if item.select_one("span.btn-soldout"):
        sold_out = True
    elif any(t.lower() == "vstup zdarma" for t in tags):
        free = True
        sold_out = False
    elif item.select_one("button.goout-sale-button"):
        # GoOut widget button — tickets available but no direct purchase URL
        sold_out = False

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
        free=free,
        sold_out=sold_out,
        room=None,
        ticket_url=ticket_url,
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


# ── helper ─────────────────────────────────────────────────────────────────────

def _extract_next_date(soup: BeautifulSoup) -> "str | None":
    """Return the data-next-date-from value from the load-more button, or None."""
    btn = soup.select_one("a.btn-load-more[data-next-date-from]")
    if btn:
        return btn.get("data-next-date-from") or None
    return None
