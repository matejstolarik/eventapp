"""Task 053 part 3: export 50 music events for labelling.
usage: python labels.py before.json after.json out.csv"""
import csv, json, re, sys, collections

before = {e["id"]: e for e in json.load(open(sys.argv[1], encoding="utf-8"))["events"]}
after = json.load(open(sys.argv[2], encoding="utf-8"))
venues = {v["id"]: v["name"] for v in after["venues"]}
MUSIC = {"concert", "dj", "music", "party"}
ELECTRONIC = {"techno", "house", "electronic", "ambient", "drum-and-bass", "dubstep",
              "electro", "uk-bass", "uk-garage", "tech-house", "trance", "ebm", "bassline",
              "experimental"}
LIVE_SET = re.compile(r"live\s*set|liveset|\blive\b.*\b(a/?v|av)\b|\(live\)|/live\b|\blive\s+act\b|"
                      r"hybrid|modular", re.I)

evs = [e for e in after["events"]
       if set(e["formats"]) & MUSIC and e.get("status") == "scheduled"]
evs.sort(key=lambda e: (e["date"], e["id"]))

def disputed(e):
    f = set(e["formats"])
    text = (e["title"] or "") + " " + (e.get("description") or "")
    if LIVE_SET.search(e["title"] or "") or re.search(r"live\s*set|liveset|live a/?v", text, re.I):
        return "live-set"
    if {"concert", "dj"} <= f:
        return "concert+dj"
    if "concert" in f and set(e.get("genres") or []) & ELECTRONIC:
        return "concert+electronic"
    if "dj" in f and re.search(r"\b(band|kapela|live)\b", text, re.I):
        return "dj+live-mention"
    return None

def party_before(e):
    b = before.get(e["id"])
    return b is not None and "party" in b["formats"]

picked, why = [], {}
def take(e, reason):
    if e["id"] not in why and len(picked) < 50:
        picked.append(e); why[e["id"]] = reason

# 1) >= 10 party (before change) outside EPIC, spread across venues
party = [e for e in evs if party_before(e) and e["venue_id"] != "epic"]
by_v = collections.defaultdict(list)
for e in party: by_v[e["venue_id"]].append(e)
while sum(1 for r in why.values() if r == "party-before") < 12 and any(by_v.values()):
    for v in list(by_v):
        if by_v[v]: take(by_v[v].pop(0), "party-before")
# 2) >= 15 disputed (live set / concert vs dj)
disp = [e for e in evs if e["id"] not in why and disputed(e)]
by_v = collections.defaultdict(list)
for e in disp: by_v[e["venue_id"]].append(e)
while sum(1 for r in why.values() if r.startswith("disputed")) < 18 and any(by_v.values()):
    for v in list(by_v):
        if by_v[v]: e = by_v[v].pop(0); take(e, "disputed:" + disputed(e))
# 3) EPIC: 3 events
for e in [e for e in evs if e["venue_id"] == "epic"][:3]: take(e, "epic")
# 4) fill to 50 round-robin over venues
by_v = collections.defaultdict(list)
for e in evs:
    if e["id"] not in why: by_v[e["venue_id"]].append(e)
while len(picked) < 50 and any(by_v.values()):
    for v in sorted(by_v, key=lambda v: sum(1 for p in picked if p["venue_id"] == v)):
        if by_v[v]: take(by_v[v].pop(0), "fill"); break

picked.sort(key=lambda e: (e["venue_id"], e["date"]))
with open(sys.argv[3], "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "venue", "date", "title", "url", "current_formats", "ai_reason", "matej", "note"])
    for e in picked:
        url = next((s["url"] for s in e.get("sources", []) if s.get("url")), "")
        w.writerow([e["id"], venues.get(e["venue_id"], e["venue_id"]), e["date"], e["title"], url,
                    " ".join(e["formats"]), (e.get("classification") or {}).get("reason") or "", "", ""])

print("total", len(picked))
print("by venue", collections.Counter(venues[e["venue_id"]] for e in picked).most_common())
print("by reason", collections.Counter(r.split(":")[0] for r in why.values()))
print("disputed kinds", collections.Counter(r for r in why.values() if r.startswith("disputed")))
print("party before outside EPIC", sum(1 for e in picked if party_before(e) and e["venue_id"] != "epic"))
print("current formats", collections.Counter(" ".join(e["formats"]) for e in picked).most_common())
print("with ai_reason", sum(1 for e in picked if (e.get("classification") or {}).get("reason")))
