from fastapi import APIRouter
from backend.app.core.db import db, DEFAULT_USER_ID
from backend.app.models.schemas import ApiResponse, UserAuthStatus, UserProfileRead, UserSettingsRead

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])

@router.get("/me", response_model=ApiResponse[UserAuthStatus])
def get_current_user_status():
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
            profile=profile_data,
            settings=settings_data
        )
    )
