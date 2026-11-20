"""HTML adapter for Jazz Republic (jazzrepublic.cz/cz/program, task 085).

Listing: li.indexlist1 > a[href="/cz/program/2026-11-21-live-united"] –
the event date is the ISO date in the URL (the card shows only "SO 21 Lis"),
h2 = title, img = poster (/pict/product/face/<n>.jpg, same as og:image).

Detail page (.concert2, verified 2026-11-20):
  .concert21 strong   "Otevřeno 20:00–24:00" = club opening → doors_time;
                      the site gives no concert start ("second set from
                      22:30" is free text) → start_time null (Matej 085:
                      show the opening, like MeetFactory)
  p                   sections headed by coloured spans: BAND, KONCERT,
                      INFORMACE, VSTUPENKY, VIDEO.  KONCERT = description;
                      VSTUPENKY "vstup volný" → price_text "vstup volný",
                      free = True (only when the page says so)
Detail pages are fetched only for new / changed events or every
DETAIL_RECHECK_DAYS days (source_config["detail_cache"], see detail_cache).
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

_BASE = "https://www.jazzrepublic.cz"
_URL_DATE = re.compile(r"/program/(\d{4}-\d{2}-\d{2})-")
_OPEN_RE = re.compile(r"Otev[řr]eno\s+(\d{1,2}):(\d{2})", re.I)
_SECTIONS = ("BAND", "KONCERT", "INFORMACE", "VSTUPENKY", "VIDEO")
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/jazzrepublic]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/jazzrepublic]: listing fetch failed: %s", venue["id"], exc)
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
                log.warning("%s [html/jazzrepublic]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/jazzrepublic]: detail %s failed: %s",
                            venue["id"], url, exc)
        if entry:
            used[url] = entry
        result.append(apply_detail(ev, (entry or {}).get("data") or {}))
    dcache.replace(cache, used)
    return result


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """Parse the programme page (no HTTP; used in tests)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    events, seen = [], set()
    for li in soup.select("li.indexlist1"):
        a = li.find("a", href=True)
        if a is None:
            continue
        m = _URL_DATE.search(a["href"])
        if not m:
            continue
        try:
            d = datetime.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d < yesterday or d > cutoff:
            continue
        url = urljoin(_BASE, a["href"])
        if url in seen:
            continue
        seen.add(url)
        h2 = a.find("h2")
        title = re.sub(r"\s+", " ", h2.get_text(" ", strip=True)).strip() if h2 else ""
        if not title:
            continue
        img = a.find("img", src=True)
        events.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=d.isoformat(),
            start_time=None,
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
            image_url=urljoin(_BASE, img["src"]) if img else None,
            source={"type": "html", "url": url, "external_id": None, "section": None},
            flags=[],
            status="scheduled",
        ))
    return events


def parse_detail(html: str) -> dict:
    """Values from the event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one(".concert2") or soup
    doors = None
    head = box.select_one(".concert21")
    m = _OPEN_RE.search(head.get_text(" ", strip=True) if head else "")
    if m:
        doors = f"{int(m.group(1)):02d}:{m.group(2)}"
    sections = _sections(box.find("p"))
    desc = _clean(sections.get("KONCERT"))
    price = free = None
    tickets = (sections.get("VSTUPENKY") or "").lower()
    if re.search(r"vstup\w*\s+(je\s+)?voln", tickets) or "vstup zdarma" in tickets:
        price, free = "vstup volný", True
    return {"doors": doors, "description": desc, "price_text": price, "free": free}


def apply_detail(ev: RawEvent, data: dict) -> RawEvent:
    import dataclasses
    return dataclasses.replace(
        ev,
        doors_time=data.get("doors"),
        description=data.get("description"),
        description_source="source" if data.get("description") else None,
        price_text=data.get("price_text"),
        free=data.get("free"),
    )


def _sections(p) -> dict:
    """{HEADING: text} from a <p> whose parts are headed by coloured spans."""
    out: dict = {}
    if p is None:
        return out
    current, parts = None, []
    for node in p.children:
        name = getattr(node, "name", None)
        text = node.get_text(" ", strip=True) if name else str(node).strip()
        if name == "span" and text.upper() in _SECTIONS:
            if current:
                out[current] = " ".join(x for x in parts if x)
            current, parts = text.upper(), []
            continue
        if current and text:
            parts.append(text)
    if current:
        out[current] = " ".join(x for x in parts if x)
    return out


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
