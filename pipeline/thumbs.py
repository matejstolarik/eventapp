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
EVENT_THUMB_W, EVENT_THUMB_H = 640, 480   # task 068: 4:3 (was 480 square, 240 before 066)
EVENT_THUMB_QUALITY = 75
# task 068: a source with w/h below this is a portrait (poster) and is shown
# whole on a blurred, darkened fill of itself; everything else = centre 4:3 crop.
PORTRAIT_MAX_RATIO = 0.8
EVENT_DOWNLOAD_LIMIT = 150      # task 068 ran once with 400 to recompute all thumbs

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
    size = f"{EVENT_THUMB_W}x{EVENT_THUMB_H}r{PORTRAIT_MAX_RATIO}" if kind == "thumb" else EVENT_DETAIL_MAX
    return _hash_url(f"{url}|{kind}{size}")


def make_event_thumb(src, Image, ImageFilter, ImageEnhance):
    """640x480 thumb: portrait sources (w/h < PORTRAIT_MAX_RATIO) uncropped,
    centred on a blurred and darkened copy of themselves; others centre-cropped
    to 4:3.  Returns (image, "portrait" | "crop")."""
    tw, th = EVENT_THUMB_W, EVENT_THUMB_H
    w, h = src.size
    if w / h < PORTRAIT_MAX_RATIO:
        # fill: cover-crop the source to 4:3, blur strongly, darken
        scale = max(tw / w, th / h)
        bg = src.resize((max(tw, round(w * scale)), max(th, round(h * scale))), Image.LANCZOS)
        left, top = (bg.width - tw) // 2, (bg.height - th) // 2
        bg = bg.crop((left, top, left + tw, top + th))
        bg = bg.filter(ImageFilter.GaussianBlur(24))
        bg = ImageEnhance.Brightness(bg).enhance(0.45)
        fw = max(1, round(w * th / h))
        fg = src.resize((fw, th), Image.LANCZOS)
        bg.paste(fg, ((tw - fw) // 2, 0))
        return bg, "portrait"
    target = tw / th
    if w / h > target:              # wider than 4:3 -> cut the sides
        cw, ch = round(h * target), h
    else:                           # taller than 4:3 -> cut top and bottom
        cw, ch = w, round(w / target)
    left, top = (w - cw) // 2, (h - ch) // 2
    img = src.crop((left, top, left + cw, top + ch)).resize((tw, th), Image.LANCZOS)
    return img, "crop"


def quote_url(url: str) -> str:
    """Percent-encode non-ASCII characters (Cyrillic "х", ZWJ, "ö" seen in
    image URLs, report 064); already-encoded parts and URL syntax are kept."""
    return urllib.parse.quote(url, safe=_URL_SAFE)


def _download(url: str) -> bytes:
    req = urllib.request.Request(quote_url(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


VENUE_CARD_DIR = THUMB_DIR / "card"      # task 082: 640x480, same as event thumbs
VENUE_DETAIL_DIR = THUMB_DIR / "detail"  # task 082: uncropped, longer side <= 1200 px


def _image_size(path: pathlib.Path) -> "list[int] | None":
    """[width, height] of a written JPEG; None when missing or unreadable."""
    if not path.exists():
        return None
    try:
        from PIL import Image
        with Image.open(path) as img:
            w, h = img.size
        return [int(w), int(h)]
    except Exception as exc:
        log.warning("thumbs: cannot read size of %s — %s", path, exc)
        return None


def generate_venue_images(venues: list[dict]) -> dict[str, dict]:
    """Download each venue image once and write three files (task 082):

      img/venues/<id>.jpg         160x160 square crop (image_thumb)
      img/venues/card/<id>.jpg    640x480, make_event_thumb (image_card)
      img/venues/detail/<id>.jpg  uncropped, longer side <= 1200 px (image_detail)

    Returns {venue_id: {image_thumb, image_card, image_detail, image_detail_size}},
    values None when the venue has no image_url or the download failed.
    A file is regenerated only when the source URL (or output size) changed
    (hash file next to it).  One attempt per image, TIMEOUT seconds; errors
    are logged as warnings and the pipeline continues.
    """
    empty = {"image_thumb": None, "image_card": None, "image_detail": None,
             "image_detail_size": None}
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        import io
    except ImportError:
        log.warning("thumbs: Pillow not installed — skipping thumbnail generation")
        return {v["id"]: dict(empty) for v in venues}

    for d in (THUMB_DIR, VENUE_CARD_DIR, VENUE_DETAIL_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # stale card/detail files of venues no longer listed or without an image
    keep = {v.get("id") for v in venues if v.get("image_url")}
    for d in (VENUE_CARD_DIR, VENUE_DETAIL_DIR):
        for jpg in list(d.glob("*.jpg")):
            if jpg.stem not in keep:
                jpg.unlink(missing_ok=True)
                (d / f"{jpg.stem}.url_hash").unlink(missing_ok=True)

    result: dict[str, dict] = {}
    for venue in venues:
        vid = venue.get("id", "")
        image_url = venue.get("image_url")
        if not image_url:
            result[vid] = dict(empty)
            continue

        outputs = {
            "thumb": (THUMB_DIR / f"{vid}.jpg", THUMB_DIR / f"{vid}.url_hash",
                      _hash_url(image_url), f"img/venues/{vid}.jpg"),
            "card": (VENUE_CARD_DIR / f"{vid}.jpg", VENUE_CARD_DIR / f"{vid}.url_hash",
                     _event_hash(image_url, "thumb"), f"img/venues/card/{vid}.jpg"),
            "detail": (VENUE_DETAIL_DIR / f"{vid}.jpg", VENUE_DETAIL_DIR / f"{vid}.url_hash",
                       _event_hash(image_url, "detail"), f"img/venues/detail/{vid}.jpg"),
        }
        missing = [k for k, (jpg, hp, h, _) in outputs.items()
                   if not (jpg.exists() and hp.exists() and hp.read_text().strip() == h)]
        try:
            if missing:
                data = _download(image_url)
                src = Image.open(io.BytesIO(data)).convert("RGB")
                for k in missing:
                    jpg, hp, h, _ = outputs[k]
                    if k == "thumb":
                        w, hh = src.size
                        side = min(w, hh)
                        left, top = (w - side) // 2, (hh - side) // 2
                        img = src.crop((left, top, left + side, top + side))
                        img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
                        img.save(jpg, "JPEG", quality=THUMB_QUALITY, optimize=True)
                    elif k == "card":
                        img, _shape = make_event_thumb(src, Image, ImageFilter, ImageEnhance)
                        img.save(jpg, "JPEG", quality=EVENT_THUMB_QUALITY, optimize=True)
                    else:
                        img = src.copy()
                        img.thumbnail((EVENT_DETAIL_MAX, EVENT_DETAIL_MAX), Image.LANCZOS)
                        img.save(jpg, "JPEG", quality=EVENT_DETAIL_QUALITY, optimize=True)
                    hp.write_text(h)
                log.info("thumbs: venue %s — wrote %s", vid, ", ".join(missing))
            detail_path = outputs["detail"][0]
            result[vid] = {
                "image_thumb": outputs["thumb"][3],
                "image_card": outputs["card"][3],
                "image_detail": outputs["detail"][3],
                "image_detail_size": _image_size(detail_path),
            }
        except Exception as exc:
            log.warning("thumbs: venue %s — %s", vid, exc)
            result[vid] = dict(empty)

    return result


def generate_thumbs(venues: list[dict]) -> dict[str, str | None]:
    """Venue thumbnail paths only ({venue_id: path | None}); see generate_venue_images."""
    return {vid: r["image_thumb"] for vid, r in generate_venue_images(venues).items()}


def event_detail_size(event_id: str) -> "list[int] | None":
    """[width, height] of the written image_detail file (task 069), read from
    the JPEG header; None when the file is missing or unreadable."""
    return _image_size(EVENT_DETAIL_DIR / f"{event_id}.jpg")


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

      img/events/<id>.jpg         640×480 (image_thumb; see make_event_thumb)
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
        from PIL import Image, ImageFilter, ImageEnhance
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
    shapes = {"portrait": 0, "crop": 0}

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
                img, shape = make_event_thumb(src, Image, ImageFilter, ImageEnhance)
                shapes[shape] += 1
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
        "event images: new=%d cache=%d errors=%d deferred=%d dir_size=%.1fMB "
        "(new thumbs: portrait=%d crop=%d)",
        new_count, cache_count, error_count, deferred_count, total_size / 1_048_576,
        shapes["portrait"], shapes["crop"],
    )
    if deferred_count:
        log.warning("event images: %d downloads deferred (limit %d reached)",
                    deferred_count, EVENT_DOWNLOAD_LIMIT)

    return result
