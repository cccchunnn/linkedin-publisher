from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    source_id: str
    url: str
    title: str
    summary: str
    body: str
    published_at: datetime
    fetched_at: datetime
    tags: list[str] = field(default_factory=list)
    image_urls: list[str] = field(default_factory=list)


@dataclass
class PostImage:
    path: str
    source_type: str
    original_url: str | None = None
    alt_text: str = ""
    prompt: str | None = None


@dataclass
class Draft:
    article: Article
    post_body: str
    hashtags: list[str] = field(default_factory=list)
    image: PostImage | None = None
    generated_at: datetime = field(default_factory=datetime.now)
    status: str = "pending_review"
    review_notes: str = ""
