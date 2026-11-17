"""Task 062 part 2: DeepSeek in the daily run -- budget, provider choice, and
nothing is lost when the API stops (HTTP 401/402, budget, no key)."""

import json

from pipeline import deepseek as D
from pipeline import enrich_ai as E
from pipeline.classify_ai import classify_events_ai
from pipeline.enrich_ai import ProviderStop

from tests.test_enrich_ai import FakeProvider, _ev, run

TODAY = "2026-11-17"


# --- budget -------------------------------------------------------------------

def test_daily_budget_run_and_month(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_RUN_BUDGET_USD", raising=False)
    assert D.daily_budget({}, TODAY).limit == 0.30
    st = {"ai_cost": {"month": "2026-11", "usd": 2.9, "runs": 20}}
    assert D.daily_budget(st, TODAY).limit == 0.1                 # 3 $ month cap
    st = {"ai_cost": {"month": "2026-11", "usd": 3.2}}
    assert D.daily_budget(st, TODAY).limit == 0.0
    st = {"ai_cost": {"month": "2026-10", "usd": 3.0}}
    assert D.daily_budget(st, TODAY).limit == 0.30                # new month
    monkeypatch.setenv("DEEPSEEK_RUN_BUDGET_USD", "1.40")          # recompute input
    assert D.daily_budget({}, TODAY).limit == 1.40


def test_record_spend_sums_runs():
    st = {}
    b = D.Budget(0.3)
    b.add(0.12)
    assert D.record_spend(st, TODAY, b) == {"month": "2026-11", "usd": 0.12, "runs": 1}
    b2 = D.Budget(0.3)
    b2.add(0.05)
    assert D.record_spend(st, TODAY, b2)["usd"] == 0.17
    assert D.record_spend(st, "2026-12-01", D.Budget(0.3)) == {"month": "2026-12", "usd": 0.0,
                                                               "runs": 1}


def test_exhausted_budget_stops_before_any_call():
    calls = []
    prov = D._DeepSeek(call=lambda body: calls.append(body), tool=lambda n, b: (200, {}),
                       budget=D.Budget(0.0))
    try:
        prov.research({"id": "x", "title": "T", "venue_id": "v", "date": TODAY, "sources": []}, {})
        raise AssertionError("no stop")
    except ProviderStop:
        pass
    assert calls == []


# --- provider choice ------------------------------------------------------------

def test_make_provider_deepseek(monkeypatch):
    monkeypatch.setenv("ENRICH_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    prov, why = E.make_provider(D.Budget(0.3))
    assert prov is None and "DEEPSEEK_API_KEY" in why
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    assert E.make_provider(None)[0] is None                       # no state -> no budget
    prov, why = E.make_provider(D.Budget(0.3))
    assert prov.name == "deepseek" and why is None                # no Claude key needed
    assert prov.monthly_search_limit == D.MONTHLY_SEARCH_LIMIT


def test_workflow_uses_deepseek_for_both():
    text = open(".github/workflows/daily.yml", encoding="utf-8").read()
    assert "ENRICH_PROVIDER: deepseek" in text
    assert "DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}" in text
    assert "ENRICH_FROM_RESEARCH: ${{ inputs.reenrich_from_research }}" in text
    assert "cron: '17 4 * * *'" in text            # 04:17 UTC, off-peak (01-04, 06-10 UTC)
    assert not D.is_peak(__import__("datetime").datetime(2026, 11, 17, 4, 17))


# --- nothing lost on stop ---------------------------------------------------------

class StopProvider(FakeProvider):
    def run(self, prompt, max_uses):
        raise ProviderStop("HTTP 402: Insufficient Balance")


def test_forced_rerun_402_keeps_previous_ai_values(monkeypatch):
    first, _ = run([_ev()])
    assert first[0]["genres"] and first[0]["descriptions"]
    prev = {first[0]["id"]: first[0]}
    monkeypatch.setenv("ENRICH_FORCE_IDS", first[0]["id"])
    out, st = run([_ev()], previous=prev, provider=StopProvider())
    assert any("stopped" in w for w in st["warnings"])
    assert st["kept_previous"] == 1
    for k in ("genres", "descriptions", "price_text", "formats", "start_time"):
        assert out[0][k] == first[0][k], k
    # Spotify links from AI are never carried over from the cache (task 060)
    assert {k: v for k, v in first[0]["enrichment"].items() if k != "artist_links"} \
        == out[0]["enrichment"]


def test_force_days_reruns_window(monkeypatch):
    first, _ = run([_ev()])
    prev = {first[0]["id"]: first[0]}
    prov = FakeProvider()
    monkeypatch.setenv("ENRICH_FORCE_DAYS", "60")
    run([_ev(), _ev(id="later", date="2027-03-01")], previous=prev, provider=prov)
    assert len(prov.calls) == 1                     # cached event re-run; later one outside window


def _cls_ev(i, title, genres=None):
    return {"id": i, "title": title, "venue_id": "v", "formats": [], "genres": [],
            "primary_format": None, "sources": []}


PREV = [{"id": "e1", "title": "TECHNO NIGHT", "formats": ["dj"], "primary_format": "dj",
         "genres": ["techno"], "classification": {"method": "llm", "confidence": 0.8}}]


def test_classify_without_key_keeps_cached_genres(monkeypatch):
    for k in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    for prov in ("claude", "deepseek"):
        monkeypatch.setenv("ENRICH_PROVIDER", prov)
        out, st = classify_events_ai([_cls_ev("e1", "TECHNO NIGHT")], [], PREV)
        assert st["skipped"] and st["cache_hits"] == 1
        assert out[0]["genres"] == ["techno"] and out[0]["primary_format"] == "dj"


def test_classify_deepseek_json_mode_and_stop(monkeypatch):
    monkeypatch.setenv("ENRICH_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    bodies = []

    def call(body):
        bodies.append(body)
        ans = {"classifications": [{"event_index": 0, "formats": ["concert"],
                                    "primary_format": "concert", "genres": ["rock"],
                                    "confidence": 0.9}]}
        return {"choices": [{"message": {"content": json.dumps(ans)}}],
                "usage": {"prompt_tokens": 1000, "prompt_cache_hit_tokens": 0,
                          "completion_tokens": 100}}

    monkeypatch.setattr(D._DeepSeek, "_http_chat", lambda self, body: call(body))
    budget = D.Budget(0.3)
    out, st = classify_events_ai([_cls_ev("e2", "ROCK BAND")], [], [], budget=budget)
    assert out[0]["formats"] == ["concert"] and out[0]["genres"] == ["rock"]
    assert bodies[0]["response_format"] == {"type": "json_object"}
    assert st["provider"] == "deepseek" and budget.spent > 0
    # HTTP 402 -> stop, cached results stay, run continues
    monkeypatch.setattr(D._DeepSeek, "_http_chat",
                        lambda self, body: (_ for _ in ()).throw(ProviderStop("HTTP 402")))
    out, st = classify_events_ai([_cls_ev("e1", "TECHNO NIGHT"), _cls_ev("e3", "X")], [], PREV,
                                 budget=D.Budget(0.3))
    assert st["stopped"] and out[0]["genres"] == ["techno"]
