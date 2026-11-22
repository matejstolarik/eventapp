"""HTML adapter for Sportovní hala Fortuna (sportovnihalafortuna.cz, task 086).

Listing /kalendar-akci: every event is in the calendar script
  events: [{date: new Date("2026-11-28"), eventName: "...",
            eventLink: "\\/kalendar-akci\\/<slug>"}, ...]
(the slider above it shows only some of them, with a time).

Detail page /kalendar-akci/<slug> (verified 2026-11-20/22, MANOWAR, HSU):
  h1 + "21/01/2027 20:00"; table th/td: datum "21.01.2027 20:00",
  vstup od "16:00" (doors), cena "od 1550,- Kč do 2.950,- Kč", prodej
  (first link = tickets); img.main-image = 1920×600 banner; .wysiwyg-editor
  = description.
The site has no event type.  Sport (Matej 086, same as O2) is recognised by
the title (hockey, MMA, …) or by the description calling it a sports event
/ match ("sportovní akce", "utkání", "zápas"); excluded and logged.

Detail pages are fetched only for new / changed events or every
DETAIL_RECHECK_DAYS days (source_config["detail_cache"]).
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

_BASE = "https://www.sportovnihalafortuna.cz"
_CAL_RE = re.compile(
    r'date:\s*new Date\("(\d{4}-\d{2}-\d{2})"\)\s*,\s*eventName:\s*"((?:[^"\\]|\\.)*)"\s*,'
    r'\s*eventLink:\s*"((?:[^"\\]|\\.)*)"')
_DT_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s+(\d{1,2}):(\d{2}))?")
_TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\b")
_SPORT_TITLE = re.compile(
    r"\b(hokej|florbal|volejbal|basketbal|házená|futsal|fotbal|tenis|box|mma|oktagon|"
    r"hsu|bitva o prahu|zápas|utkání|turnaj|liga|semifinále|finále|mistrovství|"
    r"sparta|slavia|hc |fc )", re.I)
_SPORT_TEXT = re.compile(r"sportovní akce|utkání|\bzápas", re.I)
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/fortuna]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/fortuna]: listing fetch failed: %s", venue["id"], exc)
        return []
    items = parse_listing(html, today)
    cache = source_config.get("detail_cache")
    if cache is None:
        cache = {}
    used, result, sport, stop = {}, [], [], False
    for it in items:
        url = it["url"]
        sig = dcache.signature(it["title"], [it["date"]])
        entry = cache.get(url)
        if not stop and dcache.needs_fetch(entry, sig, today.isoformat()):
            try:
                entry = {"sig": sig, "checked": today.isoformat(),
                         "data": parse_detail(fetcher.get(url))}
            except LimitExceeded as exc:
                log.warning("%s [html/fortuna]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/fortuna]: detail %s failed: %s", venue["id"], url, exc)
        if entry:
            used[url] = entry
        data = (entry or {}).get("data") or {}
        if is_sport(it["title"], data):
            sport.append(it["title"])
            continue
        result.append(make_event(venue, it, data))
    dcache.replace(cache, used)
    if sport:
        log.info("%s [html/fortuna]: %d sport events excluded: %s",
                 venue["id"], len(sport), "; ".join(sport))
    return result


def parse_listing(html: str, today: "datetime.date | None" = None) -> list[dict]:
    """[{date, title, url}] from the calendar script, in the window (no HTTP)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    out, seen = [], set()
    for d_str, name, link in _CAL_RE.findall(html):
        try:
            d = datetime.date.fromisoformat(d_str)
        except ValueError:
            continue
        name = _unescape(name)
        url = urljoin(_BASE, _unescape(link))
        if d < yesterday or d > cutoff or (url, d) in seen or not name:
            continue
        seen.add((url, d))
        out.append({"date": d, "title": re.sub(r"\s+", " ", name).strip(), "url": url})
    return sorted(out, key=lambda x: x["date"])


def _unescape(s: str) -> str:
    return re.sub(r"\\(.)", r"\1", s)


def parse_detail(html: str) -> dict:
    """Values from an event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup
    rows = {}
    for tr in main.select("table tr"):
        th, td = tr.find("th"), tr.find("td")
        if th and td:
            rows[th.get_text(" ", strip=True).lower()] = td
    date = time = None
    m = _DT_RE.search(rows["datum"].get_text(" ", strip=True)) if "datum" in rows else None
    if m:
        try:
            date = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            date = None
        if m.group(4):
            time = f"{int(m.group(4)):02d}:{m.group(5)}"
    doors = None
    if "vstup od" in rows:
        t = _TIME_RE.search(rows["vstup od"].get_text(" ", strip=True))
        if t:
            doors = f"{int(t.group(1)):02d}:{t.group(2)}"
    price = None
    if "cena" in rows:
        txt = re.sub(r"\s+", " ", rows["cena"].get_text(" ", strip=True)).strip()
        if re.search(r"\d", txt) and re.search(r"kč|czk|€|eur", txt, re.I):
            price = txt
    ticket = None
    if "prodej" in rows:
        a = rows["prodej"].find("a", href=True)
        if a and a["href"].startswith("http"):
            ticket = a["href"].strip()
    img = main.select_one("img.main-image[src]")
    image = urljoin(_BASE, img["src"]) if img else None
    ed = main.select_one(".wysiwyg-editor")
    desc = _clean(ed.get_text(" ", strip=True)) if ed else None
    return {"date": date, "time": time, "doors": doors, "price_text": price,
            "ticket_url": ticket, "image_url": image, "description": desc}


def is_sport(title: str, data: dict) -> bool:
    return bool(_SPORT_TITLE.search(title or "")
                or _SPORT_TEXT.search(data.get("description") or ""))


def make_event(venue: dict, it: dict, data: dict) -> RawEvent:
    date = it["date"].isoformat()
    # the time belongs to the detail's date; a changed date waits for recheck
    time = data.get("time") if data.get("date") == date else None
    doors = data.get("doors") if time else None
    return RawEvent(
        venue_id=venue["id"],
        title=it["title"],
        date=date,
        start_time=time,
        end_time=None,
        doors_time=doors if doors != time else None,
        formats=[],
        genres=[],
        character=list(venue.get("character") or []),
        artists=[],
        price_text=data.get("price_text"),
        free=None,
        sold_out=None,
        room=None,
        ticket_url=data.get("ticket_url"),
        image_url=data.get("image_url"),
        description=data.get("description"),
        description_source="source" if data.get("description") else None,
        source={"type": "html", "url": it["url"], "external_id": None, "section": None},
        flags=[],
        status="scheduled",
    )


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
