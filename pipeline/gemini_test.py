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
    if os.environ.get("TEST_IDS", "").strip():          # smoke test on chosen events
        ids = [i.strip() for i in os.environ["TEST_IDS"].split(",") if i.strip() in by_id]
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


def cmd_recheck(src: pathlib.Path, events_json: pathlib.Path) -> None:
    """Local: validate the saved model answers again with the current code
    (no AI call; price check = one GET per AI price as in the daily run)."""
    doc = json.loads(src.read_text(encoding="utf-8"))
    data = json.loads(events_json.read_text(encoding="utf-8"))
    by_id = {e["id"]: e for e in data["events"]}
    for r in doc["results"]:
        if r.get("error"):
            continue
        ev = dict(by_id[r["id"]])
        if "price_text" in (ev.get("enrichment") or {}):
            ev["price_text"] = None        # AI price of task 054, not the venue's
        rec = {"raw": r["raw"], "searches": r["searches"], "searched": r["searched"],
               "seen_urls": [s["url"] for s in r["sources"]],
               "allowed_urls": {s["url"] for s in r["sources"]} | ({r["url"]} if r["url"] else set()),
               "spotify_names": {s["url"]: s["spotify_name"] for s in r["sources"]
                                 if s.get("spotify_name")}}
        res, conv = process_result(ev, rec, doc["model"], doc["date"], {})
        r["result"] = res
        r["values"] = conv["values"]
        r["venue_price_text"] = ev.get("price_text")
        r["claude_price_text"] = by_id[r["id"]].get("price_text") if ev.get("price_text") is None else None
        r["price_text"] = res["price"] if res.get("price_ok") else None
        r["price"] = parse_price(r["price_text"])
    src.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")


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


def _price_cell(r: dict, res: dict) -> str:
    """App price + source + status (venue price wins in the daily run)."""
    venue = r["venue_price_text"] if "venue_price_text" in r else (r.get("current") or {}).get("price_text")
    ai = res.get("price")
    lines = []
    if venue:
        lines.append(f"{_app_price(parse_price(venue))} (web podniku má prednosť)")
    if ai:
        shown = _app_price(parse_price(ai)) or ai
        if r.get("price"):
            status = "overená GET-om"
        elif venue:
            status = "len pre porovnanie"
        else:
            why = next((d.split(": ", 1)[-1] for d in res.get("dropped", [])
                        if d.startswith("price")), "")
            status = f"zahodená: {why}"
        lines.append(f"Gemini: {shown} ({status})\n{res.get('price_source_url') or ''}")
    return "\n".join(lines)


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
        price = _price_cell(r, res)
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


# ---------------------------------------------------------------------------
# Task 059: cost tuning.  One research per event and research model, then
# step 2 (+ translation) for every variant on the same research.
# ---------------------------------------------------------------------------

FLASH, LITE = "gemini-3.6-flash", "gemini-3.1-flash-lite"
# name -> (research model, research thinking, decide model, decide thinking)
VARIANTS = {
    "A": (FLASH, "low", FLASH, "medium"),
    "B": (FLASH, "low", FLASH, "low"),
    "C": (FLASH, "low", LITE, "low"),
    "D": (FLASH, "low", LITE, "minimal"),
    "E": (LITE, "low", LITE, "low"),
    "F": (LITE, "low", FLASH, "low"),
}
# 10 events of the 058 test for the full enrichment comparison
TEN_IDS = [
    SPITFIRE_ID,
    "bike-jesus-2026-11-18-athena-chlebova-krest-praha-gambrz-reprz-ventolin-dj-set-liv",
    "meetfactory-2026-11-19-pragokoncert-allt-avralize-bite-down",
    "fuchs2-2026-11-21-family-therapy-present-asher-parashoot-fahell-zecco-millo",
    "epic-2026-11-21-video-oldies-ruda-tuceka",
    "cross-club-2026-11-18-krizovatka",
    "palac-akropolis-2027-02-23-soyuz-by-pl",
    "cross-club-2026-11-19-up-tone-w-marathon",
    "kasarna-karlin-2026-11-20-animaglajz-animations-from-sutnarka",
    "forum-karlin-2026-11-18-omah-lay",
]


def variant_label(name: str) -> str:
    rm, rt, dm, dt = VARIANTS[name]
    short = {FLASH: "3.6 Flash", LITE: "3.1 Flash-Lite"}
    return f"{name}: prieskum {short[rm]} ({rt}), rozhodnutie {short[dm]} ({dt})"


def _memo_fetch():
    cache: dict = {}

    def fetch(url):
        if url not in cache:
            try:
                cache[url] = _fetch_page_text(url)
            except Exception as exc:          # same as a failed GET
                cache[url] = None
                log.info("price page %s: %s", url, exc)
        return cache[url]
    return fetch


def cmd_tune(out: pathlib.Path) -> None:
    labels = load_labels()
    data = _get_json(EVENTS_URL)
    by_id = {e["id"]: e for e in data["events"]}
    venues = {v["id"]: v for v in data["venues"]}
    ids = list(labels) + [i for i in TEN_IDS if i not in labels]
    if os.environ.get("TEST_IDS", "").strip():
        ids = [i.strip() for i in os.environ["TEST_IDS"].split(",") if i.strip()]
    missing = [i for i in ids if i not in by_id]
    events = [by_id[i] for i in ids if i in by_id]
    names = [v.strip() for v in (os.environ.get("TEST_VARIANTS") or ",".join(VARIANTS)).split(",")
             if v.strip() in VARIANTS]
    budget = float(os.environ.get("TEST_BUDGET_USD") or "1.0")
    spent = [0.0]
    lock = __import__("threading").Lock()
    log.info("tune: %d events, variants %s, budget $%s, missing %s", len(events), names, budget,
             missing)
    pages = _page_texts(events)
    today = datetime.date.today().isoformat()

    def guarded(fn):
        with lock:
            if spent[0] >= budget:
                raise RuntimeError("budget reached")
        res = fn()
        cost = sum(u["cost_usd"] for u in res.get("steps") or res.get("usage") or [])
        with lock:
            spent[0] += cost
        return res

    # step 1 once per research model
    research: dict = {}
    if os.environ.get("TEST_RESEARCH_FILE"):       # same step-1 facts as an earlier run
        for rm, rs in _research_from_file(os.environ["TEST_RESEARCH_FILE"]).items():
            research[rm] = {i: {"rec": v["rec"], "error": v["error"]} for i, v in rs.items()}
    for rm, rt in sorted({(VARIANTS[n][0], VARIANTS[n][1]) for n in names}):
        if rm in research:
            continue
        prov = _Gemini2(model=rm, research_thinking=rt)

        def one(ev, prov=prov):
            try:
                return ev["id"], guarded(lambda: prov.research(
                    ev, venues.get(ev["venue_id"], {}))), None
            except Exception as exc:
                return ev["id"], None, f"{exc.__class__.__name__}: {exc}"[:300]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            research[rm] = {i: {"rec": r, "error": e} for i, r, e in pool.map(one, events)}
        log.info("research %s done, spent $%.4f", rm, spent[0])

    fetch = _memo_fetch()
    variants: dict = {}
    for n in names:
        rm, rt, dm, dt = VARIANTS[n]
        prov = _Gemini2(model=rm, research_thinking=rt, decide_model=dm, decide_thinking=dt)

        def two(ev, prov=prov, rm=rm):
            r = research[rm][ev["id"]]
            if not r["rec"]:
                return ev["id"], None, "research: " + (r["error"] or "?")
            try:
                rec = guarded(lambda: prov.run_from_research(
                    ev, venues.get(ev["venue_id"], {}), pages.get(ev["id"]), r["rec"]))
                rec["searches"] = len(r["rec"]["queries"])
                return ev["id"], rec, None
            except Exception as exc:
                return ev["id"], None, f"{exc.__class__.__name__}: {exc}"[:300]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            raw = list(pool.map(two, events))
        items = {}
        for (i, rec, err), ev in zip(raw, events):
            if err:
                items[i] = {"error": err}
                continue
            res, conv = process_result(ev, rec, rm, today, {}, fetch)   # sequential GETs
            items[i] = {"raw": rec["raw"], "steps": rec["steps"],
                        "result": {k: v for k, v in res.items()},
                        "price_text": res["price"] if res.get("price_ok") else None}
        variants[n] = items
        log.info("variant %s done, spent $%.4f", n, spent[0])

    def clean(rec):
        return {k: v for k, v in rec.items()} if rec else None
    doc = {"date": today, "events_url": EVENTS_URL, "generated_at": data.get("generated_at"),
           "missing": missing, "variants_run": names, "spent_usd": round(spent[0], 4),
           "events": {e["id"]: {"venue_id": e["venue_id"], "title": e["title"],
                                "date": e["date"],
                                "url": next((s.get("url") for s in e.get("sources", [])
                                             if s.get("url")), None),
                                "venue_price_text": e.get("price_text")
                                if "price_text" not in (e.get("enrichment") or {}) else None}
                      for e in events},
           "research": {rm: {i: {"error": v["error"], "rec": clean(v["rec"])}
                             for i, v in rs.items()} for rm, rs in research.items()},
           "variants": variants}
    out.mkdir(parents=True, exist_ok=True)
    (out / "tune.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                                   encoding="utf-8")
    log.info("tune done: spent $%.4f", spent[0])
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## Gemini tuning\n\nEvents {len(events)}, variants {names}, "
                    f"spent ~${spent[0]:.4f}\n")


def _research_from_file(path: str) -> dict:
    """tune: reuse step-1 research of an earlier tune run (same facts for
    every variant, no new search)."""
    doc = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return {rm: dict(rs) for rm, rs in doc["research"].items()}


_GENRE_WORDS = {"hip-hop": ["hip hop", "hip-hop", "rap"], "drum-and-bass": ["drum", "dnb", "jungle"],
                "edm": ["edm", "mainstage", "electro house", "big room"], "rnb": ["r&b", "rnb"]}


def _plain(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("-", " ").split())


def unsupported_genres(res: dict, facts: str) -> tuple[list, list]:
    """(genres without a genre_facts entry, genres whose name does not occur in
    the step-1 facts -> checked by hand)."""
    gf = {k.lower(): v for k, v in (res.get("genre_facts") or {}).items()}
    text = _plain(facts)
    no_fact, check = [], []
    for g in res.get("genres") or []:
        if g.lower() not in gf:
            no_fact.append(g)
        words = _GENRE_WORDS.get(g, [g.replace("-", " ")])
        if not any(_plain(w) in text for w in words):
            check.append(g)
    return no_fact, check


def tune_metrics(doc: dict) -> dict:
    """Per variant: type accuracy on the 50 labelled events, genres, tokens, cost."""
    from pipeline.enrich_ai import GEMINI_FREE_SEARCHES, GEMINI_SEARCH_PRICE, gemini_cost
    labels = load_labels()
    out = {}
    for n, items in doc["variants"].items():
        research = doc["research"][VARIANTS[n][0]]
        ok = ok_noex = n_lab = n_noex = 0
        errors, no_fact, check = [], [], []
        out_tok, cost, cost2, searches, n_ev = 0, 0.0, 0.0, 0, 0
        for i, v in items.items():
            r = (research.get(i) or {}).get("rec")
            if "error" in v or not r:
                errors.append(i)
                continue
            res = v["result"]
            n_ev += 1
            steps = (r.get("usage") or []) + v["steps"]
            out_tok += sum(u["output_tokens"] for u in steps)
            cost += sum(u["cost_usd"] for u in steps)
            cost2 += sum(gemini_cost(u["model"], u["input_tokens"], u["output_tokens"],
                                     u["cached_tokens"], x2=True) for u in steps)
            searches += len(r["queries"])
            a, b = unsupported_genres(res, r.get("text") or "")
            title = doc["events"][i]["title"][:40]
            no_fact += [f"{title}: {g}" for g in a]
            check += [f"{title}: {g}" for g in b]
        for i, lab in labels.items():
            v = items.get(i)
            if v is None:
                continue
            good = (v.get("result") or {}).get("primary_format") == lab["expected_primary"]
            n_lab += 1
            ok += good
            if i not in EXAMPLE_IDS:
                n_noex += 1
                ok_noex += good
        if not n_ev:                    # variant not run (budget) -> left out
            continue
        per, per2 = cost / max(n_ev, 1), cost2 / max(n_ev, 1)
        s_per = searches / max(n_ev, 1)

        def month(k, p):
            extra = max(0.0, s_per * k - GEMINI_FREE_SEARCHES) * GEMINI_SEARCH_PRICE
            return round(p * k + extra, 2)
        out[n] = {"label": variant_label(n), "events": n_ev, "errors": errors,
                  "type_ok": ok, "type_n": n_lab, "noex_ok": ok_noex, "noex_n": n_noex,
                  "no_fact": no_fact, "check": check,
                  "out_tokens": round(out_tok / max(n_ev, 1)), "searches": round(s_per, 2),
                  "cost": per, "cost2027": per2,
                  "m280": month(280, per), "m1300": month(1300, per),
                  "m280_2027": month(280, per2), "m1300_2027": month(1300, per2)}
    return out


def load_tune(srcs: list[pathlib.Path]) -> dict:
    doc = {"variants": {}, "research": {}, "events": {}}
    for s in srcs:                      # several tune runs (same research file)
        d = json.loads(s.read_text(encoding="utf-8"))
        for kk, vv in d["research"].items():
            doc["research"].setdefault(kk, {}).update(vv)
        doc["variants"].update(d["variants"])
        doc["events"].update(d["events"])
    return doc


def cmd_tune_xlsx(srcs: list[pathlib.Path], dst: pathlib.Path, verdicts: pathlib.Path | None,
                  best: list[str]) -> None:
    """Excel for Matej: sheet Varianty, sheet Akcie (10 events: 058 vs. the
    best two variants), sheet Typ 50."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font

    doc = load_tune(srcs)
    labels = load_labels()
    verd = json.loads(verdicts.read_text(encoding="utf-8")) if verdicts and verdicts.exists() else {}
    met = tune_metrics(doc)
    old = {r["id"]: r for r in json.loads(pathlib.Path("docs/tasks/058/gemini_test.json")
                                          .read_text(encoding="utf-8"))["results"]}
    wb = Workbook()
    font, bold = Font(name="Arial", size=10), Font(name="Arial", size=10, bold=True)
    wrap = Alignment(wrap_text=True, vertical="top")
    link = Font(name="Arial", size=10, color="0563C1", underline="single")

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
        for k, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, k).column_letter].width = w
        ws.freeze_panes = "A2"

    nl = "\n"
    # 058 reference (report 058: 55 events, $1.44, 356 searches, 318,591 output tokens)
    rows = [["058: prieskum + rozhodnutie 3.6 Flash (predvolené premýšľanie), popis CZ+SK+EN",
             "47/50 (94 %)", "35/38 (92 %)", "0", "0", 5793, 6.47, 0.0262, 0.0524,
             7.34, 34.08, 14.68, 68.17, "55 akcií, $1.44 (report 058)"]]
    for n, m in met.items():
        notes = verd.get("_notes", {}).get(n)
        rows.append([
            m["label"],
            f"{m['type_ok']}/{m['type_n']} ({100 * m['type_ok'] / max(m['type_n'], 1):.0f} %)",
            f"{m['noex_ok']}/{m['noex_n']} ({100 * m['noex_ok'] / max(m['noex_n'], 1):.0f} %)",
            str(len(m["no_fact"])) + (nl + nl.join(m["no_fact"]) if m["no_fact"] else ""),
            verd.get("_genres", {}).get(n) or (str(len(m["check"])) + " na kontrolu"
                                               + (nl + nl.join(m["check"]) if m["check"] else "")),
            m["out_tokens"], m["searches"], round(m["cost"], 4), round(m["cost2027"], 4),
            m["m280"], m["m1300"], m["m280_2027"], m["m1300_2027"],
            f"{m['events']} akcií" + (f", chyby: {len(m['errors'])}" if m["errors"] else "")
            + (nl + notes if notes else ""),
        ])
    ws = wb.active
    ws.title = "Varianty"
    sheet(ws, ["variant (model / premýšľanie)", "typ – 50 akcií", "typ – bez príkladov v prompte",
               "žáner bez faktu (genre_facts)", "nepodložené žánre",
               "výstupné tokeny / akcia", "hľadania / akcia", "$ / akcia",
               "$ / akcia od 1. 1. 2027", "$ / mesiac pri 280 akciách",
               "$ / mesiac pri 1 300 akciách", "$ / mesiac 280 (od 2027)",
               "$ / mesiac 1 300 (od 2027)", "poznámka"],
          rows, [46, 14, 16, 26, 34, 12, 10, 10, 12, 12, 12, 12, 12, 40])

    def cells(res: dict, r: dict, queries, sources) -> list:
        genres = ", ".join(res.get("genres") or [])
        if res.get("genre_facts"):
            genres += nl + nl.join(f"{k}: {v}" for k, v in res["genre_facts"].items())
        d = res.get("descriptions") or {}
        return [nl.join(queries), nl.join(s["url"] for s in sources),
                _type_str(res) + (f"{nl}{res['type_reason']}" if res.get("type_reason") else ""),
                genres, _price_cell(r, res), res.get("start_time") or "",
                ", ".join(res.get("artists") or [])
                + "".join(f"{nl}Spotify: {a['spotify_url']}" for a in res.get("artist_links") or []),
                d.get("cs") or "", d.get("sk") or "", d.get("en") or ""]

    arows = []
    for i in TEN_IDS:
        e = doc["events"].get(i)
        if not e:
            continue
        lab = labels.get(i)
        exp = VERIFIED[i][0] if i in VERIFIED else (SPITFIRE[0] if i == SPITFIRE_ID else "")
        if not exp and lab:
            exp = lab["expected_primary"] + f" – Matej: {lab['note'][:150]}"
        o = old.get(i)
        if o:
            arows.append([e["venue_id"], e["title"], e["url"], "058"]
                         + cells(o["result"], o, o["queries"], o["sources"])
                         + [exp, verd.get(i, {}).get("058", "")])
        for n in best:
            v = doc["variants"].get(n, {}).get(i)
            rr = (doc["research"][VARIANTS[n][0]].get(i) or {}).get("rec")
            if not v or "error" in v or not rr:
                continue
            r = {"venue_price_text": e.get("venue_price_text"),
                 "price": parse_price(v.get("price_text"))}
            arows.append([e["venue_id"], e["title"], e["url"], variant_label(n)]
                         + cells(v["result"], r, rr["queries"], rr["sources"])
                         + [exp, verd.get(i, {}).get(n, "")])
    ws2 = wb.create_sheet("Akcie")
    sheet(ws2, ["podnik", "názov akcie", "odkaz", "verzia", "čo hľadal", "zdroje", "typ",
                "žánre (v poradí) + fakty", "cena (ako v appke + zdroj)", "čas", "interpreti",
                "popis CZ", "popis SK", "popis EN", "očakávané (overené / Matej)", "výsledok"],
          arows, [12, 26, 28, 26, 30, 36, 22, 30, 24, 7, 26, 50, 40, 40, 34, 30],
          link_cols=(3,))

    trows = []
    for i, lab in labels.items():
        row = [lab["venue"], lab["title"], lab["expected_primary"]
               + (f" (+{lab['expected_secondary']})" if lab["expected_secondary"] else ""),
               "áno" if i in EXAMPLE_IDS else ""]
        for n in met:
            res = (doc["variants"][n].get(i) or {}).get("result")
            row.append("" if res is None else ("OK " if res.get("primary_format")
                                               == lab["expected_primary"] else "CHYBA ")
                       + _type_str(res))
        trows.append(row)
    ws3 = wb.create_sheet("Typ 50")
    sheet(ws3, ["podnik", "akcia", "očakávané (Matej)", "príklad v prompte"]
          + [f"variant {n}" for n in met], trows, [14, 40, 20, 10] + [24] * len(met))
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    for n, m in met.items():
        print(f"{n}: type {m['type_ok']}/{m['type_n']}, no-ex {m['noex_ok']}/{m['noex_n']}, "
              f"no_fact {len(m['no_fact'])}, check {len(m['check'])}, out {m['out_tokens']}, "
              f"searches {m['searches']}, ${m['cost']:.4f} (2027 ${m['cost2027']:.4f}), "
              f"month 280 ${m['m280']} / 1300 ${m['m1300']}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    out = pathlib.Path(os.environ.get("TEST_OUT") or "test-out")
    if cmd == "list":
        cmd_list(out)
    elif cmd == "run":
        cmd_run(out)
    elif cmd == "tune":
        cmd_tune(out)
    elif cmd == "tune-xlsx":     # tune-xlsx OUT.xlsx VERDICTS BEST1,BEST2 IN.json [IN2.json ...]
        cmd_tune_xlsx([pathlib.Path(a) for a in sys.argv[5:]], pathlib.Path(sys.argv[2]),
                      pathlib.Path(sys.argv[3]), sys.argv[4].split(","))
    elif cmd == "recheck":
        cmd_recheck(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))
    elif cmd == "xlsx":
        cmd_xlsx(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]),
                 pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None)


if __name__ == "__main__":
    main()
