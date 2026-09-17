from __future__ import annotations

from pathlib import Path

import yaml

from models import Article


def load_summarizer_config() -> dict:
    with open(Path("config/summarizer.yaml")) as f:
        return yaml.safe_load(f)


def build_prompt(article: Article, config: dict) -> tuple[str, str]:
    tone = config.get("tone_guidance", "")
    constraints = config.get("post_constraints", {})
    min_words = constraints.get("min_words", 150)
    max_words = constraints.get("max_words", 300)
    max_hashtags = constraints.get("max_hashtags", 5)

    system_prompt = f"""You are a cybersecurity professional who shares useful intel on LinkedIn.

{tone}

Post constraints:
- Length: {min_words}–{max_words} words
- Include {max_hashtags} or fewer relevant hashtags at the end
- Always include the source link
- Do not use hype words ("critical", "massive", "breaking") unless the severity genuinely warrants it
- Structure: opening observation, 2-3 sentence summary, bullet points of what stood out, brief closing, source link, hashtags"""

    tags_str = ", ".join(article.tags[:10]) if article.tags else "none"

    user_prompt = f"""Write a LinkedIn post about this article.

Title: {article.title}
Source: {article.url}
Tags: {tags_str}

Article content:
{article.body[:3000]}

Write the complete LinkedIn post now."""

    return system_prompt, user_prompt
