"""Tests for pipeline/detail_enrich.py."""

import pytest

from pipeline.detail_enrich import (
    _extract_from_page,
    _build_listing_urls,
    _build_venue_desc_selectors,
    enrich_missing_details,
)


# ── _extract_from_page ────────────────────────────────────────────────────────

def test_extract_jsonld_description_and_image():
    html = """
    <html><head>
    <script type="application/ld+json">{"@type":"Event","name":"Test","description":"A great show at the venue.","image":{"@type":"ImageObject","url":"https://example.com/img.jpg"}}</script>
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/1")
    assert result["description"] == "A great show at the venue."
    assert result["image_url"] == "https://example.com/img.jpg"


def test_extract_og_fallback_when_no_jsonld():
    html = """
    <html><head>
    <meta property="og:description" content="Summer festival on the island." />
    <meta property="og:image" content="https://cdn.example.com/summer.jpg" />
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/2")
    assert result["description"] == "Summer festival on the island."
    assert result["image_url"] == "https://cdn.example.com/summer.jpg"


def test_extract_meta_name_description_fallback():
    html = """
    <html><head>
    <meta name="description" content="Jazz night at the club every Thursday." />
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/3")
    assert result["description"] == "Jazz night at the club every Thursday."
    assert "image_url" not in result


def test_extract_prefers_jsonld_over_og():
    html = """
    <html><head>
    <script type="application/ld+json">{"@type":"Event","description":"From JSON-LD."}</script>
    <meta property="og:description" content="From og:description." />
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/4")
    assert result["description"] == "From JSON-LD."


def test_extract_empty_page():
    result = _extract_from_page("<html><body></body></html>", "https://example.com/event/5")
    assert result == {}


def test_extract_short_description_ignored():
    html = """
    <html><head>
    <meta property="og:description" content="Short." />
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/6")
    assert "description" not in result


def test_extract_og_image_requires_http():
    html = """
    <html><head>
    <meta property="og:image" content="/relative/image.jpg" />
    </head><body></body></html>
    """
    result = _extract_from_page(html, "https://example.com/event/7")
    assert "image_url" not in result


# ── _build_listing_urls ───────────────────────────────────────────────────────

def test_build_listing_urls_collects_all_url_types():
    venues = [
        {
            "id": "roxy",
            "sources": [
                {
                    "type": "html",
                    "url": "https://www.roxy.cz/club/",
                    "ajax_url": "https://www.roxy.cz/api/events",
                }
            ],
        },
        {
            "id": "fuchs2",
            "sources": [
                {
                    "type": "jsonld",
                    "url": "https://www.fuchs2.cz/events",
                    "sitemap_url": "https://www.fuchs2.cz/event-pages-sitemap.xml",
                }
            ],
        },
    ]
    result = _build_listing_urls(venues)
    assert "https://www.roxy.cz/club/" in result["roxy"]
    assert "https://www.roxy.cz/api/events" in result["roxy"]
    assert "https://www.fuchs2.cz/events" in result["fuchs2"]
    assert "https://www.fuchs2.cz/event-pages-sitemap.xml" in result["fuchs2"]


# ── enrich_missing_details (unit, no HTTP) ────────────────────────────────────

def _make_event(ev_id, venue_id, source_url, description=None, image_url=None):
    return {
        "id": ev_id,
        "venue_id": venue_id,
        "sources": [{"url": source_url}],
        "description": description,
        "image_url": image_url,
    }


def test_cache_hit_fills_description_and_image():
    ev = _make_event("ev1", "forum-karlin", "https://forumkarlin.cz/event/1")
    prev = {
        "ev1": {
            "id": "ev1",
            "venue_id": "forum-karlin",
            "sources": [{"url": "https://forumkarlin.cz/event/1"}],
            "description": "Evening concert with live band.",
            "description_source": "source",
            "image_url": "https://forumkarlin.cz/img.jpg",
        }
    }
    venues = [{"id": "forum-karlin", "sources": [{"type": "html", "url": "https://forumkarlin.cz/program/"}]}]

    result, stats = enrich_missing_details([ev], prev, venues)
    assert result[0]["description"] == "Evening concert with live band."
    assert result[0]["image_url"] == "https://forumkarlin.cz/img.jpg"
    assert stats["cache_hits"] == 1
    assert stats["fetched"] == 0


def test_cache_hit_only_fills_missing_fields():
    ev = _make_event("ev2", "meetfactory", "https://meetfactory.cz/event/2",
                     image_url="https://meetfactory.cz/existing.jpg")
    prev = {
        "ev2": {
            "id": "ev2",
            "venue_id": "meetfactory",
            "sources": [{"url": "https://meetfactory.cz/event/2"}],
            "description": "Cached description.",
            "description_source": "source",
            "image_url": "https://meetfactory.cz/cached.jpg",
        }
    }
    venues = [{"id": "meetfactory", "sources": [{"type": "jsonld", "url": "https://meetfactory.cz/cs/program"}]}]

    result, stats = enrich_missing_details([ev], prev, venues)
    # description was missing → filled from cache
    assert result[0]["description"] == "Cached description."
    # image_url was already set → NOT overwritten
    assert result[0]["image_url"] == "https://meetfactory.cz/existing.jpg"
    assert stats["cache_hits"] == 1


def test_listing_url_is_skipped():
    ev = _make_event("ev3", "roxy", "https://www.roxy.cz/club/")
    venues = [{"id": "roxy", "sources": [{"type": "html", "url": "https://www.roxy.cz/club/"}]}]

    result, stats = enrich_missing_details([ev], {}, venues)
    assert result[0]["description"] is None
    assert stats["skipped"] == 1
    assert stats["fetched"] == 0


def test_ra_co_url_is_skipped():
    ev = _make_event("ev4", "fuchs2", "https://ra.co/events/12345")
    venues = [{"id": "fuchs2", "sources": [{"type": "jsonld", "url": "https://www.fuchs2.cz/events"}]}]

    result, stats = enrich_missing_details([ev], {}, venues)
    assert stats["skipped"] == 1
    assert stats["fetched"] == 0


def test_fully_populated_event_is_passed_through():
    ev = _make_event("ev5", "kasarna-karlin", "https://kasarnakarlin.cz/event/5",
                     description="A full description.", image_url="https://kasarnakarlin.cz/img.jpg")
    venues = [{"id": "kasarna-karlin", "sources": [{"type": "jsonld", "url": "https://kasarnakarlin.cz/en/program"}]}]

    result, stats = enrich_missing_details([ev], {}, venues)
    assert result[0] is ev  # unchanged, same object
    assert stats["fetched"] == 0
    assert stats["skipped"] == 0
    assert stats["cache_hits"] == 0


# ── new features: venue_url skip, custom selector, title dedup ────────────────

def test_build_listing_urls_includes_venue_url():
    venues = [
        {
            "id": "bike-jesus",
            "sources": [
                {
                    "type": "api",
                    "url": "https://bikejesus.com/api/events",
                    "venue_url": "https://bikejesus.com",
                }
            ],
        }
    ]
    result = _build_listing_urls(venues)
    assert "https://bikejesus.com/api/events" in result["bike-jesus"]
    assert "https://bikejesus.com" in result["bike-jesus"]


def test_venue_url_source_is_skipped():
    ev = _make_event("bj1", "bike-jesus", "https://bikejesus.com")
    venues = [
        {
            "id": "bike-jesus",
            "sources": [{"type": "api", "url": "https://bikejesus.com/api/events", "venue_url": "https://bikejesus.com"}],
        }
    ]
    result, stats = enrich_missing_details([ev], {}, venues)
    assert result[0]["description"] is None
    assert stats["skipped"] == 1


def test_build_venue_desc_selectors():
    venues = [
        {"id": "meetfactory", "sources": [{"type": "jsonld", "url": "https://meetfactory.cz/hudba", "detail_desc_selector": "#text_equal p"}]},
        {"id": "roxy", "sources": [{"type": "html", "url": "https://www.roxy.cz/club/"}]},
    ]
    result = _build_venue_desc_selectors(venues)
    assert result["meetfactory"] == "#text_equal p"
    assert "roxy" not in result


def test_extract_from_page_uses_css_selector():
    html = """
    <html><head>
    <meta property="og:description" content="Generic venue text that should be ignored." />
    </head><body>
    <div id="text_equal">
      <p>An exciting concert featuring jazz bands from across Europe.</p>
      <p>Doors open at 20:00.</p>
    </div>
    </body></html>
    """
    result = _extract_from_page(html, "https://meetfactory.cz/event/1", selector="#text_equal p")
    assert "jazz" in result["description"]
    # og:description should be ignored when selector is provided
    assert "Generic venue" not in result["description"]


def test_cache_skipped_when_venue_has_custom_selector():
    ev = {**_make_event("mf1", "meetfactory", "https://meetfactory.cz/event/1"), "title": "Jazz Night"}
    prev = {
        "mf1": {
            "id": "mf1",
            "venue_id": "meetfactory",
            "sources": [{"url": "https://meetfactory.cz/event/1"}],
            "description": "Buckle up, the winter is coming to MeetFactory.",
            "description_source": "source",
            "image_url": None,
        }
    }
    # venue has detail_desc_selector → cache for description should be skipped
    venues = [
        {"id": "meetfactory", "sources": [{"type": "jsonld", "url": "https://meetfactory.cz/cs/program/hudba",
                                            "detail_desc_selector": "#text_equal p"}]}
    ]
    result, stats = enrich_missing_details([ev], prev, venues)
    # description should NOT be filled from cache (needs re-fetch)
    assert result[0].get("description") is None
    assert stats["cache_hits"] == 0


def test_cache_skipped_when_desc_equals_title():
    title = "SUNDEJ SE SUNDAY"
    ev = {**_make_event("cc1", "cross-club", "https://crossclub.cz/event/1"), "title": title}
    prev = {
        "cc1": {
            "id": "cc1",
            "venue_id": "cross-club",
            "sources": [{"url": "https://crossclub.cz/event/1"}],
            "description": title,
            "description_source": "source",
            "image_url": None,
        }
    }
    venues = [{"id": "cross-club", "sources": [{"type": "rss", "url": "https://www.crossclub.cz/cs/rss/program/"}]}]
    result, stats = enrich_missing_details([ev], prev, venues)
    # description == title → should be discarded
    assert result[0].get("description") is None
