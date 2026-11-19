from typing import Generic, TypeVar, Optional, Any, List, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime, timezone
from urllib.parse import urlsplit

T = TypeVar("T")
SkillTier = Literal["implemented", "studied", "explored", "discovered"]
ProjectMaturity = Literal["completed", "in_development", "experiment", "learning_exercise", "planned"]
InterviewMode = Literal["text", "voice"]

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

class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency_level: SkillTier
    category: Optional[str] = Field(None, max_length=100)
    verified_by_project: bool = False
    evidence_notes: Optional[str] = Field(None, max_length=4000)

class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    proficiency_level: Optional[SkillTier] = None
    category: Optional[str] = Field(None, max_length=100)
    verified_by_project: Optional[bool] = None
    evidence_notes: Optional[str] = Field(None, max_length=4000)

class SkillRead(SkillCreate):
    id: str
    user_id: str
    created_at: str
    updated_at: str

class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=8000)
    maturity: ProjectMaturity = "planned"
    github_url: Optional[str] = Field(None, max_length=2000)
    repo_name: Optional[str] = Field(None, max_length=200)
    tech_stack: List[str] = Field(default_factory=list, max_length=100)
    key_achievements: List[str] = Field(default_factory=list, max_length=100)
    screenshots: List[str] = Field(default_factory=list, max_length=100)

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        parsed = urlsplit(value.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("GitHub URL must use http or https")
        return value.strip()

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=8000)
    maturity: Optional[ProjectMaturity] = None
    github_url: Optional[str] = Field(None, max_length=2000)
    repo_name: Optional[str] = Field(None, max_length=200)
    tech_stack: Optional[List[str]] = Field(None, max_length=100)
    key_achievements: Optional[List[str]] = Field(None, max_length=100)
    screenshots: Optional[List[str]] = Field(None, max_length=100)

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        parsed = urlsplit(value.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("GitHub URL must use http or https")
        return value.strip()

class ProjectRead(ProjectCreate):
    id: str
    user_id: str
    created_at: str
    updated_at: str

class MilestoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=8000)
    category: Optional[str] = Field(None, max_length=100)
    milestone_date: date
    lessons_learned: Optional[str] = Field(None, max_length=4000)

class MilestoneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=8000)
    category: Optional[str] = Field(None, max_length=100)
    milestone_date: Optional[date] = None
    lessons_learned: Optional[str] = Field(None, max_length=4000)

class MilestoneRead(MilestoneCreate):
    id: str
    user_id: str
    created_at: str

class ProfileOnboardingRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    headline: Optional[str] = Field(None, max_length=300)
    summary: Optional[str] = Field(None, max_length=8000)
    career_direction: Optional[str] = Field(None, max_length=2000)
    target_audience: Optional[str] = Field(None, max_length=2000)
    writing_voice_notes: Optional[str] = Field(None, max_length=4000)
    seniority_level: Optional[str] = Field(None, max_length=100)
    initial_skills: List[SkillCreate] = Field(default_factory=list, max_length=100)

class KnowledgeSearchResult(BaseModel):
    entity_type: str
    entity_id: str
    title: str
    snippet: str

class InterviewStartRequest(BaseModel):
    mode: InterviewMode = "text"

class InterviewTurnRequest(BaseModel):
    user_response: str = Field(min_length=1, max_length=8000)

class InterviewMessageRead(BaseModel):
    id: str
    sender: Literal["user", "ai"]
    content: str
    created_at: str

class InterviewSessionRead(BaseModel):
    id: str
    interview_date: str
    mode: InterviewMode
    completed: bool
    summary: Optional[str] = None
    messages: List[InterviewMessageRead]

class InterviewTurnResult(BaseModel):
    session: InterviewSessionRead
    content_opportunity: Literal[
        "technical_educational_post",
        "learning_experience",
        "project_update",
        "technical_opinion",
        "none",
    ]

class UserAuthStatus(BaseModel):
    authenticated: bool
    user_id: str
    email: str
    full_name: str
    onboarding_completed: bool = False
    profile: Optional[UserProfileRead] = None
    settings: Optional[UserSettingsRead] = None

class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1024)

class ContentPostRead(BaseModel):
    id: str
    title: str
    topic: Optional[str] = None
    content_category: str
    final_content: str
    hashtags: List[str]
    status: str
    scheduled_for: Optional[str] = None
    published_at: Optional[str] = None
    linkedin_post_id: Optional[str] = None
    created_at: str
    approved_at: Optional[str] = None

class ContentPostUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    final_content: str = Field(min_length=1, max_length=3000)

class HumanizedDraftRequest(BaseModel):
    source_text: str = Field(min_length=1, max_length=8000)

class ContentMediaRead(BaseModel):
    id: str
    filename: str
    content_type: str
    preview_url: str
    created_at: str

class ContentApprovalRequest(BaseModel):
    confirm: bool

class LinkedInStatus(BaseModel):
    configured: bool
    connected: bool
    member_name: Optional[str] = None
    expires_at: Optional[str] = None
    expected_profile_url: str

class ContentScheduleRead(BaseModel):
    daily_post_time: str
    timezone: str
