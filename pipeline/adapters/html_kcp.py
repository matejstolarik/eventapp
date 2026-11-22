"""HTML adapter for Kongresové centrum Praha (praguecc.cz, task 086).

Only the culture page /cs/prehled-akci/kultura (congresses are on another
page and are not taken).  One .blog-item card per event:
  small with .fa-calendar-alt   "09. 12. 2026" or a range
                                "04. 12. 2026 - 29. 03. 2027"
  .h4 a                         title
  img                           800×600 picture
  .collapse                     free text (description, sometimes dates and
                                times), first http link = tickets
The CSV export is not used (same events, fewer fields).

Rules (085/086):
- A card whose text lists dates explicitly ("5. 12. 2026 / představení od
  14:00 a 19:30", Monte Cristo ~30 shows) = one event per listed date in the
  card's range, time = first time stated for that date (two shows on one day
  = one event, the id would collide); a date without a time → null.
- A range without a listed date = one event on the first day, no time.
- A single date: time only when the text states it ("od 19:30", "začátek
  19:30", "v 19:30 hod"); otherwise null.  Times are rare on this site.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_BASE = "https://www.praguecc.cz"
_DATE_RE = re.compile(r"\b(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})\b")
_TIME_RE = re.compile(r"\b([01]?\d|2[0-3]):([0-5]\d)\b")
_START_RE = re.compile(
    r"(?:\bod|\bv|začátek|začíná|zahájení)\s*:?\s*([01]?\d|2[0-3]):([0-5]\d)\b", re.I)
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/kcp]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/kcp]: listing fetch failed: %s", venue["id"], exc)
        return []
    return parse_listing(venue, source_config, html)


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """Parse the culture page (no HTTP; used in tests)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for card in soup.select(".blog-item"):
        icon = card.select_one(".fa-calendar-alt")
        title_el = card.select_one(".h4 a") or card.select_one(".h4")
        if icon is None or title_el is None:
            continue
        title = re.sub(r"\s+", " ", title_el.get_text(" ", strip=True)).strip()
        head = _dates(icon.parent.get_text(" ", strip=True))
        if not title or not head:
            continue
        first, last = head[0], head[-1]
        collapse = card.select_one(".collapse")
        lines = _lines(collapse)
        listed = _listed_dates(lines, first, last)
        if len(listed) >= 2 or (listed and first != last):
            days = listed
        elif first != last:
            days = [(first, None)]                         # range: first day only
        else:
            days = [(first, _single_time(lines))]
        img = card.find("img", src=True)
        image = urljoin(_BASE, img["src"]) if img else None
        ticket = None
        if collapse is not None:
            for a in collapse.find_all("a", href=True):
                if a["href"].startswith("http"):
                    ticket = a["href"].strip()
                    break
        desc = _clean(" ".join(lines))
        anchor = collapse.get("id") if collapse is not None else None
        # no #anchor: the listing URL marks "no event page" for detail_enrich
        url = source_config["url"]
        for d, t in days:
            if d < yesterday or d > cutoff or (title, d) in seen:
                continue
            seen.add((title, d))
            out.append(RawEvent(
                venue_id=venue["id"],
                title=title,
                date=d.isoformat(),
                start_time=t,
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
                ticket_url=ticket,
                image_url=image,
                description=desc,
                description_source="source" if desc else None,
                source={"type": "html", "url": url, "external_id": anchor, "section": None},
                flags=[],
                status="scheduled",
            ))
    return out


def _dates(text: str) -> list:
    out = []
    for m in _DATE_RE.finditer(text or ""):
        try:
            out.append(datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))))
        except ValueError:
            continue
    return out


def _lines(collapse) -> list:
    if collapse is None:
        return []
    text = collapse.get_text("\n", strip=True)
    return [re.sub(r"\s+", " ", x).strip() for x in text.split("\n") if x.strip()]


def _listed_dates(lines: list, first, last) -> list:
    """[(date, time|None)] for lines that are only a date inside the range;
    the time is the first one on the following line(s) before the next date."""
    out: dict = {}
    for i, line in enumerate(lines):
        m = _DATE_RE.fullmatch(line.strip().rstrip(":"))
        if not m:
            continue
        try:
            d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            continue
        if not (first <= d <= last) or d in out:
            continue
        t = None
        for nxt in lines[i + 1:i + 3]:
            if _DATE_RE.fullmatch(nxt.strip().rstrip(":")):
                break
            tm = _TIME_RE.search(nxt)
            if tm:
                t = f"{int(tm.group(1)):02d}:{tm.group(2)}"
                break
        out[d] = t
    return sorted(out.items())


def _single_time(lines: list) -> "str | None":
    for line in lines:
        m = _START_RE.search(line)
        if m:
            return f"{int(m.group(1)):02d}:{m.group(2)}"
    return None


def _clean(text) -> "str | None":
    if not text:
        return None
    text = re.sub(r"^\s*:\s*\d+\s*", "", text)          # leading ": 1370" (hall capacity)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 10:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    pos = cut.rfind(". ")
    return cut[:pos + 1] if pos > 500 else cut.rsplit(" ", 1)[0] + "..."
