"""Task 086 numbers from the published events.json + pipeline_state.json.

Usage: python docs/tasks/086/nums086.py <dir> <run-date YYYY-MM-DD>
<dir> holds events.json and state.json downloaded from Pages.
"""
import collections
import datetime
import json
import sys

d = json.load(open(sys.argv[1] + "/events.json", encoding="utf-8"))
st = json.load(open(sys.argv[1] + "/state.json", encoding="utf-8"))
run_day = sys.argv[2]
print("generated", d["generated_at"], "events", len(d["events"]))
NEW = ["duplex", "sasazu", "sportovni-hala-fortuna", "kongresove-centrum-praha", "futurum-music-bar"]
for vid in NEW:
    es = [e for e in d["events"] if e["venue_id"] == vid]
    f = lambda k: sum(1 for e in es if e.get(k))
    print(vid, len(es), "start", f("start_time"), "doors", f("doors_time"),
          "price", sum(1 for e in es if e.get("price")),
          "price_src", sum(1 for e in es if e.get("price_text")
                           and "price_text" not in (e.get("enrichment") or {})),
          "image_url", f("image_url"), "thumb", f("image_thumb"),
          "sold_out", sum(1 for e in es if e.get("sold_out")),
          "ai", sum(1 for e in es if (e.get("enrichment") or {}).get("run")))
vmap = {v["id"]: v for v in d["venues"]}
for vid in NEW:
    v = vmap[vid]
    print(vid, "image_card", v.get("image_card"), "first_loaded", v.get("first_loaded"))
print("first_loaded (all):", {v["id"]: v.get("first_loaded") for v in d["venues"]})

enr = [e for e in d["events"]
       if ((e.get("enrichment") or {}).get("run") or {}).get("checked_at") == run_day]
print(f"AI enriched in this run (checked_at {run_day}):", len(enr),
      "rechecked", sum(1 for e in enr if e["enrichment"]["run"].get("rechecked_from")))
print("events w/o AI run:", sum(1 for e in d["events"]
                                if not (e.get("enrichment") or {}).get("run")
                                and e.get("status") != "cancelled"))
print("ai_cost", st.get("ai_cost"))
print("adapter_detail", {k: len(v) for k, v in (st.get("adapter_detail") or {}).items()})
print("venue_first_loaded", st.get("venue_first_loaded"))


# "Nové" before / after part 9 on the same events.json (app rule, day = run day)
def old_new(e, today):
    cutoff = datetime.date.fromisoformat(today) - datetime.timedelta(days=6)
    return bool(e.get("first_seen")) and datetime.date.fromisoformat(e["first_seen"]) >= cutoff


def new_new(e, today):
    fl = vmap.get(e["venue_id"], {}).get("first_loaded")
    return old_new(e, today) and not (fl and e["first_seen"] <= fl)


old = collections.Counter(e["venue_id"] for e in d["events"] if old_new(e, run_day))
new = collections.Counter(e["venue_id"] for e in d["events"] if new_new(e, run_day))
print(f"Nové (day {run_day}) before:", sum(old.values()), dict(old))
print(f"Nové (day {run_day}) after:", sum(new.values()), dict(new))
