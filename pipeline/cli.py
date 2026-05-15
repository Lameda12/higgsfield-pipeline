"""CLI entrypoint for higgsfield-pipeline."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv

from pipeline.copy_gen import generate_copy
from pipeline.image_gen import generate_image
from pipeline.scraper import scrape_product
from pipeline.scorer import score_variants
from pipeline.video_gen import generate_video

load_dotenv()


@click.group()
def main() -> None:
    """Higgsfield agentic content pipeline."""


@main.command()
@click.argument("url")
@click.option("--image", is_flag=True, default=False, help="Also generate product image via Kling.")
@click.option("--output-dir", default="outputs", show_default=True, help="Base output directory.")
@click.option("--dry-run", is_flag=True, default=False, help="Scrape + copy only — skip video and image generation.")
def run(url: str, image: bool, output_dir: str, dry_run: bool) -> None:
    """Run the full pipeline for a product URL."""
    asyncio.run(_run_pipeline(url=url, image=image, output_dir=Path(output_dir), dry_run=dry_run))


async def _run_pipeline(url: str, image: bool, output_dir: Path, dry_run: bool = False) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"[pipeline] Output directory: {run_dir}")

    click.echo(f"[scraper] Scraping {url} ...")
    product = await scrape_product(url)
    click.echo(f"[scraper] Got product: {product.get('name', 'unknown')}")

    click.echo("[copy_gen] Generating copy variants ...")
    variants = await generate_copy(product)
    (run_dir / "copy_variants.json").write_text(json.dumps(variants, indent=2))
    click.echo(f"[copy_gen] {len(variants)} variants written.")

    best = score_variants(variants)
    selected_copy = best.get("copy", "")
    (run_dir / "selected_copy.txt").write_text(selected_copy)
    click.echo(f"[scorer] Selected: {selected_copy[:80]}...")

    if dry_run:
        click.echo("[pipeline] Dry run — skipping video and image generation.")
    else:
        click.echo("[video_gen] Generating video ...")
        try:
            video_path = await asyncio.wait_for(
                generate_video(copy=selected_copy, output_dir=run_dir), timeout=120.0
            )
            click.echo(f"[video_gen] Video saved: {video_path}")
        except asyncio.TimeoutError:
            click.echo("[video_gen] WARNING: video generation timed out after 120s")
        except Exception as exc:
            click.echo(f"[video_gen] WARNING: video generation failed — {exc}")

        if image:
            click.echo("[image_gen] Generating image ...")
            try:
                image_path = await asyncio.wait_for(
                    generate_image(copy=selected_copy, output_dir=run_dir), timeout=120.0
                )
                click.echo(f"[image_gen] Image saved: {image_path}")
            except asyncio.TimeoutError:
                click.echo("[image_gen] WARNING: image generation timed out after 120s")
            except Exception as exc:
                click.echo(f"[image_gen] WARNING: image generation failed — {exc}")

    click.echo(f"[pipeline] Done. Assets in {run_dir}")
