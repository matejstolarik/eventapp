"""Tests for run summaries, alerts and the weekly report (task 057)."""

import datetime
import re

from pipeline import alerts, run_summary, weekly_report


def ev(i, venue="roxy", date="2026-11-25", **kw):
    e = {"id": i, "venue_id": venue, "title": i.upper(), "date": date,
         "start_time": "20:00", "image_url": "x.jpg", "price_text": "300 Kč",
         "description": "d", "formats": ["concert"], "genres": ["rock"],
         "sources": [{"url": f"https://example.com/{i}"}]}
    e.update(kw)
    return e


# ---------------------------------------------------------------- part 1

def test_build_counts_missing_new_gone_and_review():
    events = [
        ev("a"),
        ev("b", image_url=None, start_time=None, price_text=None, genres=[],
           description=None, primary_format="concert", artists=["Band X", "Band Y", "Z"],
           artist_links=[{"name": "Band Y", "spotify_url": "s"}]),
        ev("c", formats=["theatre"], genres=[],
           classification={"method": "llm+web", "confidence": 0.4}, primary_format="theatre"),
        ev("d", enrichment={"run": {"searches": 2}},
           price_text="250 Kč", date="2026-11-21"),
        ev("e", enrichment={"run": {"searches": 3}, "genre_candidates": ["x"]}),
    ]
    events[3]["enrichment"]["price_text"] = {"by": "ai_web", "verified": False,
                                             "source_url": "https://t.example"}
    previous = {"a": ev("a"), "c": ev("c"), "e": ev("e"), "d": ev("d"), "gone1": ev("gone1"),
                "past": ev("past", date="2026-11-01")}
    web_stats = {"dropped": ["a: price '500 Kč': not on page", "c: genre 'xx': unknown"],
                 "type_changed_ids": [{"id": "c", "old": ["concert"], "new": ["theatre"]}],
                 "type_changed": 1, "prices_dropped": 1, "searches": 5, "cost_usd": 0.01,
                 "month_searches": 100, "limit": 3000,
                 "budget": {"month": "2026-11", "month_spent_usd": 1.2}}
    s = run_summary.build(events, previous, [("roxy", "rss", 4, None)], "2026-11-19",
                          "2026-11-19T05:30:00+01:00", web_stats=web_stats,
                          proposals=[{"name": "shoegaze", "kind": "music", "count": 3,
                                      "event_ids": ["a", "b"]}])
    v = s["venues"]["roxy"]
    assert (v["events"], v["new"], v["gone"]) == (5, 1, 1)
    assert v["missing"] == {"image": 1, "time": 1, "price": 1, "genre": 1, "description": 1}
    assert v["music_events"] == 4
    kinds = sorted(r["kind"] for r in s["review"])
    assert kinds == ["ai_nothing", "genres_dropped", "low_confidence", "price_dropped",
                     "type_changed"]
    assert s["no_spotify"] == [run_summary._item(events[1], artists=["Band X"])]
    assert [u["id"] for u in s["unverified_prices"]] == ["d"]
    assert s["ai"]["month_budget_usd"] == 5.0 and s["ai"]["low_confidence"] == 1
    assert s["genre_proposals"][0]["examples"][0]["id"] == "a"


def test_simulate_zero_only_changes_summary():
    s = run_summary.build([ev("a")], {}, [("roxy", "rss", 1, None)], "2026-11-19", "t",
                          simulate_zero="roxy")
    assert s["venues"]["roxy"]["sources"] == [{"label": "rss", "events": 0,
                                               "warning": "zero_events"}]
    assert s["venues"]["roxy"]["events"] == 1


def test_save_keeps_60_days(tmp_path):
    for d in ("2026-08-01", "2026-11-18"):
        (tmp_path / f"{d}.json").write_text("{}", encoding="utf-8")
    run_summary.save({"date": "2026-11-19"}, tmp_path)
    assert sorted(p.stem for p in tmp_path.glob("*.json")) == ["2026-11-18", "2026-11-19"]


# ---------------------------------------------------------------- part 2

def summ(date, counts, **kw):
    """counts = {venue: n} -> summary with one source 'rss' per venue."""
    s = {"date": date, "generated_at": f"{date}T05:30:00+01:00", "success": True,
         "events": sum(counts.values()), "new": 0,
         "venues": {v: {"events": n, "new": 0, "gone": 0, "music_events": n,
                        "missing": {f: 0 for f in run_summary.MISSING_FIELDS},
                        "sources": [{"label": "rss", "events": n,
                                     "warning": None if n else "zero_events"}]}
                    for v, n in counts.items()},
         "ai": {}, "review": [], "no_spotify": [], "unverified_prices": [],
         "genre_proposals": []}
    s.update(kw)
    return s


def days(n, start="2026-11-10"):
    d = datetime.date.fromisoformat(start)
    return [(d + datetime.timedelta(days=i)).isoformat() for i in range(n)]


HIST = [summ(d, {"roxy": 40, "epic": 30}) for d in days(7)]


def test_no_alert_on_normal_run():
    a, scope = alerts.compute("daily", "success", summ("2026-11-17", {"roxy": 38, "epic": 29}),
                              HIST, set())
    assert a == [] and "workflow:daily" in scope and "source:" in scope


def test_zero_and_drop_alerts():
    a, _ = alerts.compute("daily", "success", summ("2026-11-17", {"roxy": 0, "epic": 14}),
                          HIST, set())
    assert [x["key"] for x in a] == ["source:roxy/rss", "source:epic/rss"]
    assert "0 akcií" in a[0]["title"] and "medián posledných 7 behov: 40" in a[0]["body"]
    assert "pokles na 14" in a[1]["title"]
    # exactly half is not a drop of more than 50 %
    a, _ = alerts.compute("daily", "success", summ("2026-11-17", {"roxy": 20, "epic": 15}),
                          HIST, set())
    assert a == []


def test_ignore_list_silences_source():
    a, _ = alerts.compute("daily", "success", summ("2026-11-17", {"roxy": 0, "epic": 30}),
                          HIST, {"roxy:source"})
    assert a == []


def test_ai_limit_alert():
    s = summ("2026-11-17", {"roxy": 40}, ai={"month_cost_usd": 2.998, "month_budget_usd": 3.0})
    assert [x["key"] for x in alerts.compute("daily", "success", s, HIST, set())[0]] == ["ai:limit"]
    s["ai"] = {"http_402": True}
    assert "HTTP 402" in alerts.compute("daily", "success", s, HIST, set())[0][0]["body"]


def test_failure_alert_and_scope():
    a, scope = alerts.compute("deploy-app", "failure", None, HIST, set(), "https://run/1")
    assert [x["key"] for x in a] == ["workflow:deploy-app"] and scope == set()
    assert "https://run/1" in a[0]["body"]


class FakeIssues:
    def __init__(self, open_issues=()):
        self.issues = {i["number"]: dict(i, state="open") for i in open_issues}
        self.comments, self.n = [], 100

    def open_issues(self, label):
        return [i for i in self.issues.values() if i["state"] == "open"
                and label in i.get("labels", [label])]

    def create(self, title, body, label):
        self.n += 1
        self.issues[self.n] = {"number": self.n, "title": title, "body": body,
                               "labels": [label], "state": "open",
                               "html_url": f"https://gh/issues/{self.n}"}
        return self.issues[self.n]

    def comment(self, number, body):
        self.comments.append((number, body))

    def close(self, number, comment=None):
        if comment:
            self.comment(number, comment)
        self.issues[number]["state"] = "closed"


def test_sync_opens_comments_and_closes():
    gh = FakeIssues()
    zero = summ("2026-11-17", {"roxy": 0, "epic": 30})
    a, scope = alerts.compute("daily", "success", zero, HIST, set())
    assert alerts.sync(a, scope, gh, "2026-11-17") == ["open #101 source:roxy/rss"]
    # same problem next day -> comment, no new issue
    assert alerts.sync(a, scope, gh, "2026-11-18") == ["comment #101 source:roxy/rss"]
    assert len(gh.issues) == 1
    # a failed deploy-app run does not close source alerts (not in its scope)
    a2, scope2 = alerts.compute("deploy-app", "failure", None, HIST, set())
    alerts.sync(a2, scope2, gh, "2026-11-18")
    assert gh.issues[101]["state"] == "open"
    # normal daily run -> source issue closed; deploy-app alert stays open
    a3, scope3 = alerts.compute("daily", "success", summ("2026-11-19", {"roxy": 40}), HIST, set())
    assert alerts.sync(a3, scope3, gh, "2026-11-19") == ["close #101 source:roxy/rss"]
    assert gh.issues[102]["state"] == "open"
    # successful deploy-app closes its alert
    a4, scope4 = alerts.compute("deploy-app", "success", None, HIST, set())
    assert alerts.sync(a4, scope4, gh, "2026-11-19") == ["close #102 workflow:deploy-app"]


def test_record_status_keeps_earlier_summary(tmp_path):
    alerts.record_status("daily", "failure", None, "2026-11-19", tmp_path)
    assert run_summary.load_all(tmp_path)[0]["success"] is False
    s = summ("2026-11-19", {"roxy": 1})
    run_summary.save(s, tmp_path)
    alerts.record_status("daily", "failure", None, "2026-11-19", tmp_path)
    assert run_summary.load_all(tmp_path)[0]["venues"]


# ---------------------------------------------------------------- part 3

def test_weekly_all_ok():
    week = [summ(d, {"roxy": 40, "epic": 30}) for d in days(14, "2026-11-10")]
    title, body = weekly_report.build(week, "2026-11-23")
    assert title == "Týždenný report W48 · 2026-11-23"
    assert "✅ Všetko v poriadku" in body
    assert "| roxy | 40 | 0 | +0 |" in body


def test_weekly_problems_ids_and_sections():
    week = [summ(d, {"roxy": 40, "epic": 30}) for d in days(10, "2026-11-10")]
    last = summ("2026-11-23", {"roxy": 0, "epic": 30})
    last["venues"]["epic"]["missing"]["price"] = 20          # 67 %, usual 0 %
    last["venues"]["epic"]["new"] = 5
    item = {"id": "epic-1", "venue_id": "epic", "title": "Night", "date": "2026-11-28",
            "source_url": "https://epic.example/1"}
    last["review"] = [dict(item, kind="price_dropped", detail="price '1 Kč': not on page"),
                      dict(item, id="epic-2", kind="genres_dropped", detail="genre x")]
    last["no_spotify"] = [dict(item, artists=["DJ A"])]
    last["unverified_prices"] = [dict(item, price_text="300 Kč", price_source="https://t")]
    last["genre_proposals"] = [{"name": "shoegaze", "kind": "music", "count": 4,
                                "examples": [item]},
                               {"name": "rare", "kind": "music", "count": 2, "examples": []}]
    last["ai"] = {"searches": 10, "cost_usd": 0.1, "month": "2026-11",
                  "month_cost_usd": 1.5, "month_budget_usd": 3.0,
                  "month_searches": 900, "search_limit": 3000}
    week.append(last)
    _, body = weekly_report.build(week, "2026-11-23")
    ids = re.findall(r"\*\*(W48-\d\d)\*\*", body)
    assert ids == [f"W48-{i:02d}" for i in range(1, len(ids) + 1)]       # unique, in order
    assert "Zdroj `roxy/rss` dal v poslednom behu 0 akcií." in body
    assert "Chýbajú čísla z 3 dní" in body
    assert "`epic:price` cena chýba 67 % (20/30, bežne 0 %)" in body
    assert "zahodená cena (price '1 Kč': not on page)" in body
    assert "#/akcia/epic-1" in body and "[zdroj](https://epic.example/1)" in body
    assert "**shoegaze** (music, 4 akcií)" in body and "rare" not in body
    assert "DJ A —" in body and "300 Kč —" in body
    assert "Mesiac 2026-11: $1.50 / $3.00, 900 / 3000 hľadaní" in body
    # ignored items disappear
    _, body2 = weekly_report.build(week, "2026-11-23", {"epic:price", "epic-1", "genre:shoegaze"})
    assert "epic:price" not in body2.split("_Pravidlá")[0] and "#/akcia/epic-1" not in body2
    assert "shoegaze" not in body2


def test_publish_closes_previous_report():
    gh = FakeIssues([{"number": 5, "title": "old", "body": "", "labels": ["weekly-report"]}])
    url = weekly_report.publish("t", "b", gh)
    assert url == "https://gh/issues/101" and gh.issues[5]["state"] == "closed"
    assert "#101" in gh.comments[0][1]


# ---------------------------------------------------------------- task 085

def test_venue_image_alert_open_comment_close():
    from pipeline.main import venue_image_problems
    venues = [
        {"id": "a", "active": True, "image_url": "https://x/a.jpg", "image_card": "img/venues/card/a.jpg"},
        {"id": "b", "active": True, "image_url": None, "image_card": None},
        {"id": "c", "active": True, "image_url": "https://x/c.jpg", "image_card": None},
        {"id": "d", "active": False, "image_url": None, "image_card": None},
    ]
    missing = venue_image_problems(venues)
    assert missing == [{"id": "b", "reason": "no_image_url"},
                       {"id": "c", "reason": "download_failed", "url": "https://x/c.jpg"}]
    s = summ("2026-11-20", {"roxy": 40})
    s["venue_images_missing"] = missing
    a, scope = alerts.compute("daily", "success", s, HIST, set())
    assert [x["key"] for x in a] == ["venue-image:b", "venue-image:c"]
    assert "venue-image:" in scope and "image_url" in a[0]["body"]
    gh = FakeIssues()
    assert alerts.sync(a, scope, gh, "2026-11-20") == ["open #101 venue-image:b",
                                                       "open #102 venue-image:c"]
    # next day still missing -> comment, no duplicate issue
    assert alerts.sync(a, scope, gh, "2026-11-21") == ["comment #101 venue-image:b",
                                                       "comment #102 venue-image:c"]
    # fixed -> closed
    s["venue_images_missing"] = []
    a, scope = alerts.compute("daily", "success", s, HIST, set())
    assert alerts.sync(a, scope, gh, "2026-11-22") == ["close #101 venue-image:b",
                                                       "close #102 venue-image:c"]
    # summary without the field (older runs) never closes these issues
    _, scope = alerts.compute("daily", "success", summ("2026-11-22", {"roxy": 40}), HIST, set())
    assert "venue-image:" not in scope
