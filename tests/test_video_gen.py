"""Tests for video_gen.py."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest

from pipeline.video_gen import generate_video, _image_prompt, _video_prompt


COPY = "Stop wasting time. This product fixes it."

_IMAGE_RESULT = {"images": [{"url": "https://cdn.higgsfield.ai/img/test.jpg"}]}
_VIDEO_RESULT = {"video": {"url": "https://cdn.higgsfield.ai/vid/test.mp4"}}


def _patch_subscribe(side_effect: list):
    """Patch subscribe_async to return results in order."""
    return patch(
        "pipeline.video_gen.higgsfield_client.subscribe_async",
        AsyncMock(side_effect=side_effect),
    )


def _patch_download():
    """Patch _download to be a no-op."""
    return patch("pipeline.video_gen._download", AsyncMock())


# --- unit tests ---

def test_image_prompt_contains_copy() -> None:
    p = _image_prompt(COPY)
    assert COPY in p


def test_video_prompt_contains_copy() -> None:
    p = _video_prompt(COPY)
    assert COPY in p


# --- integration-style tests (mocked SDK + download) ---

async def test_generate_video_returns_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    with _patch_subscribe([_IMAGE_RESULT, _VIDEO_RESULT]), _patch_download():
        result = await generate_video(COPY, tmp_path)
    assert result == tmp_path / "campaign_video.mp4"


async def test_generate_video_calls_subscribe_twice(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    mock_sub = AsyncMock(side_effect=[_IMAGE_RESULT, _VIDEO_RESULT])
    with patch("pipeline.video_gen.higgsfield_client.subscribe_async", mock_sub), _patch_download():
        await generate_video(COPY, tmp_path)
    assert mock_sub.call_count == 2


async def test_generate_video_uses_image_model_first(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    mock_sub = AsyncMock(side_effect=[_IMAGE_RESULT, _VIDEO_RESULT])
    with patch("pipeline.video_gen.higgsfield_client.subscribe_async", mock_sub), _patch_download():
        await generate_video(COPY, tmp_path)
    first_call_endpoint = mock_sub.call_args_list[0].args[0]
    assert "soul" in first_call_endpoint


async def test_generate_video_uses_video_model_second(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    mock_sub = AsyncMock(side_effect=[_IMAGE_RESULT, _VIDEO_RESULT])
    with patch("pipeline.video_gen.higgsfield_client.subscribe_async", mock_sub), _patch_download():
        await generate_video(COPY, tmp_path)
    second_call_endpoint = mock_sub.call_args_list[1].args[0]
    assert "dop" in second_call_endpoint


async def test_missing_credentials_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_KEY", raising=False)
    monkeypatch.delenv("HIGGSFIELD_API_KEY", raising=False)
    with pytest.raises(ValueError, match="HF_KEY"):
        await generate_video(COPY, tmp_path)


async def test_image_generation_no_images_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    with _patch_subscribe([{"images": []}, _VIDEO_RESULT]):
        with pytest.raises(RuntimeError, match="no images"):
            await generate_video(COPY, tmp_path)


async def test_video_generation_no_url_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_KEY", "test-key:test-secret")
    with _patch_subscribe([_IMAGE_RESULT, {"video": {}}]):
        with pytest.raises(RuntimeError, match="no URL"):
            await generate_video(COPY, tmp_path)
