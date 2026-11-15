"""Generate 160×160 JPEG thumbnails for venue images."""
import hashlib
import logging
import pathlib
import urllib.request

log = logging.getLogger(__name__)

THUMB_DIR = pathlib.Path("site/img/venues")
THUMB_SIZE = 160
THUMB_QUALITY = 80
TIMEOUT = 15
USER_AGENT = "eventapp-pipeline/0.1 (thumbnail)"


def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def generate_thumbs(venues: list[dict]) -> dict[str, str | None]:
    """Download and resize venue images; return {venue_id: relative_path | None}.

    Only downloads when the source URL has changed (hash file next to thumb).
    Errors are logged as warnings; the pipeline continues.
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        log.warning("thumbs: Pillow not installed — skipping thumbnail generation")
        return {v["id"]: None for v in venues}

    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    result: dict[str, str | None] = {}

    for venue in venues:
        vid = venue.get("id", "")
        image_url = venue.get("image_url")
        if not image_url:
            result[vid] = None
            continue

        thumb_path = THUMB_DIR / f"{vid}.jpg"
        hash_path = THUMB_DIR / f"{vid}.url_hash"
        new_hash = _hash_url(image_url)

        # Skip if already cached with the same URL
        if thumb_path.exists() and hash_path.exists():
            if hash_path.read_text().strip() == new_hash:
                result[vid] = f"img/venues/{vid}.jpg"
                continue

        try:
            req = urllib.request.Request(image_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            # crop to square (cover, center)
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            img.save(thumb_path, "JPEG", quality=THUMB_QUALITY, optimize=True)
            hash_path.write_text(new_hash)
            log.info("thumbs: %s → %s (%d bytes)", vid, thumb_path, thumb_path.stat().st_size)
            result[vid] = f"img/venues/{vid}.jpg"
        except Exception as exc:
            log.warning("thumbs: %s — %s", vid, exc)
            result[vid] = None

    return result
