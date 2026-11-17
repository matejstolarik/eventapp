"""Task 058: Gemini two-step provider (research with search -> decision), no network."""

import json

from pipeline import enrich_ai as E

REDIRECT = "https://vertexaisearch.cloud.google.com/grounding-api-redirect/"
SPOT = "https://open.spotify.com/artist/" + "B" * 22
EV_URL = "https://www.akropolis.cz/akce/1"
EV = {"id": "e1", "venue_id": "akropolis", "title": "Spitfire Company & PAST", "date": "2026-12-01",
      "start_time": None, "formats": ["theatre"], "genres": [], "artists": [], "price_text": None,
      "sources": [{"url": EV_URL}], "classification": {"method": "keyword"}}


def _step1(queries=True):
    gm = {"groundingChunks": [{"web": {"uri": REDIRECT + "a", "title": "past.bandcamp.com"}},
                              {"web": {"uri": REDIRECT + "s", "title": "spotify.com"}},
                              {"web": {"uri": REDIRECT + "r", "title": "ra.co"}}]}
    if queries:
        gm["webSearchQueries"] = ["PAST band", "PAST spotify"]
    return {"candidates": [{"content": {"parts": [{"text": "PAST: industrial hip-hop duo."}]},
                            "groundingMetadata": gm}],
            "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 50}}


DECISION = {
    "formats": ["concert", "theatre"], "primary_format": "concert", "type_confidence": 0.8,
    "type_source_url": "https://past.bandcamp.com", "genres": ["hip-hop", "industrial"],
    "genre_facts": {"industrial": "bandcamp: industrial hip-hop"},
    "artists": ["PAST", "Spitfire Company"], "artists_source_url": "https://past.bandcamp.com",
    "spotify": [{"artist": "PAST", "url": SPOT}],
    "price": None, "start_time": None,
    "descriptions": {"cs": "PAST je duo.", "sk": "PAST je duo.", "en": "PAST is a duo."},
    "description_source_urls": ["https://past.bandcamp.com", "https://made-up.example/x"],
}


def _provider(step1s):
    calls = []

    def call(body):
        calls.append(body)
        if "tools" in body:
            return step1s.pop(0)
        return {"candidates": [{"content": {"parts": [{"text": json.dumps(DECISION)}]}}],
                "usageMetadata": {"promptTokenCount": 300, "candidatesTokenCount": 80,
                                  "thoughtsTokenCount": 20}}

    targets = {REDIRECT + "a": "https://past.bandcamp.com", REDIRECT + "s": SPOT,
               REDIRECT + "r": "https://ra.co/dj/past"}
    p = E._Gemini2(model="gemini-3.6-flash", resolve=targets.get,
                   spotify_name=lambda u: "PAST", call=call)
    return p, calls


def test_two_steps_and_sources():
    p, calls = _provider([_step1()])
    rec = p.run_event(EV, {"name": "Palác Akropolis"}, "page text", 12)
    assert len(calls) == 2
    assert "tools" in calls[0] and "page text" not in json.dumps(calls[0])   # step 1 without page
    assert "tools" not in calls[1] and "page text" in json.dumps(calls[1])
    assert rec["searches"] == 2 and rec["searched"]
    assert rec["input_tokens"] == 400 and rec["output_tokens"] == 150
    urls = {s["url"] for s in rec["research"]["sources"]}
    assert urls == {"https://past.bandcamp.com", SPOT}          # ra.co dropped
    res, conv = E.process_result(EV, rec, p.model, "2026-11-17", {})
    assert res["genres"] == ["hip-hop", "industrial"]
    assert res["artist_links"] == [{"name": "PAST", "spotify_url": SPOT}]
    assert res["description_source_urls"] == ["https://past.bandcamp.com"]   # invented URL dropped
    assert conv["enrichment"]["formats"]["by"] == "ai_web"


def test_retry_then_not_searched():
    p, calls = _provider([_step1(False), _step1(False)])
    rec = p.run_event(EV, {}, None, 12)
    assert len(calls) == 3 and E.RESEARCH_RETRY in json.dumps(calls[1], ensure_ascii=False)
    assert rec["searched"] is False and rec["research"]["retried"]
    res, conv = E.process_result(EV, rec, p.model, "2026-11-17", {})
    enr = conv["enrichment"]
    assert enr["run"]["searched"] is False
    assert enr["formats"]["by"] == "ai_text"
    assert "descriptions" not in conv["values"] and "artists" not in conv["values"]


def test_retry_succeeds():
    p, calls = _provider([_step1(False), _step1(True)])
    rec = p.run_event(EV, {}, None, 12)
    assert rec["searched"] and rec["research"]["retried"] and len(calls) == 3


def test_spotify_name_must_match_artist():
    p, _ = _provider([_step1()])
    p.spotify_name = lambda u: "Past Lives"
    rec = p.run_event(EV, {}, None, 12)
    res, _ = E.process_result(EV, rec, p.model, "2026-11-17", {})
    assert res["artist_links"] == []


def test_facebook_price_not_fetched():
    ok, why = E.verify_price(EV, {"price": "200 Kč", "price_source_url": "https://www.facebook.com/events/1"},
                             fetch=lambda u: 1 / 0)
    assert not ok and "facebook" in why
