"""Task 060 part 3: price check on presale pages, price waves."""

import pathlib

import pytest
import requests
from bs4 import BeautifulSoup

import pipeline.enrich_ai as E
from pipeline.price import parse_price

FIX = pathlib.Path(__file__).parent / "fixtures" / "goout" / "listky_js_price.html"
EV = {"id": "kasarna-karlin-2026-12-02-bad-karma-boy", "venue_id": "kasarna-karlin",
      "title": "Bad Karma Boy (album launch) + Island Mint", "artists": ["Bad Karma Boy"]}


def _text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    return soup.get_text(" ")


def _res(url, price="350 Kč"):
    return {"price": price, "price_source_url": url, "artists": ["Bad Karma Boy"]}


def test_goout_js_price_kept_unverified():
    page = _text(FIX.read_text(encoding="utf-8"))
    ok, why, verified = E.verify_price(EV, _res("https://goout.net/cs/listky/bad-karma-boy/abcd/"),
                                       fetch=lambda u: page)
    assert ok and verified is False and "JavaScript" in why


def test_goout_page_with_other_amount_dropped():
    page = "Bad Karma Boy (album launch) Vstupenky 290 Kč"
    ok, why, verified = E.verify_price(EV, _res("https://goout.net/cs/x/abcd/"), fetch=lambda u: page)
    assert not ok and "not on page" in why


def test_goout_page_with_amount_verified():
    page = "Bad Karma Boy (album launch) Vstupenky CZK 350"
    ok, why, verified = E.verify_price(EV, _res("https://goout.net/cs/x/abcd/"), fetch=lambda u: page)
    assert ok and verified is True


@pytest.mark.parametrize("host", ["https://www.smsticket.cz/vstupenky/1", "https://oazis.app/e/1",
                                  "https://www.ticketportal.cz/event/1",
                                  "https://www.ticketstream.cz/x/1"])
def test_presale_403_kept_unverified(host):
    def fetch(u):
        raise requests.HTTPError("403")
    ok, why, verified = E.verify_price(EV, _res(host), fetch=fetch)
    assert ok and verified is False


def test_venue_page_unreadable_dropped():
    def fetch(u):
        raise requests.HTTPError("403")
    ok, why, verified = E.verify_price(EV, _res("https://kasarnakarlin.cz/program/x"), fetch=fetch)
    assert not ok
    ok, why, verified = E.verify_price(EV, _res("https://kasarnakarlin.cz/program/x"),
                                       fetch=lambda u: "")
    assert not ok


def test_venue_page_without_amount_dropped():
    ok, why, _ = E.verify_price(EV, _res("https://kasarnakarlin.cz/program/x"),
                                fetch=lambda u: "Bad Karma Boy (album launch) program")
    assert not ok


def test_unverified_flag_in_enrichment():
    res = {"formats": [], "genres": [], "genre_candidates": [], "price": "350 Kč",
           "price_source_url": "https://goout.net/cs/x/abcd/", "price_verified": False,
           "start_time": None, "artists": [], "artist_links": [], "descriptions": None}
    conv = E.result_to_enrichment(res, "m", "2026-11-17", 1, True)
    assert conv["enrichment"]["price_text"]["verified"] is False
    assert conv["values"]["price_text"] == "350 Kč"


@pytest.mark.parametrize("text,lo,hi", [
    ("1. vlna 600 Kč, 2. vlna 650 Kč, 3. vlna 700 Kč", 600, 700),
    ("1. vlna 600 Kč / 2. vlna 700 Kč", 600, 700),
    ("Early bird 450 Kč, regular 550 Kč", 450, 550),
    ("early bird: 390,- | 2nd wave: 450,- | na místě 550,-", 390, 550),
    ("CZK 350", 350, 350),
])
def test_price_waves_range(text, lo, hi):
    p = parse_price(text)
    assert p["min"] == lo and p["max"] == hi and p["kind"] == "paid"


@pytest.mark.parametrize("text", ["TBA", "Tba", "bude upřesněno"])
def test_tba_is_not_a_price(text):
    assert parse_price(text) is None
