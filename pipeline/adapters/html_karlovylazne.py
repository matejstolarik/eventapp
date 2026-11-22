"""HTML adapter for Karlovy Lázně (karlovylazne.cz/events, task 089).

SolidPixels site, server-rendered (083).  One venue: the five floors are
only named in the event text.  The listing shows the generic nights of the
current week (also the days already past - dropped by the date window) and
special nights (NYE).  Recurring tourist nights are added (Matej 2026-11-20).

Listing card (.entry-events):
  .entry-title a[href]                     title + detail URL (/udalosti/<slug>)
  .entry-meta-date_from .entry-meta-value  "16. November 2026, 22:00" (start)
  img[data-srcset]                         poster (largest srcset entry)
Detail page (only new / changed events, detail cache): .block-inline text
(floors + DJs + blurb) -> description, og:image -> image, "BUY TICKETS" link.
The same detail URL is reused every week (5-story-saturday), the cache
signature contains the date, so a new week fetches the page again.
"""

import datetime
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent
from pipeline.adapters import detail_cache as dcache

log = logging.getLogger(__name__)

_BASE = "https://www.karlovylazne.cz"
_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}
_DATE_RE = re.compile(r"(\d{1,2})\.\s*([A-Za-z]+)\s+(\d{4})(?:,\s*(\d{1,2}):(\d{2}))?")
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/karlovylazne]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/karlovylazne]: listing fetch failed: %s", venue["id"], exc)
        return []
    events = parse_listing(venue, source_config, html, today)
    cache = source_config.get("detail_cache")
    if cache is None:
        cache = {}
    used, result, stop = {}, [], False
    for ev in events:
        url = ev.source["url"]
        sig = dcache.signature(ev.title, [ev.date])
        entry = cache.get(url)
        if not stop and dcache.needs_fetch(entry, sig, today.isoformat()):
            try:
                entry = {"sig": sig, "checked": today.isoformat(),
                         "data": parse_detail(fetcher.get(url))}
            except LimitExceeded as exc:
                log.warning("%s [html/karlovylazne]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/karlovylazne]: detail %s failed: %s",
                            venue["id"], url, exc)
        if entry:
            used[url] = entry
        result.append(apply_detail(ev, (entry or {}).get("data") or {}))
    dcache.replace(cache, used)
    return result


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """Parse the events page (no HTTP; used in tests)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for card in soup.select(".entry-events"):
        a = card.select_one(".entry-title a[href]")
        d_el = card.select_one(".entry-meta-date_from .entry-meta-value")
        if a is None or d_el is None:
            continue
        title = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        parsed = parse_date(d_el.get_text(" ", strip=True))
        if not title or parsed is None:
            continue
        d, start = parsed
        if d < yesterday or d > cutoff:
            continue
        url = urljoin(_BASE, a["href"].strip())
        if (url, d) in seen:
            continue
        seen.add((url, d))
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=d.isoformat(),
            start_time=start,
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
            ticket_url=None,
            image_url=_largest_src(card.find("img")),
            source={"type": "html", "url": url, "external_id": None, "section": None},
            flags=[],
            status="scheduled",
        ))
    return out


def parse_date(text: str) -> "tuple[datetime.date, str | None] | None":
    """'16. November 2026, 22:00' -> (date, '22:00')."""
    m = _DATE_RE.search(text or "")
    if not m:
        return None
    month = _MONTHS.get(m.group(2).lower())
    if not month:
        return None
    try:
        d = datetime.date(int(m.group(3)), month, int(m.group(1)))
    except ValueError:
        return None
    start = None
    if m.group(4) is not None:
        h, mn = int(m.group(4)), int(m.group(5))
        if h <= 23 and mn <= 59:
            start = f"{h:02d}:{mn:02d}"
    return d, start


def parse_detail(html: str) -> dict:
    """Values from the event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    parts = []
    for block in soup.select(".row-main .block.block-inline"):
        text = block.get_text("\n", strip=True)
        if text:
            parts.append(text)
    desc = _clean(" ".join(parts)) if parts else None
    og = soup.find("meta", property="og:image")
    image = (og.get("content") or "").strip() if og else ""
    ticket = None
    for a in soup.find_all("a", href=True):
        if "buy tickets" in a.get_text(" ", strip=True).lower() and a["href"].startswith("http"):
            ticket = a["href"].strip()
            break
    return {"description": desc, "image_url": image if image.startswith("http") else None,
            "ticket_url": ticket}


def apply_detail(ev: RawEvent, data: dict) -> RawEvent:
    import dataclasses
    return dataclasses.replace(
        ev,
        description=data.get("description"),
        description_source="source" if data.get("description") else None,
        image_url=data.get("image_url") or ev.image_url,
        # the ticket link carries a booking-app date of the visit, not of the
        # event; only the generic reservation page is kept
        ticket_url=_ticket_base(data.get("ticket_url")),
    )


def _ticket_base(url: "str | None") -> "str | None":
    return url.split("?", 1)[0] if url else None


def _largest_src(img) -> "str | None":
    if img is None:
        return None
    srcset = img.get("data-srcset") or img.get("srcset") or ""
    best, best_w = None, -1
    for part in srcset.split(","):
        bits = part.strip().split()
        if len(bits) == 2 and bits[1].endswith("w") and bits[1][:-1].isdigit():
            w = int(bits[1][:-1])
            if w > best_w:
                best, best_w = bits[0], w
    if best:
        return urljoin(_BASE, best)
    src = img.get("src")
    return urljoin(_BASE, src) if src else None


def _clean(text) -> "str | None":
    if not text:
        return None
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 10:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    pos = cut.rfind(". ")
    return cut[:pos + 1] if pos > 500 else cut.rsplit(" ", 1)[0] + "..."
