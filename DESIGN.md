# DESIGN.md

Technical design document for **linkedin-publisher**.

---

## 1. System Overview

linkedin-publisher is a pipeline that continuously discovers cybersecurity news, distills it into practitioner-friendly summaries, and publishes them to LinkedIn. It runs as a scheduled batch job — not a long-running service.

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐    ┌─────────────┐
│  Ingestion   │───▶│   Search &   │───▶│  Summarizer  │───▶│  Image    │───▶│  Publisher   │
│  (fetch)     │    │   Filter     │    │  (Claude AI)  │    │  Engine   │    │  (LinkedIn)  │
└─────────────┘    └─────────────┘    └──────────────┘    └──────────┘    └─────────────┘
       │                  │                   │                  │                │
       ▼                  ▼                   ▼                  ▼                ▼
   Raw articles      Ranked &            Draft text        Post image       Published /
   + images          deduplicated         + image pick      generated        queued posts
                                                                    ▼
                                                              ┌──────────┐
                                                              │  Review   │
                                                              │  (human)  │
                                                              └──────────┘
                                                              Text + image
                                                              must be approved
                                                              before publish
```

---

## 2. Module Design

### 2.1 Ingestion (`ingestion/`)

Responsible for fetching raw content from configured sources.

**Components:**
- `rss_fetcher.py` — Parses RSS/Atom feeds using `feedparser`. Handles Unit 42, CISA, Krebs, BleepingComputer, The Hacker News, Dark Reading.
- `web_scraper.py` — Falls back to `httpx` + `beautifulsoup4` for sources without RSS feeds (e.g., Palo Alto Networks Security Advisories).
- `normalizer.py` — Converts all fetched content into a unified `Article` schema regardless of source format.
- `image_extractor.py` — Extracts images from articles: Open Graph (`og:image`), inline figures, diagrams, and logos. Downloads and caches them locally in `data/images/`.

**Article Schema:**
```python
@dataclass
class Article:
    source_id: str          # e.g., "unit42", "cisa", "krebs"
    url: str                # original article URL
    title: str
    summary: str            # raw excerpt or description from feed
    body: str               # full article text (best-effort extraction)
    published_at: datetime  # original publication timestamp
    fetched_at: datetime    # when we ingested it
    tags: list[str]         # extracted keywords, CVE IDs, product names
    image_urls: list[str]   # images found in the article (og:image, inline figures)
```

**Storage:**
- Articles are stored as JSON files in `data/articles/` partitioned by date (`2026-09-17/`)
- A SQLite database (`data/articles.db`) tracks seen URLs for deduplication across runs

### 2.2 Search & Filter (`search/`)

Decides which articles are worth summarizing.

**Components:**
- `dedup.py` — Checks incoming articles against the SQLite `seen_urls` table. Also detects near-duplicate content across sources (same CVE covered by multiple outlets) using title similarity.
- `ranker.py` — Scores articles on:
  - **Recency**: published within the last 24–72 hours (configurable)
  - **Source priority**: Palo Alto Networks sources score higher by default
  - **Severity signals**: mentions of CVE scores (CVSS 7.0+), active exploitation, zero-day
  - **Topic relevance**: keyword matching against configured interest areas
- `selector.py` — Picks the top N articles per run (default: 3–5) to avoid over-posting

**Configuration** (`config/sources.yaml`):
```yaml
sources:
  - id: unit42
    name: Unit 42
    type: rss
    url: https://unit42.paloaltonetworks.com/feed/
    priority: high

  - id: cisa_alerts
    name: CISA Alerts
    type: rss
    url: https://www.cisa.gov/cybersecurity-advisories/all.xml
    priority: high

  - id: krebs
    name: Krebs on Security
    type: rss
    url: https://krebsonsecurity.com/feed/
    priority: medium

  - id: bleeping
    name: BleepingComputer
    type: rss
    url: https://www.bleepingcomputer.com/feed/
    priority: medium

  - id: hackernews_sec
    name: The Hacker News
    type: rss
    url: https://feeds.feedburner.com/TheHackersNews
    priority: medium

  - id: dark_reading
    name: Dark Reading
    type: rss
    url: https://www.darkreading.com/rss.xml
    priority: medium

selection:
  max_articles_per_run: 5
  recency_window_hours: 72
  min_relevance_score: 0.4
```

### 2.3 Summarizer (`summarizer/`)

Generates LinkedIn-ready summaries using the Claude API.

**Components:**
- `generator.py` — Sends article content to Claude with a system prompt enforcing the post guidelines (tone, structure, length). Returns a `Draft` object.
- `prompt_builder.py` — Constructs the LLM prompt from article data + the template. Injects context like CVE IDs, affected products, and severity.
- `reviewer.py` — Optional validation pass: checks draft length (150–300 words), hashtag count, source attribution present, no hype words.

**Draft Schema:**
```python
@dataclass
class Draft:
    article: Article        # source article
    post_body: str          # generated LinkedIn post text
    hashtags: list[str]     # extracted hashtags
    image: PostImage        # attached image (see §2.4)
    generated_at: datetime
    status: str             # "pending_review" | "approved" | "published"
    review_notes: str       # optional human feedback
```

**Configuration** (`config/summarizer.yaml`):
```yaml
model: claude-sonnet-5
max_tokens: 1024
temperature: 0.3

post_constraints:
  min_words: 150
  max_words: 300
  max_hashtags: 5
  require_source_link: true

tone_guidance: >
  Write as a cybersecurity practitioner sharing useful intel with peers.
  Be curious, grounded, and helpful. Open with what you noticed or
  found interesting. Avoid hype unless severity genuinely warrants it.
```

### 2.4 Image Engine (`images/`)

Every LinkedIn post includes exactly one image. The image engine selects or generates the best visual for each draft.

**Image Source Priority (highest to lowest):**
1. **Article image** — Use a high-quality image extracted from the source article (hero image, diagram, architecture figure). Best when the original visual tells the story.
2. **Branded overlay** — Composite an eye-catching image using source logos, vendor branding (e.g., Palo Alto Networks logo), or a relevant cybersecurity icon with a headline overlay. Good for advisory posts.
3. **AI-generated diagram** — Use an AI image generation API to create an animated-style or illustrative diagram that explains a technical concept (attack flow, network topology, kill chain). Best for complex topics that benefit from a visual explainer.

**Components:**
- `selector.py` — Decides which image strategy to use based on what's available. Checks article `image_urls` first, falls back to branded overlay, then AI generation.
- `downloader.py` — Downloads and validates article images. Checks resolution (minimum 1200x627 for LinkedIn), file size, and format (JPEG/PNG).
- `overlay.py` — Generates branded composite images using `Pillow`. Combines logos, icons, and headline text on a clean background. Sources from `images/assets/` (logos, icons, color palettes).
- `ai_generator.py` — Calls an AI image generation API to produce illustrative diagrams or concept visuals. Sends a prompt derived from the article summary. Generates a clean, professional-style illustration — not photorealistic.
- `resizer.py` — Ensures final image meets LinkedIn recommended specs: 1200x627px, under 5MB, RGB color space.

**PostImage Schema:**
```python
@dataclass
class PostImage:
    path: str               # local path to final image file
    source_type: str        # "article" | "overlay" | "ai_generated"
    original_url: str | None  # if sourced from article
    alt_text: str           # accessibility description
    prompt: str | None      # if AI-generated, the prompt used
```

**Image Assets** (`images/assets/`):
```
images/assets/
├── logos/                # Vendor logos (Palo Alto Networks, CISA, etc.)
├── icons/                # Cybersecurity icons (lock, shield, alert, etc.)
├── backgrounds/          # Clean background templates for overlays
└── fonts/                # Fonts for headline text overlays
```

**Configuration** (`config/images.yaml`):
```yaml
strategy:
  prefer_article_image: true
  min_resolution: [1200, 627]
  fallback_order: ["article", "overlay", "ai_generated"]

overlay:
  background_color: "#1a1a2e"
  text_color: "#ffffff"
  accent_color: "#e94560"
  font: "images/assets/fonts/Inter-Bold.ttf"
  font_size: 48

ai_generation:
  provider: openai         # dall-e-3 or similar
  style: "clean illustrative diagram, flat design, cybersecurity theme, dark background"
  size: "1792x1024"
```

### 2.5 Publisher (`publisher/`)

Handles LinkedIn API integration.

**Components:**
- `auth.py` — Manages OAuth 2.0 three-legged flow. Stores and refreshes tokens in `.env` / a local token cache (`data/linkedin_token.json`).
- `poster.py` — Creates posts via the LinkedIn Marketing API. Uploads the image first via the LinkedIn image upload API, then creates the post with the image attached. **All posts require human approval before publishing** (see §2.6 Review).
- `rate_limiter.py` — Enforces LinkedIn API rate limits and a configurable posting cadence (e.g., max 2 posts/day) to avoid spammy behavior.

**LinkedIn API Flow:**
```
1. User authorizes app → redirect URI receives auth code
2. Exchange auth code for access token + refresh token
3. Upload image via POST /images (register upload → PUT binary)
4. POST /ugcPosts with image asset URN + post text
5. Store post ID for tracking engagement (optional future feature)
```

### 2.6 Review (`review/`)

**Every post must be reviewed and approved before publishing.** The pipeline never auto-publishes. Drafts (text + image) are saved locally for the user to inspect.

**Components:**
- `preview.py` — Renders a local HTML preview of each draft showing the post text and attached image side by side, mimicking how it will appear on LinkedIn. Opens in the default browser.
- `cli_review.py` — Interactive CLI for reviewing drafts. For each draft:
  1. Displays the post text and image path
  2. Opens the image in the default viewer
  3. Prompts: **approve** / **edit** / **regenerate image** / **skip**
- `approval.py` — Manages draft status transitions in the database. Only drafts with `status = "approved"` can be published.

**Review Flow:**
```
python -m review.preview          # open HTML preview of all pending drafts
python -m review.cli_review       # interactive approve/edit/skip per draft

For each draft:
  ┌──────────────────────────────────────┐
  │  Post text + image displayed         │
  │                                      │
  │  [a] Approve  [e] Edit text          │
  │  [i] Regenerate image  [s] Skip      │
  └──────────────────────────────────────┘
        │           │            │
        ▼           ▼            ▼
    approved    re-enter      back to
    → ready     summarizer    image engine
    to publish  with edits    for new image
```

### 2.7 Templates (`templates/`)

- `default.txt` — The standard post template matching the guidelines in CLAUDE.md
- Templates use simple `{variable}` placeholders filled by the summarizer
- Easy to add new templates for different post styles (e.g., CVE-focused, incident response, product update)

---

## 3. Data Storage

```
data/
├── articles.db           # SQLite — seen URLs, article metadata, draft status
├── articles/             # Raw fetched articles as JSON, partitioned by date
│   └── 2026-09-17/
├── images/               # Downloaded article images, cached by URL hash
├── generated/            # AI-generated and overlay images, linked to draft ID
├── drafts/               # Generated drafts (text + image path) pending review
│   └── draft_001/
│       ├── post.json     # draft text, hashtags, status, image reference
│       └── image.png     # final image for this post
├── previews/             # HTML preview files for review
└── linkedin_token.json   # OAuth token cache (gitignored)
```

**Why SQLite**: Single-file, zero-config, sufficient for the volume (dozens of articles/day). No need for a separate database server.

---

## 4. Scheduling & Execution

The pipeline is designed to run as a **scheduled batch job**, not a daemon.

**Options (pick one):**
- **cron** (simplest): `0 8,18 * * * cd /path/to/linkedin-publisher && python main.py`
- **APScheduler** (in-process): For environments where cron isn't available
- **GitHub Actions** (CI-based): Scheduled workflow that runs the pipeline on a cron trigger

**Default cadence**: Twice daily (morning + evening) to catch overnight and daytime news cycles.

**`main.py` execution flow:**
```python
def main():
    # 1. Ingest
    articles = fetch_all_sources()     # includes image extraction

    # 2. Filter
    candidates = deduplicate(articles)
    ranked = rank_and_select(candidates)

    # 3. Summarize
    drafts = generate_summaries(ranked)

    # 4. Generate images
    drafts_with_images = generate_images(drafts)

    # 5. Save for review (always — never auto-publish)
    save_drafts(drafts_with_images)
    print(f"Saved {len(drafts_with_images)} drafts for review.")
    print("Run 'python -m review.preview' to review text + images.")

# Separate publish step — only after human approval
# python -m publisher.post
# (only publishes drafts with status = "approved")
```

---

## 5. Error Handling & Resilience

- **Source failures are isolated**: If one RSS feed is down, the pipeline continues with remaining sources. Failed fetches are logged, not fatal.
- **Rate limiting**: Respects LinkedIn API limits (100 requests/day for most apps). Backs off with exponential retry on 429s.
- **Token refresh**: LinkedIn access tokens expire after 60 days. The auth module auto-refreshes using the refresh token before expiry.
- **Idempotency**: Re-running the pipeline won't re-process or re-post the same articles (dedup via `articles.db`).

---

## 6. Security Considerations

- **No credentials in code**: All secrets (LinkedIn OAuth tokens, Claude API key) live in `.env`, which is gitignored.
- **Token storage**: LinkedIn tokens cached in `data/linkedin_token.json` with `0600` permissions.
- **Input sanitization**: Article content is treated as untrusted input before passing to the LLM — strip HTML, limit length, escape special characters.
- **Human-in-the-loop by default**: The pipeline saves drafts for review unless explicitly told to publish. This prevents the LLM from posting something unintended.

---

## 7. Future Considerations

These are **not in scope** for the initial build but noted for later:

- **Engagement tracking**: Pull LinkedIn post analytics to learn which topics perform well
- **Multi-platform**: Extend to Twitter/X, Mastodon, or internal Slack channels
- **Configurable personas**: Support multiple LinkedIn accounts with different focus areas
- **Web dashboard**: Simple UI for reviewing and approving drafts instead of CLI
- **RAG enrichment**: Index past articles to provide richer context in summaries
