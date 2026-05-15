"""Tests for copy_gen.py."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pipeline.copy_gen import generate_copy, _build_prompt

FIXTURE_PRODUCT = {
    "name": "Test Widget",
    "price": "$49.99",
    "tagline": "It just works.",
    "features": ["Fast", "Simple", "Reliable"],
    "url": "https://example.com/test",
}

_GOOD_VARIANTS = [
    {"id": 1, "angle": "problem-solution", "copy": "Stop wasting time. Test Widget fixes it.", "score": 0.0},
    {"id": 2, "angle": "social-proof", "copy": "10,000 users switched to Test Widget.", "score": 0.0},
    {"id": 3, "angle": "urgency", "copy": "Test Widget: limited offer ends soon.", "score": 0.0},
]


def _mock_message(text: str) -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    return msg


def _patch_client(return_text: str):
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=_mock_message(return_text))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    return patch("pipeline.copy_gen.anthropic.AsyncAnthropic", return_value=mock_client)


# --- unit tests ---

def test_build_prompt_contains_product_name() -> None:
    prompt = _build_prompt(FIXTURE_PRODUCT)
    assert "Test Widget" in prompt


def test_build_prompt_contains_features() -> None:
    prompt = _build_prompt(FIXTURE_PRODUCT)
    assert "Fast" in prompt


def test_build_prompt_handles_missing_optional_fields() -> None:
    prompt = _build_prompt({"name": "Minimal"})
    assert "Minimal" in prompt


# --- integration-style tests (mocked Anthropic) ---

async def test_generate_copy_returns_list() -> None:
    with _patch_client(json.dumps(_GOOD_VARIANTS)):
        result = await generate_copy(FIXTURE_PRODUCT)
    assert isinstance(result, list)


async def test_generate_copy_returns_three_variants() -> None:
    with _patch_client(json.dumps(_GOOD_VARIANTS)):
        result = await generate_copy(FIXTURE_PRODUCT)
    assert len(result) == 3


async def test_each_variant_has_required_keys() -> None:
    with _patch_client(json.dumps(_GOOD_VARIANTS)):
        result = await generate_copy(FIXTURE_PRODUCT)
    for v in result:
        assert "id" in v
        assert "angle" in v
        assert "copy" in v
        assert isinstance(v["copy"], str) and len(v["copy"]) > 0


async def test_markdown_fences_stripped() -> None:
    fenced = f"```json\n{json.dumps(_GOOD_VARIANTS)}\n```"
    with _patch_client(fenced):
        result = await generate_copy(FIXTURE_PRODUCT)
    assert len(result) == 3


async def test_invalid_json_raises_value_error() -> None:
    with _patch_client("not json at all"):
        with pytest.raises(ValueError, match="non-JSON"):
            await generate_copy(FIXTURE_PRODUCT)


async def test_missing_api_key_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        await generate_copy(FIXTURE_PRODUCT)
