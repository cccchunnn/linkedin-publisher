from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from db import get_connection
from images.selector import select_image
from ingestion.fetch import fetch_all_sources, load_selection_config
from models import Draft
from search.dedup import deduplicate
from search.selector import select_top_articles
from summarizer.generator import generate_summaries


def save_draft(draft: Draft, draft_id: int) -> Path:
    draft_dir = Path(f"data/drafts/draft_{draft_id:03d}")
    draft_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "source_id": draft.article.source_id,
        "article_url": draft.article.url,
        "article_title": draft.article.title,
        "post_body": draft.post_body,
        "hashtags": draft.hashtags,
        "image_path": draft.image.path if draft.image else None,
        "image_type": draft.image.source_type if draft.image else None,
        "status": draft.status,
        "generated_at": draft.generated_at.isoformat(),
    }

    post_file = draft_dir / "post.json"
    post_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return draft_dir


def run(dry_run: bool = False):
    print("=" * 60)
    print("  linkedin-publisher pipeline")
    print(f"  {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # 1. Ingest
    print("\n[1/4] Ingesting sources...")
    articles = fetch_all_sources()
    print(f"  Total: {len(articles)} articles fetched")

    if not articles:
        print("\nNo articles found. Exiting.")
        return

    # 2. Filter
    print("\n[2/4] Filtering and ranking...")
    conn = get_connection()
    new_articles = deduplicate(articles, conn)
    print(f"  New (not seen before): {len(new_articles)}")

    selection_config = load_selection_config()
    selected = select_top_articles(
        new_articles,
        max_count=selection_config.get("max_articles_per_run", 5),
        recency_hours=selection_config.get("recency_window_hours", 72),
        min_score=selection_config.get("min_relevance_score", 0.4),
    )
    print(f"  Selected top {len(selected)} articles:")
    for i, a in enumerate(selected, 1):
        print(f"    {i}. [{a.source_id}] {a.title[:70]}")

    if not selected:
        print("\nNo articles met the selection criteria. Exiting.")
        return

    if dry_run:
        print("\n--- DRY RUN — skipping summarization, images, and saving ---")
        print(f"\nWould summarize {len(selected)} articles.")
        return

    # 3. Summarize
    print("\n[3/4] Generating summaries...")
    drafts = generate_summaries(selected)
    print(f"  Generated {len(drafts)} drafts")

    # 4. Generate images
    print("\n[4/4] Generating images...")
    next_id = _next_draft_id()
    for i, draft in enumerate(drafts):
        draft_dir = f"data/drafts/draft_{next_id + i:03d}"
        image = select_image(draft.article, draft_dir)
        draft.image = image
        if image:
            print(f"  Draft {next_id + i:03d}: {image.source_type} image")
        else:
            print(f"  Draft {next_id + i:03d}: no image")

    # 5. Save
    print("\nSaving drafts...")
    for i, draft in enumerate(drafts):
        draft_dir = save_draft(draft, next_id + i)
        print(f"  Saved: {draft_dir}")

    print(f"\n{'=' * 60}")
    print(f"  Done. {len(drafts)} drafts saved for review.")
    print(f"  Run 'python -m review.preview' to review text + images.")
    print(f"{'=' * 60}")

    conn.close()


def _next_draft_id() -> int:
    drafts_dir = Path("data/drafts")
    if not drafts_dir.exists():
        return 1
    existing = [d.name for d in drafts_dir.iterdir() if d.is_dir() and d.name.startswith("draft_")]
    if not existing:
        return 1
    nums = []
    for name in existing:
        try:
            nums.append(int(name.split("_")[1]))
        except (IndexError, ValueError):
            pass
    return max(nums) + 1 if nums else 1


def main():
    parser = argparse.ArgumentParser(description="linkedin-publisher pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and rank only, no summarization or images")
    args = parser.parse_args()

    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
