#!/usr/bin/env python3
"""Print description / image_url coverage per venue from site/events.json.

Usage:
    python scripts/coverage.py [path/to/events.json]

Default path: site/events.json
"""

import json
import pathlib
import sys
from collections import Counter


def main() -> None:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "site/events.json")
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    if not events:
        print("No events found.")
        return

    venues: dict[str, dict] = {}
    for ev in events:
        vid = ev.get("venue_id", "unknown")
        if vid not in venues:
            venues[vid] = {"desc": 0, "img": 0, "total": 0, "desc_prefixes": Counter()}
        venues[vid]["total"] += 1
        if ev.get("description"):
            venues[vid]["desc"] += 1
            venues[vid]["desc_prefixes"][ev["description"][:100]] += 1
        if ev.get("image_url"):
            venues[vid]["img"] += 1

    total_desc = sum(v["desc"] for v in venues.values())
    total_img = sum(v["img"] for v in venues.values())
    total_ev = len(events)

    col_w = max(len(v) for v in venues) + 2
    print(f"{'Venue':<{col_w}} description   unique  suspicious   image_url")
    print("-" * (col_w + 48))
    for vid, d in sorted(venues.items()):
        t = d["total"]
        prefixes = d["desc_prefixes"]
        unique = len(prefixes)
        suspicious = sum(1 for c in prefixes.values() if c > 1)
        print(f"{vid:<{col_w}} {d['desc']:>3}/{t:<4}  {unique:>5}       {suspicious:>3}      {d['img']:>3}/{t:<4}")
    print("-" * (col_w + 48))
    total_unique = sum(len(d["desc_prefixes"]) for d in venues.values())
    total_susp = sum(sum(1 for c in d["desc_prefixes"].values() if c > 1) for d in venues.values())
    print(f"{'TOTAL':<{col_w}} {total_desc:>3}/{total_ev:<4}  {total_unique:>5}       {total_susp:>3}      {total_img:>3}/{total_ev:<4}")


if __name__ == "__main__":
    main()
