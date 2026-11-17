import hashlib
import hmac
import time

from backend.app.core.config import settings

SESSION_COOKIE_NAME = "brand_agent_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7


def create_session_token(now: int | None = None) -> str:
    if not settings.APP_SESSION_SECRET:
        raise RuntimeError("APP_SESSION_SECRET must be configured before creating a session")
    issued_at = int(time.time()) if now is None else now
    payload = str(issued_at)
    signature = hmac.new(
        settings.APP_SESSION_SECRET.encode("utf-8"),
        payload.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}.{signature}"


def is_valid_session(token: str | None, now: int | None = None) -> bool:
    if not token or not settings.APP_SESSION_SECRET:
        return False
    try:
        issued_at_text, signature = token.split(".", 1)
        issued_at = int(issued_at_text)
    except (ValueError, TypeError):
        return False
    current_time = int(time.time()) if now is None else now
    if issued_at > current_time or current_time - issued_at > SESSION_MAX_AGE_SECONDS:
        return False
    expected_signature = hmac.new(
        settings.APP_SESSION_SECRET.encode("utf-8"),
        issued_at_text.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


def is_authenticated(token: str | None) -> bool:
    if not settings.APP_ADMIN_PASSWORD:
        return settings.ENVIRONMENT != "production"
    return is_valid_session(token)
