from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SystemResourceInfo(BaseModel):
    cpu_cores: int
    total_ram_gb: float
    available_ram_gb: float
    free_disk_gb: float
    os_name: str
    python_version: str

class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    database: str
    ai_provider: str
    resources: SystemResourceInfo

class UserSettingsRead(BaseModel):
    id: str
    user_id: str
    theme: str
    reminder_interval_mins: int
    reminders_enabled: bool
    preferred_ai_provider: str
    offline_mode: bool
    github_username: Optional[str] = None
    created_at: str
    updated_at: str

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = Field(None, pattern="^(dark|light|system)$")
    reminder_interval_mins: Optional[int] = Field(None, ge=1, le=1440)
    reminders_enabled: Optional[bool] = None
    preferred_ai_provider: Optional[str] = Field(None, pattern="^(gemini|groq|local)$")
    offline_mode: Optional[bool] = None
    github_username: Optional[str] = None

class UserProfileRead(BaseModel):
    id: str
    user_id: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    career_direction: Optional[str] = None
    target_audience: Optional[str] = None
    writing_voice_notes: Optional[str] = None
    seniority_level: Optional[str] = None
    created_at: str
    updated_at: str

class UserProfileUpdate(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    career_direction: Optional[str] = None
    target_audience: Optional[str] = None
    writing_voice_notes: Optional[str] = None
    seniority_level: Optional[str] = None

class UserAuthStatus(BaseModel):
    authenticated: bool
    user_id: str
    email: str
    full_name: str
    profile: Optional[UserProfileRead] = None
    settings: Optional[UserSettingsRead] = None
