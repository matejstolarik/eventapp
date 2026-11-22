"""HTML adapter for OX Club Prague (oxclubprague.com/program, task 089).

The visible cards in /program are a static template.  The real programme is
in the same HTML as base64 XML in the inline script `dios_xml_akce="..."`,
from which the site's JS renders the cards (088).  The XML is a list of
<radka> rows without a root element:
  index, nazev (title), popis (HTML text), datumakce ("D.M.YYYY"),
  mpic (poster 531×531), nazevurl, djs (line-up, <br /> separated),
  neprodavat (1 = private event, not sold).
Event link: /shop/b<index>-<nazevurl>.htm (only the same text + VIP offer +
Eventlook, so it is not fetched).  One GET a day.

Time and price only when the text states them (nothing is guessed):
  "Doors: 19:00" / "Otevření dveří: 18:30" / "Otevření klubu: 23:00" -> doors
  "Start: 20:00" / "Začátek koncertu: 19:30"                          -> start
  a header line "28. 11. 2026 | 23:00–04:30 | OX CLUB PRAGUE",
  "31. 12. 2026 / 21:00 / 18+", "🕘 21:00–02:00 (poslední vstup 22:30)",
  "⏰ 21:00"                                                          -> start (end)
  "Vstupenky: Od 1 100 Kč | M-Ticket" (line with an amount)          -> price
"PRIVATE EVENT" / neprodavat=1 are skipped (logged).
"""

import base64
import datetime
import logging
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

_BASE = "https://www.oxclubprague.com"
_XML_RE = re.compile(r'dios_xml_akce\s*=\s*"([A-Za-z0-9+/=\s]*)"')
_DATE_RE = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\s*$")
_T = r"(\d{1,2})[:.](\d{2})"
_DOORS_RE = re.compile(rf"(?:doors(?:\s+open)?|otevření\s+(?:dveří|klubu))\s*:?\s*{_T}", re.I)
_START_RE = re.compile(rf"(?:\bstart|začátek(?:\s+koncertu)?)\s*:?\s*{_T}", re.I)
# a line with a date then " | " or " / " then a time (optionally a range)
_HEADER_RE = re.compile(
    rf"\d{{1,2}}\s*[./]\s*\d{{1,2}}\s*[./]\s*\d{{4}}\s*[|/]\s*{_T}(?:\s*[–-]\s*{_T})?(?=\s*(?:[|/]|$))")
# a line that is only a time or a time range (after an emoji / symbols)
_TIME_ONLY_RE = re.compile(rf"^[^\w]*{_T}(?:\s*[–-]\s*{_T})?\s*(?:\(.*\))?\s*$")
_PRICE_LINE_RE = re.compile(r"vstupn|vstupenk|cena|tickets?|entry", re.I)
_PRIVATE_RE = re.compile(r"private\s+event|soukrom[áa]\s+akce", re.I)
_DESC_MAX = 1000


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/oxclub]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/oxclub]: programme fetch failed: %s", venue["id"], exc)
        return []
    return parse(venue, source_config, html)


def decode_xml(html: str) -> "str | None":
    m = _XML_RE.search(html)
    if not m:
        return None
    try:
        return base64.b64decode(re.sub(r"\s+", "", m.group(1))).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


def parse(venue: dict, source_config: dict, html: str,
          today: "datetime.date | None" = None) -> list:
    """Parse the programme page (no HTTP; used in tests)."""
    xml = decode_xml(html)
    if xml is None:
        log.warning("%s [html/oxclub]: no dios_xml_akce programme in the page", venue["id"])
        return []
    return parse_xml(venue, source_config, xml, today)


def parse_xml(venue: dict, source_config: dict, xml: str,
              today: "datetime.date | None" = None) -> list:
    today = today or datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    try:
        root = ET.fromstring(f"<root>{xml}</root>")
    except ET.ParseError as exc:
        log.warning("%s [html/oxclub]: XML parse error: %s", venue["id"], exc)
        return []
    out, skipped = [], []
    for row in root.findall("radka"):
        title = re.sub(r"\s+", " ", row.findtext("nazev") or "").strip()
        m = _DATE_RE.match(row.findtext("datumakce") or "")
        if not title or not m:
            continue
        try:
            d = datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            continue
        if d < yesterday or d > cutoff:
            continue
        if (row.findtext("neprodavat") or "").strip() == "1" or _PRIVATE_RE.search(title):
            skipped.append(f"{d.isoformat()} {title}")
            continue
        index = (row.findtext("index") or "").strip()
        slug = (row.findtext("nazevurl") or "").strip()
        url = f"{_BASE}/shop/b{index}-{slug}.htm" if index and slug else source_config["url"]
        lines = _lines(row.findtext("popis") or "")
        times = parse_times(lines)
        image = (row.findtext("mpic") or "").strip()
        out.append(RawEvent(
            venue_id=venue["id"],
            title=title,
            date=d.isoformat(),
            start_time=times["start"],
            end_time=times["end"],
            doors_time=times["doors"],
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=_artists(row.findtext("djs") or ""),
            price_text=parse_price_line(lines),
            free=None,
            sold_out=None,
            room=None,
            ticket_url=None,
            image_url=image or None,
            description=_clean(" ".join(lines)),
            description_source="source" if lines else None,
            source={"type": "html", "url": url, "external_id": index or None, "section": None},
            flags=[],
            status="scheduled",
        ))
    if skipped:
        log.info("%s [html/oxclub]: %d private events skipped: %s",
                 venue["id"], len(skipped), "; ".join(skipped))
    return out


def parse_times(lines: list) -> dict:
    """Doors / start / end as the text states them (see module doc)."""
    doors = start = end = None
    for line in lines:
        if doors is None:
            m = _DOORS_RE.search(line)
            if m:
                doors = _hm(m.group(1), m.group(2))
                continue
        if start is None:
            m = _START_RE.search(line)
            if m:
                start = _hm(m.group(1), m.group(2))
    if start is None:
        for line in lines:
            if _DOORS_RE.search(line):
                continue
            m = _HEADER_RE.search(line) or _TIME_ONLY_RE.match(line)
            if m:
                start = _hm(m.group(1), m.group(2))
                end = _hm(m.group(3), m.group(4)) if m.group(3) else None
                break
    if doors and doors == start:
        doors = None
    return {"doors": doors, "start": start, "end": end}


def parse_price_line(lines: list) -> "str | None":
    from pipeline.price import _AMOUNT_RE
    for line in lines:
        if _PRICE_LINE_RE.search(line) and _AMOUNT_RE.search(line):
            return line[:160]
    return None


def _lines(popis_html: str) -> list:
    text = BeautifulSoup(popis_html, "html.parser").get_text("\n")
    return [ln for ln in (re.sub(r"\s+", " ", x).strip() for x in text.split("\n")) if ln]


def _artists(djs: str) -> list:
    if not djs.strip():
        return []
    text = BeautifulSoup(djs, "html.parser").get_text("\n")
    return [a for a in (x.strip() for x in text.split("\n")) if a][:10]


def _hm(h, m) -> "str | None":
    h, m = int(h), int(m)
    return f"{h:02d}:{m:02d}" if h <= 23 and m <= 59 else None


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
