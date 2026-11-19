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
    onboarding_completed INTEGER NOT NULL DEFAULT 0,
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

CREATE TABLE IF NOT EXISTS daily_post_runs (
    run_date TEXT PRIMARY KEY,
    post_id TEXT,
    status TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(post_id) REFERENCES content_posts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS linkedin_connections (
    user_id TEXT PRIMARY KEY,
    encrypted_token TEXT NOT NULL,
    person_urn TEXT NOT NULL,
    member_name TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS linkedin_oauth_states (
    state TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS media_assets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    post_id TEXT,
    asset_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_data BYTEA,
    storage_url TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_media_assets_one_image_per_post
    ON media_assets(user_id, post_id)
    WHERE post_id IS NOT NULL AND asset_type = 'image';

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

CREATE TABLE IF NOT EXISTS knowledge_fts (
    user_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    PRIMARY KEY (user_id, entity_type, entity_id)
);
"""


def _postgres_placeholders(query: str) -> str:
    output = []
    in_single_quote = False
    in_double_quote = False
    index = 0
    while index < len(query):
        char = query[index]
        if char == "'" and not in_double_quote:
            if in_single_quote and index + 1 < len(query) and query[index + 1] == "'":
                output.extend(("'", "'"))
                index += 2
                continue
            in_single_quote = not in_single_quote
            output.append(char)
        elif char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            output.append(char)
        elif char == "?" and not in_single_quote and not in_double_quote:
            output.append("%s")
        else:
            output.append(char)
        index += 1
    return "".join(output)


class _PostgreSQLConnection:
    def __init__(self, connection: Any):
        self._connection = connection

    def execute(self, query: str, params: tuple = ()):
        if query.strip().upper() == "BEGIN IMMEDIATE":
            query = "BEGIN"
        postgres_params = tuple(int(value) if isinstance(value, bool) else value for value in params)
        return self._connection.execute(_postgres_placeholders(query), postgres_params)

    def executescript(self, script: str) -> None:
        for statement in script.split(";"):
            if statement.strip():
                self.execute(statement)

    def commit(self) -> None:
        self._connection.commit()


class Database:
    def __init__(self, db_path: str | None = None, database_url: str | None = None):
        self.db_path = db_path or settings.DB_PATH
        self.database_url = settings.DATABASE_URL if database_url is None else database_url
        if self.database_url.startswith("postgres://"):
            self.database_url = "postgresql://" + self.database_url[len("postgres://"):]
        self.uses_postgres = self.database_url.startswith("postgresql://")

    @property
    def driver_name(self) -> str:
        return "postgresql" if self.uses_postgres else "sqlite"

    @contextmanager
    def get_connection(self):
        if self.uses_postgres:
            import psycopg
            from psycopg.rows import dict_row

            connection = psycopg.connect(self.database_url, row_factory=dict_row)
            try:
                yield _PostgreSQLConnection(connection)
            finally:
                connection.close()
            return

        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        """Initializes tables and seeds the local user if not present."""
        if not self.uses_postgres:
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            if self.uses_postgres:
                user_columns = {
                    row["column_name"] for row in conn.execute(
                        """SELECT column_name FROM information_schema.columns
                           WHERE table_schema = current_schema() AND table_name = 'users'"""
                    ).fetchall()
                }
                linkedin_columns = {
                    row["column_name"] for row in conn.execute(
                        """SELECT column_name FROM information_schema.columns
                           WHERE table_schema = current_schema() AND table_name = 'linkedin_connections'"""
                    ).fetchall()
                }
                media_columns = {
                    row["column_name"] for row in conn.execute(
                        """SELECT column_name FROM information_schema.columns
                           WHERE table_schema = current_schema() AND table_name = 'media_assets'"""
                    ).fetchall()
                }
            else:
                user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
                linkedin_columns = {
                    row["name"] for row in conn.execute("PRAGMA table_info(linkedin_connections)").fetchall()
                }
                media_columns = {
                    row["name"] for row in conn.execute("PRAGMA table_info(media_assets)").fetchall()
                }
            if "onboarding_completed" not in user_columns:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN onboarding_completed INTEGER NOT NULL DEFAULT 0"
                )
            if "member_name" not in linkedin_columns:
                conn.execute("ALTER TABLE linkedin_connections ADD COLUMN member_name TEXT")
            if "file_data" not in media_columns:
                conn.execute("ALTER TABLE media_assets ADD COLUMN file_data BYTEA")
            
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
            self.rebuild_knowledge_index(conn)

    @staticmethod
    def rebuild_knowledge_index(conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM knowledge_fts")

        profile_rows = conn.execute(
            "SELECT id, user_id, headline, summary, career_direction, target_audience, writing_voice_notes "
            "FROM professional_profiles"
        ).fetchall()
        for row in profile_rows:
            content = " ".join(
                value for value in (
                    row["summary"], row["career_direction"], row["target_audience"],
                    row["writing_voice_notes"],
                ) if value
            )
            conn.execute(
                "INSERT INTO knowledge_fts (user_id, entity_type, entity_id, title, content) "
                "VALUES (?, 'profile', ?, ?, ?)",
                (row["user_id"], row["id"], row["headline"] or "Professional profile", content),
            )

        for table, title_column, content_columns in (
            ("skills", "name", ("category", "proficiency_level", "evidence_notes")),
            ("projects", "title", ("description", "maturity", "tech_stack", "key_achievements")),
            ("learning_milestones", "title", ("description", "category", "lessons_learned")),
        ):
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            for row in rows:
                content = " ".join(str(row[column]) for column in content_columns if row[column])
                conn.execute(
                    "INSERT INTO knowledge_fts (user_id, entity_type, entity_id, title, content) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (row["user_id"], table, row["id"], row[title_column], content),
                )
        interviews = conn.execute(
            """SELECT id, user_id, interview_date, summary FROM interviews
               WHERE summary IS NOT NULL AND trim(summary) != ''"""
        ).fetchall()
        for interview in interviews:
            conn.execute(
                "INSERT INTO knowledge_fts (user_id, entity_type, entity_id, title, content) "
                "VALUES (?, 'interviews', ?, ?, ?)",
                (
                    interview["user_id"], interview["id"],
                    f"Interview {interview['interview_date']}", interview["summary"],
                ),
            )
        conn.commit()

    def index_knowledge(
        self, user_id: str, entity_type: str, entity_id: str, title: str, content: str
    ) -> None:
        with self.get_connection() as conn:
            conn.execute(
                "DELETE FROM knowledge_fts WHERE user_id = ? AND entity_type = ? AND entity_id = ?",
                (user_id, entity_type, entity_id),
            )
            conn.execute(
                "INSERT INTO knowledge_fts (user_id, entity_type, entity_id, title, content) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, entity_type, entity_id, title, content),
            )
            conn.commit()

    def remove_knowledge(self, user_id: str, entity_type: str, entity_id: str) -> None:
        with self.get_connection() as conn:
            conn.execute(
                "DELETE FROM knowledge_fts WHERE user_id = ? AND entity_type = ? AND entity_id = ?",
                (user_id, entity_type, entity_id),
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
