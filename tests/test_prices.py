"""Task 054: price_text / start_time from venue event pages (detail_enrich)."""

from pathlib import Path

import pytest

from pipeline.detail_enrich import (
    enrich_missing_details, extract_price, extract_start_time, page_lines,
)

FIX = Path(__file__).parent / "fixtures" / "prices"
FUCHS2 = Path(__file__).parent / "fixtures" / "fuchs2_event_latin_core_min.html"


def _lines(name):
    return page_lines((FIX / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name, price, start", [
    ("cross-club-0.html", None, "20:00"),        # "Vstupné: via FOURCE" is not a price
    ("cross-club-1.html", None, "19:00"),        # "Vstupné: Tba"
    ("epic-10.html", "BASIC: 250,-kč | VIP: 400,-kč", None),
    ("roxy-9.html", "990 Kč", None),             # "Základní vstupné 990 Kč"
    ("roxy-16.html", "599 Kč", None),            # "Vstupenky: 599 Kč"
    ("kasarna-karlin-11.html", "100 CZK", None),  # "Admission: 100 CZK"
    ("meetfactory-2.html", "Vstupenky od 950 Kč na webu pořadatele", None),
    ("meetfactory-18.html",
     "250 Kč limitovaná první vlna předprodeje / 350 Kč druhá vlna předprodeje"
     " / 250 Kč pro studenty s ISICem / 450 Kč na místě", None),
    ("citarna-unijazz-4.html", "Vstupné v předprodeji 250 Kč / 350 Kč na místě", None),
    ("citarna-unijazz-12.html", "300 Kč /400 Kč /500 Kč /600 Kč", None),
])
def test_price_and_time_from_real_pages(name, price, start):
    lines = _lines(name)
    assert extract_price(lines) == price
    assert extract_start_time(lines) == start


def test_no_price_on_fuchs2_page():
    lines = page_lines(FUCHS2.read_text(encoding="utf-8"))
    assert extract_price(lines) is None


def test_free_entry_keeps_label():
    assert extract_price(["Vstupné: zdarma / free entry"]) == "Vstupné zdarma / free entry"


def test_prose_and_grant_amounts_are_not_prices():
    lines = [
        "Pro držitele ISIC karty vstup do půlnoci GRATIS!",
        "Web je podporován grantem hl. m. Prahy ve výši 2.000.000 Kč",
        "Vstupenky",          # menu item
        "Program",
    ]
    assert extract_price(lines) is None


class _Resp:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_enrich_fills_price_and_time_and_records_check(monkeypatch):
    html = (FIX / "cross-club-0.html").read_text(encoding="utf-8").replace(
        "via FOURCE", "zdarma")
    calls = []
    monkeypatch.setattr("pipeline.detail_enrich.requests.get",
                        lambda url, **kw: calls.append(url) or _Resp(html))
    monkeypatch.setattr("pipeline.detail_enrich._robots_allowed", lambda url: True)
    monkeypatch.setattr("pipeline.detail_enrich._rate_limit", lambda url: None)
    ev = {"id": "c1", "venue_id": "cross-club", "title": "UP TONE w/ MARATHON",
          "sources": [{"url": "https://www.crossclub.cz/cs/program/8698-up-tone-w-marathon/"}],
          "description": "x" * 50, "image_url": "https://x/img.jpg",
          "price_text": None, "start_time": None}
    venues = [{"id": "cross-club", "sources": [{"type": "rss", "url": "https://www.crossclub.cz/cs/rss/program/"}]}]
    state, texts = {}, {}
    out, stats = enrich_missing_details([ev], {}, venues, check_prices=True,
                                        state=state, today="2026-11-17", page_texts=texts)
    assert out[0]["price_text"] == "Vstupné zdarma"
    assert out[0]["start_time"] == "20:00"
    assert state["detail_checked"]["c1"] == "2026-11-17"
    assert "UP TONE" in texts["c1"]
    assert stats["price_found"] == 1 and stats["time_found"] == 1

    # checked recently, price still missing -> no new fetch
    ev2 = dict(ev, price_text=None)
    state["detail_checked"]["c1"] = "2026-11-15"
    enrich_missing_details([dict(ev2, start_time="20:00")], {}, venues, check_prices=True,
                           state=state, today="2026-11-17")
    assert len(calls) == 1


def test_price_from_previous_run_is_reused_but_not_ai_price():
    venues = [{"id": "epic", "sources": [{"type": "html", "url": "https://www.epicprague.com/program"}]}]
    url = "https://www.epicprague.com/program/2075/almost-weekend"
    ev = {"id": "e1", "venue_id": "epic", "title": "A", "sources": [{"url": url}],
          "description": "d" * 20, "image_url": "i", "price_text": None}
    prev = {"e1": dict(ev, price_text="BASIC: 250,-kč")}
    out, _ = enrich_missing_details([ev], prev, venues, check_prices=True,
                                    state={"detail_checked": {"e1": "2026-11-16"}}, today="2026-11-17")
    assert out[0]["price_text"] == "BASIC: 250,-kč"
    prev_ai = {"e1": dict(ev, price_text="300 Kč",
                          enrichment={"price_text": {"by": "ai_web", "source_url": url}})}
    out, _ = enrich_missing_details([ev], prev_ai, venues, check_prices=True,
                                    state={"detail_checked": {"e1": "2026-11-16"}}, today="2026-11-17")
    assert out[0]["price_text"] is None
