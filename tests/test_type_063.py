"""Task 063 part 1: the AI type wins over the venue category (docs/ai-rules.md B7).

Order: manual > AI (formats + primary_format) > source > keyword.  Genres are
unchanged: venue genres win over AI genres."""

from pipeline import enrich_ai as E
from tests.test_enrich_ai import FakeProvider, _ev, _raw, run

ROXY = "https://www.roxy.cz/events/detail/5077/tinlicker"


def _tinlicker(**kw):
    ev = _ev(id="roxy-tinlicker", venue_id="meetfactory", title="TINLICKER",
             formats=["dj"], primary_format=None, genres=[],
             classification={"method": "source", "confidence": 1.0})
    ev.update(kw)
    return ev


def _tin_raw(**kw):
    return _raw(formats=["concert", "dj"], primary_format="concert", genres=[],
                genre_candidates=[], price=None, start_time=None, **kw)


def test_tinlicker_ai_concert_beats_source_dj():
    out, _ = run([_tinlicker()], provider=FakeProvider(raw=_tin_raw()))
    ev = out[0]
    assert ev["primary_format"] == "concert"
    assert ev["formats"] == ["concert", "dj"]           # dj secondary
    assert ev["classification"]["method"] == "llm+web"
    assert "formats" in ev["enrichment"]                # cached for the next run


def test_tinlicker_cached_ai_type_kept_next_run():
    first, _ = run([_tinlicker()], provider=FakeProvider(raw=_tin_raw()))
    prov = FakeProvider()
    out, st = run([_tinlicker()], previous={first[0]["id"]: first[0]}, provider=prov)
    assert prov.calls == [] and st["cached"] == 1
    assert out[0]["primary_format"] == "concert" and out[0]["formats"] == ["concert", "dj"]


def test_manual_beats_ai():
    ev = _tinlicker(formats=["theatre"], primary_format="theatre",
                    classification={"method": "manual", "confidence": 1.0})
    out, _ = run([ev], provider=FakeProvider(raw=_tin_raw()))
    assert out[0]["formats"] == ["theatre"] and out[0]["primary_format"] == "theatre"
    assert out[0]["classification"]["method"] == "manual"
    assert "formats" not in out[0]["enrichment"]


def test_ai_without_type_keeps_source_type():
    out, _ = run([_tinlicker()], provider=FakeProvider(raw=_tin_raw() | {"formats": [],
                                                                       "primary_format": None}))
    assert out[0]["formats"] == ["dj"] and out[0]["classification"]["method"] == "source"


def test_ai_failure_keeps_source_type():
    out, _ = run([_tinlicker()], provider=FakeProvider(fail=True))
    assert out[0]["formats"] == ["dj"] and out[0]["classification"]["method"] == "source"


def test_keyword_type_replaced_by_ai():
    ev = _tinlicker(classification={"method": "keyword", "confidence": 0.9})
    out, _ = run([ev], provider=FakeProvider(raw=_tin_raw()))
    assert out[0]["primary_format"] == "concert"


def test_venue_genres_still_win_after_ai_type():
    """classify_ai already set method llm; main passes the venue-genre ids."""
    ev = _tinlicker(genres=["techno"], classification={"method": "llm", "confidence": 0.7})
    raw = _tin_raw() | {"genres": ["metal"]}
    out, _ = E.enrich_events_ai([ev], [{"id": "meetfactory", "name": "MeetFactory"}], {}, {},
                                "2026-11-17", provider=FakeProvider(raw=raw),
                                price_fetch=lambda u: "", keep_genres={ev["id"]})
    assert out[0]["genres"] == ["techno"] and out[0]["primary_format"] == "concert"


def test_classify_ai_keeps_venue_genres():
    from pipeline.classify_ai import _apply_batch_results
    ev = _tinlicker(genres=["techno"])
    _apply_batch_results([ev], [{"event_index": 0, "formats": ["concert", "dj"],
                                 "primary_format": "concert", "genres": ["house"],
                                 "confidence": 0.8}], keep={ev["id"]})
    assert ev["primary_format"] == "concert" and ev["genres"] == ["techno"]


def test_primary_from_stored_research():
    """Enriched before 063 (no AI formats stored): the stored AI primary fills
    the missing primary_format when it is one of the formats; no API call."""
    ev = _tinlicker(formats=["theatre"], enrichment={"run": {}})
    other = _tinlicker(id="x2", formats=["dj"], enrichment={"run": {}})
    research = {ev["id"]: {"primary_format": "theatre"}, "x2": {"primary_format": "concert"}}
    assert E.fill_primary_from_research([ev, other], research) == 1
    assert ev["primary_format"] == "theatre"
    assert other["primary_format"] is None      # concert not in formats -> re-decide needed


def test_classify_ai_leaves_window_source_events_to_enrich():
    from pipeline.classify_ai import _events_needing_ai
    near = _tinlicker(date="2026-11-21")
    far = _tinlicker(id="far", date="2027-06-01")   # beyond the 180-day window (task 085)
    plain = _tinlicker(id="p", date="2026-11-21", classification=None)
    ids = [e["id"] for e in _events_needing_ai([near, far, plain], "2026-11-17")]
    assert ids == ["far", "p"]
    assert len(_events_needing_ai([near, far, plain])) == 3     # no date given: all
