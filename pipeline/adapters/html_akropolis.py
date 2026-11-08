"""HTML adapter for Palác Akropolis (palacakropolis.cz).

The site has no JSON-LD or RSS.  Events are listed as .basic_cont3 elements
on per-genre pages (hudba/divadlo/off-program).  Dates are in Czech day-month
format without a year ("4. 11."); the year is inferred:

  date < yesterday  →  next year
  date > +180 days  →  skip (outside window)

Ticket availability comes from a lightweight JSON endpoint (/pub/vstupne_6)
that maps event_id to a {no, rs, url?} dict.  One request per pipeline run.

Code meanings from the `data` attribute of `.kas_box6` HTML elements
(comma-separated strings, index = code number, e.g. index 5 → "ZRUŠENO!"):
  1  → "KUP TEĎ!" — on sale via Akropolis; ticket URL page_id=42027
  2  → "VYPRODÁNO!" — sold out; verified on SPITFIRE DVACETJEDNA 2026-11-02
  3  → "VSTUP VOLNÝ!" — free entry
  4  → "JIŽ BRZY…!" — not yet on sale
  5  → "ZRUŠENO!" — cancelled; verified via kas_box6 data attribute
  6  → "PŘELOŽENO! ►" — postponed (no specific date yet)
  9  → "prodej ukončen" — sales ended
  10 → "prodej na místě" — sold at the door
  11 → "KUP TEĎ!" via external URL (vstupne_6 entry has a `url` field)

Akropolis also lists events at external venues.  Events whose parsed `room`
is not in source_config["own_rooms"] are skipped and logged.  Events with no
room are kept (they are assumed to be at Akropolis).

Pagination: ?plg_33527_page=N  (N=1 is the default; add the param for N>1).
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

# vstupne_6 "no" codes — see module docstring for full list
_SELLING = 1           # on sale, Akropolis ticket page
_SELLING_EXTERNAL = 11  # on sale, external URL in vstupne_6 entry
_SOLD_OUT = 2
_CANCELLED = 5         # "ZRUŠENO!" — verified via kas_box6 data attribute
_FREE = 3
_COMING_SOON = 4       # "JIŽ BRZY…!" — tickets not yet on sale
_POSTPONED = 6         # "PŘELOŽENO! ►"


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)

    vstupne = _fetch_vstupne(source_config, fetcher)

    all_events: list = []
    for genre_cfg in source_config.get("genres", []):
        try:
            events = _fetch_genre(venue, source_config, genre_cfg, fetcher,
                                  vstupne, yesterday, cutoff)
            all_events.extend(events)
        except Exception as exc:
            log.error("%s [html/akropolis] genre %s: %s",
                      venue["id"], genre_cfg.get("section", "?"), exc)

    return all_events


def parse(venue: dict, source_config: dict, html: str,
          vstupne: dict, genre_cfg: dict | None = None,
          today: datetime.date | None = None) -> list:
    """Parse a single listing page.  Used in tests (no HTTP)."""
    if today is None:
        today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    gc = genre_cfg or {"section": source_config.get("section")}
    return _parse_page(venue, source_config, gc, html, vstupne, yesterday, cutoff)


# ── per-genre fetch with pagination ──────────────────────────────────────────

def _fetch_genre(venue, source_config, genre_cfg, fetcher, vstupne, yesterday, cutoff):
    base_url = source_config["base_url"]
    no = source_config.get("no", "62")
    genre = genre_cfg["genre"]
    page_id = genre_cfg["page_id"]
    other_param = "&other=true" if genre_cfg.get("other") else ""
    pagination_param = source_config.get("pagination_param", "plg_33527_page")

    listing_url = f"{base_url}?genre={genre}&no={no}&page_id={page_id}{other_param}"

    all_events: list = []
    page = 1

    while True:
        page_url = listing_url if page == 1 else f"{listing_url}&{pagination_param}={page}"
        try:
            html = fetcher.get(page_url)
        except LimitExceeded as exc:
            log.warning("%s [html/akropolis]: %s — stopping at page %d for %s",
                        venue["id"], exc, page, genre_cfg.get("section", genre))
            break
        except Exception as exc:
            log.warning("%s [html/akropolis]: page %d for %s failed: %s",
                        venue["id"], page, genre_cfg.get("section", genre), exc)
            break

        events = _parse_page(venue, source_config, genre_cfg, html, vstupne, yesterday, cutoff)
        all_events.extend(events)

        # Check for next page link
        soup = BeautifulSoup(html, "html.parser")
        next_param = f"{pagination_param}={page + 1}"
        has_next = any(next_param in (a.get("href") or "") for a in soup.find_all("a", href=True))
        if not has_next:
            break

        # Stop early if all events on this page are beyond the cutoff
        page_dates = [e_date for e in events
                      if (e_date := _safe_date(e.date)) is not None]
        if page_dates and min(page_dates) > cutoff:
            break

        page += 1

    return all_events


# ── page parser ───────────────────────────────────────────────────────────────

def _parse_page(venue, source_config, genre_cfg, html, vstupne, yesterday, cutoff):
    soup = BeautifulSoup(html, "html.parser")
    section = genre_cfg.get("section")
    base_url = source_config.get("base_url", "https://palacakropolis.cz")
    no = source_config.get("no", "62")
    ticket_page_id = source_config.get("ticket_page_id", "42027")

    own_rooms_lower = {r.lower() for r in source_config.get("own_rooms", [])}
    events = []
    for item in soup.select(".basic_cont3"):
        ev = _parse_item(item, venue, base_url, no, section, ticket_page_id,
                         vstupne, yesterday, cutoff, own_rooms_lower)
        if ev:
            events.append(ev)
    return events


def _parse_item(item, venue, base_url, no, section, ticket_page_id,
                vstupne, yesterday, cutoff, own_rooms_lower=frozenset()):
    # Title
    title_el = item.select_one(".banner_m_title")
    if not title_el:
        return None
    title = title_el.get_text(strip=True)
    if not title:
        return None

    # Date: from the colored date badge (most reliable, avoids the "repeated" date span)
    date_el = item.select_one(".color_title_date")
    if not date_el:
        return None
    date_text = date_el.get_text(strip=True)  # e.g. "4. 11."
    date_str = _parse_date_no_year(date_text, yesterday, cutoff)
    if not date_str:
        return None

    # Time + Room: from the .fct40 span ("19:30, \xa0Velký sál")
    time_room_el = item.select_one(".fct40")
    start_time = None
    room = None
    if time_room_el:
        start_time, room = _parse_time_room(time_room_el.get_text())

    # Skip events at external venues (Akropolis lists events it organises elsewhere).
    # Events without a room are kept — they are assumed to be at Akropolis.
    if room is not None and own_rooms_lower and room.lower() not in own_rooms_lower:
        log.info("%s [html/akropolis] skipping '%s' — external venue '%s'",
                 venue["id"], title, room)
        return None

    # Event ID from kas_box6
    kas_el = item.select_one(".kas_box6")
    event_id = kas_el["id"] if kas_el and kas_el.get("id") else None

    # Detail URL from wrapping <a> (page_id=33824)
    parent_a = item.find_parent("a")
    detail_url = None
    if parent_a and parent_a.get("href"):
        href = parent_a["href"]
        if href.startswith("/"):
            detail_url = f"https://palacakropolis.cz{href}"
        elif href.startswith("http"):
            detail_url = href

    # Image
    img = item.select_one(".banner_m_image img")
    image_url = None
    if img and img.get("src"):
        src = img["src"]
        if src.startswith("/"):
            image_url = f"https://palacakropolis.cz{src}"
        else:
            image_url = src

    # Ticket status from vstupne_6 (see module docstring for code meanings)
    sold_out = None
    free = None
    ticket_url = None
    status = "scheduled"
    if event_id and vstupne:
        state = vstupne.get(event_id, {})
        state_no = state.get("no")
        if state_no == _SELLING:
            sold_out = False
            ticket_url = (f"https://palacakropolis.cz/work/33298"
                          f"?event_id={event_id}&no={no}&page_id={ticket_page_id}")
        elif state_no == _SELLING_EXTERNAL:
            sold_out = False
            ticket_url = (state.get("url") or
                          f"https://palacakropolis.cz/work/33298"
                          f"?event_id={event_id}&no={no}&page_id={ticket_page_id}")
        elif state_no == _FREE:
            sold_out = False
            free = True
        elif state_no == _SOLD_OUT:
            sold_out = True
        elif state_no == _CANCELLED:
            status = "cancelled"
        elif state_no == _COMING_SOON:
            log.debug("%s [html/akropolis] '%s' not yet on sale (vstupne code 4)",
                      venue["id"], title)
        elif state_no == _POSTPONED:
            log.warning("%s [html/akropolis] '%s' postponed (vstupne code 6) — keeping as scheduled",
                        venue["id"], title)
        elif state_no is not None:
            log.warning("%s [html/akropolis] '%s' unknown vstupne code %s",
                        venue["id"], title, state_no)

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
        free=free,
        sold_out=sold_out,
        room=room,
        ticket_url=ticket_url,
        image_url=image_url,
        source={
            "type": "html",
            "url": detail_url or f"https://palacakropolis.cz/work/33298",
            "external_id": event_id,
            "section": section,
        },
        flags=[],
        status=status,
    )


# ── vstupne API ───────────────────────────────────────────────────────────────

def _fetch_vstupne(source_config: dict, fetcher) -> dict:
    """Fetch /pub/vstupne_6 and return {event_id_str: {no, rs}} dict."""
    vstupne_url = source_config.get("vstupne_url")
    if not vstupne_url:
        return {}
    try:
        text = fetcher.get(vstupne_url)
        return json.loads(text)
    except Exception as exc:
        log.warning("akropolis vstupne fetch failed: %s — sold_out/ticket_url will be null", exc)
        return {}


# ── date/time helpers ─────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"(\d{1,2})\.\s*(\d{1,2})\.")


def _parse_date_no_year(text: str, yesterday: datetime.date,
                        cutoff: datetime.date) -> "str | None":
    """Parse a date without a year ('4. 11.') applying the year-inference rule.

    If the inferred date is before yesterday, add 1 year.
    If the result is beyond +180 days (cutoff), return None (outside window).
    """
    m = _DATE_RE.search(text.strip())
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    today = yesterday + datetime.timedelta(days=1)
    try:
        d = datetime.date(today.year, month, day)
    except ValueError:
        return None
    if d < yesterday:
        try:
            d = datetime.date(today.year + 1, month, day)
        except ValueError:
            return None
    if d > cutoff:
        return None
    return d.isoformat()


_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")


def _parse_time_room(text: str) -> "tuple[str | None, str | None]":
    """Parse '19:30, \\xa0Velký sál' into (time, room).

    The text is: '{time},  {room}' with possible non-breaking spaces.
    Returns (None, None) if time cannot be parsed.
    """
    text = text.strip()
    m = _TIME_RE.match(text)
    if not m:
        return None, None
    h, mn = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 23 and 0 <= mn <= 59):
        return None, None
    time_str = f"{h:02d}:{mn:02d}"

    # Room follows the first comma
    comma_idx = text.find(",")
    room = None
    if comma_idx != -1:
        room_raw = text[comma_idx + 1:].replace("\xa0", " ").strip()
        if room_raw:
            room = room_raw

    return time_str, room


def _safe_date(date_str: str) -> "datetime.date | None":
    try:
        return datetime.date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
