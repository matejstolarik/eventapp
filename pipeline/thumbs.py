"""Generate JPEG thumbnails for venue and event images."""
import hashlib
import logging
import pathlib
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

THUMB_DIR = pathlib.Path("site/img/venues")
THUMB_SIZE = 160
THUMB_QUALITY = 80

EVENT_THUMB_DIR = pathlib.Path("site/img/events")
EVENT_THUMB_SIZE = 480          # task 066 (was 240); still a centre square
EVENT_THUMB_QUALITY = 75
EVENT_DOWNLOAD_LIMIT = 150

# task 066: uncropped copy for the event detail, longer side <= 1200 px
EVENT_DETAIL_DIR = EVENT_THUMB_DIR / "detail"
EVENT_DETAIL_MAX = 1200
EVENT_DETAIL_QUALITY = 80

TIMEOUT = 10
from .fetch import USER_AGENT

# Characters kept as they are when quoting an image URL (URL syntax and "%").
_URL_SAFE = ":/?#[]@!$&'()*+,;=%~"


def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _event_hash(url: str, kind: str) -> str:
    """Hash of the source URL plus output size, so a size change regenerates."""
    size = EVENT_THUMB_SIZE if kind == "thumb" else EVENT_DETAIL_MAX
    return _hash_url(f"{url}|{kind}{size}")


def quote_url(url: str) -> str:
    """Percent-encode non-ASCII characters (Cyrillic "х", ZWJ, "ö" seen in
    image URLs, report 064); already-encoded parts and URL syntax are kept."""
    return urllib.parse.quote(url, safe=_URL_SAFE)


def _download(url: str) -> bytes:
    req = urllib.request.Request(quote_url(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


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
            data = _download(image_url)
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
    """Thumbnail paths only ({event_id: path | None}); see generate_event_images."""
    return {eid: paths[0] for eid, paths in generate_event_images(events).items()}


def _open_with_retry(image_url, fallback, missing, outputs, Image, io):
    """Download + decode, one retry, then the fallback URL (task 067).
    Returns (RGB image, URL used, outputs still missing for that URL)."""
    last = None
    for _ in range(2):
        try:
            data = _download(image_url)
            return Image.open(io.BytesIO(data)).convert("RGB"), image_url, missing
        except Exception as exc:
            last = exc
    if not fallback or fallback == image_url:
        raise last
    log.warning("thumbs: %s failed twice (%s) — using listing image %s", image_url, last, fallback)
    data = _download(fallback)
    return Image.open(io.BytesIO(data)).convert("RGB"), fallback, ["thumb", "detail"]


def generate_event_images(events: list[dict], fallbacks: "dict | None" = None,
                          used_fallback: "dict | None" = None) -> dict[str, tuple]:
    """Download each event image once and write two files:

      img/events/<id>.jpg         480×480 centre square (image_thumb)
      img/events/detail/<id>.jpg  uncropped, longer side <= 1200 px (image_detail)

    Returns {event_id: (thumb_path | None, detail_path | None)}.  A file is
    regenerated only when the source URL or the output size changed (hash file
    next to it).  Max EVENT_DOWNLOAD_LIMIT downloads per run; deferred events
    keep files still valid for their URL, the rest get None.  Files of events
    no longer in the list are removed.

    Task 067: an image that fails (download or decode, e.g. a truncated PNG)
    is downloaded once more; when it fails again and fallbacks[event_id]
    (the listing image) is given, that image is used instead and recorded in
    used_fallback[event_id] (the caller sets image_url to it).
    """
    try:
        from PIL import Image
        import io
    except ImportError:
        log.warning("thumbs: Pillow not installed — skipping event thumbnail generation")
        return {e["id"]: (None, None) for e in events}

    EVENT_THUMB_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_DETAIL_DIR.mkdir(parents=True, exist_ok=True)

    current_ids = {e["id"] for e in events}

    # Cleanup stale files
    for d in (EVENT_THUMB_DIR, EVENT_DETAIL_DIR):
        for jpg in list(d.glob("*.jpg")):
            eid = jpg.stem
            if eid not in current_ids:
                jpg.unlink(missing_ok=True)
                (d / f"{eid}.url_hash").unlink(missing_ok=True)
                log.info("thumbs: removed stale event image %s/%s", d.name, eid)

    result: dict[str, tuple] = {}
    new_count = cache_count = error_count = deferred_count = 0

    for event in events:
        eid = event.get("id", "")
        image_url = event.get("image_url")
        if not image_url:
            result[eid] = (None, None)
            continue

        outputs = {
            "thumb": (EVENT_THUMB_DIR / f"{eid}.jpg", EVENT_THUMB_DIR / f"{eid}.url_hash",
                      f"img/events/{eid}.jpg"),
            "detail": (EVENT_DETAIL_DIR / f"{eid}.jpg", EVENT_DETAIL_DIR / f"{eid}.url_hash",
                       f"img/events/detail/{eid}.jpg"),
        }
        missing = [k for k, (jpg, hp, _) in outputs.items()
                   if not (jpg.exists() and hp.exists()
                           and hp.read_text().strip() == _event_hash(image_url, k))]
        if not missing:
            result[eid] = (outputs["thumb"][2], outputs["detail"][2])
            cache_count += 1
            continue

        if new_count >= EVENT_DOWNLOAD_LIMIT:
            result[eid] = tuple(None if k in missing else outputs[k][2]
                                for k in ("thumb", "detail"))
            deferred_count += 1
            continue

        try:
            src, image_url, missing = _open_with_retry(
                image_url, (fallbacks or {}).get(eid), missing, outputs, Image, io)
            new_count += 1
            if image_url != event.get("image_url") and used_fallback is not None:
                used_fallback[eid] = image_url
            if "thumb" in missing:
                w, h = src.size
                side = min(w, h)
                left, top = (w - side) // 2, (h - side) // 2
                img = src.crop((left, top, left + side, top + side))
                img = img.resize((EVENT_THUMB_SIZE, EVENT_THUMB_SIZE), Image.LANCZOS)
                img.save(outputs["thumb"][0], "JPEG", quality=EVENT_THUMB_QUALITY, optimize=True)
                outputs["thumb"][1].write_text(_event_hash(image_url, "thumb"))
            if "detail" in missing:
                img = src.copy()
                img.thumbnail((EVENT_DETAIL_MAX, EVENT_DETAIL_MAX), Image.LANCZOS)  # never enlarges
                img.save(outputs["detail"][0], "JPEG", quality=EVENT_DETAIL_QUALITY, optimize=True)
                outputs["detail"][1].write_text(_event_hash(image_url, "detail"))
            result[eid] = (outputs["thumb"][2], outputs["detail"][2])
        except Exception as exc:
            log.warning("thumbs: event %s — %s", eid, exc)
            result[eid] = (None, None)
            error_count += 1

    total_size = sum(f.stat().st_size for d in (EVENT_THUMB_DIR, EVENT_DETAIL_DIR)
                     for f in d.glob("*.jpg"))
    log.info(
        "event images: new=%d cache=%d errors=%d deferred=%d dir_size=%.1fMB",
        new_count, cache_count, error_count, deferred_count, total_size / 1_048_576,
    )
    if deferred_count:
        log.warning("event images: %d downloads deferred (limit %d reached)",
                    deferred_count, EVENT_DOWNLOAD_LIMIT)

    return result
