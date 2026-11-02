"""Print statistics from site/events.json.

Usage:
    python scripts/stats.py [path/to/events.json]
"""

import json
import sys
import pathlib
from collections import Counter


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("site/events.json")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    events = data.get("events", [])
    print(f"generated_at: {data.get('generated_at', '?')}")
    print(f"total events: {len(events)}")
    print()

    venue_counts = Counter(e["venue_id"] for e in events)
    print("Events per venue:")
    for vid, cnt in sorted(venue_counts.items()):
        print(f"  {vid}: {cnt}")
    print()

    section_counts: Counter = Counter()
    for e in events:
        for src in e.get("sources", []):
            if src.get("section"):
                section_counts[src["section"]] += 1
    if section_counts:
        print("Events by section (source):")
        for sec, cnt in sorted(section_counts.items()):
            print(f"  {sec}: {cnt}")
        print()

    room_counts = Counter(e.get("room") for e in events)
    room_none = room_counts.pop(None, 0)
    if room_counts or room_none:
        print("Events by room:")
        for room, cnt in sorted(room_counts.items()):
            print(f"  {room}: {cnt}")
        print(f"  (no room): {room_none}")
        print()

    sold_out = sum(1 for e in events if e.get("sold_out") is True)
    not_sold_out = sum(1 for e in events if e.get("sold_out") is False)
    sold_out_null = sum(1 for e in events if e.get("sold_out") is None)
    print(f"sold_out: true={sold_out} false={not_sold_out} null={sold_out_null}")

    status_counts = Counter(e.get("status", "scheduled") for e in events)
    print("Status:", dict(status_counts))

    flag_counts: Counter = Counter()
    for e in events:
        for flag in e.get("flags", []):
            flag_counts[flag] += 1
    if flag_counts:
        print("Quality flags:", dict(flag_counts))

    with_time = sum(1 for e in events if e.get("start_time"))
    print(f"with start_time: {with_time}/{len(events)}")


if __name__ == "__main__":
    main()
