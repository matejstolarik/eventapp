"""
Manual additions (task 060 part 4): data/manual.json, written by the main
chat for Matej.

    {
      "artist_links": { "<artist name>": "https://open.spotify.com/artist/<ID>" },
      "events": { "<event_id>": { "formats": [...], "primary_format": "...",
                                  "genres": [...], "price_text": "...",
                                  "start_time": "HH:MM",
                                  "descriptions": {"cs": "...", "sk": "...", "en": "..."} } },
      "series": [ { "venue_id": "...", "title_contains": "...", "formats": [...],
                    "primary_format": "...", "genres": [...],
                    "descriptions": {"cs": "..."} } ]
    }

Manual values win over the AI and over the venue source (the source's
status cancelled / sold out is never touched: those fields cannot be set
here).  Order: series first, then the event entry (more specific).  Every
applied field gets `enrichment.<field> = {"by": "manual", "checked_at"}`.
A Spotify link is attached to every event whose artist (or a title part)
is that name (no accents / case); only these links are kept, AI links are
dropped (task 060 part 6).
"""

import json
import logging
import pathlib
import re
import unicodedata

log = logging.getLogger(__name__)

MANUAL_PATH = pathlib.Path("data/manual.json")
EVENT_FIELDS = ("formats", "primary_format", "genres", "price_text", "start_time", "descriptions")
SERIES_FIELDS = ("formats", "primary_format", "genres", "descriptions")
_SPOTIFY_RE = re.compile(r"^https://open\.spotify\.com/artist/[A-Za-z0-9]{22}$")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_TITLE_SPLIT = re.compile(r"\s+[-–+&/|x×]\s+|\s*[,:;+☆►•|]\s*|\s+(?:w/|feat\.?|ft\.?|b2b|vs\.?)\s+",
                          re.I)


def key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def load(path: pathlib.Path = MANUAL_PATH) -> dict:
    """Read and validate manual.json; invalid entries are logged and skipped."""
    empty = {"artist_links": {}, "events": {}, "series": []}
    if not path.exists():
        return empty
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning("manual.json unreadable (%s) - ignored", exc)
        return empty
    out = dict(empty)
    links = {}
    for name, url in (raw.get("artist_links") or {}).items():
        if isinstance(url, str) and _SPOTIFY_RE.match(url) and key(name):
            links[name] = url
        else:
            log.warning("manual.json artist_links %r: not an open.spotify.com/artist URL", name)
    out["artist_links"] = links
    events = {}
    for ev_id, fields in (raw.get("events") or {}).items():
        clean = _clean_fields(fields, EVENT_FIELDS, f"events[{ev_id}]")
        if clean:
            events[ev_id] = clean
    out["events"] = events
    series = []
    for i, s in enumerate(raw.get("series") or []):
        if not (isinstance(s, dict) and s.get("venue_id") and s.get("title_contains")):
            log.warning("manual.json series[%d]: venue_id and title_contains required", i)
            continue
        clean = _clean_fields(s, SERIES_FIELDS, f"series[{i}]")
        if clean:
            series.append({"venue_id": s["venue_id"], "title_contains": s["title_contains"], **clean})
    out["series"] = series
    return out


def _clean_fields(fields, allowed, where) -> dict:
    if not isinstance(fields, dict):
        return {}
    clean = {}
    for k, v in fields.items():
        if k in ("venue_id", "title_contains", "note"):
            continue
        if k not in allowed:
            log.warning("manual.json %s: field %r not allowed - ignored", where, k)
            continue
        if k in ("formats", "genres") and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            log.warning("manual.json %s.%s: list of strings expected", where, k)
            continue
        if k == "start_time" and not (isinstance(v, str) and _TIME_RE.match(v)):
            log.warning("manual.json %s.start_time: HH:MM expected", where)
            continue
        if k == "descriptions" and not (isinstance(v, dict) and v.get("cs")):
            log.warning("manual.json %s.descriptions: {cs, sk?, en?} with cs expected", where)
            continue
        if k in ("price_text", "primary_format") and not (isinstance(v, str) and v.strip()):
            continue
        clean[k] = v
    return clean


def series_for(ev: dict, manual: dict) -> dict | None:
    """First series entry matching the event (venue + title substring, no accents / case)."""
    t = key(ev.get("title"))
    for s in manual.get("series") or []:
        if s["venue_id"] == ev.get("venue_id") and key(s["title_contains"]) in t:
            return s
    return None


def is_known_series(ev: dict, manual: dict) -> bool:
    return series_for(ev, manual) is not None


def _set(ev: dict, field: str, value, today: str) -> None:
    ev[field] = value
    enr = ev.setdefault("enrichment", {})
    name = "description" if field == "descriptions" else field
    if field == "primary_format":
        return
    enr[name] = {"by": "manual", "checked_at": today}


def apply_manual(events: list[dict], manual: dict, today: str) -> tuple[list[dict], dict]:
    """Apply series and event entries.  Safe to call more than once."""
    stats = {"series": 0, "events": 0}
    out = []
    for ev in events:
        s = series_for(ev, manual)
        e = (manual.get("events") or {}).get(ev.get("id"))
        if not (s or e):
            out.append(ev)
            continue
        ev = dict(ev)
        ev["enrichment"] = json.loads(json.dumps(ev.get("enrichment") or {}))
        fields = {}
        if s:
            fields.update({k: v for k, v in s.items() if k in SERIES_FIELDS})
            stats["series"] += 1
        if e:
            fields.update(e)
            stats["events"] += 1
        for k, v in fields.items():
            _set(ev, k, v, today)
        if "formats" in fields or "genres" in fields:
            ev["classification"] = {"method": "manual", "confidence": 1.0}
            fmts = ev.get("formats") or []
            if ev.get("primary_format") not in fmts:
                ev["primary_format"] = fields.get("primary_format") if fields.get("primary_format") in fmts \
                    else (fmts[0] if len(fmts) == 1 else None)
        if "descriptions" in fields and (not ev.get("description") or ev.get("description_source") == "ai"):
            ev["description"] = fields["descriptions"]["cs"]
            ev["description_source"] = "manual"
        out.append(ev)
    return out, stats


def _artist_names(ev: dict) -> list[str]:
    names = list(ev.get("artists") or [])
    title = re.sub(r"\([^)]*\)", " ", ev.get("title") or "")
    names += [p for p in _TITLE_SPLIT.split(title) if p and p.strip()]
    return names


def apply_artist_links(events: list[dict], manual: dict, today: str) -> tuple[list[dict], dict]:
    """artist_links only from manual.json (task 060 part 6): AI links that are
    not in manual.json are dropped, manual links are attached by artist name."""
    by_key = {key(n): (n, u) for n, u in (manual.get("artist_links") or {}).items()}
    allowed = {u for _, u in by_key.values()}
    stats = {"attached": 0, "ai_dropped": 0}
    out = []
    for ev in events:
        links, seen = [], set()
        for name in _artist_names(ev):
            hit = by_key.get(key(name))
            if hit and hit[1] not in seen:
                links.append({"name": hit[0], "spotify_url": hit[1]})
                seen.add(hit[1])
        old = ev.get("artist_links") or []
        dropped = [l for l in old if l.get("spotify_url") not in allowed]
        if not (links or old):
            out.append(ev)
            continue
        ev = dict(ev)
        enr = dict(ev.get("enrichment") or {})
        stats["ai_dropped"] += len(dropped)
        if links:
            ev["artist_links"] = links[:5]
            enr["artist_links"] = {"by": "manual", "checked_at": today}
            stats["attached"] += 1
        else:
            ev.pop("artist_links", None)
            enr.pop("artist_links", None)
        ev["enrichment"] = enr
        out.append(ev)
    return out, stats
