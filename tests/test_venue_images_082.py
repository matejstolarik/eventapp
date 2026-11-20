"""Task 082: venue image_card / image_detail / image_detail_size."""
import io

from PIL import Image

from pipeline import thumbs


def _png(w, h):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 50, 50)).save(buf, "PNG")
    return buf.getvalue()


def _setup(monkeypatch, tmp_path, sizes):
    d = tmp_path / "venues"
    monkeypatch.setattr(thumbs, "THUMB_DIR", d)
    monkeypatch.setattr(thumbs, "VENUE_CARD_DIR", d / "card")
    monkeypatch.setattr(thumbs, "VENUE_DETAIL_DIR", d / "detail")
    calls = []

    def fake_download(url):
        calls.append(url)
        if url not in sizes:
            raise OSError("HTTP 403")
        return _png(*sizes[url])

    monkeypatch.setattr(thumbs, "_download", fake_download)
    return d, calls


def test_venue_images_written_once_and_cached(monkeypatch, tmp_path):
    d, calls = _setup(monkeypatch, tmp_path, {"http://a/big.jpg": (2400, 1600)})
    venues = [{"id": "a", "image_url": "http://a/big.jpg"}, {"id": "b", "image_url": None}]
    r = thumbs.generate_venue_images(venues)
    assert r["a"] == {"image_thumb": "img/venues/a.jpg",
                      "image_card": "img/venues/card/a.jpg",
                      "image_detail": "img/venues/detail/a.jpg",
                      "image_detail_size": [1200, 800]}
    assert r["b"] == {"image_thumb": None, "image_card": None,
                      "image_detail": None, "image_detail_size": None}
    assert len(calls) == 1
    assert Image.open(d / "card" / "a.jpg").size == (640, 480)
    assert Image.open(d / "a.jpg").size == (160, 160)
    # unchanged URL -> no download
    assert thumbs.generate_venue_images(venues) == r
    assert len(calls) == 1


def test_small_image_not_enlarged_and_url_change_regenerates(monkeypatch, tmp_path):
    d, calls = _setup(monkeypatch, tmp_path,
                      {"http://a/1.jpg": (320, 426), "http://a/2.jpg": (800, 600)})
    r = thumbs.generate_venue_images([{"id": "a", "image_url": "http://a/1.jpg"}])
    assert r["a"]["image_detail_size"] == [320, 426]
    r = thumbs.generate_venue_images([{"id": "a", "image_url": "http://a/2.jpg"}])
    assert r["a"]["image_detail_size"] == [800, 600]
    assert len(calls) == 2


def test_existing_thumb_only_still_creates_card_with_one_download(monkeypatch, tmp_path):
    d, calls = _setup(monkeypatch, tmp_path, {"http://a/1.jpg": (1000, 1000)})
    thumbs.generate_venue_images([{"id": "a", "image_url": "http://a/1.jpg"}])
    (d / "card" / "a.jpg").unlink()
    (d / "detail" / "a.jpg").unlink()
    r = thumbs.generate_venue_images([{"id": "a", "image_url": "http://a/1.jpg"}])
    assert r["a"]["image_card"] == "img/venues/card/a.jpg"
    assert len(calls) == 2


def test_download_error_gives_nulls_and_continues(monkeypatch, tmp_path):
    _setup(monkeypatch, tmp_path, {"http://ok/1.jpg": (900, 600)})
    r = thumbs.generate_venue_images([{"id": "x", "image_url": "http://fail/1.jpg"},
                                      {"id": "y", "image_url": "http://ok/1.jpg"}])
    assert r["x"]["image_card"] is None and r["x"]["image_detail_size"] is None
    assert r["y"]["image_card"] == "img/venues/card/y.jpg"
