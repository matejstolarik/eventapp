"""Task 085: Lucerna Music Bar, O2 arena + O2 universum, Jazz Republic adapters."""

import datetime
import pathlib

import pytest

from pipeline.adapters import html_jazzrepublic, html_lucerna, html_o2, detail_cache
from pipeline import images

FIX = pathlib.Path(__file__).parent / "fixtures" / "survey2"
TODAY = datetime.date(2026, 11, 20)      # day the fixtures were saved (083)


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


# ── Lucerna Music Bar ──────────────────────────────────────────────────────────

LMB = {"id": "lucerna-music-bar", "character": ["retro"]}
LMB_SRC = {"type": "html", "strategy": "lucerna", "url": "https://musicbar.cz/cs/program/"}


@pytest.fixture(scope="module")
def lmb():
    return html_lucerna.parse_listing(LMB, LMB_SRC, _read("lucernamusicbar_program.html"), TODAY)


def test_lucerna_count_and_private_skipped(lmb):
    # 74 cards: 2 x "Soukromá akce" are not events, 4 are after today + 180 days
    assert len(lmb) == 68
    assert not any(e.title.lower() == "soukromá akce" for e in lmb)


def test_lucerna_doors_vs_start(lmb):
    thom = next(e for e in lmb if e.title == "Thom Artway")
    assert thom.date == "2026-11-22"
    assert thom.doors_time == "18:00"        # listing text = doors
    assert thom.start_time == "19:00"        # data-start = start
    currents = next(e for e in lmb if e.title.startswith("Currents"))
    assert (currents.doors_time, currents.start_time) == ("16:00", "16:40")


def test_lucerna_same_doors_and_start_only_start(lmb):
    pop = next(e for e in lmb if e.date == "2026-11-21" and e.title.startswith("Pop 80s"))
    assert pop.start_time == "22:00" and pop.doors_time is None


def test_lucerna_sold_out(lmb):
    mig = [e for e in lmb if e.title == "Mig 21"]
    assert len(mig) >= 5
    sold = [e for e in mig if e.date in ("2026-11-24", "2026-11-25", "2026-11-26")]
    assert len(sold) == 3 and all(e.sold_out is True for e in sold)
    assert all(e.sold_out is None for e in mig if e.date.startswith("2027-04"))
    currents = next(e for e in lmb if e.title.startswith("Currents"))
    assert currents.sold_out is True
    assert "VYPRODÁNO" not in currents.title
    assert currents.title == "Currents + ERRA / US, support: Caskets / UK, Aviana / SE"


def test_lucerna_year_rollover(lmb):
    keks = [e for e in lmb if e.date.startswith("2027-01")]
    assert keks, "January dates belong to 2027"
    assert all(e.date >= "2026-11-19" for e in lmb)


def test_lucerna_image_rule():
    found, url = images.detail_image("lucerna-music-bar", _read("lucernamusicbar_detail.html"),
                                     "https://musicbar.cz/cs/program/thom-artway/")
    assert found and url.startswith("https://static.goout.cloud/") and "1920x1080" in url


# ── O2 arena / O2 universum ────────────────────────────────────────────────────

ARENA = {"id": "o2-arena", "character": ["commercial"]}
ARENA_SRC = {"type": "html", "strategy": "o2", "url": "https://www.o2arena.cz/events/",
             "domain": "www.o2arena.cz"}
UNI = {"id": "o2-universum", "character": ["commercial"]}
UNI_SRC = {"type": "html", "strategy": "o2", "url": "https://www.o2universum.cz/events/",
           "domain": "www.o2universum.cz"}


def test_o2_sections_split_no_duplicates():
    arena = html_o2.parse_listing(ARENA, ARENA_SRC, _read("o2arena_events.html"), TODAY)
    uni = html_o2.parse_listing(UNI, UNI_SRC, _read("o2universum_events.html"), TODAY)
    # the same cards, read from the other venue's page
    uni_from_arena = html_o2.parse_listing(UNI, UNI_SRC, _read("o2arena_events.html"), TODAY)
    assert arena and uni
    assert all("o2arena.cz" in c["url"] for c in arena)
    assert all("o2universum.cz" in c["url"] for c in uni)
    assert not {c["url"] for c in arena} & {c["url"] for c in uni}
    assert [c["url"] for c in uni] == [c["url"] for c in uni_from_arena]


def test_o2_multiple_dates_one_event_each():
    arena = html_o2.parse_listing(ARENA, ARENA_SRC, _read("o2arena_events.html"), TODAY)
    calin = next(c for c in arena if "calin-viktor-sheen" in c["url"])
    evs = html_o2.card_events(ARENA, ARENA_SRC, calin, {})
    assert [(e.date, e.start_time) for e in evs] == [("2026-12-04", "19:00"),
                                                     ("2026-12-05", "19:00")]
    nedvedi = next(c for c in arena if "/nedvedi-27/" in c["url"])
    assert len(nedvedi["dates"]) == 2
    assert not any(c["url"].endswith("/ptk/") for c in arena)     # 1. 12. 2027: beyond 180 days


def test_o2_same_day_two_shows_one_event_and_past_dates_dropped():
    uni = html_o2.parse_listing(UNI, UNI_SRC, _read("o2universum_events.html"), TODAY)
    cech = next(c for c in uni if "cechomor" in c["url"])
    assert cech["dates"] == [(datetime.date(2026, 11, 29), "15:00")]
    witcher = next(c for c in uni if "witcher" in c["url"])
    assert witcher["dates"] == [(datetime.date(2026, 11, 25), "20:00")]   # 8.11. is past


def test_o2_range_first_day_no_time():
    uni = html_o2.parse_listing(UNI, UNI_SRC, _read("o2universum_events.html"), TODAY)
    cc = next(c for c in uni if "comic-con" in c["url"])
    assert cc["range"] and cc["dates"] == [(datetime.date(2027, 4, 16), None)]


def test_o2_detail_local_time_price_doors():
    d = html_o2.parse_detail(_read("o2arena_detail.html"))
    assert d["sport"] is False
    assert d["types"] == ["Elektronická hudba", "Hudba"]
    assert d["doors"] == ["18:30"]
    assert d["price_text"] == "1 830 – 4 690 Kč"
    assert d["ticket_url"].startswith("https://www.ticketportal.cz/")
    assert d["description"].startswith("Elektroničtí pionýři The Prodigy")
    arena = html_o2.parse_listing(ARENA, ARENA_SRC, _read("o2arena_events.html"), TODAY)
    card = next(c for c in arena if c["url"].endswith("/the-prodigy/"))
    ev = html_o2.card_events(ARENA, ARENA_SRC, card, d)[0]
    # JSON-LD says 20:00+00:00 (wrong zone); the event is 20:00 Prague time
    assert (ev.date, ev.start_time, ev.doors_time) == ("2026-11-23", "20:00", "18:30")
    assert ev.price_text == "1 830 – 4 690 Kč"


def test_o2_sport_detected():
    d = html_o2.parse_detail(_read("o2arena_detail_sport.html"))
    assert d["types"] == ["Hokej", "Sport"] and d["sport"] is True


def test_o2_multi_doors_per_date():
    d = html_o2.parse_detail(_read("o2arena_detail_multi.html"))
    assert d["doors"] == ["12:00", "17:30"] and d["sport"] is True
    card = {"url": "https://www.o2arena.cz/events/x/", "title": "X", "image_url": None,
            "range": False,
            "dates": [(datetime.date(2026, 12, 19), "13:30"), (datetime.date(2026, 12, 20), "19:00")]}
    evs = html_o2.card_events(ARENA, ARENA_SRC, card, d)
    assert [e.doors_time for e in evs] == ["12:00", "17:30"]


def test_o2_fetch_excludes_sport_and_uses_cache(monkeypatch):
    listing = _read("o2arena_events.html")
    sparta = "https://www.o2arena.cz/events/hc-sparta-praha-bili-tygri-liberec-26-01/"
    pages = {sparta: _read("o2arena_detail_sport.html")}
    calls = []

    class F:
        def get(self, url, http_timeout=30):
            calls.append(url)
            if url == ARENA_SRC["url"]:
                return listing
            return pages.get(url, _read("o2arena_detail.html"))

    monkeypatch.setattr(html_o2, "make_fetcher", lambda cfg: F())

    class D(datetime.date):
        @classmethod
        def today(cls):
            return TODAY
    monkeypatch.setattr(html_o2.datetime, "date", D)
    cache = {}
    evs = html_o2.fetch(ARENA, {**ARENA_SRC, "detail_cache": cache})
    assert not any(e.source["url"] == sparta for e in evs)
    assert any(e.source["url"].endswith("/the-prodigy/") for e in evs)
    n_first = len(calls)
    assert n_first > 10 and len(cache) == n_first - 1
    calls.clear()
    evs2 = html_o2.fetch(ARENA, {**ARENA_SRC, "detail_cache": cache})
    assert calls == [ARENA_SRC["url"]]          # details from the cache
    assert len(evs2) == len(evs)


def test_detail_cache_recheck():
    e = {"sig": "a|2026-11-20", "checked": "2026-11-13", "data": {}}
    assert detail_cache.needs_fetch(e, "a|2026-11-20", "2026-11-20")      # 7 days
    assert not detail_cache.needs_fetch(e, "a|2026-11-20", "2026-11-19")
    assert detail_cache.needs_fetch(e, "b|2026-11-20", "2026-11-19")      # changed
    assert detail_cache.needs_fetch(None, "a", "2026-11-19")


# ── Jazz Republic ──────────────────────────────────────────────────────────────

JR = {"id": "jazz-republic", "character": ["cozy"]}
JR_SRC = {"type": "html", "strategy": "jazzrepublic", "url": "https://www.jazzrepublic.cz/cz/program"}


def test_jazzrepublic_listing_date_from_url():
    evs = html_jazzrepublic.parse_listing(JR, JR_SRC, _read("jazzrepublic_program.html"), TODAY)
    assert len(evs) == 73
    first = evs[0]
    assert (first.date, first.title) == ("2026-11-20", "JAZZ CARAVAN")
    assert first.source["url"] == "https://www.jazzrepublic.cz/cz/program/2026-11-20-jazz-caravan"
    assert first.image_url == "https://www.jazzrepublic.cz/pict/product/face/3698.jpg"
    assert evs[-1].date == "2027-01-31"
    assert all(e.start_time is None for e in evs)


def test_jazzrepublic_detail_doors_price_description():
    d = html_jazzrepublic.parse_detail(_read("jazzrepublic_detail.html"))
    assert d["doors"] == "20:00"
    assert d["price_text"] == "vstup volný" and d["free"] is True
    assert d["description"].startswith("To nejlepší, co může jazzový koncert")
    evs = html_jazzrepublic.parse_listing(JR, JR_SRC, _read("jazzrepublic_program.html"), TODAY)
    ev = html_jazzrepublic.apply_detail(evs[1], d)
    assert ev.doors_time == "20:00" and ev.start_time is None


def test_jazzrepublic_no_price_when_page_silent():
    html = ('<div class="concert2"><div class="concert21"><strong>Otevřeno 20:00–24:00</strong>'
            '</div><p><span>KONCERT</span><br/>Večer standardů s hosty z Brna a Vídně.</p></div>')
    d = html_jazzrepublic.parse_detail(html)
    assert d["price_text"] is None and d["free"] is None and d["doors"] == "20:00"


# ── robots.txt fetched with our User-Agent (Cloudflare 403 to urllib UA) ─────

def test_robots_uses_requests_with_our_user_agent(monkeypatch):
    from pipeline import fetch as F

    seen = {}

    class R:
        def __init__(self, code, text=""):
            self.status_code, self.text = code, text

    def fake_get(url, headers=None, timeout=None):
        seen[url] = headers.get("User-Agent")
        if "musicbar" in url:
            return R(200, "User-agent: *\nDisallow: /wp-admin/\n")
        if "blocked" in url:
            return R(403)
        return R(404)

    monkeypatch.setattr(F.requests, "get", fake_get)
    monkeypatch.setattr(F, "_robots_cache", {})
    assert F._robots_allowed("https://musicbar.cz/cs/program/")
    assert not F._robots_allowed("https://musicbar.cz/wp-admin/x")
    assert seen["https://musicbar.cz/robots.txt"] == F.USER_AGENT
    assert not F._robots_allowed("https://blocked.example/x")       # 403 = disallow all
    assert F._robots_allowed("https://none.example/x")              # 404 = allow all
