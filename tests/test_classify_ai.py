"""
Tests for pipeline/classify_ai.py — uses mock API, no network calls.
"""

from unittest.mock import patch, MagicMock

import pytest

from pipeline.classify_ai import classify_events_ai


VENUE = {
    "id": "test-venue",
    "name": "Test Venue",
    "type": ["club"],
    "music": ["techno"],
    "character": [],
}
VENUES = [VENUE]


def _ev(id, title, method=None, formats=None, genres=None):
    ev = {
        "id": id,
        "title": title,
        "venue_id": "test-venue",
        "formats": list(formats or []),
        "genres": list(genres or []),
        "sources": [],
    }
    if method:
        ev["classification"] = {"method": method, "confidence": 0.9}
    return ev


def _mock_client(classifications, stop_reason="end_turn", in_tok=100, out_tok=50):
    usage = MagicMock()
    usage.input_tokens = in_tok
    usage.output_tokens = out_tok

    block = MagicMock()
    block.type = "tool_use"
    block.name = "classify_events"
    block.input = {"classifications": classifications}

    resp = MagicMock()
    resp.stop_reason = stop_reason
    resp.content = [block]
    resp.usage = usage

    client = MagicMock()
    client.messages.create.return_value = resp
    return client


# ---------------------------------------------------------------------------


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_batch_classifies_events(mock_cls):
    mock_cls.return_value = _mock_client([
        {"event_index": 0, "formats": ["dj"], "genres": ["techno"], "confidence": 0.9},
        {"event_index": 1, "formats": ["concert"], "genres": [], "confidence": 0.8},
    ])

    events = [_ev("e1", "TECHNO NIGHT"), _ev("e2", "Live Band")]
    result, stats = classify_events_ai(events, VENUES)

    assert result[0]["formats"] == ["dj"]
    assert result[0]["genres"] == ["techno"]
    assert result[0]["classification"]["method"] == "llm"
    assert result[1]["formats"] == ["concert"]
    assert stats["api_calls"] == 1
    assert stats["skipped"] is False


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_cache_hit_skips_api(mock_cls):
    """Event whose title matches a previous llm-classified event reuses cache."""
    client = MagicMock()
    mock_cls.return_value = client

    prev = [_ev("e1", "TECHNO NIGHT", method="llm", formats=["dj"], genres=["techno"])]
    prev[0]["classification"]["confidence"] = 0.9

    events = [_ev("e1", "TECHNO NIGHT")]
    result, stats = classify_events_ai(events, VENUES, previous_events=prev)

    client.messages.create.assert_not_called()
    assert result[0]["formats"] == ["dj"]
    assert result[0]["genres"] == ["techno"]
    assert stats["cache_hits"] == 1
    assert stats["api_calls"] == 0


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_changed_title_bypasses_cache(mock_cls):
    """Cache miss when event title changed — event goes to API."""
    mock_cls.return_value = _mock_client([
        {"event_index": 0, "formats": ["concert"], "genres": [], "confidence": 0.7},
    ])

    prev = [_ev("e1", "OLD TITLE", method="llm", formats=["dj"])]
    prev[0]["classification"]["confidence"] = 0.9

    events = [_ev("e1", "NEW TITLE")]
    result, stats = classify_events_ai(events, VENUES, previous_events=prev)

    assert stats["cache_hits"] == 0
    assert stats["api_calls"] == 1
    assert result[0]["formats"] == ["concert"]


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_invalid_format_and_genre_discarded(mock_cls):
    """Values not in VALID_FORMATS / VALID_GENRES are silently dropped."""
    mock_cls.return_value = _mock_client([
        {
            "event_index": 0,
            "formats": ["dj", "not-a-format"],
            "genres": ["techno", "not-a-genre"],
            "confidence": 0.7,
        },
    ])

    events = [_ev("e1", "TECHNO NIGHT")]
    result, stats = classify_events_ai(events, VENUES)

    assert result[0]["formats"] == ["dj"]
    assert result[0]["genres"] == ["techno"]


def test_missing_api_key_skips_ai(monkeypatch):
    """Pipeline continues gracefully when ANTHROPIC_API_KEY is not set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    events = [_ev("e1", "TECHNO NIGHT")]
    result, stats = classify_events_ai(events, VENUES)

    assert stats["skipped"] is True
    assert result[0]["formats"] == []


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_max_tokens_keeps_layer1_result(mock_cls):
    """Truncated API response (stop_reason=max_tokens) leaves event at layer 1."""
    truncated = MagicMock()
    truncated.stop_reason = "max_tokens"
    truncated.content = []
    usage = MagicMock()
    usage.input_tokens = 100
    usage.output_tokens = 4096
    truncated.usage = usage

    client = MagicMock()
    client.messages.create.return_value = truncated
    mock_cls.return_value = client

    events = [_ev("e1", "TECHNO NIGHT")]
    result, stats = classify_events_ai(events, VENUES)

    assert result[0]["formats"] == []
    assert "classification" not in result[0]
    assert stats["errors"] == 1


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"})
@patch("pipeline.classify_ai.anthropic.Anthropic")
def test_layer1_source_keyword_not_overwritten(mock_cls):
    """Events classified by source or keyword are excluded from AI processing."""
    mock_cls.return_value = _mock_client([
        {"event_index": 0, "formats": ["other"], "genres": [], "confidence": 0.5},
    ])

    events = [
        _ev("e1", "TECHNO NIGHT", method="source", formats=["dj"]),
        _ev("e2", "Live Gig", method="keyword", formats=["live"]),
        _ev("e3", "Unknown Event"),
    ]
    result, stats = classify_events_ai(events, VENUES)

    # Layer 1 events unchanged
    assert result[0]["formats"] == ["dj"]
    assert result[0]["classification"]["method"] == "source"
    assert result[1]["formats"] == ["live"]
    assert result[1]["classification"]["method"] == "keyword"
    # Only e3 classified by AI
    assert result[2]["formats"] == ["other"]
    assert result[2]["classification"]["method"] == "llm"
