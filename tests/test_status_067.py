"""Task 067: cancellation / postponement / sold-out marks in all sources."""
import datetime
import json
import pathlib

import pytest

from pipeline import status_marks as sm
from pipeline.models import RawEvent
from pipeline.normalize import normalize_event

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


# ── title marks ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("title,status,sold_out,clean", [
    ("ZRUŠENO! Omah Lay", "cancelled", None, "ZRUŠENO! Omah Lay"),
    ("ZRUŠENO: Omah Lay", "cancelled", None, "ZRUŠENO: Omah Lay"),
    ("Omah Lay (zrušeno)", "cancelled", None, "Omah Lay (zrušeno)"),
    ("Omah Lay – CANCELLED", "cancelled", None, "Omah Lay – CANCELLED"),
    ("[CANCELED] Band", "cancelled", None, "[CANCELED] Band"),
    ("ODPADÁ: Kvíz", "cancelled", None, "ODPADÁ: Kvíz"),
    ("POSTPONED: deBasement", "postponed", None, "deBasement"),
    ("PŘESUNUTO / FLOA:  Bert and Friends", "postponed", None, "FLOA:  Bert and Friends"),
    ("PŘELOŽENO: Kapela", "postponed", None, "Kapela"),
    ("Kapela (odloženo)", "postponed", None, "Kapela"),
    ("PŘESUNUTO NA 12. 3.: Kapela", "rescheduled", None, "PŘESUNUTO NA 12. 3.: Kapela"),
    ("NOVÝ TERMÍN: Kapela", "rescheduled", None, "NOVÝ TERMÍN: Kapela"),
    ("VYPRODÁNO: COLORFACTORY", None, True, "VYPRODÁNO: COLORFACTORY"),
    ("Band (SOLD OUT)", None, True, "Band (SOLD OUT)"),
    ("VYPRODÁNO: ZRUŠENO: X", "cancelled", True, "VYPRODÁNO: ZRUŠENO: X"),
])
def test_title_marks(title, status, sold_out, clean):
    m = sm.title_marks(title)
    assert m["status"] == status
    assert m["sold_out"] == sold_out
    assert m["title"] == clean


@pytest.mark.parametrize("title", [
    "SPITFIRE COMPANY & PAST ►CANCEL",    # show name (Akropolis)
    "Postponed Dreams",                    # band name, not capitals
    "Cancelled Tour Live",
    "Nic se neruší",
    "Večer, který se neruší",
    "Odpadlíci",
    "Sold Outsiders",
    "Přesunutí hranic",
    "KŘIŽOVATKA",
])
def test_title_false_positives(title):
    m = sm.title_marks(title)
    assert m["status"] is None and m["sold_out"] is None
    assert m["title"] == title


# ── short labels ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("label,kind", [
    ("Zrušeno", "cancelled"), ("ZRUŠENO!", "cancelled"), ("Akce zrušena", "cancelled"),
    ("Koncert zrušen", "cancelled"), ("Event cancelled", "cancelled"),
    ("Zrušeno / Cancelled", "cancelled"), ("Odpadá", "cancelled"),
    ("Přeloženo ►", "postponed"), ("POSTPONED", "postponed"), ("Odloženo", "postponed"),
    ("Vyprodáno", "sold_out"), ("SOLD OUT", "sold_out"),
])
def test_label_kind(label, kind):
    assert sm.label_kind(label)[0] == kind


@pytest.mark.parametrize("label", [
    "nic se neruší", "Koncert je zrušen kvůli nemoci zpěváka",
    "Po zrušeném turné se kapela vrací s novou deskou.", "hudba", "EN friendly",
    "Zrušeno / vyprodáno", None, "",
])
def test_label_not_a_mark(label):
    assert sm.label_kind(label)[0] == ""


# ── schema.org ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("value,expected", [
    ("https://schema.org/EventCancelled", "cancelled"),
    ("EventCancelled", "cancelled"),
    ("https://schema.org/EventPostponed", "postponed"),
    ("https://schema.org/EventRescheduled", "rescheduled"),
    ("https://schema.org/EventScheduled", None),
    ("Eventscheduled", None),
    (None, None),
])
def test_ld_status(value, expected):
    assert sm.ld_status(value) == expected


def test_jsonld_event_status_postponed_and_rescheduled():
    from pipeline.adapters.jsonld import _event_status
    assert _event_status("https://schema.org/EventCancelled") == "cancelled"
    assert _event_status("https://schema.org/EventPostponed") == "postponed"
    assert _event_status("https://schema.org/EventRescheduled") == "scheduled"


def test_ld_sold_out():
    assert sm.ld_sold_out({"availability": "https://schema.org/SoldOut"}) is True
    assert sm.ld_sold_out([{"availability": "InStock"}, {"availability": "SoldOut"}]) is True
    # InStock is a CMS default, not "tickets on sale"
    assert sm.ld_sold_out({"availability": "https://schema.org/InStock"}) is None
    assert sm.ld_sold_out(None) is None


# ── event page ────────────────────────────────────────────────────────────────

def test_page_status_near_title():
    lines = ["Program", "Kapela X | Cross Club", "Kapela X", "ZRUŠENO", "20. 11. 2026",
             "Popis večera, nic se neruší."]
    assert sm.page_status(lines, "Kapela X")["status"] == "cancelled"


def test_page_status_ignores_other_event_far_below():
    lines = ["Kapela X", "20. 11. 2026", "Vstupné: 200 Kč"] + ["text"] * 30 + \
            ["Další akce", "Kapela Y", "ZRUŠENO"]
    assert sm.page_status(lines, "Kapela X")["status"] is None


def test_page_status_ignores_sentences():
    lines = ["Kapela X", "Koncert je zrušen kvůli nemoci? Ne, nic se neruší, hrajeme."]
    assert sm.page_status(lines, "Kapela X")["status"] is None


def test_page_status_jsonld():
    ld = [{"@type": "MusicEvent", "eventStatus": "https://schema.org/EventPostponed"}]
    assert sm.page_status([], "Kapela X", ld)["status"] == "postponed"


def test_page_status_without_title_uses_only_metadata():
    assert sm.page_status(["ZRUŠENO"], "Kapela X")["status"] is None


# ── normalize ─────────────────────────────────────────────────────────────────

def _raw(title, **kw):
    return RawEvent(venue_id="roxy", title=title, date="2026-11-20", start_time=None,
                    end_time=None, source={"type": "html", "url": "u"}, **kw)


def test_normalize_title_sold_out_keeps_title():
    ev = normalize_event(_raw("VYPRODÁNO: COLORFACTORY"))
    assert ev["sold_out"] is True
    assert ev["title"] == "VYPRODÁNO: COLORFACTORY"
    assert ev["status"] == "scheduled"


def test_normalize_title_cancelled():
    ev = normalize_event(_raw("ZRUŠENO: Kapela"))
    assert ev["status"] == "cancelled"
    assert ev["title"] == "ZRUŠENO: Kapela"


def test_normalize_rescheduled_only_logged():
    ev = normalize_event(_raw("NOVÝ TERMÍN: Kapela"))
    assert ev["status"] == "scheduled"


def test_normalize_adapter_postponed():
    ev = normalize_event(_raw("Kapela", status="postponed"))
    assert ev["status"] == "postponed"


def test_normalize_false_positive_title():
    ev = normalize_event(_raw("SPITFIRE COMPANY & PAST ►CANCEL", sold_out=True))
    assert ev["status"] == "scheduled"


# ── adapters ──────────────────────────────────────────────────────────────────

def test_archa_canceled_class():
    from pipeline.adapters.html_archa import parse
    html = (FIXTURES / "archa_program_canceled_20261118.html").read_text(encoding="utf-8")
    events = parse({"id": "archa-plus", "character": []},
                   {"type": "html", "strategy": "archa", "url": "https://archa-plus.cz/cz/program/"},
                   html, today=datetime.date(2026, 11, 18))
    by_title = {e.title: e for e in events}
    assert by_title["Mat213 – křest desky a medley největších hitů"].status == "cancelled"
    assert by_title["Billy Barman & Dievčatá zo SĽUK-u - Vianočný koncert"].status == "scheduled"


def _strapi(items):
    return json.dumps({"data": items, "meta": {"pagination": {"page": 1, "pageCount": 1}}})


def test_bike_jesus_subtitle_and_tag():
    from pipeline.adapters.api import parse_strapi
    d = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
    items = [
        {"id": 1, "Title": "Band A", "Date": d, "Subtitle": "ZRUŠENO", "Tag": None},
        {"id": 2, "Title": "Band B", "Date": d, "Subtitle": None, "Tag": "Sold out"},
        {"id": 3, "Title": "Band C", "Date": d, "Subtitle": "Koncert je zrušen? Ne.", "Tag": None},
    ]
    evs = {e.title: e for e in parse_strapi({"id": "bike-jesus", "character": []},
                                            {"venue_url": "https://bikejesus.com"}, _strapi(items))}
    assert evs["Band A"].status == "cancelled"
    assert evs["Band B"].sold_out is True and evs["Band B"].status == "scheduled"
    assert evs["Band C"].status == "scheduled" and evs["Band C"].sold_out is None


def test_roxy_postponed_element():
    from pipeline.adapters.html_roxy import parse_listing
    html = """<a href="/events/detail/1/x" class="item" data-hashtags="#concert"><article class="wrap">
      <div class="front"><time class="date" datetime="2026-11-25 20:00">St 25/11</time>
      <p class="postponed">Přeloženo</p><h2 class="title">KAPELA</h2></div></article></a>"""
    evs = parse_listing({"id": "roxy", "character": []}, {}, html,
                        yesterday=datetime.date(2026, 11, 17), cutoff=datetime.date(2027, 5, 1))
    assert evs[0].status == "postponed"


# ── daily re-check of near events ─────────────────────────────────────────────

def _setup(monkeypatch, html, calls):
    from pipeline import detail_enrich as de

    class R:
        text = html
        def raise_for_status(self): pass

    monkeypatch.setattr(de.requests, "get", lambda *a, **k: calls.append(a) or R())
    monkeypatch.setattr(de, "_robots_allowed", lambda u: True)
    monkeypatch.setattr(de, "_rate_limit", lambda u: None)
    return de


def _ev(date, venue="kasarna-karlin", status="scheduled"):
    return {"id": "e1", "venue_id": venue, "title": "Kapela X", "date": date,
            "sources": [{"url": "https://kasarnakarlin.cz/en/program/kapela-x"}],
            "description": "popis akce dost dlouhy", "image_url": "https://x/img.jpg",
            "price_text": "200 Kč", "start_time": "20:00", "status": status}


PAGE = "<html><body><h1>Kapela X</h1><p>ZRUŠENO</p><p>Popis</p></body></html>"


def test_recheck_near_event_once_a_day(monkeypatch):
    calls = []
    de = _setup(monkeypatch, PAGE, calls)
    venues = [{"id": "kasarna-karlin", "sources": [{"url": "https://kasarnakarlin.cz/en/program"}]}]
    ev = _ev("2026-11-20")
    state = {}
    out, st = de.enrich_missing_details([ev], {"e1": ev}, venues, check_prices=True,
                                        state=state, today="2026-11-18")
    assert out[0]["status"] == "cancelled"
    assert st["status_checks"] == 1 and st["status_found"] == 1
    assert state["status_checked"]["e1"] == "2026-11-18"
    # same day: not fetched again
    de.enrich_missing_details([ev], {"e1": ev}, venues, check_prices=True,
                              state=state, today="2026-11-18")
    assert len(calls) == 1
    # next day: fetched again
    de.enrich_missing_details([ev], {"e1": ev}, venues, check_prices=True,
                              state=state, today="2026-11-19")
    assert len(calls) == 2


def test_no_recheck_far_event_or_list_venue(monkeypatch):
    calls = []
    de = _setup(monkeypatch, PAGE, calls)
    venues = [{"id": "kasarna-karlin", "sources": []}, {"id": "forum-karlin", "sources": []}]
    far = _ev("2026-11-30")
    fk = dict(_ev("2026-11-20", venue="forum-karlin"), id="e2")
    done = _ev("2026-11-20", status="cancelled")
    de.enrich_missing_details([far, fk, done], {}, venues, check_prices=True,
                              state={}, today="2026-11-18")
    assert calls == []


def test_page_status_real_archa_cancelled_page():
    # saved 2026-11-18: https://archa-plus.cz/cz/program/detail/791/...
    from pipeline.detail_enrich import page_lines
    html = (FIXTURES / "archa_detail_mat213_canceled.html").read_text(encoding="utf-8")
    m = sm.page_status(page_lines(html), "Mat213 – křest desky a medley největších hitů")
    assert m["status"] == "cancelled"


# ── task 067 part 3: broken event-page image -> listing image ────────────────

def test_broken_image_falls_back_to_listing(monkeypatch, tmp_path):
    import io
    from PIL import Image
    from pipeline import thumbs
    monkeypatch.setattr(thumbs, "EVENT_THUMB_DIR", tmp_path / "t")
    monkeypatch.setattr(thumbs, "EVENT_DETAIL_DIR", tmp_path / "d")
    buf = io.BytesIO()
    Image.new("RGB", (620, 360), "red").save(buf, "JPEG")
    good = buf.getvalue()
    calls = []

    def dl(url):
        calls.append(url)
        return b"\x89PNG\r\n\x1a\n truncated" if url.endswith(".png") else good

    monkeypatch.setattr(thumbs, "_download", dl)
    ev = {"id": "epic-x", "image_url": "https://epic/big.png"}
    used = {}
    res = thumbs.generate_event_images([ev], {"epic-x": "https://epic/list.jpg"}, used)
    assert calls == ["https://epic/big.png", "https://epic/big.png", "https://epic/list.jpg"]
    assert used == {"epic-x": "https://epic/list.jpg"}
    assert res["epic-x"] == ("img/events/epic-x.jpg", "img/events/detail/epic-x.jpg")


def test_broken_image_without_fallback_is_none(monkeypatch, tmp_path):
    from pipeline import thumbs
    monkeypatch.setattr(thumbs, "EVENT_THUMB_DIR", tmp_path / "t")
    monkeypatch.setattr(thumbs, "EVENT_DETAIL_DIR", tmp_path / "d")
    monkeypatch.setattr(thumbs, "_download", lambda url: b"broken")
    res = thumbs.generate_event_images([{"id": "e", "image_url": "https://x/a.png"}])
    assert res["e"] == (None, None)
