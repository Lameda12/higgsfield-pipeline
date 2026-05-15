"""Video generation via Higgsfield CLI (text→image→video pipeline)."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import httpx


def _run_cli(args: list[str]) -> str:
    result = subprocess.run(
        ["higgsfield"] + args, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"higgsfield CLI error: {result.stderr.strip()}")
    return result.stdout.strip()


async def generate_video(copy: str, output_dir: Path) -> Path:
    """Generate a campaign video clip from hook copy.

    Step 1: higgsfield generate create flux_2 → CDN URL → extract UUID.
    Step 2: higgsfield generate create wan2_7 --medias UUID → CDN video URL → download.

    Args:
        copy: Selected hook copy string.
        output_dir: Directory to write campaign_video.mp4.

    Returns:
        Path to the downloaded video file.

    Raises:
        RuntimeError: If CLI call fails or output cannot be parsed.
    """
    # Step 1: text → image
    image_stdout = _run_cli([
        "generate", "create", "flux_2",
        "--prompt", _image_prompt(copy),
        "--aspect_ratio", "16:9",
        "--wait",
    ])
    print(f"[video_gen] image stdout: {image_stdout}")

    image_uuid = _extract_uuid_from_output(image_stdout)
    if not image_uuid:
        raise RuntimeError(f"Could not extract image UUID from CLI output: {image_stdout!r}")
    print(f"[video_gen] image UUID: {image_uuid}")

    # Step 2: image UUID → video
    medias_json = json.dumps([{"role": "start_image", "data": {"id": image_uuid, "type": "image"}}])
    video_stdout = _run_cli([
        "generate", "create", "wan2_7",
        "--prompt", _video_prompt(copy),
        "--medias", medias_json,
        "--duration", "5",
        "--wait",
    ])
    print(f"[video_gen] video stdout: {video_stdout}")

    video_url = _extract_url(video_stdout)
    if not video_url:
        raise RuntimeError(f"Could not extract video URL from CLI output: {video_stdout!r}")
    print(f"[video_gen] video URL: {video_url}")

    video_path = output_dir / "campaign_video.mp4"
    await _download(video_url, video_path)
    return video_path


def _extract_uuid_from_output(text: str) -> str:
    """Extract UUID from CDN URL filename or bare UUID in CLI output."""
    # Try bare UUID first
    m = re.search(r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b", text)
    if m:
        return m.group(1)
    # Try UUID embedded in URL path
    m = re.search(r"/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", text)
    if m:
        return m.group(1)
    return ""


def _extract_url(text: str) -> str:
    """Extract first https:// URL from CLI output."""
    m = re.search(r"https://\S+", text)
    return m.group(0) if m else ""


async def _download(url: str, dest: Path) -> None:
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with dest.open("wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)


def _image_prompt(copy: str) -> str:
    return (
        f"Product advertisement photo, professional studio lighting, "
        f"clean background, high quality commercial photography. "
        f"Campaign theme: {copy}"
    )


def _video_prompt(copy: str) -> str:
    return (
        f"Smooth cinematic camera movement, product showcase animation, "
        f"professional ad style. {copy}"
    )
