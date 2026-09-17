from __future__ import annotations

from datetime import datetime, timezone
from time import mktime

import ssl

import feedparser
import httpx

from models import Article


def _get_ssl_context() -> ssl.SSLContext:
    """Use system trust store to handle corporate proxy certificates."""
    try:
        import truststore
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except (ImportError, Exception):
        ctx = ssl.create_default_context()
    return ctx


def fetch_rss(source_id: str, url: str) -> list[Article]:
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True, verify=_get_ssl_context(), headers={
            "User-Agent": "linkedin-publisher/1.0"
        })
        resp.raise_for_status()
    except httpx.HTTPError as e:
        print(f"  [!] Failed to fetch {source_id}: {e}")
        return []

    feed = feedparser.parse(resp.text)
    articles = []

    for entry in feed.entries:
        published = datetime.now(tz=timezone.utc)
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)

        summary = entry.get("summary", "") or ""
        body = entry.get("content", [{}])[0].get("value", summary) if entry.get("content") else summary

        image_urls = []
        if hasattr(entry, "media_content"):
            for media in entry.media_content:
                if media.get("medium") == "image" or media.get("type", "").startswith("image"):
                    image_urls.append(media["url"])
        if hasattr(entry, "media_thumbnail"):
            for thumb in entry.media_thumbnail:
                image_urls.append(thumb["url"])

        tags = []
        if hasattr(entry, "tags"):
            tags = [t.get("term", "") for t in entry.tags if t.get("term")]

        articles.append(Article(
            source_id=source_id,
            url=entry.get("link", ""),
            title=entry.get("title", "Untitled"),
            summary=summary[:500],
            body=body[:5000],
            published_at=published,
            fetched_at=datetime.now(tz=timezone.utc),
            tags=tags,
            image_urls=image_urls,
        ))

    return articles
