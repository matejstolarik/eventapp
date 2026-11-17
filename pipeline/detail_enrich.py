"""Post-processing step: fetch missing description / image_url from event detail pages.

For events that:
  - have a source URL that differs from the venue's configured listing URL(s), AND
  - are missing description or image_url, AND
  - have not already been enriched (checked via previous_events cache)

we fetch the detail page once per event per pipeline run, extract description and
image_url, then propagate the result through events.json so the next run can skip
the fetch entirely.

Task 054: the same detail page also gives price_text (venues in PRICE_VENUES)
and a missing start_time (venues in TIME_VENUES), exactly as the page states
it.  Pages are re-checked for a missing price at most every PRICE_RECHECK_DAYS
days (state["detail_checked"], kept between runs in site/pipeline_state.json).
The page text is also kept in memory (page_texts) for the AI enrichment step.

Limits:
  - NEW_DETAILS_PER_VENUE new detail fetches per venue per run (default 40)
  - standard robots.txt, rate limiting, 1 s between requests to same host
  - Resident Advisor (ra.co) is never fetched
  - Bike Jesus main-page source URL is skipped (not an individual event page)
"""

import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup

from pipeline.fetch import USER_AGENT, _robots_allowed, _rate_limit
from pipeline.adapters.jsonld import (
    _all_ld_items, _is_event, _clean_description, _resolve_image,
)

log = logging.getLogger(__name__)

NEW_DETAILS_PER_VENUE = 40
_DESC_MAX = 1000

# Venues whose event pages state the price in a labelled line (verified
# 2026-11-17, task 054).  Fuchs2 (ra.co tickets only), Forum Karlín
# (Ticketmaster/Ticketportal buttons only) and Bike Jesus (Strapi API, no
# price field) do not show a price.  Archa+ and Akropolis give only "free
# entry", handled in their adapters.
PRICE_VENUES = frozenset({
    "cross-club", "epic", "roxy", "meetfactory", "kasarna-karlin", "citarna-unijazz",
})
# Venues whose adapter often has no start time but the event page has it.
TIME_VENUES = frozenset({"cross-club"})
PRICE_RECHECK_DAYS = 7
PAGE_TEXT_MAX = 6000

_BLOCK_TAGS = ["p", "div", "br", "li", "tr", "td", "th", "h1", "h2", "h3", "h4",
               "h5", "h6", "section", "article", "header", "footer", "dd", "dt"]
_PRICE_TOKEN = re.compile(
    r"\d[\d  .]*\s*(?:kč|czk|,-|eur|€)|\bzdarma\b|\bfree\b|\bvoln[ýy]\b|\bdobrovoln",
    re.I)
_PRICE_LABEL = re.compile(
    r"(?:^|[.!?]\s*)((?:základní\s+)?(?:vstupné|vstupenky|vstup|admission|entry))\b[ \t]*:?[ \t]*(.*)$",
    re.I)
_START_LABEL = re.compile(r"^Začátek:\s*([01]?\d|2[0-3]):([0-5]\d)\b")


def enrich_missing_details(
    events: list,
    previous_events: dict,
    venues: list,
    check_prices: bool = False,
    state: "dict | None" = None,
    today: "str | None" = None,
    page_texts: "dict | None" = None,
) -> tuple[list, dict]:
    """Fetch missing description / image_url (and, with check_prices, price_text
    and a missing start_time) from event detail pages.

    state: pipeline state dict (mutated): state["detail_checked"][event_id] =
    date of the last page check made because of a missing price/time.
    page_texts: dict filled with event_id -> plain page text (for the AI step).

    Returns (enriched_events, stats_dict).
    """
    listing_urls = _build_listing_urls(venues)
    venue_desc_selectors = _build_venue_desc_selectors(venues)
    checked = (state if state is not None else {}).setdefault("detail_checked", {})

    stats = {
        "fetched": 0,
        "cache_hits": 0,
        "skipped": 0,
        "errors": 0,
        "price_found": 0,
        "time_found": 0,
    }

    # Count new fetches per venue to enforce the per-venue limit
    new_fetches: dict[str, int] = {}

    result: list = []
    for ev in events:
        venue_id = ev.get("venue_id", "")
        ev_id = ev.get("id", "")

        needs_desc = not ev.get("description")
        needs_img = not ev.get("image_url")
        needs_price = check_prices and venue_id in PRICE_VENUES and not ev.get("price_text")
        needs_time = check_prices and venue_id in TIME_VENUES and not ev.get("start_time")

        if not (needs_desc or needs_img or needs_price or needs_time):
            result.append(ev)
            continue

        sources = ev.get("sources", [])
        detail_url = sources[0].get("url") if sources else None

        if not detail_url:
            stats["skipped"] += 1
            result.append(ev)
            continue

        # Skip listing URLs (same URL shared by all events of a venue)
        if detail_url in listing_urls.get(venue_id, set()):
            stats["skipped"] += 1
            result.append(ev)
            continue

        # Never fetch Resident Advisor
        if "ra.co" in detail_url:
            stats["skipped"] += 1
            result.append(ev)
            continue

        # Cache check: reuse from previous pipeline run
        prev = previous_events.get(ev_id)
        event_title = ev.get("title", "")
        has_custom_selector = venue_id in venue_desc_selectors
        if prev:
            prev_sources = prev.get("sources", [])
            prev_url = prev_sources[0].get("url") if prev_sources else None
            if prev_url == detail_url:
                ev = dict(ev)
                filled = False
                if needs_desc and prev.get("description"):
                    prev_desc = prev["description"]
                    # Skip cached desc if venue has a custom selector (old extraction may be wrong)
                    # or if the cached description equals the event title (not a real description)
                    is_title_only = prev_desc.strip().lower() == event_title.strip().lower()
                    # task 054: an AI description is not a source description
                    is_ai = prev.get("description_source") == "ai"
                    if not has_custom_selector and not is_title_only and not is_ai:
                        ev["description"] = prev_desc
                        ev["description_source"] = prev.get("description_source", "source")
                        needs_desc = False
                        filled = True
                if needs_img and prev.get("image_url"):
                    ev["image_url"] = prev["image_url"]
                    needs_img = False
                    filled = True
                # price / time taken from the page in an earlier run (not AI values)
                prev_ai = prev.get("enrichment") or {}
                if needs_price and prev.get("price_text") and "price_text" not in prev_ai:
                    ev["price_text"] = prev["price_text"]
                    needs_price = False
                    filled = True
                if needs_time and prev.get("start_time") and "start_time" not in prev_ai:
                    ev["start_time"] = prev["start_time"]
                    needs_time = False
                    filled = True
                if filled:
                    stats["cache_hits"] += 1
                if not (needs_desc or needs_img or needs_price or needs_time):
                    result.append(ev)
                    continue

        # Price/time only: do not re-fetch a page checked in the last days
        if not needs_desc and not needs_img and _checked_recently(checked.get(ev_id), today):
            result.append(ev)
            continue

        # Per-venue limit on new fetches
        if new_fetches.get(venue_id, 0) >= NEW_DETAILS_PER_VENUE:
            result.append(ev)
            continue

        # Robots.txt check
        try:
            if not _robots_allowed(detail_url):
                log.warning("detail_enrich: robots.txt disallows %s — skipping", detail_url)
                stats["skipped"] += 1
                result.append(ev)
                continue
        except Exception:
            pass

        # Rate limit (1 s per host)
        try:
            _rate_limit(detail_url)
        except Exception:
            pass

        # Fetch detail page
        try:
            resp = requests.get(
                detail_url,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            resp.raise_for_status()
            html = resp.text
            new_fetches[venue_id] = new_fetches.get(venue_id, 0) + 1
            stats["fetched"] += 1
        except Exception as exc:
            log.warning("detail_enrich: %s fetch failed: %s", detail_url, exc)
            stats["errors"] += 1
            result.append(ev)
            continue

        selector = venue_desc_selectors.get(venue_id)
        enriched = _extract_from_page(html, detail_url, selector=selector)
        ev = dict(ev)
        if needs_desc and enriched.get("description"):
            desc = enriched["description"]
            # Discard if description equals the event title (not a real description)
            if desc.strip().lower() != event_title.strip().lower():
                ev["description"] = desc
                ev["description_source"] = "source"
        if needs_img and enriched.get("image_url"):
            ev["image_url"] = enriched["image_url"]

        if needs_price or needs_time:
            lines = page_lines(html)
            if needs_price:
                price = extract_price(lines)
                if price:
                    ev["price_text"] = price
                    stats["price_found"] += 1
            if needs_time:
                st = extract_start_time(lines)
                if st:
                    ev["start_time"] = st
                    stats["time_found"] += 1
            if today:
                checked[ev_id] = today
        if page_texts is not None:
            page_texts[ev_id] = page_text(html)

        result.append(ev)

    log.info(
        "detail_enrich: fetched=%d cache_hits=%d skipped=%d errors=%d price_found=%d time_found=%d",
        stats["fetched"], stats["cache_hits"], stats["skipped"], stats["errors"],
        stats["price_found"], stats["time_found"],
    )
    return result, stats


def _checked_recently(last: "str | None", today: "str | None") -> bool:
    if not last or not today:
        return False
    try:
        days = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last)).days
    except ValueError:
        return False
    return 0 <= days < PRICE_RECHECK_DAYS


# ── price / time from page text (task 054) ───────────────────────────────────

def page_lines(html: str) -> list[str]:
    """Plain text lines of a page: block elements and <br> become line breaks."""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "nav"]):
        t.decompose()
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for tag in soup.find_all(_BLOCK_TAGS):
        tag.insert_after("\n")
    lines = []
    for line in soup.get_text("").split("\n"):
        line = re.sub(r"\s+", " ", line.replace("​", "")).strip()
        if line:
            lines.append(line)
    return lines


def page_text(html: str) -> str:
    return "\n".join(page_lines(html))[:PAGE_TEXT_MAX]


def extract_price(lines: list[str]) -> "str | None":
    """Return the price text exactly as the page states it, or None.

    A price is a labelled line ("Vstupné:", "Vstupenky:", "Admission:",
    "vstup …") whose value contains an amount (Kč/CZK/,-/€) or a free-entry
    word.  A label with an empty value takes the following lines that contain
    an amount (MeetFactory lists price tiers one per line).  Values without an
    amount ("Tba", "via FOURCE") are ignored.
    """
    for i, line in enumerate(lines):
        if len(line) > 400:
            continue
        m = _PRICE_LABEL.search(line)
        if not m:
            continue
        label, value = m.group(1), m.group(2).strip()
        if not value:
            parts = []
            for nxt in lines[i + 1:i + 7]:
                if not _PRICE_TOKEN.search(nxt) or len(nxt) > 120:
                    break
                parts.append(nxt)
            value = " / ".join(parts)
        if not value or not _PRICE_TOKEN.search(value) or len(value) > 200:
            continue
        value = value.rstrip(" .")
        if value[0].islower():
            # "zdarma / free entry", "v předprodeji 250 Kč …" read badly without the label
            value = f"{label} {value}"
        return value
    return None


def extract_start_time(lines: list[str]) -> "str | None":
    for line in lines:
        m = _START_LABEL.search(line)
        if m:
            return f"{int(m.group(1)):02d}:{m.group(2)}"
    return None


def _extract_from_page(html: str, url: str, selector: "str | None" = None) -> dict:
    """Extract description and image_url from an event detail page.

    When *selector* is given, use that CSS selector to extract description text
    instead of og:description / meta[name=description].

    Priority (description):
      If selector: CSS selector text
      Else: JSON-LD description → og:description → meta[name=description]

    Priority (image_url): JSON-LD image → og:image
    """
    soup = BeautifulSoup(html, "html.parser")
    result: dict = {}

    # 1. JSON-LD Event (always tried for image; description only when no custom selector)
    for item in _all_ld_items(soup):
        if not _is_event(item):
            continue
        if "description" not in result and not selector:
            d = _clean_description(item.get("description"))
            if d:
                result["description"] = d
        if "image_url" not in result:
            img = _resolve_image(item.get("image"), url)
            if img:
                result["image_url"] = img
        break  # first Event block is enough

    if selector:
        # Custom CSS selector for venue-specific description extraction
        if "description" not in result:
            els = soup.select(selector)
            parts = [el.get_text(separator=" ", strip=True) for el in els]
            text = " ".join(p for p in parts if p)
            d = _truncate(text)
            if d:
                result["description"] = d
    else:
        # 2. og:description
        if "description" not in result:
            d = _meta_property(soup, "og:description")
            if d:
                result["description"] = d

        # 3. meta[name=description]
        if "description" not in result:
            d = _meta_name(soup, "description")
            if d:
                result["description"] = d

    # 4. og:image
    if "image_url" not in result:
        img = _meta_property(soup, "og:image")
        if img and img.startswith("http"):
            result["image_url"] = img

    return result


# ── helpers ───────────────────────────────────────────────────────────────────

def _meta_property(soup: BeautifulSoup, prop: str) -> "str | None":
    el = soup.find("meta", property=prop)
    if not el:
        return None
    text = (el.get("content") or "").strip()
    return _truncate(text) if text else None


def _meta_name(soup: BeautifulSoup, name: str) -> "str | None":
    el = soup.find("meta", attrs={"name": name})
    if not el:
        return None
    text = (el.get("content") or "").strip()
    return _truncate(text) if text else None


def _truncate(text: str) -> "str | None":
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text or len(text) < 10:
        return None
    if len(text) <= _DESC_MAX:
        return text
    cut = text[:_DESC_MAX]
    for marker in (". ", "! ", "? "):
        pos = cut.rfind(marker)
        if pos > _DESC_MAX // 2:
            return cut[:pos + 1].strip()
    return cut.rsplit(" ", 1)[0] + "..."


def _build_listing_urls(venues: list) -> dict:
    """Return {venue_id: set_of_listing_urls} to skip non-detail-page source URLs."""
    result: dict = {}
    for venue in venues:
        urls: set = set()
        for source in venue.get("sources", []):
            main = source.get("url")
            if main:
                urls.add(main)
            sitemap = source.get("sitemap_url")
            if sitemap:
                urls.add(sitemap)
            ajax = source.get("ajax_url")
            if ajax:
                urls.add(ajax)
            # venue_url is the venue root page, not an individual event page
            venue_url = source.get("venue_url")
            if venue_url:
                urls.add(venue_url)
        result[venue["id"]] = urls
    return result


def _build_venue_desc_selectors(venues: list) -> dict:
    """Return {venue_id: css_selector} for venues with custom description extraction."""
    result: dict = {}
    for venue in venues:
        for source in venue.get("sources", []):
            sel = source.get("detail_desc_selector")
            if sel:
                result[venue["id"]] = sel
                break
    return result
