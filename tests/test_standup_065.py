"""Task 065 part 2: culture format comedy -> stand-up everywhere."""

from pipeline import enrich_ai as E
from pipeline.classify import rename_format_fields, rename_formats
from pipeline.classify_ai import VALID_FORMATS
from pipeline.main import _migrate_event


def test_valid_formats():
    assert "stand-up" in VALID_FORMATS and "comedy" not in VALID_FORMATS


def test_rename_formats():
    assert rename_formats(["comedy", "theatre", "stand-up"]) == ["stand-up", "theatre"]


def test_cached_event_with_comedy_becomes_stand_up():
    """TANTEHORSE ►IRIS (2026-12-01) had formats [comedy, theatre, music] in the cache."""
    prev = {"id": "palac-akropolis-2026-12-01-tantehorse-iris",
            "formats": ["comedy", "theatre", "music"], "primary_format": "comedy"}
    ev = _migrate_event(prev)
    assert ev["formats"] == ["stand-up", "theatre", "music"]
    assert ev["primary_format"] == "stand-up"
    assert prev["formats"][0] == "comedy"          # input not mutated


def test_unchanged_event_is_the_same_object():
    ev = {"formats": ["concert"], "primary_format": "concert"}
    assert rename_format_fields(ev) is ev


def test_model_answer_comedy_is_stand_up():
    raw = {"formats": ["comedy"], "primary_format": "comedy", "type_source_url": None,
           "genres": [], "genre_candidates": []}
    res = E.validate(raw, {"id": "x", "title": "Stand-up večer"}, None)
    assert res["formats"] == ["stand-up"] and res["primary_format"] == "stand-up"


def test_primary_from_research_comedy():
    ev = {"id": "a", "formats": ["stand-up", "theatre"], "primary_format": None,
          "classification": {"method": "source"}, "enrichment": {}}
    n = E.fill_primary_from_research([ev], {"a": {"primary_format": "comedy"}})
    assert n == 1 and ev["primary_format"] == "stand-up"
