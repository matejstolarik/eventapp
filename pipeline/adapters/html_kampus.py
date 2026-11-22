"""HTML adapter for Kampus Hybernská (kampushybernska.cz/program, task 089).

Webflow.  The programme list is paginated with the CMS key `9857990c`
(`?9857990c_page=N`, 20 cards a page, ~4 pages, about one month ahead).  All
events are taken, without a category filter (Matej 2026-11-22); the type is
decided by the classification like elsewhere.  One venue: rooms only as
`room` (e.g. "E.0 Sál").  If the pagination key changes, the list is empty
-> 0 events -> the existing zero-events warning.

Listing card (.event-card in the list whose pagination link has the key):
  data-id                       slug -> detail URL /program/<slug>
  .event-date-row (first)       "23.11." (no year), .date-to = last day
  .event-time                   "10:00 – 12:30" -> start / end
  .price-text                   "Zdarma" / "300 Kč" / "1 500 Kč za celý kurz"
  .event-card-meta-tag (3rd)    room
Detail page (only new / changed events, detail cache): full date with the
year (overrides the guessed year), "Druh akce" (category -> source.section),
"Vstupné", og:image, description (.w-richtext).
A multi-day card (conference 26.–27. 11.) is one event on the first day
(rule from 085).
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

_BASE = "https://www.kampushybernska.cz"
_DM_RE = re.compile(r"(\d{1,2})\s*\.\s*(\d{1,2})\s*\.\s*(\d{4})?")
_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})")
_FREE_RE = re.compile(r"^\s*zdarma\s*$|vstup\s+(?:zdarma|voln)", re.I)
_DESC_MAX = 1000
DEFAULT_PAGE_KEY = "9857990c"
MAX_PAGES = 8


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    key = source_config.get("page_key", DEFAULT_PAGE_KEY)
    base = source_config["url"]
    events, seen = [], set()
    for page in range(1, MAX_PAGES + 1):
        url = base if page == 1 else f"{base}?{key}_page={page}"
        try:
            html = fetcher.get(url)
        except LimitExceeded as exc:
            log.warning("%s [html/kampus]: %s — stopping at page %d", venue["id"], exc, page)
            break
        except Exception as exc:
            log.warning("%s [html/kampus]: page %d failed: %s", venue["id"], page, exc)
            break
        page_events, has_next = parse_listing(venue, source_config, html, today, key)
        for ev in page_events:
            if ev.source["url"] not in seen:
                seen.add(ev.source["url"])
                events.append(ev)
        if not has_next:
            break

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
                log.warning("%s [html/kampus]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/kampus]: detail %s failed: %s", venue["id"], url, exc)
        if entry:
            used[url] = entry
        ev = apply_detail(ev, (entry or {}).get("data") or {})
        if ev is not None:
            result.append(ev)
    dcache.replace(cache, used)
    return result


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None,
                  key: str = DEFAULT_PAGE_KEY) -> "tuple[list, bool]":
    """Cards of one programme page and whether a next page exists (no HTTP)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    soup = BeautifulSoup(html, "html.parser")
    lst, has_next = None, False
    # only the list's own links ("?<key>_page=N"); from page 2 on the other
    # lists' links carry both keys ("?7527e81e_page=2&<key>_page=2")
    for a in soup.find_all("a", href=re.compile(rf"^\?{re.escape(key)}_page=\d+$")):
        parent = a.find_parent(class_="w-dyn-list")
        if parent is not None and parent.select_one(".event-card"):
            lst = parent
            if "w-pagination-next" in (a.get("class") or []):
                has_next = True
    if lst is None:
        # last page: only a "previous" link, or no pagination at all
        for el in soup.find_all(attrs={"fs-cmsload-element": "list"}):
            parent = el.find_parent(class_="w-dyn-list")
            if parent is not None and parent.select_one(".event-card"):
                lst = parent
                break
    if lst is None:
        return [], False
    out = []
    for card in lst.select(".event-card"):
        slug = (card.get("data-id") or "").strip()
        a = card.select_one("a.event-card-title[href]")
        t_el = card.select_one(".event-card-title h3") or a
        if not slug or a is None or t_el is None:
            continue
        title = re.sub(r"\s+", " ", t_el.get_text(" ", strip=True)).strip()
        rows = card.select(".dates .event-date-row")
        if not title or not rows:
            continue
        d = guess_date(rows[0].get_text("", strip=True), today)
        if d is None or d < yesterday or d > cutoff:
            continue
        start, end = _times(card.select_one(".event-time"))
        price_el = card.select_one(".price-text")
        price = re.sub(r"\s+", " ", price_el.get_text(" ", strip=True)).strip() if price_el else ""
        tags = card.select(".event-card-meta-tag")
        room = None
        if len(tags) >= 3:
            room = re.sub(r"\s+", " ", tags[2].get_text(" ", strip=True)).strip() or None
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=d.isoformat(),
            start_time=start,
            end_time=end,
            doors_time=None,
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=[],
            price_text=price or None,
            free=True if price and _FREE_RE.search(price) else None,
            sold_out=None,
            room=room,
            ticket_url=None,
            image_url=None,
            source={"type": "html", "url": urljoin(_BASE, a["href"].strip()),
                    "external_id": None, "section": None},
            flags=[],
            status="scheduled",
        ))
    return out, has_next


def guess_date(text: str, today: datetime.date) -> "datetime.date | None":
    """'23.11.' (no year) -> the next such date from about a month ago on;
    the detail page's full date replaces it."""
    m = _DM_RE.search(text or "")
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    years = [int(m.group(3))] if m.group(3) else [today.year, today.year + 1]
    for y in years:
        try:
            d = datetime.date(y, month, day)
        except ValueError:
            continue
        if m.group(3) or d >= today - datetime.timedelta(days=31):
            return d
    return None


def parse_detail(html: str) -> dict:
    """Values from the event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    fields = {}
    for row in soup.select(".row.event-detail"):
        cells = row.find_all(class_="cell", recursive=False)
        if len(cells) < 2:
            continue
        label = cells[0].get_text(" ", strip=True)
        fields[label] = cells[1]
    date = None
    dcell = fields.get("Datum")
    if dcell is not None:
        first = dcell.select_one(".date-from") or dcell
        m = _DM_RE.search(first.get_text("", strip=True))
        if m and m.group(3):
            try:
                date = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
            except ValueError:
                pass
    category = None
    ccell = fields.get("Druh akce")
    if ccell is not None:
        names = [x.get_text(" ", strip=True) for x in ccell.select(".meta-list-item")]
        names = [n for n in dict.fromkeys(names) if n]
        category = ", ".join(names) or None
    price = None
    pcell = fields.get("Vstupné")
    if pcell is not None:
        label = pcell.select_one(".cell-label")
        if label is not None:
            label.extract()
        price = re.sub(r"\s+", " ", pcell.get_text(" ", strip=True)).strip() or None
    og = soup.find("meta", property="og:image")
    image = (og.get("content") or "").strip() if og else ""
    rich = soup.select_one(".w-richtext")
    desc = _clean(rich.get_text(" ", strip=True)) if rich else None
    if not desc:
        ogd = soup.find("meta", property="og:description")
        desc = _clean((ogd.get("content") or "") if ogd else "")
    return {"date": date, "category": category, "price_text": price,
            "image_url": image if image.startswith("http") else None, "description": desc}


def apply_detail(ev: RawEvent, data: dict) -> "RawEvent | None":
    import dataclasses
    date, flags = ev.date, list(ev.flags)
    if data.get("date") and data["date"] != ev.date:
        # the listing has no year; the detail's full date is the source value
        date = data["date"]
    price = data.get("price_text") or ev.price_text
    return dataclasses.replace(
        ev,
        date=date,
        flags=flags,
        price_text=price,
        free=True if price and _FREE_RE.search(price) else ev.free,
        image_url=data.get("image_url") or ev.image_url,
        description=data.get("description"),
        description_source="source" if data.get("description") else None,
        source={**ev.source, "section": data.get("category") or ev.source.get("section")},
    )


def _times(el) -> "tuple[str | None, str | None]":
    if el is None:
        return None, None
    found = _TIME_RE.findall(el.get_text(" ", strip=True))
    vals = [f"{int(h):02d}:{int(m):02d}" for h, m in found if int(h) <= 23 and int(m) <= 59]
    start = vals[0] if vals else None
    end = vals[1] if len(vals) > 1 else None
    return start, end


def _clean(text) -> "str | None":
    if not text:
        return None
    text = re.sub(r"\s+", " ", text.replace("‍", " ")).strip()
    if len(text) < 10:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    pos = cut.rfind(". ")
    return cut[:pos + 1] if pos > 500 else cut.rsplit(" ", 1)[0] + "..."
