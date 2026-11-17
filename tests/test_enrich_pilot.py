"""Tests for pipeline/enrich_pilot.py (task 052) — no network, mocked Claude."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pipeline import enrich_pilot as ep


def _ev(id, venue, fmts, genres=(), desc=None, date="2026-12-01", title=None):
    return {"id": id, "venue_id": venue, "title": title or id, "date": date,
            "formats": list(fmts), "genres": list(genres), "description": desc,
            "price_text": None, "sources": [{"url": f"https://x.cz/{id}"}]}


def test_select_events_covers_required_venues_and_skips_priced_past():
    events = []
    for v in ep.REQUIRED_VENUES + ["roxy", "forum-karlin"]:
        events += [_ev(f"{v}-a", v, ["concert"]), _ev(f"{v}-b", v, ["dj", "party"], ["techno"], "x")]
    priced = _ev("priced", "roxy", ["concert"])
    priced["price_text"] = "200 Kč"
    past = _ev("past", "roxy", ["concert"], date="2026-11-01")
    cancelled = _ev("canc", "roxy", ["concert"], title="SHOW ►CANCEL")
    sel = ep.select_events(events + [priced, past, cancelled], "2026-11-17", n=20)
    ids = {e["id"] for e in sel}
    assert len(sel) == 18  # all eligible events
    assert not ids & {"priced", "past", "canc"}
    assert {e["venue_id"] for e in sel} >= set(ep.REQUIRED_VENUES)
    assert all("bez ceny" in e["pilot_reasons"] for e in sel)


def test_suspicion_reasons():
    assert ep.suspicion_reasons(_ev("a", "v", ["concert"]))  # empty genres
    assert ep.suspicion_reasons(_ev("a", "v", ["concert", "dj", "party"], ["rock"]))
    assert not ep.suspicion_reasons(_ev("a", "v", ["dj"], ["techno"], title="Techno night"))
    # new party definition (Matej 2026-11-17): every party is re-checked
    assert ep.suspicion_reasons(_ev("a", "v", ["dj", "party"], ["techno"], title="Techno night"))


def test_validate_result_rules():
    ev = _ev("e", "v", ["concert"])
    ev["start_time"] = "20:00"
    raw = {
        "formats": ["concert", "bogus"], "genres": ["rock"], "type_source_url": None,
        "type_confidence": 0.8, "artists": ["Band"],
        "spotify": [{"artist": "Band", "url": "https://open.spotify.com/artist/0123456789abcdefghijkl?si=1"},
                    {"artist": "X", "url": "https://open.spotify.com/album/0123456789abcdefghijkl"}],
        "price": "250 Kč", "price_source_url": "https://ra.co/events/1",
        "start_time": "21:00", "start_time_source_url": "https://x.cz",
        "description_cs": "Text.", "description_source_urls": [],
    }
    seen = {"https://open.spotify.com/artist/0123456789abcdefghijkl"}
    out = ep.validate_result(raw, ev, seen)
    assert out["formats"] == ["concert"]
    assert out["type_is_estimate"] is True
    assert out["price"] is None                      # ra.co source dropped
    assert out["start_time"] is None                 # event already has a time
    assert out["description_cs"] is None             # no source urls
    assert [s["url"] for s in out["spotify"]] == ["https://open.spotify.com/artist/0123456789abcdefghijkl"]
    assert any("ra.co" in d for d in out["dropped"])


def test_validate_spotify_must_be_seen():
    ev = _ev("e", "v", ["concert"])
    raw = {"formats": [], "genres": [], "type_confidence": 0, "artists": [], "price": None,
           "start_time": None, "description_cs": None,
           "spotify": [{"artist": "A", "url": "https://open.spotify.com/artist/0123456789abcdefghijkl"}]}
    assert ep.validate_result(raw, ev, set())["spotify"] == []


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test"})
def test_run_claude_parses_report_and_counts_searches():
    report = {"formats": ["concert"], "genres": ["rock"], "type_source_url": "https://x.cz/e",
              "type_confidence": 0.9, "artists": ["Band"], "price": "300 Kč",
              "price_source_url": "https://x.cz/e", "start_time": None,
              "description_cs": "Koncert kapely.", "description_source_urls": ["https://x.cz/e"]}
    resp = SimpleNamespace(
        stop_reason="tool_use",
        usage=SimpleNamespace(input_tokens=1000, output_tokens=200,
                              server_tool_use=SimpleNamespace(web_search_requests=2)),
        content=[
            SimpleNamespace(type="server_tool_use", name="web_search", input={"query": "band praha"}),
            SimpleNamespace(type="web_search_tool_result",
                            content=[SimpleNamespace(url="https://x.cz/e")]),
            SimpleNamespace(type="tool_use", name="report_enrichment", input=report),
        ],
    )
    client = MagicMock()
    client.messages.create.return_value = resp
    with patch("anthropic.Anthropic", return_value=client):
        results, totals = ep.run_claude([_ev("e", "v", ["concert"])], {}, budget=60)
    assert totals["searches"] == 2
    assert totals["cost_usd"] == round(1000 * 0.1e-6 + 200 * 0.5e-6 + 2 * 0.01, 4)
    r = results[0]["result"]
    assert r["price"] == "300 Kč" and r["description_cs"] == "Koncert kapely."
    kwargs = client.messages.create.call_args.kwargs
    ws = kwargs["tools"][0]
    assert ws["blocked_domains"] == ["ra.co"] and ws["max_uses"] == 3
