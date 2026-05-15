"""Tests for scraper.py."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from pipeline.scraper import scrape_product, _strip_html, _extract_features_from_text


# --- unit tests for helpers ---

def test_strip_html_removes_tags() -> None:
    assert _strip_html("<b>Hello</b> <i>world</i>") == "Hello   world"


def test_extract_features_splits_sentences() -> None:
    text = "Fast delivery. Easy returns. Great quality."
    result = _extract_features_from_text(text)
    assert len(result) == 3
    assert result[0] == "Fast delivery"


def test_extract_features_caps_at_five() -> None:
    text = ". ".join([f"Feature {i}" for i in range(10)]) + "."
    result = _extract_features_from_text(text)
    assert len(result) <= 5


# --- Shopify scraper ---

def _make_shopify_response() -> dict:
    return {
        "product": {
            "title": "Test Gadget",
            "body_html": "<p>Fast and reliable. Easy to use. Great value.</p>",
            "variants": [{"price": "49.99"}],
        }
    }


async def test_scrape_shopify_returns_required_keys() -> None:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = _make_shopify_response()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        url = "https://mystore.myshopify.com/products/test-gadget"
        result = await scrape_product(url)

    for key in ("name", "price", "tagline", "features", "url"):
        assert key in result, f"Missing key: {key}"
    assert result["name"] == "Test Gadget"
    assert result["price"] == "$49.99"
    assert result["url"] == url


async def test_scrape_shopify_invalid_url_raises() -> None:
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        with pytest.raises(ValueError, match="handle"):
            await scrape_product("https://mystore.myshopify.com/collections/all")


# --- Amazon scraper ---

_AMAZON_HTML = """
<html><body>
<span id="productTitle">  Amazing Widget  </span>
<span class="a-price-whole">29</span>
<span class="a-list-item">Ships in 24 hours</span>
<span class="a-list-item">Works with all devices</span>
</body></html>
"""


async def test_scrape_amazon_returns_required_keys() -> None:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = _AMAZON_HTML

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        url = "https://www.amazon.com/dp/B00EXAMPLE"
        result = await scrape_product(url)

    for key in ("name", "price", "tagline", "features", "url"):
        assert key in result, f"Missing key: {key}"
    assert result["name"] == "Amazing Widget"
    assert result["price"] == "$29"
    assert "Ships in 24 hours" in result["features"]
