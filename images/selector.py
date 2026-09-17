from __future__ import annotations

from images.downloader import download_article_image
from images.overlay import generate_overlay
from models import Article, PostImage


def select_image(article: Article, draft_dir: str) -> PostImage | None:
    image = download_article_image(article, draft_dir)
    if image:
        return image

    image = generate_overlay(article, draft_dir)
    if image:
        return image

    # AI generation is a future fallback
    print(f"    [!] No image available for: {article.title[:50]}")
    return None
