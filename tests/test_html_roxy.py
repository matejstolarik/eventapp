"""Tests for the ROXY Prague HTML adapter."""

import datetime
import pathlib

import pytest

from pipeline.adapters.html_roxy import parse_listing

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
VENUE = {"id": "roxy", "character": ["alternative", "late-night"]}
SOURCE = {
    "type": "html",
    "strategy": "roxy",
    "url": "https://www.roxy.cz/club/",
    "max_requests": 5,
}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ── survey fixture tests ───────────────────────────────────────────────────────

def test_roxy_parses_events():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    assert len(events) > 3


def test_roxy_titles_non_empty():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    for ev in events:
        assert ev.title and len(ev.title) > 1


def test_roxy_dates_valid():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    for ev in events:
        d = datetime.date.fromisoformat(ev.date)
        assert d >= yesterday
        assert d <= cutoff


def test_roxy_start_time_present():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    # All Roxy events have a time in the datetime attribute
    for ev in events:
        assert ev.start_time is not None, f"start_time missing for {ev.title}"


def test_roxy_detail_url_present():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    for ev in events:
        assert "roxy.cz" in ev.source["url"]


def test_roxy_concert_format():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    concert_events = [e for e in events if "concert" in e.formats]
    assert len(concert_events) > 0


def test_roxy_dj_format():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    dj_events = [e for e in events if "dj" in e.formats]
    assert len(dj_events) > 0


def test_roxy_venue_id():
    events = parse_listing(VENUE, SOURCE, fixture("roxy_club.html"))
    for ev in events:
        assert ev.venue_id == "roxy"


# ── minimal HTML tests ─────────────────────────────────────────────────────────

_MINIMAL_HTML = """<!DOCTYPE html><html><body>
<div class="event-list">
  <a data-hashtags="#concert" href="/events/detail/1/band-one" class="item">
    <article class="wrap">
      <div class="front">
        <time class="date" datetime="2026-11-20 20:00">Pá 20/11</time>
        <h2 class="title">BAND ONE</h2>
        <h3 class="subtitle">(CZ)</h3>
      </div>
    </article>
  </a>
  <a data-hashtags="#dj|#techno" href="/events/detail/2/dj-two" class="item">
    <article class="wrap">
      <div class="front">
        <time class="date" datetime="2026-11-21 23:00">So 21/11</time>
        <h2 class="title">DJ TWO</h2>
        <h3 class="subtitle">(UK)</h3>
      </div>
    </article>
  </a>
  <a data-hashtags="#party" href="/events/detail/3/party-night" class="item">
    <article class="wrap">
      <div class="front">
        <time class="date" datetime="2026-11-22 23:00">Ne 22/11</time>
        <h2 class="title">PARTY NIGHT</h2>
        <h3 class="subtitle">(CZ)</h3>
      </div>
    </article>
  </a>
  <a data-hashtags="#live|#rock" href="/events/detail/4/old-live" class="item">
    <article class="wrap">
      <div class="front">
        <time class="date" datetime="2026-11-25 19:00">St 25/11</time>
        <h2 class="title">OLD LIVE EVENT</h2>
        <h3 class="subtitle">(CZ)</h3>
      </div>
    </article>
  </a>
  <a data-hashtags="#" href="/events/detail/5/other-event" class="item">
    <article class="wrap">
      <div class="front">
        <time class="date" datetime="2026-11-28 20:00">So 28/11</time>
        <h2 class="title">ROXY VISUALS</h2>
        <h3 class="subtitle">(CZ)</h3>
      </div>
    </article>
  </a>
</div>
</body></html>"""


def test_minimal_concert():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if e.title == "BAND ONE"), None)
    if ev is None:
        pytest.skip("BAND ONE outside window")
    assert ev.formats == ["concert"]
    assert ev.source["section"] == "concert"
    assert ev.start_time == "20:00"


def test_minimal_dj():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if e.title == "DJ TWO"), None)
    if ev is None:
        pytest.skip("DJ TWO outside window")
    assert ev.formats == ["dj"]
    assert ev.source["section"] == "dj"
    assert ev.start_time == "23:00"


def test_minimal_party():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if e.title == "PARTY NIGHT"), None)
    if ev is None:
        pytest.skip("PARTY NIGHT outside window")
    assert "dj" in ev.formats
    assert "party" in ev.formats
    assert ev.source["section"] == "party"


def test_minimal_live_hashtag_maps_to_concert():
    """Old #live hashtag on the site should map to format 'concert'."""
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if e.title == "OLD LIVE EVENT"), None)
    if ev is None:
        pytest.skip("OLD LIVE EVENT outside window")
    assert ev.formats == ["concert"]
    assert ev.source["section"] == "concert"


def test_minimal_no_format_hashtag():
    """Event with only '#' (empty) should have no format set (AI will decide)."""
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    ev = next((e for e in events if e.title == "ROXY VISUALS"), None)
    if ev is None:
        pytest.skip("ROXY VISUALS outside window")
    assert ev.formats == []
    assert ev.source["section"] is None


def test_minimal_detail_url_absolute():
    events = parse_listing(VENUE, SOURCE, _MINIMAL_HTML)
    for ev in events:
        assert ev.source["url"].startswith("http")
