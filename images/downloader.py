from __future__ import annotations

from pathlib import Path

import httpx

from models import Article, PostImage


def download_article_image(article: Article, draft_dir: str) -> PostImage | None:
    if not article.image_urls:
        return None

    for url in article.image_urls[:3]:
        try:
            resp = httpx.get(url, timeout=15, follow_redirects=True, headers={
                "User-Agent": "linkedin-publisher/1.0"
            })
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "image" not in content_type:
                continue

            ext = ".jpg" if "jpeg" in content_type else ".png"
            path = Path(draft_dir) / f"image{ext}"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(resp.content)

            if path.stat().st_size < 5000:
                path.unlink()
                continue

            return PostImage(
                path=str(path),
                source_type="article",
                original_url=url,
                alt_text=f"Image from: {article.title[:80]}",
            )
        except (httpx.HTTPError, OSError):
            continue

    return None
