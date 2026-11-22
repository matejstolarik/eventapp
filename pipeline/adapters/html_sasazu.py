"""HTML adapter for SaSaZu (www.sasazu-club.com/kalendar, task 086).

The club's own site (not the restaurant sasazu.com) is a Next.js app.  The
calendar page carries its data in the React Server Components payload
(self.__next_f.push([1, "..."]) script chunks):
  "entries": [{"visibility": "public", "id": <uuid>, "date": "2026-11-21",
               "title": "Portugal. The Man (USA)", "description": ...}]
A long description is a reference "$1c" to a text row "1c:T<hex bytes>,<text>"
elsewhere in the payload.

No time anywhere (not on the event page either) → start_time null.
Event page /akce/<id>: og:image (1080×608 poster) and the "Buy tickets" link.
It is fetched only for new / changed events or every DETAIL_RECHECK_DAYS
days (source_config["detail_cache"], see detail_cache).
"""

import datetime
import json
import logging
import re

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent
from pipeline.adapters import detail_cache as dcache

log = logging.getLogger(__name__)

_BASE = "https://www.sasazu-club.com"
_PUSH_RE = re.compile(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', re.S)
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/sasazu]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/sasazu]: listing fetch failed: %s", venue["id"], exc)
        return []
    events = parse_listing(venue, source_config, html, today)
    if not events:
        log.warning("%s [html/sasazu]: no entries in the page payload", venue["id"])
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
                log.warning("%s [html/sasazu]: %s — rest from cache / listing only",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/sasazu]: detail %s failed: %s", venue["id"], url, exc)
        if entry:
            used[url] = entry
        result.append(apply_detail(ev, (entry or {}).get("data") or {}))
    dcache.replace(cache, used)
    return result


def payload_text(html: str) -> str:
    """The concatenated RSC payload of the page."""
    parts = []
    for chunk in _PUSH_RE.findall(html):
        try:
            parts.append(json.loads('"' + chunk + '"'))
        except ValueError:
            continue
    return "".join(parts)


def _resolve_ref(payload: str, value):
    """'$1c' → text of row '1c:T<hexlen>,<text>'; plain strings unchanged."""
    if not isinstance(value, str):
        return None
    m = re.fullmatch(r"\$([0-9a-f]+)", value)
    if not m:
        return value
    row = re.search(r"(?:^|\n)" + m.group(1) + r":T([0-9a-f]+),", payload)
    if not row:
        return None
    size = int(row.group(1), 16)
    return payload[row.end():].encode("utf-8")[:size].decode("utf-8", "ignore")


def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list:
    """Events from the calendar payload (no HTTP; used in tests)."""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    payload = payload_text(html)
    i = payload.find('"entries":')
    if i < 0:
        return []
    try:
        entries, _ = json.JSONDecoder().raw_decode(payload[i + len('"entries":'):])
    except ValueError:
        return []
    out, seen = [], set()
    for e in entries if isinstance(entries, list) else []:
        if not isinstance(e, dict) or e.get("visibility", "public") != "public":
            continue
        title = re.sub(r"\s+", " ", str(e.get("title") or "")).strip()
        eid = str(e.get("id") or "").strip()
        try:
            d = datetime.date.fromisoformat(str(e.get("date") or ""))
        except ValueError:
            continue
        if not title or not eid or eid in seen or d < yesterday or d > cutoff:
            continue
        seen.add(eid)
        desc = _clean(_resolve_ref(payload, e.get("description")))
        url = f"{_BASE}/akce/{eid}"
        out.append(RawEvent(
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
            image_url=None,
            description=desc,
            description_source="source" if desc else None,
            source={"type": "html", "url": url, "external_id": eid, "section": None},
            flags=[],
            status="scheduled",
        ))
    return out


def parse_detail(html: str) -> dict:
    """og:image and the ticket link of an event page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    img = soup.find("meta", property="og:image")
    image = (img.get("content") or "").strip() if img else ""
    ticket = None
    for a in soup.find_all("a", href=True):
        if re.search(r"buy tickets|vstupenky|koupit", a.get_text(" ", strip=True), re.I) \
                and a["href"].startswith("http"):
            ticket = a["href"].strip()
            break
    return {"image_url": image if image.startswith("http") else None, "ticket_url": ticket}


def apply_detail(ev: RawEvent, data: dict) -> RawEvent:
    import dataclasses
    return dataclasses.replace(ev, image_url=data.get("image_url"),
                               ticket_url=data.get("ticket_url"))


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
