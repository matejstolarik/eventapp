"""
Stored AI research (task 059 part 3).

For every event processed by the Gemini two-step enrichment the step-1
research is kept: search queries, resolved sources, the fact lines, kworb
Spotify checks, and from step 2 the genre facts and type reason.  Files are
published next to events.json as site/research/<YYYY-MM>.json (month of
processing), NOT in events.json, and are not used by the app.

When the rules change, step 2 can be re-run from these facts without a new
search (ENRICH_FROM_RESEARCH = "all" or comma-separated event ids).

Pages are rebuilt on every run, so each run loads the files of the last
KEEP_MONTHS months from the published site and writes them back.  This
covers the 60-day enrichment window; older months drop off.
"""

import datetime
import json
import logging
import os
import pathlib
import urllib.error
import urllib.request

from pipeline.fetch import USER_AGENT

log = logging.getLogger(__name__)

RESEARCH_DIR = pathlib.Path("site/research")
KEEP_MONTHS = 3


def months(today: str, n: int = KEEP_MONTHS) -> list[str]:
    d = datetime.date.fromisoformat(today).replace(day=1)
    out = []
    for _ in range(n):
        out.append(d.isoformat()[:7])
        d = (d - datetime.timedelta(days=1)).replace(day=1)
    return out


def record_from(ev: dict, rec: dict, res: dict, conf: dict, today: str) -> dict:
    r = rec["research"]
    return {
        "id": ev["id"], "title": ev.get("title"), "event_date": ev.get("date"),
        "processed": today,
        "research_model": r.get("model"), "research_thinking": r.get("thinking"),
        "decide_model": conf.get("decide_model"), "decide_thinking": conf.get("decide_thinking"),
        "searched": r.get("searched"), "queries": r.get("queries") or [],
        "sources": r.get("sources") or [], "facts": r.get("text") or "",
        "kworb": res.get("kworb") or r.get("kworb") or [],
        "primary_format": res.get("primary_format"), "type_reason": res.get("type_reason"),
        "genres": res.get("genres") or [], "genre_facts": res.get("genre_facts") or {},
    }


def to_research(record: dict) -> dict:
    """Stored record -> the research dict used by _Gemini2.run_from_research."""
    return {"text": record.get("facts") or "", "queries": record.get("queries") or [],
            "sources": record.get("sources") or [], "searched": bool(record.get("searched")),
            "kworb": [{k: v for k, v in x.items() if k != "status"}
                      for x in record.get("kworb") or []],
            "usage": [], "retried": False, "model": record.get("research_model"),
            "thinking": record.get("research_thinking")}


def _base_url() -> str | None:
    url = os.environ.get("PREVIOUS_EVENTS_URL")
    return url.rsplit("/", 1)[0] + "/research/" if url else None


def load(today: str) -> dict:
    """id -> record from the published (CI) or local (dev) month files."""
    store: dict = {}
    base = _base_url()
    for m in reversed(months(today)):          # newer months override older ones
        data = None
        try:
            if base:
                req = urllib.request.Request(base + f"{m}.json", headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
            elif (RESEARCH_DIR / f"{m}.json").exists():
                data = json.loads((RESEARCH_DIR / f"{m}.json").read_text(encoding="utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                log.warning("research %s not available (%s)", m, exc)
        except (OSError, ValueError) as exc:
            log.warning("research %s not available (%s)", m, exc)
        for rec in (data or {}).get("events", []):
            store[rec["id"]] = rec
    log.info("research store: %d records loaded", len(store))
    return store


def save(store: dict, today: str) -> dict:
    """Write site/research/<YYYY-MM>.json; returns {month: bytes}."""
    keep = set(months(today))
    by_month: dict = {}
    for rec in store.values():
        m = (rec.get("processed") or today)[:7]
        if m in keep:
            by_month.setdefault(m, []).append(rec)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for m, recs in sorted(by_month.items()):
        recs.sort(key=lambda r: r["id"])
        text = json.dumps({"month": m, "events": recs}, ensure_ascii=False, indent=1)
        (RESEARCH_DIR / f"{m}.json").write_text(text, encoding="utf-8")
        sizes[m] = len(text.encode("utf-8"))
    return sizes
