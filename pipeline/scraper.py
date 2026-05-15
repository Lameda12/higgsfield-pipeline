"""Product page scraper — stub implementation."""

from __future__ import annotations


async def scrape_product(url: str) -> dict:
    """Scrape a product URL and return structured product data.

    Args:
        url: The product page URL to scrape.

    Returns:
        Dict with keys: name, price, tagline, features (list[str]), url.
    """
    # STUB: returns hardcoded fixture. Replace with real httpx + HTML parsing.
    return {
        "name": "Example Product",
        "price": "$99.00",
        "tagline": "The best product you've never heard of.",
        "features": ["Fast", "Reliable", "Affordable"],
        "url": url,
    }
