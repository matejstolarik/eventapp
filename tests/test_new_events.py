"""Tests for main.count_new_events (task 052)."""

from pipeline.main import count_new_events


def test_count_new_events_per_venue():
    events = [
        {"id": "a", "venue_id": "roxy"},
        {"id": "b", "venue_id": "roxy"},
        {"id": "c", "venue_id": "epic"},
        {"id": "d", "venue_id": "epic"},
    ]
    previous = {"a": {}, "d": {}}
    total, per_venue = count_new_events(events, previous)
    assert total == 2
    assert per_venue == {"epic": 1, "roxy": 1}


def test_count_new_events_none_new():
    events = [{"id": "a", "venue_id": "roxy"}]
    assert count_new_events(events, {"a": {}}) == (0, {})
