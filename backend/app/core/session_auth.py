import hashlib
import hmac
import secrets
import time

from backend.app.core.db import db
from backend.app.core.config import settings

SESSION_COOKIE_NAME = "brand_agent_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


def create_session_token(now: int | None = None) -> str:
    if not settings.APP_SESSION_SECRET:
        raise RuntimeError("APP_SESSION_SECRET must be configured before creating a session")
    issued_at = int(time.time()) if now is None else now
    payload = f"{issued_at}.{secrets.token_urlsafe(16)}"
    signature = hmac.new(
        settings.APP_SESSION_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}.{signature}"


def _validated_session(token: str | None, now: int | None = None) -> tuple[str, int] | None:
    if not token or not settings.APP_SESSION_SECRET:
        return None
    try:
        issued_at_text, session_id, signature = token.split(".", 2)
        issued_at = int(issued_at_text)
    except (ValueError, TypeError):
        return None
    current_time = int(time.time()) if now is None else now
    if issued_at > current_time or current_time - issued_at > SESSION_MAX_AGE_SECONDS:
        return None
    payload = f"{issued_at_text}.{session_id}"
    expected_signature = hmac.new(
        settings.APP_SESSION_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None
    return session_id, issued_at + SESSION_MAX_AGE_SECONDS


def is_valid_session(token: str | None, now: int | None = None) -> bool:
    session = _validated_session(token, now)
    if not session:
        return False
    session_id, _ = session
    return db.fetch_one(
        "SELECT session_id FROM revoked_sessions WHERE session_id = ?",
        (session_id,),
    ) is None


def revoke_session_token(token: str | None) -> None:
    session = _validated_session(token)
    if not session:
        return
    session_id, expires_at = session
    now = int(time.time())
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO revoked_sessions (session_id, expires_at) VALUES (?, ?) "
            "ON CONFLICT(session_id) DO NOTHING",
            (session_id, expires_at),
        )
        conn.execute("DELETE FROM revoked_sessions WHERE expires_at <= ?", (now,))
        conn.commit()


def is_authenticated(token: str | None) -> bool:
    if not settings.APP_ADMIN_PASSWORD:
        return settings.ENVIRONMENT != "production"
    return is_valid_session(token)
