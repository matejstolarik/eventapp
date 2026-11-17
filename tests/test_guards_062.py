"""Task 062 part 1: guards on AI results (genres, price, '!', venue in description)."""

from pipeline.ai_guards import genre_supported, price_supported, venue_mentions
from pipeline.ai_rules import DECIDE_PROMPT, RULES_TYPE, TRANSLATE_PROMPT
from pipeline.enrich_ai import description_problems, validate
from pipeline.genres import load_aliases

AL = load_aliases()
EV = {"id": "x", "title": "Test", "venue_id": "v", "date": "2026-11-20",
      "sources": [{"url": "https://venue.cz/e"}]}
URL = "https://venue.cz/e"


def _raw(genres, facts, **kw):
    r = {"formats": ["concert"], "primary_format": "concert", "genres": genres,
         "genre_facts": facts, "type_source_url": URL}
    r.update(kw)
    return r


def _ok(g, quote, research=None):
    return genre_supported(g, quote, research if research is not None else quote, AL)[0]


# --- cases from report 061 -------------------------------------------------

def test_warhaus_indie_electronic_dropped_pop_kept():
    facts = "P: Warhaus | genres: seductive pop, noir-ish pop, club jazz; Gqom-inspired rhythms"
    raw = _raw(["pop", "indie", "electronic"], {
        "pop": "Warhaus is described as seductive, noir-ish pop.",
        "indie": "alternative pop with MIA Best Alternative award.",
        "electronic": "New album The Donkey uses Gqom-inspired rhythms and grime elements."})
    out = validate(raw, EV, None, AL, None, facts)
    assert out["genres"] == ["pop"]
    assert any("genre indie" in d for d in out["dropped"])
    assert any("genre electronic" in d for d in out["dropped"])


def test_student_wednesday_electronic_parent_dropped():
    facts = "E: hudební styl: MAINSTREAM, EDM"
    raw = _raw(["edm", "electronic"], {"edm": "hudební styl: MAINSTREAM, EDM",
                                      "electronic": "hudební styl: MAINSTREAM, EDM"})
    assert validate(raw, EV, None, AL, None, facts)["genres"] == ["edm"]


def test_electronic_dance_music_is_no_support_for_electronic():
    assert _ok("edm", "plays electronic dance music")
    assert not _ok("electronic", "plays electronic dance music")


def test_slvl_hard_techno_is_not_hardcore():
    q = "SLVL plays hard techno"
    assert not _ok("hardcore", q)
    assert _ok("techno", q)
    assert _ok("hardcore", "Dutch hardcore and gabber DJ")


def test_allt_death_core_is_not_death_metal():
    assert not _ok("death-metal", "Švédská death-core banda ALLT")
    assert _ok("metalcore", "progressive metalcore band")
    assert not _ok("metal", "progressive metalcore band")
    assert not _ok("metal", "Swedish death metal band")


def test_keo_alt_rock_is_not_indie():
    assert not _ok("indie", "London band playing alt-rock")
    assert _ok("rock", "London band playing alt-rock")


def test_amphibian_atmospheric_listening_is_not_ambient():
    q = "Radio Labe takeover is described as calm, atmospheric listening area"
    assert not _ok("ambient", q)
    assert not _ok("ambient", "klidné, atmosférické poslouchání")
    assert _ok("ambient", "ambient techno set")      # approved alias -> techno, ambient
    assert _ok("techno", "ambient techno set")


def test_subgenre_gives_no_support_to_parent():
    assert not _ok("house", "tech house DJ")
    assert _ok("tech-house", "tech house DJ")
    assert not _ok("pop", "dream pop duo")
    assert not _ok("punk", "post-punk band")


def test_aliases_spelling_and_czech_forms():
    assert _ok("hip-hop", "Czech rapper, rap and trap")
    assert _ok("drum-and-bass", "Drum & bass night")
    assert _ok("drum-and-bass", "d&b DJ")
    assert _ok("rock", "česká rocková kapela")
    assert _ok("electronic", "elektronická hudba")
    assert _ok("rnb", "R&B singer")


def test_quote_must_also_be_in_research():
    ok, why = genre_supported("jazz", "jazz trio", "P: X | genres: soul", AL)
    assert not ok and "research" in why
    ok, why = genre_supported("jazz", None, "jazz", AL)
    assert not ok and "quote" in why


def test_candidate_of_dropped_genre_removed():
    raw = _raw(["death-metal"], {"death-metal": "death-core banda"})
    out = validate(raw, EV, None, AL, None, "death-core banda")
    assert out["genres"] == []
    assert all(c["maps_to"] != "death-metal" for c in out["genre_candidates"])


# --- price without support --------------------------------------------------

def test_price_tba_dropped():
    assert not price_supported("Tba", "price Tba")[0]
    assert not price_supported("bude upřesněno", "bude upřesněno")[0]


def test_price_needs_amount_in_research_or_page():
    assert price_supported("990 Kč", "E: price 990 CZK including fees")[0]
    assert price_supported("1 290 Kč", "price 1290 Kč")[0]
    ok, why = price_supported("400 Kč", "E: price not found")
    assert not ok and "400" in why
    assert price_supported("zdarma", "vstup zdarma")[0]
    assert not price_supported("zdarma", "U: price not found")[0]   # Text-appeal


def test_validate_drops_price_without_support():
    raw = _raw([], {}, price="350 Kč", price_source_url=URL)
    out = validate(raw, EV, None, AL, None, "U: price not found")
    assert out["price"] is None
    assert any("price '350 Kč'" in d for d in out["dropped"])


# --- exclamation mark in a name ---------------------------------------------

def test_exclamation_in_band_name_is_ok():
    text = "FIRE! je švédské trio saxofonisty Matse Gustafssona."
    assert description_problems(text, ["FIRE! (SE)", "FIRE!"]) == []
    assert description_problems("Skvělý večer!", ["FIRE!"]) == ["exclamation mark"]
    assert description_problems(text) == ["exclamation mark"]


def test_validate_keeps_description_with_fire():
    ev = dict(EV, title="FIRE! (SE)")
    raw = _raw([], {}, descriptions={"cs": "FIRE! je švédské trio.", "sk": "FIRE! je švédske trio.",
                                    "en": "FIRE! is a Swedish trio."},
               description_source_urls=[URL])
    assert validate(raw, ev, None, AL)["descriptions"]["cs"].startswith("FIRE!")


# --- venue / hall in the description -> review --------------------------------

def test_description_with_venue_goes_to_review():
    venue = {"id": "forum-karlin", "name": "Forum Karlín"}
    raw = _raw([], {}, descriptions={"cs": "Koncert se koná ve Velkém sále."},
               description_source_urls=[URL])
    out = validate(raw, EV, None, AL, None, None, venue)
    assert out["descriptions"]                      # not dropped
    assert out["needs_review"] and out["review"]
    raw["descriptions"] = {"cs": "V pražském Foru Karlín vystoupí poprvé."}
    assert validate(raw, EV, None, AL, None, None, venue)["needs_review"]
    raw["descriptions"] = {"cs": "Švédská kapela hraje metalcore."}
    assert not validate(raw, EV, None, AL, None, None, venue)["needs_review"]


def test_venue_mentions_unijazz():
    assert venue_mentions("Akce se koná v Čítárně Unijazz.", {"name": "Unijazz"})


# --- prompts ------------------------------------------------------------------

def test_prompts_follow_ai_rules_062():
    assert "Tinlicker" in RULES_TYPE and "7." in RULES_TYPE and '"DJ set"' in RULES_TYPE
    assert "about 5 sentences" in DECIDE_PROMPT
    assert "organiser" in DECIDE_PROMPT and "hall" in DECIDE_PROMPT
    assert "grammatical gender" in TRANSLATE_PROMPT and "number" in TRANSLATE_PROMPT
