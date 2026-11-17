"""
Fixed genre lists and mapping of raw genre names (task 054 part 4a, task 058 part 3).

Principle (Matej 2026-11-17, docs/ai-rules.md C): only synonyms and spelling
variants are mapped (``rap -> hip-hop``, ``d&b -> drum-and-bass``).  Subgenres
on the list stay separate and a parent genre is never added automatically
(``metalcore`` is not ``metal``).  Genres keep the order given (main first).

Mapping of a raw name, in this order:
  1. the name itself is on the list (after spelling normalisation:
     lower case, "&" -> "and", spaces/underscores -> "-": "Drum and Bass",
     "dream pop", "Physical theatre"),
  2. approved aliases in data/genre_aliases.json ({raw: genre | [genres]}),
  3. otherwise None (-> genre candidate / proposal for Matej).
"""

import json
import pathlib
import re

ALIASES_PATH = pathlib.Path("data/genre_aliases.json")

MUSIC_GENRES = frozenset({
    "ambient", "bass-music", "bassline", "blues", "darkwave", "death-metal", "disco",
    "dream-pop", "drum-and-bass", "dubstep", "ebm", "edm", "electro", "electro-swing",
    "electronic", "experimental", "folk", "funk", "goregrind", "grindcore", "hardcore",
    "hardstyle", "hip-hop", "house", "indie", "industrial", "jazz", "latin", "metal",
    "metalcore", "oldies", "pop", "post-punk", "punk", "rave", "reggae", "rnb", "rock",
    "ska", "shoegaze", "slowcore", "tech-house", "techno", "trance", "uk-bass",
    "uk-garage", "world",
})
FILM_GENRES: frozenset = frozenset()
STAGE_GENRES = frozenset({"physical-theatre"})

# Renamed codes (old -> new); applied to all genres in the output.
RENAMED = {"r-n-b": "rnb"}

_LISTS = {"music": MUSIC_GENRES, "film": FILM_GENRES, "stage": STAGE_GENRES}


def slug(raw: str) -> str:
    s = str(raw or "").strip().lower().replace("&", " and ")
    s = re.sub(r"['’`]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def load_aliases(path: pathlib.Path = ALIASES_PATH) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def map_genre(raw: str, kind: str = "music", aliases: dict | None = None) -> list[str]:
    """Raw genre name -> list of our genres (main first), [] if unmapped."""
    allowed = _LISTS.get(kind, frozenset())
    s = RENAMED.get(slug(raw), slug(raw))
    if s in allowed:
        return [s]
    al = {slug(k): v for k, v in (aliases or {}).items()}
    target = al.get(s)
    if target is None:
        return []
    targets = target if isinstance(target, list) else [target]
    return [t for t in targets if t in allowed]


def rename_genres(genres: list | None) -> list:
    """Apply RENAMED and drop duplicates, keeping the order."""
    out = []
    for g in genres or []:
        g = RENAMED.get(g, g)
        if g not in out:
            out.append(g)
    return out
