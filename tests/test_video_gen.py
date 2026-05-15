"""Tests for video_gen.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.video_gen import (
    generate_video,
    _image_prompt,
    _video_prompt,
    _extract_uuid_from_output,
    _extract_url,
    _run_cli,
)

COPY = "Stop wasting time. This product fixes it."

_IMAGE_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
_VIDEO_URL = "https://cdn.higgsfield.ai/vid/output.mp4"

_IMAGE_STDOUT = f"Generated image: https://cdn.higgsfield.ai/img/{_IMAGE_UUID}/result.jpg"
_VIDEO_STDOUT = f"Generated video: {_VIDEO_URL}"


def _patch_cli(side_effects: list[str]):
    return patch("pipeline.video_gen._run_cli", side_effect=side_effects)


def _patch_download():
    return patch("pipeline.video_gen._download", AsyncMock())


# --- unit tests ---

def test_image_prompt_contains_copy() -> None:
    assert COPY in _image_prompt(COPY)


def test_video_prompt_contains_copy() -> None:
    assert COPY in _video_prompt(COPY)


def test_extract_uuid_from_url_path() -> None:
    text = f"https://cdn.higgsfield.ai/img/{_IMAGE_UUID}/result.jpg"
    assert _extract_uuid_from_output(text) == _IMAGE_UUID


def test_extract_bare_uuid() -> None:
    text = f"Request ID: {_IMAGE_UUID}"
    assert _extract_uuid_from_output(text) == _IMAGE_UUID


def test_extract_uuid_returns_empty_on_no_match() -> None:
    assert _extract_uuid_from_output("no uuid here") == ""


def test_extract_url_finds_https() -> None:
    assert _extract_url(f"Done: {_VIDEO_URL}") == _VIDEO_URL


def test_extract_url_returns_empty_on_no_match() -> None:
    assert _extract_url("no url here") == ""


def test_run_cli_raises_on_nonzero() -> None:
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = "auth failed"
    with patch("pipeline.video_gen.subprocess.run", return_value=mock_result):
        with pytest.raises(RuntimeError, match="auth failed"):
            _run_cli(["generate", "create", "flux_2"])


def test_run_cli_returns_stdout_on_success() -> None:
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "  output line  "
    with patch("pipeline.video_gen.subprocess.run", return_value=mock_result):
        assert _run_cli(["generate", "create", "flux_2"]) == "output line"


# --- integration-style tests (mocked CLI + download) ---

async def test_generate_video_returns_path(tmp_path: Path) -> None:
    with _patch_cli([_IMAGE_STDOUT, _VIDEO_STDOUT]), _patch_download():
        result = await generate_video(COPY, tmp_path)
    assert result == tmp_path / "campaign_video.mp4"


async def test_generate_video_calls_cli_twice(tmp_path: Path) -> None:
    with patch("pipeline.video_gen._run_cli", side_effect=[_IMAGE_STDOUT, _VIDEO_STDOUT]) as mock_cli, \
         _patch_download():
        await generate_video(COPY, tmp_path)
    assert mock_cli.call_count == 2


async def test_generate_video_first_call_uses_flux2(tmp_path: Path) -> None:
    with patch("pipeline.video_gen._run_cli", side_effect=[_IMAGE_STDOUT, _VIDEO_STDOUT]) as mock_cli, \
         _patch_download():
        await generate_video(COPY, tmp_path)
    assert "flux_2" in mock_cli.call_args_list[0].args[0]


async def test_generate_video_second_call_uses_wan2_7(tmp_path: Path) -> None:
    with patch("pipeline.video_gen._run_cli", side_effect=[_IMAGE_STDOUT, _VIDEO_STDOUT]) as mock_cli, \
         _patch_download():
        await generate_video(COPY, tmp_path)
    assert "wan2_7" in mock_cli.call_args_list[1].args[0]


async def test_generate_video_passes_uuid_to_video_step(tmp_path: Path) -> None:
    with patch("pipeline.video_gen._run_cli", side_effect=[_IMAGE_STDOUT, _VIDEO_STDOUT]) as mock_cli, \
         _patch_download():
        await generate_video(COPY, tmp_path)
    video_args = mock_cli.call_args_list[1].args[0]
    assert _IMAGE_UUID in str(video_args)


async def test_missing_uuid_raises(tmp_path: Path) -> None:
    with _patch_cli(["no uuid in this output", _VIDEO_STDOUT]):
        with pytest.raises(RuntimeError, match="UUID"):
            await generate_video(COPY, tmp_path)


async def test_missing_video_url_raises(tmp_path: Path) -> None:
    with _patch_cli([_IMAGE_STDOUT, "no url in this output"]):
        with pytest.raises(RuntimeError, match="video URL"):
            await generate_video(COPY, tmp_path)
