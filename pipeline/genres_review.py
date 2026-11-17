"""
Genre mappings and candidates for Matej's review (task 062 part 4, earlier
058 part 3 / 060 part 5).

    python -m pipeline.genres_review site/events.json docs/tasks/062/genres-review.md

Reads one events.json (latest pipeline run) and lists:
  1. approved aliases (data/genre_aliases.json),
  2. mappings proposed by the AI (genre_candidates with maps_to) that are not
     approved yet: raw name -> our genre, count, example events,
  3. candidates without a list genre (maps_to null), all of them,
  4. genres in use (count of events).
"""

import collections
import json
import pathlib
import sys

from pipeline.genres import load_aliases


def build(events: list[dict], approved: dict, generated_at: str | None, src: str) -> str:
    in_window = [e for e in events if (e.get("enrichment") or {}).get("run")]
    mapped: dict = collections.defaultdict(list)
    unmapped: dict = collections.defaultdict(list)
    for ev in in_window:
        for c in (ev.get("enrichment") or {}).get("genre_candidates") or []:
            raw = (c.get("raw") or "").strip()
            if not raw:
                continue
            key = (raw, c.get("kind") or "music")
            if c.get("maps_to"):
                mapped[key + (c["maps_to"],)].append(ev)
            else:
                unmapped[key].append(ev)
    used = collections.Counter(g for e in events for g in e.get("genres") or [])
    approved_l = {k.lower() for k in approved}

    def examples(evs):
        return "; ".join(f"{e.get('title', '')[:40]} ({e['id']})" for e in evs[:3])

    out = [f"# Žánre na kontrolu (úloha 062)", "",
           f"Zdroj: `{src}` (generated_at {generated_at}), príkaz: "
           f"`python -m pipeline.genres_review {src} docs/tasks/062/genres-review.md`.",
           f"Akcie s AI doplnením: {len(in_window)} z {len(events)}.", "",
           "Matej: pri každom riadku napíš áno / nie (alebo iný cieľ). Schválené mapovania "
           "pôjdu do `data/genre_aliases.json`, schválené nové žánre do zoznamu v "
           "`pipeline/genres.py`.", "",
           "## 1. Schválené mapovania (`data/genre_aliases.json`)", "",
           "| surový názov | náš žáner |", "|---|---|"]
    for k, v in sorted(approved.items()):
        out.append(f"| {k} | {', '.join(v) if isinstance(v, list) else v} |")
    out += ["", "## 2. Mapovania navrhnuté AI (ešte neschválené)", "",
            "Surový názov sa mapoval na žáner zo zoznamu (pravopisný variant alebo synonymum).",
            "", "| surový názov | druh | → náš žáner | akcií | príklady | schváliť? |",
            "|---|---|---|---|---|---|"]
    rows = [(k, v) for k, v in mapped.items() if k[0].lower() not in approved_l]
    for (raw, kind, to), evs in sorted(rows, key=lambda x: (-len(x[1]), x[0][0])):
        out.append(f"| {raw} | {kind} | {to} | {len(evs)} | {examples(evs)} | |")
    if not rows:
        out.append("| – | | | | | |")
    out += ["", "## 3. Kandidáti bez žánru zo zoznamu (`maps_to: null`)", "",
            "Nový žáner do zoznamu, mapovanie na existujúci, alebo nič.", "",
            "| surový názov | druh | akcií | príklady | rozhodnutie |", "|---|---|---|---|---|"]
    for (raw, kind), evs in sorted(unmapped.items(), key=lambda x: (-len(x[1]), x[0][0])):
        out.append(f"| {raw} | {kind} | {len(evs)} | {examples(evs)} | |")
    if not unmapped:
        out.append("| – | | | | |")
    out += ["", "## 4. Použité žánre (počet akcií v `events.json`)", "",
            "| žáner | akcií |", "|---|---|"]
    for g, n in used.most_common():
        out.append(f"| {g} | {n} |")
    return "\n".join(out) + "\n"


def main() -> None:
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    data = json.loads(src.read_text(encoding="utf-8"))
    text = build(data["events"], load_aliases(), data.get("generated_at"), sys.argv[1])
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8")
    print(f"written {dst} ({len(text)} chars)")


if __name__ == "__main__":
    main()
