"""Task 090: El Magico - HTML adapter, monthly poster (DeepSeek image input),
poster <-> HTML pairing."""

import datetime
import hashlib
import json
import pathlib

from pipeline import poster_merge, poster_read
from pipeline.adapters import html_elmagico, poster
from pipeline.enrich_ai import event_page_url
from pipeline.normalize import normalize_event

FIX = pathlib.Path(__file__).parent / "fixtures"
VENUE = {"id": "el-magico"}
RAW = json.loads((FIX / "elmagico" / "poster_raw_listopad_2026.json").read_text(encoding="utf-8"))
MEDIA = json.loads((FIX / "elmagico" / "media_search.json").read_text(encoding="utf-8"))
NOV = "https://elmagico.cz/wp-content/uploads/2026/11/program-listopad-2026-el-magico.jpg"


# ── HTML ──────────────────────────────────────────────────────────────────────

def test_html_two_nearest_events():
    html = (FIX / "survey2" / "elmagico_program.html").read_text(encoding="utf-8")
    evs = html_elmagico.parse(VENUE, {}, html)
    assert [(e.date, e.title) for e in evs] == [
        ("2026-11-20", "Miss Tanga 2026 vol.2 – HRAJE SE O 10.000 Kč!"),
        ("2026-11-21", "GLOW IN THE DARK! by Let’s Rave It Up")]
    a, b = evs
    assert a.image_url.endswith("/2026/11/miss-tanga-flyer.jpg")
    assert b.image_url.endswith("Glow-in-the-Dark-by-Lets-Rave-It-Up-21.11.2026.jpg")   # not the FB emoji
    assert a.price_text == "Vstup 150Kč" and b.price_text == "Regular vstup: 150Kč"
    assert a.start_time is None and b.start_time is None        # no time in the text
    assert "DJ ABSOLUTH za mixem!" in a.description and "UV světla" in b.description
    assert a.source["type"] == "html" and a.source["url"].startswith("https://elmagico.cz/program/miss-tanga")


# ── poster discovery ──────────────────────────────────────────────────────────

def test_months_wanted_and_find_posters():
    assert poster.months_wanted(datetime.date(2026, 12, 15)) == [(2026, 12), (2027, 1)]
    months = poster.months_wanted(datetime.date(2026, 11, 22))
    assert months == [(2026, 11), (2026, 12)]
    found = poster.find_posters(MEDIA, months)
    assert set(found) == {(2026, 11)} and found[(2026, 11)]["source_url"] == NOV
    # names vary (-FINAL, -korekce-01) and the upload folder can be the previous month
    found = poster.find_posters(MEDIA, [(2026, 10), (2026, 7), (2026, 9)])
    assert found[(2026, 10)]["source_url"].endswith("program-rijen-2026-el-magico-FINAL.jpg")
    assert found[(2026, 7)]["source_url"].endswith("program-cervenec-2026-el-magico-korekce-01.jpg")
    assert found[(2026, 9)]["source_url"].endswith("/2026/08/program-zari-2026-el-magico.jpg")
    two = [{"source_url": "https://x/program-prosinec-2026-el-magico.jpg", "modified": "2026-11-28T10:00:00"},
           {"source_url": "https://x/program-prosinec-2026-el-magico-FINAL.jpg", "modified": "2026-11-29T10:00:00"}]
    assert poster.find_posters(two, [(2026, 12)])[(2026, 12)]["source_url"].endswith("FINAL.jpg")


# ── reading and checks ────────────────────────────────────────────────────────

def test_check_rows_real_answer_november():
    rows, dropped = poster_read.check_rows(RAW, 2026, 11)
    assert len(rows) == 21 and dropped == []
    assert rows[0] == {"date": "2026-11-03", "weekday": "ÚT",
                       "title": "BEER PONG CHAMPIONSHIP & AFTERPARTY /VSTUP ZDARMA/",
                       "performers": "EL MÁGICO DJ'S", "time": None}
    assert rows[10]["date"] == "2026-11-16" and rows[10]["weekday"] == "PO"


def test_check_rows_rejects():
    raw = {"month": 11, "year": 2026, "events": [
        {"day": 4, "weekday": "PO", "title": "WRONG WEEKDAY"},          # 4. 11. 2026 is Wednesday
        {"day": 31, "weekday": None, "title": "NO SUCH DAY"},
        {"day": 5, "weekday": "ČT", "title": "UNSURE", "uncertain": True},
        {"day": 6, "weekday": "PÁ", "title": "  "},
        {"day": "x", "title": "BAD DAY"},
        {"day": 7, "weekday": "so", "title": "OK", "time": "22:00"},
        {"day": 7, "weekday": "SO", "title": "OK"},                    # duplicate row
        {"day": 10, "title": "TIME NOT HH:MM", "time": "od deseti"}]}
    rows, dropped = poster_read.check_rows(raw, 2026, 11)
    assert [(r["date"], r["title"], r["time"]) for r in rows] == [
        ("2026-11-07", "OK", "22:00"), ("2026-11-10", "TIME NOT HH:MM", None)]
    assert len(dropped) == 6
    # a poster of another month is dropped as a whole
    assert poster_read.check_rows({**raw, "month": 12}, 2026, 11)[0] == []
    assert poster_read.check_rows(None, 2026, 11) == ([], ["no JSON from the model"])


def test_read_poster_schema_fallback_and_cost():
    calls = []

    def post(body, key):
        calls.append(body)
        if len(calls) == 1:
            return 400, "unknown field detail"
        return 200, {"choices": [{"message": {"content": "```json\n" + json.dumps(RAW) + "\n```"}}],
                     "usage": {"prompt_tokens": 1269, "completion_tokens": 1296}}
    res = poster_read.read_poster(b"\xff\xd8jpeg", key="k", post=post,
                                  now=lambda: datetime.datetime(2026, 11, 22, 15, tzinfo=datetime.timezone.utc))
    assert res["error"] is None and len(res["raw"]["events"]) == 21
    first, second = calls
    img = first["messages"][0]["content"][0]
    assert first["model"] == "deepseek-flash" and img["type"] == "image_url"
    assert img["image_url"]["url"].startswith("data:image/jpeg;base64,") and img["image_url"]["detail"] == "high"
    assert "detail" not in second["messages"][0]["content"][0]["image_url"]
    assert second["response_format"] == {"type": "json_object"}
    assert abs(res["cost_usd"] - (1269 * 0.15e-6 + 1296 * 0.6e-6)) < 1e-6   # Sunday = off-peak
    assert poster_read.read_poster(b"x", key="")["error"] == "DEEPSEEK_API_KEY missing"


def test_compare_with_reference():
    rows, _ = poster_read.check_rows(RAW, 2026, 11)
    ref = poster_read.load_reference("docs/tasks/083/elmagico/poster-reference-listopad-2026.md")
    cmp = poster_read.compare(rows, ref)
    assert (cmp["reference"], cmp["read"], cmp["dates_ok"], cmp["titles_exact"]) == (21, 21, 21, 21)


# ── poster events ─────────────────────────────────────────────────────────────

def test_rows_to_events_title_note_artists():
    rows, _ = poster_read.check_rows(RAW, 2026, 11)
    evs = {e.date: e for e in poster.rows_to_events(VENUE, rows, NOV)}
    e = evs["2026-11-03"]
    assert (e.title, e.price_text, e.free, e.artists, e.start_time, e.image_url) == (
        "BEER PONG CHAMPIONSHIP & AFTERPARTY", "VSTUP ZDARMA", True, [], None, None)
    assert e.source == {"type": "poster", "url": NOV, "external_id": None, "section": None}
    e = evs["2026-11-11"]
    assert e.price_text == "VSTUP DO 22:00 ZDARMA" and e.free is None and e.artists == ["DJ ABSOLUTH"]
    assert evs["2026-11-07"].artists == []           # "LET'S RAVE IT UP DJ'S" is a collective


class _FakeFetcher:
    def __init__(self, media, image):
        self.media, self.image, self.calls = media, image, []

    def get(self, url):
        self.calls.append(url)
        return json.dumps(self.media)

    def get_bytes(self, url):
        self.calls.append(url)
        return self.image


def test_poster_fetch_reads_once_and_on_change(monkeypatch):
    image = b"poster-v1"
    ff = _FakeFetcher(MEDIA, image)
    monkeypatch.setattr(poster, "make_fetcher", lambda cfg: ff)
    reads = []

    def read(img, mime):
        reads.append(img)
        return {"raw": RAW, "cost_usd": 0.001, "usage": {}, "error": None}
    cache = {}
    cfg = {"strategy": "elmagico", "media_url": "https://elmagico.cz/wp-json/wp/v2/media?search=program",
           "detail_cache": cache}
    today = datetime.date(2026, 11, 22)
    evs = poster.fetch(VENUE, cfg, today=today, read=read)
    assert len(evs) == 21 and len(reads) == 1 and poster.take_spend() == 0.001
    entry = cache["posters"][NOV]
    assert entry["sha256"] == hashlib.sha256(image).hexdigest() and entry["month"] == "2026-11"
    # same URL and modified: cached, no download, no read
    ff.calls.clear()
    assert len(poster.fetch(VENUE, cfg, today=today, read=read)) == 21
    assert len(reads) == 1 and ff.calls == [cfg["media_url"]] and poster.take_spend() == 0
    # modified changed, same bytes: downloaded, not read again
    ff.media = [{**m, "modified": "2026-11-23T08:00:00"} if m["source_url"] == NOV else m for m in MEDIA]
    poster.fetch(VENUE, cfg, today=today, read=read)
    assert len(reads) == 1 and cache["posters"][NOV]["modified"] == "2026-11-23T08:00:00"
    # new bytes (and new modified): read again
    ff.media = [{**m, "modified": "2026-11-24T08:00:00"} if m["source_url"] == NOV else m for m in MEDIA]
    ff.image = b"poster-v2"
    poster.fetch(VENUE, cfg, today=today, read=read)
    assert len(reads) == 2


def test_poster_failed_read_not_cached(monkeypatch):
    ff = _FakeFetcher(MEDIA, b"img")
    monkeypatch.setattr(poster, "make_fetcher", lambda cfg: ff)
    cache = {}
    cfg = {"strategy": "elmagico", "media_url": "u", "detail_cache": cache}
    fail = lambda img, mime: {"raw": None, "cost_usd": 0.0, "usage": {}, "error": "HTTP 500"}
    assert poster.fetch(VENUE, cfg, today=datetime.date(2026, 11, 22), read=fail) == []
    assert cache["posters"] == {}
    poster.take_spend()


# ── pairing poster <-> HTML ───────────────────────────────────────────────────

def _norm(raw, prev=None):
    return normalize_event(raw, prev or {})


def _poster_events(prev=None):
    rows, _ = poster_read.check_rows(RAW, 2026, 11)
    return [_norm(r, prev) for r in poster.rows_to_events(VENUE, rows, NOV)]


def _html_events(prev=None):
    html = (FIX / "survey2" / "elmagico_program.html").read_text(encoding="utf-8")
    return [_norm(r, prev) for r in html_elmagico.parse(VENUE, {}, html)]


def test_merge_html_replaces_poster_keeps_id_and_first_seen():
    p_evs = _poster_events()
    for e in p_evs:
        e["first_seen"] = "2026-11-02"
    events = p_evs + _html_events()
    out, stats = poster_merge.merge(events)
    assert stats == {"poster": 21, "html": 2, "replaced": 2}
    assert len(out) == 21
    tanga = next(e for e in out if e["date"] == "2026-11-20")
    assert tanga["title"].startswith("Miss Tanga") and tanga["image_url"].endswith("miss-tanga-flyer.jpg")
    assert tanga["id"] == "el-magico-2026-11-20-miss-tanga-2026-vol-2-o-10-000-kc"
    assert tanga["first_seen"] == "2026-11-02"
    assert [s["type"] for s in tanga["sources"]] == ["html", "poster"]
    assert event_page_url(tanga).startswith("https://elmagico.cz/program/miss-tanga")


def test_merge_two_events_one_day_pairs_the_right_one():
    def ev(eid, title, typ):
        return {"id": eid, "venue_id": "el-magico", "date": "2026-12-03", "title": title,
                "first_seen": "2026-12-01", "sources": [{"type": typ, "url": "u"}]}
    quiz = ev("p-quiz", "Z-QUIZ & AFTERPARTY", "poster")
    dj = ev("p-dj", "FRIDAY KÝBLMANIA", "poster")
    html_dj = ev("h-dj", "Friday Kýblmania 🔥 s DJ Partyboy", "html")
    out, stats = poster_merge.merge([quiz, dj, html_dj])
    assert stats["replaced"] == 1
    assert sorted(e["id"] for e in out) == ["p-dj", "p-quiz"]
    assert next(e for e in out if e["id"] == "p-dj")["title"].startswith("Friday")
    # an unlike HTML event on the same day is not paired (duplicate rather than a wrong merge)
    other = ev("h-other", "Beer pong championship", "html")
    out, stats = poster_merge.merge([dict(quiz), other])
    assert stats["replaced"] == 0 and len(out) == 2


def test_merge_uses_previous_poster_event():
    """The poster no longer lists the event (e.g. a new month's poster), the HTML
    event keeps the id it had in the previous run."""
    prev_ev = {"id": "el-magico-2026-11-21-glow-in-the-dark-by-let-s-rave-it-up", "venue_id": "el-magico",
               "date": "2026-11-21", "title": "GLOW IN THE DARK! by Let’s Rave It Up",
               "first_seen": "2026-11-05",
               "sources": [{"type": "html", "url": "x"}, {"type": "poster", "url": NOV}]}
    html_evs = _html_events()
    out, stats = poster_merge.merge(html_evs, {prev_ev["id"]: prev_ev})
    glow = next(e for e in out if e["date"] == "2026-11-21")
    assert stats["replaced"] == 1 and glow["id"] == prev_ev["id"] and glow["first_seen"] == "2026-11-05"
    # venues without a poster are untouched
    other = [{"id": "x", "venue_id": "roxy", "date": "2026-11-21", "title": "A", "sources": [{"type": "html"}]}]
    assert poster_merge.merge(other) == (other, {"poster": 0, "html": 0, "replaced": 0})


def test_poster_image_is_not_an_event_page():
    ev = {"sources": [{"type": "poster", "url": NOV}]}
    assert event_page_url(ev) is None


def test_merge_live_page_two_html_events_for_one_poster_row():
    """2026-11-22: the poster row 'DARTS BATTLE & RUMOVÝ PROJECT X - STUDENT TAKEOVER'
    is two events on the web; one replaces the poster event, the other stays."""
    html = (FIX / "elmagico" / "program_2026-11-22.html").read_text(encoding="utf-8")
    h = [_norm(r) for r in html_elmagico.parse(VENUE, {}, html)]
    assert [(e["date"], e["title"]) for e in h] == [
        ("2026-11-24", "Beer, Chill & Games & Chupito 1+1 ZDARMA"),
        ("2026-11-25", "Darts Battle"), ("2026-11-25", "Rumový PROJECT X – STUDENT TAKEOVER")]
    out, stats = poster_merge.merge(_poster_events() + h)
    assert stats["replaced"] == 2 and len(out) == 22
    day25 = sorted((e["title"], e["id"]) for e in out if e["date"] == "2026-11-25")
    assert day25 == [("Darts Battle", "el-magico-2026-11-25-darts-battle"),
                     ("Rumový PROJECT X – STUDENT TAKEOVER",
                      "el-magico-2026-11-25-darts-battle-rumovy-project-x-student-takeover")]
