import datetime
import json
import pathlib

import pytest

from pipeline.adapters.html_akropolis import (
    _parse_date_no_year,
    _parse_time_room,
    parse,
)

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VENUE = {"id": "palac-akropolis", "character": []}
SOURCE = {
    "type": "html",
    "strategy": "akropolis",
    "base_url": "https://palacakropolis.cz/work/33298",
    "no": "62",
    "genres": [{"genre": "1", "page_id": "38637", "section": "hudba"}],
    "detail_page_id": "33824",
    "ticket_page_id": "42027",
    "vstupne_url": "https://palacakropolis.cz/pub/vstupne_6",
    "pagination_param": "plg_33527_page",
    "max_requests": 20,
}
GENRE_HUDBA = {"genre": "1", "page_id": "38637", "section": "hudba"}


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def vstupne() -> dict:
    return json.loads((FIXTURES / "akropolis_vstupne.json").read_text(encoding="utf-8"))


# ── _parse_time_room ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("text,exp_time,exp_room", [
    ("19:30, \xa0Velký sál", "19:30", "Velký sál"),
    ("21:00, \xa0Malá scéna", "21:00", "Malá scéna"),
    ("20:00, \xa0Jazz Bar", "20:00", "Jazz Bar"),
    ("18:15,  Velký sál", "18:15", "Velký sál"),
    ("not a time", None, None),
    ("", None, None),
])
def test_parse_time_room(text, exp_time, exp_room):
    assert _parse_time_room(text) == (exp_time, exp_room)


# ── _parse_date_no_year ───────────────────────────────────────────────────────

def test_date_no_year_current_year():
    today = datetime.date.today()
    # A date well in the future (but < 180 days) should use the current year
    future = today + datetime.timedelta(days=30)
    text = f"{future.day}. {future.month}."
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    result = _parse_date_no_year(text, yesterday, cutoff)
    assert result == future.isoformat()


def test_date_no_year_rollover_to_next_year():
    """A date in the past rolls over to next year if still within 180 days.

    Scenario: today = 2026-11-02, date = '15. 3.' (March 15).
    2026-03-15 < yesterday → rolls to 2027-03-15.
    2027-03-15 is within 180 days of 2026-11-02 → returned.
    """
    yesterday = datetime.date(2026, 11, 1)
    cutoff = datetime.date(2027, 4, 30)
    result = _parse_date_no_year("15. 3.", yesterday, cutoff)
    assert result == "2027-03-15"


def test_date_no_year_beyond_cutoff_returns_none():
    """A date beyond +180 days returns None (outside window)."""
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    cutoff = today + datetime.timedelta(days=180)
    far = today + datetime.timedelta(days=200)
    text = f"{far.day}. {far.month}."
    result = _parse_date_no_year(text, yesterday, cutoff)
    assert result is None


def test_date_no_year_december_january_rollover():
    """December date seen in November → current year; same date in new year."""
    # Simulate: today is 2026-11-02, date is "15. 12." → 2026-12-15
    yesterday = datetime.date(2026, 11, 1)
    cutoff = datetime.date(2027, 4, 30)
    result = _parse_date_no_year("15. 12.", yesterday, cutoff)
    assert result == "2026-12-15"


def test_date_no_year_january_from_december():
    """January date seen in December → next year."""
    yesterday = datetime.date(2026, 12, 1)
    cutoff = datetime.date(2027, 5, 30)
    result = _parse_date_no_year("15. 1.", yesterday, cutoff)
    assert result == "2027-01-15"


# ── parse (single page) ───────────────────────────────────────────────────────

def test_akropolis_parses_three_events():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    assert len(events) == 3


def test_akropolis_title_and_date():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.title == "KAFKA BAND HRAJE KAFKU"
    assert kafka.date.endswith("-11-04")


def test_akropolis_html_entities_in_title():
    """HTML entity ► in title should be decoded (title field is raw; normalize decodes)."""
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    nebojsy = next(e for e in events if "NEBOJSY" in e.title)
    # The raw title comes from .get_text(strip=True) so BS4 already decodes entities
    assert "►" in nebojsy.title or "KUCHYŇSKÉ" in nebojsy.title


def test_akropolis_time_and_room():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.start_time == "19:30"
    assert kafka.room == "Velký sál"


def test_akropolis_section():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    for e in events:
        assert e.source["section"] == "hudba"


def test_akropolis_sold_out():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    nebojsy = next(e for e in events if "NEBOJSY" in e.title)
    assert nebojsy.sold_out is True
    assert nebojsy.ticket_url is None


def test_akropolis_kup_ted_ticket_url():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.sold_out is False
    assert kafka.ticket_url == "https://palacakropolis.cz/work/33298?event_id=40205&no=62&page_id=42027"


def test_akropolis_image_absolute():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.image_url and kafka.image_url.startswith("https://palacakropolis.cz")


def test_akropolis_detail_url_in_source():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert "event_id=40205" in kafka.source["url"]
    assert "page_id=33824" in kafka.source["url"]


def test_akropolis_event_id_in_source():
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.source["external_id"] == "40205"


# ── own_rooms filter ─────────────────────────────────────────────────────────

def test_own_rooms_filters_external_venue():
    # Velký sál only → DECEMBER CONCERT (Malá scéna) is skipped
    source_strict = {**SOURCE, "own_rooms": ["Velký sál"]}
    events = parse(VENUE, source_strict, fixture("akropolis_hudba.html"), vstupne(), GENRE_HUDBA)
    assert all("DECEMBER" not in e.title for e in events), "external-venue event should be filtered"
    assert any("KAFKA" in e.title for e in events), "own-venue event should be kept"


def test_own_rooms_no_room_event_kept():
    # An event with no room is always kept, even with strict own_rooms
    html_no_room = """<!DOCTYPE html><html><body>
<a href='/work/33298?event_id=99001&page_id=33824'>
<div class='basic_cont3'>
<span class='color_title_date'>1. 12.</span>
<div class='banner_m_title'>NO ROOM EVENT</div>
<div class='kas_box6' id='99001'></div>
</div></a></body></html>"""
    source_strict = {**SOURCE, "own_rooms": ["Velký sál", "Malá scéna", "Jazz bar"]}
    events = parse(VENUE, source_strict, html_no_room, {}, GENRE_HUDBA)
    assert any("NO ROOM" in e.title for e in events)


def test_own_rooms_external_room_skipped():
    # An event at an unlisted room ("Roxy") is skipped
    html_external = """<!DOCTYPE html><html><body>
<a href='/work/33298?event_id=99002&page_id=33824'>
<div class='basic_cont3'>
<span class='color_title_date'>1. 12.</span>
<div class='banner_m_title'>EXTERNAL VENUE EVENT</div>
<span class='fct40'>20:00, &nbsp;Roxy</span>
<div class='kas_box6' id='99002'></div>
</div></a></body></html>"""
    source_with_rooms = {**SOURCE, "own_rooms": ["Velký sál", "Malá scéna", "Jazz bar"]}
    events = parse(VENUE, source_with_rooms, html_external, {}, GENRE_HUDBA)
    assert len(events) == 0, "event at external venue should be filtered"


# ── vstupne_6 codes ──────────────────────────────────────────────────────────

def test_vstupne_code_3_free():
    v = {**vstupne(), "40205": {"no": 3}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.free is True
    assert kafka.sold_out is False
    assert kafka.ticket_url is None


def test_vstupne_code_4_coming_soon():
    v = {**vstupne(), "40205": {"no": 4}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    # Not yet on sale: sold_out stays None, no ticket_url, status scheduled
    assert kafka.sold_out is None
    assert kafka.ticket_url is None
    assert kafka.status == "scheduled"


def test_vstupne_code_5_cancelled():
    v = {**vstupne(), "40205": {"no": 5}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.status == "cancelled"


def test_vstupne_code_6_postponed_stays_scheduled():
    v = {**vstupne(), "40205": {"no": 6}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.status == "scheduled"


def test_vstupne_code_11_external_url():
    ext_url = "https://goout.net/tickets/12345"
    v = {**vstupne(), "40205": {"no": 11, "url": ext_url}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.sold_out is False
    assert kafka.ticket_url == ext_url


def test_vstupne_unknown_code_no_crash():
    v = {**vstupne(), "40205": {"no": 99}}
    events = parse(VENUE, SOURCE, fixture("akropolis_hudba.html"), v, GENRE_HUDBA)
    kafka = next(e for e in events if "KAFKA" in e.title)
    assert kafka.status == "scheduled"
    assert kafka.sold_out is None


# ── pagination ────────────────────────────────────────────────────────────────

def test_akropolis_pagination_fetches_all_pages():
    from pipeline.fetch import Fetcher

    base_url = "https://palacakropolis.cz/work/33298?genre=1&no=62&page_id=38637"
    pages = {
        base_url: fixture("akropolis_hudba.html"),
        base_url + "&plg_33527_page=2": fixture("akropolis_hudba_p2.html"),
    }

    class _DictFetcher(Fetcher):
        def get(self, url, http_timeout=30):
            return pages[url]

    from pipeline.adapters.html_akropolis import _fetch_genre
    import datetime as _dt
    today = _dt.date.today()
    events = _fetch_genre(
        VENUE, SOURCE, GENRE_HUDBA, _DictFetcher(),
        vstupne(),
        today - _dt.timedelta(days=1),
        today + _dt.timedelta(days=180),
    )
    titles = [e.title for e in events]
    assert any("KAFKA" in t for t in titles), "page 1 event missing"
    assert any("PAGE TWO" in t for t in titles), "page 2 event missing"
