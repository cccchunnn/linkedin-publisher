from __future__ import annotations

import json
import webbrowser
from pathlib import Path


def generate_preview():
    drafts_dir = Path("data/drafts")
    if not drafts_dir.exists():
        print("No drafts found.")
        return

    draft_dirs = sorted(drafts_dir.iterdir())
    if not draft_dirs:
        print("No drafts found.")
        return

    html_parts = ["""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>LinkedIn Publisher — Draft Review</title>
<style>
body { font-family: -apple-system, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
h1 { color: #e94560; }
.draft { display: flex; gap: 30px; background: #16213e; border-radius: 12px; padding: 24px; margin: 20px 0; }
.draft-text { flex: 1; white-space: pre-wrap; line-height: 1.6; }
.draft-image { flex: 0 0 400px; }
.draft-image img { max-width: 100%; border-radius: 8px; }
.meta { color: #888; font-size: 14px; margin-bottom: 12px; }
.status { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
.status.pending_review { background: #e94560; }
.status.approved { background: #2ecc71; }
.status.published { background: #3498db; }
hr { border: 1px solid #333; }
</style></head><body>
<h1>Draft Review</h1>"""]

    for d in draft_dirs:
        post_file = d / "post.json"
        if not post_file.exists():
            continue

        data = json.loads(post_file.read_text(encoding="utf-8"))
        status = data.get("status", "pending_review")
        image_path = d / "image.png"
        image_jpg = d / "image.jpg"

        img_tag = ""
        if image_path.exists():
            img_tag = f'<img src="file:///{image_path.resolve()}" alt="post image">'
        elif image_jpg.exists():
            img_tag = f'<img src="file:///{image_jpg.resolve()}" alt="post image">'

        html_parts.append(f"""
<div class="draft">
  <div class="draft-text">
    <div class="meta">
      <span class="status {status}">{status.upper()}</span>
      &nbsp; Source: {data.get('source_id', 'unknown')} &nbsp; | &nbsp; {data.get('generated_at', '')}
    </div>
    <div>{data.get('post_body', '')}</div>
  </div>
  <div class="draft-image">{img_tag}</div>
</div>""")

    html_parts.append("</body></html>")

    preview_path = Path("data/previews/review.html")
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_path.write_text("\n".join(html_parts), encoding="utf-8")

    print(f"Preview saved to {preview_path}")
    webbrowser.open(str(preview_path.resolve()))


if __name__ == "__main__":
    generate_preview()
