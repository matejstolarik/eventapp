"""Generate JPEG thumbnails for venue and event images."""
import hashlib
import logging
import pathlib
import urllib.request

log = logging.getLogger(__name__)

THUMB_DIR = pathlib.Path("site/img/venues")
THUMB_SIZE = 160
THUMB_QUALITY = 80

EVENT_THUMB_DIR = pathlib.Path("site/img/events")
EVENT_THUMB_SIZE = 240
EVENT_THUMB_QUALITY = 75
EVENT_DOWNLOAD_LIMIT = 150

TIMEOUT = 10
from .fetch import USER_AGENT


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


def generate_event_thumbs(events: list[dict]) -> dict[str, str | None]:
    """Download and resize event images; return {event_id: relative_path | None}.

    240×240 JPEG, quality 75. Only downloads when the source URL changed.
    Max EVENT_DOWNLOAD_LIMIT new downloads per run; deferred events get None.
    Removes thumbs for events no longer in the list.
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        log.warning("thumbs: Pillow not installed — skipping event thumbnail generation")
        return {e["id"]: None for e in events}

    EVENT_THUMB_DIR.mkdir(parents=True, exist_ok=True)

    current_ids = {e["id"] for e in events}

    # Cleanup stale thumbnails
    for jpg in list(EVENT_THUMB_DIR.glob("*.jpg")):
        eid = jpg.stem
        if eid not in current_ids:
            jpg.unlink(missing_ok=True)
            hash_file = EVENT_THUMB_DIR / f"{eid}.url_hash"
            hash_file.unlink(missing_ok=True)
            log.info("thumbs: removed stale event thumb %s", eid)

    result: dict[str, str | None] = {}
    new_count = 0
    cache_count = 0
    error_count = 0
    deferred_count = 0

    for event in events:
        eid = event.get("id", "")
        image_url = event.get("image_url")
        if not image_url:
            result[eid] = None
            continue

        thumb_path = EVENT_THUMB_DIR / f"{eid}.jpg"
        hash_path = EVENT_THUMB_DIR / f"{eid}.url_hash"
        new_hash = _hash_url(image_url)

        # Cache hit: same URL, thumb already exists
        if thumb_path.exists() and hash_path.exists():
            if hash_path.read_text().strip() == new_hash:
                result[eid] = f"img/events/{eid}.jpg"
                cache_count += 1
                continue

        # Enforce per-run download limit
        if new_count >= EVENT_DOWNLOAD_LIMIT:
            result[eid] = None
            deferred_count += 1
            continue

        try:
            req = urllib.request.Request(image_url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((EVENT_THUMB_SIZE, EVENT_THUMB_SIZE), Image.LANCZOS)
            img.save(thumb_path, "JPEG", quality=EVENT_THUMB_QUALITY, optimize=True)
            hash_path.write_text(new_hash)
            result[eid] = f"img/events/{eid}.jpg"
            new_count += 1
        except Exception as exc:
            log.warning("thumbs: event %s — %s", eid, exc)
            result[eid] = None
            error_count += 1

    total_size = sum(f.stat().st_size for f in EVENT_THUMB_DIR.glob("*.jpg"))
    log.info(
        "event thumbs: new=%d cache=%d errors=%d deferred=%d dir_size=%.1fMB",
        new_count, cache_count, error_count, deferred_count, total_size / 1_048_576,
    )
    if deferred_count:
        log.warning("event thumbs: %d downloads deferred (limit %d reached)", deferred_count, EVENT_DOWNLOAD_LIMIT)

    return result
