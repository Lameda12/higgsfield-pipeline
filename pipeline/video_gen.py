"""Higgsfield video generation via MCP — stub implementation."""

from __future__ import annotations

import os
from pathlib import Path


async def generate_video(copy: str, output_dir: Path) -> Path:
    """Generate a video clip via Higgsfield MCP.

    Args:
        copy: The selected hook copy string.
        output_dir: Directory to write the output video file.

    Returns:
        Path to the generated video file.
    """
    # STUB: raises NotImplementedError.
    # Real impl: connect to Higgsfield MCP server, call video generation tool,
    # poll for completion, download artifact to output_dir / "campaign_video.mp4".
    _ = os.getenv("HIGGSFIELD_API_KEY")
    raise NotImplementedError(
        "generate_video not yet implemented — wire up the Higgsfield MCP client."
    )
