from __future__ import annotations

import sqlite3

from db import is_seen, mark_seen
from models import Article


def deduplicate(articles: list[Article], conn: sqlite3.Connection) -> list[Article]:
    new_articles = []
    for article in articles:
        if is_seen(conn, article.url):
            continue
        mark_seen(conn, article.url, article.source_id, article.title)
        new_articles.append(article)
    return new_articles
