"""usage: python compare.py before.json after.json"""
import json, sys, collections
def etype(e):
    f = e["formats"]; p = e.get("primary_format")
    if p and p in f: f = [p]
    if "party" in f: return "party"
    if "dj" in f: return "dj"
    if "concert" in f or "music" in f: return "concert"
    return "culture/other"
b = {e["id"]: e for e in json.load(open(sys.argv[1], encoding="utf-8"))["events"]}
a = json.load(open(sys.argv[2], encoding="utf-8"))
print("after generated_at", a["generated_at"], "events", len(a["events"]))
names = {v["id"]: v["name"] for v in a["venues"]}
a = {e["id"]: e for e in a["events"]}
print("type   before after")
cb = collections.Counter(etype(e) for e in b.values()); ca = collections.Counter(etype(e) for e in a.values())
for t in ["party", "dj", "concert", "culture/other"]: print(f"{t:14} {cb[t]:4} {ca[t]:4}")
print("party by venue before", collections.Counter(names.get(e["venue_id"]) for e in b.values() if etype(e) == "party").most_common())
print("party by venue after ", collections.Counter(names.get(e["venue_id"]) for e in a.values() if etype(e) == "party").most_common())
print("primary_format set:", sum(1 for e in a.values() if e.get("primary_format")), "methods", collections.Counter((e.get("classification") or {}).get("method") for e in a.values()))
ch = [(names.get(e["venue_id"]), e["title"], etype(b[i]), etype(e), " ".join(b[i]["formats"]), " ".join(e["formats"]), e.get("primary_format"), (e.get("classification") or {}).get("reason"))
      for i, e in a.items() if i in b and etype(b[i]) != etype(e)]
print("changed type:", len(ch), collections.Counter(f"{x[2]}->{x[3]}" for x in ch))
for x in sorted(ch): print(" | ".join(str(v) for v in x))
