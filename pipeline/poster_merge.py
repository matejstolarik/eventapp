"""
Task 090: an event from the HTML programme replaces the same event from the
monthly poster (source type `poster`).

Pairing per venue and date: title similarity = shared words / words of the
shorter title (after folding case, diacritics and punctuation; short filler
words ignored).  A pair needs similarity >= MIN_SCORE and at least
MIN_SHARED shared words (one word is enough when the shorter title has only
one).  Pairs are taken best-first (a tie goes to more shared words), so on a day with two events (e.g. a quiz
and a DJ night) each HTML event takes the poster event it resembles most and
an unlike event stays unpaired (a duplicate is a smaller error than merging
two different events, data-model.md).

The HTML event wins (poster, detail, description) but keeps the poster
event's `id` and `first_seen` (it is not a new event) and gets the poster
source appended to `sources`.  Poster events of the previous run (by a
`poster` entry in `sources`) also count, so the id stays when the poster no
longer lists the event.
"""

import logging
import re
import unicodedata

log = logging.getLogger(__name__)

MIN_SCORE = 0.6
MIN_SHARED = 2
_STOP = {"a", "o", "s", "v", "z", "u", "k", "i", "ve", "na", "se", "by", "the", "and", "of",
         "for", "de", "la", "x", "vol"}


def words(title: str) -> set[str]:
    t = unicodedata.normalize("NFKD", str(title or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c)).replace("’", "'")
    t = re.sub(r"'s\b", "s", t)
    return {w for w in re.split(r"[^a-z0-9]+", t) if w and w not in _STOP}


def score(a: str, b: str) -> tuple[float, int]:
    wa, wb = words(a), words(b)
    if not wa or not wb:
        return 0.0, 0
    shared = len(wa & wb)
    return shared / min(len(wa), len(wb)), shared


def _is_poster(ev: dict) -> bool:
    return any((s or {}).get("type") == "poster" for s in ev.get("sources") or [])


def _paired(a: str, b: str) -> float | None:
    s, shared = score(a, b)
    need = 1 if min(len(words(a)), len(words(b))) == 1 else MIN_SHARED
    return s if s >= MIN_SCORE and shared >= need else None


def merge(events: list[dict], previous: dict | None = None) -> tuple[list[dict], dict]:
    previous = previous or {}
    stats = {"poster": 0, "html": 0, "replaced": 0}
    poster = [e for e in events if _is_poster(e) and len(e.get("sources") or []) == 1]
    stats["poster"] = len(poster)
    venues = {e["venue_id"] for e in poster} | {
        p["venue_id"] for p in previous.values() if _is_poster(p)}
    if not venues:
        return events, stats
    ids_now = {e["id"] for e in events}
    cands: dict[tuple, list[dict]] = {}
    for p in poster:
        cands.setdefault((p["venue_id"], p["date"]), []).append(p)
    for p in previous.values():
        if _is_poster(p) and p["venue_id"] in venues and p["id"] not in ids_now:
            cands.setdefault((p["venue_id"], p["date"]), []).append(p)
    html = [e for e in events if e["venue_id"] in venues and not _is_poster(e)]
    stats["html"] = len(html)
    pairs = []
    for h in html:
        for p in cands.get((h["venue_id"], h["date"]), []):
            s = _paired(h["title"], p["title"])
            if s is not None:
                pairs.append((s, score(h["title"], p["title"])[1], id(h), id(p), h, p))
    pairs.sort(key=lambda x: (-x[0], -x[1]))      # tie: more shared words first
    used_h, used_p, drop = set(), set(), set()
    for s, _, ih, ip, h, p in pairs:
        if ih in used_h or ip in used_p:
            continue
        used_h.add(ih)
        used_p.add(ip)
        log.info("poster event replaced by HTML: %s %r -> %r (%.2f)", h["date"], p["title"],
                 h["title"], s)
        poster_src = [x for x in p.get("sources") or [] if (x or {}).get("type") == "poster"]
        h["id"], h["first_seen"] = p["id"], p.get("first_seen") or h["first_seen"]
        h["sources"] = list(h.get("sources") or []) + poster_src[:1]
        drop.add(ip)
        stats["replaced"] += 1
    return [e for e in events if id(e) not in drop], stats
