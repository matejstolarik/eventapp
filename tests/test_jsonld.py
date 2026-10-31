import datetime
import pathlib

import pytest

from pipeline.adapters.jsonld import (
    _fetch_listing_pages,
    _parse_kasarna_detail,
    _parse_time_line,
    parse,
    parse_kasarna,
)

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE_MF = {"id": "meetfactory", "character": []}
VENUE_KK = {"id": "kasarna-karlin", "character": []}
VENUE_CU = {"id": "citarna-unijazz", "character": []}

SOURCE_MF = {"type": "jsonld", "url": "https://meetfactory.cz/cs/program/hudba", "section": "hudba"}
SOURCE_KK = {"type": "jsonld", "url": "https://kasarnakarlin.cz/program",
             "follow_links": True, "detail_lang": "en"}
SOURCE_CU = {"type": "jsonld", "url": "https://citarna.unijazz.cz/program/"}

BAD_KARMA_URL = "https://kasarnakarlin.cz/en/program/2026/12/02/bad-karma-boy-album-launch-island-mint"
KEO_URL = "https://kasarnakarlin.cz/en/program/2027/04/12/keo-uk"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def kasarna_details() -> dict:
    return {
        BAD_KARMA_URL: fixture("kasarna_bad_karma_boy.html"),
        KEO_URL: fixture("kasarna_keo.html"),
    }


# ── MeetFactory ───────────────────────────────────────────────────────────────

def test_meetfactory_parses_two_events():
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    assert len(events) == 2


def test_meetfactory_doors_time_and_no_start_time():
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    altin = next(e for e in events if "Alt" in e.title)
    assert altin.doors_time == "20:00"
    assert altin.start_time is None


def test_meetfactory_cancelled_status():
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    cancelled = next(e for e in events if "Cancelled" in e.title)
    assert cancelled.status == "cancelled"


def test_meetfactory_section_in_source():
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    for e in events:
        assert e.source["section"] == "hudba"


def test_meetfactory_image_absolute():
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    altin = next(e for e in events if "Alt" in e.title)
    assert altin.image_url and altin.image_url.startswith("http")


def test_meetfactory_no_ticket_url():
    """offers.url is the event page, not ticket sales — must be null."""
    events = parse(VENUE_MF, SOURCE_MF, fixture("meetfactory_hudba.html"))
    for e in events:
        assert e.ticket_url is None


def test_meetfactory_pagination_fetches_all_pages():
    """_fetch_listing_pages follows endless_more links across multiple pages."""
    from pipeline.fetch import Fetcher

    pages = {
        "https://meetfactory.cz/cs/program/hudba": fixture("meetfactory_hudba_p1.html"),
        "https://meetfactory.cz/cs/program/hudba?page=2": fixture("meetfactory_hudba_p2.html"),
    }

    class _DictFetcher(Fetcher):
        def get(self, url, http_timeout=30):
            return pages[url]

    events = _fetch_listing_pages(VENUE_MF, SOURCE_MF,
                                  fixture("meetfactory_hudba_p1.html"),
                                  _DictFetcher())
    titles = [e.title for e in events]
    assert "Page1 Event" in titles
    assert "Page2 Event" in titles
    assert len(events) == 2


# ── Kasárna time parsing ──────────────────────────────────────────────────────

@pytest.mark.parametrize("text,expected", [
    ("...\n12. 2. 2026\n7:00 PM\n\nDescription", "19:00"),
    ("...\n4. 12. 2027\n19:00\n\nDescription", "19:00"),
    ("...\nEVENT\n12:30 AM\n\nDescription", "00:30"),
    ("...\n12:00 PM\n\nNoon event", "12:00"),
    ("...\n12:00 AM\n\nMidnight event", "00:00"),
    ("No time here at all", None),
])
def test_parse_time_line(text, expected):
    assert _parse_time_line(text) == expected


def test_parse_time_line_deep_in_page():
    """Real Kasárna pages have the time at raw line ~374 (not within first 50)."""
    padding = "\n" * 200
    text = padding + "7:00 PM\n\nDescription"
    assert _parse_time_line(text) == "19:00"


def test_kasarna_ampm_time_from_fixture():
    """Bad Karma Boy shows 7:00 PM in the page → start_time 19:00."""
    events = parse_kasarna(VENUE_KK, SOURCE_KK, fixture("kasarna_listing.html"),
                           kasarna_details())
    bad_karma = next(e for e in events if "Bad Karma" in e.title)
    assert bad_karma.start_time == "19:00"


def test_kasarna_24h_time_from_fixture():
    """Keo shows 19:00 in the page → start_time 19:00."""
    events = parse_kasarna(VENUE_KK, SOURCE_KK, fixture("kasarna_listing.html"),
                           kasarna_details())
    keo = next(e for e in events if "Keo" in e.title)
    assert keo.start_time == "19:00"


def test_kasarna_no_date_conflict_when_dates_match():
    """URL date == JSON-LD date for both fixtures → no date_conflict flag."""
    events = parse_kasarna(VENUE_KK, SOURCE_KK, fixture("kasarna_listing.html"),
                           kasarna_details())
    for e in events:
        assert "date_conflict" not in e.flags, f"unexpected flag on {e.title}"


def test_kasarna_date_conflict_flag():
    """JSON-LD date differs from URL date → date_conflict (but not date_suspicious)."""
    html = fixture("kasarna_bad_karma_boy.html").replace(
        '"2026-12-02T13:00:00+0100"', '"2026-12-03T13:00:00+0100"'
    )
    ev = _parse_kasarna_detail(
        VENUE_KK, SOURCE_KK,
        BAD_KARMA_URL, datetime.date(2026, 12, 2), html
    )
    assert "date_conflict" in ev.flags
    assert "date_suspicious" not in ev.flags


def test_kasarna_date_swap_flags():
    """URL=2026-04-12, JSON-LD=2026-12-04 → date_conflict + date_suspicious."""
    html = fixture("kasarna_bad_karma_boy.html").replace(
        '"2026-12-02T13:00:00+0100"', '"2026-12-04T13:00:00+0100"'
    )
    url = "https://kasarnakarlin.cz/en/program/2026/04/12/some-event"
    ev = _parse_kasarna_detail(
        VENUE_KK, SOURCE_KK,
        url, datetime.date(2026, 4, 12), html
    )
    assert "date_conflict" in ev.flags
    assert "date_suspicious" in ev.flags


def test_kasarna_relative_image_becomes_absolute():
    events = parse_kasarna(VENUE_KK, SOURCE_KK, fixture("kasarna_listing.html"),
                           kasarna_details())
    bad_karma = next(e for e in events if "Bad Karma" in e.title)
    assert bad_karma.image_url == "https://kasarnakarlin.cz/sites/default/files/bad-karma-boy.png"


def test_kasarna_window_filter():
    """Detail URLs outside +180 days must not be fetched."""
    listing_html = """<html><body>
    <a href="/en/program/2030/01/01/far-future-event">Far future</a>
    </body></html>"""
    events = parse_kasarna(VENUE_KK, SOURCE_KK, listing_html, {})
    assert events == []


# ── Čitárna Unijazz ──────────────────────────────────────────────────────────

def test_citarna_parses_two_events():
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    assert len(events) == 2


def test_citarna_start_time_null():
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    for e in events:
        assert e.start_time is None


def test_citarna_empty_image_becomes_null():
    """Empty string image field → image_url None."""
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    for e in events:
        assert e.image_url is None


def test_citarna_no_ticket_url():
    """offers.url on Čitárna is the event page URL — ticket_url must be null."""
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    for e in events:
        assert e.ticket_url is None


def test_citarna_no_section():
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    for e in events:
        assert e.source.get("section") is None


def test_citarna_skips_webpage_type():
    """WebPage JSON-LD must not become an event (its name is 'Program - Čítárna Unijazz')."""
    events = parse(VENUE_CU, SOURCE_CU, fixture("citarna_program.html"))
    titles = [e.title for e in events]
    assert "Program - Čítárna Unijazz" not in titles
