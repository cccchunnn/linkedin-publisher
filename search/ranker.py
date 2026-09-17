from __future__ import annotations

import re
from datetime import datetime, timezone

from models import Article

PRIORITY_SCORES = {"high": 3.0, "medium": 2.0, "low": 1.0}

SOURCE_PRIORITIES = {
    "unit42": "high",
    "cisa_alerts": "high",
    "krebs": "medium",
    "bleeping": "medium",
    "hackernews_sec": "medium",
    "dark_reading": "medium",
}

CVE_PATTERN = re.compile(r"CVE-\d{4}-\d+", re.IGNORECASE)
SEVERITY_KEYWORDS = [
    "zero-day", "0-day", "actively exploited", "in the wild",
    "critical vulnerability", "remote code execution", "rce",
]


def score_article(article: Article, recency_hours: int = 72) -> float:
    score = 0.0

    priority = SOURCE_PRIORITIES.get(article.source_id, "low")
    score += PRIORITY_SCORES[priority]

    age_hours = (datetime.now(tz=timezone.utc) - article.published_at).total_seconds() / 3600
    if age_hours <= 24:
        score += 3.0
    elif age_hours <= 48:
        score += 2.0
    elif age_hours <= recency_hours:
        score += 1.0

    text = f"{article.title} {article.summary}".lower()

    cves = CVE_PATTERN.findall(text)
    score += min(len(cves) * 1.0, 3.0)

    for keyword in SEVERITY_KEYWORDS:
        if keyword in text:
            score += 2.0
            break

    return score


def rank_articles(articles: list[Article], recency_hours: int = 72) -> list[tuple[Article, float]]:
    scored = [(a, score_article(a, recency_hours)) for a in articles]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
