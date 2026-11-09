"""Tests for description extraction across adapter types (task 009)."""
import pathlib

import pytest

from pipeline.adapters.rss import parse as rss_parse, _description_from_entry
from pipeline.adapters.api import parse_strapi, _clean_description as api_clean
from pipeline.adapters.jsonld import parse as jsonld_parse, _clean_description as jsonld_clean

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE = {"id": "test-venue", "character": []}
RSS_SOURCE = {"type": "rss", "url": "https://example.com/rss"}
STRAPI_SOURCE = {
    "type": "api",
    "strategy": "strapi",
    "url": "https://bikejesus.com/api/events",
    "venue_url": "https://bikejesus.com",
    "page_size": 100,
}


# ── _clean_description helper ──────────────────────────────────────────────────

def test_clean_description_strips_html():
    result = api_clean("<p>Hello <b>world</b></p>")
    assert result == "Hello world"


def test_clean_description_strips_whitespace():
    result = api_clean("  Hello   world  ")
    assert result == "Hello world"


def test_clean_description_returns_none_for_empty():
    assert api_clean("") is None
    assert api_clean("   ") is None
    assert api_clean(None) is None


def test_clean_description_truncates_at_sentence():
    long_text = ("This is a sentence. " * 60)  # well over 1000 chars
    result = api_clean(long_text)
    assert result is not None
    assert len(result) <= 1000
    assert result.endswith(".")


def test_clean_description_truncates_with_ellipsis_no_sentence():
    # 60 words without sentence-ending punctuation in first half
    long_text = ("word " * 220)  # over 1000 chars
    result = api_clean(long_text)
    assert result is not None
    assert len(result) <= 1004  # slight overshoot for "..."
    assert result.endswith("...")


def test_jsonld_clean_same_as_api_clean():
    """Both adapters share the same truncation logic."""
    text = "Hello world."
    assert jsonld_clean(text) == api_clean(text)


# ── RSS adapter ────────────────────────────────────────────────────────────────

_RSS_WITH_DESC = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Test Event</title>
    <link>https://example.com/event/1</link>
    <guid>1</guid>
    <pubDate>Mon, 10 Nov 2026 23:00:00 GMT</pubDate>
    <description>A great concert with live music.</description>
  </item>
</channel></rss>"""

_RSS_EMPTY_DESC = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Test Event</title>
    <link>https://example.com/event/1</link>
    <guid>1</guid>
    <pubDate>Mon, 10 Nov 2026 23:00:00 GMT</pubDate>
    <description></description>
  </item>
</channel></rss>"""


def test_rss_description_extracted():
    events = rss_parse(VENUE, RSS_SOURCE, _RSS_WITH_DESC)
    assert len(events) == 1
    assert events[0].description == "A great concert with live music."
    assert events[0].description_source == "source"


def test_rss_description_null_when_empty():
    events = rss_parse(VENUE, RSS_SOURCE, _RSS_EMPTY_DESC)
    assert len(events) == 1
    assert events[0].description is None
    assert events[0].description_source is None


def test_rss_no_description_on_cross_club():
    """Cross Club RSS has empty description tags — all null."""
    events = rss_parse(VENUE, RSS_SOURCE,
                       (FIXTURES / "cross_club_rss.xml").read_text(encoding="utf-8"))
    for ev in events:
        assert ev.description is None
        assert ev.description_source is None


# ── API adapter (Bike Jesus) ──────────────────────────────────────────────────

def test_strapi_description_extracted():
    events = parse_strapi(VENUE, STRAPI_SOURCE,
                          (FIXTURES / "bike_jesus_api.json").read_text(encoding="utf-8"))
    with_desc = [e for e in events if e.description is not None]
    assert len(with_desc) > 0, "Expected at least one event with description in fixture"
    for ev in with_desc:
        assert ev.description_source == "source"
        assert isinstance(ev.description, str)
        assert ev.description.strip()


def test_strapi_description_null_when_missing():
    events = parse_strapi(VENUE, STRAPI_SOURCE,
                          (FIXTURES / "bike_jesus_api.json").read_text(encoding="utf-8"))
    without_desc = [e for e in events if e.description is None]
    assert len(without_desc) > 0, "Expected events without description in fixture"
    for ev in without_desc:
        assert ev.description_source is None


def test_strapi_description_max_1000_chars():
    events = parse_strapi(VENUE, STRAPI_SOURCE,
                          (FIXTURES / "bike_jesus_api.json").read_text(encoding="utf-8"))
    for ev in events:
        if ev.description:
            assert len(ev.description) <= 1000


# ── JSON-LD adapter ────────────────────────────────────────────────────────────

_JSONLD_WITH_DESC = """<!DOCTYPE html><html><body>
<script type="application/ld+json">
{
  "@type": "MusicEvent",
  "name": "Test Concert",
  "startDate": "2026-11-15",
  "description": "An amazing live music event.",
  "url": "https://example.com/event/test"
}
</script></body></html>"""

_JSONLD_NO_DESC = """<!DOCTYPE html><html><body>
<script type="application/ld+json">
{
  "@type": "MusicEvent",
  "name": "Test Concert",
  "startDate": "2026-11-15"
}
</script></body></html>"""


def test_jsonld_description_extracted():
    events = jsonld_parse(VENUE, {"url": "https://example.com/program"}, _JSONLD_WITH_DESC)
    assert len(events) == 1
    assert events[0].description == "An amazing live music event."
    assert events[0].description_source == "source"


def test_jsonld_description_null_when_absent():
    events = jsonld_parse(VENUE, {"url": "https://example.com/program"}, _JSONLD_NO_DESC)
    assert len(events) == 1
    assert events[0].description is None
    assert events[0].description_source is None
