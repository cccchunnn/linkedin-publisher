"""Extracts images from articles: Open Graph (og:image), inline figures, diagrams, and logos."""

from __future__ import annotations


def extract_images(html: str, base_url: str) -> list[str]:
    raise NotImplementedError
