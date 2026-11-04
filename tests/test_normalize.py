"""Tests for pipeline/normalize.py — postponed/moved event handling."""

import pytest

from pipeline.normalize import normalize_event, _detect_postponed_moved
from pipeline.models import RawEvent


def _raw(title, venue_id="fuchs2", date="2026-12-01", status="scheduled"):
    return RawEvent(
        venue_id=venue_id,
        title=title,
        date=date,
        start_time="22:00",
        end_time=None,
        source={"type": "jsonld", "url": "https://fuchs2.cz/events/x", "external_id": None},
        status=status,
    )


# ---------------------------------------------------------------------------
# _detect_postponed_moved
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("title,expected_action,expected_clean", [
    ("POSTPONED: deBasement", "postponed", "deBasement"),
    ("POSTPONED: deBasement", "postponed", "deBasement"),
    ("postponed: Some Show", "postponed", "Some Show"),
    ("ODLOŽENO: Noční Jízda", "postponed", "Noční Jízda"),
    ("ODLOŽENÁ: Párty", "postponed", "Párty"),
    ("ODLOŽENO - Blackout", "postponed", "Blackout"),
    ("ODLOŽENO Blackout", "postponed", "Blackout"),
    ("PŘESUNUTO DO MEETFACTORY / CONCERT", "moved", "PŘESUNUTO DO MEETFACTORY / CONCERT"),
    ("PRESUNUTO DO MeetFactory / Show", "moved", "PRESUNUTO DO MeetFactory / Show"),
    ("MOVED TO Forum Karlín / BAND", "moved", "MOVED TO Forum Karlín / BAND"),
    ("Normal Event Title", "", "Normal Event Title"),
    ("F2 LIVE: Band Name", "", "F2 LIVE: Band Name"),
])
def test_detect_postponed_moved(title, expected_action, expected_clean):
    action, clean = _detect_postponed_moved(title)
    assert action == expected_action
    assert clean == expected_clean


# ---------------------------------------------------------------------------
# normalize_event — postponed
# ---------------------------------------------------------------------------

def test_postponed_strips_prefix_and_sets_status():
    raw = _raw("POSTPONED: deBasement")
    ev = normalize_event(raw)
    assert ev is not None
    assert ev["title"] == "deBasement"
    assert ev["status"] == "postponed"


def test_postponed_id_uses_clean_title():
    raw = _raw("POSTPONED: deBasement", date="2026-12-01")
    ev = normalize_event(raw)
    assert "postponed" not in ev["id"]
    assert ev["id"].startswith("fuchs2-2026-12-01-debasement")


def test_postponed_id_matches_clean_event():
    """Event later re-announced without prefix gets the same ID."""
    postponed_raw = _raw("POSTPONED: deBasement", date="2026-12-01")
    clean_raw = _raw("deBasement", date="2026-12-01")
    ev_postponed = normalize_event(postponed_raw)
    ev_clean = normalize_event(clean_raw)
    assert ev_postponed["id"] == ev_clean["id"]


def test_postponed_cz_odlozeno():
    raw = _raw("ODLOŽENO: Blackout Show")
    ev = normalize_event(raw)
    assert ev["title"] == "Blackout Show"
    assert ev["status"] == "postponed"


# ---------------------------------------------------------------------------
# normalize_event — moved to another venue
# ---------------------------------------------------------------------------

def test_moved_returns_none(caplog):
    import logging
    raw = _raw("PŘESUNUTO DO MEETFACTORY / CONCERT")
    with caplog.at_level(logging.INFO, logger="pipeline.normalize"):
        ev = normalize_event(raw)
    assert ev is None
    assert "PŘESUNUTO DO MEETFACTORY" in caplog.text


def test_moved_en_returns_none():
    raw = _raw("MOVED TO Forum Karlín / BAND SHOW")
    ev = normalize_event(raw)
    assert ev is None


# ---------------------------------------------------------------------------
# normalize_event — normal event unaffected
# ---------------------------------------------------------------------------

def test_normal_event_unchanged():
    raw = _raw("LATIN CORE THURSDAYS")
    ev = normalize_event(raw)
    assert ev is not None
    assert ev["title"] == "LATIN CORE THURSDAYS"
    assert ev["status"] == "scheduled"


def test_adapter_cancelled_still_works():
    raw = _raw("ZRUŠENO: Concert", status="cancelled")
    ev = normalize_event(raw)
    # "ZRUŠENO" is not in the postponed/moved patterns, status comes from adapter
    assert ev is not None
    assert ev["status"] == "cancelled"
    assert ev["title"] == "ZRUŠENO: Concert"
