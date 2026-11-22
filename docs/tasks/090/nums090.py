"""Task 090 numbers from the published events.json + pipeline_state.json.

usage: python docs/tasks/090/nums090.py <dir with events.json and state.json>
"""
import collections
import json
import sys

d = sys.argv[1]
data = json.load(open(f"{d}/events.json", encoding="utf-8"))
state = json.load(open(f"{d}/state.json", encoding="utf-8"))
evs = [e for e in data["events"] if e["venue_id"] == "el-magico"]
kinds = collections.Counter(tuple(s["type"] for s in e["sources"]) for e in evs)
print("generated_at", data.get("generated_at"), "| all events", len(data["events"]))
print("el-magico events", len(evs), "| by sources", dict(kinds))
v = next(v for v in data["venues"] if v["id"] == "el-magico")
print("venue first_loaded", v.get("first_loaded"), "| image_card", v.get("image_card"))
posters = ((state.get("adapter_detail") or {}).get("el-magico") or {}).get("posters") or {}
for url, p in posters.items():
    print("poster", url, p.get("month"), "read_at", p.get("read_at"), "rows", len(p.get("rows") or []),
          "dropped", len(p.get("dropped") or []), "cost_usd", p.get("cost_usd"), "usage", p.get("usage"))
print("ai_cost", state.get("ai_cost"))
enriched = sum(1 for e in evs if ((e.get("enrichment") or {}).get("run") or {}).get("checked_at"))
print("AI enriched", enriched, "of", len(evs))
print()
print("| Dátum | Názov | Zdroj | Typ (primary) | formats | Cena | Čas | Interpreti |")
print("|---|---|---|---|---|---|---|---|")
for e in sorted(evs, key=lambda e: (e["date"], e["title"])):
    src = "+".join(s["type"] for s in e["sources"])
    print(f"| {e['date']} | {e['title']} | {src} | {e.get('primary_format')} | "
          f"{', '.join(e.get('formats') or [])} | {e.get('price_text') or ''} | "
          f"{e.get('start_time') or ''} | {', '.join(e.get('artists') or [])} |")
