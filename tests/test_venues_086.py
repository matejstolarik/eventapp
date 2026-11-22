"""Task 086: Duplex, SaSaZu, Sportovní hala Fortuna, KCP, Futurum adapters
and the "new only from later runs" rule (pipeline.first_load)."""

import datetime
import json
import pathlib

from pipeline.adapters import (api, html, html_fortuna, html_futurum, html_kcp, html_lucerna,
                               html_sasazu)
from pipeline import first_load

FIX = pathlib.Path(__file__).parent / "fixtures" / "survey2"
TODAY = datetime.date(2026, 11, 20)      # day the 083 fixtures were saved
TODAY2 = datetime.date(2026, 11, 22)     # day the 086 fixtures were saved


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


def test_strategies_registered():
    for s in ("sasazu", "fortuna", "kcp", "futurum"):
        assert s in html._STRATEGIES


# ── Duplex ─────────────────────────────────────────────────────────────────────

DPX = {"id": "duplex", "character": ["commercial"]}


def _duplex():
    return api.parse_duplex(DPX, {"venue_url": "https://www.duplex.cz"},
                            _read("duplex_agent_events.json"), TODAY)


def test_duplex_boat_party_and_private_excluded():
    evs = _duplex()
    raw = json.loads(_read("duplex_agent_events.json"))["events"]
    boats = [e for e in raw if "BOAT PARTY" in e["title"].upper()]
    assert len(raw) == 50 and len(boats) == 16
    assert len(evs) == 50 - 16 - 1            # 1 x "Private Event"
    assert not any("boat" in e.title.lower() or "private" in e.title.lower() for e in evs)


def test_duplex_local_time_from_offset_and_title_date_removed():
    evs = _duplex()
    fm = next(e for e in evs if e.date == "2026-11-20")
    assert fm.title == "FRIDAY MADNESS"          # " – 20.11.2026" dropped
    assert fm.start_time == "22:00"              # 2026-11-20T22:00:00+01:00
    assert fm.end_time == "05:00"
    assert fm.source["url"].startswith("https://www.duplex.cz/duplex-events/")


def test_duplex_price_in_eur_as_given_and_recurring_nights_kept():
    evs = _duplex()
    fm = next(e for e in evs if e.date == "2026-11-20")
    assert fm.price_text == "15–60 EUR"
    vv = next(e for e in evs if "Vini Vici" in e.title)
    assert vv.price_text == "35–100 EUR"
    assert vv.image_url.endswith("VINIVICI_2026_11_WIDE-scaled.jpg")
    assert vv.description
    assert sum(1 for e in evs if e.title == "MAGIC MONDAY") >= 4


# ── SaSaZu ─────────────────────────────────────────────────────────────────────

SZ = {"id": "sasazu", "character": []}


def test_sasazu_payload_entries():
    evs = html_sasazu.parse_listing(SZ, {}, _read("sasazu_kalendar.html"), TODAY)
    assert len(evs) == 23
    first = evs[0]
    assert (first.date, first.title) == ("2026-11-21", "Portugal. The Man (USA)")
    assert first.start_time is None                       # no time on the site
    assert first.source["url"] == ("https://www.sasazu-club.com/akce/"
                                   "85fb896b-001e-4d11-ab91-a3ae6b5b1b1c")
    # "$1c" reference resolved to the text row
    assert first.description.startswith("Portugal. The Man se proslavili")


def test_sasazu_detail_image_and_tickets():
    d = html_sasazu.parse_detail(_read("sasazu_detail.html"))
    assert d["image_url"].startswith("https://qglmzuvgrznvopdyfmie.supabase.co/")
    assert d["ticket_url"] == "https://www.ticketportal.cz/event/Polyphia"


# ── Sportovní hala Fortuna ─────────────────────────────────────────────────────

def test_fortuna_listing_from_calendar_script():
    items = html_fortuna.parse_listing(_read("fortuna_kalendar.html"), TODAY)
    titles = [i["title"] for i in items]
    assert "MANOWAR" in titles and "PLACEBO" not in titles      # past dropped
    assert items[0]["url"].startswith("https://www.sportovnihalafortuna.cz/kalendar-akci/")


def test_fortuna_detail_time_price():
    d = html_fortuna.parse_detail(_read("fortuna_detail.html"))
    assert (d["date"], d["time"]) == ("2027-01-21", "20:00")
    assert d["price_text"] == "od 1550,- Kč do 2.950,- Kč"
    assert d["image_url"].endswith("/data/j/m/1920x600.jpg")


def test_fortuna_sport_excluded(monkeypatch):
    pages = {
        "https://www.sportovnihalafortuna.cz/kalendar-akci": _read("fortuna_kalendar.html"),
        "https://www.sportovnihalafortuna.cz/kalendar-akci/manowar": _read("fortuna_detail.html"),
        "https://www.sportovnihalafortuna.cz/kalendar-akci/hsu-bitva-o-prahu-iv-semifinale":
            _read("fortuna_detail_sport.html"),
    }

    class F:
        def get(self, url):
            return pages.get(url, "<main></main>")

    class D(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2026, 11, 19)

    monkeypatch.setattr(html_fortuna, "make_fetcher", lambda cfg: F())
    monkeypatch.setattr(html_fortuna.datetime, "date", D)
    evs = html_fortuna.fetch({"id": "sportovni-hala-fortuna"},
                             {"url": "https://www.sportovnihalafortuna.cz/kalendar-akci",
                              "detail_cache": {}})
    titles = [e.title for e in evs]
    assert not any(t.startswith("HSU") for t in titles)
    mano = next(e for e in evs if e.title == "MANOWAR")
    assert mano.start_time == "20:00" and mano.price_text


def test_fortuna_sport_rule():
    hsu = html_fortuna.parse_detail(_read("fortuna_detail_sport.html"))
    assert html_fortuna.is_sport("HSU: Bitva o Prahu IV. – Semifinále", hsu)
    assert html_fortuna.is_sport("Concert", hsu)              # "sportovní akce" in text
    assert not html_fortuna.is_sport("MANOWAR", html_fortuna.parse_detail(_read("fortuna_detail.html")))
    assert not html_fortuna.is_sport("Boombox tour", {})


# ── KCP ────────────────────────────────────────────────────────────────────────

KCP_SRC = {"url": "https://www.praguecc.cz/cs/prehled-akci/kultura"}


def _kcp(name="kcp_kultura.html", today=TODAY):
    return html_kcp.parse_listing({"id": "kongresove-centrum-praha"}, KCP_SRC, _read(name), today)


def test_kcp_monte_cristo_one_event_per_listed_date():
    mc = [e for e in _kcp() if e.title == "Monte Cristo"]
    assert len(mc) == 30
    by_date = {e.date: e.start_time for e in mc}
    assert by_date["2026-12-04"] is None          # premiere, no time in the text
    assert by_date["2026-12-05"] == "14:00"       # "od 14:00 a 19:30" -> first show
    assert by_date["2026-12-18"] == "19:30"
    assert by_date["2027-03-29"] == "14:00"


def test_kcp_range_without_listed_dates_first_day_only():
    evs = _kcp()
    korn = [e for e in evs if e.title.startswith("Jiří Korn")]
    assert [(e.date, e.start_time) for e in korn] == [("2026-12-28", None)]


def test_kcp_next_year_cards_and_no_time_without_text():
    evs = _kcp("kcp_kultura_20261122.html", TODAY2)
    jc = next(e for e in evs if e.title == "Jimmy Carr: Laughs Funny")
    assert jc.date == "2027-02-24" and jc.start_time is None
    assert jc.ticket_url and jc.image_url.endswith("25505_cs.png")
    assert jc.source["url"] == KCP_SRC["url"]
    assert not jc.description.startswith(":")


# ── Futurum ────────────────────────────────────────────────────────────────────

FUT = {"id": "futurum-music-bar", "character": []}


def _fut():
    return html_futurum.parse_listing(FUT, {}, _read("futurum_program.html"), TODAY2)


def test_futurum_listing_doors_sold_out_moved_skipped():
    evs = _fut()
    assert len(evs) == 39                          # 40 cards, 1 moved to Lucerna
    assert not any("Poletíme" in e.title for e in evs)
    mw = evs[0]
    assert (mw.date, mw.title, mw.doors_time, mw.start_time) == \
        ("2026-11-22", "MOON WALKER / US", "18:30", None)
    wg = next(e for e in evs if e.title.startswith("WESGHOST"))
    assert wg.title == "WESGHOST / US" and wg.sold_out is True
    assert all(e.source["url"].startswith("https://futurum.musicbar.cz/program/") for e in evs)


def test_futurum_detail_doors_start_price():
    d = html_futurum.parse_detail(_read("futurum_detail.html"))
    assert (d["doors"], d["start"]) == ("18:30", "19:30")
    assert d["price_text"] == "předprodej 550 Kč na webu obscure.cz, na místě 650 Kč"
    assert d["ticket_url"] == "https://obscure.cz/cs/tickets/detail/id/1038"
    ev = html_futurum.apply_detail(_fut()[0], d)
    assert (ev.doors_time, ev.start_time) == ("18:30", "19:30")


def test_futurum_and_lucerna_do_not_mix():
    # the lucerna strategy finds nothing on the Futurum page and vice versa
    assert html_lucerna.parse_listing({"id": "x"}, {}, _read("futurum_program.html"), TODAY2) == []
    assert html_futurum.parse_listing(FUT, {}, _read("lucernamusicbar_program.html"), TODAY) == []


# ── "New" only from later runs (part 9) ────────────────────────────────────────

def _ev(vid, seen):
    return {"id": f"{vid}-{seen}", "venue_id": vid, "first_seen": seen}


def test_first_load_bootstrap_and_new_venue():
    previous = {e["id"]: e for e in [_ev("roxy", "2026-11-20"),
                                     _ev("lucerna-music-bar", "2026-11-21")]}
    state = {}
    events = [_ev("roxy", "2026-11-22"), _ev("duplex", "2026-11-22")]
    fl = first_load.update(state, events, previous, "2026-11-22")
    assert fl["roxy"] is None                        # loaded before the rule
    assert fl["lucerna-music-bar"] == "2026-11-21"   # 085 venues retroactively
    assert fl["jazz-republic"] == "2026-11-21"
    assert fl["duplex"] == "2026-11-22"              # first load today
    assert state[first_load.STATE_KEY] is fl
    # next day: kept, a venue that failed so far is recorded on its first success
    fl2 = first_load.update(state, [_ev("duplex", "2026-11-23"), _ev("sasazu", "2026-11-23")],
                            previous, "2026-11-23")
    assert fl2["duplex"] == "2026-11-22" and fl2["sasazu"] == "2026-11-23"


def test_first_load_is_new():
    today = "2026-11-23"
    assert not first_load.is_new(_ev("duplex", "2026-11-22"), "2026-11-22", today)
    assert first_load.is_new(_ev("duplex", "2026-11-23"), "2026-11-22", today)
    assert first_load.is_new(_ev("roxy", "2026-11-20"), None, today)
    assert not first_load.is_new(_ev("roxy", "2026-11-16"), None, today)
