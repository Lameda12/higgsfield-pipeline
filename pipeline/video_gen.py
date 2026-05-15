"""Video generation via Higgsfield API (text→image→video pipeline)."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import higgsfield_client

_IMAGE_MODEL = "higgsfield-ai/soul/standard"
_VIDEO_MODEL = "higgsfield-ai/dop/standard"


def _check_credentials() -> None:
    hf_key = os.getenv("HF_KEY") or os.getenv("HIGGSFIELD_API_KEY")
    if not hf_key:
        raise ValueError("HF_KEY (or HIGGSFIELD_API_KEY) not set")
    # SDK reads HF_KEY automatically; map HIGGSFIELD_API_KEY → HF_KEY if needed
    if not os.getenv("HF_KEY") and hf_key:
        os.environ["HF_KEY"] = hf_key


async def generate_video(copy: str, output_dir: Path) -> Path:
    """Generate a campaign video clip from hook copy.

    Two-step pipeline:
      1. Text → image via higgsfield-ai/soul/standard
      2. Image → video via higgsfield-ai/dop/standard

    Args:
        copy: The selected hook copy string (used as generation prompt).
        output_dir: Directory to write the output video file.

    Returns:
        Path to the downloaded campaign_video.mp4.

    Raises:
        ValueError: If credentials are missing or generation fails.
        RuntimeError: If image or video generation job fails/is cancelled.
    """
    _check_credentials()

    # Step 1: generate a product image from copy
    image_url = await _generate_image_url(copy)

    # Step 2: animate the image into a short video clip
    video_url = await _generate_video_url(image_url=image_url, prompt=copy)

    # Step 3: download video to output_dir
    video_path = output_dir / "campaign_video.mp4"
    await _download(video_url, video_path)

    return video_path


async def _generate_image_url(prompt: str) -> str:
    """Generate an image and return its hosted URL."""
    result = await higgsfield_client.subscribe_async(
        _IMAGE_MODEL,
        arguments={
            "prompt": _image_prompt(prompt),
            "aspect_ratio": "16:9",
            "resolution": "720p",
        },
        on_queue_update=_log_status,
    )

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"Image generation returned no images. Result: {result}")

    url = images[0].get("url") or images[0].get("raw", {}).get("url", "")
    if not url:
        raise RuntimeError(f"Image result missing URL. Result: {result}")
    return url


async def _generate_video_url(image_url: str, prompt: str) -> str:
    """Animate an image into a video and return its hosted URL."""
    result = await higgsfield_client.subscribe_async(
        _VIDEO_MODEL,
        arguments={
            "image_url": image_url,
            "prompt": _video_prompt(prompt),
            "duration": 5,
        },
        on_queue_update=_log_status,
    )

    video = result.get("video") or {}
    url = video.get("url") or result.get("url", "")
    if not url:
        raise RuntimeError(f"Video generation returned no URL. Result: {result}")
    return url


async def _download(url: str, dest: Path) -> None:
    """Download a file from url to dest."""
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


def _log_status(status: object) -> None:
    name = type(status).__name__
    if name not in ("Queued",):  # suppress spammy queued messages
        print(f"[video_gen] status: {name}")
