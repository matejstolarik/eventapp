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
    assert img.size == (240, 240)
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
