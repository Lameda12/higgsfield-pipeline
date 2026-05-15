"""Kling image generation — stub implementation."""

from __future__ import annotations

import os
from pathlib import Path


async def generate_image(copy: str, output_dir: Path) -> Path:
    """Generate a product image via the Kling API.

    Args:
        copy: The selected hook copy string.
        output_dir: Directory to write the output image file.

    Returns:
        Path to the generated image file.
    """
    # STUB: raises NotImplementedError.
    # Real impl: POST to Kling API with copy as prompt, download image to output_dir.
    _ = os.getenv("KLING_API_KEY")
    raise NotImplementedError(
        "generate_image not yet implemented — wire up the Kling API client."
    )
