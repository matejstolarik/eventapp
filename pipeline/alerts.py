"""
Immediate alerts as GitHub issues with the label `alert` (task 057 part 2).

Raised only for:
  - a failed daily run or app deploy (key  workflow:<name>),
  - a source with 0 events, or with fewer than DROP_RATIO x the median of
    its last MEDIAN_RUNS runs (key  source:<venue>/<label>),
  - the monthly AI limit used up: search limit, month budget, HTTP 402
    (key  ai:limit).
One open issue per key: while it is open, a repeated problem adds a comment;
when the problem is gone, the run closes the issue with a comment.
Rules and ignore list: docs/report-rules.md, data/report_ignore.json.

    python -m pipeline.alerts --workflow daily --job-status success
    python -m pipeline.alerts --workflow deploy-app --job-status failure
    python -m pipeline.alerts ... --dry-run      (print, no GitHub calls)
"""

import argparse
import datetime
import json
import os
import pathlib
import re
import statistics
import sys
from zoneinfo import ZoneInfo

from pipeline import run_summary

PRAGUE_TZ = ZoneInfo("Europe/Prague")
LABEL = "alert"
MEDIAN_RUNS = 7
DROP_RATIO = 0.5
BUDGET_EPS_USD = 0.005
IGNORE_PATH = pathlib.Path("data/report_ignore.json")
MARKER = re.compile(r"<!-- alert-key: (.+?) -->")
WORKFLOW_NAMES = {"daily": "Denný beh pipeline", "deploy-app": "Nasadenie appky"}


def load_ignore(path: pathlib.Path = IGNORE_PATH) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    items = data.get("ignore", []) if isinstance(data, dict) else data
    return {(i.get("id") if isinstance(i, dict) else i) for i in items}


def _alert(key: str, title: str, body: str) -> dict:
    return {"key": key, "title": title, "body": body}


def source_alerts(latest: dict, history: list[dict], ignore: set[str]) -> list[dict]:
    """0 events, or a drop > 50 % against the median of the last 7 runs."""
    past: dict[str, list[int]] = {}
    for s in [h for h in history if h.get("venues")][-MEDIAN_RUNS:]:
        for vid, v in s["venues"].items():
            for src in v.get("sources") or []:
                past.setdefault(f"{vid}/{src['label']}", []).append(src["events"])
    out = []
    for vid, v in (latest.get("venues") or {}).items():
        if f"{vid}:source" in ignore:
            continue
        for src in v.get("sources") or []:
            key = f"{vid}/{src['label']}"
            if key in ignore or f"source:{key}" in ignore:
                continue
            n, hist = src["events"], past.get(key, [])
            med = statistics.median(hist) if hist else None
            med_txt = f"medián posledných {len(hist)} behov: {med:g}" if hist else "bez histórie"
            if n == 0:
                why = "chyba zdroja" if src.get("warning") == "error" else "0 akcií"
                out.append(_alert(f"source:{key}", f"⚠ Zdroj {key}: {why}",
                                  f"Zdroj `{key}` vrátil v behu {latest['date']} **0 akcií**"
                                  f" ({why}; {med_txt}). Pravdepodobne sa zmenil web alebo"
                                  " zdroj nefunguje."))
            elif med and n < DROP_RATIO * med:
                out.append(_alert(f"source:{key}", f"⚠ Zdroj {key}: pokles na {n} akcií",
                                  f"Zdroj `{key}` vrátil v behu {latest['date']} **{n} akcií**,"
                                  f" {med_txt} (pokles o viac ako"
                                  f" {round((1 - DROP_RATIO) * 100)} %)."))
    return out


def ai_alerts(latest: dict) -> list[dict]:
    ai = latest.get("ai") or {}
    reasons = []
    if ai.get("http_402"):
        reasons.append("AI vrátila HTTP 402 (minutý kredit)")
    if ai.get("search_limit_reached"):
        reasons.append(f"minutý mesačný limit hľadaní ({ai.get('month_searches')}"
                       f" / {ai.get('search_limit')})")
    if ai.get("month_budget_usd") and ai.get("month_cost_usd") is not None \
            and ai["month_cost_usd"] >= ai["month_budget_usd"] - BUDGET_EPS_USD:
        reasons.append(f"minutý mesačný rozpočet AI (${ai['month_cost_usd']:.2f}"
                       f" / ${ai['month_budget_usd']:.2f})")
    if not reasons:
        return []
    return [_alert("ai:limit", "⚠ AI: minutý mesačný limit",
                   f"Beh {latest['date']}: " + "; ".join(reasons)
                   + ". AI doplnenie sa zastavilo, beh pokračuje bez neho.")]


def workflow_alert(workflow: str, run_url: str | None) -> dict:
    name = WORKFLOW_NAMES.get(workflow, workflow)
    link = f" Beh: {run_url}" if run_url else ""
    return _alert(f"workflow:{workflow}", f"⚠ {name} zlyhal",
                  f"{name} (`{workflow}`) zlyhal.{link}")


def compute(workflow: str, job_status: str, latest: dict | None, history: list[dict],
            ignore: set[str], run_url: str | None = None) -> tuple[list[dict], set[str]]:
    """-> (active alerts, prefixes of keys this run is allowed to close).

    latest = summary written by this run (None if the pipeline did not get
    that far); history = earlier summaries, oldest first."""
    alerts, scope = [], set()
    if job_status != "success":
        alerts.append(workflow_alert(workflow, run_url))
    else:
        scope.add(f"workflow:{workflow}")
    if workflow == "daily" and latest and latest.get("venues"):
        alerts += source_alerts(latest, history, ignore)
        alerts += ai_alerts(latest)
        scope |= {"source:", "ai:"}
    return alerts, scope


def _today() -> str:
    return datetime.datetime.now(PRAGUE_TZ).date().isoformat()


def _this_run_summary(summaries: list[dict], today: str) -> dict | None:
    """The newest summary if it is from today and less than 6 hours old."""
    if not summaries or summaries[-1].get("date") != today:
        return None
    try:
        gen = datetime.datetime.fromisoformat(summaries[-1]["generated_at"])
    except (KeyError, ValueError):
        return None
    age = datetime.datetime.now(PRAGUE_TZ) - gen
    return summaries[-1] if age < datetime.timedelta(hours=6) else None


def record_status(workflow: str, job_status: str, latest: dict | None, today: str,
                  directory: pathlib.Path = run_summary.SUMMARY_DIR) -> None:
    """Daily run: write the job result into today's summary (a minimal one if
    the pipeline did not write it)."""
    if workflow != "daily":
        return
    if latest is None and (directory / f"{today}.json").exists():
        return          # keep the numbers of an earlier run of the same day
    s = latest or {"date": today, "generated_at": datetime.datetime.now(PRAGUE_TZ).isoformat()}
    s["success"] = job_status == "success"
    run_summary.save(s, directory)


def sync(alerts: list[dict], scope: set[str], issues, date: str) -> list[str]:
    """Open / comment / close GitHub issues.  Returns a log of actions."""
    done = []
    open_by_key = {}
    for i in issues.open_issues(LABEL):
        m = MARKER.search(i.get("body") or "")
        if m:
            open_by_key[m.group(1)] = i
    active = {a["key"] for a in alerts}
    for a in alerts:
        if a["key"] in open_by_key:
            issues.comment(open_by_key[a["key"]]["number"], f"Stále trvá ({date}): {a['body']}")
            done.append(f"comment #{open_by_key[a['key']]['number']} {a['key']}")
        else:
            i = issues.create(a["title"], f"{a['body']}\n\n<!-- alert-key: {a['key']} -->", LABEL)
            done.append(f"open #{i['number']} {a['key']}")
    for key, i in open_by_key.items():
        if key not in active and any(key.startswith(p) for p in scope):
            issues.close(i["number"], f"Vyriešené ({date}): problém sa v tomto behu neopakoval.")
            done.append(f"close #{i['number']} {key}")
    return done


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--job-status", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    today = _today()
    summaries = run_summary.load_all()
    latest = _this_run_summary(summaries, today) if args.workflow == "daily" else None
    history = [s for s in summaries if s is not latest]
    run_url = None
    if os.environ.get("GITHUB_RUN_ID"):
        run_url = (f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/"
                   f"{os.environ.get('GITHUB_REPOSITORY')}/actions/runs/"
                   f"{os.environ['GITHUB_RUN_ID']}")
    alerts, scope = compute(args.workflow, args.job_status, latest, history, load_ignore(),
                            run_url)
    record_status(args.workflow, args.job_status, latest, today)
    for a in alerts:
        print(f"ALERT {a['key']}: {a['title']}")
    if args.dry_run:
        return 0
    from pipeline.github_issues import Issues
    for line in sync(alerts, scope, Issues(), today):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
