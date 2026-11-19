"""
Daily run summary (task 057 part 1).

Every daily run writes one compact JSON with the numbers of the run to
data/cache/run_summaries/<YYYY-MM-DD>.json (Prague date; a second run on the
same day overwrites it).  The directory is kept between runs by the GitHub
Actions cache (daily.yml) and is read by the alerts (pipeline.alerts) and
the weekly report (pipeline.weekly_report).  Files older than KEEP_DAYS are
deleted.  Format: docs/data-model.md, section "Run summary".
"""

import datetime
import json
import logging
import os
import pathlib

log = logging.getLogger(__name__)

SUMMARY_DIR = pathlib.Path("data/cache/run_summaries")
KEEP_DAYS = 60
LOW_CONFIDENCE = 0.6           # classification.confidence below this = low (AI type)
MUSIC_FORMATS = {"concert", "dj", "party", "music"}
MISSING_FIELDS = ("image", "time", "price", "genre", "description")
UNVERIFIED_PRICE_DAYS = 14
APP_EVENT_URL = "https://matejstolarik.github.io/eventapp/#/akcia/"


def missing_fields(ev: dict) -> list[str]:
    """Fields the event lacks (genre only counts for music events)."""
    out = []
    if not ev.get("image_url"):
        out.append("image")
    if not ev.get("start_time"):
        out.append("time")
    if not ev.get("price_text") and not ev.get("price") and ev.get("free") is not True:
        out.append("price")
    if set(ev.get("formats") or []) & MUSIC_FORMATS and not ev.get("genres"):
        out.append("genre")
    if not ev.get("description"):
        out.append("description")
    return out


def _source_url(ev: dict) -> str | None:
    srcs = ev.get("sources") or []
    return srcs[0].get("url") if srcs else None


def _item(ev: dict, **extra) -> dict:
    d = {"id": ev["id"], "venue_id": ev["venue_id"], "title": ev.get("title"),
         "date": ev.get("date"), "source_url": _source_url(ev)}
    d.update(extra)
    return d


def _ai_nothing(ev: dict) -> bool:
    """AI searched but no value was applied (only the run record is left)."""
    enr = ev.get("enrichment") or {}
    run = enr.get("run") or {}
    return bool(run.get("searches")) and set(enr) <= {"run", "genre_candidates"}


def _low_confidence(ev: dict) -> bool:
    cls = ev.get("classification") or {}
    return cls.get("method") in ("llm", "llm+web") \
        and (cls.get("confidence") if cls.get("confidence") is not None else 1) < LOW_CONFIDENCE


def _dropped_by_id(dropped: list[str], prefix: str) -> dict[str, list[str]]:
    """'<id>: price '..': why' entries -> {id: [what, ...]} for one kind."""
    out: dict[str, list[str]] = {}
    for d in dropped or []:
        ev_id, _, what = d.partition(": ")
        if what.startswith(prefix):
            out.setdefault(ev_id, []).append(what[:160])
    return out


def build(events: list[dict], previous: dict, source_results: list[tuple], today: str,
          generated_at: str, ai_stats: dict | None = None, web_stats: dict | None = None,
          proposals: list | None = None, warnings: list[str] | None = None,
          simulate_zero: str | None = None) -> dict:
    """Summary dict of one run.  previous = {id: event} of the previous run.

    simulate_zero (env ALERT_SIMULATE_ZERO, test switch): the sources of this
    venue are recorded with 0 events and warning zero_events.  Only the
    summary changes, events.json is not touched."""
    web_stats = web_stats or {}
    ai_stats = ai_stats or {}
    today_d = datetime.date.fromisoformat(today)
    by_id = {e["id"]: e for e in events}

    venues: dict[str, dict] = {}

    def v(vid):
        return venues.setdefault(vid, {"events": 0, "new": 0, "gone": 0, "sources": [],
                                       "missing": {f: 0 for f in MISSING_FIELDS},
                                       "music_events": 0})

    for vid, label, count, warning in source_results:
        if simulate_zero and vid == simulate_zero:
            count, warning = 0, "zero_events"
        v(vid)["sources"].append({"label": label, "events": count, "warning": warning})

    new_ids, gone = [], []
    for e in events:
        d = v(e["venue_id"])
        d["events"] += 1
        if set(e.get("formats") or []) & MUSIC_FORMATS:
            d["music_events"] += 1
        for f in missing_fields(e):
            d["missing"][f] += 1
        if previous and e["id"] not in previous:
            d["new"] += 1
            new_ids.append(e["id"])
    for pid, pe in (previous or {}).items():
        if pid not in by_id and (pe.get("date") or "") >= today:
            v(pe["venue_id"])["gone"] += 1
            gone.append(pid)

    dropped = web_stats.get("dropped") or []
    prices_dropped = _dropped_by_id(dropped, "price '")
    genres_dropped = _dropped_by_id(dropped, "genre")
    type_changed = web_stats.get("type_changed_ids") or []

    review = []
    for e in events:
        if _ai_nothing(e):
            review.append(_item(e, kind="ai_nothing"))
        if _low_confidence(e):
            cls = e["classification"]
            review.append(_item(e, kind="low_confidence", primary_format=e.get("primary_format"),
                                confidence=cls.get("confidence")))
    for ev_id, whats in prices_dropped.items():
        if ev_id in by_id:
            review.append(_item(by_id[ev_id], kind="price_dropped", detail=whats[0]))
    for ev_id, whats in genres_dropped.items():
        if ev_id in by_id:
            review.append(_item(by_id[ev_id], kind="genres_dropped", detail="; ".join(whats)[:200]))
    for tc in type_changed:
        if tc.get("id") in by_id:
            review.append(_item(by_id[tc["id"]], kind="type_changed",
                                old=tc.get("old"), new=tc.get("new")))

    # artists of new concerts / DJ nights without a Spotify link (task 057 part 3.6)
    no_spotify = []
    for ev_id in new_ids:
        e = by_id[ev_id]
        if e.get("primary_format") not in ("concert", "dj") and not (
                e.get("primary_format") is None and set(e.get("formats") or []) & {"concert", "dj"}):
            continue
        linked = {(a.get("name") or "").lower() for a in e.get("artist_links") or []}
        main = [a for a in (e.get("artists") or [])[:2] if a.lower() not in linked]
        if main:
            no_spotify.append(_item(e, artists=main))

    horizon = (today_d + datetime.timedelta(days=UNVERIFIED_PRICE_DAYS)).isoformat()
    unverified = [_item(e, price_text=e.get("price_text"),
                        price_source=((e.get("enrichment") or {}).get("price_text") or {})
                        .get("source_url"))
                  for e in events
                  if ((e.get("enrichment") or {}).get("price_text") or {}).get("verified") is False
                  and today <= (e.get("date") or "") <= horizon]

    budget = web_stats.get("budget") or {}
    texts = [str(w) for w in (warnings or [])] + [str(w) for w in web_stats.get("warnings") or []]
    if ai_stats.get("reason"):
        texts.append(str(ai_stats["reason"]))
    try:
        from pipeline.deepseek import MONTH_BUDGET_USD
    except Exception:      # pragma: no cover
        MONTH_BUDGET_USD = None
    ai = {
        "provider": web_stats.get("provider"),
        "searches": web_stats.get("searches", 0),
        "month_searches": web_stats.get("month_searches"),
        "search_limit": web_stats.get("limit"),
        "cost_usd": round((web_stats.get("cost_usd") or 0)
                          + (ai_stats.get("estimated_cost_usd") or 0), 4),
        "month": budget.get("month"),
        "month_cost_usd": budget.get("month_spent_usd"),
        "month_budget_usd": MONTH_BUDGET_USD if budget else None,
        "type_changed": web_stats.get("type_changed", 0),
        "nothing_found": sum(1 for r in review if r["kind"] == "ai_nothing"),
        "prices_dropped": web_stats.get("prices_dropped", 0),
        "low_confidence": sum(1 for r in review if r["kind"] == "low_confidence"),
        "search_limit_reached": any("search limit" in t and "reached" in t for t in texts),
        "http_402": any("HTTP 402" in t for t in texts),
        "balance_usd": web_stats.get("balance_usd"),     # task 074; None = unknown
    }

    return {
        "date": today,
        "generated_at": generated_at,
        "success": True,
        "has_previous": bool(previous),
        "events": len(events),
        "new": len(new_ids),
        "gone": len(gone),
        "venues": dict(sorted(venues.items())),
        "ai": ai,
        "review": review,
        "no_spotify": no_spotify,
        "unverified_prices": unverified,
        "genre_proposals": [{"name": p.get("name"), "kind": p.get("kind"),
                             "count": p.get("count"),
                             "examples": [_item(by_id[i]) for i in (p.get("event_ids") or [])
                                          if i in by_id][:3]}
                            for p in proposals or []],
        "warnings": texts[:50],
    }


def save(summary: dict, directory: pathlib.Path = SUMMARY_DIR) -> pathlib.Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{summary['date']}.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    cutoff = (datetime.date.fromisoformat(summary["date"])
              - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    for p in directory.glob("*.json"):
        if p.stem < cutoff:
            p.unlink()
    return path


def load_all(directory: pathlib.Path = SUMMARY_DIR) -> list[dict]:
    """All stored summaries, oldest first (unreadable files are skipped)."""
    out = []
    for p in sorted(directory.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            log.warning("run summary %s unreadable: %s", p.name, exc)
    return out


def simulate_zero_venue() -> str | None:
    return (os.environ.get("ALERT_SIMULATE_ZERO") or "").strip() or None
