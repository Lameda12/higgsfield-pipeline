# higgsfield-pipeline

Agentic content pipeline: product URL in, campaign-ready image/video assets out. Uses the Higgsfield MCP server for video generation, Claude for copy, and Kling for images.

---

## What This Is

A CLI-driven agentic pipeline. You give it a product URL. It:

1. Scrapes the product page for copy signals (name, price, tagline, key features)
2. Uses Claude to generate hook copy variants (3-5 options, different angles)
3. Picks the highest-scoring variant (or lets you pick)
4. Calls the Higgsfield MCP server to generate a short video clip
5. Optionally calls Kling API for a product image
6. Dumps everything to `outputs/` — video, image, copy JSON

No manual steps. One command.

---

## Stack

- **Python 3.12** — main pipeline language
- **Claude Code** — primary dev tool; Claude claude-sonnet-4-20250514 for copy generation
- **Higgsfield MCP** — video generation via MCP server
- **Kling API** — image generation (optional, gated behind `--image` flag)
- **httpx** — async HTTP for scraping and API calls
- **click** — CLI interface
- **python-dotenv** — env management

---

## Project Structure

```
higgsfield-pipeline/
├── CLAUDE.md               # this file
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── pipeline/
│   ├── __init__.py
│   ├── cli.py              # click entrypoint: `pipeline run <url>`
│   ├── scraper.py          # httpx-based product page scraper
│   ├── copy_gen.py         # Claude API call → hook copy variants
│   ├── video_gen.py        # Higgsfield MCP client
│   ├── image_gen.py        # Kling API client (optional)
│   └── scorer.py           # simple heuristic copy scorer
├── outputs/                # generated assets land here (gitignored)
└── tests/
    ├── test_scraper.py
    └── test_copy_gen.py
```

---

## MVP Scope

The MVP is a working CLI that runs end to end on at least one product URL and produces a video. Image generation is optional in MVP.

**In scope for MVP:**
- `pipeline run <url>` command
- Product page scraping (httpx, basic HTML parsing)
- Copy generation via Claude API (3 variants, JSON output)
- Higgsfield video generation via MCP
- Outputs saved to `outputs/<timestamp>/`

**Out of scope for MVP:**
- Web UI
- Copy selection UI (auto-pick highest score)
- Batch processing
- Kling image generation (flag exists, just not wired)

---

## Environment Variables

```env
ANTHROPIC_API_KEY=
HIGGSFIELD_API_KEY=
KLING_API_KEY=          # optional, only needed for --image
```

Use `.env` locally. Never commit it.

---

## MCP Integration

The Higgsfield MCP server handles video generation. Claude Code connects to it via the MCP protocol. The pipeline calls it programmatically using the MCP client SDK.

**MCP server:** Higgsfield hosted endpoint (URL in env or config)
**Connection:** MCP over HTTP/SSE — standard Anthropic MCP client pattern

For Claude Code sessions, MCP is already wired. For standalone script runs, the pipeline uses `anthropic` SDK with `mcp_servers` param in the API call.

---

## Git Remote

```
https://github.com/Lameda12/higgsfield-pipeline
```

Push to `main`. No branches for MVP — iterate fast, squash later.

---

## Claude Code Instructions

When using Claude Code on this project:

- Read this file first on every new session
- Keep the pipeline modular: one file per concern
- Prefer `async`/`await` throughout (httpx async client)
- Type hint everything
- All secrets via `os.getenv()` — never hardcoded
- Outputs go to `outputs/<timestamp>/` — never overwrite
- Run `python -m pipeline.cli run <url>` to test end-to-end
- If Higgsfield MCP call fails, log the error and continue — don't crash the whole pipeline
- Commit working states often: `git add . && git commit -m "<what works>"`

---

## Build Order

1. Scaffold project: `pyproject.toml`, `cli.py` with stub command, `.env.example`
2. `scraper.py` — scrape a product URL, return structured dict
3. `copy_gen.py` — Claude API call, return 3 hook variants as JSON
4. `scorer.py` — score variants, return best
5. `video_gen.py` — Higgsfield MCP call, return video path
6. Wire everything in `cli.py` — `pipeline run <url>` produces output
7. Write `README.md` — install, usage, demo output
8. Push to GitHub

---

## Definition of Done (MVP)

Running `pipeline run https://example-product.com` produces:

```
outputs/20260515_143022/
├── copy_variants.json
├── selected_copy.txt
└── campaign_video.mp4
```

No crashes. No manual steps between scrape and video output.