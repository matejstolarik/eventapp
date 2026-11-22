"""Source type `poster` (task 090): events from a monthly programme poster.

Strategy `elmagico`: El Magico publishes one poster per month,
/wp-content/uploads/YYYY/MM/program-<month>-YYYY-el-magico*.jpg (the file
name varies: -FINAL, -korekce-01; the upload folder can be the previous
month).  It is found through the WordPress media search
(source_config["media_url"], 1 GET a run) for the current and the next
month (Prague date).  The month and year come from the file name.

The poster is read with DeepSeek (pipeline.poster_read) only once: the
reading is kept in the venue's adapter cache (pipeline_state.json,
state["adapter_detail"][venue]["posters"]) under the image URL with the
media `modified` time and the SHA-256 of the image.  A new or changed poster
(new URL, new `modified` and different bytes) is read again.  A failed read
is not cached (next run tries again) and the old reading of the same URL,
if any, is kept.

Event from a poster row: title (the trailing "/VSTUP ZDARMA/"-like note goes
to price_text; "VSTUP ZDARMA" also sets free), date, time only if printed
(El Magico prints none), named DJs from the right column as artists
(collective names like "EL MÁGICO DJ'S" are not artists), no image (the app
shows the venue image, task 082), source {"type": "poster", "url": <image>}.
When the same event appears in the HTML programme it replaces this one
(pipeline.poster_merge).
"""

import datetime
import hashlib
import json
import logging
import re
from zoneinfo import ZoneInfo

from pipeline import poster_read
from pipeline.fetch import LimitExceeded, make_fetcher
from pipeline.models import RawEvent

log = logging.getLogger(__name__)

PRAGUE_TZ = ZoneInfo("Europe/Prague")
MONTHS_CS = ["leden", "unor", "brezen", "duben", "kveten", "cerven", "cervenec", "srpen",
             "zari", "rijen", "listopad", "prosinec"]
_NOTE_RE = re.compile(r"\s*/([^/]*\bVSTUP\b[^/]*)/\s*$", re.I)
_FREE_RE = re.compile(r"^\s*vstup\s+zdarma\s*$", re.I)
_COLLECTIVE_RE = re.compile(r"DJ['’]?S\s*$", re.I)

# spend of poster readings in this process (added to the run's DeepSeek budget by main.py)
_spent: list[float] = []


def take_spend() -> float:
    """Sum of poster reading costs since the last call (and reset)."""
    total = round(sum(_spent), 6)
    _spent.clear()
    return total


def months_wanted(today: datetime.date) -> list[tuple[int, int]]:
    nxt = (today.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return [(today.year, today.month), (nxt.year, nxt.month)]


def find_posters(media: list, months: list[tuple[int, int]]) -> dict:
    """{(year, month): media item} - newest `modified` per month."""
    out = {}
    for item in media if isinstance(media, list) else []:
        url = str(item.get("source_url") or "")
        name = url.rsplit("/", 1)[-1].lower()
        for y, m in months:
            if re.fullmatch(rf"program-{MONTHS_CS[m - 1]}-{y}-el-magico[\w-]*\.(?:jpe?g|png|webp)",
                            name):
                old = out.get((y, m))
                if old is None or str(item.get("modified") or "") > str(old.get("modified") or ""):
                    out[(y, m)] = item
    return out


def split_title(title: str) -> tuple[str, str | None, bool | None]:
    """'BEER PONG ... /VSTUP ZDARMA/' -> ('BEER PONG ...', 'VSTUP ZDARMA', True)."""
    m = _NOTE_RE.search(title)
    if not m:
        return title.strip(), None, None
    note = m.group(1).strip()
    clean = title[:m.start()].strip(" –-")
    return (clean or title.strip()), note, (True if _FREE_RE.match(note) else None)


def rows_to_events(venue: dict, rows: list[dict], poster_url: str) -> list:
    out = []
    for r in rows:
        title, note, free = split_title(r["title"])
        perf = r.get("performers")
        artists = [perf] if perf and not _COLLECTIVE_RE.search(perf) else []
        out.append(RawEvent(
            venue_id=venue["id"], title=title, date=r["date"], start_time=r.get("time"),
            end_time=None, artists=artists, price_text=note, free=free,
            source={"type": "poster", "url": poster_url, "external_id": None, "section": None},
        ))
    return out


def _mime(url: str) -> str:
    ext = url.rsplit(".", 1)[-1].lower()
    return {"png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")


def fetch(venue: dict, source_config: dict, today: datetime.date | None = None,
          read=poster_read.read_poster) -> list:
    if source_config.get("strategy") != "elmagico":
        log.warning("%s [poster]: unknown strategy %r", venue["id"], source_config.get("strategy"))
        return []
    today = today or datetime.datetime.now(PRAGUE_TZ).date()
    cache = source_config.get("detail_cache")
    store = cache.setdefault("posters", {}) if isinstance(cache, dict) else {}
    fetcher = make_fetcher(source_config)
    try:
        media = json.loads(fetcher.get(source_config["media_url"]))
    except LimitExceeded as exc:
        log.warning("%s [poster]: %s", venue["id"], exc)
        return []
    except Exception as exc:
        log.error("%s [poster]: media search failed: %s", venue["id"], exc)
        return []
    months = months_wanted(today)
    found = find_posters(media, months)
    if (months[0] not in found):
        log.warning("%s [poster]: no poster for %d/%d in the media search", venue["id"],
                    months[0][1], months[0][0])
    events, keep = [], {}
    for (y, m), item in sorted(found.items()):
        url = item["source_url"]
        entry = store.get(url)
        if entry and entry.get("modified") == item.get("modified") and "rows" in entry:
            keep[url] = entry
        else:
            try:
                image = fetcher.get_bytes(url)
            except Exception as exc:
                log.warning("%s [poster]: image download failed %s: %s", venue["id"], url, exc)
                if entry:
                    keep[url] = entry
                continue
            sha = hashlib.sha256(image).hexdigest()
            if entry and entry.get("sha256") == sha and "rows" in entry:
                entry = {**entry, "modified": item.get("modified")}
            else:
                res = read(image, _mime(url))
                _spent.append(float(res.get("cost_usd") or 0))
                rows, dropped = poster_read.check_rows(res.get("raw"), y, m)
                if res.get("raw") is None:
                    log.warning("%s [poster]: reading %s failed: %s", venue["id"], url,
                                res.get("error"))
                    if entry:
                        keep[url] = entry
                    continue
                for d in dropped:
                    log.warning("%s [poster]: row dropped (%s): %s", venue["id"],
                                url.rsplit("/", 1)[-1], d)
                entry = {"modified": item.get("modified"), "sha256": sha, "month": f"{y}-{m:02d}",
                         "read_at": today.isoformat(), "model": poster_read.MODEL,
                         "cost_usd": res.get("cost_usd"), "usage": res.get("usage"),
                         "rows": rows, "dropped": dropped}
                log.info("%s [poster]: read %s: %d rows, %d dropped, $%.6f", venue["id"], url,
                         len(rows), len(dropped), float(res.get("cost_usd") or 0))
            keep[url] = entry
        events.extend(rows_to_events(venue, keep[url]["rows"], url))
    store.clear()
    store.update(keep)
    return events
