# higgsfield-pipeline

Agentic content pipeline. Give it a product URL; get campaign-ready video and copy.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # fill in your keys
```

## Usage

```bash
pipeline run https://example.com/product
pipeline run https://example.com/product --image   # also generate image via Kling
```

## Output

```
outputs/20260515_143022/
├── copy_variants.json
├── selected_copy.txt
└── campaign_video.mp4
```

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude copy generation |
| `HIGGSFIELD_API_KEY` | Yes | Video generation via MCP |
| `KLING_API_KEY` | No | Image generation (`--image` flag) |
