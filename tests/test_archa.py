import datetime
import pathlib

import pytest

from pipeline.adapters.html_archa import parse, _extract_next_date
from bs4 import BeautifulSoup

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

TEST_TODAY = datetime.date(2026, 11, 1)

VENUE = {"id": "archa-plus", "character": []}
SOURCE = {
    "type": "html",
    "strategy": "archa",
    "url": "https://archa-plus.cz/cz/program/",
    "max_requests": 10,
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ── parse (listing page) ──────────────────────────────────────────────────────

def test_archa_parses_events():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    assert len(events) > 5, "expected several events from listing"


def test_archa_title_and_date():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    # First event should be Lenka Vagnerová (2026-11-03)
    assert any(e for e in events if "Vagnerová" in e.title or "Vagnerova" in e.title)
    dates = [e.date for e in events]
    assert all(d.startswith("202") for d in dates), "all dates should be in YYYY-MM-DD format"


def test_archa_time_parsed():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    timed = [e for e in events if e.start_time is not None]
    assert len(timed) > 0, "at least some events should have start_time"
    for ev in timed:
        assert len(ev.start_time) == 5 and ":" in ev.start_time


def test_archa_source_url_is_detail():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    for ev in events:
        assert "archa-plus.cz/cz/program/detail" in ev.source["url"]


def test_archa_source_type():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    for ev in events:
        assert ev.source["type"] == "html"
        assert ev.venue_id == "archa-plus"


def test_archa_free_event():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    free = [e for e in events if e.free is True]
    assert len(free) > 0, "KARAOKE+ and similar free events should be detected"


def test_archa_goout_button_sold_out_false():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    paid = [e for e in events if e.sold_out is False and e.free is not True]
    assert len(paid) > 0, "events with GoOut button should have sold_out=False"


def test_archa_sold_out_event():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    sold_out = [e for e in events if e.sold_out is True]
    # DEKKADANCERS Dec 18 is sold out
    assert any("DEKKADANCERS" in e.title for e in sold_out), "sold-out event should be detected"


def test_archa_no_ticket_url():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    for ev in events:
        assert ev.ticket_url is None, "Archa+ uses GoOut modal — no direct ticket URL"


def test_archa_section_assigned():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    sectioned = [e for e in events if e.source.get("section") is not None]
    assert len(sectioned) > 0, "some events should have a section"


def test_archa_image_url():
    events = parse(VENUE, SOURCE, fixture("archa_program.html"), today=TEST_TODAY)
    with_img = [e for e in events if e.image_url]
    assert len(with_img) > 0
    for ev in with_img:
        assert ev.image_url.startswith("http")


# ── minimal HTML fixtures ─────────────────────────────────────────────────────

_MINIMAL_LISTING = """<!DOCTYPE html><html><body>
<div class="program-cards">
<div class="program-item">
  <div class="program-image">
    <a href="https://archa-plus.cz/cz/program/detail/99/2026-11-15-test-event">
      <img src="/img/test.jpg" alt="Test Event">
    </a>
  </div>
  <div class="program-item-description">
    <div class="performance-date">
      <h2><a href="https://archa-plus.cz/cz/program/detail/99/2026-11-15-test-event">
        So 15 11,
        20:00
      </a></h2>
    </div>
    <div class="performance-title">
      <h2 class="goout-event-header">
        <a href="https://archa-plus.cz/cz/program/detail/99/2026-11-15-test-event">Test Event</a>
      </h2>
    </div>
    <div class="tags-tickets">
      <div class="tags">
        <span class="tag">hudba</span>
        <span class="tag">EN friendly</span>
        <button class="btn btn-tickets goout-sale-button" data-sale="abc123">
          <span class="goout-sale-datetime">2026-11-15 20:00</span>
          Vstupenky
        </button>
      </div>
    </div>
  </div>
</div>
<div class="program-item">
  <div class="program-image">
    <a href="https://archa-plus.cz/cz/program/detail/100/2026-11-20-free-event">
      <img src="/img/free.jpg" alt="Free Event">
    </a>
  </div>
  <div class="program-item-description">
    <div class="performance-date">
      <h2><a href="https://archa-plus.cz/cz/program/detail/100/2026-11-20-free-event">
        Pá 20 11,
        19:00
      </a></h2>
    </div>
    <div class="performance-title">
      <h2 class="goout-event-header">
        <a href="https://archa-plus.cz/cz/program/detail/100/2026-11-20-free-event">Free Event</a>
      </h2>
    </div>
    <div class="tags-tickets">
      <div class="tags">
        <span class="tag">divadlo</span>
        <span class="tag">vstup zdarma</span>
      </div>
    </div>
  </div>
</div>
<div class="program-item">
  <div class="program-image">
    <a href="https://archa-plus.cz/cz/program/detail/101/2026-12-05-soldout-event">
      <img src="/img/sold.jpg" alt="Sold Out">
    </a>
  </div>
  <div class="program-item-description">
    <div class="performance-date">
      <h2><a href="https://archa-plus.cz/cz/program/detail/101/2026-12-05-soldout-event">
        So 05 12,
        21:00
      </a></h2>
    </div>
    <div class="performance-title">
      <h2 class="goout-event-header">
        <a href="https://archa-plus.cz/cz/program/detail/101/2026-12-05-soldout-event">Sold Out</a>
      </h2>
    </div>
    <div class="tags-tickets">
      <div class="tags">
        <span class="tag">tanec</span>
        <span class="btn btn-soldout">Vyprodáno</span>
      </div>
    </div>
  </div>
</div>
</div>
<div class="load-more">
  <a class="btn btn-load-more" data-next-date-from="2027-02-01" href="/cz/program/load-more?dateFrom=2027-02-01">Načíst další akce</a>
</div>
</body></html>"""


def test_minimal_listing_count():
    events = parse(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    # Dates: 2026-11-15, 2026-11-20, 2026-12-05 — all within +180 days from TEST_TODAY
    yesterday = TEST_TODAY - datetime.timedelta(days=1)
    cutoff = TEST_TODAY + datetime.timedelta(days=180)
    expected = sum(1 for d in [
        datetime.date(2026, 11, 15),
        datetime.date(2026, 11, 20),
        datetime.date(2026, 12, 5),
    ] if yesterday <= d <= cutoff)
    assert len(events) == expected


def test_minimal_goout_event():
    events = parse(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Test Event"), None)
    assert ev is not None, "Test Event should be in window for TEST_TODAY"
    assert ev.date == "2026-11-15"
    assert ev.start_time == "20:00"
    assert ev.sold_out is False
    assert ev.free is None
    assert ev.ticket_url is None
    assert ev.source["section"] == "hudba"


def test_minimal_free_event():
    events = parse(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Free Event"), None)
    assert ev is not None, "Free Event should be in window for TEST_TODAY"
    assert ev.free is True
    assert ev.sold_out is False
    assert ev.source["section"] == "divadlo"


def test_minimal_sold_out_event():
    events = parse(VENUE, SOURCE, _MINIMAL_LISTING, today=TEST_TODAY)
    ev = next((e for e in events if e.title == "Sold Out"), None)
    assert ev is not None, "Sold Out event should be in window for TEST_TODAY"
    assert ev.sold_out is True


def test_extract_next_date():
    soup = BeautifulSoup(_MINIMAL_LISTING, "html.parser")
    assert _extract_next_date(soup) == "2027-02-01"


def test_extract_next_date_none():
    soup = BeautifulSoup("<html><body><p>no button</p></body></html>", "html.parser")
    assert _extract_next_date(soup) is None
