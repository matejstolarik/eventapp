"""Task 064: build a local contact sheet comparing square crop variants of event images.

Usage:
    pip install opencv-python-headless pillow        # script-only deps, not in the daily run
    python scripts/review/crop-sheet.py [site/events.json]

Output (all under docs/tasks/064/sheet/, git-ignored: third-party images):
    orig/<hash>.img     downloaded originals (cache; re-runs do not re-download)
    v/<event_id>_<variant>.jpg   360 px squares: center, faces, top, whole
    index.html          sheet with a choice per row; "Uložiť" downloads choices.json
    stats.json          per-image data (size, ratio, faces, detection time)
Also prints a Markdown summary (aspect ratios, faces, detection time, per-venue sizes).

Face detection: OpenCV YuNet (face_detection_yunet_2023mar.onnx from opencv_zoo, cached in
.cache/opencv/). Chosen over Haar cascades because posters often have tilted, partly turned or
stylised faces where Haar misses or fires on texture; YuNet is a small CNN (230 kB), runs on CPU.
"""
import hashlib
import html
import io
import json
import pathlib
import statistics
import sys
import time
import urllib.parse
import urllib.request

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/tasks/064/sheet"
ORIG = OUT / "orig"
VAR = OUT / "v"
MODEL = ROOT / ".cache/opencv/face_detection_yunet_2023mar.onnx"
MODEL_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/"
             "face_detection_yunet/face_detection_yunet_2023mar.onnx")
UA = "eventapp-review/1.0 (personal project; crop review script)"
SIZE = 360
DETECT_MAX = 1024          # detection runs on a copy downscaled to this longer side
SCORE = 0.75               # YuNet confidence threshold
MIN_FACE = 0.04            # ignore faces smaller than this fraction of the shorter side
VARIANTS = ["center", "faces", "top", "whole"]
LABELS = {"center": "1 dnes (stred)", "faces": "2 tváre", "top": "3 zhora", "whole": "4 celý"}


def fetch(url: str, last_hit: dict) -> bytes | None:
    path = ORIG / (hashlib.md5(url.encode()).hexdigest() + ".img")
    if path.exists():
        return path.read_bytes() or None
    host = urllib.parse.urlsplit(url).netloc
    wait = 1.0 - (time.time() - last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    last_hit[host] = time.time()
    try:
        # percent-encode non-ASCII characters (urllib refuses them)
        safe = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~")
        req = urllib.request.Request(safe, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
    except Exception as exc:
        print(f"  ! {url}: {exc}", file=sys.stderr)
        data = b""
    path.write_bytes(data)
    return data or None


def square_at(img: Image.Image, cx: float, cy: float) -> Image.Image:
    w, h = img.size
    s = min(w, h)
    left = int(min(max(cx - s / 2, 0), w - s))
    top = int(min(max(cy - s / 2, 0), h - s))
    return img.crop((left, top, left + s, top + s)).resize((SIZE, SIZE), Image.LANCZOS)


def crop_center(img):
    w, h = img.size
    return square_at(img, w / 2, h / 2)


def crop_top(img):
    w, h = img.size
    if h > w:
        return square_at(img, w / 2, 0)
    return crop_center(img)


def crop_whole(img):
    w, h = img.size
    k = SIZE / min(w, h)
    bg = img.resize((max(SIZE, round(w * k)), max(SIZE, round(h * k))), Image.LANCZOS)
    bg = crop_center(bg).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    k = SIZE / max(w, h)
    fg = img.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    bg.paste(fg, ((SIZE - fg.width) // 2, (SIZE - fg.height) // 2))
    return bg


def detect(det, img) -> tuple[list[tuple[float, float, float, float]], float]:
    """Return face boxes (x, y, w, h) in original pixels and detection time in ms."""
    w, h = img.size
    k = min(1.0, DETECT_MAX / max(w, h))
    small = img.resize((max(1, round(w * k)), max(1, round(h * k)))) if k < 1 else img
    bgr = cv2.cvtColor(np.array(small), cv2.COLOR_RGB2BGR)
    t0 = time.perf_counter()
    det.setInputSize((bgr.shape[1], bgr.shape[0]))
    _, faces = det.detect(bgr)
    ms = (time.perf_counter() - t0) * 1000
    boxes = []
    for f in (faces if faces is not None else []):
        x, y, fw, fh = (float(v) / k for v in f[:4])
        if float(f[14]) >= SCORE and fh >= MIN_FACE * min(w, h):
            boxes.append((x, y, fw, fh))
    return boxes, ms


def union(boxes):
    # face box plus some room: hair above, chin/neck below
    xs0 = [x - 0.15 * fw for x, y, fw, fh in boxes]
    ys0 = [y - 0.35 * fh for x, y, fw, fh in boxes]
    xs1 = [x + 1.15 * fw for x, y, fw, fh in boxes]
    ys1 = [y + 1.25 * fh for x, y, fw, fh in boxes]
    return min(xs0), min(ys0), max(xs1), max(ys1)


def crop_faces(img, boxes):
    if not boxes:
        return crop_top(img), "none"
    s = min(img.size)
    fits = lambda b: (b[2] - b[0]) <= s and (b[3] - b[1]) <= s
    u = union(boxes)
    mode = "all"
    if not fits(u):
        # greedily keep the largest faces whose combined area still fits the square
        chosen = []
        for b in sorted(boxes, key=lambda b: -b[2] * b[3]):
            if not chosen or fits(union(chosen + [b])):
                chosen.append(b)
        u = union(chosen)
        mode = "largest"
    return square_at(img, (u[0] + u[2]) / 2, (u[1] + u[3]) / 2), mode


def aspect_class(w, h):
    r = w / h
    if r >= 2:
        return "banner"
    if r > 1.05:
        return "landscape"
    if r >= 0.95:
        return "square"
    return "portrait"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "site/events.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    events = data["events"]
    venues = {}
    vpath = ROOT / "data/venues.json"
    if vpath.exists():
        vj = json.loads(vpath.read_text(encoding="utf-8"))
        for v in (vj["venues"] if isinstance(vj, dict) else vj):
            venues[v["id"]] = v.get("name", v["id"])

    ORIG.mkdir(parents=True, exist_ok=True)
    VAR.mkdir(parents=True, exist_ok=True)
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320), SCORE, 0.3, 5000)

    rows, last_hit = [], {}
    for i, ev in enumerate(events):
        row = {"id": ev["id"], "title": ev["title"], "venue_id": ev["venue_id"],
               "venue": venues.get(ev["venue_id"], ev["venue_id"]), "date": ev["date"],
               "image_url": ev.get("image_url")}
        rows.append(row)
        if not row["image_url"]:
            continue
        raw = fetch(row["image_url"], last_hit)
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB") if raw else None
        except Exception as exc:
            print(f"  ! decode {row['image_url']}: {exc}", file=sys.stderr)
            img = None
        if img is None:
            row["error"] = True
            continue
        w, h = img.size
        boxes, ms = detect(det, img)
        faces_img, mode = crop_faces(img, boxes)
        row.update(w=w, h=h, aspect=aspect_class(w, h), faces=len(boxes), face_mode=mode,
                   detect_ms=round(ms, 1))
        out = {"center": crop_center(img), "faces": faces_img, "top": crop_top(img),
               "whole": crop_whole(img)}
        for k, im in out.items():
            im.save(VAR / f"{ev['id']}_{k}.jpg", "JPEG", quality=85)
        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(events)}", file=sys.stderr)

    (OUT / "stats.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    write_html(rows, data.get("generated_at"))
    print_summary(rows, data.get("generated_at"))


def write_html(rows, generated_at):
    esc = html.escape
    out = []
    for r in rows:
        if "w" not in r:
            continue
        cells = []
        for k in VARIANTS:
            cells.append(
                f'<label class="v"><img loading="lazy" src="v/{esc(r["id"])}_{k}.jpg" width="180" height="180">'
                f'<span><input type="radio" name="{esc(r["id"])}" value="{k}"> {LABELS[k]}</span></label>')
        faces = f'{r["faces"]} tvár(e), {r["face_mode"]}' if r["faces"] else "bez tváre"
        out.append(
            f'<tr><td class="meta"><b>{esc(r["title"])}</b><br>{esc(r["venue"])} · {esc(r["date"])}<br>'
            f'{r["w"]}×{r["h"]} · {r["w"] / r["h"]:.2f} ({r["aspect"]})<br>{faces}<br>'
            f'<a href="{esc(r["image_url"])}" target="_blank">originál</a></td>'
            f'<td class="o"><img loading="lazy" src="{esc(r["image_url"])}"></td>'
            + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    page = f"""<!doctype html><html lang="sk"><head><meta charset="utf-8">
<title>064 orezy</title><style>
body{{font:14px system-ui,sans-serif;margin:16px;background:#111;color:#eee}}
table{{border-collapse:collapse}} td{{border-top:1px solid #333;padding:8px;vertical-align:top}}
.meta{{width:220px}} .o img{{max-width:220px;max-height:220px}} a{{color:#8cf}}
.v{{display:block;cursor:pointer}} .v img{{display:block;border:3px solid transparent}}
.v:has(input:checked) img{{border-color:#f5c400}}
#bar{{position:sticky;top:0;background:#111;padding:8px 0;z-index:1}}
button{{font-size:15px;padding:6px 16px}}
</style></head><body>
<div id="bar">Zdroj: events.json {esc(str(generated_at))} · <span id="n"></span>
<button id="save">Uložiť</button> (stiahne choices.json; voľby sa priebežne pamätajú v prehliadači)</div>
<table>{''.join(out)}</table>
<script>
const KEY='choices064';
let c={{}}; try{{c=JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{}}
const radios=[...document.querySelectorAll('input[type=radio]')];
const total=new Set(radios.map(r=>r.name)).size;
const upd=()=>document.getElementById('n').textContent=Object.keys(c).length+' / '+total+' vybraných';
radios.forEach(r=>{{ if(c[r.name]===r.value) r.checked=true;
  r.addEventListener('change',()=>{{c[r.name]=r.value; try{{localStorage.setItem(KEY,JSON.stringify(c))}}catch(e){{}} upd();}});}});
upd();
document.getElementById('save').onclick=()=>{{
  const blob=new Blob([JSON.stringify({{generated_at:{json.dumps(generated_at)},choices:c}},null,1)],{{type:'application/json'}});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='choices.json'; a.click();
}};
</script></body></html>"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


def print_summary(rows, generated_at):
    imgs = [r for r in rows if "w" in r]
    print(f"events.json generated_at {generated_at}: {len(rows)} events, "
          f"{sum(1 for r in rows if r['image_url'])} with image_url, {len(imgs)} decoded, "
          f"{sum(1 for r in rows if r.get('error'))} download/decode errors\n")
    print("| aspect | count |\n|---|---|")
    for a in ["portrait", "square", "landscape", "banner"]:
        print(f"| {a} | {sum(1 for r in imgs if r['aspect'] == a)} |")
    one = sum(1 for r in imgs if r["faces"] == 1)
    many = sum(1 for r in imgs if r["faces"] > 1)
    largest = sum(1 for r in imgs if r["face_mode"] == "largest")
    ms = [r["detect_ms"] for r in imgs]
    print(f"\nfaces: 1 face {one}, more faces {many} (of which only largest fit: {largest}), "
          f"none {len(imgs) - one - many}")
    if ms:
        print(f"detection time per image (YuNet, <= {DETECT_MAX} px): median {statistics.median(ms):.1f} ms, "
              f"max {max(ms):.1f} ms, total {sum(ms) / 1000:.1f} s\n")
    print("| venue | events | no image | median w×h | min short side | short side < 600 |\n|---|---|---|---|---|---|")
    by = {}
    for r in rows:
        by.setdefault(r["venue_id"], []).append(r)
    for vid, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        ok = [r for r in rs if "w" in r]
        noimg = sum(1 for r in rs if not r["image_url"])
        err = sum(1 for r in rs if r.get("error"))
        if ok:
            mw = statistics.median(r["w"] for r in ok)
            mh = statistics.median(r["h"] for r in ok)
            mins = min(min(r["w"], r["h"]) for r in ok)
            small = sum(1 for r in ok if min(r["w"], r["h"]) < 600)
            dims = f"{mw:.0f}×{mh:.0f} | {mins} | {small}/{len(ok)}"
        else:
            dims = "– | – | –"
        print(f"| {vid} | {len(rs)} | {noimg}{f' (+{err} err)' if err else ''} | {dims} |")


if __name__ == "__main__":
    main()
