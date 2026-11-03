import pathlib
import datetime

import pytest

from pipeline.adapters.api import parse_strapi

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE = {"id": "bike-jesus", "character": []}
SOURCE = {
    "type": "api",
    "strategy": "strapi",
    "url": "https://bikejesus.com/api/events",
    "venue_url": "https://bikejesus.com",
    "page_size": 100,
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_bike_jesus_parses_events():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    assert len(events) > 0


def test_bike_jesus_no_start_time():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    for ev in events:
        assert ev.start_time is None


def test_bike_jesus_ticket_url_stripped():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    for ev in events:
        if ev.ticket_url:
            assert ev.ticket_url == ev.ticket_url.strip()
            assert ev.ticket_url.startswith("http")


def test_bike_jesus_within_window():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    for ev in events:
        d = datetime.date.fromisoformat(ev.date)
        assert yesterday <= d <= cutoff, f"{ev.title}: {ev.date} out of window"


def test_bike_jesus_external_id_set():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    for ev in events:
        assert ev.source.get("external_id"), f"{ev.title} has no external_id"


def test_bike_jesus_source_url_is_venue_website():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    for ev in events:
        assert ev.source["url"] == "https://bikejesus.com"


def test_bike_jesus_venue_id():
    events = parse_strapi(VENUE, SOURCE, fixture("bike_jesus_api.json"))
    for ev in events:
        assert ev.venue_id == "bike-jesus"


def test_bike_jesus_minimal_json():
    """Adapter handles minimal Strapi response without crashing."""
    import json
    minimal = json.dumps({
        "data": [
            {"id": 1, "documentId": "abc123", "Title": "Test Event",
             "Date": "2027-01-01", "Tickets": None, "stableId": 1}
        ],
        "meta": {"pagination": {"page": 1, "pageSize": 100, "pageCount": 1, "total": 1}}
    })
    events = parse_strapi(VENUE, SOURCE, minimal)
    # 2027-01-01 is within 180 days from Nov 2026
    assert len(events) == 1
    assert events[0].title == "Test Event"
    assert events[0].ticket_url is None


def test_bike_jesus_empty_title_skipped():
    import json
    data = json.dumps({
        "data": [{"id": 1, "documentId": "abc", "Title": "", "Date": "2027-01-01",
                  "stableId": 1}],
        "meta": {"pagination": {"page": 1, "pageSize": 100, "pageCount": 1, "total": 1}}
    })
    assert parse_strapi(VENUE, SOURCE, data) == []
