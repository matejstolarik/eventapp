"""
AI event classification — layer 2 (Claude Haiku).

Classifies events that layer 1 could not determine:
  - formats == ["music"]  (music event, live/dj unknown)
  - formats == []          (layer 1 gave up entirely)

Manual overrides and source/keyword classifications are preserved and never
re-classified by AI.

Cache: AI results are stored in events.json (classification.method == "llm").
On subsequent pipeline runs, results are loaded from previous_events and
re-used without calling the API (unless the event title changes).

Configuration:
  ENRICH_PROVIDER   env var — "deepseek" (task 062, daily run): DeepSeek in
  JSON mode with the run / month budget; otherwise Claude Haiku.
  ANTHROPIC_API_KEY / DEEPSEEK_API_KEY — without the key (or on HTTP 401/402,
  budget reached) no API call is made, but cached AI results are still
  applied (task 062: genres from the cache are never lost).
  AI_MAX_CALLS      env var — max API calls per run (default 50)
  AI_MAX_TOKENS     env var — max total tokens per run (default 200000)
"""

import json
import logging
import os
import time as _time

import anthropic

from pipeline.ai_rules import RULES_TYPE, TYPE_EXAMPLES
from pipeline.classify import venue_genre_ids
from pipeline.genres import MUSIC_GENRES

log = logging.getLogger(__name__)

MODEL = "claude-haiku-5-5"
INPUT_PRICE_PER_MTOK = 0.10   # USD per million input tokens
OUTPUT_PRICE_PER_MTOK = 0.50  # USD per million output tokens (up to 100K prompt)

BATCH_SIZE = 20

VALID_FORMATS = frozenset({
    "concert", "dj", "party", "music", "dance", "talk", "comedy", "workshop",
    "theatre", "film", "opening", "quiz", "performance", "other",
})
VALID_GENRES = MUSIC_GENRES   # task 058: lists live in pipeline/genres.py

_CLASSIFY_TOOL = {
    "name": "classify_events",
    "description": (
        "Classify event formats and genres for a batch of Prague events. "
        "Return one entry per event in the same order as the input."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "classifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "event_index": {
                            "type": "integer",
                            "description": "0-based index of the event in the input list.",
                        },
                        "formats": {
                            "type": "array",
                            "description": (
                                "Event format(s). Multiple allowed (e.g. [\"concert\", \"dj\"] "
                                "for a concert with a DJ afterparty)."
                            ),
                            "items": {"type": "string", "enum": sorted(VALID_FORMATS)},
                        },
                        "genres": {
                            "type": "array",
                            "description": (
                                "Musical genres — only include items from the fixed list and "
                                "only when confident. Empty list if unsure."
                            ),
                            "items": {"type": "string", "enum": sorted(VALID_GENRES)},
                        },
                        "primary_format": {
                            "type": "string",
                            "enum": sorted(VALID_FORMATS),
                            "description": (
                                "The ONE format of the main part of the event (the main "
                                "performer decides); must be one of formats."
                            ),
                        },
                        "party_reason": {
                            "type": "string",
                            "description": (
                                "Required when formats include \"party\": short reason "
                                "(max ~15 words) why this is a commercial/mainstream party."
                            ),
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence 0–1 for the format classification.",
                        },
                    },
                    "required": ["event_index", "formats", "primary_format", "confidence"],
                },
            }
        },
        "required": ["classifications"],
        "additionalProperties": False,
    },
}

# task 058: rules from docs/ai-rules.md (pipeline/ai_rules.py)
_SYSTEM_PROMPT = f"""You classify events at music and culture venues in Prague from the event data only (no web search). Prefer specific formats over "music" or "other".

{RULES_TYPE}

{TYPE_EXAMPLES}

Genres: only from the fixed list, ordered from the main genre, only when the event data supports them (synonyms only, never a parent genre automatically: metalcore is not metal). Empty list is fine."""



def classify_events_ai(
    events: list[dict],
    venues: list[dict],
    previous_events: list[dict] | None = None,
    max_calls: int | None = None,
    max_tokens: int | None = None,
    budget=None,
    call=None,
) -> tuple[list[dict], dict]:
    """AI classification for events layer 1 could not determine.

    Returns (events, stats).  events are mutated in-place.
    stats keys: cache_hits, api_calls, errors, total_input_tokens,
                total_output_tokens, estimated_cost_usd, skipped (bool).
    """
    if max_calls is None:
        max_calls = int(os.environ.get("AI_MAX_CALLS", 50))
    if max_tokens is None:
        max_tokens = int(os.environ.get("AI_MAX_TOKENS", 200_000))

    venues_map = {v["id"]: v for v in venues}

    ai_cache = _build_ai_cache(previous_events or [])

    keep = venue_genre_ids(events)            # task 063: venue genres win
    to_classify = _events_needing_ai(events)
    log.info("[classify_ai]: %d events need AI classification", len(to_classify))

    # Apply cache
    cache_hits = 0
    still_need: list[dict] = []
    for event in to_classify:
        cached = ai_cache.get(event["id"])
        if cached and cached.get("title") == event.get("title"):
            _apply_ai_result(event, cached["formats"], cached.get("genres", []),
                             cached["confidence"], cached.get("reason"),
                             cached.get("primary_format"), event["id"] in keep)
            cache_hits += 1
        else:
            still_need.append(event)

    log.info("[classify_ai]: %d cache hits, %d to classify via API",
             cache_hits, len(still_need))

    # task 062: the cache is applied above in every case; only the API calls
    # depend on the provider and its key
    provider = (os.environ.get("ENRICH_PROVIDER") or "claude").strip().lower()
    deepseek = None
    client = None
    why = None
    if call is not None:
        pass
    elif provider == "deepseek":
        if not (os.environ.get("DEEPSEEK_API_KEY") or "").strip():
            why = "DEEPSEEK_API_KEY not set"
        elif budget is None:
            why = "DeepSeek budget unavailable (pipeline state not loaded)"
        else:
            from pipeline.deepseek import _DeepSeek
            deepseek = _DeepSeek(budget=budget)
    else:
        api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
        if api_key:
            client = anthropic.Anthropic(api_key=api_key)
        else:
            why = "ANTHROPIC_API_KEY not set"
    if why:
        log.warning("[classify_ai]: %s — no API calls, %d cache hits applied", why, cache_hits)
        return events, {"skipped": True, "reason": why, "cache_hits": cache_hits,
                        "to_classify": len(still_need)}
    if call is None:
        call = ((lambda b, v: _call_deepseek(deepseek, b, v)) if deepseek
                else (lambda b, v: _call_api_with_retry(client, b, v)))

    total_input = 0
    total_output = 0
    api_calls = 0
    errors = 0
    cost = 0.0
    stopped = None
    total_batches = (len(still_need) + BATCH_SIZE - 1) // BATCH_SIZE if still_need else 0

    for batch_idx, i in enumerate(range(0, len(still_need), BATCH_SIZE)):
        batch_num = batch_idx + 1
        if api_calls >= max_calls:
            log.warning("[classify_ai]: max_calls=%d reached, stopping early", max_calls)
            break
        if total_input + total_output >= max_tokens:
            log.warning("[classify_ai]: max_tokens=%d reached, stopping early", max_tokens)
            break

        batch = still_need[i : i + BATCH_SIZE]
        batch_venues = {e["venue_id"]: venues_map.get(e["venue_id"], {}) for e in batch}

        try:
            results, usage = call(batch, batch_venues)
            api_calls += 1
            total_input += usage.input_tokens
            total_output += usage.output_tokens
            cost += getattr(usage, "cost_usd", None) or (
                usage.input_tokens / 1_000_000 * INPUT_PRICE_PER_MTOK
                + usage.output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MTOK)
            _apply_batch_results(batch, results, keep)
        except Exception as exc:
            if exc.__class__.__name__ == "ProviderStop":     # HTTP 401/402, budget
                stopped = str(exc)[:200]
                log.warning("[classify_ai]: stopped: %s", stopped)
                break
            cause = f" (cause: {exc.__cause__})" if exc.__cause__ else ""
            log.warning(
                "[classify_ai]: API call %d/%d failed: %s: %s%s — batch skipped",
                batch_num, total_batches, type(exc).__name__, exc, cause,
            )
            errors += 1

    stats = {
        "skipped": False,
        "provider": "deepseek" if deepseek else ("claude" if client else "test"),
        "stopped": stopped,
        "cache_hits": cache_hits,
        "api_calls": api_calls,
        "errors": errors,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "estimated_cost_usd": round(cost, 6),
    }
    log.info(
        "[classify_ai]: done — %d cache hits, %d API calls, %d errors, "
        "%.0f in + %.0f out tokens, $%.4f",
        cache_hits, api_calls, errors, total_input, total_output, cost,
    )
    return events, stats


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _events_needing_ai(events: list[dict]) -> list[dict]:
    """Return events the AI classifies: all but manual ones (task 063).
    Layer-1 types (source, keyword) stay when the AI returns nothing."""
    result = []
    for ev in events:
        cls = ev.get("classification")
        # task 063 (docs/ai-rules.md B7): the AI type wins over the venue
        # category (source) and title keywords; only manual is never sent
        if cls and cls.get("method") == "manual":
            continue
        result.append(ev)
    return result


def _build_ai_cache(previous_events: list[dict]) -> dict:
    """Build event_id -> cached AI result from a previous pipeline output.

    Every LLM-classified event is cached; it is re-sent to the API only when
    its title changes (checked by the caller).

    Task 052: the one-time 'party' re-evaluation trigger from task 020 was
    removed.  It excluded music events without 'party' from the cache, but the
    AI legitimately withholds 'party' for many of them, so the same ~90-130
    events were re-classified on every run.
    """
    cache: dict[str, dict] = {}
    for ev in previous_events:
        cls = ev.get("classification")
        # task 054: "llm+web" = verified by the AI enrichment step (cached too)
        if not (cls and cls.get("method") in ("llm", "llm+web")):
            continue
        if "primary_format" not in ev:
            # Task 053: classified before primary_format / the new party
            # definition existed -> re-classify once.  Every event written by
            # the new pipeline has the key (value may be null), so this ends
            # after one successful run.
            continue
        cache[ev["id"]] = {
            "title": ev.get("title"),
            "formats": ev.get("formats", []),
            "genres": ev.get("genres", []),
            "confidence": cls.get("confidence", 0.5),
            "reason": cls.get("reason"),
            "primary_format": ev.get("primary_format"),
        }
    return cache


def _apply_ai_result(
    event: dict,
    formats: list,
    genres: list,
    confidence: float,
    reason: str | None = None,
    primary_format: str | None = None,
    keep_genres: bool = False,
) -> None:
    event["formats"] = formats
    event["primary_format"] = primary_format if primary_format in formats else None
    if genres and not (keep_genres and event.get("genres")):   # task 063: venue genres win
        event["genres"] = genres
    cls = {"method": "llm", "confidence": round(confidence, 2)}
    if reason:
        cls["reason"] = reason
    event["classification"] = cls


def _apply_batch_results(batch: list[dict], results: list[dict],
                         keep: set | None = None) -> None:
    """Apply tool-use results to events in batch order."""
    for entry in results:
        idx = entry.get("event_index")
        if idx is None or not (0 <= idx < len(batch)):
            continue
        event = batch[idx]
        raw_formats = entry.get("formats", [])
        raw_genres = entry.get("genres", [])
        confidence = float(entry.get("confidence", 0.5))

        fmts = [f for f in raw_formats if f in VALID_FORMATS]
        genres = [g for g in raw_genres if g in VALID_GENRES]

        invalid_fmts = [f for f in raw_formats if f not in VALID_FORMATS]
        invalid_genres = [g for g in raw_genres if g not in VALID_GENRES]
        if invalid_fmts:
            log.warning("[classify_ai]: invalid formats discarded %s for '%s'",
                        invalid_fmts, event.get("title"))
        if invalid_genres:
            log.warning("[classify_ai]: invalid genres discarded %s for '%s'",
                        invalid_genres, event.get("title"))

        reason = (entry.get("party_reason") or "").strip() or None
        if "party" in fmts and not reason:
            # Task 053: "party" needs an explicit reason, otherwise it is dropped.
            log.warning("[classify_ai]: 'party' without party_reason dropped for '%s'",
                        event.get("title"))
            fmts = [f for f in fmts if f != "party"]
        if "party" not in fmts:
            reason = None

        primary = entry.get("primary_format")
        if primary not in fmts:
            if primary:
                log.warning("[classify_ai]: primary_format %r not in formats %s for '%s'",
                            primary, fmts, event.get("title"))
            primary = None

        if fmts:
            _apply_ai_result(event, fmts, genres, confidence, reason, primary,
                             event["id"] in (keep or set()))
        else:
            log.warning("[classify_ai]: no valid formats in AI result for '%s'",
                        event.get("title"))


def _call_api_with_retry(
    client: anthropic.Anthropic,
    batch: list[dict],
    venues: dict,
    max_retries: int = 3,
    base_delay: float = 5.0,
) -> tuple[list[dict], object]:
    """Call API with retry on network errors, rate limits and 5xx responses."""
    for attempt in range(max_retries):
        try:
            return _call_api(client, batch, venues)
        except anthropic.APIConnectionError as exc:
            if attempt >= max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            log.warning(
                "[classify_ai]: connection error (attempt %d/%d), retry in %.0fs: %s",
                attempt + 1, max_retries, delay, exc,
            )
            _time.sleep(delay)
        except anthropic.RateLimitError:
            if attempt >= max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            log.warning(
                "[classify_ai]: rate limit 429 (attempt %d/%d), retry in %.0fs",
                attempt + 1, max_retries, delay,
            )
            _time.sleep(delay)
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500 and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                log.warning(
                    "[classify_ai]: HTTP %d (attempt %d/%d), retry in %.0fs",
                    exc.status_code, attempt + 1, max_retries, delay,
                )
                _time.sleep(delay)
            else:
                raise
    raise RuntimeError("unreachable")  # pragma: no cover


def _call_api(
    client: anthropic.Anthropic,
    batch: list[dict],
    venues: dict,
) -> tuple[list[dict], object]:
    """One API call to classify a batch of events. Returns (results_list, usage)."""
    prompt = _build_prompt(batch, venues)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        output_config={"effort": "low"},
        system=_SYSTEM_PROMPT,
        tools=[_CLASSIFY_TOOL],
        tool_choice={"type": "tool", "name": "classify_events"},
        messages=[{"role": "user", "content": prompt}],
    )

    if response.stop_reason == "max_tokens":
        raise RuntimeError("Response truncated by max_tokens")

    for block in response.content:
        if block.type == "tool_use" and block.name == "classify_events":
            classifications = block.input.get("classifications", [])
            return classifications, response.usage

    raise RuntimeError(
        f"No classify_events tool_use block in response "
        f"(stop_reason={response.stop_reason})"
    )


class _Usage:
    def __init__(self, inp: int, out: int, cost: float):
        self.input_tokens, self.output_tokens, self.cost_usd = inp, out, cost


def _call_deepseek(prov, batch: list[dict], venues: dict) -> tuple[list[dict], "_Usage"]:
    """task 062: same prompt and schema as the Claude tool, DeepSeek JSON mode."""
    system = (_SYSTEM_PROMPT + "\n\nAnswer with ONLY one JSON object of this JSON schema: "
              + json.dumps(_CLASSIFY_TOOL["input_schema"], ensure_ascii=False))
    out, usage = prov._json_call("classify", "disabled", system, _build_prompt(batch, venues), 4096)
    u = _Usage(sum(x["input_tokens"] for x in usage), sum(x["output_tokens"] for x in usage),
               sum(x["cost_usd"] for x in usage))
    if not isinstance(out, dict) or not isinstance(out.get("classifications"), list):
        raise RuntimeError("DeepSeek: no classifications in JSON answer")
    return out["classifications"], u


def _build_prompt(batch: list[dict], venues: dict) -> str:
    lines = [f"Classify these {len(batch)} events from Prague venues:\n"]
    for i, ev in enumerate(batch):
        venue = venues.get(ev["venue_id"], {})
        venue_name = venue.get("name", ev["venue_id"])
        venue_types = ", ".join(venue.get("type") or [])
        venue_music = ", ".join(venue.get("music") or [])
        venue_char = ", ".join(venue.get("character") or [])

        section = next(
            (s["section"] for s in ev.get("sources", []) if s.get("section")), None
        )

        parts = [f"[{i}] {ev.get('title', '')}"]
        parts.append(
            f"    Venue: {venue_name}"
            + (f" ({venue_types})" if venue_types else "")
            + (f"; music: {venue_music}" if venue_music else "")
            + (f"; character: {venue_char}" if venue_char else "")
        )
        if section:
            parts.append(f"    Section: {section}")
        if (ev.get("classification") or {}).get("method") in ("source", "keyword")                 and ev.get("formats"):
            # task 063: the venue category is a hint only; the performer decides (B7)
            parts.append(f"    Venue category: {', '.join(ev['formats'])}")
        if ev.get("start_time"):
            parts.append(f"    Start time: {ev['start_time']}")
        if ev.get("artists"):
            parts.append(f"    Artists: {', '.join(ev['artists'][:5])}")
        lines.extend(parts)
        lines.append("")

    return "\n".join(lines)
