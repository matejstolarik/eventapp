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
  ANTHROPIC_API_KEY env var — required for AI layer; pipeline continues
  without it (warning in job summary).
  AI_MAX_CALLS      env var — max API calls per run (default 50)
  AI_MAX_TOKENS     env var — max total tokens per run (default 200000)
"""

import json
import logging
import os
import time as _time

import anthropic

log = logging.getLogger(__name__)

MODEL = "claude-haiku-5-5"
INPUT_PRICE_PER_MTOK = 0.10   # USD per million input tokens
OUTPUT_PRICE_PER_MTOK = 0.50  # USD per million output tokens (up to 100K prompt)

BATCH_SIZE = 20

VALID_FORMATS = frozenset({
    "live", "dj", "music", "dance", "talk", "comedy", "workshop",
    "theatre", "film", "opening", "quiz", "other",
})
VALID_GENRES = frozenset({
    "ambient", "bassline", "drum-and-bass", "dubstep", "ebm", "electro", "electro-swing",
    "electronic", "experimental", "folk", "funk", "hip-hop", "house", "indie", "jazz",
    "metal", "pop", "post-punk", "punk", "reggae", "rock", "shoegaze", "tech-house",
    "techno", "uk-bass", "uk-garage", "world",
})

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
                                "Event format(s). Multiple allowed (e.g. [\"live\", \"dj\"] "
                                "for a concert+club night)."
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
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence 0–1 for the format classification.",
                        },
                    },
                    "required": ["event_index", "formats", "confidence"],
                },
            }
        },
        "required": ["classifications"],
        "additionalProperties": False,
    },
}

_SYSTEM_PROMPT = """\
You classify events at music and culture venues in Prague.

Formats:
- live: live musicians/band on stage
- dj: DJ set or electronic music performance
- music: musical event but cannot determine if live or DJ (use as last resort)
- dance: dance show/performance
- talk: lecture, debate, reading, panel discussion
- comedy: stand-up comedy
- workshop: hands-on workshop or class
- theatre: theatrical performance or play
- film: film screening
- opening: art vernissage / exhibition opening
- quiz: pub quiz
- other: does not fit any category above

An event may have multiple formats (e.g. ["live", "dj"] for a concert that becomes a club night).
Prefer specific formats over "music" or "other".
For genres, only add items you are confident about — empty list is fine.\
"""


def classify_events_ai(
    events: list[dict],
    venues: list[dict],
    previous_events: list[dict] | None = None,
    max_calls: int | None = None,
    max_tokens: int | None = None,
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

    api_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        log.warning("[classify_ai]: ANTHROPIC_API_KEY not set — skipping AI layer")
        return events, {"skipped": True, "reason": "ANTHROPIC_API_KEY not set"}

    client = anthropic.Anthropic(api_key=api_key)
    venues_map = {v["id"]: v for v in venues}

    ai_cache = _build_ai_cache(previous_events or [])

    to_classify = _events_needing_ai(events)
    log.info("[classify_ai]: %d events need AI classification", len(to_classify))

    # Apply cache
    cache_hits = 0
    still_need: list[dict] = []
    for event in to_classify:
        cached = ai_cache.get(event["id"])
        if cached and cached.get("title") == event.get("title"):
            _apply_ai_result(event, cached["formats"], cached.get("genres", []),
                             cached["confidence"])
            cache_hits += 1
        else:
            still_need.append(event)

    log.info("[classify_ai]: %d cache hits, %d to classify via API",
             cache_hits, len(still_need))

    total_input = 0
    total_output = 0
    api_calls = 0
    errors = 0
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
            results, usage = _call_api_with_retry(client, batch, batch_venues)
            api_calls += 1
            total_input += usage.input_tokens
            total_output += usage.output_tokens
            _apply_batch_results(batch, results)
        except Exception as exc:
            cause = f" (cause: {exc.__cause__})" if exc.__cause__ else ""
            log.warning(
                "[classify_ai]: API call %d/%d failed: %s: %s%s — batch skipped",
                batch_num, total_batches, type(exc).__name__, exc, cause,
            )
            errors += 1

    cost = (total_input / 1_000_000 * INPUT_PRICE_PER_MTOK +
            total_output / 1_000_000 * OUTPUT_PRICE_PER_MTOK)

    stats = {
        "skipped": False,
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
    """Return events that layer 1 did not classify (AI should handle)."""
    result = []
    for ev in events:
        cls = ev.get("classification")
        if cls and cls.get("method") in ("manual", "source", "keyword"):
            continue
        result.append(ev)
    return result


def _build_ai_cache(previous_events: list[dict]) -> dict:
    """Build event_id → cached AI result from a previous pipeline output."""
    cache: dict[str, dict] = {}
    for ev in previous_events:
        cls = ev.get("classification")
        if cls and cls.get("method") == "llm":
            cache[ev["id"]] = {
                "title": ev.get("title"),
                "formats": ev.get("formats", []),
                "genres": ev.get("genres", []),
                "confidence": cls.get("confidence", 0.5),
            }
    return cache


def _apply_ai_result(event: dict, formats: list, genres: list, confidence: float) -> None:
    event["formats"] = formats
    if genres:
        event["genres"] = genres
    event["classification"] = {"method": "llm", "confidence": round(confidence, 2)}


def _apply_batch_results(batch: list[dict], results: list[dict]) -> None:
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

        if fmts:
            _apply_ai_result(event, fmts, genres, confidence)
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
        if ev.get("start_time"):
            parts.append(f"    Start time: {ev['start_time']}")
        if ev.get("artists"):
            parts.append(f"    Artists: {', '.join(ev['artists'][:5])}")
        lines.extend(parts)
        lines.append("")

    return "\n".join(lines)
