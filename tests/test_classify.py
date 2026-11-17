"""Tests for pipeline/classify.py — commercial club rule (task 053)."""

from pipeline.classify import apply_commercial_clubs

VENUES = [
    {"id": "epic", "commercial_club": True},
    {"id": "cross-club"},
]


def _ev(venue_id, formats, method="llm"):
    return {
        "id": f"{venue_id}-x",
        "venue_id": venue_id,
        "formats": formats,
        "primary_format": None,
        "classification": {"method": method, "confidence": 0.9},
    }


def test_music_event_in_commercial_club_is_party():
    events = [_ev("epic", ["dj"]), _ev("epic", ["music"]), _ev("epic", ["concert", "dj"])]
    apply_commercial_clubs(events, VENUES)
    assert events[0]["formats"] == ["dj", "party"]
    assert events[1]["formats"] == ["party"]
    assert events[2]["formats"] == ["concert", "dj", "party"]
    assert all(e["primary_format"] == "party" for e in events)


def test_existing_party_not_duplicated():
    events = [_ev("epic", ["dj", "party"])]
    apply_commercial_clubs(events, VENUES)
    assert events[0]["formats"] == ["dj", "party"]


def test_non_music_and_other_venues_untouched():
    events = [_ev("epic", ["quiz"]), _ev("cross-club", ["dj"]), _ev("epic", [])]
    apply_commercial_clubs(events, VENUES)
    assert events[0]["formats"] == ["quiz"]
    assert events[0]["primary_format"] is None
    assert events[1]["formats"] == ["dj"]
    assert events[2]["formats"] == []


def test_manual_override_untouched():
    events = [_ev("epic", ["dj"], method="manual")]
    apply_commercial_clubs(events, VENUES)
    assert events[0]["formats"] == ["dj"]


def test_named_dj_in_commercial_club_keeps_dj_primary():
    """Task 058 (ai-rules B5): AI chose dj (known named DJ) -> dj primary, party added."""
    ev = _ev("epic", ["dj"], method="llm+web")
    ev["primary_format"] = "dj"
    generic = _ev("epic", ["dj", "party"], method="llm+web")
    generic["primary_format"] = "party"
    kw = _ev("epic", ["dj"], method="keyword")
    kw["primary_format"] = "dj"
    apply_commercial_clubs([ev, generic, kw], VENUES)
    assert ev["formats"] == ["dj", "party"] and ev["primary_format"] == "dj"
    assert generic["primary_format"] == "party"
    assert kw["primary_format"] == "party"
