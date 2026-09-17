# Product Requirements Document (PRD)

## linkedin-publisher

**Author:** cccchunnn
**Created:** 2026-09-17
**Status:** Draft

---

## 1. Problem Statement

Cybersecurity professionals need to stay current with threats, vulnerabilities, and advisories — but turning that knowledge into consistent LinkedIn content is time-consuming. Manually reading multiple sources, writing summaries, finding visuals, and posting regularly takes 30–60 minutes per post. Most practitioners fall behind or stop posting entirely.

There's also a community gap: many security updates from vendors like Palo Alto Networks, CISA, and threat intelligence outlets don't reach the broader LinkedIn audience because practitioners don't have time to share them.

---

## 2. Product Vision

**linkedin-publisher** is a personal automation tool that discovers cybersecurity news, summarizes it in your voice, pairs it with a relevant image, and queues it for your review — so publishing to LinkedIn takes minutes instead of an hour.

It's not a social media management platform. It's a personal pipeline that does the heavy lifting while keeping you in full control of what goes out under your name.

---

## 3. Target User

**Primary:** A cybersecurity professional (you) who:
- Works in the security industry (e.g., Palo Alto Networks, SOC, IR, threat intel)
- Wants to build a LinkedIn presence around cybersecurity awareness
- Reads advisories and news as part of the job but doesn't have time to write about them
- Values authenticity — posts should sound like a practitioner sharing intel, not a marketing team

**Not for:** Social media managers, marketing teams, or multi-user collaboration. This is a single-user tool.

---

## 4. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Consistent posting cadence | Posts per week | 3–5 |
| Reduce time to publish | Minutes from draft notification to published post | < 5 minutes |
| Cover key sources | % of high-priority articles surfaced | > 80% of Unit 42 + CISA advisories |
| Quality control | Posts rejected or heavily edited during review | < 20% |
| Audience relevance | Post engagement (likes, comments, reposts) | Baseline + growth over time |

---

## 5. Requirements

### 5.1 Ingestion (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| ING-1 | Fetch articles from RSS/Atom feeds on a configurable schedule | P0 |
| ING-2 | Support web scraping for sources without RSS feeds | P0 |
| ING-3 | Extract images from articles (og:image, inline figures, diagrams) | P0 |
| ING-4 | Normalize all content into a unified Article schema | P0 |
| ING-5 | Deduplicate articles across sources (same CVE, same story) | P0 |
| ING-6 | Cache fetched articles locally as JSON partitioned by date | P1 |

**Sources (initial set):**

| Source | Type | Priority |
|--------|------|----------|
| Unit 42 (Palo Alto Networks) | RSS | High |
| Palo Alto Networks Security Advisories | Web scrape | High |
| CISA Alerts & Advisories | RSS | High |
| Krebs on Security | RSS | Medium |
| BleepingComputer | RSS | Medium |
| The Hacker News | RSS | Medium |
| Dark Reading | RSS | Medium |

### 5.2 Search & Filtering (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| FIL-1 | Rank articles by recency (configurable window, default 72 hours) | P0 |
| FIL-2 | Prioritize Palo Alto Networks sources by default | P0 |
| FIL-3 | Boost articles mentioning high-severity CVEs (CVSS 7.0+), active exploitation, zero-days | P0 |
| FIL-4 | Select top N articles per run (configurable, default 3–5) | P0 |
| FIL-5 | Detect near-duplicate content across sources using title similarity | P1 |

### 5.3 Summarization (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| SUM-1 | Generate LinkedIn post text using Claude API | P0 |
| SUM-2 | Enforce post length: 150–300 words | P0 |
| SUM-3 | Enforce tone: practitioner sharing intel with peers — curious, grounded, helpful | P0 |
| SUM-4 | Include 3–5 relevant hashtags per post | P0 |
| SUM-5 | Always include source attribution link | P0 |
| SUM-6 | Avoid hype words unless severity genuinely warrants it | P0 |
| SUM-7 | Inject article context (CVE IDs, affected products, severity) into the prompt | P1 |
| SUM-8 | Validate drafts against post constraints before saving | P1 |

### 5.4 Image Engine (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| IMG-1 | Every post must include exactly one image | P0 |
| IMG-2 | First choice: use a high-quality image from the source article | P0 |
| IMG-3 | Second choice: generate a branded overlay (logo + headline + icon on dark background) | P0 |
| IMG-4 | Third choice: generate an AI-created illustrative diagram explaining the concept | P1 |
| IMG-5 | Ensure images meet LinkedIn specs: minimum 1200x627px, under 5MB, JPEG or PNG | P0 |
| IMG-6 | AI-generated images should be clean flat design, cybersecurity theme, not photorealistic | P1 |
| IMG-7 | Include alt text for accessibility | P2 |

### 5.5 Review (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| REV-1 | Pipeline must never auto-publish — all posts require human approval | P0 |
| REV-2 | Provide HTML preview showing post text and image side by side | P0 |
| REV-3 | Interactive CLI review: approve, edit text, regenerate image, or skip each draft | P0 |
| REV-4 | Only drafts with approved status can be published | P0 |
| REV-5 | Support editing post text during review (opens in editor) | P1 |
| REV-6 | Support regenerating just the image without re-summarizing | P1 |

### 5.6 Publishing (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| PUB-1 | Publish posts to LinkedIn via the Marketing API with image attached | P0 |
| PUB-2 | Upload image to LinkedIn before creating the post | P0 |
| PUB-3 | Handle OAuth 2.0 three-legged flow for authentication | P0 |
| PUB-4 | Auto-refresh LinkedIn tokens before expiry (60-day lifecycle) | P1 |
| PUB-5 | Enforce rate limiting: respect LinkedIn API limits, max 2 posts/day | P1 |
| PUB-6 | Return the live LinkedIn post URL after publishing | P1 |

### 5.7 Scheduling & Notifications (Must Have)

| ID | Requirement | Priority |
|----|-------------|----------|
| SCH-1 | Run pipeline once daily at 9:00 AM GMT+8 | P0 |
| SCH-2 | Support Windows Task Scheduler, cron, and GitHub Actions as scheduling options | P0 |
| SCH-3 | Send Slack notification when new drafts are ready for review | P0 |
| SCH-4 | Pipeline runs independently — no dependency on Claude Code or any interactive tool | P0 |
| SCH-5 | If scheduled run is missed (PC asleep), run as soon as possible after wake | P1 |
| SCH-6 | Support email notifications as an alternative to Slack | P2 |

---

## 6. User Stories

### Daily Use

> **As a** cybersecurity professional,
> **I want to** receive a Slack notification each morning with new draft posts,
> **so that** I can review and publish LinkedIn content in under 5 minutes before starting my workday.

> **As a** cybersecurity professional,
> **I want to** see the post text and image together before publishing,
> **so that** I can ensure the content accurately represents my perspective and the visual is appropriate.

> **As a** cybersecurity professional,
> **I want to** edit the post text or regenerate the image during review,
> **so that** I can refine the output without starting from scratch.

### Content Quality

> **As a** cybersecurity professional,
> **I want** posts written in the tone of a practitioner sharing useful intel,
> **so that** my LinkedIn audience sees authentic, helpful content — not automated marketing.

> **As a** cybersecurity professional,
> **I want** each post to include a relevant, eye-catching image,
> **so that** posts stand out in the LinkedIn feed and complex topics are easier to understand.

> **As a** cybersecurity professional,
> **I want** Palo Alto Networks content (Unit 42, advisories) prioritized,
> **so that** my posts align with my professional focus and expertise.

### Reliability

> **As a** cybersecurity professional,
> **I want** the pipeline to run automatically even if my PC is off,
> **so that** drafts are waiting for me regardless of my morning routine.

> **As a** cybersecurity professional,
> **I want** the system to never post without my explicit approval,
> **so that** nothing goes out under my name that I haven't reviewed.

---

## 7. Scope

### In Scope (v1)

- RSS/web ingestion from 7 cybersecurity sources
- Article deduplication and relevance ranking
- Claude-powered summarization with tone guidelines
- Image engine: article images, branded overlays, AI-generated diagrams
- Human-in-the-loop review (HTML preview + CLI)
- LinkedIn Publishing API integration with image upload
- Slack webhook notifications
- Once-daily scheduling (9 AM GMT+8)
- SQLite storage, local file-based data

### Out of Scope (v1)

- Multi-platform publishing (Twitter/X, Mastodon, Slack channels)
- Engagement analytics and tracking
- Web dashboard for review (CLI only in v1)
- Multi-user or multi-account support
- RAG enrichment from historical articles
- Automated A/B testing of post formats
- Comment monitoring or reply automation

---

## 8. Technical Constraints

| Constraint | Detail |
|------------|--------|
| **Single user** | Designed for one person's LinkedIn account |
| **Local-first** | Data stored locally (SQLite + files), no cloud database |
| **API rate limits** | LinkedIn: ~100 API calls/day; Claude: per-token billing; OpenAI image: per-image billing |
| **LinkedIn OAuth** | Tokens expire after 60 days, require browser-based re-auth |
| **Image generation cost** | AI-generated images cost ~$0.04–0.08 per image (DALL-E 3), used only as fallback |
| **No real-time** | Batch pipeline, not a streaming or real-time system |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM generates inaccurate summary | Incorrect info posted under your name | Human review is mandatory; never auto-publish |
| RSS feed URL changes or goes offline | Missing content from that source | Health check command, isolated failures don't block pipeline |
| LinkedIn API changes or app gets restricted | Can't publish | Token refresh automation, rate limiting, stay within API terms |
| AI-generated image is low quality or misleading | Unprofessional post | Image review is part of the approval flow; can regenerate or swap |
| Over-posting or spammy cadence | Audience fatigue, reduced reach | Max 2 posts/day limit, configurable selection count |
| API costs accumulate | Unexpected bills | Claude and image generation are per-use; monitor with provider dashboards |

---

## 10. Milestones

| Phase | Deliverable | Estimated Effort |
|-------|-------------|-----------------|
| **Phase 1: Core Pipeline** | Ingestion + filtering + summarization (text only, no images) | 1–2 weeks |
| **Phase 2: Image Engine** | Article image extraction, branded overlays, AI generation | 1 week |
| **Phase 3: Review** | HTML preview + CLI review workflow | 3–5 days |
| **Phase 4: Publishing** | LinkedIn API integration, OAuth, image upload | 1 week |
| **Phase 5: Scheduling & Notifications** | Task Scheduler / GitHub Actions + Slack webhook | 2–3 days |
| **Phase 6: Polish & Testing** | End-to-end testing, error handling, documentation | 3–5 days |

**Total estimated effort: 4–6 weeks**

---

## 11. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Which LinkedIn Developer App tier is needed? (Marketing API access requires app review) | Open |
| 2 | Should we support scheduling posts for future times, or always publish immediately on approval? | Open |
| 3 | Do we want a weekly digest post in addition to individual article posts? | Open |
| 4 | Should the pipeline support manually injecting a topic (e.g., "write about Log4Shell anniversary")? | Open |
| 5 | What's the budget ceiling for AI image generation per month? | Open |
