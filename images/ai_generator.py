"""AI image generation for illustrative diagrams explaining technical concepts."""

from __future__ import annotations

from models import Article, PostImage


def generate_ai_image(article: Article, draft_dir: str, config: dict) -> PostImage | None:
    raise NotImplementedError
