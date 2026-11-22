"""
Task 090: read a monthly programme poster (image) with DeepSeek.

Model: `deepseek-flash` accepts images in /chat/completions as content parts
{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
(https://api-docs.deepseek.com/guides/vision/; the older name
`deepseek-v4-flash-vision-exp` is retired and served by the same model).
No new key: DEEPSEEK_API_KEY as for the AI enrichment.

The model only transcribes the poster rows into a fixed JSON schema
(POSTER_PROMPT).  Our code then checks every row (check_rows):
  - the poster month / year must equal the month in the file name,
  - the day must exist in that month,
  - a printed weekday must match the date,
  - rows the model marks as uncertain, or with an empty title, are dropped,
  - a time is kept only when it is a valid HH:MM printed on the poster.
Dropped rows are logged; nothing is completed or guessed.

`python -m pipeline.poster_read test <image> <reference.md> <out_dir>` reads
the November 2026 El Magico poster and compares it with the hand-made
reference (docs/tasks/083/elmagico/poster-reference-listopad-2026.md); run in
GitHub Actions (deepseek-test.yml mode=poster), the API host is not reachable
from the developer machine.
"""

import base64
import calendar
import datetime
import json
import logging
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request

from pipeline.deepseek import API, MODEL, is_peak, token_cost
from pipeline.fetch import USER_AGENT

log = logging.getLogger(__name__)

MAX_TOKENS = 4000
WEEKDAYS_CS = ["PO", "ÚT", "ST", "ČT", "PÁ", "SO", "NE"]       # Monday = 0
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

POSTER_PROMPT = """You transcribe a club's monthly programme poster (Czech). Copy text exactly as printed; never invent, complete or correct anything.

Return JSON only:
{"month_label": "<month and year as printed in the header, e.g. LISTOPAD 2026>",
 "month": <month number 1-12 from the header>, "year": <year from the header>,
 "events": [{"day": <day of month as printed>, "weekday": "<weekday abbreviation as printed, e.g. ÚT, or null>",
             "title": "<the event title exactly as printed, including notes like /VSTUP ZDARMA/>",
             "performers": "<DJ / performer text printed next to the event, or null>",
             "time": "<HH:MM only if a start time is printed for this event, else null>",
             "uncertain": <true if any part of the date or title is not clearly legible>}]}

One entry per event row, in the order on the poster. Keep diacritics. Do not translate. If the poster shows no events, return "events": []."""


# -- model call -------------------------------------------------------------

def _post(body: dict, key: str, timeout: int = 180) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        API + "/chat/completions", data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}",
                 "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")[:500]
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, f"network: {exc}"


def _bodies(data_url: str) -> list[dict]:
    """Request variants, most specific first.  The docs do not say whether JSON
    mode and the optional `detail` field work together with images, so a
    variant rejected with HTTP 400 falls back to the next one."""
    def body(detail: bool, json_mode: bool) -> dict:
        img = {"url": data_url, **({"detail": "high"} if detail else {})}
        b = {"model": MODEL, "temperature": 0, "max_tokens": MAX_TOKENS,
             "thinking": {"type": "disabled"},
             "messages": [{"role": "user", "content": [
                 {"type": "image_url", "image_url": img},
                 {"type": "text", "text": POSTER_PROMPT}]}]}
        if json_mode:
            b["response_format"] = {"type": "json_object"}
        return b
    return [body(True, True), body(False, True), body(False, False)]


def read_poster(image: bytes, mime: str = "image/jpeg", key: str | None = None,
                post=_post, now=None) -> dict:
    """One model call (plus fallbacks on HTTP 400).  Returns
    {"raw": parsed JSON or None, "usage": {...}, "cost_usd": float, "error": str|None}."""
    key = key if key is not None else os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        return {"raw": None, "usage": {}, "cost_usd": 0.0, "error": "DEEPSEEK_API_KEY missing"}
    data_url = f"data:{mime};base64," + base64.b64encode(image).decode()
    peak = is_peak(now() if now else None)
    cost, usage, err = 0.0, {}, None
    for body in _bodies(data_url):
        code, data = post(body, key)
        if code != 200:
            err = f"HTTP {code}: {str(data)[:300]}"
            log.warning("poster read: %s", err)
            if code == 400:
                continue
            break
        um = data.get("usage") or {}
        hit = um.get("prompt_cache_hit_tokens", 0)
        miss = um.get("prompt_cache_miss_tokens", max(0, um.get("prompt_tokens", 0) - hit))
        out = um.get("completion_tokens", 0)
        cost += token_cost(hit, miss, out, peak)
        usage = {"input_tokens": hit + miss, "cached_tokens": hit, "output_tokens": out,
                 "peak": peak, "detail": "detail" in body["messages"][0]["content"][0]["image_url"],
                 "json_mode": "response_format" in body}
        text = (((data.get("choices") or [{}])[0]).get("message") or {}).get("content") or ""
        m = re.search(r"\{.*\}", text, re.S)
        try:
            return {"raw": json.loads(m.group(0)) if m else None, "usage": usage,
                    "cost_usd": round(cost, 6), "error": None if m else "no JSON in answer",
                    "text": text[:4000]}
        except ValueError:
            return {"raw": None, "usage": usage, "cost_usd": round(cost, 6),
                    "error": "invalid JSON in answer", "text": text[:4000]}
    return {"raw": None, "usage": usage, "cost_usd": round(cost, 6), "error": err}


# -- checks -----------------------------------------------------------------

def _fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "").upper())
    return "".join(c for c in s if not unicodedata.combining(c)).strip(" .")


def check_rows(raw: dict | None, year: int, month: int) -> tuple[list[dict], list[str]]:
    """Validated rows [{date, weekday, title, performers, time}] and the
    reasons of dropped rows.  A month / year that differs from the expected
    one drops the whole poster."""
    if not isinstance(raw, dict):
        return [], ["no JSON from the model"]
    try:
        r_month, r_year = int(raw.get("month")), int(raw.get("year"))
    except (TypeError, ValueError):
        return [], [f"poster month/year not readable: {raw.get('month_label')!r}"]
    if (r_year, r_month) != (year, month):
        return [], [f"poster header {r_month}/{r_year} != expected {month}/{year}"]
    days_in = calendar.monthrange(year, month)[1]
    rows, dropped, seen = [], [], set()
    for ev in raw.get("events") or []:
        if not isinstance(ev, dict):
            continue
        title = re.sub(r"\s+", " ", str(ev.get("title") or "")).strip()
        label = f"{ev.get('day')}. {title[:60]!r}"
        if ev.get("uncertain") is True:
            dropped.append(f"uncertain: {label}")
            continue
        if not title:
            dropped.append(f"empty title: {label}")
            continue
        try:
            day = int(ev.get("day"))
        except (TypeError, ValueError):
            dropped.append(f"day not a number: {label}")
            continue
        if not 1 <= day <= days_in:
            dropped.append(f"day outside the month: {label}")
            continue
        date = datetime.date(year, month, day)
        wd = ev.get("weekday")
        if wd:
            want = _fold(WEEKDAYS_CS[date.weekday()])
            if _fold(wd) != want:
                dropped.append(f"weekday {wd!r} != {WEEKDAYS_CS[date.weekday()]}: {label}")
                continue
        key = (date.isoformat(), _fold(title))
        if key in seen:
            dropped.append(f"duplicate row: {label}")
            continue
        seen.add(key)
        t = str(ev.get("time") or "").strip()
        perf = re.sub(r"\s+", " ", str(ev.get("performers") or "")).strip()
        rows.append({"date": date.isoformat(), "weekday": wd or None, "title": title,
                     "performers": perf if perf and perf not in ("-", "–") else None,
                     "time": t if _TIME_RE.match(t) else None})
    return rows, dropped


# -- accuracy test against the reference (task 090) ---------------------------

def load_reference(path: str) -> list[dict]:
    """Rows of the markdown table: | # | 3. 11. | ÚT | title | performers |"""
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*\d+\s*\|\s*(\d{1,2})\.\s*(\d{1,2})\.\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]*)\|",
                     line)
        if m:
            perf = m.group(5).strip()
            out.append({"day": int(m.group(1)), "month": int(m.group(2)),
                        "weekday": m.group(3).strip(), "title": m.group(4).strip(),
                        "performers": None if perf in ("–", "-", "") else perf})
    return out


def norm_title(s: str) -> str:
    s = _fold(s).replace("’", "'")
    s = re.sub(r"[^A-Z0-9'+&]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def compare(rows: list[dict], ref: list[dict]) -> dict:
    """Per reference row: found (same date), title exact (after folding case,
    diacritics, punctuation) and title similarity; extra rows not in the reference."""
    from difflib import SequenceMatcher
    by_date: dict[int, list[dict]] = {}
    for r in rows:
        by_date.setdefault(int(r["date"][-2:]), []).append(r)
    table, used = [], set()
    for ref_row in ref:
        cands = [r for r in by_date.get(ref_row["day"], []) if id(r) not in used]
        best, score = None, 0.0
        for r in cands:
            s = SequenceMatcher(None, norm_title(r["title"]), norm_title(ref_row["title"])).ratio()
            if s > score:
                best, score = r, s
        if best is not None:
            used.add(id(best))
        table.append({"day": ref_row["day"], "ref_title": ref_row["title"],
                      "read_title": best["title"] if best else None,
                      "date_ok": best is not None,
                      "title_exact": bool(best) and norm_title(best["title"]) == norm_title(ref_row["title"]),
                      "similarity": round(score, 3),
                      "ref_performers": ref_row["performers"],
                      "read_performers": best["performers"] if best else None})
    extra = [r for r in rows if id(r) not in used]
    return {"reference": len(ref), "read": len(rows),
            "dates_ok": sum(t["date_ok"] for t in table),
            "titles_exact": sum(t["title_exact"] for t in table),
            "titles_close": sum(t["similarity"] >= 0.9 for t in table),
            "extra": extra, "table": table}


def _test(image_path: str, ref_path: str, out_dir: str) -> int:
    logging.basicConfig(level=logging.INFO)
    os.makedirs(out_dir, exist_ok=True)
    with open(image_path, "rb") as f:
        image = f.read()
    res = read_poster(image)
    rows, dropped = check_rows(res.get("raw"), 2026, 11)
    cmp = compare(rows, load_reference(ref_path))
    result = {"model": MODEL, "read": res, "rows": rows, "dropped": dropped, "compare": cmp}
    with open(os.path.join(out_dir, "poster_test.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    lines = [f"model {MODEL}, cost ${res.get('cost_usd')}, usage {res.get('usage')}, "
             f"error {res.get('error')}",
             f"reference {cmp['reference']}, read {cmp['read']}, dates ok {cmp['dates_ok']}, "
             f"titles exact {cmp['titles_exact']}, titles >= 0.9 {cmp['titles_close']}, "
             f"extra {len(cmp['extra'])}, dropped {len(dropped)}", ""]
    lines += [f"{t['day']:>2} | {'ok' if t['date_ok'] else 'MISSING'} | "
              f"{'=' if t['title_exact'] else t['similarity']} | {t['ref_title']} | {t['read_title']}"
              f" | {t['ref_performers']} | {t['read_performers']}" for t in cmp["table"]]
    lines += ["", "dropped:"] + dropped + ["", "extra:"] + [json.dumps(e, ensure_ascii=False)
                                                             for e in cmp["extra"]]
    with open(os.path.join(out_dir, "poster_test.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if res.get("raw") is not None else 1


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "test":
        sys.exit(_test(*sys.argv[2:5]))
    print("usage: python -m pipeline.poster_read test <image> <reference.md> <out_dir>")
    sys.exit(2)
