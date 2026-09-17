import sqlite3
from pathlib import Path

DB_PATH = Path("data/articles.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_urls (
            url TEXT PRIMARY KEY,
            source_id TEXT,
            title TEXT,
            fetched_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_url TEXT,
            post_body TEXT,
            hashtags TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'pending_review',
            review_notes TEXT DEFAULT '',
            generated_at TEXT,
            published_at TEXT
        )
    """)
    conn.commit()
    return conn


def is_seen(conn: sqlite3.Connection, url: str) -> bool:
    row = conn.execute("SELECT 1 FROM seen_urls WHERE url = ?", (url,)).fetchone()
    return row is not None


def mark_seen(conn: sqlite3.Connection, url: str, source_id: str, title: str):
    from datetime import datetime

    conn.execute(
        "INSERT OR IGNORE INTO seen_urls (url, source_id, title, fetched_at) VALUES (?, ?, ?, ?)",
        (url, source_id, title, datetime.now().isoformat()),
    )
    conn.commit()
