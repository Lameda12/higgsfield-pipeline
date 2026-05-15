"""Product page scraper — Shopify JSON API + Amazon HTML fallback."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_TIMEOUT = httpx.Timeout(15.0)


async def scrape_product(url: str) -> dict:
    """Scrape a product URL and return structured product data.

    Dispatches to Shopify JSON API or Amazon HTML scraper based on URL.

    Args:
        url: The product page URL to scrape.

    Returns:
        Dict with keys: name, price, tagline, features (list[str]), url.

    Raises:
        ValueError: If the URL is not a supported site or product data cannot be extracted.
    """
    host = urlparse(url).netloc.lower()

    async with httpx.AsyncClient(headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True) as client:
        if "amazon." in host:
            return await _scrape_amazon(client, url)
        return await _scrape_shopify(client, url)


async def _scrape_shopify(client: httpx.AsyncClient, url: str) -> dict:
    """Scrape via Shopify /products/<handle>.json endpoint."""
    parsed = urlparse(url)
    # Extract handle from path: /products/<handle> or /products/<handle>/...
    match = re.search(r"/products/([^/?#]+)", parsed.path)
    if not match:
        raise ValueError(f"Cannot extract Shopify product handle from URL: {url}")

    handle = match.group(1)
    json_url = f"{parsed.scheme}://{parsed.netloc}/products/{handle}.json"

    resp = await client.get(json_url)
    resp.raise_for_status()
    data = resp.json().get("product", {})

    name: str = data.get("title", "")
    tagline: str = _strip_html(data.get("body_html", ""))[:200]

    # Features: bullet-like sentences from body_html
    features = _extract_features_from_text(tagline)

    # Price from first available variant
    price = ""
    variants = data.get("variants", [])
    if variants:
        raw_price = variants[0].get("price", "")
        price = f"${raw_price}" if raw_price and not str(raw_price).startswith("$") else str(raw_price)

    if not name:
        raise ValueError(f"No product name found at {json_url}")

    return {"name": name, "price": price, "tagline": tagline, "features": features, "url": url}


async def _scrape_amazon(client: httpx.AsyncClient, url: str) -> dict:
    """Scrape Amazon product page via HTML heuristics."""
    resp = await client.get(url)
    resp.raise_for_status()
    html = resp.text

    name = _re_extract(html, [
        r'<span id="productTitle"[^>]*>\s*(.*?)\s*</span>',
        r'"title"\s*:\s*"([^"]{5,})"',
    ])

    price = _re_extract(html, [
        r'<span class="a-price-whole">([^<]+)</span>',
        r'"priceAmount"\s*:\s*([\d.]+)',
        r'id="priceblock_ourprice"[^>]*>\s*\$?([\d.,]+)',
    ])
    if price and not price.startswith("$"):
        price = f"${price}"

    # Bullet features from feature-bullets section
    raw_bullets = re.findall(
        r'<span class="a-list-item">\s*(.*?)\s*</span>',
        html,
        re.DOTALL,
    )
    features = [_strip_html(b).strip() for b in raw_bullets if len(b.strip()) > 5][:6]

    tagline = features[0] if features else name

    if not name:
        raise ValueError(f"Could not extract product name from Amazon page: {url}")

    return {"name": name, "price": price, "tagline": tagline, "features": features, "url": url}


def _re_extract(html: str, patterns: list[str]) -> str:
    for pattern in patterns:
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            return _strip_html(m.group(1)).strip()
    return ""


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).strip()


def _extract_features_from_text(text: str) -> list[str]:
    """Split text into feature-like sentences (up to 5)."""
    sentences = re.split(r"[.!?\n]+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 10][:5]
