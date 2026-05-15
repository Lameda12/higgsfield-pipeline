"""Tests for scraper.py."""

from __future__ import annotations

import pytest

from pipeline.scraper import scrape_product


async def test_scrape_product_returns_dict() -> None:
    result = await scrape_product("https://example.com/product")
    assert isinstance(result, dict)


async def test_scrape_product_has_required_keys() -> None:
    result = await scrape_product("https://example.com/product")
    for key in ("name", "price", "tagline", "features", "url"):
        assert key in result, f"Missing key: {key}"


async def test_scrape_product_url_echoed() -> None:
    url = "https://example.com/my-product"
    result = await scrape_product(url)
    assert result["url"] == url
