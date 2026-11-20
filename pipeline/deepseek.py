"""
Task 061: DeepSeek provider (variant A: research, decision and translation
all with DeepSeek).  Task 062: used by the daily run (ENRICH_PROVIDER=deepseek)
for AI enrichment and AI classification; budget per run and per calendar
month (daily_budget / record_spend, state["ai_cost"]).

Same three steps as _Gemini2 (task 059), same validation afterwards
(pipeline.enrich_ai.process_result):

1. research: `deepseek-flash` with tool calls.  The tools `search(query)` and
   `fetch(url)` are executed by our code through the DeepSeek Search / Fetch
   API (https://api-docs.deepseek.com/guides/search/).  Hard limits in code:
   MAX_SEARCHES searches and MAX_FETCHES fetches per event; every query gets
   `-site:ra.co -site:instagram.com`, results from blocked hosts are dropped,
   blocked URLs are never fetched.  Spotify is not searched (ai-rules G).
2. decision: `deepseek-flash` in JSON mode from the research facts, the
   numbered sources and the venue page text (DECIDE_PROMPT, as Gemini).
3. translation CS -> SK, EN: a separate short call (TRANSLATE_PROMPT).

Cost: tokens are priced by the UTC time of each call (peak 01-04 and 06-10
UTC Mon-Fri, https://api-docs.deepseek.com/quick_start/pricing/); every step
also records the peak and off-peak price for the monthly estimate.  Search and
Fetch: $0.75 / 1,000 successful requests.  The run stops at BUDGET_USD and
on HTTP 402 (credit used up).
"""

import datetime
import json
import logging
import os
import re
import threading
import time
import urllib.error
import urllib.request

from pipeline.ai_rules import DECIDE_PROMPT, TRANSLATE_PROMPT
from pipeline.enrich_ai import (ProviderStop, _DECIDE_SCHEMA, _Gemini2, _sum_usage, blocked,
                                build_prompt, canon_url)
from pipeline.fetch import USER_AGENT

log = logging.getLogger(__name__)

API = "https://api.deepseek.com"
MODEL = "deepseek-flash"
# $ per token: (cache hit, cache miss, output), off-peak / peak
PRICES = {"offpeak": (0.003 / 1e6, 0.15 / 1e6, 0.6 / 1e6),
          "peak": (0.006 / 1e6, 0.3 / 1e6, 1.2 / 1e6)}
TOOL_PRICE = 0.75 / 1000            # Search and Fetch, per successful request
PEAK_UTC_HOURS = set(range(1, 4)) | set(range(6, 10))
MAX_SEARCHES = 3
MAX_FETCHES = 2
MAX_TURNS = 8                       # model calls in the research loop
SEARCH_COUNT = 6                    # results per search
SEARCH_SUFFIX = " -site:ra.co -site:instagram.com"
FETCH_CHARS = 6000                  # page text passed to the model
BUDGET_USD = float(os.environ.get("DEEPSEEK_BUDGET_USD") or "1.0")     # test script (061)
RUN_BUDGET_USD = 0.30               # task 062: daily run
MONTH_BUDGET_USD = 5.0              # calendar month (state["ai_cost"]); 3.0 in 062, 5.0 task 085 (Matej 2026-11-20)
MONTHLY_SEARCH_LIMIT = 3000         # searches cost $0.00075; the $ budget is the real limit

RESEARCH_PROMPT_DS = f"""You research one event at a Prague venue with the tools search(query) and fetch(url). Report only facts you found with the tools. Do not decide the event type and do not write prose.

Use AT MOST {MAX_SEARCHES} searches: determine ALL performers; about every MAIN performer find who it is, where from, how they present themselves (band / DJ / producer / live act / theatre company …), genre, releases; find the page of this event (venue website, public Facebook event, ticket presale) for the price (all price levels) and the start time of THIS date. Combine several performers in one search when you can. Only for a concert or a DJ night you may fetch AT MOST {MAX_FETCHES} pages (e.g. the event page or the artist's own page) when the search summaries are not enough. Never use Instagram or ra.co (Resident Advisor). Do not search for Spotify. For a film screening also find the film itself (director, year, country) and its genres as the sources say (e.g. animated, documentary, drama, comedy, horror); for theatre, dance or performance the genre of the piece (e.g. drama / činohra, contemporary dance, dance theatre, puppet theatre, new circus, opera, cabaret).

When done, answer (without a tool call) with short fact lines only (no sentences around them), max ~150 words, each fact with the number of its source [n] from the tool results:
P: <name> | <who / origin> | presents as: <...> | genres: <as the sources say> | releases: <...> [n]
F: <film or piece> | <director / company, year, country> | genres: <as the sources say> [n]
E: url <...> | price <as written> | start <HH:MM> [n]
U: <what you could not find>"""

RESEARCH_RETRY_DS = ("IMPORTANT: you did not search. You MUST use the search tool now (at most "
                     f"{MAX_SEARCHES} searches). Facts from memory are not accepted.")

TOOLS = [
    {"type": "function", "function": {
        "name": "search",
        "description": "Web search. Returns numbered results with title, URL, date and a summary.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Search query, max 90 characters."}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "fetch",
        "description": "Fetch one web page (HTTP/HTTPS URL) and return its text as Markdown.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "The page URL."}},
            "required": ["url"]}}},
]


def is_peak(now: datetime.datetime | None = None) -> bool:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return now.weekday() < 5 and now.hour in PEAK_UTC_HOURS


def token_cost(hit: int, miss: int, out: int, peak: bool) -> float:
    ph, pm, po = PRICES["peak" if peak else "offpeak"]
    return hit * ph + miss * pm + out * po


def balance_usd(key: str | None = None, timeout: int = 15, opener=None) -> float | None:
    """Account balance in USD (task 074), GET /user/balance
    (api-docs.deepseek.com/api/get-user-balance): `balance_infos[]` with
    `currency` (CNY / USD) and `total_balance` (string, granted + topped up).
    None when the key is missing, the call fails or there is no USD entry;
    never raises (a failure must not stop the run)."""
    key = key if key is not None else os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        return None
    req = urllib.request.Request(API + "/user/balance", method="GET",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Accept": "application/json",
                                          "User-Agent": USER_AGENT})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        for info in data.get("balance_infos") or []:
            if str(info.get("currency")).upper() == "USD":
                return round(float(info["total_balance"]), 4)
        log.warning("DeepSeek balance: no USD entry in %s",
                    [i.get("currency") for i in data.get("balance_infos") or []])
    except Exception as exc:   # HTTP error, timeout, bad JSON
        log.warning("DeepSeek balance not available: %s", str(exc)[:200])
    return None


class Budget:
    """Shared spend counter of one run (thread safe)."""

    def __init__(self, limit: float = BUDGET_USD):
        self.limit, self.spent, self._lock = limit, 0.0, threading.Lock()

    def check(self) -> None:
        with self._lock:
            if self.spent >= self.limit:
                raise ProviderStop(f"budget ${self.limit} reached (spent ${self.spent:.4f})")

    def add(self, usd: float) -> None:
        with self._lock:
            self.spent += usd


def daily_budget(state: dict, today: str, run_limit: float | None = None) -> "Budget":
    """Budget of one daily run: min(run limit, month limit - spent this month).

    run_limit: env DEEPSEEK_RUN_BUDGET_USD (workflow input, e.g. 1.40 for the
    one-off recompute), default RUN_BUDGET_USD.  The month spend is the sum
    of the recorded run costs in state["ai_cost"] (pipeline_state.json)."""
    if run_limit is None:
        run_limit = float(os.environ.get("DEEPSEEK_RUN_BUDGET_USD", "").strip() or RUN_BUDGET_USD)
    cost = state.get("ai_cost") or {}
    spent = float(cost.get("usd") or 0) if cost.get("month") == today[:7] else 0.0
    b = Budget(round(max(0.0, min(run_limit, MONTH_BUDGET_USD - spent)), 4))
    b.month_spent_before, b.run_limit = spent, run_limit
    return b


def record_spend(state: dict, today: str, budget: "Budget") -> dict:
    """Add the run's spend to state["ai_cost"] (new month -> starts at 0)."""
    cost = state.get("ai_cost") or {}
    if cost.get("month") != today[:7]:
        cost = {"month": today[:7], "usd": 0.0, "runs": 0}
    cost["usd"] = round(float(cost.get("usd") or 0) + budget.spent, 4)
    cost["runs"] = int(cost.get("runs") or 0) + 1
    state["ai_cost"] = cost
    return cost


class _DeepSeek(_Gemini2):
    """Steps 2-3 and run_from_research / run_event come from _Gemini2; the
    model calls and the research loop are DeepSeek's."""
    name = "deepseek"
    reserve = MAX_SEARCHES
    monthly_search_limit = MONTHLY_SEARCH_LIMIT

    def __init__(self, call=None, tool=None, budget: Budget | None = None,
                 decide_thinking: str | None = None, now=None):
        self.key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        self.model = MODEL
        dt = decide_thinking or os.environ.get("DEEPSEEK_DECIDE_THINKING", "").strip() or "disabled"
        self.conf = {"model": MODEL, "research_thinking": "disabled", "decide_model": MODEL,
                     "decide_thinking": dt, "translate_model": MODEL,
                     "translate_thinking": "disabled"}
        self.prices = (PRICES["peak"][1], PRICES["peak"][2], TOOL_PRICE)
        self.spotify_name = lambda url: None          # Spotify is not searched (ai-rules G)
        self._call = call or self._http_chat
        self._tool = tool or self._http_tool
        self.budget = budget or Budget()
        self._now = now or (lambda: datetime.datetime.now(datetime.timezone.utc))

    @property
    def label(self) -> str:
        return f"{MODEL} (research + tools, decide thinking {self.conf['decide_thinking']})"

    # -- HTTP ---------------------------------------------------------------

    def _post(self, path: str, body: dict, timeout: int) -> tuple[int, dict | str]:
        req = urllib.request.Request(
            API + path, data=json.dumps(body).encode(), method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}",
                     "User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode("utf-8", "replace")[:300]
            if exc.code in (401, 402):                 # 402: prepaid credit used up
                raise ProviderStop(f"HTTP {exc.code}: {msg}")
            return exc.code, msg

    def _http_chat(self, body: dict) -> dict:
        last = None
        for attempt in range(3):
            try:
                code, data = self._post("/chat/completions", body, 180)
            except (urllib.error.URLError, TimeoutError) as exc:
                code, data = 0, f"network: {exc}"
            if code == 200:
                return data
            last = RuntimeError(f"HTTP {code}: {data}")
            if code not in (0, 429, 500, 502, 503, 504):
                raise last
            time.sleep(5 * (attempt + 1))
        raise last

    def _http_tool(self, name: str, body: dict) -> tuple[int, dict | str]:
        for attempt in range(2):
            try:
                code, data = self._post(f"/v1/tools/{name}", body, 60)
            except (urllib.error.URLError, TimeoutError) as exc:
                code, data = 0, f"network: {exc}"
            if code not in (0, 408, 429, 500, 504):
                return code, data
            time.sleep(3 * (attempt + 1))
        return code, data

    # -- model calls --------------------------------------------------------

    def _chat(self, step: str, thinking: str, body: dict) -> tuple[dict, dict]:
        self.budget.check()
        body = {"model": MODEL, **body,
                "thinking": {"type": "enabled" if thinking not in ("disabled", None) else "disabled"}}
        peak = is_peak(self._now())
        data = self._call(body)
        um = data.get("usage") or {}
        hit = um.get("prompt_cache_hit_tokens", 0)
        miss = um.get("prompt_cache_miss_tokens", max(0, um.get("prompt_tokens", 0) - hit))
        out = um.get("completion_tokens", 0)
        u = {"step": step, "model": MODEL, "thinking": thinking,
             "input_tokens": hit + miss, "cached_tokens": hit, "output_tokens": out,
             "reasoning_tokens": (um.get("completion_tokens_details") or {}).get(
                 "reasoning_tokens", 0),
             "peak": peak, "cost_usd": token_cost(hit, miss, out, peak),
             "cost_peak_usd": token_cost(hit, miss, out, True),
             "cost_offpeak_usd": token_cost(hit, miss, out, False)}
        self.budget.add(u["cost_usd"])
        return data, u

    @staticmethod
    def _message(data: dict) -> dict:
        return ((data.get("choices") or [{}])[0]).get("message") or {}

    def _json_call(self, step: str, thinking: str, system: str, user: str,
                   max_tokens: int) -> tuple[dict | None, list]:
        usage = []
        for _ in range(2):          # JSON mode may return blank content -> one retry
            data, u = self._chat(step, thinking, {
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}],
                "response_format": {"type": "json_object"},
                "temperature": 0.1, "max_tokens": max_tokens})
            usage.append(u)
            text = self._message(data).get("content") or ""
            m = re.search(r"\{.*\}", text, re.S)
            if m:
                try:
                    return json.loads(m.group(0)), usage
                except ValueError:
                    pass
        return None, usage

    # -- tools --------------------------------------------------------------

    def _tool_step(self, name: str) -> dict:
        return {"step": name, "model": name, "thinking": None, "input_tokens": 0,
                "cached_tokens": 0, "output_tokens": 0, "reasoning_tokens": 0, "peak": None,
                "cost_usd": TOOL_PRICE, "cost_peak_usd": TOOL_PRICE,
                "cost_offpeak_usd": TOOL_PRICE}

    def _do_search(self, query: str, rec: dict, sources: list, seen: dict) -> str:
        if len(rec["queries"]) >= MAX_SEARCHES:
            return "Search limit reached. Answer now with the fact lines."
        q = " ".join(str(query or "").split())[:128 - len(SEARCH_SUFFIX)] + SEARCH_SUFFIX
        rec["queries"].append(q)
        self.budget.check()
        code, data = self._tool("search", {"query": q, "count": SEARCH_COUNT})
        if code != 200 or not isinstance(data, dict):
            rec["tool_errors"].append(f"search {code}: {str(data)[:120]}")
            return f"Search failed (HTTP {code})."
        results = data.get("results") or []
        if results:                                  # empty results are not billed
            rec["usage"].append(self._tool_step("search"))
            self.budget.add(TOOL_PRICE)
        lines = []
        for r in results:
            url = r.get("url")
            if not url or blocked(url):
                rec["dropped_results"] += 1
                continue
            n = self._source(url, r.get("title"), sources, seen, "search")
            lines.append(f"[{n}] {r.get('title') or ''} | {url} | {r.get('date') or ''}\n"
                         f"{r.get('summary') or r.get('snippet') or ''}")
        return "\n\n".join(lines) or "No results."

    def _do_fetch(self, url: str, rec: dict, sources: list, seen: dict) -> str:
        if len(rec["fetched"]) >= MAX_FETCHES:
            return "Fetch limit reached. Answer now with the fact lines."
        url = str(url or "").strip()
        if not url.startswith("http") or blocked(url):
            return "This URL must not be used."
        rec["fetched"].append(url)
        self.budget.check()
        code, data = self._tool("fetch", {"url": url})
        if code != 200 or not isinstance(data, dict) or not data.get("content"):
            rec["tool_errors"].append(f"fetch {code}: {url}")
            return f"Fetch failed (HTTP {code})."
        rec["usage"].append(self._tool_step("fetch"))
        self.budget.add(TOOL_PRICE)
        n = self._source(url, data.get("title"), sources, seen, "fetch")
        return f"[{n}] {data.get('title') or ''} | {url}\n{data['content'][:FETCH_CHARS]}"

    @staticmethod
    def _source(url: str, title, sources: list, seen: dict, via: str) -> int:
        k = canon_url(url)
        if k not in seen:
            sources.append({"title": title or url, "url": url, "via": via})
            seen[k] = len(sources)
        elif via == "fetch":
            sources[seen[k] - 1]["fetched"] = True
        return seen[k]

    # -- steps --------------------------------------------------------------

    def research(self, ev: dict, venue: dict) -> dict:
        src = next((s.get("url") for s in ev.get("sources", []) if s.get("url")), None)
        user = "\n".join([
            f"Event: {ev.get('title')}",
            f"Venue: {venue.get('name', ev['venue_id'])}, Prague"
            + (f" ({venue['website']})" if venue.get("website") else ""),
            f"Date: {ev.get('date')}",
            f"Event page at the venue: {src or '(none)'}",
        ])
        rec = {"text": "", "queries": [], "fetched": [], "sources": [], "usage": [],
               "retried": False, "searched": False, "kworb": [], "tool_errors": [],
               "dropped_results": 0, "model": MODEL, "thinking": "disabled"}
        sources: list = []
        seen: dict = {}
        msgs = [{"role": "system", "content": RESEARCH_PROMPT_DS},
                {"role": "user", "content": user}]
        for turn in range(MAX_TURNS):
            last = turn == MAX_TURNS - 1
            data, u = self._chat("research", "disabled", {
                "messages": msgs, "tools": TOOLS, "tool_choice": "none" if last else "auto",
                "temperature": 0.2, "max_tokens": 1500})
            rec["usage"].append(u)
            msg = self._message(data)
            calls = msg.get("tool_calls") or []
            if not calls:
                if not rec["queries"] and not rec["retried"]:
                    rec["retried"] = True
                    msgs += [{"role": "assistant", "content": msg.get("content") or ""},
                             {"role": "user", "content": RESEARCH_RETRY_DS}]
                    continue
                rec["text"] = (msg.get("content") or "").strip()
                break
            msgs.append({"role": "assistant", "content": msg.get("content") or "",
                         "tool_calls": calls})
            for c in calls:
                fn = c.get("function") or {}
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except ValueError:
                    args = {}
                if fn.get("name") == "search":
                    out = self._do_search(args.get("query"), rec, sources, seen)
                elif fn.get("name") == "fetch":
                    out = self._do_fetch(args.get("url"), rec, sources, seen)
                else:
                    out = "Unknown tool."
                msgs.append({"role": "tool", "tool_call_id": c.get("id"), "content": out})
        rec["searched"] = bool(rec["queries"])
        rec["sources"] = sources
        return rec

    def decide(self, ev: dict, venue: dict, page_text: str | None,
               research: dict) -> tuple[dict, dict]:
        lines = [build_prompt(ev, venue, page_text), "", "RESEARCH FACTS (step 1)",
                 research["text"] or "(nothing found)", "", "SOURCES"]
        for n, s in enumerate(research["sources"], 1):
            lines.append(f"[{n}] {s['title']}: {s['url']}")
        if not research["sources"]:
            lines.append("(none)")
        system = DECIDE_PROMPT + "\n\nJSON keys (JSON schema of the values): " + _DECIDE_SCHEMA
        raw, usage = self._json_call("decide", self.conf["decide_thinking"], system,
                                     "\n".join(lines), 8000)
        if raw is None:
            raise RuntimeError("step 2: no JSON in answer")
        u = usage[0] if len(usage) == 1 else _merge(usage, "decide")
        return raw, u

    def translate(self, cs: str) -> tuple[dict, dict]:
        out, usage = self._json_call("translate", "disabled", TRANSLATE_PROMPT, cs, 3000)
        u = usage[0] if len(usage) == 1 else _merge(usage, "translate")
        out = out or {}
        return {k: out[k] for k in ("sk", "en") if isinstance(out.get(k), str)}, u

    def run_from_research(self, ev: dict, venue: dict, page_text: str | None, r: dict) -> dict:
        rec = super().run_from_research(ev, venue, page_text, r)
        rec["spotify_names"] = {}            # any Spotify link from the model is dropped
        rec["kworb"] = []
        return rec

    def run_event(self, ev: dict, venue: dict, page_text: str | None, max_uses: int = 0) -> dict:
        r = self.research(ev, venue)
        rec = self.run_from_research(ev, venue, page_text, r)
        rec["searches"] = len(r["queries"])
        rec["fetches"] = len(r["fetched"])
        rec["steps"] = r["usage"] + rec["steps"]
        return _sum_usage(rec)


def _merge(usage: list, step: str) -> dict:
    u = {"step": step, "model": MODEL, "thinking": usage[0]["thinking"], "peak": usage[0]["peak"]}
    for k in ("input_tokens", "cached_tokens", "output_tokens", "reasoning_tokens", "cost_usd",
              "cost_peak_usd", "cost_offpeak_usd"):
        u[k] = sum(x[k] for x in usage)
    return u
