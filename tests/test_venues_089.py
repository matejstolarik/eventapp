"""Task 089: Karlovy Lázně, Café V Lese, Klub 007 Strahov, OX Club, Kampus
Hybernská adapters and the month limit ignored on task runs."""

import datetime
import json
import pathlib

from pipeline.adapters import html, html_kampus, html_karlovylazne, html_oxclub, jsonld
from pipeline import deepseek as D

FIX = pathlib.Path(__file__).parent / "fixtures" / "survey2"
TODAY_083 = datetime.date(2026, 11, 20)   # Karlovy Lázně fixtures (083)
TODAY = datetime.date(2026, 11, 22)       # 088 / 089 fixtures


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


def test_strategies_registered():
    for s in ("karlovylazne", "oxclub", "kampus"):
        assert s in html._STRATEGIES


def test_venues_json_entries():
    venues = {v["id"]: v for v in json.loads(
        (pathlib.Path(__file__).parent.parent / "data" / "venues.json").read_text(encoding="utf-8"))}
    for vid, strategy in (("karlovy-lazne", "karlovylazne"), ("cafe-v-lese", "mec_ajax"),
                          ("klub-007-strahov", "eventon"), ("ox-club", "oxclub"),
                          ("kampus-hybernska", "kampus")):
        v = venues[vid]
        assert v["active"] and v["image_url"] and v["description"] is None
        assert v["sources"][0]["strategy"] == strategy
    assert venues["karlovy-lazne"]["capacity"] == 1000
    assert venues["klub-007-strahov"]["capacity"] == 180
    assert venues["klub-007-strahov"]["instagram"] is None
    assert venues["cafe-v-lese"]["capacity"] is None


# ── Karlovy Lázně ─────────────────────────────────────────────────────────────

KL = {"id": "karlovy-lazne", "character": ["tourist"]}


def test_karlovy_listing_week_nights_and_nye():
    evs = html_karlovylazne.parse_listing(KL, {}, _read("karlovylazne_events.html"), TODAY_083)
    # Mon-Wed of the week are past (window starts yesterday); recurring nights kept
    assert [(e.date, e.title) for e in evs] == [
        ("2026-11-19", "Thursday Thunder"), ("2026-11-20", "5 Story Friday"),
        ("2026-11-21", "5 Story Saturday"), ("2026-11-22", "Sunday Shakedown"),
        ("2026-12-31", "NYE 2026")]
    assert evs[0].start_time == "22:00" and evs[-1].start_time == "20:00"
    assert evs[2].source["url"] == "https://www.karlovylazne.cz/udalosti/5-story-saturday"
    assert evs[2].image_url.endswith("/1920/0/saturday.jpg")
    assert all(e.price_text is None for e in evs)


def test_karlovy_detail_description_image():
    d = html_karlovylazne.parse_detail(_read("karlovylazne_detail.html"))
    assert d["description"].startswith("5 STORY SATURDAY ULTIMATE HITS FLOOR DJ 4U")
    assert d["image_url"] == "https://www.karlovylazne.cz/files/saturday.jpg"
    ev = html_karlovylazne.parse_listing(KL, {}, _read("karlovylazne_events.html"), TODAY_083)[2]
    ev = html_karlovylazne.apply_detail(ev, d)
    assert ev.ticket_url == "https://aplikace.karlovylazne.cz/en/reservation/music-club"


# ── Café V Lese (MEC with atts from the page) ─────────────────────────────────

CVL = {"url": "https://cafevlese.cz/", "ld_local_time": True}


def test_cafevlese_atts_from_page_post_body():
    atts = jsonld.mec_atts_from_page(_read("cafevlese_home.html"))
    assert atts.startswith("atts%5Blabel%5D=") and "atts%5Bskin%5D=tile" in atts
    body = jsonld.mec_post_data(atts, 2026, 12)
    assert body.startswith("action=mec_tile_load_month&mec_year=2026&mec_month=12&atts%5B")
    assert body.endswith("&apply_sf_date=0&navigator_click=true")


def test_citarna_post_unchanged():
    # Čitárna keeps the numeric skin id: same form fields as before task 089
    assert jsonld.mec_post_data({"atts[id]": "47"}, 2026, 3) == {
        "action": "mec_tile_load_month", "mec_year": "2026", "mec_month": "03",
        "atts[id]": "47", "navigator_click": "true", "apply_sf_date": "0"}


def test_cafevlese_local_time_despite_zone_and_no_price():
    month = json.loads(_read("cafevlese_mec_ajax_202612.json"))["month"]
    evs = jsonld.parse_mec_month({"id": "cafe-v-lese"}, CVL, month)
    assert len(evs) == 16
    wants = evs[0]
    assert wants.title == "The Wants (USA)" and wants.date == "2026-12-01"
    assert wants.start_time == "19:30"          # "2026-12-01T19:30:00+00:00": local part
    assert all(e.price_text is None for e in evs)   # "0 USD" ignored
    assert wants.source["url"] == "https://cafevlese.cz/events/the-wants-usa/"


def test_mec_without_local_time_flag_unchanged():
    month = json.loads(_read("cafevlese_mec_ajax_202612.json"))["month"]
    evs = jsonld.parse_mec_month({"id": "x"}, {"url": "https://cafevlese.cz/"}, month)
    assert all(e.start_time is None for e in evs)


# ── Klub 007 Strahov (EventON) ────────────────────────────────────────────────

def test_loose_iso_dates():
    assert jsonld.parse_loose_datetime("2026-12-3T19:00+1:00") == ("2026-12-03", "19:00")
    assert jsonld.parse_loose_datetime("2027-1-9T16:00+1:00") == ("2027-01-09", "16:00")
    assert jsonld.parse_loose_datetime("2026-11-24T19:00:00+01:00") == ("2026-11-24", "19:00")
    assert jsonld.parse_loose_datetime("2026-02-30T19:00") == (None, None)
    assert jsonld.parse_loose_datetime("") == (None, None)
    # the strict parser of the other sources is unchanged
    assert jsonld._parse_iso_date("2026-12-3T19:00+1:00") is None


def test_klub007_events():
    evs = jsonld.parse_eventon({"id": "klub-007-strahov"}, {"url": "https://klub007strahov.cz/"},
                               _read("klub007_home.html"), TODAY)
    assert len(evs) == 33
    dec3 = next(e for e in evs if e.date == "2026-12-03")     # "2026-12-3T19:00+1:00"
    assert dec3.title.startswith("ASTRO ZOMBIES")
    assert (dec3.start_time, dec3.end_time) == ("19:00", "22:00")
    assert dec3.source["section"] == "psychobilly"
    lak = next(e for e in evs if e.date == "2026-11-26")
    assert lak.price_text == "Vstupné 300 Kč"
    assert next(e for e in evs if e.date == "2026-11-24").price_text is None
    party = next(e for e in evs if e.date == "2026-12-04")
    assert party.end_time is None                              # 23:59 = no stated end
    assert any(e.title == "DAVE HAUSE & THE MERMAID (us)" for e in evs)   # &amp; unescaped


# ── OX Club ───────────────────────────────────────────────────────────────────

def test_oxclub_base64_xml_and_private_skipped():
    evs = html_oxclub.parse({"id": "ox-club"}, {"url": "https://www.oxclubprague.com/program"},
                            _read("oxclub_program.html"), TODAY)
    assert [e.date for e in evs] == ["2026-11-22", "2026-11-28", "2026-12-10", "2026-12-31",
                                     "2027-02-12", "2027-04-02", "2027-04-10", "2027-04-17"]
    assert not any("PRIVATE" in e.title for e in evs)
    diana = evs[0]
    assert diana.title == "Diana Arbenina"
    assert (diana.doors_time, diana.start_time) == ("19:00", "20:00")
    assert diana.source["url"] == "https://www.oxclubprague.com/shop/b1058-Diana-Arbenina.htm"
    assert diana.image_url.endswith("/mpic/1/1058/XP0-24433694.png")
    separ = evs[1]
    assert (separ.doors_time, separ.start_time, separ.end_time) == (None, "23:00", "04:30")
    maniak = evs[4]
    assert (maniak.start_time, maniak.doors_time, maniak.price_text) == (None, None, None)
    alena = evs[6]
    assert (alena.doors_time, alena.start_time) == ("18:30", "19:30")
    assert alena.price_text == "Vstupenky: Od 1 100 Kč | M-Ticket"
    assert evs[7].artists == ["DAXSON", "LAURA VAN DAM", "LUCCA", "DJ TiGi"]


def test_oxclub_no_programme_script():
    assert html_oxclub.parse({"id": "ox-club"}, {"url": "u"}, "<html></html>", TODAY) == []


# ── Kampus Hybernská ──────────────────────────────────────────────────────────

KH = {"id": "kampus-hybernska", "character": []}


def test_kampus_pagination_pages():
    p1, n1 = html_kampus.parse_listing(KH, {}, _read("kampushybernska_program.html"), TODAY)
    p2, n2 = html_kampus.parse_listing(KH, {}, _read("kampushybernska_program_p2.html"), TODAY)
    p4, n4 = html_kampus.parse_listing(KH, {}, _read("kampushybernska_program_p4.html"), TODAY)
    assert (len(p1), n1) == (20, True)
    assert (len(p2), n2) == (20, True)
    assert (len(p4), n4) == (4, False)
    # the past-events list on the same page is never taken
    assert not {e.source["url"] for e in p1} & {e.source["url"] for e in p2}
    assert all(e.date >= "2026-11-21" for e in p1 + p2 + p4)


def test_kampus_card_fields_all_categories():
    evs, _ = html_kampus.parse_listing(KH, {}, _read("kampushybernska_program.html"), TODAY)
    first = evs[0]
    assert first.date == "2026-11-23" and (first.start_time, first.end_time) == ("10:00", "12:30")
    assert first.price_text == "Zdarma" and first.free is True and first.room == "A.3 Sál"
    sewing = next(e for e in evs if "šicí dílna" in e.title)       # workshops are kept
    assert sewing.price_text == "300 Kč" and sewing.free is None


def test_kampus_detail():
    d = html_kampus.parse_detail(_read("kampushybernska_detail.html"))
    assert d["date"] == "2026-12-04" and d["category"] == "Hudba"
    assert d["price_text"] == "250 Kč v předprodeji, 300 Kč na místě"
    assert d["image_url"].endswith("_PIO%20copy.jpg")
    assert d["description"].startswith("Pražský improvizační orchestr (PIO)")


def test_kampus_guess_year():
    assert html_kampus.guess_date("23.11.", TODAY) == datetime.date(2026, 11, 23)
    assert html_kampus.guess_date("8.1.", TODAY) == datetime.date(2027, 1, 8)
    assert html_kampus.guess_date("4.12.2026", TODAY) == datetime.date(2026, 12, 4)


# ── month limit ignored on task runs ──────────────────────────────────────────

def test_month_cap_ignored_only_on_task_runs(monkeypatch):
    st = {"ai_cost": {"month": "2026-11", "usd": 4.9}}
    monkeypatch.setenv("DEEPSEEK_RUN_BUDGET_USD", "1.00")
    monkeypatch.setenv("DEEPSEEK_IGNORE_MONTHLY_CAP", "true")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    b = D.daily_budget(st, "2026-11-22")
    assert b.limit == 1.00 and b.month_cap_ignored
    # scheduled daily run: the month limit always applies
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    b = D.daily_budget(st, "2026-11-22")
    assert b.limit == 0.1 and not b.month_cap_ignored
    # manual run without the input: month limit applies
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("DEEPSEEK_IGNORE_MONTHLY_CAP", "false")
    assert D.daily_budget(st, "2026-11-22").limit == 0.1
