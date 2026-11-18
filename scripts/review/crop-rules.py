"""Task 066: how often each crop rule matches Matej's choice in the 064 sheet.

Reads docs/tasks/064/sheet/stats.json (aspect, faces per image),
docs/tasks/064/sheet/v/<id>_<variant>.jpg (360 px variants) and
docs/tasks/064/choices.json.  Nothing in the app or pipeline changes.

Rules (variant names of the sheet: center, faces, top, whole):
  R1 always center
  R2 portrait -> top, else center
  R3 portrait -> top; landscape/banner with a face -> faces;
     landscape/banner without a face -> whole; square -> center
  R4 as R3, but banner (>= 2:1) with a face -> center

Rows skipped as "variants practically the same": square images
(0.95 <= w/h <= 1.05), where center, faces and top show the same square.
A rule also counts as a match when its variant is practically identical to
the chosen one (mean absolute pixel difference < 2 on 0-255), e.g. "faces"
on a portrait without faces equals "top".

Usage: python scripts/review/crop-rules.py
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image

SHEET = pathlib.Path("docs/tasks/064/sheet")
CHOICES = pathlib.Path("docs/tasks/064/choices.json")
SAME = 2.0


def rule(name, aspect, faces):
    if name == "R1":
        return "center"
    if name == "R2":
        return "top" if aspect == "portrait" else "center"
    if aspect == "portrait":
        return "top"
    if aspect == "square":
        return "center"
    if faces:
        if name == "R4" and aspect == "banner":
            return "center"
        return "faces"
    return "whole"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    stats = {r["id"]: r for r in json.loads((SHEET / "stats.json").read_text(encoding="utf-8"))}
    choices = json.loads(CHOICES.read_text(encoding="utf-8"))["choices"]
    cache = {}

    def px(eid, v):
        k = (eid, v)
        if k not in cache:
            cache[k] = np.asarray(Image.open(SHEET / "v" / f"{eid}_{v}.jpg").convert("L"), dtype=np.int16)
        return cache[k]

    def same(eid, a, b):
        return a == b or float(np.abs(px(eid, a) - px(eid, b)).mean()) < SAME

    rules = ["R1", "R2", "R3", "R4"]
    rows, skipped, missing = [], 0, 0
    for eid, choice in choices.items():
        st = stats.get(eid)
        if not st or not (SHEET / "v" / f"{eid}_{choice}.jpg").exists():
            missing += 1
            continue
        if st["aspect"] == "square":
            skipped += 1
            continue
        hit = {r: same(eid, rule(r, st["aspect"], st["faces"]), choice) for r in rules}
        rows.append((eid, st, choice, hit))

    n = len(rows)
    print(f"choices {len(choices)}; skipped square {skipped}; missing {missing}; compared {n}")
    print("| pravidlo | zhoda | % |\n|---|---|---|")
    for r in rules:
        k = sum(h[r] for *_, h in rows)
        print(f"| {r} | {k}/{n} | {100 * k / n:.0f} % |")
    by_aspect = {}
    for eid, st, choice, hit in rows:
        by_aspect.setdefault(st["aspect"], []).append(hit)
    print("\npo pomere strán:")
    for a, hs in sorted(by_aspect.items()):
        print(f"  {a} ({len(hs)}): " + ", ".join(f"{r} {sum(h[r] for h in hs)}" for r in rules))
    best = max(rules, key=lambda r: sum(h[r] for *_, h in rows))
    print(f"\nnajlepšie {best}; nesedí (prvých 10):")
    print("| id | pomer š/v | tváre | voľba Mateja | " + best + " |\n|---|---|---|---|---|")
    k = 0
    for eid, st, choice, hit in rows:
        if hit[best]:
            continue
        print(f"| {eid} | {st['w'] / st['h']:.2f} ({st['aspect']}) | {st['faces']} | {choice} "
              f"| {rule(best, st['aspect'], st['faces'])} |")
        k += 1
        if k == 10:
            break
    print(f"(spolu nesedí {sum(not h[best] for *_, h in rows)})")


if __name__ == "__main__":
    main()
