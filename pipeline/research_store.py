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
covers the 180-day enrichment window (task 085: 7 months, was 3 for the
60-day window); older months drop off.

Task 074: a weekly backup in the repo (data/research_backup/<YYYY-MM>.json,
same format, text and links only), written by weekly-report.yml:

    python -m pipeline.research_store backup

When Pages + cache give fewer records than the backup, `load` merges the
backup too and logs a warning.
"""

import datetime
import json
import logging
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

from pipeline.fetch import USER_AGENT

log = logging.getLogger(__name__)

RESEARCH_DIR = pathlib.Path("site/research")
BACKUP_DIR = pathlib.Path("data/research_backup")      # task 074
KEEP_MONTHS = 7      # task 085: 180-day AI window (was 3)


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


def _fetch_month(base: str, m: str) -> tuple[dict | None, str | None]:
    """Published month file -> (data, error); a 404 is (None, None)."""
    last = None
    for attempt in range(3):                   # task 065: Pages answered 503 / 404
        try:
            req = urllib.request.Request(base + f"{m}.json", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read()), None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None, None
            last = f"HTTP {exc.code}"
        except (OSError, ValueError) as exc:
            last = str(exc)[:120]
        time.sleep(2 * (attempt + 1))
    return None, last


def _merge(store: dict, data: dict | None) -> int:
    """Add records; for the same id the later `processed` wins (equal: the
    later source).  Returns the number of records read."""
    recs = (data or {}).get("events", [])
    for rec in recs:
        old = store.get(rec["id"])
        if old is None or (rec.get("processed") or "") >= (old.get("processed") or ""):
            store[rec["id"]] = rec
    return len(recs)


def load(today: str) -> dict:
    """id -> record, merged from (task 065) a one-off seed file
    (RESEARCH_SEED, comma-separated paths), the local month files
    (site/research, kept between CI runs by actions/cache) and the published
    (Pages) month files.  Before task 065 only Pages was read in CI: when it
    answered with an error / 404 the store was empty and the run published
    an almost empty file (run 44198194551: 243 -> 1 record)."""
    store: dict = {}
    for path in [x.strip() for x in os.environ.get("RESEARCH_SEED", "").split(",") if x.strip()]:
        try:
            n = _merge(store, json.loads(pathlib.Path(path).read_text(encoding="utf-8")))
            log.info("research seed %s: %d records", path, n)
        except (OSError, ValueError) as exc:
            log.warning("research seed %s not readable (%s)", path, exc)
    base = _base_url()
    for m in reversed(months(today)):          # newer months override older ones
        local_n = 0
        f = RESEARCH_DIR / f"{m}.json"
        if f.exists():
            try:
                local_n = _merge(store, json.loads(f.read_text(encoding="utf-8")))
            except (OSError, ValueError) as exc:
                log.warning("research %s: local file not readable (%s)", m, exc)
        if not base:
            continue
        data, err = _fetch_month(base, m)
        pages_n = _merge(store, data)
        if err:
            log.warning("research %s not available from Pages (%s); local copy: %d records",
                        m, err, local_n)
        elif pages_n < local_n:
            log.warning("research %s: Pages has %d records, local copy %d (merged)",
                        m, pages_n, local_n)
    backup = _read_dir(BACKUP_DIR, today)
    if len(backup) > len(store):        # task 074: Pages + cache lost records
        log.warning("research store: Pages + cache gave %d records, repo backup has %d;"
                    " backup merged", len(store), len(backup))
        for rec in backup.values():
            _merge(store, {"events": [rec]})
    log.info("research store: %d records loaded", len(store))
    return store


def _read_dir(directory: pathlib.Path, today: str) -> dict:
    """id -> record from <directory>/<YYYY-MM>.json of the kept months."""
    store: dict = {}
    for m in reversed(months(today)):
        f = directory / f"{m}.json"
        if f.exists():
            try:
                _merge(store, json.loads(f.read_text(encoding="utf-8")))
            except (OSError, ValueError) as exc:
                log.warning("research %s: %s not readable (%s)", m, f, exc)
    return store


def save(store: dict, today: str, directory: pathlib.Path | None = None) -> dict:
    """Write <directory>/<YYYY-MM>.json (default site/research); returns
    {month: bytes}."""
    directory = directory or RESEARCH_DIR
    keep = set(months(today))
    by_month: dict = {}
    for rec in store.values():
        m = (rec.get("processed") or today)[:7]
        if m in keep:
            by_month.setdefault(m, []).append(rec)
    directory.mkdir(parents=True, exist_ok=True)
    sizes = {}
    for m, recs in sorted(by_month.items()):
        recs.sort(key=lambda r: r["id"])
        text = json.dumps({"month": m, "events": recs}, ensure_ascii=False, indent=1)
        (directory / f"{m}.json").write_text(text, encoding="utf-8")
        sizes[m] = len(text.encode("utf-8"))
    return sizes


def backup(today: str, directory: pathlib.Path | None = None) -> int:
    """Task 074: write the stored research (Pages + cache + current backup)
    into the repo backup; month files no longer kept are removed.  Only the
    research records (text and links), nothing else.  Returns the number of
    records."""
    directory = directory or BACKUP_DIR
    store = load(today)
    save(store, today, directory)
    keep = {f"{m}.json" for m in months(today)}
    for f in directory.glob("*.json"):
        if f.name not in keep:
            f.unlink()
    n = sum(1 for r in store.values() if (r.get("processed") or today)[:7] in set(months(today)))
    log.info("research backup: %d records in %s", n, directory)
    return n


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if sys.argv[1:] != ["backup"]:
        sys.exit("usage: python -m pipeline.research_store backup")
    from zoneinfo import ZoneInfo
    backup(datetime.datetime.now(ZoneInfo("Europe/Prague")).date().isoformat())
