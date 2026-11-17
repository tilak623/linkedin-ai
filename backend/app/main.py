import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging, logger
from backend.app.core.db import db
from backend.app.core.errors import AppError, app_error_handler, global_exception_handler
from backend.app.core.session_auth import SESSION_COOKIE_NAME, is_authenticated
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.settings import router as settings_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.memory import router as memory_router
from backend.app.api.v1.profile import router as profile_router
from backend.app.api.v1.interviews import router as interviews_router
from backend.app.api.v1.content import (
    recover_interrupted_posts,
    router as content_router,
    scheduler_loop,
)
from backend.app.api.v1.linkedin import router as linkedin_router

setup_logging()
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ENVIRONMENT == "production":
        missing = [
            key for key, value in (
                ("APP_ADMIN_PASSWORD", settings.APP_ADMIN_PASSWORD),
                ("APP_SESSION_SECRET", settings.APP_SESSION_SECRET),
            ) if not value
        ]
        if missing:
            raise RuntimeError(
                "Production startup requires secure values for: " + ", ".join(missing)
            )
        if len(settings.APP_ADMIN_PASSWORD) < 16:
            raise RuntimeError("APP_ADMIN_PASSWORD must be at least 16 characters in production")
        if len(settings.APP_SESSION_SECRET) < 32:
            raise RuntimeError("APP_SESSION_SECRET must be at least 32 characters in production")
    if settings.APP_ADMIN_PASSWORD and not settings.APP_SESSION_SECRET:
        raise RuntimeError("APP_SESSION_SECRET is required when app-password authentication is enabled")
    if settings.HOST not in ("127.0.0.1", "localhost") and not settings.APP_ADMIN_PASSWORD:
        raise RuntimeError("APP_ADMIN_PASSWORD is required when binding beyond localhost")
    if settings.HOST not in ("127.0.0.1", "localhost") and settings.ENVIRONMENT != "production":
        raise RuntimeError("Non-local deployments must use ENVIRONMENT=production and HTTPS")
    logger.info("Initializing Personal Branding AI Agent Backend...")
    db.init_db()
    recover_interrupted_posts()
    logger.info("Database schema validated and seeded successfully.")
    scheduler_task = (
        asyncio.create_task(scheduler_loop())
        if settings.ENABLE_BACKGROUND_SCHEDULER
        else None
    )
    try:
        yield
    finally:
        if scheduler_task:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass
    logger.info("Personal Branding AI Agent Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent, authentic, zero-cost personal branding assistant backend.",
    lifespan=lifespan
)

@app.middleware("http")
async def protect_api(request: Request, call_next):
    path = request.url.path
    public_paths = {
        f"{settings.API_V1_PREFIX}/health",
        f"{settings.API_V1_PREFIX}/auth/me",
        f"{settings.API_V1_PREFIX}/auth/login",
        f"{settings.API_V1_PREFIX}/linkedin/callback",
    }
    if (
        settings.APP_ADMIN_PASSWORD
        and path.startswith(f"{settings.API_V1_PREFIX}/")
        and path not in public_paths
        and not is_authenticated(request.cookies.get(SESSION_COOKIE_NAME))
    ):
        return JSONResponse(status_code=401, content={"detail": "Sign in to continue"})
    return await call_next(request)

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(memory_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(interviews_router, prefix=settings.API_V1_PREFIX)
app.include_router(content_router, prefix=settings.API_V1_PREFIX)
app.include_router(linkedin_router, prefix=settings.API_V1_PREFIX)

if settings.ENVIRONMENT == "production" and (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="frontend-assets",
    )


@app.get("/{frontend_path:path}", include_in_schema=False)
def frontend_route(frontend_path: str):
    if (
        settings.ENVIRONMENT == "production"
        and not frontend_path.startswith("api/")
        and (FRONTEND_DIST / "index.html").is_file()
    ):
        return FileResponse(FRONTEND_DIST / "index.html")
    from fastapi import HTTPException

    raise HTTPException(status_code=404, detail="Not found")

@app.get("/")
def root_info():
    index_file = FRONTEND_DIST / "index.html"
    if settings.ENVIRONMENT == "production" and index_file.is_file():
        return FileResponse(index_file)
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
