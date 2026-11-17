"""Task 063: ids for reenrich_from_research (no search)."""
import json, sys
sys.path.insert(0, ".")  # run from the repo root
from pipeline.ai_guards import strip_no_info
ev = json.load(open(sys.argv[1], encoding="utf-8"))["events"]
rs = {r["id"]: r for r in json.load(open(sys.argv[2], encoding="utf-8"))["events"]}
typ, desc = [], []
for e in ev:
    r = rs.get(e["id"])
    if not r:
        continue
    m = (e.get("classification") or {}).get("method")
    if m in ("source", "keyword") and r.get("primary_format") and r["primary_format"] not in (e.get("formats") or []):
        typ.append(e["id"])
    if "description" in (e.get("enrichment") or {}) and strip_no_info((e.get("descriptions") or {}).get("cs"))[1]:
        desc.append(e["id"])
ids = list(dict.fromkeys(typ + desc))
print(len(typ), len(desc), len(ids), file=sys.stderr)
print(",".join(ids))
