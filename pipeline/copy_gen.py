"""Copy generation via Claude API."""

from __future__ import annotations

import json
import os

import anthropic

_MODEL = "claude-sonnet-4-20250514"

_SYSTEM = """\
You are an expert direct-response copywriter specializing in short-form video ad hooks.
Given product data, generate exactly 3 hook copy variants — each under 15 words.
Each variant must use a different angle.

Respond ONLY with valid JSON — an array of 3 objects, each with:
  "id": integer (1-3)
  "angle": one of "problem-solution" | "social-proof" | "urgency" | "curiosity" | "benefit-first"
  "copy": the hook string (≤15 words)
  "score": 0.0

No markdown fences. No explanation. JSON only."""


def _build_prompt(product: dict) -> str:
    name = product.get("name", "Unknown Product")
    price = product.get("price", "")
    tagline = product.get("tagline", "")
    features = product.get("features", [])

    lines = [f"Product: {name}"]
    if price:
        lines.append(f"Price: {price}")
    if tagline:
        lines.append(f"Tagline: {tagline}")
    if features:
        lines.append(f"Key features: {', '.join(features[:4])}")

    return "\n".join(lines)


async def generate_copy(product: dict) -> list[dict]:
    """Generate hook copy variants for a product using Claude.

    Args:
        product: Structured product dict from scrape_product().

    Returns:
        List of 3 variant dicts, each with: id (int), angle (str), copy (str), score (float).

    Raises:
        ValueError: If Claude response cannot be parsed as valid variant JSON.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    message = await client.messages.create(
        model=_MODEL,
        max_tokens=512,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _build_prompt(product)}],
    )

    raw = message.content[0].text.strip()

    # Strip accidental markdown fences if Claude includes them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        variants = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Claude returned non-JSON copy response: {raw!r}") from exc

    if not isinstance(variants, list) or not variants:
        raise ValueError(f"Expected list of variants, got: {variants!r}")

    for v in variants:
        v.setdefault("score", 0.0)

    return variants
