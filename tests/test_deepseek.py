"""Task 061: DeepSeek provider (tool calls search / fetch -> decision -> translation), no network."""

import datetime
import json

import pytest

from pipeline import deepseek as D
from pipeline import enrich_ai as E

EV_URL = "https://www.roxy.cz/events/detail/1"
EV = {"id": "e1", "venue_id": "roxy", "title": "Tinlicker", "date": "2026-12-01",
      "start_time": None, "formats": ["dj"], "genres": [], "artists": [], "price_text": None,
      "sources": [{"url": EV_URL}], "classification": {"method": "keyword"}}
OFFPEAK = lambda: datetime.datetime(2026, 11, 17, 18, 0, tzinfo=datetime.timezone.utc)  # noqa: E731

DECISION = {
    "formats": ["concert"], "primary_format": "concert", "type_confidence": 0.8,
    "type_source_url": "https://tinlicker.com", "genres": ["house", "techno"],
    "genre_facts": {"house": "tinlicker.com: melodic house duo"},
    "artists": ["Tinlicker"], "artists_source_url": "https://tinlicker.com",
    "spotify": [{"artist": "Tinlicker", "url": "https://open.spotify.com/artist/" + "A" * 22}],
    "price": "Tba", "start_time": None,
    "descriptions": {"cs": "Tinlicker je nizozemské duo."},
    "description_source_urls": ["https://tinlicker.com", "https://made-up.example/x"],
}


def _usage(hit=0, miss=100, out=20):
    return {"prompt_cache_hit_tokens": hit, "prompt_cache_miss_tokens": miss,
            "completion_tokens": out}


def _tool_call(i, name, **args):
    return {"id": f"c{i}", "type": "function",
            "function": {"name": name, "arguments": json.dumps(args)}}


def _provider(research_answers, tool_answers=None, decision=DECISION, budget=None):
    calls, tools = [], []

    def call(body):
        calls.append(body)
        if "tools" in body:
            return research_answers.pop(0)
        sys = body["messages"][0]["content"]
        if sys == E.TRANSLATE_PROMPT:
            content = json.dumps({"sk": "Tinlicker je holandské duo.", "en": "Tinlicker is a Dutch duo."})
        else:
            content = json.dumps(decision) if isinstance(decision, dict) else decision.pop(0)
        return {"choices": [{"message": {"content": content}}], "usage": _usage(50, 300, 80)}

    def tool(name, body):
        tools.append((name, body))
        if tool_answers is not None:
            return tool_answers.pop(0)
        if name == "search":
            return 200, {"results": [
                {"title": "Tinlicker", "url": "https://tinlicker.com", "summary": "melodic house duo"},
                {"title": "RA", "url": "https://ra.co/dj/tinlicker", "summary": "x"},
                {"title": "IG", "url": "https://www.instagram.com/tinlicker", "summary": "x"},
                {"title": "FB", "url": "https://www.facebook.com/events/1", "summary": "350 Kč"}]}
        return 200, {"title": "Roxy", "content": "Tinlicker live, vstupné 350 Kč"}

    p = D._DeepSeek(call=call, tool=tool, budget=budget or D.Budget(1.0), now=OFFPEAK)
    return p, calls, tools


def _msg(content="", calls=None):
    m = {"content": content}
    if calls:
        m["tool_calls"] = calls
    return {"choices": [{"message": m}], "usage": _usage()}


def test_research_tools_limits_and_blocked():
    answers = [
        _msg(calls=[_tool_call(1, "search", query="Tinlicker band"),
                    _tool_call(2, "search", query="Tinlicker Roxy"),
                    _tool_call(3, "search", query="Tinlicker live"),
                    _tool_call(4, "search", query="fourth")]),
        _msg(calls=[_tool_call(5, "fetch", url="https://ra.co/events/1"),
                    _tool_call(6, "fetch", url=EV_URL),
                    _tool_call(7, "fetch", url="https://tinlicker.com"),
                    _tool_call(8, "fetch", url="https://example.com/3")]),
        _msg("P: Tinlicker | NL duo | presents as: live act | genres: melodic house [1]"),
    ]
    p, calls, tools = _provider(answers)
    r = p.research(EV, {"name": "Roxy"})
    assert len(r["queries"]) == 3 and all(q.endswith(D.SEARCH_SUFFIX) for q in r["queries"])
    assert [n for n, _ in tools].count("search") == 3
    assert r["fetched"] == [EV_URL, "https://tinlicker.com"]          # ra.co refused, 3rd over limit
    urls = [s["url"] for s in r["sources"]]
    assert "https://www.facebook.com/events/1" in urls                 # Facebook allowed
    assert not any("ra.co" in u or "instagram" in u for u in urls)
    assert r["dropped_results"] == 6
    tool_msgs = [m for m in calls[-1]["messages"] if m["role"] == "tool"]
    assert "Search limit reached" in tool_msgs[3]["content"]
    assert "must not be used" in tool_msgs[4]["content"]
    assert "Fetch limit reached" in tool_msgs[7]["content"]
    assert r["searched"] and r["text"].startswith("P:")
    assert calls[0]["thinking"] == {"type": "disabled"} and calls[0]["model"] == "deepseek-flash"


def test_query_shortened_to_128():
    p, _, tools = _provider([_msg(calls=[_tool_call(1, "search", query="x" * 200)]), _msg("P: x")])
    p.research(EV, {})
    assert len(tools[0][1]["query"]) == 128 and tools[0][1]["query"].endswith(D.SEARCH_SUFFIX)


def test_retry_when_no_search_then_not_searched():
    p, calls, _ = _provider([_msg("from memory"), _msg("still nothing")])
    r = p.research(EV, {})
    assert r["retried"] and not r["searched"]
    assert calls[1]["messages"][-1]["content"] == D.RESEARCH_RETRY_DS


def test_run_event_rules_applied_and_cost():
    answers = [_msg(calls=[_tool_call(1, "search", query="Tinlicker")]),
               _msg("P: Tinlicker | melodic house [1]")]
    p, calls, _ = _provider(answers)
    rec = p.run_event(EV, {"name": "Roxy"}, "page text", 0)
    assert rec["searches"] == 1 and rec["fetches"] == 0
    assert rec["raw"]["descriptions"]["sk"].startswith("Tinlicker je holandské")
    # decide + translate in JSON mode
    assert all(c.get("response_format") == {"type": "json_object"} for c in calls if "tools" not in c)
    res, conv = E.process_result(EV, rec, D.MODEL, "2026-11-17", {}, lambda u: None)
    assert res["artist_links"] == []                    # Spotify never from the model
    assert res["genres"] == ["house", "techno"]         # same validation as Gemini: kept,
    assert list(res["genre_facts"]) == ["house"]        # counted as "no fact" in the test
    assert not res["price_ok"]                          # "Tba" -> no price
    assert "https://made-up.example/x" not in (res.get("description_source_urls") or [])
    # 2 research + decide + translate; offpeak prices; 1 search
    tok = sum(u["cost_usd"] for u in rec["steps"] if u["model"] == D.MODEL)
    exp = 2 * D.token_cost(0, 100, 20, False) + 2 * D.token_cost(50, 300, 80, False)
    assert tok == pytest.approx(exp)
    assert rec["cost_usd"] == pytest.approx(exp + D.TOOL_PRICE)
    assert p.budget.spent == pytest.approx(rec["cost_usd"])


def test_blank_json_retried():
    answers = [_msg(calls=[_tool_call(1, "search", query="Tinlicker")]), _msg("P: x [1]")]
    p, calls, _ = _provider(answers, decision=["   ", json.dumps(DECISION)])
    rec = p.run_event(EV, {}, None, 0)
    assert rec["raw"]["primary_format"] == "concert"
    decide = [u for u in rec["steps"] if u.get("step") == "decide"]
    assert len(decide) == 1 and decide[0]["input_tokens"] == 700     # two calls merged


def test_empty_search_not_billed_and_failed_fetch():
    answers = [_msg(calls=[_tool_call(1, "search", query="nothing"),
                           _tool_call(2, "fetch", url="https://example.com/x")]), _msg("U: nothing")]
    p, _, _ = _provider(answers, tool_answers=[(200, {"results": []}), (404, "no content")])
    r = p.research(EV, {})
    assert not [u for u in r["usage"] if u["model"] in ("search", "fetch")]
    assert r["tool_errors"] == ["fetch 404: https://example.com/x"]


def test_budget_and_402_stop():
    b = D.Budget(0.0)
    p, _, _ = _provider([_msg("x")], budget=b)
    with pytest.raises(E.ProviderStop):
        p.research(EV, {})

    p2 = D._DeepSeek(budget=D.Budget(1.0))

    def boom(path, body, timeout):
        raise E.ProviderStop("HTTP 402: Insufficient Balance")
    p2._post = boom
    with pytest.raises(E.ProviderStop):
        p2._http_chat({})


def test_peak_hours():
    utc = datetime.timezone.utc
    assert D.is_peak(datetime.datetime(2026, 11, 17, 7, 30, tzinfo=utc))       # Tue 08:30 Prague
    assert not D.is_peak(datetime.datetime(2026, 11, 17, 5, 0, tzinfo=utc))
    assert not D.is_peak(datetime.datetime(2026, 11, 21, 7, 30, tzinfo=utc))   # Saturday
    assert D.token_cost(0, 1_000_000, 0, True) == pytest.approx(0.3)
    assert D.token_cost(1_000_000, 0, 1_000_000, False) == pytest.approx(0.603)
