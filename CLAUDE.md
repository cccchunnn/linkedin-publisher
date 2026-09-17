# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Objective

**linkedin-publisher** automates cybersecurity awareness on LinkedIn by:
1. Ingesting the latest cybersecurity blogs, advisories, and news — with a focus on **Palo Alto Networks** (Unit 42, Cortex, Prisma, PAN-OS advisories)
2. Summarizing key highlights into concise, professional posts
3. Publishing or drafting those summaries to LinkedIn to raise cybersecurity awareness

## Architecture Overview

```
linkedin-publisher/
├── ingestion/        # Source fetchers (RSS, web scraping, API clients, image extraction)
├── search/           # Content filtering, deduplication, relevance ranking
├── summarizer/       # LLM-powered summarization pipeline
├── images/           # Image engine (article images, branded overlays, AI-generated diagrams)
│   └── assets/       # Logos, icons, backgrounds, fonts for overlays
├── review/           # Human review workflow (HTML preview, CLI approval)
├── publisher/        # LinkedIn API integration (OAuth 2.0, image upload, post creation)
├── config/           # Source URLs, scheduling, API credentials reference
├── templates/        # LinkedIn post templates and formatting rules
└── tests/
```

### Data Flow

```
Sources (RSS/APIs/Scraping)
    → Ingestion (fetch + normalize + extract images)
    → Search & Filter (relevance, dedup, recency)
    → Summarizer (LLM-generated highlights)
    → Image Engine (select or generate one image per post)
    → Review (human approves text + image before publish)
    → Publisher (LinkedIn API image upload + post)
```

## Key Sources to Ingest

- **Palo Alto Networks**: Unit 42 blog, Security Advisories, Cortex/XSIAM release notes
- **General Cyber News**: CISA alerts, Krebs on Security, BleepingComputer, The Hacker News, Dark Reading
- **Threat Intelligence Feeds**: CVE databases, MITRE ATT&CK updates

## LinkedIn Post Guidelines

- Posts should be 150–300 words — concise and scannable
- Open with what you noticed or found interesting — share it like a peer, not a keynote speaker
- Write as a cybersecurity practitioner sharing useful intel with the community, not pitching or lecturing
- Tone: curious, grounded, helpful — the voice of someone who reads advisories and wants others to benefit too
- Avoid hype words ("critical", "massive", "breaking") unless the severity genuinely warrants it
- Include 3–5 relevant hashtags (e.g., #CyberSecurity #PaloAltoNetworks #ThreatIntel #InfoSec)
- Always attribute the original source with a link
- Every post must include one image (see Image Guidelines below)
- Example structure:
  ```
  Came across this advisory from Unit 42 — worth a read if you're
  running [affected product/version].

  [2-3 sentence summary of the finding and what's relevant]

  A few things that stood out:
  • [Detail 1]
  • [Detail 2]
  • [Detail 3]

  Sharing in case it's useful for anyone managing similar environments.

  Source: [link]

  #CyberSecurity #PaloAltoNetworks #ThreatIntel
  ```

## Image Guidelines

Each post includes exactly one image. The image engine picks the best option in this order:

1. **Article image** — A high-quality figure, diagram, or hero image from the source article
2. **Branded overlay** — A composite with vendor logos, cybersecurity icons, and a headline on a clean dark background
3. **AI-generated diagram** — An illustrative, animated-style diagram explaining a technical concept (attack flow, network topology, kill chain)

- Images must be at least 1200x627px (LinkedIn recommended), under 5MB, JPEG or PNG
- AI-generated images should be professional and clean — flat design, cybersecurity theme, not photorealistic
- All images are reviewed alongside the post text before publishing

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (ingest → summarize → generate images → save drafts)
python main.py

# Ingest sources only
python -m ingestion.fetch

# Generate summaries without images
python -m summarizer.generate --dry-run

# Review drafts (text + image) in browser
python -m review.preview

# Interactive CLI review (approve / edit / regenerate image / skip)
python -m review.cli_review

# Publish approved drafts to LinkedIn
python -m publisher.post

# Run tests
pytest

# Run a single test
pytest tests/test_ingestion.py::test_rss_fetch

# Lint
ruff check .
```

## Configuration

- API credentials (LinkedIn OAuth, any news APIs) go in `.env` — never committed
- Source URLs and scheduling config live in `config/sources.yaml`
- LLM summarization settings (model, prompt templates) in `config/summarizer.yaml`
- Image engine settings (overlay branding, AI generation style) in `config/images.yaml`

## Tech Stack

- **Python 3.11+**
- **RSS/Web**: `feedparser`, `httpx`, `beautifulsoup4`
- **LLM**: Anthropic Claude API for summarization
- **Image processing**: `Pillow` for branded overlays and resizing
- **Image generation**: AI image API (e.g., DALL-E 3) for concept diagrams
- **LinkedIn**: LinkedIn Marketing API (OAuth 2.0 three-legged flow)
- **Scheduling**: cron or APScheduler for recurring ingestion
- **Testing**: pytest
- **Linting**: ruff

## Review Workflow

The pipeline **never auto-publishes**. Every post (text + image) must be reviewed and approved:

1. `python main.py` — runs the full pipeline, saves drafts
2. `python -m review.preview` — opens HTML preview in browser showing text + image
3. `python -m review.cli_review` — approve, edit text, regenerate image, or skip each draft
4. `python -m publisher.post` — publishes only approved drafts
