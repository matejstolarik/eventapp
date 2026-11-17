"""Tests for pipeline/enrich_ai.py (task 054) — mock provider, no network."""

import pytest

from pipeline import enrich_ai as E

TODAY = "2026-11-17"
URL = "https://www.meetfactory.cz/cs/program/detail/pragokoncert-allt-avralize-bite-down"
DESC_CS = ("Švédská kapela Allt hraje progresivní metalcore. Letos vydala album Ataraxia. "
           "Večer otevřou Avralize a Bite Down.")


def _ev(**kw):
    ev = {"id": "mf-1", "venue_id": "meetfactory", "title": "Pragokoncert: Allt + Avralize",
          "date": "2026-11-19", "start_time": None, "formats": ["concert"], "genres": [],
          "artists": [], "price_text": None, "free": None, "description": "Puvodni popis.",
          "description_source": "source", "sources": [{"url": URL}],
          "classification": {"method": "llm", "confidence": 0.6}}
    ev.update(kw)
    return ev


def _raw(**kw):
    raw = {"formats": ["concert"], "primary_format": "concert", "party_reason": None,
           "type_source_url": URL, "type_confidence": 0.9, "genres": ["metal"],
           "genre_candidates": [{"raw": "Metalcore", "kind": "music", "maps_to": "metal"}],
           "artists": ["Allt", "Avralize"], "artists_source_url": URL,
           "spotify": [{"artist": "Allt", "url": "https://open.spotify.com/artist/" + "A" * 22 + "?si=x"}],
           "price": "od 950 Kč", "price_source_url": URL,
           "start_time": "20:00", "start_time_source_url": URL,
           "descriptions": {"cs": DESC_CS, "sk": "Švédska kapela Allt.", "en": "Swedish band Allt."},
           "description_source_urls": [URL],
           # task 062: every genre needs a quote with its name
           "genre_facts": {"metal": "Swedish metal band", "metalcore": "plays metalcore",
                           "death-metal": "death metal", "techno": "ambient techno DJ",
                           "ambient": "ambient techno DJ", "hip-hop": "Czech hip-hop and rap",
                           "physical-theatre": "physical theatre company"}}
    raw.update(kw)
    return raw


class FakeProvider:
    name, model, prices = "claude", "claude-haiku-5-5", (0.1e-6, 0.5e-6, 0.01)

    def __init__(self, raw=None, searches=1, fail=False):
        self.raw, self.searches, self.fail, self.calls = raw or _raw(), searches, fail, []

    def run(self, prompt, max_uses):
        self.calls.append((prompt, max_uses))
        if self.fail:
            raise RuntimeError("boom")
        return {"searches": self.searches, "input_tokens": 1000, "output_tokens": 100,
                "seen_urls": ["https://open.spotify.com/artist/" + "A" * 22], "raw": self.raw}


PAGE = "Pragokoncert: Allt + Avralize + Bite Down ... Vstupenky: od 950 Kč na webu pořadatele"


def run(events, previous=None, state=None, provider=None, page=PAGE):
    state = {} if state is None else state
    return E.enrich_events_ai(events, [{"id": "meetfactory", "name": "MeetFactory"}],
                              previous or {}, state, TODAY, provider=provider or FakeProvider(),
                              price_fetch=lambda url: page)


# ── validation ──────────────────────────────────────────────────────────────

def test_validate_rules():
    raw = _raw(price_source_url="https://ra.co/events/1", start_time_source_url=None,
               formats=["dj", "party"], primary_format="party", party_reason=None,
               spotify=[{"artist": "X", "url": "https://open.spotify.com/artist/" + "B" * 22}])
    res = E.validate(raw, _ev(), seen_urls=set())
    assert res["price"] is None and res["start_time"] is None
    assert res["formats"] == ["dj"] and res["primary_format"] is None   # party without reason
    assert res["artist_links"] == []                                    # not in search results
    assert any("ra.co" in d or "source_url" in d for d in res["dropped"])


def test_validate_genres_and_candidates():
    """Task 058: order kept, subgenres on the list stay, no parent genre added,
    unknown names are candidates, only aliases / spelling variants map."""
    res = E.validate(_raw(genres=["metalcore", "Death metal", "deep house"],
                          genre_candidates=[{"raw": "Psytrance", "kind": "music", "maps_to": "trance"}]),
                     _ev(), None)
    assert res["genres"] == ["metalcore", "death-metal"]
    assert {"raw": "deep house", "kind": "music", "maps_to": None} in res["genre_candidates"]
    assert {"raw": "psytrance", "kind": "music", "maps_to": None} in res["genre_candidates"]
    # approved alias maps it, list target keeps the main genre first
    res = E.validate(_raw(genres=["ambient techno", "rap"], genre_candidates=[]), _ev(), None,
                     aliases={"ambient techno": ["techno", "ambient"], "rap": "hip-hop"})
    assert res["genres"] == ["techno", "ambient", "hip-hop"]
    assert {"raw": "rap", "kind": "music", "maps_to": "hip-hop"} in res["genre_candidates"]


def test_stage_genre_physical_theatre():
    res = E.validate(_raw(formats=["theatre"], primary_format="theatre", genres=["Physical theatre"],
                          genre_candidates=[]), _ev(formats=["theatre"]), None)
    assert res["genres"] == ["physical-theatre"]
    res = E.validate(_raw(formats=["theatre"], primary_format="theatre",
                          genres=["physical theatre", "hip-hop"], genre_candidates=[]),
                     _ev(formats=["theatre"]), None)
    assert res["genres"] == ["physical-theatre", "hip-hop"]


def test_film_genres_list_is_empty_so_all_are_candidates():
    res = E.validate(_raw(formats=["film"], primary_format="film", genres=["documentary"],
                          genre_candidates=[]), _ev(formats=["film"]), None)
    assert res["genres"] == []
    assert res["genre_candidates"] == [{"raw": "documentary", "kind": "film", "maps_to": None}]


@pytest.mark.parametrize("text", [
    "Skvělý koncert, nezmeškejte!", "Legendární kapela přijede.", "Koncert 🎸 v Praze."])
def test_description_style_is_enforced(text):
    res = E.validate(_raw(descriptions={"cs": text, "sk": "x", "en": "y"}), _ev(), None)
    assert res["descriptions"] is None


def test_price_on_page():
    ev = _ev()
    assert E.price_on_page(PAGE, "od 950 Kč", ev, [])[0]
    assert not E.price_on_page(PAGE, "400 Kč", ev, [])[0]
    assert not E.price_on_page("Vstupné 950 Kč, jiná akce", "950 Kč", ev, [])[0]
    assert E.price_on_page("ALLT live, vstup zdarma", "zdarma", ev, ["Allt"])[0]
    assert E.price_on_page("Allt 1 280 Kč", "1280 Kč", ev, ["Allt"])[0]
    # task 058: decimals and dates are not amounts
    assert E.price_on_page("Allt vstupenky 1 490 Kč", "1490.00 Kč", ev, ["Allt"])[0]
    assert E.price_on_page("Allt: 500 Kč / 600 Kč", "do 31. 12. 2026 500 Kč / do 7. 4. 2027 600 Kč",
                           ev, ["Allt"])[0]


# ── main entry ──────────────────────────────────────────────────────────────

def test_enrich_fills_empty_fields_with_provenance():
    out, st = run([_ev()])
    ev = out[0]
    assert ev["price_text"] == "od 950 Kč" and ev["start_time"] == "20:00"
    assert ev["artists"] == ["Allt", "Avralize"]
    assert ev["artist_links"] == [{"name": "Allt", "spotify_url": "https://open.spotify.com/artist/" + "A" * 22}]
    assert ev["descriptions"]["cs"] == DESC_CS
    assert ev["description"] == "Puvodni popis." and ev["description_source"] == "source"
    assert ev["classification"]["method"] == "llm+web"
    assert ev["genres"] == ["metal", "metalcore"]
    enr = ev["enrichment"]
    assert enr["run"]["checked_at"] == TODAY
    assert enr["price_text"] == {"by": "ai_web", "model": "claude-haiku-5-5",
                                 "checked_at": TODAY, "source_url": URL}
    assert enr["description"]["source_urls"] == [URL]
    assert st["price"] == 1 and st["spotify"] == 1 and st["searches"] == 1


def test_description_used_when_source_has_none():
    out, _ = run([_ev(description=None, description_source=None)])
    assert out[0]["description"] == DESC_CS and out[0]["description_source"] == "ai"


def test_source_values_win():
    out, _ = run([_ev(price_text="250 Kč", start_time="19:00",
                      classification={"method": "source", "confidence": 1.0}, genres=["rock"])])
    ev = out[0]
    assert ev["price_text"] == "250 Kč" and ev["start_time"] == "19:00"
    assert ev["formats"] == ["concert"] and ev["genres"] == ["rock"]
    for field in ("price_text", "start_time", "genres"):
        assert field not in ev["enrichment"]
    # task 063 (B7): the AI type wins over the venue category
    assert "formats" in ev["enrichment"] and ev["primary_format"] == "concert"
    assert ev["classification"]["method"] in ("llm", "llm+web")


def test_unconfirmed_price_is_dropped():
    out, st = run([_ev()], page="Úplně jiná stránka, 400 Kč")
    assert out[0]["price_text"] is None
    assert "price_text" not in out[0]["enrichment"]
    assert st["prices_dropped"] == 1


def test_cache_same_title_no_api_and_values_kept():
    first, _ = run([_ev()])
    prev = {first[0]["id"]: first[0]}
    prov = FakeProvider()
    out, st = run([_ev()], previous=prev, provider=prov)
    assert prov.calls == [] and st["cached"] == 1
    assert out[0]["price_text"] == "od 950 Kč" and out[0]["descriptions"]["cs"] == DESC_CS
    # title changed -> new request
    prov = FakeProvider()
    run([_ev(title="Allt (new title)")], previous=prev, provider=prov)
    assert len(prov.calls) == 1


def test_cached_value_replaced_by_later_source_value():
    first, _ = run([_ev()])
    out, _ = run([_ev(price_text="1 000 Kč")], previous={first[0]["id"]: first[0]})
    assert out[0]["price_text"] == "1 000 Kč"
    assert "price_text" not in out[0]["enrichment"]


def test_window_and_monthly_limit():
    far = _ev(id="far", date="2027-03-01")
    state = {"ai_searches": {"month": "2026-11", "count": E.MONTHLY_SEARCH_LIMIT - 1}}
    prov = FakeProvider()
    evs = [far, _ev(id="a"), _ev(id="b", date="2026-11-20")]
    out, st = run(evs, state=state, provider=prov)
    assert st["window"] == 2
    assert len(prov.calls) == 1 and prov.calls[0][1] == 1     # only 1 search left
    assert st["skipped_limit"] == 1
    assert state["ai_searches"]["count"] == E.MONTHLY_SEARCH_LIMIT
    assert any("limit" in w for w in st["warnings"])
    assert "enrichment" not in out[0]


def test_new_month_resets_counter():
    state = {"ai_searches": {"month": "2026-10", "count": 400}}
    _, st = run([_ev()], state=state)
    assert state["ai_searches"] == {"month": "2026-11", "count": 1}


def test_provider_errors_do_not_stop():
    out, st = run([_ev(id=f"e{i}") for i in range(3)], provider=FakeProvider(fail=True))
    assert st["errors"] == 3 and len(out) == 3
    assert all("enrichment" not in e for e in out)


def test_no_state_means_no_searches():
    out, st = E.enrich_events_ai([_ev()], [], {}, None, TODAY, provider=FakeProvider())
    assert st["skipped"] == "state unavailable" and "enrichment" not in out[0]


def test_genre_tables_threshold():
    evs = [{"id": f"e{i}", "enrichment": {"genre_candidates": [
        {"raw": "psytrance", "kind": "music", "maps_to": None},
        {"raw": "metalcore", "kind": "music", "maps_to": "metal"}]}} for i in range(3)]
    evs.append({"id": "x", "enrichment": {"genre_candidates": [
        {"raw": "chiptune", "kind": "music", "maps_to": None}]}})
    aliases, proposals = E.genre_tables(evs)
    assert aliases == {"metalcore": "metal"}
    assert [p["name"] for p in proposals] == ["psytrance"]
    assert proposals[0]["count"] == 3 and proposals[0]["kind"] == "music"


def test_forced_ids_ignore_cache(monkeypatch):
    first, _ = run([_ev()])
    monkeypatch.setenv("ENRICH_FORCE_IDS", "mf-1, other")
    prov = FakeProvider()
    run([_ev()], previous={first[0]["id"]: first[0]}, provider=prov)
    assert len(prov.calls) == 1
