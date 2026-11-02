"""LLM extraction test - Task 006.

Tests whether claude-haiku-5-5 can reliably extract events from HTML.
Compares LLM output against the html_akropolis parser for Akropolis.
Runs stability test (3 identical calls) per page.

Usage:
    Set ANTHROPIC_API_KEY, then:
    python scripts/llm_test/run.py

Fixtures required:
    tests/fixtures/llm/akropolis_hudba_p1.html  (fetched automatically)
    tests/fixtures/llm/akropolis_hudba_p2.html  (fetched automatically)
    tests/fixtures/llm/twist_music.html         (save manually from browser)
"""

import datetime
import json
import os
import re
import sys
import textwrap
from pathlib import Path

from bs4 import BeautifulSoup

# ── constants ──────────────────────────────────────────────────────────────────

MODEL = "claude-haiku-5-5"
# $0.10/1M input, $0.50/1M output (as of 2026-11-02)
PRICE_INPUT_PER_M = 0.10
PRICE_OUTPUT_PER_M = 0.50
BUDGET_USD = 0.50

TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
CUTOFF = TODAY + datetime.timedelta(days=180)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "llm"

# ── API key check ──────────────────────────────────────────────────────────────

def _check_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        sys.exit("ERROR: ANTHROPIC_API_KEY is not set.")
    print(f"API key present: True, length: {len(key)}")
    return key


# ── HTML cleaning ──────────────────────────────────────────────────────────────

def clean_html(html: str) -> str:
    """Strip scripts, styles, navigation and return visible text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "noscript", "svg", "iframe", "link", "meta"]):
        tag.decompose()
    # Also strip hidden elements
    for tag in soup.find_all(style=re.compile(r"display\s*:\s*none")):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token."""
    return len(text) // 4


# ── year inference (same rule as html_akropolis adapter) ──────────────────────

def infer_year(day: int, month: int) -> "str | None":
    """Apply year inference rule: if date < yesterday, use next year.
    Returns YYYY-MM-DD string or None if outside +180-day window.
    """
    try:
        d = datetime.date(TODAY.year, month, day)
    except ValueError:
        return None
    if d < YESTERDAY:
        try:
            d = datetime.date(TODAY.year + 1, month, day)
        except ValueError:
            return None
    if d > CUTOFF:
        return None
    return d.isoformat()


_DATE_RAW_RE = re.compile(r"(\d{1,2})[.\s]+(\d{1,2})[.\s]*")
_TIME_RE = re.compile(r"\b(\d{1,2}):(\d{2})\b")


def parse_date_raw(date_raw: str) -> "str | None":
    """Parse a raw date string like '4. 11.' into YYYY-MM-DD."""
    if not date_raw:
        return None
    m = _DATE_RAW_RE.match(date_raw.strip())
    if not m:
        return None
    day, month = int(m.group(1)), int(m.group(2))
    return infer_year(day, month)


# ── verification: check model values exist in source text ─────────────────────

def verify_event(event: dict, source_text: str) -> dict:
    """Verify model-returned values exist literally in source.

    Returns event with a 'hallucinated' list of fields that were NOT found
    in the source text.
    """
    hallucinated = []

    date_raw = event.get("date_raw")
    if date_raw:
        # Check the day+month appear together in source text
        m = _DATE_RAW_RE.match(date_raw.strip())
        if m:
            day, month = m.group(1), m.group(2)
            # Look for "DD. MM." or "D. M." pattern near each other in source
            pattern = re.compile(
                rf"\b{int(day)}\s*[.\s]\s*{int(month)}\s*[.\s]"
            )
            if not pattern.search(source_text):
                hallucinated.append("date_raw")
        else:
            hallucinated.append("date_raw")

    start_time = event.get("start_time")
    if start_time:
        # Time should be literally in the source
        if start_time not in source_text:
            hallucinated.append("start_time")

    room = event.get("room")
    if room:
        if room not in source_text:
            hallucinated.append("room")

    return {**event, "hallucinated": hallucinated}


# ── LLM prompt ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an event data extraction assistant.
    Extract events from HTML program pages of Czech/Slovak music venues.
    Return ONLY a JSON array. No explanation, no markdown fences.
""")

def build_user_prompt(page_text: str, venue_hint: str) -> str:
    today_str = TODAY.isoformat()
    return textwrap.dedent(f"""\
        Today is {today_str}. Extract events from the following venue program page for: {venue_hint}

        Return a JSON array of objects with these fields:
        - "title": event name as written on the page (string)
        - "date_raw": date exactly as it appears on the page, e.g. "4. 11." (string or null)
        - "start_time": start time in HH:MM format if present (string or null)
        - "room": room/stage name if present (string or null)
        - "sold_out": true if the page explicitly says sold out, false if tickets available, null otherwise

        Rules:
        - Only include values that are explicitly on the page — do NOT guess or infer any value.
        - For date_raw: write only what is printed, e.g. "4. 11." or "4.11." — do NOT add a year.
        - For start_time: only if an explicit time like "19:30" appears next to the event.
        - Omit cancelled/postponed events.

        Page text:
        ---
        {page_text}
        ---
    """)


# ── single LLM call ───────────────────────────────────────────────────────────

def call_llm(client, page_text: str, venue_hint: str) -> "tuple[list[dict], dict]":
    """Call LLM and return (events, usage_dict)."""
    import anthropic

    user_prompt = build_user_prompt(page_text, venue_hint)
    input_tokens_est = estimate_tokens(SYSTEM_PROMPT + user_prompt)

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "input_tokens_est": input_tokens_est,
    }

    text = next((b.text for b in response.content if b.type == "text"), "")
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    try:
        events = json.loads(text)
        if not isinstance(events, list):
            events = []
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse error: {e}")
        print(f"  Raw response: {text[:500]}")
        events = []

    return events, usage


# ── budget guard ───────────────────────────────────────────────────────────────

class BudgetGuard:
    def __init__(self, budget: float):
        self.budget = budget
        self.total_input = 0
        self.total_output = 0

    @property
    def spent(self) -> float:
        return (self.total_input * PRICE_INPUT_PER_M / 1_000_000 +
                self.total_output * PRICE_OUTPUT_PER_M / 1_000_000)

    def add(self, usage: dict):
        self.total_input += usage["input_tokens"]
        self.total_output += usage["output_tokens"]

    def check(self, est_input: int, est_output: int = 2000):
        projected = self.spent + (
            est_input * PRICE_INPUT_PER_M / 1_000_000 +
            est_output * PRICE_OUTPUT_PER_M / 1_000_000
        )
        if projected > self.budget:
            sys.exit(
                f"BUDGET EXCEEDED: projected ${projected:.4f} > limit ${self.budget:.2f}. "
                f"Already spent: ${self.spent:.4f}"
            )


# ── Akropolis parser comparison ────────────────────────────────────────────────

def run_akropolis_parser(html_p1: str, html_p2: str) -> list[dict]:
    """Run the existing Akropolis adapter on the same HTML pages."""
    sys.path.insert(0, str(ROOT))
    from pipeline.adapters.html_akropolis import parse

    venue = {"id": "palac-akropolis", "character": []}
    source_config = {
        "base_url": "https://palacakropolis.cz/work/33298",
        "no": "62",
        "own_rooms": ["Velký sál", "Malá scéna", "Jazz bar"],
        "ticket_page_id": "42027",
    }
    genre_cfg = {"section": "hudba"}
    vstupne = {}  # empty — sold_out from vstupne_6 not comparable

    events = []
    for html in [html_p1, html_p2]:
        events.extend(parse(venue, source_config, html, vstupne, genre_cfg))

    return [
        {
            "title": e.title,
            "date": e.date,
            "start_time": e.start_time,
            "room": e.room,
        }
        for e in events
    ]


# ── comparison logic ───────────────────────────────────────────────────────────

def compare_akropolis(llm_events: list[dict], parser_events: list[dict]) -> dict:
    """Compare LLM vs parser events, matching by date+title."""
    # Normalize LLM events (infer year)
    llm_norm = []
    for ev in llm_events:
        date = parse_date_raw(ev.get("date_raw", "") or "")
        llm_norm.append({
            "title": (ev.get("title") or "").strip(),
            "date": date,
            "start_time": ev.get("start_time"),
            "room": ev.get("room"),
        })

    # Build lookup: (date, title_lower) -> event
    def key(ev):
        return (ev["date"], (ev["title"] or "").lower().strip())

    llm_by_key = {key(e): e for e in llm_norm}
    parser_by_key = {key(e): e for e in parser_events}

    all_keys = set(llm_by_key) | set(parser_by_key)

    matches = 0
    missing_in_llm = []     # in parser, not in LLM
    extra_in_llm = []       # in LLM, not in parser
    wrong_time = []
    wrong_room = []

    for k in sorted(all_keys):
        in_llm = k in llm_by_key
        in_parser = k in parser_by_key

        if in_llm and in_parser:
            matches += 1
            lev = llm_by_key[k]
            pev = parser_by_key[k]
            if lev["start_time"] != pev["start_time"]:
                wrong_time.append({
                    "title": k[1], "date": k[0],
                    "llm": lev["start_time"], "parser": pev["start_time"],
                })
            if (lev["room"] or "").lower() != (pev["room"] or "").lower():
                wrong_room.append({
                    "title": k[1], "date": k[0],
                    "llm": lev["room"], "parser": pev["room"],
                })
        elif in_parser and not in_llm:
            missing_in_llm.append(parser_by_key[k])
        elif in_llm and not in_parser:
            extra_in_llm.append(llm_by_key[k])

    return {
        "matches": matches,
        "missing_in_llm": missing_in_llm,
        "extra_in_llm": extra_in_llm,
        "wrong_time": wrong_time,
        "wrong_room": wrong_room,
    }


# ── stability test ─────────────────────────────────────────────────────────────

def stability_test(client, page_text: str, venue_hint: str,
                   budget: BudgetGuard, n: int = 3) -> bool:
    """Run extraction N times and return True if all results are identical."""
    results = []
    for i in range(n):
        est = estimate_tokens(page_text) + 500
        budget.check(est)
        print(f"  Stability run {i + 1}/{n}...")
        events, usage = call_llm(client, page_text, venue_hint)
        budget.add(usage)
        # Normalize for comparison
        norm = sorted(
            [
                (
                    (ev.get("title") or "").strip(),
                    (ev.get("date_raw") or "").strip(),
                    ev.get("start_time"),
                )
                for ev in events
            ]
        )
        results.append(norm)
        print(f"    -> {len(events)} events, tokens: {usage['input_tokens']}in/{usage['output_tokens']}out")

    identical = all(r == results[0] for r in results)
    return identical, results


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    # Fix Windows console encoding for Czech characters
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    _check_api_key()

    import anthropic
    client = anthropic.Anthropic()
    budget = BudgetGuard(BUDGET_USD)

    print(f"\n=== LLM Extraction Test — {TODAY} ===")
    print(f"Model: {MODEL}  (${PRICE_INPUT_PER_M}/M in, ${PRICE_OUTPUT_PER_M}/M out)")
    print(f"Budget: ${BUDGET_USD:.2f}\n")

    # ── load fixtures ─────────────────────────────────────────────────────────
    ak_p1_path = FIXTURE_DIR / "akropolis_hudba_p1.html"
    ak_p2_path = FIXTURE_DIR / "akropolis_hudba_p2.html"
    twist_path = FIXTURE_DIR / "twist_music.html"

    if not ak_p1_path.exists() or not ak_p2_path.exists():
        sys.exit(f"ERROR: Akropolis fixtures not found in {FIXTURE_DIR}")

    ak_p1_html = ak_p1_path.read_text(encoding="utf-8")
    ak_p2_html = ak_p2_path.read_text(encoding="utf-8")
    ak_p1_text = clean_html(ak_p1_html)
    ak_p2_text = clean_html(ak_p2_html)

    twist_html = None
    twist_text = None
    if twist_path.exists():
        twist_html = twist_path.read_text(encoding="utf-8")
        twist_text = clean_html(twist_html)
    else:
        print(f"WARNING: Twist fixture not found at {twist_path}")
        print("  -> Save https://twistbar.co/music as that file and re-run.\n")

    # ── pre-flight token estimates ─────────────────────────────────────────────
    print("--- Token estimates (cleaned text) ---")
    for label, text in [
        ("Akropolis p1", ak_p1_text),
        ("Akropolis p2", ak_p2_text),
    ] + ([("Twist", twist_text)] if twist_text else []):
        t = estimate_tokens(text)
        cost = t * PRICE_INPUT_PER_M / 1_000_000
        print(f"  {label}: ~{t:,} input tokens, est. ${cost:.5f}/call")

    # ── Akropolis extraction ──────────────────────────────────────────────────
    print("\n--- Akropolis: LLM extraction ---")
    all_ak_llm = []
    total_hallucinated = 0

    for label, html, text in [
        ("p1", ak_p1_html, ak_p1_text),
        ("p2", ak_p2_html, ak_p2_text),
    ]:
        est = estimate_tokens(text) + 500
        budget.check(est)
        print(f"  Extracting {label}...")
        events, usage = call_llm(client, text, "Palác Akropolis - hudba")
        budget.add(usage)
        print(f"  -> {len(events)} events, tokens: {usage['input_tokens']}in/{usage['output_tokens']}out, spent: ${budget.spent:.5f}")

        # Verify each event
        source_text = html + " " + text  # search in both HTML and text
        verified = [verify_event(e, source_text) for e in events]
        hallucinated = sum(1 for e in verified for f in e["hallucinated"])
        total_hallucinated += hallucinated
        if hallucinated:
            print(f"  WARNING: {hallucinated} hallucinated field(s) found:")
            for e in verified:
                if e["hallucinated"]:
                    print(f"    '{e.get('title')}': {e['hallucinated']}")

        all_ak_llm.extend(events)

    print(f"\n  Total Akropolis LLM events: {len(all_ak_llm)}, hallucinated fields: {total_hallucinated}")

    # ── Akropolis parser comparison ───────────────────────────────────────────
    print("\n--- Akropolis: Parser vs LLM comparison ---")
    parser_events = run_akropolis_parser(ak_p1_html, ak_p2_html)
    print(f"  Parser found: {len(parser_events)} events")
    print(f"  LLM found:    {len(all_ak_llm)} events")

    comp = compare_akropolis(all_ak_llm, parser_events)
    print(f"\n  Matches (same date+title): {comp['matches']}")
    print(f"  Missing in LLM (parser has, LLM doesn't): {len(comp['missing_in_llm'])}")
    print(f"  Extra in LLM (LLM has, parser doesn't): {len(comp['extra_in_llm'])}")
    print(f"  Wrong start_time: {len(comp['wrong_time'])}")
    print(f"  Wrong room: {len(comp['wrong_room'])}")

    if comp["missing_in_llm"]:
        print("\n  Missing in LLM:")
        for e in comp["missing_in_llm"][:5]:
            print(f"    {e['date']} {e['title']}")

    if comp["extra_in_llm"]:
        print("\n  Extra in LLM (possible hallucinations or parser filtering):")
        for e in comp["extra_in_llm"][:5]:
            print(f"    {e['date']} {e['title']}")

    if comp["wrong_time"]:
        print("\n  Wrong time examples:")
        for e in comp["wrong_time"][:3]:
            print(f"    {e['date']} '{e['title']}': LLM={e['llm']} parser={e['parser']}")

    if comp["wrong_room"]:
        print("\n  Wrong room examples:")
        for e in comp["wrong_room"][:3]:
            print(f"    {e['date']} '{e['title']}': LLM={e['room']} parser={e['parser']}")

    # ── Akropolis stability test ──────────────────────────────────────────────
    print("\n--- Akropolis: Stability test (3x p1) ---")
    ak_stable, ak_runs = stability_test(client, ak_p1_text, "Palác Akropolis - hudba", budget)
    print(f"  Identical results: {ak_stable}")
    if not ak_stable:
        for i, (a, b) in enumerate(zip(ak_runs, ak_runs[1:]), 1):
            diffs = [(x, y) for x, y in zip(a, b) if x != y]
            if diffs:
                print(f"  Run {i} vs {i+1}: {len(diffs)} differences")

    # ── Twist ─────────────────────────────────────────────────────────────────
    twist_events_final = []
    if twist_text:
        print("\n--- Twist: LLM extraction ---")
        est = estimate_tokens(twist_text) + 500
        budget.check(est)
        twist_events, twist_usage = call_llm(client, twist_text, "Twist Bar - music")
        budget.add(twist_usage)
        print(f"  -> {len(twist_events)} events, tokens: {twist_usage['input_tokens']}in/{twist_usage['output_tokens']}out, spent: ${budget.spent:.5f}")

        # Verify
        verified = [verify_event(e, twist_html + " " + twist_text) for e in twist_events]
        hall = sum(1 for e in verified for f in e["hallucinated"])
        if hall:
            print(f"  WARNING: {hall} hallucinated field(s)")

        # Print table
        print(f"\n  Twist events ({len(twist_events)} total):")
        print(f"  {'Date':<12} {'Day':<10} {'Title':<50}")
        print(f"  {'-'*12} {'-'*10} {'-'*50}")
        for ev in twist_events:
            date_str = parse_date_raw(ev.get("date_raw") or "") or (ev.get("date_raw") or "?")
            title = (ev.get("title") or "")[:50]
            # Try to get day of week from date
            dow = ""
            try:
                d = datetime.date.fromisoformat(date_str) if len(date_str) == 10 else None
                dow = d.strftime("%A") if d else ""
            except Exception:
                pass
            print(f"  {date_str:<12} {dow:<10} {title}")

        twist_events_final = twist_events

        # Stability test
        print("\n--- Twist: Stability test (3x) ---")
        tw_stable, _ = stability_test(client, twist_text, "Twist Bar - music", budget)
        print(f"  Identical results: {tw_stable}")

    # ── final summary ─────────────────────────────────────────────────────────
    input_cost = budget.total_input * PRICE_INPUT_PER_M / 1_000_000
    output_cost = budget.total_output * PRICE_OUTPUT_PER_M / 1_000_000

    # Estimate monthly cost at daily run for 15 venues
    # Using the Akropolis extraction calls as the proxy (exclude stability test overhead)
    # Akropolis: 2 extraction calls + Twist: 1 extraction call = 3 extraction calls
    n_extraction_calls = 2 + (1 if twist_events_final else 0)
    n_calls = n_extraction_calls  # calls per run for these venues
    if n_calls > 0 and budget.total_input > 0:
        avg_input = budget.total_input / n_calls
        avg_output = budget.total_output / n_calls
        monthly_input = avg_input * 15 * 30
        monthly_output = avg_output * 15 * 30
        monthly_cost = (monthly_input * PRICE_INPUT_PER_M / 1_000_000 +
                        monthly_output * PRICE_OUTPUT_PER_M / 1_000_000)
    else:
        monthly_cost = 0

    print("\n=== FINAL SUMMARY ===")
    print(f"\nModel: {MODEL}")
    print(f"Price: ${PRICE_INPUT_PER_M}/M input, ${PRICE_OUTPUT_PER_M}/M output")

    print(f"\nToken usage:")
    print(f"  Total input:  {budget.total_input:,} tokens  (${input_cost:.5f})")
    print(f"  Total output: {budget.total_output:,} tokens  (${output_cost:.5f})")
    print(f"  TOTAL COST:   ${budget.spent:.5f}")

    print(f"\nEstimated monthly cost (15 venues, daily):")
    print(f"  {monthly_input:,.0f} input + {monthly_output:,.0f} output tokens/month")
    print(f"  ~${monthly_cost:.3f}/month")

    print(f"\nAccuracy (Akropolis, both pages):")
    total_parser = len(parser_events)
    if total_parser:
        precision = comp["matches"] / max(len(all_ak_llm), 1) * 100
        recall = comp["matches"] / max(total_parser, 1) * 100
        print(f"  Parser events:  {total_parser}")
        print(f"  LLM events:     {len(all_ak_llm)}")
        print(f"  Matches:        {comp['matches']}")
        print(f"  Precision:      {precision:.0f}%")
        print(f"  Recall:         {recall:.0f}%")
        print(f"  Wrong time:     {len(comp['wrong_time'])}")
        print(f"  Wrong room:     {len(comp['wrong_room'])}")
        print(f"  Hallucinated:   {total_hallucinated} field(s)")
        print(f"  Stability (Akropolis): {'PASS' if ak_stable else 'FAIL'}")

    if twist_events_final:
        print(f"\nTwist: {len(twist_events_final)} events extracted")
        print("\n  === Verify 5 random Twist events against web ===")
        import random
        sample = random.sample(twist_events_final, min(5, len(twist_events_final)))
        for ev in sample:
            date = parse_date_raw(ev.get("date_raw") or "") or (ev.get("date_raw") or "?")
            print(f"  {date} | {(ev.get('start_time') or '?'):5} | {ev.get('title', '')}")
        print("  -> Please verify these 5 against https://twistbar.co/music")

    print("\n--- NOTE: Delete or let expire ANTHROPIC_API_KEY after 2026-11-09 ---\n")


if __name__ == "__main__":
    main()
