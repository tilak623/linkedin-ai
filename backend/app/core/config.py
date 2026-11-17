import os
import json
from typing import List
from pydantic import BaseModel, Field

def parse_cors_origins(raw: str) -> List[str]:
    if not raw:
        return ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

class Settings(BaseModel):
    # App Information
    PROJECT_NAME: str = "Personal Branding AI Agent"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_PREFIX: str = "/api/v1"
    
    # Host and Port
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Origins
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: parse_cors_origins(os.getenv("CORS_ORIGINS", "")))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./brand_agent.db")
    DB_PATH: str = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "brand_agent.db"))
    
    # Supabase (Optional cloud sync)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Free AI Providers
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # LinkedIn
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/v1/linkedin/callback")
    LINKEDIN_FRONTEND_URL: str = os.getenv("LINKEDIN_FRONTEND_URL", "http://localhost:5173")
    LINKEDIN_API_VERSION: str = os.getenv("LINKEDIN_API_VERSION", "202611")
    LINKEDIN_TOKEN_ENCRYPTION_KEY: str = os.getenv("LINKEDIN_TOKEN_ENCRYPTION_KEY", "")
    DAILY_POST_TIME: str = os.getenv("DAILY_POST_TIME", "09:00")
    DAILY_POST_TIMEZONE: str = os.getenv("DAILY_POST_TIMEZONE", "Asia/Kolkata")
    ENABLE_BACKGROUND_SCHEDULER: bool = os.getenv("ENABLE_BACKGROUND_SCHEDULER", "true").lower() == "true"

    # Single-owner deployment security. Both values are required in production.
    APP_ADMIN_PASSWORD: str = os.getenv("APP_ADMIN_PASSWORD", "")
    APP_SESSION_SECRET: str = os.getenv("APP_SESSION_SECRET", "")

settings = Settings()
