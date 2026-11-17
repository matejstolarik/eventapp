"""
Task 061: test of the DeepSeek provider (variant A) on Matej's 50 labelled
events (docs/tasks/056/labels-matej.csv, the same events as 058 / 059).
Manual only (workflow .github/workflows/deepseek-test.yml, key from the
secret DEEPSEEK_API_KEY).  Does NOT touch events.json or the daily run.

    python -m pipeline.deepseek_test run            # TEST_OUT/deepseek_test.json + research/
    python -m pipeline.deepseek_test summary IN     # numbers for the report
    python -m pipeline.deepseek_test xlsx IN OUT    # Excel: Matej label, Gemini D (059), DeepSeek A

TEST_IDS=id1,id2 limits the run (smoke test of 3 events before the full run).
"""

import concurrent.futures
import datetime
import json
import logging
import os
import pathlib
import sys

from pipeline import research_store
from pipeline.deepseek import MODEL, Budget, _DeepSeek
from pipeline.enrich_ai import ProviderStop, process_result
from pipeline.gemini_test import (EVENTS_URL, _app_price, _get_json, _memo_fetch, _page_texts,
                                  _type_str, load_labels, unsupported_genres)
from pipeline.price import parse_price

log = logging.getLogger("pipeline.deepseek_test")
GEMINI_D = pathlib.Path("docs/tasks/059/tune.json")


def cmd_run(out: pathlib.Path) -> None:
    labels = load_labels()
    data = _get_json(EVENTS_URL)
    by_id = {e["id"]: e for e in data["events"]}
    venues = {v["id"]: v for v in data["venues"]}
    ids = list(labels)
    if os.environ.get("TEST_IDS", "").strip():
        ids = [i.strip() for i in os.environ["TEST_IDS"].split(",") if i.strip()]
    missing = [i for i in ids if i not in by_id]
    events = [by_id[i] for i in ids if i in by_id]
    budget = Budget()
    prov = _DeepSeek(budget=budget)
    log.info("deepseek test: %d events, budget $%s, missing %s", len(events), budget.limit, missing)
    pages = _page_texts(events)
    today = datetime.date.today().isoformat()
    stopped = []

    def one(ev):
        if stopped:
            return ev["id"], None, "stopped: " + stopped[0]
        try:
            return ev["id"], prov.run_event(ev, venues.get(ev["venue_id"], {}),
                                            pages.get(ev["id"])), None
        except ProviderStop as exc:
            stopped.append(str(exc))
            return ev["id"], None, f"ProviderStop: {exc}"[:300]
        except Exception as exc:
            return ev["id"], None, f"{exc.__class__.__name__}: {exc}"[:300]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        raw = list(pool.map(one, events))

    fetch = _memo_fetch()
    store, results = {}, {}
    for (i, rec, err), ev in zip(raw, events):
        item = {"venue_id": ev["venue_id"], "title": ev["title"], "date": ev["date"],
                "url": next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None),
                "venue_price_text": ev.get("price_text")
                if "price_text" not in (ev.get("enrichment") or {}) else None}
        if err:
            item["error"] = err
            results[i] = item
            continue
        res, _ = process_result(ev, rec, MODEL, today, {}, fetch)        # sequential GETs
        r = rec["research"]
        item.update({
            "research": {k: r[k] for k in ("text", "queries", "fetched", "sources", "searched",
                                           "retried", "tool_errors", "dropped_results")},
            "steps": rec["steps"], "raw": rec["raw"],
            "result": res, "price_text": res["price"] if res.get("price_ok") else None,
            "searches": rec["searches"], "fetches": rec["fetches"],
            "cost_usd": rec["cost_usd"],
            "cost_peak_usd": sum(u["cost_peak_usd"] for u in rec["steps"]),
            "cost_offpeak_usd": sum(u["cost_offpeak_usd"] for u in rec["steps"]),
        })
        results[i] = item
        store[i] = research_store.record_from(ev, rec, res, prov.conf, today)
    out.mkdir(parents=True, exist_ok=True)
    research_store.RESEARCH_DIR = out / "research"
    research_store.save(store, today)
    doc = {"date": today, "model": MODEL, "label": prov.label, "events_url": EVENTS_URL,
           "generated_at": data.get("generated_at"), "missing": missing,
           "spent_usd": round(budget.spent, 4), "stopped": stopped[:1], "events": results}
    (out / "deepseek_test.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    s = summary(doc)
    log.info("deepseek test done: %s", s)
    text = "\n".join(f"- {k}: {v}" for k, v in s.items())
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"## DeepSeek test ({prov.label})\n\n{text}\n")


def summary(doc: dict) -> dict:
    labels = load_labels()
    ev = doc["events"]
    ok = [i for i, v in ev.items() if "error" not in v]
    n = max(len(ok), 1)
    s = {"events": len(ev), "errors": len(ev) - len(ok)}
    lab = [i for i in ok if i in labels]
    s["type_ok"] = f"{sum(ev[i]['result'].get('primary_format') == labels[i]['expected_primary'] for i in lab)}/{len(lab)}"
    no_fact = check = 0
    for i in ok:
        a, b = unsupported_genres(ev[i]["result"], ev[i]["research"]["text"])
        no_fact += len(a)
        check += len(b)
    s["genres_without_fact"] = no_fact
    s["genres_name_not_in_facts"] = check
    s["prices"] = sum(1 for i in ok if ev[i]["price_text"])
    s["prices_verified_by_get"] = sum(1 for i in ok if ev[i]["price_text"]
                                      and ev[i]["result"].get("price_verified"))
    s["not_searched"] = sum(1 for i in ok if not ev[i]["research"]["searched"])
    s["nothing_relevant_found"] = sum(1 for i in ok if "P:" not in ev[i]["research"]["text"]
                                      and "E:" not in ev[i]["research"]["text"])
    s["needs_review"] = sum(1 for i in ok if ev[i]["result"].get("needs_review"))
    s["dropped_by_rules"] = sum(len(ev[i]["result"].get("dropped") or []) for i in ok)
    s["dropped_ra_ig_results"] = sum(ev[i]["research"]["dropped_results"] for i in ok)
    s["searches_per_event"] = round(sum(ev[i]["searches"] for i in ok) / n, 2)
    s["fetches_per_event"] = round(sum(ev[i]["fetches"] for i in ok) / n, 2)
    toks = [u for i in ok for u in ev[i]["steps"] if u["model"] == MODEL]
    s["input_tokens_per_event"] = round(sum(u["input_tokens"] for u in toks) / n)
    s["cached_share"] = round(sum(u["cached_tokens"] for u in toks)
                              / max(sum(u["input_tokens"] for u in toks), 1), 2)
    s["output_tokens_per_event"] = round(sum(u["output_tokens"] for u in toks) / n)
    s["cost_total_usd"] = round(sum(ev[i]["cost_usd"] for i in ok), 4)
    s["cost_per_event_usd"] = round(s["cost_total_usd"] / n, 5)
    peak = sum(ev[i]["cost_peak_usd"] for i in ok) / n
    off = sum(ev[i]["cost_offpeak_usd"] for i in ok) / n
    s["per_event_peak_usd"] = round(peak, 5)
    s["per_event_offpeak_usd"] = round(off, 5)
    for k in (280, 1300):
        s[f"month_{k}_peak_usd"] = round(peak * k, 2)
        s[f"month_{k}_offpeak_usd"] = round(off * k, 2)
    return s


def _gemini_d() -> tuple[dict, dict]:
    d = json.loads(GEMINI_D.read_text(encoding="utf-8"))
    rs = d["research"]["gemini-3.6-flash"]
    return d["variants"]["D"], {i: (v.get("rec") or {}) for i, v in rs.items()}


def _genres(res: dict | None) -> str:
    return ", ".join((res or {}).get("genres") or [])


def _price(v: dict, res: dict, who: str) -> str:
    if v.get("venue_price_text"):
        return f"{_app_price(parse_price(v['venue_price_text']))} (web podniku)"
    if v.get("price_text"):
        st = "overená GET-om" if res.get("price_verified") else "neoverená (stránka bez čitateľnej ceny)"
        return f"{who}: {_app_price(parse_price(v['price_text'])) or v['price_text']} ({st})\n" \
               f"{res.get('price_source_url') or ''}"
    why = next((d for d in res.get("dropped", []) if d.startswith("price")), "")
    return f"zahodená: {why}" if why else ""


def _same_genres(a: list, b: list) -> bool:
    return [g.lower() for g in a] == [g.lower() for g in b]


def cmd_xlsx(src: pathlib.Path, dst: pathlib.Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font

    doc = json.loads(src.read_text(encoding="utf-8"))
    labels = load_labels()
    gd, gres = _gemini_d()
    nl = "\n"
    rows, eq_d = [], 0
    for i, lab in labels.items():
        v = doc["events"].get(i) or {"error": "not run"}
        d = (gd.get(i) or {}).get("result") or {}
        res = v.get("result") or {}
        exp = lab["expected_primary"] + (f" (+{lab['expected_secondary']})" if lab["expected_secondary"] else "")
        ok = res.get("primary_format") == lab["expected_primary"]
        same = _same_genres(res.get("genres") or [], d.get("genres") or [])
        eq_d += bool(res) and same
        desc = res.get("descriptions") or {}
        r = v.get("research") or {}
        gf = nl.join(f"{k}: {x}" for k, x in (res.get("genre_facts") or {}).items())
        rows.append([
            lab["venue"], lab["title"], lab["url"], exp, lab["note"],
            _type_str(d) if d else "", ("áno" if d.get("primary_format") == lab["expected_primary"] else "nie") if d else "",
            v.get("error") or _type_str(res) + (f"{nl}{res['type_reason']}" if res.get("type_reason") else ""),
            "" if v.get("error") else ("áno" if ok else "nie"),
            _genres(d), _genres(res) + (nl + gf if gf else ""), "áno" if res and same else "nie",
            _price({"venue_price_text": v.get("venue_price_text"),
                    "price_text": (gd.get(i) or {}).get("price_text")}, d, "Gemini D") if d else "",
            _price(v, res, "DeepSeek") if res else "",
            d.get("start_time") or "", res.get("start_time") or "",
            ", ".join(d.get("artists") or []), ", ".join(res.get("artists") or []),
            (d.get("descriptions") or {}).get("cs") or "", desc.get("cs") or "",
            desc.get("sk") or "", desc.get("en") or "",
            nl.join(r.get("queries") or []), nl.join(r.get("fetched") or []),
            nl.join(s["url"] for s in r.get("sources") or []),
            v.get("searches", ""), v.get("fetches", ""),
            round(v["cost_usd"], 5) if "cost_usd" in v else "",
            nl.join(res.get("dropped") or []),
        ])
    head = ["podnik", "akcia", "odkaz", "Matej (expected)", "Matejova poznámka",
            "typ Gemini D", "D zhoda", "typ DeepSeek A + dôvod", "A zhoda",
            "žánre Gemini D", "žánre DeepSeek A + fakty", "žánre A = D",
            "cena Gemini D", "cena DeepSeek A (+ overenie)", "čas D", "čas A",
            "interpreti D", "interpreti A", "popis CZ Gemini D", "popis CZ DeepSeek A",
            "popis SK DeepSeek A", "popis EN DeepSeek A", "hľadania (dotazy)", "načítané stránky",
            "zdroje (URL)", "počet hľadaní", "počet načítaní", "cena $", "zahodené poistkami"]
    widths = [12, 30, 28, 16, 30, 16, 7, 30, 7, 20, 34, 8, 26, 30, 7, 7, 24, 24, 50, 50, 50, 50,
              34, 30, 40, 8, 8, 9, 40]
    wb = Workbook()
    ws = wb.active
    ws.title = "Akcie"
    font, bold = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
    link = Font(name="Arial", size=10, color="0563C1", underline="single")
    wrap = Alignment(wrap_text=True, vertical="top")
    ws.append(head)
    for row in rows:
        ws.append(row)
    for c in ws[1]:
        c.font, c.alignment = bold, wrap
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font, c.alignment = font, wrap
            if c.column == 3 and isinstance(c.value, str) and c.value.startswith("http"):
                c.hyperlink, c.font = c.value, link
    for k, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(1, k).column_letter].width = w
    ws.freeze_panes = "C2"
    s = summary(doc)
    s["genres_equal_D"] = f"{eq_d}/{len(rows)}"
    ws2 = wb.create_sheet("Súhrn")
    ws2.append(["ukazovateľ", "hodnota"])
    for k, v in s.items():
        ws2.append([k, str(v)])
    ws2.column_dimensions["A"].width, ws2.column_dimensions["B"].width = 34, 20
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    for k, v in s.items():
        print(f"{k}: {v}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        cmd_run(pathlib.Path(os.environ.get("TEST_OUT") or "test-out"))
    elif cmd == "summary":
        for k, v in summary(json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))).items():
            print(f"{k}: {v}")
    elif cmd == "xlsx":
        cmd_xlsx(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
