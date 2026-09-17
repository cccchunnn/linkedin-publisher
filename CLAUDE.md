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
├── ingestion/        # Source fetchers (RSS, web scraping, API clients)
├── search/           # Content filtering, deduplication, relevance ranking
├── summarizer/       # LLM-powered summarization pipeline
├── publisher/        # LinkedIn API integration (OAuth 2.0, post creation)
├── config/           # Source URLs, scheduling, API credentials reference
├── templates/        # LinkedIn post templates and formatting rules
└── tests/
```

### Data Flow

```
Sources (RSS/APIs/Scraping)
    → Ingestion (fetch + normalize)
    → Search & Filter (relevance, dedup, recency)
    → Summarizer (LLM-generated highlights)
    → Publisher (LinkedIn API draft/post)
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

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (ingest → summarize → draft)
python main.py

# Ingest sources only
python -m ingestion.fetch

# Generate summaries without publishing
python -m summarizer.generate --dry-run

# Publish a draft to LinkedIn
python -m publisher.post --draft

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

## Tech Stack

- **Python 3.11+**
- **RSS/Web**: `feedparser`, `httpx`, `beautifulsoup4`
- **LLM**: Anthropic Claude API for summarization
- **LinkedIn**: LinkedIn Marketing API (OAuth 2.0 three-legged flow)
- **Scheduling**: cron or APScheduler for recurring ingestion
- **Testing**: pytest
- **Linting**: ruff
