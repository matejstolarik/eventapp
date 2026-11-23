"""Task 092: a failing source keeps its last known future events."""
from pipeline import source_outage, run_summary

TODAY = "2026-11-23"
VENUES = [
    {"id": "klub-007-strahov", "sources": [{"type": "jsonld", "strategy": "eventon", "url": "u"}]},
    {"id": "meetfactory", "sources": [{"type": "jsonld", "section": "hudba", "url": "h"},
                                      {"type": "jsonld", "section": "divadlo", "url": "d"}]},
    {"id": "quiet", "sources": [{"type": "rss", "url": "r"}]},
]


def ev(id_, venue, date, src=None, **kw):
    return {"id": id_, "venue_id": venue, "date": date, "last_seen": "2026-11-21",
            "sources": [src or {"type": "jsonld"}], "title": id_, **kw}


def previous():
    evs = [
        ev("a", "klub-007-strahov", "2026-11-25"),
        ev("b", "klub-007-strahov", "2026-12-01", source_last_ok="2026-11-20"),
        ev("past", "klub-007-strahov", "2026-11-22"),
        ev("m1", "meetfactory", "2026-11-30", {"type": "jsonld", "section": "hudba"}),
        ev("m2", "meetfactory", "2026-11-30", {"type": "jsonld", "section": "divadlo"}),
    ]
    return {e["id"]: e for e in evs}


def test_error_keeps_future_events_unchanged_and_drops_past():
    state = {}
    results = [("klub-007-strahov", "eventon", 0, "error"), ("meetfactory", "hudba", 3, None),
               ("meetfactory", "divadlo", 2, None), ("quiet", "rss", 0, "zero_events")]
    kept, stats, failing = source_outage.keep_failing(VENUES, results, [], previous(), state, TODAY)
    by_id = {e["id"]: e for e in kept}
    assert set(by_id) == {"a", "b"}
    assert by_id["a"]["source_last_ok"] == "2026-11-21"      # from last_seen
    assert by_id["b"]["source_last_ok"] == "2026-11-20"      # kept before: value stays
    assert by_id["a"]["title"] == "a"
    assert stats == {"klub-007-strahov/eventon": 2}
    assert failing == {"klub-007-strahov"}                   # quiet: no program, not failing
    assert state["failing_sources"] == {"klub-007-strahov/eventon": TODAY}


def test_zero_events_after_events_is_failing_per_section():
    state = {}
    results = [("klub-007-strahov", "eventon", 4, None), ("meetfactory", "hudba", 3, None),
               ("meetfactory", "divadlo", 0, "zero_events")]
    current = [ev("m1", "meetfactory", "2026-11-30", {"type": "jsonld", "section": "hudba"})]
    kept, stats, failing = source_outage.keep_failing(VENUES, results, current, previous(), state,
                                                      TODAY)
    assert [e["id"] for e in kept] == ["m2"]
    assert failing == {"meetfactory"}


def test_outage_without_future_events_hides_and_recovery_clears():
    state = {"failing_sources": {"klub-007-strahov/eventon": "2026-11-22"}}
    results = [("klub-007-strahov", "eventon", 0, "zero_events")]
    kept, stats, failing = source_outage.keep_failing(VENUES, results, [], {}, state, TODAY)
    assert kept == [] and stats == {"klub-007-strahov/eventon": 0}
    assert failing == {"klub-007-strahov"}                   # still failing: venue hidden in app
    assert state["failing_sources"] == {"klub-007-strahov/eventon": "2026-11-22"}
    results = [("klub-007-strahov", "eventon", 5, None)]
    kept, stats, failing = source_outage.keep_failing(VENUES, results, [], {}, state, TODAY)
    assert failing == set() and state["failing_sources"] == {}


def test_summary_records_kept_count():
    s = run_summary.build([], {}, [("klub-007-strahov", "eventon", 0, "error")], TODAY,
                          TODAY + "T06:00:00+01:00", kept={"klub-007-strahov/eventon": 7})
    assert s["venues"]["klub-007-strahov"]["sources"][0]["kept"] == 7


def test_venues_have_own_descriptions():
    """Task 092: all venues have own descriptions in 3 languages; copied fields are gone."""
    import json
    import pathlib
    root = pathlib.Path(__file__).parent.parent
    venues = json.loads((root / "data" / "venues.json").read_text(encoding="utf-8"))
    src = json.loads((root / "docs" / "tasks" / "092" / "venue-descriptions.json")
                     .read_text(encoding="utf-8"))["venues"]
    assert len(venues) == 26
    for v in venues:
        assert "description" not in v and "description_url" not in v
        e = src[v["id"]]
        assert v["descriptions"] == {"cs": e["cs"], "sk": e["sk"], "en": e["en"]}
        assert v["description_sources"] == e["sources"]
