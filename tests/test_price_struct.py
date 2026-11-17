"""Task 058 part 4: structured price from real price texts (tests/fixtures/prices + events.json)."""

from pathlib import Path

import pytest

from pipeline.detail_enrich import extract_price, page_lines
from pipeline.price import parse_price

FIX = Path(__file__).parent / "fixtures" / "prices"


def P(lo, hi, cur="CZK", kind="paid"):
    return {"min": lo, "max": hi, "currency": cur, "kind": kind}


FREE = {"min": None, "max": None, "currency": None, "kind": "free"}


@pytest.mark.parametrize("name, expected", [
    ("epic-10.html", P(250, 400)),
    ("roxy-9.html", P(990, 990)),
    ("roxy-16.html", P(599, 599)),
    ("kasarna-karlin-11.html", P(100, 100)),
    ("meetfactory-2.html", P(950, None)),            # "od 950 Kč na webu pořadatele"
    ("meetfactory-18.html", P(250, 450)),
    ("citarna-unijazz-4.html", P(250, 350)),
    ("citarna-unijazz-12.html", P(300, 600)),
])
def test_price_from_real_pages(name, expected):
    text = extract_price(page_lines((FIX / name).read_text(encoding="utf-8")))
    assert parse_price(text) == expected


@pytest.mark.parametrize("text, expected", [
    # real price_text values from events.json (2026-11-17)
    ("předprodej: BASIC: 290,-kč / VIP 580,-kč | v den akce: BASIC: 350,-kč / VIP 700,-kč", P(290, 700)),
    ("2. VLNA | BASIC: 690,-kč / VIP 1280,-kč", P(690, 1280)),
    ("1. vlna 299 Kč", P(299, 299)),
    ("550 Kč v předprodeji od pátku 10. července, 11:00 / 350 Kč pro studenty s ISICem / 650 Kč na místě",
     P(350, 650)),
    ("350 Kč / 250 Kč pro studenty a občany s trvalým pobytem na Praze 5", P(250, 350)),
    ("890 Kč / VIP 3 260 Kč", P(890, 3260)),
    ("1,450.00 Kč až 4,880 Kč", P(1450, 4880)),
    ("100,- na místě v hotovosti", P(100, 100)),
    ("od 900 Kč (plus poplatky prodejců)", P(900, None)),
    ("250–599", P(250, 599, cur=None)),
    ("is 100 CZK per person. We don't take reservations, but team spots are limited", P(100, 100)),
    ("zdarma / free entry", FREE),
    ("vstup zdarma", FREE),
    ("volný", FREE),
    ("dobrovolné vstupné (benefiční)", {**FREE, "kind": "voluntary"}),
    ("zdarma, nutná rezervace", {**FREE, "kind": "free_reservation"}),
    ("20 €", P(20, 20, cur="EUR")),
    ("Vstupné: Tba", None),
    ("via FOURCE", None),
    (None, None),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected
