"""Task 066: bigger event images from the event pages (saved 2026-11-18)."""
import datetime
import pathlib

import pytest

from pipeline import images
from pipeline.adapters.html_epic import parse_listing as epic_listing
from pipeline.adapters.html_forum_karlin import parse_listing as fk_listing, parse_detail as fk_detail

FX = pathlib.Path(__file__).parent / "fixtures"


def page(name):
    return (FX / "img066" / f"{name}.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("venue,name,url,expected", [
    ("archa-plus", "archa2", "https://archa-plus.cz/cz/program/detail/748/2026-11-19-jose-gonzalez",
     "https://archa-plus.cz/images/gonzalez-press2.jpeg"),
    ("roxy", "roxy1", "https://www.roxy.cz/events/detail/5137/vyprodano-colorfactory",
     "https://www.roxy.cz/upload/temp/baner-colorfactory-1400x480px-4l3g2vy35qbh-1400-500.png"),
    ("meetfactory", "mf2", "http://www.meetfactory.cz/cs/program/detail/music-press-production-arab-strap",
     "http://www.meetfactory.cz/media/images/ab6761610000e5eb547b0b30ac01160630da14eb.jpeg"),
    ("cross-club", "cc1",
     "https://www.crossclub.cz/cs/program/8728-drum-and-bus-station-w-fourward-smooth-chris-su-7-mc-fedora/",
     "https://www.crossclub.cz/files/2026/prosinec/sub.jpg"),
    ("palac-akropolis", "pa2", "https://palacakropolis.cz/work/33298?event_id=41290&genre=1&no=62&page_id=33824",
     "https://palacakropolis.cz/images/photos/0026/5550/Claptrap___Tristan_d_Hervez_2_web_event.jpg"),
    ("epic", "ep1", "https://www.epicprague.com/program/2173/slvl",
     "https://www.epicprague.com/upload/temp/events/1000x1000-irg2gp5zj6-1920-1080.png"),
    ("citarna-unijazz", "uj1", "https://citarna.unijazz.cz/events/david-pillow-krest-jakub-eden/",
     "https://citarna.unijazz.cz/wp-content/uploads/2026/10/album-photoshoot-3.jpg"),
])
def test_detail_image(venue, name, url, expected):
    assert images.detail_image(venue, page(name), url) == (True, expected)


def test_unijazz_without_own_image_is_none():
    # psytrance-united: no slider image, only the site-wide og:image and the logo
    url = "https://citarna.unijazz.cz/events/psytrance-united/"
    assert images.detail_image("citarna-unijazz", page("uj2"), url) == (True, None)


def test_rule_not_matching_keeps_listing():
    assert images.detail_image("palac-akropolis", "<html></html>", "https://x/") == (False, None)


@pytest.mark.parametrize("venue,url,rejected", [
    ("roxy", "https://www.roxy.cz/upload/temp/no-image-480-480.png", True),
    ("citarna-unijazz", "https://citarna.unijazz.cz/wp-content/uploads/2022/11/DSC_0040-scaled.jpg", True),
    ("cross-club", "https://www.crossclub.cz/data/resized/files/2016/cerven/150x150c-a2aa-cross-logo.jpg", True),
    ("cross-club", "https://www.crossclub.cz/files/2026/prosinec/sub.jpg", False),
    ("roxy", "https://www.roxy.cz/upload/temp/img-7878-jh8am7wda21n-1400-500.JPG", False),
])
def test_rejected(venue, url, rejected):
    assert images.is_rejected(venue, url) is rejected


def test_epic_listing_colour_image():
    evs = epic_listing({"id": "epic"}, {"url": "https://www.epicprague.com/program"}, page("eplist"),
                       yesterday=datetime.date(2026, 11, 17), cutoff=datetime.date(2027, 6, 1))
    slvl = next(e for e in evs if "/2173/" in e.source["url"])
    assert slvl.image_url == "https://www.epicprague.com/data/events/620x360-pjh6ro4iug.png"
    assert all(e.image_url for e in evs)


def test_forum_karlin_listing_srcset_and_detail_og_image():
    evs = fk_listing({"id": "forum-karlin"}, {"url": "https://www.forumkarlin.cz/program/"},
                     (FX / "forumkarlin_program_20261118.html").read_text(encoding="utf-8"),
                     today=datetime.date(2026, 11, 18))
    omah = next(e for e in evs if e.title == "Omah Lay")
    assert omah.image_url == "https://www.forumkarlin.cz/wp-content/uploads/2026/07/2400x800-1280x640.png"
    out = fk_detail(omah, (FX / "forumkarlin_detail_omah_lay.html").read_text(encoding="utf-8"))
    assert out.image_url == "https://www.forumkarlin.cz/wp-content/uploads/2026/07/2400x800.png"


def test_detail_enrich_uses_rule_once_and_caches(monkeypatch):
    from pipeline import detail_enrich as de
    url = "https://www.roxy.cz/events/detail/5137/vyprodano-colorfactory"
    calls = []

    class R:
        text = page("roxy1")
        def raise_for_status(self): pass

    monkeypatch.setattr(de.requests, "get", lambda *a, **k: calls.append(a) or R())
    monkeypatch.setattr(de, "_robots_allowed", lambda u: True)
    monkeypatch.setattr(de, "_rate_limit", lambda u: None)
    venues = [{"id": "roxy", "sources": [{"url": "https://www.roxy.cz/club/"}]}]
    ev = {"id": "r1", "venue_id": "roxy", "title": "Colorfactory", "sources": [{"url": url}],
          "description": "d" * 20,
          "image_url": "https://www.roxy.cz/upload/temp/baner-colorfactory-1400x480px-4l3g2vy35qbh-crop-480-480.png"}
    state = {}
    out, _ = de.enrich_missing_details([ev], {"r1": ev}, venues, state=state)
    assert out[0]["image_url"].endswith("-1400-500.png")
    assert len(calls) == 1
    out, _ = de.enrich_missing_details([ev], {"r1": out[0]}, venues, state=state)
    assert out[0]["image_url"].endswith("-1400-500.png")
    assert len(calls) == 1  # cached in state["detail_image"]


def test_detail_enrich_limit_keeps_previous_image(monkeypatch):
    """Over the per-venue limit the page is not fetched; the image of the
    previous run stays (Roxy has no image in the listing)."""
    from pipeline import detail_enrich as de
    monkeypatch.setattr(de, "NEW_DETAILS_PER_VENUE", 0)
    monkeypatch.setattr(de.requests, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("fetched")))
    url = "https://www.roxy.cz/events/detail/1/x"
    venues = [{"id": "roxy", "sources": [{"url": "https://www.roxy.cz/club/"}]}]
    ev = {"id": "r2", "venue_id": "roxy", "title": "X", "sources": [{"url": url}],
          "description": "d" * 20, "image_url": None}
    prev = dict(ev, image_url="https://www.roxy.cz/upload/temp/x-crop-480-480.png")
    out, _ = de.enrich_missing_details([ev], {"r2": prev}, venues, state={})
    assert out[0]["image_url"] == prev["image_url"]
