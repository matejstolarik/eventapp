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
        if body["systemInstruction"]["parts"][0]["text"] == E.TRANSLATE_PROMPT:
            return {"candidates": [{"content": {"parts": [{"text": json.dumps(
                {"sk": "PAST je duo (sk).", "en": "PAST is a duo."})}]}}],
                    "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 10}}
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
    assert len(calls) == 3                       # research, decision, translation
    assert "tools" in calls[0] and "page text" not in json.dumps(calls[0])   # step 1 without page
    assert "tools" not in calls[1] and "page text" in json.dumps(calls[1])
    assert calls[0]["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "low"}
    assert calls[1]["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "medium"}
    assert calls[2]["contents"][0]["parts"][0]["text"] == "PAST je duo."   # only cs translated
    assert rec["searches"] == 2 and rec["searched"]
    assert rec["input_tokens"] == 410 and rec["output_tokens"] == 160
    assert rec["raw"]["descriptions"] == {"cs": "PAST je duo.", "sk": "PAST je duo (sk).",
                                          "en": "PAST is a duo."}
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
    assert len(calls) == 4 and E.RESEARCH_RETRY in json.dumps(calls[1], ensure_ascii=False)
    assert rec["searched"] is False and rec["research"]["retried"]
    res, conv = E.process_result(EV, rec, p.model, "2026-11-17", {})
    enr = conv["enrichment"]
    assert enr["run"]["searched"] is False
    assert enr["formats"]["by"] == "ai_text"
    assert "descriptions" not in conv["values"] and "artists" not in conv["values"]


def test_retry_succeeds():
    p, calls = _provider([_step1(False), _step1(True)])
    rec = p.run_event(EV, {}, None, 12)
    assert rec["searched"] and rec["research"]["retried"] and len(calls) == 4


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


KWORB = "https://kworb.net/spotify/artist/" + "K" * 22 + "_songs.html"
SPOT_K = "https://open.spotify.com/artist/" + "K" * 22


def _kworb_provider(page_name):
    p, calls = _provider([_step1()])
    targets = {REDIRECT + "a": "https://past.bandcamp.com", REDIRECT + "s": KWORB,
               REDIRECT + "r": "https://ra.co/dj/past"}
    p.resolve = targets.get
    got = []
    p.spotify_name = lambda u: got.append(u) or page_name
    return p, got


def test_kworb_id_verified_and_stored():
    p, got = _kworb_provider("Past")          # case-insensitive match with "PAST"
    rec = p.run_event(EV, {}, None, 12)
    assert got == [SPOT_K]                    # one GET of the Spotify page, none of kworb
    res, _ = E.process_result(EV, rec, p.model, "2026-11-17", {})
    assert {"name": "Past", "spotify_url": SPOT_K} in res["artist_links"]
    assert res["kworb"][0]["status"] == "ok"


def test_kworb_rejected_on_name_or_http():
    for name in ("Someone Else", None):
        p, _ = _kworb_provider(name)
        rec = p.run_event(EV, {}, None, 12)
        res, _ = E.process_result(EV, rec, p.model, "2026-11-17", {})
        assert all(link["spotify_url"] != SPOT_K for link in res["artist_links"])
        assert res["kworb"][0]["status"].startswith("rejected")


def test_from_stored_research_without_search(monkeypatch, tmp_path):
    from pipeline import research_store as R
    p, calls = _provider([_step1()])
    store: dict = {}
    ev = dict(EV, date="2026-11-20")
    E.enrich_events_ai([ev], [], {}, {}, "2026-11-17", provider=p,
                       price_fetch=lambda u: None, research=store)
    assert store["e1"]["facts"] == "PAST: industrial hip-hop duo."
    assert store["e1"]["queries"] == ["PAST band", "PAST spotify"]
    monkeypatch.setattr(R, "RESEARCH_DIR", tmp_path)
    monkeypatch.delenv("PREVIOUS_EVENTS_URL", raising=False)
    sizes = R.save(store, "2026-11-17")
    assert list(sizes) == ["2026-11"] and (tmp_path / "2026-11.json").exists()
    loaded = R.load("2026-11-17")
    assert loaded["e1"]["genre_facts"] == store["e1"]["genre_facts"]
    # rules changed -> step 2 again from the stored facts, no search, cache ignored
    n = len(calls)
    monkeypatch.setenv("ENRICH_FROM_RESEARCH", "all")
    prev = {"e1": dict(ev, enrichment={"run": {"model": "x"}})}
    _, st = E.enrich_events_ai([ev], [], prev, {}, "2026-11-17", provider=p,
                               price_fetch=lambda u: None, research=loaded)
    new = calls[n:]
    assert new and all("tools" not in c for c in new)
    assert st["from_research"] == 1 and st["searches"] == 0
