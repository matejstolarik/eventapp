"""Tests for the EPIC Prague HTML adapter."""

import datetime
import pathlib

import pytest

from pipeline.adapters.html_epic import parse_listing

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
VENUE = {"id": "epic", "character": ["commercial", "student", "tourist", "late-night"]}
SOURCE = {
    "type": "html",
    "strategy": "epic",
    "url": "https://www.epicprague.com/program",
    "max_requests": 5,
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ── survey fixture tests ───────────────────────────────────────────────────────

def test_epic_parses_events():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    assert len(events) > 3


def test_epic_titles_non_empty():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        assert ev.title and len(ev.title) > 1


def test_epic_dates_valid():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    for ev in events:
        d = datetime.date.fromisoformat(ev.date)
        assert d >= yesterday
        assert d <= cutoff


def test_epic_start_time_present():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        assert ev.start_time is not None, f"start_time missing for {ev.title}"


def test_epic_ticket_url_present():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    with_ticket = [e for e in events if e.ticket_url]
    assert len(with_ticket) > 0


def test_epic_ticket_url_starts_with_http():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        if ev.ticket_url:
            assert ev.ticket_url.startswith("http")


def test_epic_formats_empty_for_ai():
    """EPIC has no hashtag sections — formats should be empty (AI decides)."""
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        assert ev.formats == []


def test_epic_venue_id():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        assert ev.venue_id == "epic"


def test_epic_detail_url_absolute():
    events = parse_listing(VENUE, SOURCE, fixture("epic_program.html"))
    for ev in events:
        assert ev.source["url"].startswith("http")


# ── minimal HTML tests ─────────────────────────────────────────────────────────

_MINIMAL_HTML = """<!DOCTYPE html><html><body>
<main>
  <div class="program__item" data-id="100">
    <div class="program__item-container">
      <time class="program__item-datetime" datetime="2026-11-20 22:00">
        <a href="/program/100/club-night">20/11/2026</a>
      </time>
      <h2 class="program__item-heading">
        <a href="/program/100/club-night">CLUB NIGHT<br></a>
      </h2>
      <div class="program__item-button-wrapper">
        <a href="/program/100/club-night" class="program__item-button epic-button">
          <div class="epic-button__text">Info</div>
        </a>
        <a href="https://tickets.epicprague.com/tickets/events/100/book.html" class="program__item-button epic-button">
          <div class="epic-button__text">Vstupenky</div>
        </a>
      </div>
    </div>
  </div>
  <div class="program__item" data-id="101">
    <div class="program__item-container">
      <time class="program__item-datetime" datetime="2026-11-27 22:00">
        <a href="/program/101/dj-set">27/11/2026</a>
      </time>
      <h2 class="program__item-heading">
        <a href="/program/101/dj-set">BIG DJ SET<br></a>
      </h2>
      <div class="program__item-button-wrapper">
        <a href="/program/101/dj-set" class="program__item-button epic-button">
          <div class="epic-button__text">Info</div>
        </a>
      </div>
    </div>
  </div>
</main>
</body></html>"""


def test_minimal_event_count():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    today = datetime.date.today()
    cutoff = today + datetime.timedelta(days=180)
    yesterday = today - datetime.timedelta(days=1)
    in_window = sum(1 for d in [
        datetime.date(2026, 11, 20),
        datetime.date(2026, 11, 27),
    ] if yesterday <= d <= cutoff)
    assert len(events) == in_window


def test_minimal_title():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if "CLUB NIGHT" in e.title), None)
    if ev is None:
        pytest.skip("CLUB NIGHT outside window")
    assert ev.title == "CLUB NIGHT"
    assert ev.start_time == "22:00"


def test_minimal_ticket_url():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if "CLUB NIGHT" in e.title), None)
    if ev is None:
        pytest.skip("CLUB NIGHT outside window")
    assert ev.ticket_url == "https://tickets.epicprague.com/tickets/events/100/book.html"


def test_minimal_no_ticket_url():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if "BIG DJ SET" in e.title), None)
    if ev is None:
        pytest.skip("BIG DJ SET outside window")
    assert ev.ticket_url is None


def test_minimal_formats_empty():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    for ev in events:
        assert ev.formats == []


def test_minimal_section_none():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    for ev in events:
        assert ev.source["section"] is None
