from __future__ import annotations

from pathlib import Path

import yaml

from ingestion.rss_fetcher import fetch_rss
from models import Article


def load_sources() -> list[dict]:
    config_path = Path("config/sources.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def load_selection_config() -> dict:
    config_path = Path("config/sources.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config.get("selection", {})


def fetch_all_sources() -> list[Article]:
    sources = load_sources()
    all_articles: list[Article] = []

    for source in sources:
        source_id = source["id"]
        url = source["url"]
        source_type = source.get("type", "rss")

        print(f"  Fetching {source['name']} ({source_id})...")

        if source_type == "rss":
            articles = fetch_rss(source_id, url)
        else:
            print(f"  [!] Unsupported source type: {source_type}, skipping")
            continue

        print(f"    Found {len(articles)} articles")
        all_articles.extend(articles)

    return all_articles


if __name__ == "__main__":
    print("Fetching all sources...")
    articles = fetch_all_sources()
    print(f"\nTotal: {len(articles)} articles fetched")
    for a in articles[:10]:
        print(f"  [{a.source_id}] {a.title[:80]}")
