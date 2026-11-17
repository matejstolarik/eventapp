"""Task 063: before/after comparison of two events.json files."""
import json, sys, collections
sys.path.insert(0, ".")  # run from the repo root
from pipeline.ai_guards import strip_no_info
b = {e["id"]: e for e in json.load(open(sys.argv[1], encoding="utf-8"))["events"]}
A = json.load(open(sys.argv[2], encoding="utf-8"))
a = {e["id"]: e for e in A["events"]}
print("generated_at", A.get("generated_at"), "events", len(a))
def ty(e):
    return e.get("primary_format") or "/".join(e.get("formats") or []) or "-"
print("\n## type changed (before -> after)")
summ = collections.Counter()
for i, e in a.items():
    o = b.get(i)
    if not o:
        continue
    if (o.get("primary_format"), sorted(o.get("formats") or [])) != (e.get("primary_format"), sorted(e.get("formats") or [])):
        if ty(o) != ty(e) or sorted(o.get("formats") or []) != sorted(e.get("formats") or []):
            summ[(ty(o), ty(e))] += 1
            print(f"| {e['title'][:45]} | {e['venue_id']} | {e['date']} | {'/'.join(o.get('formats') or [])} ({o.get('primary_format')}) | {'/'.join(e.get('formats') or [])} ({e.get('primary_format')}) | {(o.get('classification') or {}).get('method')} -> {(e.get('classification') or {}).get('method')} |")
print("summary", dict(summ))
enr = [e for e in a.values() if "enrichment" in e]
print("\nwith AI enrichment", len(enr))
print("with primary_format (all / enriched)", sum(1 for e in a.values() if e.get("primary_format")), sum(1 for e in enr if e.get("primary_format")))
print("enriched without primary_format", [i for i, e in a.items() if "enrichment" in e and not e.get("primary_format")])
print("methods", collections.Counter((e.get("classification") or {}).get("method") for e in a.values()))
print("needs_review before/after", sum(1 for e in b.values() if (e.get("enrichment") or {}).get("run", {}).get("needs_review")), sum(1 for e in a.values() if (e.get("enrichment") or {}).get("run", {}).get("needs_review")))
print("needs_review ids", [i for i, e in a.items() if (e.get("enrichment") or {}).get("run", {}).get("needs_review")])
ai_desc = [e for e in a.values() if "description" in (e.get("enrichment") or {})]
print("AI descriptions before/after", sum(1 for e in b.values() if "description" in (e.get("enrichment") or {})), len(ai_desc))
print("enriched without AI description", sum(1 for e in enr if "description" not in e["enrichment"]))
left = [(e["id"], s) for e in ai_desc for s in strip_no_info((e.get("descriptions") or {}).get("cs"))[1]]
print("no-info sentences left", len(left)); [print("  ", x) for x in left]
