"""HTML adapter for El Magico (elmagico.cz/program/, task 090).

The programme page (WordPress + Bricks) always shows only the 2 nearest
events (083).  Each card (the block around `.hp-datum-akce`) has:
  .hp-datum-akce   day ("20"),  .hp-mesic-akce  month name ("Listopad") and
  year ("2026"),  .hp-den-akce  weekday,
  h3 a             title + link to the event page,
  img data-src     event flyer,
  .brxe-post-content  the full event text (the event page has the same text).
One GET a day; the event page is not fetched.

Time and price only when the text states them (nothing is guessed):
  "Začátek 21:00" / "Start: 21:00"               -> start_time
  (not "od 17:00": the texts use it for happy hours and opening hours)
  "Vstup 150Kč" / "Vstupné ..." line with an amount -> price_text
  "Vstup zdarma"                                  -> price_text, free=True
The whole month is on the monthly poster (source type `poster`, task 090).
"""

import datetime
import logging
import re

from bs4 import BeautifulSoup

from pipeline.fetch import make_fetcher, LimitExceeded
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

MONTHS_CS = {"leden": 1, "unor": 2, "brezen": 3, "duben": 4, "kveten": 5, "cerven": 6,
             "cervenec": 7, "srpen": 8, "zari": 9, "rijen": 10, "listopad": 11, "prosinec": 12}
_FOLD = str.maketrans("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ", "acdeeinorstuuyzACDEEINORSTUUYZ")
_T = r"([01]?\d|2[0-3])[:.]([0-5]\d)"
_START_RE = re.compile(rf"(?:začátek|\bstart)\s*:?\s*{_T}\b", re.I)
_PRICE_RE = re.compile(r"^.*\b(?:vstup(?:né)?|vstupenk[ay]|cena)\b.*$", re.I | re.M)
_AMOUNT_RE = re.compile(r"\d[\d .]*\s*(?:Kč|CZK|,-)", re.I)
_FREE_RE = re.compile(r"\bvstup(?:né)?\s+(?:je\s+)?zdarma\b", re.I)
_EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
_DESC_MAX = 1000


def fold(s: str) -> str:
    return (s or "").translate(_FOLD).lower().strip()


def fetch(venue: dict, source_config: dict) -> list:
    fetcher = make_fetcher(source_config)
    try:
        html = fetcher.get(source_config["url"])
    except LimitExceeded as exc:
        log.warning("%s [html/elmagico]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [html/elmagico]: programme fetch failed: %s", venue["id"], exc)
        return []
    return parse(venue, source_config, html)


def _clean(text: str) -> str:
    text = _EMOJI_RE.sub("", text)
    return re.sub(r"[ \t]+", " ", text).strip(" –-")


def _flyer(card):
    """The card's flyer: an uploaded image outside the post text (the text
    may contain Facebook emoji images)."""
    for img in card.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if "/wp-content/uploads/" in src and not img.find_parent(class_="brxe-post-content"):
            return img
    return None


def parse(venue: dict, source_config: dict, html: str) -> list:
    """Parse the programme page (no HTTP; used in tests)."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for day_el in soup.select(".hp-datum-akce"):
        card, img = day_el, None
        while card is not None and card.name != "body":
            if card.find("h3"):
                img = _flyer(card)
                if img is not None or len(card.select(".hp-datum-akce")) > 1:
                    break
            card = card.parent
        if card is None or len(card.select(".hp-datum-akce")) > 1:
            card, img = day_el.parent.parent, None        # card without a flyer
        if card is None:
            continue
        head = day_el.parent
        months = [m.get_text(strip=True) for m in head.select(".hp-mesic-akce")]
        try:
            day = int(day_el.get_text(strip=True))
            month = MONTHS_CS[fold(months[0])]
            year = int(months[1])
            date = datetime.date(year, month, day).isoformat()
        except (ValueError, KeyError, IndexError):
            log.warning("%s [html/elmagico]: unreadable date %r %r", venue["id"],
                        day_el.get_text(strip=True), months)
            continue
        link = card.select_one("h3 a[href]")
        if link is None:
            continue
        title = _clean(link.get_text(" ", strip=True))
        image = (img.get("data-src") or img.get("src") or "") if img else ""
        body = card.select_one(".brxe-post-content")
        blocks = [b for b in body.find_all(["p", "li", "div", "h2", "h3", "h4"])
                  if not b.find(["p", "li", "div"])] if body else []
        lines = [_clean(b.get_text(" ", strip=True)) for b in blocks]
        text = "\n".join(line for line in lines if line)
        start = None
        m = _START_RE.search(text)
        if m:
            start = f"{int(m.group(1)):02d}:{m.group(2)}"
        price, free = None, None
        if _FREE_RE.search(text):
            price, free = _FREE_RE.search(text).group(0), True
        else:
            for pm in _PRICE_RE.finditer(text):
                if _AMOUNT_RE.search(pm.group(0)):
                    price = pm.group(0).strip()
                    break
        out.append(RawEvent(
            venue_id=venue["id"], title=title, date=date, start_time=start, end_time=None,
            price_text=price, free=free,
            image_url=image if image.startswith("http") else None,
            description=text[:_DESC_MAX] or None,
            description_source="source" if text else None,
            source={"type": "html", "url": link["href"], "external_id": None, "section": None},
        ))
    return out
