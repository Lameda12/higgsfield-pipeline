# higgsfield-pipeline

Agentic content pipeline. Give it a product URL; get campaign-ready video and copy.

Scrapes the product page → generates hook copy variants via Claude → scores and selects the best → generates a short video clip via Higgsfield CLI.

## Prerequisites

- Python 3.12+
- [Higgsfield CLI](https://cloud.higgsfield.ai) installed and authenticated:
  ```bash
  pip install higgsfield
  higgsfield auth login
  ```
- Anthropic API key

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in ANTHROPIC_API_KEY
```

## Usage

```bash
# Full pipeline — scrape + copy + video
pipeline run https://example.com/products/your-product

# Dry run — scrape + copy only, skip video (useful with just ANTHROPIC_API_KEY)
pipeline run https://example.com/products/your-product --dry-run

# Also generate product image via Higgsfield
pipeline run https://example.com/products/your-product --image
```

## Output

```
outputs/20260515_161522/
├── copy_variants.json   # all 3 scored variants
├── selected_copy.txt    # winning hook
└── campaign_video.mp4   # generated video clip
```

## Demo Output

Running against `https://allbirds.com/products/mens-wool-runners`:

**`copy_variants.json`**
```json
[
  {
    "id": 1,
    "angle": "problem-solution",
    "copy": "Tired of uncomfortable sneakers? This wool shoe changes everything.",
    "score": 0.0
  },
  {
    "id": 2,
    "angle": "social-proof",
    "copy": "Called the world's most comfortable shoe by millions of customers.",
    "score": 7.5918
  },
  {
    "id": 3,
    "angle": "curiosity",
    "copy": "The original wool sneaker that started a comfort revolution.",
    "score": 0.0
  }
]
```

**`selected_copy.txt`**
```
Called the world's most comfortable shoe by millions of customers.
```

## Supported Sites

| Site | Method |
|------|--------|
| Shopify stores | `/products/<handle>.json` — reliable, no HTML parsing |
| Amazon | HTML heuristics — may break on layout changes |
| Other | Falls back to Shopify JSON API pattern |

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude copy generation |
| `HIGGSFIELD_API_KEY` | No | Passed to Higgsfield CLI if set |
| `KLING_API_KEY` | No | Image generation (`--image` flag) |

## Security

- SSRF protection on all scraped URLs — blocks private IPs, localhost, non-http/https schemes
- All secrets via env vars — never hardcoded
- `outputs/` and `.env` are gitignored
