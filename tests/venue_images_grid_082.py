"""Task 082: grid of venue image_card files from Pages for Matej (docs/tasks/082/venue-images.jpg).
Run: python tests/venue_images_grid_082.py"""
import io, json, pathlib, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont

PAGES = "https://matejstolarik.github.io/eventapp/"
OUT = pathlib.Path("docs/tasks/082/venue-images.jpg")
UA = {"User-Agent": "eventapp-task082-grid"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()


data = json.loads(get(PAGES + "events.json"))
venues = data["venues"]
CW, CH, TXT, COLS = 320, 240, 54, 3
rows = (len(venues) + COLS - 1) // COLS
grid = Image.new("RGB", (COLS * CW + (COLS + 1) * 10, rows * (CH + TXT) + (rows + 1) * 10), (17, 17, 24))
draw = ImageDraw.Draw(grid)
try:
    font = ImageFont.truetype("arial.ttf", 15)
except OSError:
    font = ImageFont.load_default()
for i, v in enumerate(venues):
    x, y = 10 + (i % COLS) * (CW + 10), 10 + (i // COLS) * (CH + TXT + 10)
    ext = pathlib.PurePosixPath(urllib.parse.urlparse(v.get("image_url") or "").path).suffix.lstrip(".").upper() or "-"
    if v.get("image_card"):
        grid.paste(Image.open(io.BytesIO(get(PAGES + v["image_card"]))).convert("RGB").resize((CW, CH)), (x, y))
    size = v.get("image_detail_size")
    small = size and size[0] < 640
    draw.text((x, y + CH + 6), v["id"], fill=(244, 242, 255), font=font)
    draw.text((x, y + CH + 26), f"{size[0]}x{size[1]} {ext}" if size else f"no image_card {ext}",
              fill=(255, 77, 141) if small or not size else (185, 182, 204), font=font)
    if small:
        draw.text((x + 170, y + CH + 26), "< 640 px", fill=(255, 77, 141), font=font)
OUT.parent.mkdir(parents=True, exist_ok=True)
grid.save(OUT, "JPEG", quality=80)
print(OUT, grid.size)
for v in venues:
    print(v["id"], v.get("image_detail_size"), v.get("image_url"))
