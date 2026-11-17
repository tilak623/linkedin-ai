import hmac
import time
from threading import Lock

from fastapi import APIRouter, HTTPException, Request, Response, status

from backend.app.core.config import settings
from backend.app.core.db import db, DEFAULT_USER_ID
from backend.app.core.session_auth import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    create_session_token,
    is_authenticated,
)
from backend.app.models.schemas import ApiResponse, LoginRequest, UserAuthStatus, UserProfileRead, UserSettingsRead

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])
LOGIN_WINDOW_SECONDS = 15 * 60
MAX_LOGIN_FAILURES = 5
_LOGIN_FAILURES: dict[str, tuple[float, int]] = {}
_LOGIN_FAILURES_LOCK = Lock()


def _client_address(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _login_retry_after(client_address: str, now: float) -> int:
    with _LOGIN_FAILURES_LOCK:
        attempt = _LOGIN_FAILURES.get(client_address)
        if not attempt:
            return 0
        first_attempt, failures = attempt
        if now - first_attempt >= LOGIN_WINDOW_SECONDS:
            _LOGIN_FAILURES.pop(client_address, None)
            return 0
        if failures >= MAX_LOGIN_FAILURES:
            return max(1, int(LOGIN_WINDOW_SECONDS - (now - first_attempt)))
    return 0

@router.get("/me", response_model=ApiResponse[UserAuthStatus])
def get_current_user_status(request: Request):
    authenticated = is_authenticated(request.cookies.get(SESSION_COOKIE_NAME))
    if not authenticated:
        return ApiResponse(
            success=True,
            data=UserAuthStatus(
                authenticated=False,
                user_id="",
                email="",
                full_name="",
                onboarding_completed=False,
            ),
        )
    user = db.fetch_one("SELECT * FROM users WHERE id = ?", (DEFAULT_USER_ID,))
    profile = db.fetch_one("SELECT * FROM professional_profiles WHERE user_id = ?", (DEFAULT_USER_ID,))
    settings = db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (DEFAULT_USER_ID,))
    
    profile_data = None
    if profile:
        profile_data = UserProfileRead(
            id=profile["id"],
            user_id=profile["user_id"],
            headline=profile["headline"],
            summary=profile["summary"],
            career_direction=profile["career_direction"],
            target_audience=profile["target_audience"],
            writing_voice_notes=profile["writing_voice_notes"],
            seniority_level=profile["seniority_level"],
            created_at=profile["created_at"],
            updated_at=profile["updated_at"]
        )
        
    settings_data = None
    if settings:
        settings_data = UserSettingsRead(
            id=settings["id"],
            user_id=settings["user_id"],
            theme=settings["theme"],
            reminder_interval_mins=settings["reminder_interval_mins"],
            reminders_enabled=bool(settings["reminders_enabled"]),
            preferred_ai_provider=settings["preferred_ai_provider"],
            offline_mode=bool(settings["offline_mode"]),
            github_username=settings["github_username"],
            created_at=settings["created_at"],
            updated_at=settings["updated_at"]
        )

    return ApiResponse(
        success=True,
        data=UserAuthStatus(
            authenticated=True,
            user_id=user["id"] if user else DEFAULT_USER_ID,
            email=user["email"] if user else "developer@local.host",
            full_name=user["full_name"] if user else "Engineering Leader",
            onboarding_completed=bool(user["onboarding_completed"]) if user else False,
            profile=profile_data,
            settings=settings_data
        )
    )


@router.post("/login")
def login(payload: LoginRequest, request: Request, response: Response) -> ApiResponse[dict]:
    if not settings.APP_ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="App password authentication is not configured")
    client_address = _client_address(request)
    retry_after = _login_retry_after(client_address, time.monotonic())
    if retry_after:
        raise HTTPException(
            status_code=429,
            detail="Too many failed sign-in attempts; try again later",
            headers={"Retry-After": str(retry_after)},
        )
    if not hmac.compare_digest(
        payload.password.encode("utf-8"),
        settings.APP_ADMIN_PASSWORD.encode("utf-8"),
    ):
        now = time.monotonic()
        with _LOGIN_FAILURES_LOCK:
            if len(_LOGIN_FAILURES) >= 1024:
                expired = [
                    address for address, (first_attempt, _) in _LOGIN_FAILURES.items()
                    if now - first_attempt >= LOGIN_WINDOW_SECONDS
                ]
                for address in expired:
                    _LOGIN_FAILURES.pop(address, None)
                if len(_LOGIN_FAILURES) >= 1024:
                    oldest = min(_LOGIN_FAILURES, key=lambda address: _LOGIN_FAILURES[address][0])
                    _LOGIN_FAILURES.pop(oldest, None)
            first_attempt, failures = _LOGIN_FAILURES.get(client_address, (now, 0))
            if now - first_attempt >= LOGIN_WINDOW_SECONDS:
                first_attempt, failures = now, 0
            _LOGIN_FAILURES[client_address] = (first_attempt, failures + 1)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    with _LOGIN_FAILURES_LOCK:
        _LOGIN_FAILURES.pop(client_address, None)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        path="/",
    )
    return ApiResponse(success=True, data={"authenticated": True})


@router.post("/logout")
def logout(response: Response) -> ApiResponse[dict]:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        path="/",
    )
    return ApiResponse(success=True, data={"authenticated": False})
