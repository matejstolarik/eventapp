import dataclasses
import datetime
import pathlib

import pytest

from pipeline.adapters.html_forum_karlin import parse_listing, parse_detail
from pipeline.models import RawEvent

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

TEST_TODAY = datetime.date(2026, 11, 1)

VENUE = {"id": "forum-karlin", "character": []}
SOURCE = {
    "type": "html",
    "strategy": "forum_karlin",
    "url": "https://www.forumkarlin.cz/program/",
    "max_requests": 50,
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _stub_event(**kwargs) -> RawEvent:
    defaults = dict(
        venue_id="forum-karlin",
        title="Test Event",
        date="2026-11-15",
        start_time=None,
        end_time=None,
        doors_time=None,
        formats=[],
        genres=[],
        character=[],
        artists=[],
        price_text=None,
        free=None,
        sold_out=None,
        room=None,
        ticket_url=None,
        image_url=None,
        source={"type": "html", "url": "https://www.forumkarlin.cz/program/test", "external_id": None, "section": None},
        flags=[],
        status="scheduled",
    )
    defaults.update(kwargs)
    return RawEvent(**defaults)


# ── listing ───────────────────────────────────────────────────────────────────

def test_forum_karlin_parses_events():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    assert len(events) > 5


def test_forum_karlin_titles_non_empty():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    for ev in events:
        assert ev.title and len(ev.title) > 1


def test_forum_karlin_dates_valid():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    yesterday = TEST_TODAY - datetime.timedelta(days=1)
    cutoff = TEST_TODAY + datetime.timedelta(days=180)
    for ev in events:
        d = datetime.date.fromisoformat(ev.date)
        assert d >= yesterday
        assert d <= cutoff


def test_forum_karlin_start_time_none_from_listing():
    """Listing has no time — start_time should be None before detail enrichment."""
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    for ev in events:
        assert ev.start_time is None


def test_forum_karlin_detail_url_present():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    for ev in events:
        url = ev.source.get("url", "")
        assert "forumkarlin.cz" in url


def test_forum_karlin_venue_id():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    for ev in events:
        assert ev.venue_id == "forum-karlin"


def test_forum_karlin_shinedown_in_listing():
    events = parse_listing(VENUE, SOURCE, fixture("forumkarlin_program.html"), today=TEST_TODAY)
    assert any("Shinedown" in ev.title for ev in events), "Shinedown should appear in Nov listing"


# ── detail enrichment (Shinedown fixture) ─────────────────────────────────────

def test_forum_karlin_detail_start_time():
    ev = _stub_event()
    enriched = parse_detail(ev, fixture("forumkarlin_detail_shinedown.html"))
    assert enriched.start_time is not None
    assert ":" in enriched.start_time
    assert len(enriched.start_time) == 5


def test_forum_karlin_detail_doors_time():
    ev = _stub_event()
    enriched = parse_detail(ev, fixture("forumkarlin_detail_shinedown.html"))
    assert enriched.doors_time is not None
    assert ":" in enriched.doors_time


def test_forum_karlin_detail_ticket_url():
    ev = _stub_event()
    enriched = parse_detail(ev, fixture("forumkarlin_detail_shinedown.html"))
    if enriched.ticket_url is not None:
        assert enriched.ticket_url.startswith("http")


def test_forum_karlin_detail_preserves_title():
    ev = _stub_event(title="Shinedown")
    enriched = parse_detail(ev, fixture("forumkarlin_detail_shinedown.html"))
    assert enriched.title == "Shinedown"


# ── minimal HTML fixtures ─────────────────────────────────────────────────────

_MINIMAL_LISTING = """<!DOCTYPE html><html><body>
<div class="program">
<div class="event">
  <div class="event_inner">
    <div class="photo_wrapper">
      <img src="/img/band1.jpg" alt="Band 1">
    </div>
    <h3><a href="https://www.forumkarlin.cz/program/band-one">Band One</a></h3>
    <div class="date"><span class="day">St</span> 15. 11. 2026</div>
  </div>
</div>
<div class="event">
  <div class="event_inner">
    <h3><a href="https://www.forumkarlin.cz/program/band-two">Band Two</a></h3>
    <div class="date"><span class="day">Pá</span> 20. 11. 2026</div>
    <div class="nalepka"><span class="msg">VYPRODÁNO</span></div>
  </div>
</div>
<div class="event">
  <div class="event_inner">
    <h3><a href="https://www.forumkarlin.cz/program/band-three">Band Three</a></h3>
    <div class="date"><span class="day">So</span> 28. 11. 2026</div>
    <div class="nalepka"><span class="msg">ZRUŠENO</span></div>
  </div>
</div>
<div class="event">
  <div class="event_inner">
    <h3><a href="https://www.forumkarlin.cz/program/band-four">Band Four</a></h3>
    <div class="date"><span class="day">Ne</span> 05. 12. 2026</div>
    <div class="nalepka"><span class="msg">JIŽ BRZY</span></div>
  </div>
</div>
</div>
</body></html>"""

_MINIMAL_DETAIL = """<!DOCTYPE html><html><body>
<div class="datum">
  <span class="hodina">20:00</span>
</div>
<div id="otevreni">Otevření dveří: 18:30</div>
<div id="sellers">
  <div class="btn_static"><a href="https://ticketmaster.cz/event/band-one">Ticketmaster</a></div>
  <div class="btn_static"><a href="https://goout.net/event/band-one">GoOut</a></div>
</div>
</body></html>"""


def test_minimal_listing_count():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    yesterday = TEST_TODAY - datetime.timedelta(days=1)
    cutoff = TEST_TODAY + datetime.timedelta(days=180)
    in_window = sum(1 for d in [
        datetime.date(2026, 11, 15),
        datetime.date(2026, 11, 20),
        datetime.date(2026, 11, 28),
        datetime.date(2026, 12, 5),
    ] if yesterday <= d <= cutoff)
    assert len(events) == in_window


def test_minimal_listing_band_one():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Band One"), None)
    assert ev is not None, "Band One should be in window for TEST_TODAY"
    assert ev.date == "2026-11-15"
    assert ev.start_time is None
    assert ev.sold_out is None
    assert ev.status == "scheduled"
    assert "forumkarlin.cz" in ev.source["url"]


def test_minimal_listing_sold_out():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Band Two"), None)
    assert ev is not None, "Band Two should be in window for TEST_TODAY"
    assert ev.sold_out is True


def test_minimal_listing_cancelled():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Band Three"), None)
    assert ev is not None, "Band Three should be in window for TEST_TODAY"
    assert ev.status == "cancelled"


def test_minimal_listing_jiz_brzy_no_change():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Band Four"), None)
    assert ev is not None, "Band Four should be in window for TEST_TODAY"
    assert ev.status == "scheduled"
    assert ev.sold_out is None


def test_minimal_detail_start_time():
    ev = _stub_event()
    enriched = parse_detail(ev, _MINIMAL_DETAIL)
    assert enriched.start_time == "20:00"


def test_minimal_detail_doors_time():
    ev = _stub_event()
    enriched = parse_detail(ev, _MINIMAL_DETAIL)
    assert enriched.doors_time == "18:30"


def test_minimal_detail_ticket_url_first():
    ev = _stub_event()
    enriched = parse_detail(ev, _MINIMAL_DETAIL)
    assert enriched.ticket_url == "https://ticketmaster.cz/event/band-one"


def test_minimal_detail_no_ticket_url():
    html_no_sellers = "<html><body><div class='datum'><span class='hodina'>21:00</span></div></body></html>"
    ev = _stub_event()
    enriched = parse_detail(ev, html_no_sellers)
    assert enriched.ticket_url is None
    assert enriched.start_time == "21:00"
    assert enriched.doors_time is None
