"""Tests for generate_event_thumbs()."""
import io
import pathlib
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image


def _make_image_bytes(size=(400, 300), color=(200, 100, 50)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    return buf.getvalue()


def _make_event(eid: str, image_url: str | None = "https://example.com/img.jpg") -> dict:
    return {"id": eid, "image_url": image_url}


def test_thumbnail_dimensions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    img_bytes = _make_image_bytes()

    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = img_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        from pipeline.thumbs import generate_event_thumbs
        result = generate_event_thumbs([_make_event("ev1")])

    thumb_path = tmp_path / "site" / "img" / "events" / "ev1.jpg"
    assert thumb_path.exists()
    img = Image.open(thumb_path)
    assert img.size == (480, 480)
    assert result["ev1"] == "img/events/ev1.jpg"


def test_same_url_not_downloaded_twice(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    img_bytes = _make_image_bytes()

    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = img_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        from pipeline.thumbs import generate_event_thumbs
        generate_event_thumbs([_make_event("ev2")])
        call_count_after_first = mock_open.call_count

        generate_event_thumbs([_make_event("ev2")])

    assert mock_open.call_count == call_count_after_first  # no new request


def test_changed_url_redownloads(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    img_bytes = _make_image_bytes()

    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = img_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        from pipeline.thumbs import generate_event_thumbs
        generate_event_thumbs([_make_event("ev3", "https://example.com/v1.jpg")])
        count_after_first = mock_open.call_count

        generate_event_thumbs([_make_event("ev3", "https://example.com/v2.jpg")])

    assert mock_open.call_count > count_after_first


def test_cleanup_removes_stale_thumb(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    img_bytes = _make_image_bytes()

    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = img_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        from pipeline.thumbs import generate_event_thumbs
        generate_event_thumbs([_make_event("ev4")])

    thumb_path = tmp_path / "site" / "img" / "events" / "ev4.jpg"
    assert thumb_path.exists()

    # Run with empty list — ev4 should be cleaned up
    with patch("urllib.request.urlopen"):
        from pipeline.thumbs import generate_event_thumbs as get
        get([])

    assert not thumb_path.exists()


def test_download_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    img_bytes = _make_image_bytes()
    events = [_make_event(f"ev{i}", f"https://example.com/{i}.jpg") for i in range(200)]

    with patch("urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = img_bytes
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp

        from pipeline import thumbs as thumbs_mod
        original_limit = thumbs_mod.EVENT_DOWNLOAD_LIMIT
        thumbs_mod.EVENT_DOWNLOAD_LIMIT = 150
        try:
            from pipeline.thumbs import generate_event_thumbs
            result = generate_event_thumbs(events)
        finally:
            thumbs_mod.EVENT_DOWNLOAD_LIMIT = original_limit

    downloaded = sum(1 for v in result.values() if v is not None)
    deferred = sum(1 for v in result.values() if v is None)
    # Events without image_url would also be None, but all 200 have one
    assert downloaded == 150
    assert deferred == 50
    assert mock_open.call_count == 150


# ── task 066 ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("url,expected", [
    # Cyrillic "х" in "2400х800" (Forum Karlín)
    ("https://www.forumkarlin.cz/wp-content/uploads/2026/02/ENIGMA-2400х800-600x300.jpg",
     "https://www.forumkarlin.cz/wp-content/uploads/2026/02/ENIGMA-2400%D1%85800-600x300.jpg"),
    # zero-width joiner
    ("https://example.com/a‍b.jpg", "https://example.com/a%E2%80%8Db.jpg"),
    # "ö" (Kötter), and an already encoded query is kept as it is
    ("https://example.com/Kötter.jpg?x=%2Fimages&w=500", "https://example.com/K%C3%B6tter.jpg?x=%2Fimages&w=500"),
])
def test_quote_url_non_ascii(url, expected):
    from pipeline.thumbs import quote_url
    assert quote_url(url) == expected
    assert quote_url(url).isascii()


def _mock_urlopen(mock_open, img_bytes):
    mock_resp = MagicMock()
    mock_resp.read.return_value = img_bytes
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_open.return_value = mock_resp


def test_non_ascii_url_is_downloaded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("urllib.request.urlopen") as mock_open:
        _mock_urlopen(mock_open, _make_image_bytes())
        from pipeline.thumbs import generate_event_images
        res = generate_event_images([_make_event("ev9", "https://example.com/2400х800.png")])
        sent = mock_open.call_args[0][0].full_url
    assert sent == "https://example.com/2400%D1%85800.png"
    assert res["ev9"] == ("img/events/ev9.jpg", "img/events/detail/ev9.jpg")


@pytest.mark.parametrize("size,expected", [
    ((3000, 1000), (1200, 400)),   # wide banner, longer side scaled to 1200
    ((675, 1200), (675, 1200)),    # already within the limit
    ((800, 2400), (400, 1200)),    # portrait
    ((300, 200), (300, 200)),      # small: never enlarged
])
def test_detail_copy_uncropped(tmp_path, monkeypatch, size, expected):
    monkeypatch.chdir(tmp_path)
    with patch("urllib.request.urlopen") as mock_open:
        _mock_urlopen(mock_open, _make_image_bytes(size=size))
        from pipeline.thumbs import generate_event_images
        generate_event_images([_make_event("evd")])
    assert Image.open(tmp_path / "site/img/events/detail/evd.jpg").size == expected
    assert Image.open(tmp_path / "site/img/events/evd.jpg").size == (480, 480)


def test_old_240_thumb_is_regenerated(tmp_path, monkeypatch):
    """A thumb cached with the old URL-only hash (240 px) is rebuilt once."""
    monkeypatch.chdir(tmp_path)
    from pipeline.thumbs import generate_event_images, _hash_url
    d = tmp_path / "site/img/events"
    d.mkdir(parents=True)
    Image.new("RGB", (240, 240)).save(d / "old.jpg", "JPEG")
    (d / "old.url_hash").write_text(_hash_url("https://example.com/img.jpg"))
    with patch("urllib.request.urlopen") as mock_open:
        _mock_urlopen(mock_open, _make_image_bytes())
        generate_event_images([_make_event("old")])
        generate_event_images([_make_event("old")])
        assert mock_open.call_count == 1
    assert Image.open(d / "old.jpg").size == (480, 480)
