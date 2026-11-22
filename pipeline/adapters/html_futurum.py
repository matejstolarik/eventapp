"""HTML adapter for Futurum Music Bar (futurum.musicbar.cz/program, task 086).

A sister site of Lucerna Music Bar, but a different template (WordPress), so
the lucerna strategy does not fit (checked 2026-11-22).  Listing (008):
  a.event-lines[href]       detail URL (futurum.musicbar.cz/program/<slug>/)
    .line-date              "Neděle 22.11.2026"
    .event-lines-doors      "18:30" = DOORS (detail: "Doors 18:30 Start 19:30")
    .event-lines_title      title; "– VYPRODÁNO" → sold_out, removed
    img                     800×480 crop (the detail's og:image is the original)
Detail page .single-blok (verified on Moon Walker, Poletíme?):
  .block .half  "Doors:" / "Start:" / "Předprodej:" / "Cena na místě:"
  .event_content  description;  .ticket_button  ticket link;  og:image
The RSS feed is not used (10 items, pubDate = publishing date).

Events moved to another venue ("Poletíme? – PŘESUNUTO DO LUCERNA MUSIC BARU")
are skipped and logged: they belong to the other venue's programme, so the
Futurum and Lucerna events never mix.  "Soukromá akce" is skipped too.
Detail pages: only new / changed events or every DETAIL_RECHECK_DAYS days.
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

_BASE = "https://futurum.musicbar.cz"
_DATE_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
_TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")
_SOLD_RE = re.compile(r"\s*[–-]\s*vyprodáno\s*$", re.I)
_MOVED_RE = re.compile(r"přesunuto\s+do\b", re.I)
_SKIP_TITLES = ("soukromá akce", "private event")
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/futurum]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/futurum]: listing fetch failed: %s", venue["id"], exc)
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
                log.warning("%s [html/futurum]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/futurum]: detail %s failed: %s", venue["id"], url, exc)
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
    out, seen, skipped = [], set(), []
    for a in soup.select("a.event-lines[href]"):
        url = urljoin(_BASE, a["href"].strip())
        if url in seen:
            continue
        t_el = a.select_one(".event-lines_title")
        d_el = a.select_one(".line-date")
        if t_el is None or d_el is None:
            continue
        title = re.sub(r"\s+", " ", t_el.get_text(" ", strip=True)).strip()
        m = _DATE_RE.search(d_el.get_text(" ", strip=True))
        if not title or not m:
            continue
        try:
            d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            continue
        if d < yesterday or d > cutoff:
            continue
        if _MOVED_RE.search(title) or title.lower() in _SKIP_TITLES:
            skipped.append(title)
            continue
        seen.add(url)
        sold_out = None
        if _SOLD_RE.search(title):
            sold_out = True
            title = _SOLD_RE.sub("", title).strip()
        doors_el = a.select_one(".event-lines-doors")
        doors = _time(doors_el.get_text(strip=True)) if doors_el else None
        img = a.find("img", src=True)
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=d.isoformat(),
            start_time=None,
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
            image_url=urljoin(_BASE, img["src"]) if img else None,
            source={"type": "html", "url": url, "external_id": None, "section": None},
            flags=[],
            status="scheduled",
        ))
    if skipped:
        log.info("%s [html/futurum]: %d events skipped (moved / private): %s",
                 venue["id"], len(skipped), "; ".join(skipped))
    return out


def parse_detail(html: str) -> dict:
    """Values from the event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one(".single-blok") or soup
    fields = {}
    for half in box.select(".block .half"):
        k, v = half.find("strong"), half.find("span")
        if k and v:
            fields[k.get_text(" ", strip=True).rstrip(":").strip().lower()] = \
                re.sub(r"\s+", " ", v.get_text(" ", strip=True)).strip()
    parts = []
    if fields.get("předprodej"):
        parts.append(f"předprodej {fields['předprodej']}")
    if fields.get("cena na místě"):
        parts.append(f"na místě {fields['cena na místě']}")
    price = ", ".join(parts) if parts and re.search(r"\d", " ".join(parts)) else None
    content = box.select_one(".event_content")
    desc = _clean(content.get_text(" ", strip=True)) if content else None
    ticket = box.select_one("a.ticket_button[href]")
    og = soup.find("meta", property="og:image")
    image = (og.get("content") or "").strip() if og else ""
    return {"doors": _time(fields.get("doors", "")), "start": _time(fields.get("start", "")),
            "price_text": price, "description": desc,
            "ticket_url": ticket["href"].strip() if ticket and ticket["href"].startswith("http")
            else None,
            "image_url": image if image.startswith("http") else None}


def apply_detail(ev: RawEvent, data: dict) -> RawEvent:
    import dataclasses
    doors = data.get("doors") or ev.doors_time
    start = data.get("start")
    if doors and doors == start:
        doors = None                    # same value: only the start is known
    return dataclasses.replace(
        ev,
        doors_time=doors,
        start_time=start,
        price_text=data.get("price_text"),
        description=data.get("description"),
        description_source="source" if data.get("description") else None,
        ticket_url=data.get("ticket_url"),
        image_url=data.get("image_url") or ev.image_url,
    )


def _time(text: str) -> "str | None":
    m = _TIME_RE.match(text or "")
    if not m:
        return None
    h, mn = int(m.group(1)), int(m.group(2))
    return f"{h:02d}:{mn:02d}" if h <= 23 and mn <= 59 else None


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
