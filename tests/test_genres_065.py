"""Task 065: approved genres, hierarchy as data, C7, mappings, guard forms."""

import pytest

from pipeline import enrich_ai as E
from pipeline.ai_guards import genre_supported
from pipeline.genres import (ALL_GENRES, FILM_GENRES, MUSIC_GENRES, NOT_A_LABEL, STAGE_GENRES,
                             UMBRELLAS, drop_contained_parents, finalize_genres, is_ignored,
                             load_aliases, load_hierarchy, load_ignored, map_genre, slug)

ALIASES = load_aliases()
HIER = load_hierarchy()


def test_hierarchy_parents_exist_and_no_cycles():
    for g, parents in HIER.items():
        assert g in ALL_GENRES, g
        assert parents, g
        for p in parents:
            assert p in ALL_GENRES or p in UMBRELLAS, (g, p)
    for start in HIER:
        seen, todo = set(), list(HIER[start])
        while todo:
            p = todo.pop()
            assert p != start, f"cycle through {start}"
            if p not in seen:
                seen.add(p)
                todo += HIER.get(p, [])


def test_alias_targets_are_list_genres():
    for raw, target in ALIASES.items():
        for t in target if isinstance(target, list) else [target]:
            assert t in ALL_GENRES, (raw, t)


@pytest.mark.parametrize("genre,parents", [
    ("hard-techno", ["techno"]), ("trap", ["hip-hop"]), ("afrobeats", ["afro"]),
    ("grunge", ["rock", "alternative"]), ("indie", ["alternative"]), ("doom-metal", ["metal"]),
    ("psytrance", ["trance"]), ("reggaeton", ["latin"]), ("neo-soul", ["soul"]),
    ("drama", ["film", "theatre"]), ("ballet", ["dance"]), ("cult-classic", ["film"]),
])
def test_hierarchy_examples(genre, parents):
    assert HIER[genre] == parents


def test_lists():
    assert {"psytrance", "reggaeton", "afro", "chanson", "soundtrack"} <= MUSIC_GENRES
    assert "alternative" not in MUSIC_GENRES and "alternative" in NOT_A_LABEL
    assert {"drama", "musical", "documentary", "arthouse", "cult-classic"} <= FILM_GENRES
    assert {"drama", "musical", "opera", "puppet-theatre", "contemporary-dance"} <= STAGE_GENRES
    assert "comedy" not in STAGE_GENRES and "stand-up" not in STAGE_GENRES   # C9


@pytest.mark.parametrize("raw,kind,expected", [
    ("psytrance", "music", ["psytrance"]), ("Psy Trance", "music", ["psytrance"]),
    ("psychedelic trance", "music", ["psytrance"]), ("reggaeton", "music", ["reggaeton"]),
    ("Hard Techno", "music", ["hard-techno"]), ("hardtechno", "music", ["hard-techno"]),
    ("breaks", "music", ["breakbeat"]), ("raggajungle", "music", ["jungle"]),
    ("ragga", "music", ["dancehall"]), ("acid house", "music", ["house"]),
    ("afro house", "music", ["house", "afro"]), ("afro-fusion", "music", ["afro"]),
    ("alt. rock", "music", ["alternative-rock"]), ("noise rock", "music", ["noise-rock"]),
    ("folk-rock", "music", ["folk", "rock"]), ("doom metal", "music", ["doom-metal"]),
    ("doom", "music", []), ("sludge", "music", ["sludge-metal"]),
    ("emo-rap", "music", ["hip-hop"]), ("indie pop", "music", ["indie", "pop"]),
    ("electropop", "music", ["pop", "electronic"]), ("šanson", "music", ["chanson"]),
    ("současný tanec", "stage", ["contemporary-dance"]), ("alternative", "music", []),
    ("Documentary", "film", ["documentary"]), ("drama", "stage", ["drama"]),
])
def test_mappings(raw, kind, expected):
    assert map_genre(raw, kind, ALIASES) == expected


def test_slug_strips_diacritics():
    assert slug("šanson") == "sanson"
    assert slug("Trampská píseň") == "trampska-pisen"


@pytest.mark.parametrize("genres,expected", [
    (["doom-metal", "metal"], ["doom-metal"]),
    (["metal", "doom-metal"], ["doom-metal"]),
    (["trap", "hip-hop"], ["trap", "hip-hop"]),            # parent name not contained
    (["hard-techno", "techno", "house"], ["hard-techno", "house"]),
    (["grunge", "rock"], ["grunge", "rock"]),
    (["alternative-rock", "rock"], ["alternative-rock"]),
    (["metalcore", "metal"], ["metalcore", "metal"]),     # no hierarchy entry
])
def test_c7_contained_parent_removed(genres, expected):
    assert drop_contained_parents(genres, HIER) == expected


def test_finalize_drops_alternative_and_renames():
    assert finalize_genres(["alternative", "r-n-b", "rnb", "punk"], HIER) == ["rnb", "punk"]


def _ok(genre, quote):
    return genre_supported(genre, quote, quote, ALIASES)[0]


@pytest.mark.parametrize("genre,text", [
    ("cult-classic", "kultovní snímek osmdesátých let"),
    ("arthouse", "artový film z festivalu v Cannes"),
    ("drama", "činohra Národního divadla"),
    ("drama", "činoherní soubor"),
    ("puppet-theatre", "loutkové divadlo pro dospělé"),
    ("contemporary-dance", "představení současného tance"),
    ("ballet", "baletní soubor"),
    ("documentary", "dokumentární film o kapele"),
    ("animation", "animovaný film"),
    ("horror", "slovenský horor"),
    ("chanson", "česká šansoniérka"),
    ("classical", "koncert vážné hudby"),
    ("psytrance", "Israeli psytrance producer"),
    ("afrobeats", "Nigerian afrobeats star"),
    ("doom-metal", "British doom metal band"),
])
def test_guard_czech_and_english_forms(genre, text):
    assert _ok(genre, text)


@pytest.mark.parametrize("genre,text", [
    ("metal", "British doom metal band"),            # subgenre is no support for parent
    ("trance", "Israeli psytrance producer"),
    ("classical", "klasický rock sedmdesátých let"),
    ("rock", "klasický rock sedmdesátých let"),
])
def test_guard_parent_not_supported_by_subgenre(genre, text):
    assert not _ok(genre, text)


def test_black_and_white_is_no_genre():
    q = "černobílý film z roku 1962"
    assert not any(_ok(g, q) for g in sorted(FILM_GENRES))


def _raw(**kw):
    raw = {"formats": ["talk"], "primary_format": "talk", "type_source_url": "https://x.cz/a",
           "type_confidence": 0.9, "genres": [], "genre_candidates": [], "genre_facts": {},
           "artists": [], "descriptions": None}
    raw.update(kw)
    return raw


EV = {"id": "x", "title": "Jazzmánie", "venue_id": "v", "date": "2026-12-01"}


def test_list_genre_on_talk_event_is_kept_not_a_null_candidate():
    """Jazzmánie (talk) had 'jazz' as a candidate with maps_to null."""
    res = E.validate(_raw(genres=["jazz"], genre_facts={"jazz": "pořad o české jazzové moderně"}),
                     EV, None)
    assert res["genres"] == ["jazz"]
    assert res["genre_candidates"] == []


def test_unlisted_genre_on_talk_event_is_no_music_candidate():
    res = E.validate(_raw(genres=["educational narrative adventure game"]), EV, None)
    assert res["genres"] == [] and res["genre_candidates"] == []
    assert any("no genre list" in d for d in res["dropped"])


def test_ignored_candidates():
    ign = load_ignored()
    assert is_ignored("Trampská píseň", "music", ign)
    assert is_ignored("rock'n'roll", "music", ign)
    assert is_ignored("cabaret", "music", ign)
    assert not is_ignored("cabaret", "stage", ign)
    assert not is_ignored("goa trance", "music", ign)


def test_genre_tables_skip_ignored():
    evs = [{"id": f"e{i}", "enrichment": {"genre_candidates": [
        {"raw": "swing", "kind": "music", "maps_to": None},
        {"raw": "goa trance", "kind": "music", "maps_to": None}]}} for i in range(3)]
    _, props = E.genre_tables(evs, {})
    assert [p["name"] for p in props] == ["goa trance"]
