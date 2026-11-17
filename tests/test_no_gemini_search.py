"""Task 060: the daily run never calls Gemini with the google_search tool."""

import pipeline.enrich_ai as enrich_ai


def _boom(*a, **kw):
    raise AssertionError("Gemini provider must not be created in the daily run")


def test_make_provider_refuses_gemini(monkeypatch):
    monkeypatch.setenv("ENRICH_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(enrich_ai, "_Gemini2", _boom)
    provider, why = enrich_ai.make_provider()
    assert provider is None
    assert "refused" in why


def test_daily_enrichment_with_gemini_env_does_not_call_gemini(monkeypatch):
    monkeypatch.setenv("ENRICH_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(enrich_ai, "_Gemini2", _boom)
    calls = []
    monkeypatch.setattr(enrich_ai.requests, "post",
                        lambda *a, **kw: calls.append((a, kw)) or _boom())
    ev = {"id": "x-2026-11-20-a", "venue_id": "x", "title": "A", "date": "2026-11-20",
          "sources": [{"url": "https://example.org/a"}]}
    out, stats = enrich_ai.enrich_events_ai([ev], [{"id": "x"}], {}, {}, "2026-11-17")
    assert calls == []
    assert "refused" in stats["skipped"]
    assert out[0]["id"] == ev["id"]


def test_daily_workflow_has_no_gemini_provider():
    import pathlib
    wf = pathlib.Path(".github/workflows/daily.yml").read_text(encoding="utf-8")
    assert "ENRICH_PROVIDER: claude" in wf
    assert not pathlib.Path(".github/workflows/gemini-test.yml").exists()
