"""Tests for copy_gen.py."""

from __future__ import annotations

import pytest

from pipeline.copy_gen import generate_copy

FIXTURE_PRODUCT = {
    "name": "Test Product",
    "price": "$49.99",
    "tagline": "It just works.",
    "features": ["Fast", "Simple"],
    "url": "https://example.com/test",
}


async def test_generate_copy_returns_list() -> None:
    result = await generate_copy(FIXTURE_PRODUCT)
    assert isinstance(result, list)


async def test_generate_copy_has_at_least_one_variant() -> None:
    result = await generate_copy(FIXTURE_PRODUCT)
    assert len(result) >= 1


async def test_each_variant_has_required_keys() -> None:
    result = await generate_copy(FIXTURE_PRODUCT)
    for variant in result:
        assert "id" in variant
        assert "angle" in variant
        assert "copy" in variant
        assert isinstance(variant["copy"], str)
        assert len(variant["copy"]) > 0
