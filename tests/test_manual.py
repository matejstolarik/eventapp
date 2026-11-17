"""Task 060 parts 4 and 6: data/manual.json."""

import json

import pipeline.enrich_ai as E
from pipeline import manual as M

SP = "https://open.spotify.com/artist/" + "A" * 22
SP2 = "https://open.spotify.com/artist/" + "B" * 22
TODAY = "2026-11-17"


def _manual(tmp_path, data):
    p = tmp_path / "manual.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return M.load(p)


def _ev(**kw):
    ev = {"id": "fuchs2-2026-11-26-latin-core", "venue_id": "fuchs2", "date": "2026-11-26",
          "title": "LATIN CORE THURSDAYS: Addly Muff ☆ Gatita Tribalera", "formats": ["concert"],
          "genres": ["rock"], "classification": {"method": "llm", "confidence": 0.6},
          "status": "cancelled", "sold_out": True, "price_text": "200 Kč", "start_time": "22:00",
          "sources": [{"url": "https://www.fuchs2.cz/event-details/x"}]}
    ev.update(kw)
    return ev


def test_load_validates(tmp_path):
    m = _manual(tmp_path, {
        "artist_links": {"Good": SP, "Bad": "https://open.spotify.com/search/bad"},
        "events": {"x": {"start_time": "25:00", "status": "scheduled", "price_text": "300 Kč"}},
        "series": [{"venue_id": "fuchs2", "formats": ["party"]},
                   {"venue_id": "fuchs2", "title_contains": "latin core", "formats": ["party"]}]})
    assert m["artist_links"] == {"Good": SP}
    assert m["events"] == {"x": {"price_text": "300 Kč"}}          # status not allowed
    assert len(m["series"]) == 1


def test_missing_file_is_empty(tmp_path):
    assert M.load(tmp_path / "none.json") == {"artist_links": {}, "events": {}, "series": []}


def test_series_and_event_win_over_ai_and_source_but_not_status(tmp_path):
    m = _manual(tmp_path, {
        "series": [{"venue_id": "fuchs2", "title_contains": "Latin Core Thursdays",
                    "formats": ["party"], "genres": ["reggaeton", "latin"],
                    "descriptions": {"cs": "Čtvrteční latinská party."}}],
        "events": {"fuchs2-2026-11-26-latin-core": {"price_text": "250 Kč", "start_time": "23:00"}}})
    out, st = M.apply_manual([_ev(), _ev(id="other", venue_id="roxy")], m, TODAY)
    ev = out[0]
    assert ev["formats"] == ["party"] and ev["primary_format"] == "party"
    assert ev["genres"] == ["reggaeton", "latin"]
    assert ev["classification"]["method"] == "manual"
    assert ev["price_text"] == "250 Kč" and ev["start_time"] == "23:00"
    assert ev["descriptions"]["cs"].startswith("Čtvrteční")
    assert ev["status"] == "cancelled" and ev["sold_out"] is True
    assert ev["enrichment"]["price_text"] == {"by": "manual", "checked_at": TODAY}
    assert ev["enrichment"]["description"]["by"] == "manual"
    assert out[1] == _ev(id="other", venue_id="roxy")
    assert st == {"series": 1, "events": 1}
    again, _ = M.apply_manual(out, m, TODAY)
    assert again[0] == ev


def test_known_series_prompt_skips_type_and_genres(tmp_path):
    m = _manual(tmp_path, {"series": [{"venue_id": "fuchs2", "title_contains": "LATIN CORE",
                                       "formats": ["party"]}]})
    ev = M.apply_manual([_ev()], m, TODAY)[0][0]
    assert M.is_known_series(ev, m)
    assert "FIXED by manual data" in E.build_prompt(ev, {"name": "Fuchs2"}, None)
    assert "FIXED" not in E.build_prompt(_ev(), {"name": "Fuchs2"}, None)


def test_ai_does_not_override_manual_type():
    ev = {**_ev(), "classification": {"method": "manual", "confidence": 1.0},
          "formats": ["party"], "genres": ["latin"]}
    enr = {"formats": {"by": "ai_web", "source_url": "u", "confidence": 0.9},
           "genres": {"by": "ai_web", "source_url": "u"}}
    out = E.apply_enrichment(ev, enr, {"formats": ["concert"], "genres": ["rock"]})
    assert out["formats"] == ["party"] and out["genres"] == ["latin"]


def test_manual_values_not_cached_as_ai():
    enr = {"price_text": {"by": "manual"}, "start_time": {"by": "ai_web", "source_url": "u"},
           "artist_links": {"by": "ai_web"}}
    prev = {"price_text": "250 Kč", "start_time": "21:00", "artist_links": [{"spotify_url": SP}]}
    vals = E.values_from_enrichment(enr, prev)
    assert vals == {"start_time": "21:00"}


def test_spotify_links_only_from_manual(tmp_path):
    m = _manual(tmp_path, {"artist_links": {"Addly Muff": SP, "Gatita Tribalera": SP2}})
    ai_only = _ev(id="b", title="Someone", artists=["Someone"],
                  artist_links=[{"name": "Someone", "spotify_url": SP.replace("A", "C")}],
                  enrichment={"artist_links": {"by": "ai_web"}})
    with_artist = _ev(id="c", title="Night", artists=["Gátita tribalera"])
    out, st = M.apply_artist_links([_ev(), ai_only, with_artist], m, TODAY)
    assert out[0]["artist_links"] == [{"name": "Addly Muff", "spotify_url": SP},
                                      {"name": "Gatita Tribalera", "spotify_url": SP2}]
    assert "artist_links" not in out[1] and "artist_links" not in out[1]["enrichment"]
    assert out[2]["artist_links"] == [{"name": "Gatita Tribalera", "spotify_url": SP2}]
    assert out[2]["enrichment"]["artist_links"]["by"] == "manual"
    assert st == {"attached": 2, "ai_dropped": 1}


def test_title_word_is_not_a_partial_match(tmp_path):
    m = _manual(tmp_path, {"artist_links": {"Keo": SP}})
    out, _ = M.apply_artist_links([_ev(title="Keoma Live", artists=[])], m, TODAY)
    assert "artist_links" not in out[0]
    out, _ = M.apply_artist_links([_ev(title="Keo (UK)", artists=[])], m, TODAY)
    assert out[0]["artist_links"][0]["spotify_url"] == SP
