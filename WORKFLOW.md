# WORKFLOW.md

Operational workflow for **linkedin-publisher** — how to set up, run daily, and maintain the pipeline.

---

## 1. First-Time Setup

### 1.1 Prerequisites

- Python 3.11+
- A LinkedIn account with a [LinkedIn Developer App](https://www.linkedin.com/developers/apps) (for API access)
- An [Anthropic API key](https://console.anthropic.com/) (for Claude summarization)
- An [OpenAI API key](https://platform.openai.com/) (for AI image generation, optional)

### 1.2 Installation

```bash
git clone https://github.com/cccchunnn/linkedin-publisher.git
cd linkedin-publisher
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.3 Configuration

**Step 1 — Create `.env`** (never committed):
```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...                # optional, for AI image generation
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
```

**Step 2 — Authorize LinkedIn** (one-time OAuth flow):
```bash
python -m publisher.auth
# Opens browser → sign in → authorize → tokens saved to data/linkedin_token.json
```

**Step 3 — Customize sources** (optional):
Edit `config/sources.yaml` to add/remove/reprioritize news sources.

**Step 4 — Add image assets** (optional):
Drop vendor logos and icons into `images/assets/logos/` and `images/assets/icons/` for branded overlays.

---

## 2. Daily Workflow

This is the typical day-to-day cycle. The pipeline is designed around a **generate → review → publish** rhythm.

### 2.1 Run the Pipeline

```bash
python main.py
```

This runs the full pipeline in one shot:
1. Fetches latest articles from all configured sources
2. Filters, deduplicates, and ranks by relevance
3. Generates LinkedIn post summaries via Claude
4. Selects or generates one image per post
5. Saves everything as drafts in `data/drafts/`

**Typical output:**
```
Fetched 47 articles from 6 sources.
After dedup and filtering: 12 candidates.
Selected top 4 articles for summarization.
Generated 4 drafts with images.
Saved 4 drafts for review.
Run 'python -m review.preview' to review text + images.
```

### 2.2 Review Drafts

**Option A — Browser preview** (recommended for first look):
```bash
python -m review.preview
```
Opens an HTML page in your browser showing each draft's text and image side by side.

**Option B — Interactive CLI** (for approve/edit/skip decisions):
```bash
python -m review.cli_review
```

For each draft you'll see:
```
─────────────────────────────────────────────
Draft 1 of 4 | Source: Unit 42
─────────────────────────────────────────────
[Post text displayed here]

Image: data/drafts/draft_001/image.png (overlay)

  [a] Approve
  [e] Edit text
  [i] Regenerate image
  [s] Skip

Your choice:
```

| Action | What happens |
|--------|-------------|
| **Approve** | Draft status → `approved`, ready to publish |
| **Edit text** | Opens the post text in your editor, re-saves on close |
| **Regenerate image** | Sends draft back through the image engine for a new visual |
| **Skip** | Draft stays as `pending_review`, won't be published this round |

### 2.3 Publish Approved Drafts

```bash
python -m publisher.post
```

Only drafts with `status = "approved"` are published. For each:
1. Uploads the image to LinkedIn
2. Creates the post with image attached
3. Updates draft status to `published`
4. Prints the live LinkedIn post URL

**Example output:**
```
Publishing 2 approved drafts...
✓ Draft 001 published → https://www.linkedin.com/feed/update/urn:li:share:...
✓ Draft 003 published → https://www.linkedin.com/feed/update/urn:li:share:...
Done. 2 posts published, 0 failed.
```

---

## 3. Workflow Variations

### 3.1 Ingest Only (No Summarization)

Useful for checking what's new before generating posts:
```bash
python -m ingestion.fetch
```
Check `data/articles/` for what was fetched.

### 3.2 Dry Run (Summaries Without Images or Publishing)

Preview what the summarizer would generate:
```bash
python -m summarizer.generate --dry-run
```
Outputs draft text to the console without saving or generating images.

### 3.3 Regenerate Images for Existing Drafts

If you approved the text but want a different image:
```bash
python -m review.cli_review
# Select [i] Regenerate image for the relevant draft
```

### 3.4 Manual / Ad-Hoc Post

Want to write about something specific that wasn't in the feeds:
1. Create a draft manually in `data/drafts/draft_xxx/post.json`
2. Add your image as `data/drafts/draft_xxx/image.png`
3. Set `"status": "approved"` in the JSON
4. Run `python -m publisher.post`

---

## 4. Scheduling (Automated Runs)

The pipeline runs **once daily at 9:00 AM GMT+8 (1:00 AM UTC)**. It runs independently of Claude Code — you don't need Claude Code open for the pipeline to execute. Claude Code is a development tool; the pipeline is a standalone Python program triggered by your OS scheduler or GitHub Actions.

**Only ingestion + summarization + image generation are automated** — review and publish always require you.

### Option A — Cron (Linux/Mac)

```bash
# Run pipeline at 9 AM GMT+8 (1 AM UTC) daily
0 1 * * * cd /path/to/linkedin-publisher && /path/to/venv/bin/python main.py >> logs/pipeline.log 2>&1
```

### Option B — Task Scheduler (Windows, recommended for this setup)

1. Open **Task Scheduler** → Create Basic Task
2. Name: `linkedin-publisher`
3. Trigger: Daily at **09:00**
4. Action: Start a program
   - Program: `C:\Users\cchun\linkedin-publisher\venv\Scripts\python.exe`
   - Arguments: `main.py`
   - Start in: `C:\Users\cchun\linkedin-publisher`
5. Under Settings, check **"Run task as soon as possible after a scheduled start is missed"** — this ensures that if your PC was off or asleep at 9 AM, the pipeline runs as soon as it wakes up.

### Option C — GitHub Actions (runs in the cloud — PC can be off)

This is the **most reliable option** if you're not always at your machine at 9 AM. GitHub runs the pipeline on their servers, generates drafts, and notifies you via Slack. You review and publish whenever you're ready.

```yaml
# .github/workflows/pipeline.yml
name: Run Pipeline
on:
  schedule:
    - cron: '0 1 * * *'         # 1:00 AM UTC = 9:00 AM GMT+8
  workflow_dispatch:             # manual trigger from GitHub UI

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      # Notify via Slack when drafts are ready
      - name: Notify Slack
        if: success()
        run: |
          DRAFT_COUNT=$(ls -d data/drafts/draft_*/ 2>/dev/null | wc -l)
          curl -X POST "${{ secrets.SLACK_WEBHOOK_URL }}" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"📰 linkedin-publisher: ${DRAFT_COUNT} new drafts ready for review.\"}"

      - uses: actions/upload-artifact@v4
        with:
          name: drafts-${{ github.run_id }}
          path: data/drafts/
```
Drafts are saved as a GitHub Actions artifact. Download them, review locally, then publish.

---

## 5. Notifications

After the pipeline runs at 9 AM, you need to know drafts are waiting — even if you're not at your desk yet. The pipeline sends a notification at the end of each run so you can review whenever you're ready.

### Slack Webhook (recommended)

The simplest and most reliable option. Works whether the pipeline runs locally or in GitHub Actions.

**Setup:**
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From Scratch
2. Choose your workspace, name it `linkedin-publisher`
3. Go to **Incoming Webhooks** → Activate → **Add New Webhook to Workspace**
4. Pick a channel (e.g., `#linkedin-drafts` or DM to yourself)
5. Copy the webhook URL (looks like `https://hooks.slack.com/services/T.../B.../xxx`)
6. Add to `.env`:
   ```env
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../xxx
   ```

**How it works:**
At the end of `main.py`, the pipeline sends one HTTP POST to your Slack webhook:
```python
import httpx

def notify_slack(drafts):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    httpx.post(url, json={
        "text": f"📰 linkedin-publisher: {len(drafts)} new drafts ready for review."
    })
```

You'll see a Slack message like:
> 📰 linkedin-publisher: 4 new drafts ready for review.

No Slack bot, no OAuth, no server — just a single webhook URL. Works on your phone too, so you'll see it whenever you check Slack.

**For GitHub Actions:** The webhook URL is stored as a repository secret (`SLACK_WEBHOOK_URL`) and called in the workflow step (see §4 Option C).

### Other Notification Options

| Method | How it works | When to use |
|--------|-------------|-------------|
| **Email** | Pipeline sends via SMTP (Gmail, SendGrid, etc.) using `smtplib` | If you check email before Slack |
| **Desktop toast** | `plyer` library shows a Windows notification | Only works if pipeline runs locally and PC is on |
| **Telegram bot** | POST to Telegram Bot API with your chat ID | If you prefer Telegram over Slack |

Configure in `config/notifications.yaml`:
```yaml
notifications:
  slack:
    enabled: true
    # webhook URL is read from SLACK_WEBHOOK_URL env var

  email:
    enabled: false
    smtp_host: smtp.gmail.com
    smtp_port: 587
    from: your-email@gmail.com
    to: your-email@gmail.com
    # password is read from EMAIL_PASSWORD env var
```

---

## 6. Maintenance

### 6.1 Token Refresh

LinkedIn access tokens expire after **60 days**. The auth module auto-refreshes, but if it fails:
```bash
python -m publisher.auth
# Re-authorizes via browser
```

### 6.2 Source Health Check

Periodically verify that RSS feeds haven't changed URLs or gone offline:
```bash
python -m ingestion.fetch --check
# Reports which sources are reachable and which failed
```

### 6.3 Cleanup Old Data

Drafts and articles accumulate over time. Prune periodically:
```bash
# Remove articles older than 30 days
python -m tools.cleanup --older-than 30d

# Remove published drafts (already posted, safe to delete)
python -m tools.cleanup --published
```

### 6.4 Updating Sources

To add a new source:
1. Add the entry in `config/sources.yaml`
2. If it's RSS, just add the URL — `rss_fetcher.py` handles it
3. If it requires scraping, add a parser in `ingestion/web_scraper.py`
4. Run `python -m ingestion.fetch` to verify it works

To remove a source:
1. Delete or comment out the entry in `config/sources.yaml`

### 6.5 Updating Image Assets

To add a new vendor logo for overlays:
1. Save the logo as a transparent PNG in `images/assets/logos/`
2. Name it by source ID (e.g., `unit42.png`, `cisa.png`)
3. The overlay engine picks it up automatically based on `article.source_id`

---

## 7. Typical Weekly Rhythm

| Time | What happens |
|------|-------------|
| **9:00 AM** | Pipeline runs automatically (scheduler or GitHub Actions) |
| **9:01 AM** | Slack notification arrives: "X new drafts ready for review" |
| **When you're ready** | Open `review.preview` → review text + images → approve/edit/skip |
| **After review** | Run `publisher.post` → approved drafts go live on LinkedIn |
| **Weekend** | Pipeline still runs, drafts queue up — review Monday morning or skip |
| **Monthly** | Run `--check` on sources, clean up old data, verify LinkedIn token is healthy |

**You don't need to be at your desk at 9 AM.** The pipeline runs, generates drafts, and pings you on Slack. Review and publish whenever you have 5 minutes — could be 9 AM, could be lunch, could be the next day. Nothing posts without your approval.

---

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No articles fetched` | Check internet, run `python -m ingestion.fetch --check` to see which sources are down |
| `LinkedIn 401 Unauthorized` | Token expired — run `python -m publisher.auth` to re-authorize |
| `LinkedIn 429 Too Many Requests` | Hit rate limit — wait and retry, or reduce `max_articles_per_run` |
| `Image too small` | Article image didn't meet 1200x627 — pipeline falls back to overlay or AI generation |
| `Claude API error` | Check `ANTHROPIC_API_KEY` in `.env`, verify quota at console.anthropic.com |
| `No drafts to publish` | Run `python -m review.cli_review` first — drafts must be approved before publishing |
| `Duplicate posts` | Should not happen (dedup via `articles.db`) — check if the DB was deleted or corrupted |
