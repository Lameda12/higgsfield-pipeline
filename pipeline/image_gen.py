"""Image generation via Higgsfield API (text→image)."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import higgsfield_client

_IMAGE_MODEL = "higgsfield-ai/soul/standard"


def _check_credentials() -> None:
    hf_key = os.getenv("HF_KEY") or os.getenv("HIGGSFIELD_API_KEY")
    if not hf_key:
        raise ValueError("HF_KEY (or HIGGSFIELD_API_KEY) not set")
    if not os.getenv("HF_KEY") and hf_key:
        os.environ["HF_KEY"] = hf_key


async def generate_image(copy: str, output_dir: Path) -> Path:
    """Generate a product image via Higgsfield text-to-image.

    Args:
        copy: The selected hook copy string (used as generation prompt).
        output_dir: Directory to write the output image file.

    Returns:
        Path to the downloaded product_image.jpg.

    Raises:
        ValueError: If credentials are missing.
        RuntimeError: If image generation returns no result or URL.
    """
    _check_credentials()

    result = await higgsfield_client.subscribe_async(
        _IMAGE_MODEL,
        arguments={
            "prompt": _image_prompt(copy),
            "aspect_ratio": "1:1",
            "resolution": "720p",
        },
    )

    images = result.get("images") or []
    if not images:
        raise RuntimeError(f"Image generation returned no images. Result: {result}")

    url = images[0].get("url") or images[0].get("raw", {}).get("url", "")
    if not url:
        raise RuntimeError(f"Image result missing URL. Result: {result}")

    image_path = output_dir / "product_image.jpg"
    await _download(url, image_path)
    return image_path


async def _download(url: str, dest: Path) -> None:
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        async with client.stream("GET", url) as resp:
            resp.raise_for_status()
            with dest.open("wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)


def _image_prompt(copy: str) -> str:
    return (
        f"Professional product photography, clean white background, "
        f"studio lighting, commercial quality. Campaign theme: {copy}"
    )
