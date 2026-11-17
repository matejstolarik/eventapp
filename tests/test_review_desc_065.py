"""Task 065 part 3 (ai-rules F, H): the model flags needs_review -> no AI
description (cs, sk, en), for new and for cached events; price / time stay."""

import json

from pipeline import enrich_ai as E
from tests.test_enrich_ai import DESC_CS, FakeProvider, _ev, _raw, run


def test_validate_drops_description_when_model_flags_review():
    res = E.validate(_raw(needs_review=True), _ev(), None)
    assert res["descriptions"] is None
    assert res["needs_review"] is True
    assert res["price"] == "od 950 Kč" and res["start_time"] == "20:00"
    assert any("needs_review" in d for d in res["dropped"])


def test_validate_keeps_description_without_review():
    res = E.validate(_raw(needs_review=False), _ev(), None)
    assert res["descriptions"]["cs"] == DESC_CS


def test_new_event_flagged_has_no_description():
    out, _ = run([_ev()], provider=FakeProvider(raw=_raw(needs_review=True)))
    assert not out[0].get("descriptions")
    assert "description" not in out[0]["enrichment"]
    assert out[0]["enrichment"]["run"]["needs_review"] is True


def test_cached_flagged_event_loses_description():
    """REVO: Z Gumy Do Gumy was stored with needs_review and a description."""
    first, _ = run([_ev()])
    prev = json.loads(json.dumps(first[0]))
    assert prev["descriptions"]
    prev["enrichment"]["run"]["needs_review"] = True
    out, st = run([_ev()], previous={prev["id"]: prev})
    assert not out[0].get("descriptions")
    assert "description" not in out[0]["enrichment"]
    assert out[0].get("description_source") != "ai"
    assert st["descriptions_dropped_review"] == [prev["id"]]
    assert out[0]["price_text"] == "od 950 Kč"      # price stays


def test_cached_event_without_review_keeps_description():
    first, _ = run([_ev()])
    out, st = run([_ev()], previous={first[0]["id"]: first[0]})
    assert out[0]["descriptions"]["cs"] == DESC_CS
    assert st["descriptions_dropped_review"] == []

