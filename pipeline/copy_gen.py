"""Copy generation via Claude API — stub implementation."""

from __future__ import annotations

import os


async def generate_copy(product: dict) -> list[dict]:
    """Generate hook copy variants for a product using Claude.

    Args:
        product: Structured product dict from scrape_product().

    Returns:
        List of variant dicts, each with: id (int), angle (str), copy (str), score (float).
    """
    # STUB: returns hardcoded fixture variants.
    # Real impl: anthropic.AsyncAnthropic().messages.create(model=..., ...)
    _ = os.getenv("ANTHROPIC_API_KEY")

    name = product.get("name", "this product")
    return [
        {
            "id": 1,
            "angle": "problem-solution",
            "copy": f"Tired of settling? {name} changes everything.",
            "score": 0.0,
        },
        {
            "id": 2,
            "angle": "social-proof",
            "copy": f"Thousands already switched to {name}. Here's why.",
            "score": 0.0,
        },
        {
            "id": 3,
            "angle": "urgency",
            "copy": f"{name}: limited time, unlimited impact.",
            "score": 0.0,
        },
    ]
