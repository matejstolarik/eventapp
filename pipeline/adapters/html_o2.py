"""HTML adapter for O2 arena and O2 universum (task 085).

Both sites (www.o2arena.cz/events/, www.o2universum.cz/events/) show the
programme of BOTH venues on one page: an "O2arena" and an "O2universum"
section with the same .event_preview cards.  Each venue has its own source;
the adapter keeps only the cards whose detail link is on the venue's own
domain (source_config["domain"]), so no event is taken twice.

Listing card (.event_preview):
  p.time   "20.11.2026 20:00"; several dates on one card
           ("4.12.2026 19:00 5.12.2026 19:00") = one event per date;
           a range "5.12.2026 - 6.12.2026" = one event on the first day,
           no time (not guessed per day); empty = card skipped (no date)
  h3 a     title + detail URL
  .eye_catcher  background-image (1080×1080 poster)

Detail page (table.event_data, verified 2026-11-20 on The Prodigy, Papa
Roach, HC Sparta, FMX Gladiator Games):
  Typ akce   "Hokej, Sport" → any "Sport" = sport event, excluded (Matej 085)
  Vstup od   doors ("18:30"; "12:00 a 17:30" = per date of a multi-date card)
  Cena       first line of the first <p> ("1 830 – 4 690 Kč")
  JSON-LD    description only.  Its times carry a wrong zone "+00:00" on
             Prague local time (20:00+00:00 = 20:00 in Prague); the adapter
             takes times from the listing / table, never from JSON-LD.
  Prodej     first ticketportal / ticketmaster link → ticket_url

Two shows on the same day (Čechomor 15:00 + 20:00) would get the same event
id (venue-date-title), so the day is one event with the first time.

Detail pages are fetched only for new cards, cards whose dates changed, or
pages checked DETAIL_RECHECK_DAYS days ago (cache passed by main.py in
source_config["detail_cache"], kept in pipeline_state.json).
"""

import dataclasses
import datetime
import json
import logging
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent
from pipeline.adapters import detail_cache as dcache

log = logging.getLogger(__name__)

_DT_RE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s+(\d{1,2}):(\d{2}))?")
_RANGE_RE = re.compile(r"\d{1,2}\.\d{1,2}\.\d{4}\s*-\s*\d{1,2}\.\d{1,2}\.\d{4}")
_TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\b")
_BG_RE = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    today = datetime.date.today()
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/o2]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/o2]: listing fetch failed: %s", venue["id"], exc)
        return []

    cards = parse_listing(venue, source_config, html, today)
    cache = source_config.get("detail_cache")
    if cache is None:
        cache = {}
    used: dict = {}
    result, sport = [], []
    stop = False
    for card in cards:
        url = card["url"]
        sig = dcache.signature(card["title"], [d for d, _ in card["dates"]])
        entry = cache.get(url)
        if not stop and dcache.needs_fetch(entry, sig, today.isoformat()):
            try:
                detail_html = fetcher.get(url)
                entry = {"sig": sig, "checked": today.isoformat(),
                         "data": parse_detail(detail_html)}
            except LimitExceeded as exc:
                log.warning("%s [html/o2]: %s — remaining cards use cached / no detail",
                            venue["id"], exc)
                stop = True
            except Exception as exc:
                log.warning("%s [html/o2]: detail %s failed: %s", venue["id"], url, exc)
        if entry:
            used[url] = entry
        data = (entry or {}).get("data") or {}
        if data.get("sport"):
            sport.append(card["title"])
            continue
        result.extend(card_events(venue, source_config, card, data))
    dcache.replace(cache, used)
    if sport:
        log.info("%s [html/o2]: %d sport events excluded: %s",
                 venue["id"], len(sport), "; ".join(sport))
    return result


# ── listing ────────────────────────────────────────────────────────────────────

def parse_listing(venue: dict, source_config: dict, html: str,
                  today: "datetime.date | None" = None) -> list[dict]:
    """Cards of this venue's domain in the window (no HTTP; used in tests).

    -> [{url, title, dates: [(date, time|None)], image_url, range}]"""
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    domain = source_config.get("domain") or urlparse(source_config["url"]).netloc
    soup = BeautifulSoup(html, "html.parser")
    cards, seen = [], set()
    for card in soup.select(".event_preview"):
        a = card.select_one("h3 a[href]")
        if not a:
            continue
        url = a["href"].strip()
        if urlparse(url).netloc != domain or url in seen:
            continue
        seen.add(url)
        title = (a.get("title") or a.get_text(" ", strip=True)).strip()
        title = re.sub(r"\s+", " ", title)
        t_el = card.select_one("p.time")
        text = t_el.get_text(" ", strip=True) if t_el else ""
        if not text:
            log.info("%s [html/o2] skipped (no date on the card): %s", venue["id"], title)
            continue
        is_range = bool(_RANGE_RE.search(text))
        dates = _parse_dates(text, is_range)
        dates = [(d, t) for d, t in dates if yesterday <= d <= cutoff]
        if not dates:
            continue
        img = None
        eye = card.select_one(".eye_catcher")
        if eye is not None:
            m = _BG_RE.search(eye.get("style") or "")
            if m and m.group(1).startswith("http"):
                img = m.group(1)
        cards.append({"url": url, "title": title, "dates": dates, "image_url": img,
                      "range": is_range})
    return cards


def _parse_dates(text: str, is_range: bool) -> list:
    """[(date, 'HH:MM' | None)], one entry per day (first time of the day)."""
    out: dict = {}
    for m in _DT_RE.finditer(text):
        try:
            d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            continue
        t = f"{int(m.group(4)):02d}:{m.group(5)}" if m.group(4) else None
        if d not in out:
            out[d] = t
        if is_range:
            break           # range: first day only, no time
    return sorted(out.items())


# ── detail ─────────────────────────────────────────────────────────────────────

def parse_detail(html: str) -> dict:
    """Values from the detail page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    rows = {}
    for tr in soup.select("table.event_data tr"):
        tds = tr.find_all("td", recursive=False)
        if len(tds) >= 2:
            rows[tds[0].get_text(" ", strip=True)] = tds[1]
    types = []
    if "Typ akce" in rows:
        types = [t.strip() for t in rows["Typ akce"].get_text(" ", strip=True).split(",")
                 if t.strip()]
    doors = []
    if "Vstup od" in rows:
        doors = [f"{int(h):02d}:{mn}" for h, mn in _TIME_RE.findall(
            rows["Vstup od"].get_text(" ", strip=True))]
    price = None
    if "Cena" in rows:
        p = rows["Cena"].find("p")
        if p is not None:
            first = p.get_text("\n", strip=True).split("\n")[0].strip()
            first = re.sub(r"\s+", " ", first)
            if re.search(r"\d", first) and re.search(r"kč|czk|€|eur", first, re.I):
                price = first
    ticket = None
    if "Prodej / rezervace" in rows:
        for a in rows["Prodej / rezervace"].find_all("a", href=True):
            if a["href"].startswith("http"):
                ticket = a["href"]
                break
    description = None
    for sc in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(sc.string or "")
        except ValueError:
            continue
        if isinstance(data, dict) and str(data.get("@type", "")).endswith("Event"):
            description = _clean(data.get("description"))
            break
    return {"types": types, "sport": any(t.lower() == "sport" for t in types),
            "doors": doors, "price_text": price, "ticket_url": ticket,
            "description": description}


def card_events(venue: dict, source_config: dict, card: dict, data: dict) -> list:
    """RawEvents of one card (one per day) with detail values applied."""
    doors = data.get("doors") or []
    n = len(card["dates"])
    out = []
    for i, (d, t) in enumerate(card["dates"]):
        door = None
        if not card["range"]:
            if len(doors) == 1 and n == 1:
                door = doors[0]
            elif len(doors) == n and n > 1:
                door = doors[i]         # "12:00 a 17:30" for two dates
        out.append(RawEvent(
            venue_id=venue["id"],
            title=card["title"],
            date=d.isoformat(),
            start_time=t,
            end_time=None,
            doors_time=door,
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=[],
            price_text=data.get("price_text"),
            free=None,
            sold_out=None,
            room=None,
            ticket_url=data.get("ticket_url"),
            image_url=card.get("image_url"),
            description=data.get("description"),
            description_source="source" if data.get("description") else None,
            source={"type": "html", "url": card["url"], "external_id": None,
                    "section": ", ".join(data.get("types") or []) or None},
            flags=[],
            status="scheduled",
        ))
    return out


def _clean(text) -> "str | None":
    if not isinstance(text, str):
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 10:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    for marker in (". ", "! ", "? "):
        pos = cut.rfind(marker)
        if pos > 500:
            return cut[:pos + 1].strip()
    return cut.rsplit(" ", 1)[0] + "..."
