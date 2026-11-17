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
import unicodedata

ALIASES_PATH = pathlib.Path("data/genre_aliases.json")
HIERARCHY_PATH = pathlib.Path("data/genre_hierarchy.json")
IGNORED_PATH = pathlib.Path("data/genre_ignored.json")

MUSIC_GENRES = frozenset({
    "ambient", "bass-music", "bassline", "blues", "darkwave", "death-metal", "disco",
    "dream-pop", "drum-and-bass", "dubstep", "ebm", "edm", "electro", "electro-swing",
    "electronic", "experimental", "folk", "funk", "goregrind", "grindcore", "hardcore",
    "hardstyle", "hip-hop", "house", "indie", "industrial", "jazz", "latin", "metal",
    "metalcore", "oldies", "pop", "post-punk", "punk", "rave", "reggae", "rnb", "rock",
    "ska", "shoegaze", "slowcore", "tech-house", "techno", "trance", "uk-bass",
    "uk-garage", "world",
    # task 065 (Matej 2026-11-17)
    "hard-techno", "breakbeat", "jungle", "synthwave", "grime", "trap", "drill", "afro",
    "afrobeats", "dub", "dancehall", "alternative-rock", "noise-rock", "post-rock",
    "grunge", "gothic-rock", "classic-rock", "garage-rock", "emo", "post-hardcore",
    "noise", "pop-punk", "dance-punk", "noise-punk", "doom-metal", "sludge-metal",
    "stoner-metal", "hyperpop", "dance-pop", "alt-pop", "soul", "neo-soul", "classical",
    "orchestral", "soundtrack", "country", "chanson", "psytrance", "reggaeton",
})
# task 065 (Matej 2026-11-17); parent of all: the culture subtype `film`
FILM_GENRES = frozenset({
    "action", "adventure", "animation", "biography", "comedy", "crime", "documentary",
    "drama", "family", "fantasy", "history", "horror", "music", "musical", "mystery",
    "romance", "sci-fi", "short", "thriller", "war", "western", "experimental", "queer",
    "cult-classic", "arthouse",
})
# parents: the culture subtypes `theatre` / `dance` (data/genre_hierarchy.json)
STAGE_GENRES = frozenset({
    "physical-theatre",
    # task 065 (Matej 2026-11-17)
    "drama", "musical", "opera", "puppet-theatre", "improv", "cabaret", "new-circus",
    "experimental", "contemporary-dance", "ballet", "dance-theatre",
})
ALL_GENRES = MUSIC_GENRES | FILM_GENRES | STAGE_GENRES
# Umbrellas used only as parents in the hierarchy (filter), never as a label
# (ai-rules C8, C9): `alternative`, and the culture subtypes.
UMBRELLAS = frozenset({"alternative", "film", "theatre", "dance"})
NOT_A_LABEL = frozenset({"alternative"})

# Renamed codes (old -> new); applied to all genres in the output.
RENAMED = {"r-n-b": "rnb"}

_LISTS = {"music": MUSIC_GENRES, "film": FILM_GENRES, "stage": STAGE_GENRES}


def slug(raw: str) -> str:
    s = unicodedata.normalize("NFKD", str(raw or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))   # "šanson" -> "sanson"
    s = s.strip().lower().replace("&", " and ")
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


def load_hierarchy(path: pathlib.Path = HIERARCHY_PATH) -> dict:
    """{genre: [parents]} (task 065, ai-rules C7)."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: list(v) for k, v in data.items() if not k.startswith("_")}


def load_ignored(path: pathlib.Path = IGNORED_PATH) -> set:
    """Raw candidate names Matej rejected (task 065): never proposed again.
    Set of (slug, kind) with kind "*" = any kind."""
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {(slug(x), "*") for x in data.get("ignored") or []}
    for kind in ("music", "film", "stage"):
        out |= {(slug(x), kind) for x in data.get(f"ignored_{kind}") or []}
    return out


def is_ignored(raw: str, kind: str | None, ignored: set) -> bool:
    s = slug(raw)
    return (s, "*") in ignored or (s, kind or "music") in ignored


def drop_contained_parents(genres: list, hierarchy: dict | None) -> list:
    """ai-rules C7: a parent is removed when a subgenre of it is also present
    and the parent's name is contained in the subgenre's name
    (doom-metal + metal -> doom-metal); other parents stay (trap + hip-hop)."""
    hierarchy = hierarchy or {}
    drop = set()
    for g in genres:
        for p in hierarchy.get(g) or []:
            if p in genres and p != g and p in g:
                drop.add(p)
    return [g for g in genres if g not in drop]


def finalize_genres(genres: list | None, hierarchy: dict | None = None) -> list:
    """Output genres: renamed codes, no duplicates, no umbrella-only codes
    (`alternative`, ai-rules C8), C7 parent removal."""
    if hierarchy is None:
        hierarchy = load_hierarchy()
    out = [g for g in rename_genres(genres) if g not in NOT_A_LABEL]
    return drop_contained_parents(out, hierarchy)
