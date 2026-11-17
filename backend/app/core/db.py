import sqlite3
import os
from contextlib import contextmanager
from typing import Any, List, Dict, Optional
from datetime import datetime, timezone
from backend.app.core.config import settings
from backend.app.core.logging_config import logger

DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_settings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    theme TEXT DEFAULT 'dark',
    reminder_interval_mins INTEGER DEFAULT 15,
    reminders_enabled INTEGER DEFAULT 1,
    preferred_ai_provider TEXT DEFAULT 'gemini',
    offline_mode INTEGER DEFAULT 0,
    github_username TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS professional_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    headline TEXT,
    summary TEXT,
    career_direction TEXT,
    target_audience TEXT,
    writing_voice_notes TEXT,
    seniority_level TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT,
    proficiency_level TEXT NOT NULL,
    verified_by_project INTEGER DEFAULT 0,
    evidence_notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    maturity TEXT NOT NULL,
    github_url TEXT,
    repo_name TEXT,
    tech_stack TEXT DEFAULT '[]',
    key_achievements TEXT DEFAULT '[]',
    screenshots TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS learning_milestones (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    milestone_date TEXT NOT NULL,
    lessons_learned TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interviews (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    interview_date TEXT NOT NULL,
    mode TEXT DEFAULT 'text',
    completed INTEGER DEFAULT 0,
    summary TEXT,
    extracted_topics TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interview_messages (
    id TEXT PRIMARY KEY,
    interview_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    audio_url TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_items (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    credibility_score REAL DEFAULT 0.8,
    category TEXT,
    trend_classification TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content_posts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    interview_id TEXT,
    title TEXT NOT NULL,
    topic TEXT,
    content_category TEXT NOT NULL,
    draft_versions TEXT DEFAULT '[]',
    final_content TEXT NOT NULL,
    hashtags TEXT DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft',
    scheduled_for TEXT,
    published_at TEXT,
    linkedin_post_id TEXT,
    approval_log TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS media_assets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    post_id TEXT,
    asset_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    storage_url TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS networking_suggestions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    person_name TEXT NOT NULL,
    profile_url TEXT,
    target_role TEXT,
    reason TEXT NOT NULL,
    connection_note_draft TEXT,
    comment_draft TEXT,
    status TEXT DEFAULT 'suggested',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

class Database:
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables and seeds the local user if not present."""
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            
            # Check if default user exists
            cursor = conn.execute("SELECT id FROM users WHERE id = ?", (DEFAULT_USER_ID,))
            row = cursor.fetchone()
            now = datetime.now(timezone.utc).isoformat()
            if not row:
                logger.info(f"Seeding default local user {DEFAULT_USER_ID}")
                conn.execute(
                    "INSERT INTO users (id, email, full_name, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (DEFAULT_USER_ID, "developer@local.host", "Engineering Leader", now, now)
                )
                conn.execute(
                    """INSERT INTO user_settings 
                       (id, user_id, theme, reminder_interval_mins, reminders_enabled, preferred_ai_provider, offline_mode, created_at, updated_at) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("settings-001", DEFAULT_USER_ID, "dark", 15, 1, "gemini", 0, now, now)
                )
                conn.execute(
                    """INSERT INTO professional_profiles
                       (id, user_id, headline, summary, career_direction, target_audience, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    ("profile-001", DEFAULT_USER_ID, "AI Systems & Full-Stack Engineer", 
                     "Architecting intelligent, high-reliability personal branding systems.",
                     "Building high-impact developer and AI tooling", 
                     "Engineering leaders, peers, tech founders", now, now)
                )
                conn.commit()

    def execute_sync(self, query: str, params: tuple = ()) -> None:
        with self.get_connection() as conn:
            conn.execute(query, params)
            conn.commit()

    def fetch_one_sync(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def fetch_all_sync(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # Aliases
    execute = execute_sync
    fetch_one = fetch_one_sync
    fetch_all = fetch_all_sync

db = Database()
