"""Task 065: research store survives a failing Pages copy (local cache, seed)."""

import io
import json
import urllib.error

from pipeline import research_store as R


def _month(*recs):
    return {"month": "2026-11", "events": list(recs)}


def _rec(i, processed="2026-11-17", **kw):
    return {"id": i, "processed": processed, **kw}


def _setup(tmp_path, monkeypatch, pages):
    monkeypatch.setattr(R, "RESEARCH_DIR", tmp_path / "research")
    monkeypatch.setattr(R.time, "sleep", lambda s: None)
    monkeypatch.setenv("PREVIOUS_EVENTS_URL", "https://x.github.io/eventapp/events.json")
    monkeypatch.delenv("RESEARCH_SEED", raising=False)
    calls = []

    def urlopen(req, timeout=0):
        calls.append(req.full_url)
        res = pages.get(req.full_url.rsplit("/", 1)[1], 404)
        if isinstance(res, int):
            raise urllib.error.HTTPError(req.full_url, res, "x", {}, None)
        return io.BytesIO(json.dumps(res).encode())
    monkeypatch.setattr(R.urllib.request, "urlopen", urlopen)
    return calls


def test_pages_error_keeps_local_copy(tmp_path, monkeypatch, caplog):
    calls = _setup(tmp_path, monkeypatch, {"2026-11.json": 503})
    R.RESEARCH_DIR.mkdir()
    (R.RESEARCH_DIR / "2026-11.json").write_text(json.dumps(_month(_rec("a"), _rec("b"))))
    store = R.load("2026-11-18")
    assert set(store) == {"a", "b"}
    assert sum(u.endswith("2026-11.json") for u in calls) == 3          # retried
    assert "not available from Pages (HTTP 503)" in caplog.text


def test_pages_and_local_merged_later_processed_wins(tmp_path, monkeypatch, caplog):
    _setup(tmp_path, monkeypatch, {"2026-11.json": _month(_rec("a", "2026-11-18", v=2))})
    R.RESEARCH_DIR.mkdir()
    (R.RESEARCH_DIR / "2026-11.json").write_text(
        json.dumps(_month(_rec("a", "2026-11-17", v=1), _rec("b"))))
    store = R.load("2026-11-18")
    assert store["a"]["v"] == 2 and "b" in store
    assert "Pages has 1 records, local copy 2" in caplog.text


def test_seed_file(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, {"2026-11.json": _month(_rec("new", "2026-11-18"))})
    seed = tmp_path / "seed.json"
    seed.write_text(json.dumps(_month(_rec("old1"), _rec("old2"))))
    monkeypatch.setenv("RESEARCH_SEED", str(seed))
    store = R.load("2026-11-18")
    assert set(store) == {"old1", "old2", "new"}
    sizes = R.save(store, "2026-11-18")
    assert json.loads((R.RESEARCH_DIR / "2026-11.json").read_text(encoding="utf-8"))["events"][0]["id"] == "new"
    assert len(json.loads((R.RESEARCH_DIR / "2026-11.json").read_text(encoding="utf-8"))["events"]) == 3
    assert sizes
