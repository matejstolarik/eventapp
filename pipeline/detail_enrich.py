"""Post-processing step: fetch missing description / image_url from event detail pages.

For events that:
  - have a source URL that differs from the venue's configured listing URL(s), AND
  - are missing description or image_url, AND
  - have not already been enriched (checked via previous_events cache)

we fetch the detail page once per event per pipeline run, extract description and
image_url, then propagate the result through events.json so the next run can skip
the fetch entirely.

Limits:
  - NEW_DETAILS_PER_VENUE new detail fetches per venue per run (default 40)
  - standard robots.txt, rate limiting, 1 s between requests to same host
  - Resident Advisor (ra.co) is never fetched
  - Bike Jesus main-page source URL is skipped (not an individual event page)
"""

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


def enrich_missing_details(
    events: list,
    previous_events: dict,
    venues: list,
) -> tuple[list, dict]:
    """Fetch missing description / image_url from event detail pages.

    Returns (enriched_events, stats_dict).
    """
    listing_urls = _build_listing_urls(venues)

    stats = {
        "fetched": 0,
        "cache_hits": 0,
        "skipped": 0,
        "errors": 0,
    }

    # Count new fetches per venue to enforce the per-venue limit
    new_fetches: dict[str, int] = {}

    result: list = []
    for ev in events:
        venue_id = ev.get("venue_id", "")
        ev_id = ev.get("id", "")

        needs_desc = not ev.get("description")
        needs_img = not ev.get("image_url")

        if not needs_desc and not needs_img:
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
        if prev:
            prev_sources = prev.get("sources", [])
            prev_url = prev_sources[0].get("url") if prev_sources else None
            if prev_url == detail_url:
                ev = dict(ev)
                filled = False
                if needs_desc and prev.get("description"):
                    ev["description"] = prev["description"]
                    ev["description_source"] = prev.get("description_source", "source")
                    needs_desc = False
                    filled = True
                if needs_img and prev.get("image_url"):
                    ev["image_url"] = prev["image_url"]
                    needs_img = False
                    filled = True
                if filled:
                    stats["cache_hits"] += 1
                if not needs_desc and not needs_img:
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

        enriched = _extract_from_page(html, detail_url)
        ev = dict(ev)
        if needs_desc and enriched.get("description"):
            ev["description"] = enriched["description"]
            ev["description_source"] = "source"
        if needs_img and enriched.get("image_url"):
            ev["image_url"] = enriched["image_url"]

        result.append(ev)

    log.info(
        "detail_enrich: fetched=%d cache_hits=%d skipped=%d errors=%d",
        stats["fetched"], stats["cache_hits"], stats["skipped"], stats["errors"],
    )
    return result, stats


def _extract_from_page(html: str, url: str) -> dict:
    """Extract description and image_url from an event detail page.

    Priority:
      description: JSON-LD description → og:description → meta[name=description]
      image_url:   JSON-LD image       → og:image
    """
    soup = BeautifulSoup(html, "html.parser")
    result: dict = {}

    # 1. JSON-LD Event
    for item in _all_ld_items(soup):
        if not _is_event(item):
            continue
        if "description" not in result:
            d = _clean_description(item.get("description"))
            if d:
                result["description"] = d
        if "image_url" not in result:
            img = _resolve_image(item.get("image"), url)
            if img:
                result["image_url"] = img
        break  # first Event block is enough

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
        result[venue["id"]] = urls
    return result
