"""
Task 058 part 1: test of the Gemini two-step enrichment (manual only).

Run in GitHub Actions (workflow .github/workflows/gemini-test.yml, the API key
is a secret).  Does NOT touch events.json or the daily run.

    python -m pipeline.gemini_test list          # models available to the key
    python -m pipeline.gemini_test run           # 55 events, writes TEST_OUT/gemini_test.json
    python -m pipeline.gemini_test xlsx IN OUT   # local: Excel for Matej (needs openpyxl)

Events: 14 manually verified events from tasks 052/054, Spitfire Company &
PAST (Akropolis), and all 50 events of docs/tasks/056/labels-matej.csv (the 5
disputed ones are among them).  Each event: step 1 (research with Google
Search), step 2 (decision without search), the same validation and price check
as the daily run (pipeline.enrich_ai.process_result).
"""

import concurrent.futures
import csv
import datetime
import json
import logging
import os
import pathlib
import sys
import urllib.request

from pipeline.ai_rules import EXAMPLE_IDS
from pipeline.enrich_ai import (_Gemini2, _fetch_page_text, process_result,
                                GEMINI_PRICE_TABLE)
from pipeline.fetch import USER_AGENT
from pipeline.price import parse_price

log = logging.getLogger("pipeline.gemini_test")

EVENTS_URL = os.environ.get("TEST_EVENTS_URL") or "https://matejstolarik.github.io/eventapp/events.json"
LABELS = pathlib.Path("docs/tasks/056/labels-matej.csv")
SPITFIRE_ID = "palac-akropolis-2026-11-19-spitfire-company-past-cancel"

# 14 events verified by hand in 052/054 (docs/tasks/054 report, part 1 table):
# id -> (expected, Claude 052, expected primary type)
VERIFIED = {
    "cross-club-2026-11-18-krizovatka":
        ("dj; drum-and-bass + rap; zdarma; 20:00", "dj / drum-and-bass, hip-hop; zdarma", "dj"),
    "fuchs2-2026-11-20-high-speed-fairytales-liia-theya-dj-king-kobra-tmk":
        ("concert (dj vedľajší, Matej 056); DnB / broken beats; bez ceny",
         "dj / drum-and-bass, uk-garage, electronic", "concert"),
    "bike-jesus-2026-11-18-athena-chlebova-krest-praha-gambrz-reprz-ventolin-dj-set-liv":
        ("concert (krst); hip-hop; 290 Kč; 20:00", "concert,dj / hip-hop; 290 Kč; 20:00", "concert"),
    "palac-akropolis-2027-02-23-soyuz-by-pl":
        ("concert; folk / pop; 400 Kč", "concert / folk, pop; 400 Kč", "concert"),
    "epic-2026-11-18-student-wednesday":
        ("party; BASIC 290 / VIP 500 Kč", "dj,party; bez ceny", "party"),
    "archa-plus-2026-11-30-roast-slavi-narozky":
        ("talk / comedy; zdarma", "talk,other; bez ceny", "talk"),
    "forum-karlin-2026-11-18-omah-lay":
        ("concert; pop / hip-hop (afrobeats)", "concert / pop, hip-hop; Spotify", "concert"),
    "roxy-2026-11-19-colorfactory":
        ("concert; 990 Kč", "concert; 990 Kč", "concert"),
    "cross-club-2026-11-19-kavarna-krest-boldrikovo-knihy":
        ("talk (+dj)", "talk,dj", "talk"),
    "fuchs2-2026-11-21-family-therapy-present-asher-parashoot-fahell-zecco-millo":
        ("dj; cena na webe nie je", "dj; 400 Kč (vymyslená)", "dj"),
    "meetfactory-2026-11-19-pragokoncert-allt-avralize-bite-down":
        ("concert; metalcore; od 950 Kč; 20:00", "concert / metal; bez ceny; 20:00", "concert"),
    "epic-2026-11-19-almost-weekend":
        ("party; 250 / 400 Kč", "dj,party; 250/400 Kč (zlý zdroj)", "party"),
    "kasarna-karlin-2026-11-20-animaglajz-animations-from-sutnarka":
        ("film; 100 CZK; 19:00", "film; 100 CZK", "film"),
    "cross-club-2026-11-19-up-tone-w-marathon":
        ("concert (dj vedľajší); post-punk / shoegaze; zdarma (rezervácia); 20:00",
         "concert,dj / post-punk, shoegaze; zdarma; 20:00", "concert"),
}
SPITFIRE = ("theatre; Spitfire Company = fyzické divadlo, PAST = experimentálny / industrial "
            "hip-hop s elektronikou", "theatre; bez žánru (PAST prehliadnutý)", "theatre")
DISPUTED = [
    "archa-plus-2026-11-20-amphibian-quadrophonic-soundsystem",
    "bike-jesus-2026-11-20-credit-00-live-midirama-raphael-kosmos",
    "cross-club-2026-11-27-drumstation",
    "epic-2026-11-20-slvl",
    "bike-jesus-2026-11-16-bashment-bass-foundation-anniversary-dance-featuring-nomadix",
]


def load_labels() -> dict:
    with LABELS.open(encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def selected_ids(labels: dict) -> list[str]:
    ids = list(VERIFIED) + [SPITFIRE_ID] + DISPUTED
    ids += [i for i in labels if i not in ids]
    return ids


def _get_json(url: str, key: str | None = None) -> dict:
    headers = {"User-Agent": USER_AGENT}
    if key:
        headers["x-goog-api-key"] = key
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.loads(r.read())


def cmd_list(out: pathlib.Path) -> None:
    key = os.environ["GEMINI_API_KEY"].strip()
    data = _get_json("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000", key)
    names = sorted(m["name"].split("/")[-1] for m in data.get("models", []))
    flash = [n for n in names if "flash" in n]
    out.mkdir(parents=True, exist_ok=True)
    (out / "models.json").write_text(json.dumps(names, indent=1), encoding="utf-8")
    print("\n".join(flash))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Gemini models (flash)\n\n" + "\n".join(f"- `{n}`" for n in flash) + "\n")


def _page_texts(events: list[dict]) -> dict:
    texts = {}
    for ev in events:   # sequential, rate-limited per site
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        if not src:
            continue
        try:
            texts[ev["id"]] = " ".join((_fetch_page_text(src) or "").split())[:5000]
        except Exception as exc:
            log.warning("page %s: %s", src, exc)
    return texts


def cmd_run(out: pathlib.Path) -> None:
    labels = load_labels()
    data = _get_json(EVENTS_URL)
    by_id = {e["id"]: e for e in data["events"]}
    venues = {v["id"]: v for v in data["venues"]}
    ids = [i for i in selected_ids(labels) if i in by_id]
    missing = [i for i in selected_ids(labels) if i not in by_id]
    events = [by_id[i] for i in ids]
    model = os.environ.get("TEST_MODEL", "").strip() or None
    provider = _Gemini2(model=model)
    log.info("gemini test: %d events, model %s, missing %s", len(events), provider.model, missing)
    pages = _page_texts(events)
    today = datetime.date.today().isoformat()

    def one(ev):
        try:
            return ev["id"], provider.run_event(ev, venues.get(ev["venue_id"], {}),
                                                pages.get(ev["id"]), 12), None
        except Exception as exc:
            return ev["id"], None, f"{exc.__class__.__name__}: {exc}"[:300]

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        raw = {i: (rec, err) for i, rec, err in pool.map(one, events)}

    results, tot = [], {"input_tokens": 0, "output_tokens": 0, "searches": 0, "errors": 0}
    for ev in events:
        rec, err = raw[ev["id"]]
        item = {"id": ev["id"], "venue_id": ev["venue_id"], "title": ev["title"],
                "date": ev["date"], "url": next((s.get("url") for s in ev.get("sources", [])
                                                 if s.get("url")), None),
                "current": {k: ev.get(k) for k in ("formats", "primary_format", "genres",
                                                     "price_text", "start_time")}}
        if err:
            item["error"] = err
            tot["errors"] += 1
            results.append(item)
            continue
        res, conv = process_result(ev, rec, provider.model, today, {})
        price_text = res["price"] if res.get("price_ok") else None
        item.update({
            "searched": rec["searched"], "retried": rec["research"]["retried"],
            "queries": rec["research"]["queries"], "sources": rec["research"]["sources"],
            "research_text": rec["research"]["text"], "searches": rec["searches"],
            "input_tokens": rec["input_tokens"], "output_tokens": rec["output_tokens"],
            "raw": rec["raw"],
            "result": {k: v for k, v in res.items()},
            "price_text": price_text, "price": parse_price(price_text),
            "values": conv["values"],
        })
        for k in ("input_tokens", "output_tokens", "searches"):
            tot[k] += rec[k]
        results.append(item)
    pin, pout = GEMINI_PRICE_TABLE.get(provider.model, GEMINI_PRICE_TABLE["gemini-3.6-flash"])
    tot["cost_usd"] = round(tot["input_tokens"] * pin + tot["output_tokens"] * pout, 4)
    out.mkdir(parents=True, exist_ok=True)
    doc = {"model": provider.model, "date": today, "events_url": EVENTS_URL,
           "generated_at": data.get("generated_at"), "missing": missing,
           "totals": tot, "results": results}
    (out / "gemini_test.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    log.info("gemini test done: %s", tot)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## Gemini two-step test ({provider.model})\n\n"
                    f"Events {len(results)}, errors {tot['errors']}, searches {tot['searches']}, "
                    f"tokens {tot['input_tokens']} in / {tot['output_tokens']} out, "
                    f"cost ~${tot['cost_usd']}\n")


# ---------------------------------------------------------------------------
# Excel for Matej (local)
# ---------------------------------------------------------------------------

def _app_price(p: dict | None) -> str:
    if not p:
        return ""
    if p["kind"] == "free":
        return "Zdarma"
    if p["kind"] == "free_reservation":
        return "Zdarma, rezervace"
    if p["kind"] == "voluntary":
        return "Dobrovolné vstupné"
    unit = {"CZK": " Kč", "EUR": " €"}.get(p["currency"] or "", "")
    if p["max"] is None:
        return f"od {p['min']}{unit}"
    return (f"{p['min']}–{p['max']}" if p["max"] != p["min"] else f"{p['min']}") + unit


def _type_str(r: dict) -> str:
    fm = r.get("formats") or []
    pf = r.get("primary_format")
    rest = [f for f in fm if f != pf]
    return (pf or "?") + (f" (+{', '.join(rest)})" if rest else "")


def cmd_xlsx(src: pathlib.Path, dst: pathlib.Path, verdicts: pathlib.Path | None = None) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font

    doc = json.loads(src.read_text(encoding="utf-8"))
    labels = load_labels()
    verd = json.loads(verdicts.read_text(encoding="utf-8")) if verdicts and verdicts.exists() else {}
    wb = Workbook()
    font, bold = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
    link = Font(name="Arial", size=10, color="0563C1", underline="single")
    wrap = Alignment(wrap_text=True, vertical="top")

    def sheet(ws, header, rows, widths, link_cols=()):
        ws.append(header)
        for row in rows:
            ws.append(row)
        for c in ws[1]:
            c.font, c.alignment = bold, wrap
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment = font, wrap
                if c.column in link_cols and isinstance(c.value, str) and c.value.startswith("http"):
                    c.hyperlink, c.font = c.value, link
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = w
        ws.freeze_panes = "A2"

    main_ids = list(VERIFIED) + [SPITFIRE_ID] + DISPUTED
    by_id = {r["id"]: r for r in doc["results"]}
    rows = []
    for i in main_ids:
        r = by_id.get(i)
        if not r:
            continue
        res = r.get("result") or {}
        lab = labels.get(i)
        if i in VERIFIED:
            exp, claude = VERIFIED[i][0], VERIFIED[i][1]
        elif i == SPITFIRE_ID:
            exp, claude = SPITFIRE[0], SPITFIRE[1]
        else:
            exp = (f"{lab['expected_primary']}" + (f" (+{lab['expected_secondary']})"
                   if lab["expected_secondary"] else "") + f" – Matej: {lab['note'][:200]}")
            claude = ", ".join(r["current"]["formats"] or []) + " (053)"
        price = _app_price(r.get("price"))
        if price:
            price += f"\n{res.get('price_source_url') or ''}"
        elif res.get("price"):
            price = f"(zahodená: {res['price']}; {res.get('price_source_url')})"
        if r.get("error"):
            rows.append([r["venue_id"], r["title"], r["url"], "CHYBA", r["error"]] + [""] * 9)
            continue
        genres = ", ".join(res.get("genres") or [])
        if res.get("genre_facts"):
            genres += "\n" + "\n".join(f"{k}: {v}" for k, v in res["genre_facts"].items())
        cands = [c["raw"] for c in res.get("genre_candidates") or [] if not c.get("maps_to")]
        if cands:
            genres += "\nmimo zoznamu: " + ", ".join(cands)
        v = verd.get(i, {})
        rows.append([
            r["venue_id"], r["title"], r["url"],
            ("" if r["searched"] else "NEHĽADAL\n") + "\n".join(r["queries"]),
            "\n".join(s["url"] for s in r["sources"]),
            _type_str(res) + (f"\n{res['type_reason']}" if res.get("type_reason") else ""),
            genres, price, res.get("start_time") or "",
            ", ".join(res.get("artists") or [])
            + "".join(f"\nSpotify: {a['spotify_url']}" for a in res.get("artist_links") or []),
            (res.get("descriptions") or {}).get("cs") or "",
            exp, claude, v.get("result", ""),
        ])
    ws = wb.active
    ws.title = "Akcie"
    sheet(ws, ["podnik", "názov akcie", "odkaz", "čo hľadal", "zdroje", "typ (Gemini)",
               "žánre (Gemini, v poradí)", "cena (ako v appke + zdroj)", "čas", "interpreti",
               "popis CZ", "očakávané (overené / Matej)", "Claude 052/054", "výsledok"],
          rows, [12, 28, 30, 34, 40, 22, 30, 24, 7, 26, 60, 40, 28, 30], link_cols=(3,))

    # sheet 3: type on all 50 labelled events
    trows, ok_all, ok_noex, n_all, n_noex = [], 0, 0, 0, 0
    for i, lab in labels.items():
        r = by_id.get(i)
        res = (r or {}).get("result") or {}
        got = res.get("primary_format")
        ok = got == lab["expected_primary"]
        ex = i in EXAMPLE_IDS
        n_all += 1
        ok_all += ok
        if not ex:
            n_noex += 1
            ok_noex += ok
        trows.append([lab["venue"], lab["title"], lab["url"],
                      lab["expected_primary"] + (f" (+{lab['expected_secondary']})"
                                                 if lab["expected_secondary"] else ""),
                      _type_str(res) if r and not r.get("error") else "CHYBA",
                      "OK" if ok else "chyba", "áno" if ex else "",
                      res.get("type_reason") or ""])
    acc_all = f"{ok_all}/{n_all} ({100 * ok_all / max(n_all, 1):.0f} %)"
    acc_noex = f"{ok_noex}/{n_noex} ({100 * ok_noex / max(n_noex, 1):.0f} %)"

    ws2 = wb.create_sheet("Súhrn")
    t = doc["totals"]
    summ = verd.get("_summary", {})
    srows = [
        ["Model", doc["model"]],
        ["Dátum testu", doc["date"]],
        ["Akcie spolu", len(doc["results"])],
        ["Chyby", t["errors"]],
        ["Akcie „nehľadal“", sum(1 for r in doc["results"] if r.get("searched") is False)],
        ["Hľadania spolu", t["searches"]],
        ["Tokeny vstup / výstup", f"{t['input_tokens']} / {t['output_tokens']}"],
        ["Cena testu (z tokenov a cenníka)", f"${t['cost_usd']}"],
        ["Akcie so Spotify (všetkých 55)",
         sum(1 for r in doc["results"] if (r.get("result") or {}).get("artist_links"))],
        ["Typ – 50 akcií (Matej), spolu", acc_all],
        ["Typ – 50 akcií, bez príkladov v prompte", acc_noex],
    ] + [[k, v] for k, v in summ.items()]
    sheet(ws2, ["Ukazovateľ", "Hodnota"], srows, [48, 70])

    ws3 = wb.create_sheet("Typ 50 akcií")
    sheet(ws3, ["podnik", "akcia", "odkaz", "očakávané (Matej)", "Gemini", "OK/chyba",
                "príklad v prompte", "dôvod (Gemini)"], trows, [14, 40, 30, 20, 22, 10, 10, 50],
          link_cols=(3,))
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    print(f"{dst}: type 50 = {acc_all}, without examples = {acc_noex}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    out = pathlib.Path(os.environ.get("TEST_OUT") or "test-out")
    if cmd == "list":
        cmd_list(out)
    elif cmd == "run":
        cmd_run(out)
    elif cmd == "xlsx":
        cmd_xlsx(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]),
                 pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None)


if __name__ == "__main__":
    main()
