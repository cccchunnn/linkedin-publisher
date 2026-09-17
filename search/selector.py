from __future__ import annotations

from models import Article
from search.ranker import rank_articles


def select_top_articles(
    articles: list[Article],
    max_count: int = 5,
    recency_hours: int = 72,
    min_score: float = 0.4,
) -> list[Article]:
    ranked = rank_articles(articles, recency_hours)
    selected = [a for a, score in ranked if score >= min_score]
    return selected[:max_count]
