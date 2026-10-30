import pathlib
import pytest

from pipeline.adapters.rss import parse

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE = {
    "id": "cross-club",
    "character": ["alternative", "underground"],
}

SOURCE = {"type": "rss", "url": "https://www.crossclub.cz/cs/rss/program/"}


def _fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_returns_events():
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    assert len(events) == 15


def test_all_events_have_date_and_no_start_time():
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    for e in events:
        assert e.date, f"missing date on '{e.title}'"
        assert e.start_time is None, f"start_time should be null, got {e.start_time!r} on '{e.title}'"


def test_neurocells_date_winter_time():
    """pubDate Thu 29 Oct 2026 23:00 GMT (CET = UTC+1) -> 2026-10-30"""
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    e = next(e for e in events if "NEUROCELLS" in e.title)
    assert e.date == "2026-10-30"
    assert e.start_time is None


def test_cross_square_date_summer_time():
    """pubDate Thu 13 May 2027 22:00 GMT (CEST = UTC+2) -> 2027-05-14"""
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    e = next(e for e in events if "CROSS SQUARE" in e.title)
    assert e.date == "2027-05-14"
    assert e.start_time is None


def test_23h_gmt_becomes_next_day():
    """Synthetic: 23:00 GMT in winter (CET, UTC+1) -> next calendar day, start_time null."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <item>
    <title>Test Event</title>
    <link>https://example.com/event/1</link>
    <guid>1</guid>
    <pubDate>Mon, 10 Nov 2026 23:00:00 GMT</pubDate>
  </item>
</channel></rss>"""
    events = parse(VENUE, SOURCE, xml)
    assert len(events) == 1
    assert events[0].date == "2026-11-11"  # 10 Nov 23:00 UTC = 11 Nov 00:00 Prague (CET)
    assert events[0].start_time is None


def test_character_inherited_from_venue():
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    for e in events:
        assert e.character == ["alternative", "underground"]


def test_source_fields():
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    for e in events:
        assert e.source["type"] == "rss"
        assert e.source["url"].startswith("https://")
        assert e.source["external_id"] is not None


def test_venue_id():
    events = parse(VENUE, SOURCE, _fixture("cross_club_rss.xml"))
    for e in events:
        assert e.venue_id == "cross-club"
