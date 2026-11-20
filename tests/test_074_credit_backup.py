"""Task 074: DeepSeek low-credit alert, balance lookup never stops the run,
research backup used when Pages + cache give fewer records."""

import io
import json
import urllib.error

from pipeline import alerts, deepseek, research_store as R, weekly_report
from tests.test_run_report import FakeIssues, HIST, summ


def _summ(date, bal):
    return summ(date, {"roxy": 40}, ai={"balance_usd": bal})


def test_low_credit_opens_then_closes_after_top_up():
    gh = FakeIssues()
    a, scope = alerts.compute("daily", "success", _summ("2026-11-17", 0.12), HIST, set())
    assert [x["key"] for x in a] == ["ai:low-credit"] and "$0.12" in a[0]["body"]
    assert alerts.sync(a, scope, gh, "2026-11-17") == ["open #101 ai:low-credit"]
    # balance unknown in the next run -> the issue stays open
    a, scope = alerts.compute("daily", "success", _summ("2026-11-18", None), HIST, set())
    assert a == [] and alerts.sync(a, scope, gh, "2026-11-18") == []
    assert gh.issues[101]["state"] == "open"
    # topped up -> closed
    a, scope = alerts.compute("daily", "success", _summ("2026-11-19", 0.20), HIST, set())
    assert alerts.sync(a, scope, gh, "2026-11-19") == ["close #101 ai:low-credit"]


def test_low_credit_and_402_are_separate_issues():
    s = summ("2026-11-17", {"roxy": 40}, ai={"balance_usd": 0.0, "http_402": True})
    keys = [x["key"] for x in alerts.compute("daily", "success", s, HIST, set())[0]]
    assert keys == ["ai:limit", "ai:low-credit"]


def test_balance_parsed_from_usd_entry():
    body = {"is_available": True, "balance_infos": [
        {"currency": "CNY", "total_balance": "9.00"},
        {"currency": "USD", "total_balance": "1.76", "granted_balance": "0.00",
         "topped_up_balance": "1.76"}]}
    seen = []

    def opener(req, timeout=0):
        seen.append((req.full_url, req.get_method(), req.get_header("Authorization")))
        return io.BytesIO(json.dumps(body).encode())
    assert deepseek.balance_usd("k", opener=opener) == 1.76
    assert seen == [("https://api.deepseek.com/user/balance", "GET", "Bearer k")]


def test_balance_failure_does_not_raise(caplog):
    def http_err(req, timeout=0):
        raise urllib.error.HTTPError(req.full_url, 500, "x", {}, None)

    def timeout(req, timeout=0):
        raise TimeoutError("timed out")
    assert deepseek.balance_usd("k", opener=http_err) is None
    assert deepseek.balance_usd("k", opener=timeout) is None
    assert deepseek.balance_usd("k", opener=lambda r, timeout=0: io.BytesIO(b"<html>")) is None
    assert deepseek.balance_usd("") is None
    assert "balance not available" in caplog.text


def test_weekly_report_shows_balance():
    s = _summ("2026-11-17", 1.5)
    s["success"] = True
    _, body = weekly_report.build([s], "2026-11-17")
    assert "Zostatok DeepSeek: $1.50 (2026-11-17)" in body


def _pages(monkeypatch, tmp_path, pages):
    monkeypatch.setattr(R, "RESEARCH_DIR", tmp_path / "research")
    monkeypatch.setattr(R.time, "sleep", lambda s: None)
    monkeypatch.setenv("PREVIOUS_EVENTS_URL", "https://x.github.io/eventapp/events.json")
    monkeypatch.delenv("RESEARCH_SEED", raising=False)

    def urlopen(req, timeout=0):
        res = pages.get(req.full_url.rsplit("/", 1)[1], 404)
        if isinstance(res, int):
            raise urllib.error.HTTPError(req.full_url, res, "x", {}, None)
        return io.BytesIO(json.dumps(res).encode())
    monkeypatch.setattr(R.urllib.request, "urlopen", urlopen)


def _month(*ids, processed="2026-11-17"):
    return {"month": "2026-11", "events": [{"id": i, "processed": processed, "facts": i}
                                           for i in ids]}


def test_backup_used_when_pages_and_cache_have_fewer(tmp_path, monkeypatch, caplog):
    _pages(monkeypatch, tmp_path, {"2026-11.json": _month("a", processed="2026-11-18")})
    R.BACKUP_DIR.mkdir()
    (R.BACKUP_DIR / "2026-11.json").write_text(json.dumps(_month("a", "b", "c")))
    store = R.load("2026-11-19")
    assert sorted(store) == ["a", "b", "c"]
    assert store["a"]["processed"] == "2026-11-18"        # newer Pages record kept
    assert "backup merged" in caplog.text


def test_backup_not_used_when_pages_complete(tmp_path, monkeypatch, caplog):
    _pages(monkeypatch, tmp_path, {"2026-11.json": _month("a", "b")})
    R.BACKUP_DIR.mkdir()
    (R.BACKUP_DIR / "2026-11.json").write_text(json.dumps(_month("x")))
    assert sorted(R.load("2026-11-19")) == ["a", "b"]
    assert "backup merged" not in caplog.text


def test_backup_writes_kept_months_only(tmp_path, monkeypatch):
    _pages(monkeypatch, tmp_path, {"2026-11.json": _month("a", "b")})
    R.BACKUP_DIR.mkdir()
    # task 085: KEEP_MONTHS = 7 (2026-05 .. 2026-11); 2026-04 is out
    (R.BACKUP_DIR / "2026-04.json").write_text(json.dumps({"month": "2026-04", "events": []}))
    assert R.backup("2026-11-19") == 2
    assert sorted(p.name for p in R.BACKUP_DIR.iterdir()) == ["2026-11.json"]
    data = json.loads((R.BACKUP_DIR / "2026-11.json").read_text(encoding="utf-8"))
    assert [r["id"] for r in data["events"]] == ["a", "b"]
