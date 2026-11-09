import datetime
import html as _html_module
import re
from zoneinfo import ZoneInfo

import feedparser
import requests

from pipeline.models import RawEvent

PRAGUE_TZ = ZoneInfo("Europe/Prague")
USER_AGENT = "eventapp/0.1 (personal project; contact matejstolarik@gmail.com)"

_DESC_MAX = 1000


def _description_from_entry(entry) -> "str | None":
    """Extract plain-text description from an RSS entry, truncated to 1000 chars."""
    raw = entry.get("summary") or entry.get("description") or ""
    if isinstance(raw, list):
        raw = raw[0].get("value", "") if raw else ""
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = re.sub(r"<[^>]+>", " ", raw)
    text = _html_module.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    for marker in (". ", "! ", "? "):
        pos = cut.rfind(marker)
        if pos > _DESC_MAX // 2:
            return cut[: pos + 1].strip()
    return cut.rsplit(" ", 1)[0] + "..."


def fetch(venue: dict, source_config: dict) -> list:
    url = source_config["url"]
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return parse(venue, source_config, resp.text)


def parse(venue: dict, source_config: dict, xml_text: str) -> list:
    feed = feedparser.parse(xml_text)
    events = []
    for entry in feed.entries:
        date = _parse_date(entry)
        if date is None:
            continue
        description = _description_from_entry(entry)
        events.append(RawEvent(
            venue_id=venue["id"],
            title=entry.get("title", "").strip(),
            date=date,
            start_time=None,  # RSS encodes date as midnight UTC; no event start time available
            end_time=None,
            formats=[],
            genres=[],
            character=list(venue.get("character") or []),
            artists=[],
            price_text=None,
            free=None,
            ticket_url=None,  # RSS gives the event page URL, not a ticket sales link
            image_url=None,
            description=description,
            description_source="source" if description else None,
            source={
                "type": "rss",
                "url": entry.get("link") or source_config["url"],
                "external_id": entry.get("id") or None,
            },
        ))
    return events


def _parse_date(entry) -> str | None:
    parsed = getattr(entry, "published_parsed", None)
    if parsed is None:
        return None
    dt_utc = datetime.datetime(*parsed[:6], tzinfo=datetime.timezone.utc)
    dt_prague = dt_utc.astimezone(PRAGUE_TZ)
    return dt_prague.strftime("%Y-%m-%d")
