from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from backend.app.core.db import db, DEFAULT_USER_ID
from backend.app.models.schemas import ApiResponse, UserSettingsRead, UserSettingsUpdate
from backend.app.core.logging_config import logger

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=ApiResponse[UserSettingsRead])
def get_settings():
    row = db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (DEFAULT_USER_ID,))
    if not row:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    settings_data = UserSettingsRead(
        id=row["id"],
        user_id=row["user_id"],
        theme=row["theme"],
        reminder_interval_mins=row["reminder_interval_mins"],
        reminders_enabled=bool(row["reminders_enabled"]),
        preferred_ai_provider=row["preferred_ai_provider"],
        offline_mode=bool(row["offline_mode"]),
        github_username=row["github_username"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )
    return ApiResponse(success=True, data=settings_data)

@router.patch("", response_model=ApiResponse[UserSettingsRead])
def update_settings(update: UserSettingsUpdate):
    row = db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (DEFAULT_USER_ID,))
    if not row:
        raise HTTPException(status_code=404, detail="Settings not found")

    theme = update.theme if update.theme is not None else row["theme"]
    reminder_interval = update.reminder_interval_mins if update.reminder_interval_mins is not None else row["reminder_interval_mins"]
    reminders_enabled = int(update.reminders_enabled) if update.reminders_enabled is not None else row["reminders_enabled"]
    ai_provider = update.preferred_ai_provider if update.preferred_ai_provider is not None else row["preferred_ai_provider"]
    offline_mode = int(update.offline_mode) if update.offline_mode is not None else row["offline_mode"]
    github_username = update.github_username if update.github_username is not None else row["github_username"]
    now = datetime.now(timezone.utc).isoformat()

    db.execute(
        """UPDATE user_settings 
           SET theme = ?, reminder_interval_mins = ?, reminders_enabled = ?, 
               preferred_ai_provider = ?, offline_mode = ?, github_username = ?, updated_at = ?
           WHERE user_id = ?""",
        (theme, reminder_interval, reminders_enabled, ai_provider, offline_mode, github_username, now, DEFAULT_USER_ID)
    )

    updated_row = db.fetch_one("SELECT * FROM user_settings WHERE user_id = ?", (DEFAULT_USER_ID,))
    settings_data = UserSettingsRead(
        id=updated_row["id"],
        user_id=updated_row["user_id"],
        theme=updated_row["theme"],
        reminder_interval_mins=updated_row["reminder_interval_mins"],
        reminders_enabled=bool(updated_row["reminders_enabled"]),
        preferred_ai_provider=updated_row["preferred_ai_provider"],
        offline_mode=bool(updated_row["offline_mode"]),
        github_username=updated_row["github_username"],
        created_at=updated_row["created_at"],
        updated_at=updated_row["updated_at"]
    )
    logger.info(f"Updated user settings for {DEFAULT_USER_ID}")
    return ApiResponse(success=True, data=settings_data)
