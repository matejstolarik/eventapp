"""
Weekly pipeline report as a GitHub issue with the label `weekly-report`
(task 057 part 3).  Reads the run summaries of the last 7 days (and the week
before for trends); one phone screen, in Slovak; every item has a short ID
(W47-03) so Matej can refer to it.  Closes the previous weekly issue.
Rules: docs/report-rules.md; ignored items: data/report_ignore.json.

    python -m pipeline.weekly_report            (create the issue)
    python -m pipeline.weekly_report --dry-run  (print the Markdown)
"""

import argparse
import datetime
import statistics
import sys
from zoneinfo import ZoneInfo

from pipeline import run_summary
from pipeline.alerts import load_ignore

PRAGUE_TZ = ZoneInfo("Europe/Prague")
LABEL = "weekly-report"
APP = run_summary.APP_EVENT_URL

# thresholds (documented in docs/report-rules.md)
MISSING_RATE = 0.30          # report a field missing at more than 30 % of a venue's events
MISSING_WORSE = 0.15         # ... or 15 points worse than the venue's usual rate
MISSING_MIN_EVENTS = 3       # venues with fewer events (of the kind) are not judged
MISSING_SHOWN = 8            # lines shown, the rest folded
REVIEW_SHOWN = 10
PROPOSAL_MIN = 3
STATUS_SHOWN = 3

FIELD_SK = {"image": "obrázok", "time": "čas", "price": "cena", "genre": "žáner (hudba)",
            "description": "popis"}
KIND_SK = {"price_dropped": "zahodená cena", "type_changed": "AI zmenila typ",
           "low_confidence": "nízka istota typu", "ai_nothing": "AI nič nenašla",
           "genres_dropped": "zahodené žánre"}
REVIEW_ORDER = ["price_dropped", "type_changed", "low_confidence", "ai_nothing"]


class _Ids:
    def __init__(self, week: str):
        self.week, self.n = week, 0

    def next(self) -> str:
        self.n += 1
        return f"{self.week}-{self.n:02d}"


def _d(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)


def _pct(x: float) -> str:
    return f"{round(x * 100)} %"


def _ev_line(it: dict) -> str:
    title = (it.get("title") or it["id"]).replace("|", "/").replace("[", "(").replace("]", ")")
    src = f" · [zdroj]({it['source_url']})" if it.get("source_url") else ""
    return f"[{title[:60]}]({APP}{it['id']}) · {it['venue_id']} · {it.get('date', '')}{src}"


def _rate(v: dict, field: str) -> tuple[float, int] | None:
    base = v.get("music_events", 0) if field == "genre" else v.get("events", 0)
    if base < MISSING_MIN_EVENTS:
        return None
    return v["missing"].get(field, 0) / base, base


def missing_items(latest: dict, older: list[dict], ignore: set[str]) -> list[dict]:
    """venue:field pairs > MISSING_RATE missing or MISSING_WORSE above usual."""
    out = []
    for vid, v in (latest.get("venues") or {}).items():
        for f in run_summary.MISSING_FIELDS:
            if f"{vid}:{f}" in ignore:
                continue
            r = _rate(v, f)
            if r is None:
                continue
            rate, base = r
            usual_rates = [x[0] for s in older
                           if (x := _rate((s.get("venues") or {}).get(vid) or {"events": 0},
                                          f)) is not None] if older else []
            usual = statistics.median(usual_rates) if usual_rates else None
            worse = usual is not None and rate - usual >= MISSING_WORSE
            if rate > MISSING_RATE or worse:
                out.append({"key": f"{vid}:{f}", "rate": rate, "usual": usual, "base": base,
                            "missing": v["missing"].get(f, 0), "worse": worse})
    # worse than usual first, then by rate
    return sorted(out, key=lambda x: (not x["worse"], -x["rate"], x["key"]))


def _union(week: list[dict], field: str, today: str, ignore: set[str]) -> list[dict]:
    """Items of one list over the week, newest first, unique by (id, kind),
    only events from today on, ignored ids left out."""
    seen, out = set(), []
    for s in reversed(week):
        for it in s.get(field) or []:
            k = (it["id"], it.get("kind"))
            if k in seen or it["id"] in ignore or (it.get("date") or "") < today:
                continue
            seen.add(k)
            out.append(it)
    return out


def build(summaries: list[dict], today: str, ignore: set[str] | None = None) -> tuple[str, str]:
    """-> (title, Markdown body)."""
    ignore = ignore or set()
    t = _d(today)
    iso = t.isocalendar()
    week_id = f"W{iso.week:02d}"
    ids = _Ids(week_id)
    start = (t - datetime.timedelta(days=6)).isoformat()
    prev_start = (t - datetime.timedelta(days=13)).isoformat()
    week = [s for s in summaries if start <= s.get("date", "") <= today]
    prev = [s for s in summaries if prev_start <= s.get("date", "") < start and s.get("venues")]
    older = [s for s in summaries if s.get("date", "") < start and s.get("venues")]
    ok = [s for s in week if s.get("venues")]
    latest = ok[-1] if ok else {}
    prev_last = prev[-1] if prev else {}

    title = f"Týždenný report {week_id} · {today}"
    lines = [f"## Týždenný report {week_id} ({_d(start).day}. {_d(start).month}. –"
             f" {t.day}. {t.month}. {t.year})", ""]

    # ---- 1. status ---------------------------------------------------------
    problems = []
    failed = [s["date"] for s in week if s.get("success") is False]
    if failed:
        problems.append(f"Denný beh zlyhal {len(failed)}× ({', '.join(failed)}).")
    missing_days = 7 - len({s["date"] for s in week})
    if missing_days > 0:
        problems.append(f"Chýbajú čísla z {missing_days} dní (beh neprebehol alebo"
                        " sa nezapísal).")
    for vid, v in (latest.get("venues") or {}).items():
        for src in v.get("sources") or []:
            if src["events"] == 0 and f"{vid}:source" not in ignore:
                problems.append(f"Zdroj `{vid}/{src['label']}` dal v poslednom behu 0 akcií.")
    ai = latest.get("ai") or {}
    if any((s.get("ai") or {}).get(k) for s in ok for k in ("http_402", "search_limit_reached")):
        problems.append("AI narazila na mesačný limit / HTTP 402.")
    miss = missing_items(latest, older, ignore) if latest else []
    for m in [m for m in miss if m["worse"]][:2]:
        vid, f = m["key"].split(":")
        problems.append(f"`{vid}`: {FIELD_SK[f]} chýba pri {_pct(m['rate'])} akcií"
                        f" (bežne {_pct(m['usual'])}).")
    lines.append("### 1. Stav")
    if problems:
        for p in problems[:STATUS_SHOWN]:
            lines.append(f"- **{ids.next()}** {p}")
        if len(problems) > STATUS_SHOWN:
            lines.append(f"- … a ďalšie ({len(problems) - STATUS_SHOWN}), pozri nižšie.")
    else:
        lines.append("✅ Všetko v poriadku")
    lines.append("")

    # ---- 2. venues ---------------------------------------------------------
    lines += ["### 2. Podniky", "", "| Podnik | Akcie | Nové | Trend | Varovania |",
              "|---|--:|--:|--:|---|"]
    for vid, v in (latest.get("venues") or {}).items():
        new = sum(((s.get("venues") or {}).get(vid) or {}).get("new", 0) for s in ok)
        before = ((prev_last.get("venues") or {}).get(vid) or {}).get("events")
        trend = "–" if before is None else f"{v['events'] - before:+d}"
        warn_days = sum(1 for s in ok for src in ((s.get("venues") or {}).get(vid) or {})
                        .get("sources", []) if src.get("warning"))
        warn = f"{warn_days}× zdroj" if warn_days else ""
        lines.append(f"| {vid} | {v['events']} | {new} | {trend} | {warn} |")
    total_before = prev_last.get("events")
    total_trend = "–" if total_before is None else f"{latest.get('events', 0) - total_before:+d}"
    lines += [f"| **spolu** | **{latest.get('events', 0)}** |"
              f" **{sum(s.get('new', 0) for s in ok)}** | {total_trend} | |", ""]

    # ---- 3. missing data ---------------------------------------------------
    if miss:
        lines += ["### 3. Chýbajúce údaje", ""]
        def mline(m):
            vid, f = m["key"].split(":")
            usual = f", bežne {_pct(m['usual'])}" if m["usual"] is not None else ""
            return (f"- **{ids.next()}** `{m['key']}` {FIELD_SK[f]} chýba {_pct(m['rate'])}"
                    f" ({m['missing']}/{m['base']}{usual})")
        lines += [mline(m) for m in miss[:MISSING_SHOWN]]
        if len(miss) > MISSING_SHOWN:
            lines += ["", f"<details><summary>ďalšie ({len(miss) - MISSING_SHOWN})</summary>",
                      ""] + [mline(m) for m in miss[MISSING_SHOWN:]] + ["", "</details>"]
        lines.append("")

    # ---- 4. to review --------------------------------------------------------
    review = _union(ok, "review", today, ignore)
    top = sorted([r for r in review if r["kind"] in REVIEW_ORDER],
                 key=lambda r: (REVIEW_ORDER.index(r["kind"]), r.get("date", "")))
    if top:
        lines += ["### 4. Na kontrolu", ""]
        for r in top[:REVIEW_SHOWN]:
            lines.append(f"- **{ids.next()}** {KIND_SK[r['kind']]}{_review_detail(r)}:"
                         f" {_ev_line(r)}")
        if len(top) > REVIEW_SHOWN:
            lines.append(f"- … ďalších {len(top) - REVIEW_SHOWN} v časti 6.")
        lines.append("")

    # ---- 5. genre proposals -----------------------------------------------
    props = [p for p in latest.get("genre_proposals") or []
             if (p.get("count") or 0) >= PROPOSAL_MIN and f"genre:{p.get('name')}" not in ignore]
    if props:
        lines += ["### 5. Návrhy nových žánrov", "",
                  "_Odpovedz: schváliť / zlúčiť s X / zamietnuť._", ""]
        for p in props:
            ex = ", ".join(f"[{(e.get('title') or e['id'])[:40]}]({APP}{e['id']})"
                           for e in p.get("examples") or [])
            lines.append(f"- **{ids.next()}** **{p['name']}** ({p.get('kind')}, {p['count']}"
                         f" akcií): {ex}")
        lines.append("")

    # ---- 6. for the main chat (folded) ---------------------------------------
    nosp = _union(ok, "no_spotify", today, ignore)
    unver = [u for u in latest.get("unverified_prices") or [] if u["id"] not in ignore]
    lines += ["### 6. Na doplnenie v chate", "",
              f"<details><summary>Spotify {len(nosp)} · neoverené ceny {len(unver)} ·"
              f" na kontrolu {len(review)}</summary>", ""]
    if nosp:
        lines += ["**Interpreti bez Spotify (nové koncerty / DJ noci):**", ""]
        lines += [f"- **{ids.next()}** {', '.join(n['artists'])} — {_ev_line(n)}" for n in nosp]
        lines.append("")
    if unver:
        lines += ["**Ceny `verified: false` v najbližších 14 dňoch:**", ""]
        lines += [f"- **{ids.next()}** {u.get('price_text')} — {_ev_line(u)}"
                  + (f" · [cena]({u['price_source']})" if u.get("price_source") else "")
                  for u in unver]
        lines.append("")
    if review:
        lines += ["**Na kontrolu (všetko):**", ""]
        lines += [f"- **{ids.next()}** {KIND_SK.get(r['kind'], r['kind'])}{_review_detail(r)}:"
                  f" {_ev_line(r)}" for r in review]
        lines.append("")
    if not (nosp or unver or review):
        lines += ["Nič.", ""]
    # ---- 7. AI ---------------------------------
    week_searches = sum((s.get("ai") or {}).get("searches") or 0 for s in ok)
    week_cost = sum((s.get("ai") or {}).get("cost_usd") or 0 for s in ok)
    month = []
    if ai.get("month_cost_usd") is not None:
        month.append(f"${ai['month_cost_usd']:.2f} / ${ai.get('month_budget_usd') or 0:.2f}")
    if ai.get("month_searches") is not None:
        month.append(f"{ai['month_searches']} / {ai.get('search_limit')} hľadaní")
    ai_lines = ["### 7. AI", "",
              f"- Týždeň: {week_searches} hľadaní, ${week_cost:.2f}",
              f"- Mesiac {ai.get('month') or ''}: " + (", ".join(month) or "–"), ""]

    lines += ["</details>", ""] + ai_lines + [
              f"_Pravidlá: `docs/report-rules.md`, ignorované: `data/report_ignore.json`."
              f" Behov v týždni: {len(ok)}._"]
    return title, "\n".join(lines) + "\n"


def _review_detail(r: dict) -> str:
    if r["kind"] == "type_changed":
        return f" ({'/'.join(r.get('old') or []) or '–'} → {'/'.join(r.get('new') or [])})"
    if r["kind"] == "low_confidence":
        return f" ({r.get('primary_format') or '–'} {r.get('confidence')})"
    if r.get("detail"):
        return f" ({r['detail'][:80]})"
    return ""


def publish(title: str, body: str, issues) -> str:
    old = issues.open_issues(LABEL)
    new = issues.create(title, body, LABEL)
    for i in old:
        issues.close(i["number"], f"Nahradené novým reportom #{new['number']}.")
    return new["html_url"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    today = datetime.datetime.now(PRAGUE_TZ).date().isoformat()
    title, body = build(run_summary.load_all(), today, load_ignore())
    if args.dry_run:
        print(title)
        print(body)
        return 0
    from pipeline.github_issues import Issues
    print(publish(title, body, Issues()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
