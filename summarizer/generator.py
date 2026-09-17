from __future__ import annotations

import os
import re
from datetime import datetime, timezone

from models import Article, Draft
from summarizer.prompt_builder import build_prompt, load_summarizer_config


def generate_summary(article: Article) -> Draft | None:
    config = load_summarizer_config()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return _generate_mock(article, config)

    return _generate_with_claude(article, config, api_key)


def _generate_with_claude(article: Article, config: dict, api_key: str) -> Draft | None:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt, user_prompt = build_prompt(article, config)

    try:
        response = client.messages.create(
            model=config.get("model", "claude-sonnet-5"),
            max_tokens=config.get("max_tokens", 1024),
            temperature=config.get("temperature", 0.3),
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        post_body = response.content[0].text
    except Exception as e:
        print(f"  [!] Claude API error for '{article.title[:50]}': {e}")
        return None

    hashtags = re.findall(r"#\w+", post_body)

    return Draft(
        article=article,
        post_body=post_body,
        hashtags=hashtags,
        generated_at=datetime.now(tz=timezone.utc),
    )


def _generate_mock(article: Article, config: dict) -> Draft:
    """Generate a placeholder draft when no API key is available."""
    tags_str = " ".join(article.tags[:5]) if article.tags else ""
    hashtags = ["#CyberSecurity", "#ThreatIntel", "#InfoSec"]
    if "unit42" in article.source_id:
        hashtags.append("#PaloAltoNetworks")

    post_body = f"""Came across this from {article.source_id} — worth a look.

{article.title}

{article.summary[:200]}

Sharing in case it's useful for anyone tracking these developments.

Source: {article.url}

{' '.join(hashtags)}"""

    return Draft(
        article=article,
        post_body=post_body,
        hashtags=hashtags,
        generated_at=datetime.now(tz=timezone.utc),
    )


def generate_summaries(articles: list[Article]) -> list[Draft]:
    drafts = []
    for article in articles:
        print(f"  Summarizing: {article.title[:70]}...")
        draft = generate_summary(article)
        if draft:
            drafts.append(draft)
    return drafts
