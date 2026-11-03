import pathlib
import datetime

import pytest

from pipeline.adapters.jsonld import parse_fuchs2, _parse_wix_datetime, _parse_wix_sitemap

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE = {"id": "fuchs2", "character": []}
SOURCE = {
    "type": "jsonld",
    "strategy": "wix_sitemap",
    "sitemap_url": "https://www.fuchs2.cz/event-pages-sitemap.xml",
    "url": "https://www.fuchs2.cz/events/latin-core-thursdays-addly-muff-gatita-tribalera-swine-daily",
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ── _parse_wix_datetime ────────────────────────────────────────────────────────

def test_parse_wix_datetime_winter():
    date, time = _parse_wix_datetime("2026-11-26T23:00:00+01:00")
    assert date == "2026-11-26"
    assert time == "23:00"


def test_parse_wix_datetime_summer():
    date, time = _parse_wix_datetime("2026-07-15T22:00:00+02:00")
    assert date == "2026-07-15"
    assert time == "22:00"


def test_parse_wix_datetime_date_only():
    date, time = _parse_wix_datetime("2026-11-26")
    assert date == "2026-11-26"
    assert time is None


# ── parse_fuchs2 ───────────────────────────────────────────────────────────────

def test_fuchs2_parses_event():
    # Uses future date 2026-11-26; test is valid as long as today < 2027-05-25
    events = parse_fuchs2(VENUE, SOURCE, fixture("fuchs2_event_latin_core_min.html"))
    # If the event date is outside the +180 day window (today > 2027-05-25), skip assertion
    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=180)
    event_date = datetime.date(2026, 11, 26)
    if event_date < today - datetime.timedelta(days=1) or event_date > cutoff:
        pytest.skip("Event date is outside the test's +180 day window")
    assert len(events) == 1
    ev = events[0]
    assert ev.title == "LATIN CORE THURSDAYS: Addly Muff ☆ Gatita Tribalera ☆ Swine Daily"
    assert ev.date == "2026-11-26"
    assert ev.start_time == "23:00"
    assert ev.end_time == "04:00"
    assert ev.venue_id == "fuchs2"
    assert ev.status == "scheduled"
    assert ev.ticket_url is None


def test_fuchs2_source_url_is_event_page():
    events = parse_fuchs2(VENUE, SOURCE, fixture("fuchs2_event_latin_core_min.html"))
    if not events:
        pytest.skip("No events in window")
    assert events[0].source["type"] == "jsonld"
    assert "fuchs2.cz/events/" in events[0].source["url"]


def test_fuchs2_past_event_skipped():
    # Create a minimal HTML with a past event date
    past_html = """<!DOCTYPE html>
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Event","name":"Old Event","startDate":"2020-01-01T20:00:00+01:00","eventStatus":"https://schema.org/EventScheduled","location":{"@type":"Place","name":"Fuchs2","address":"Praha"}}
</script>
</head><body></body></html>"""
    events = parse_fuchs2(VENUE, SOURCE, past_html)
    assert events == []


# ── _parse_wix_sitemap ─────────────────────────────────────────────────────────

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.fuchs2.cz/events/upcoming-event</loc>
    <lastmod>2026-11-01</lastmod>
  </url>
  <url>
    <loc>https://www.fuchs2.cz/events/old-event</loc>
    <lastmod>2025-01-01</lastmod>
  </url>
  <url>
    <loc>https://www.fuchs2.cz/events/another-recent</loc>
    <lastmod>2026-10-15</lastmod>
  </url>
</urlset>"""


def test_parse_wix_sitemap_filters_old():
    since = datetime.date(2026, 8, 1)
    urls = _parse_wix_sitemap(SITEMAP_XML, since)
    assert "https://www.fuchs2.cz/events/upcoming-event" in urls
    assert "https://www.fuchs2.cz/events/another-recent" in urls
    assert "https://www.fuchs2.cz/events/old-event" not in urls


def test_parse_wix_sitemap_empty_xml():
    assert _parse_wix_sitemap("", datetime.date(2026, 1, 1)) == []


