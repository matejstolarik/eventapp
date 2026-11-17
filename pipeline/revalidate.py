"""
Task 062: re-apply the guards (validate / process_result) to the stored model
answers of a `deepseek_test redecide` run -- no API call, the venue pages are
fetched again (one request at a time per site).

    python -m pipeline.revalidate IN.json OUT.json
"""

import json
import pathlib
import sys

from pipeline.deepseek import MODEL
from pipeline.deepseek_test import guards_summary, summary
from pipeline.enrich_ai import process_result
from pipeline.gemini_test import EVENTS_URL, _get_json, _memo_fetch, _page_texts
from pipeline.genres import load_aliases


def main() -> None:
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    doc = json.loads(src.read_text(encoding="utf-8"))
    data = _get_json(EVENTS_URL)
    by_id = {e["id"]: e for e in data["events"]}
    venues = {v["id"]: v for v in data["venues"]}
    old = json.loads(pathlib.Path("docs/tasks/061/deepseek-test.json").read_text(encoding="utf-8"))
    events = {}
    for i, v in doc["events"].items():
        ev = by_id.get(i)
        if ev is None:
            o = old["events"][i]
            ev = {"id": i, "venue_id": o["venue_id"], "title": o["title"], "date": o["date"],
                  "sources": [{"url": o["url"]}] if o.get("url") else [],
                  "price_text": o.get("venue_price_text"), "artists": []}
        events[i] = ev
    pages = _page_texts(list(events.values()))
    fetch = _memo_fetch()
    aliases = load_aliases()
    for i, v in doc["events"].items():
        if "error" in v:
            continue
        ev = events[i]
        r = v["research"]
        src_url = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        rec = {"raw": v["raw"], "searches": 0, "searched": r["searched"], "research": r,
               "seen_urls": [s["url"] for s in r["sources"]],
               "allowed_urls": {s["url"] for s in r["sources"]} | ({src_url} if src_url else set()),
               "spotify_names": {}, "kworb": [],
               "support_text": "\n".join([r.get("text") or "", pages.get(i) or "",
                                          ev.get("title") or "", ev.get("price_text") or ""])}
        res, _ = process_result(ev, rec, MODEL, doc["date"], aliases, fetch,
                                venues.get(ev["venue_id"], {}))
        v["result"] = res
        v["price_text"] = res["price"] if res.get("price_ok") else None
    doc["revalidated"] = "pipeline.revalidate (task 062 guards after the measurement fix)"
    dst.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    s = {**summary(doc), **guards_summary(doc)}
    for k, x in s.items():
        if k != "dropped_list":
            print(f"{k}: {x}")
    print("\n".join(s["dropped_list"]))


if __name__ == "__main__":
    main()
