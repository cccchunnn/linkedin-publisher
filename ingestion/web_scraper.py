"""Web scraper for sources without RSS feeds (e.g., Palo Alto Networks Security Advisories)."""

from __future__ import annotations

from models import Article


def scrape_page(source_id: str, url: str) -> list[Article]:
    raise NotImplementedError
