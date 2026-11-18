"""Per-venue rules for the event image taken from the event's own page (task 066).

The listing pages of several venues only give a small or pre-cropped image;
the event page has a bigger one (verified 2026-11-18, report 064 and 066):

  archa-plus       og:image = original /images/… (listing: 500×500 server crop)
  roxy             banner `…-1400-500` in .description .image background-image
                   (og:image / listing: `-crop-480-480` square cut by Roxy)
  meetfactory      og:image = original (JSON-LD image: 250 px thumbnail)
  cross-club       lightbox link of the header image (original /files/…),
                   else the `420x0-` image (og:image: 150×150 crop)
  palac-akropolis  main gallery image `…_web_event` (listing: `…_web_hp`)
  epic             slideshow image `/upload/temp/events/…` (listing: 620×360)
  forum-karlin     og:image = original (listing: 600×300) – used in the adapter
  citarna-unijazz  first image of the event slider (.oxy-dynamic-list);
                   og:image is the site-wide photo, JSON-LD image the logo

detail_image() returns (found, url): found=False means the rule did not
match the page (keep what the event already has); found=True with url=None
means the page clearly has no own image (placeholder / logo only).
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

DETAIL_IMAGE_VENUES = frozenset({
    "archa-plus", "roxy", "meetfactory", "cross-club", "palac-akropolis", "epic",
})

_BG_URL = re.compile(r"background-image\s*:\s*url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", re.I)

# Site-wide images that are not an image of the event.
_SHARED = {
    "citarna-unijazz": ("/2022/11/DSC_0040-scaled.jpg",),
}
_LOGO_VENUES = frozenset({"cross-club", "citarna-unijazz"})


def is_rejected(venue_id: str, url: "str | None") -> bool:
    """True if *url* is a placeholder, logo or site-wide image, not an event image."""
    if not url:
        return False
    low = url.lower()
    if venue_id == "roxy" and "/no-image-" in low:
        return True
    if any(s.lower() in low for s in _SHARED.get(venue_id, ())):
        return True
    if venue_id in _LOGO_VENUES and "logo" in low.rsplit("/", 1)[-1]:
        return True
    return False


def clean(venue_id: str, url: "str | None") -> "str | None":
    return None if is_rejected(venue_id, url) else url


def _abs(url: str, page_url: str) -> str:
    url = url.replace("\\/", "/").replace("\\.", ".").strip()
    return urljoin(page_url, url)


def _og_image(soup) -> "str | None":
    el = soup.find("meta", property="og:image")
    val = (el.get("content") or "").strip() if el else ""
    return val if val.startswith("http") else None


def _bg_url(el) -> "str | None":
    if el is None:
        return None
    m = _BG_URL.search(el.get("style") or "")
    return m.group(1) if m else None


def detail_image(venue_id: str, html: str, page_url: str) -> "tuple[bool, str | None]":
    soup = BeautifulSoup(html, "html.parser")
    url = None
    if venue_id in ("archa-plus", "meetfactory", "forum-karlin"):
        url = _og_image(soup)
    elif venue_id == "roxy":
        raw = _bg_url(soup.select_one(".wrapper.description .image"))
        url = _abs(raw, page_url) if raw else None
    elif venue_id == "cross-club":
        a = soup.select_one("#eventDetail td.image a[rel=lightbox][href]")
        if a:
            url = _abs(a["href"], page_url)
        else:
            img = soup.select_one("#eventDetail td.image img[src]")
            if img and "420x0-" in img["src"]:
                url = _abs(img["src"], page_url)
    elif venue_id == "palac-akropolis":
        img = soup.select_one("img.galery_out_img[src]")
        if img and "_web_event" in img["src"].lower():
            url = _abs(img["src"], page_url)
    elif venue_id == "epic":
        img = soup.select_one(".slideshow-main__slides-item img[src]")
        if img:
            url = _abs(img["src"], page_url)
    elif venue_id == "citarna-unijazz":
        raw = _bg_url(soup.select_one(".oxy-dynamic-list .ct-div-block[style]"))
        if raw:
            url = _abs(raw, page_url)
        else:
            # The page has no slider image: only the site-wide og:image / logo.
            return True, None
    if url is None:
        return False, None
    if is_rejected(venue_id, url):
        return True, None
    return True, url


def largest_srcset(img) -> "str | None":
    """URL of the widest candidate in an <img srcset> (w descriptors)."""
    best, best_w = None, -1
    for part in (img.get("srcset") or "").split(","):
        bits = part.strip().split()
        if len(bits) == 2 and bits[1].endswith("w") and bits[1][:-1].isdigit():
            w = int(bits[1][:-1])
            if w > best_w:
                best, best_w = bits[0], w
    return best
