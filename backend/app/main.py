from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging, logger
from backend.app.core.db import db
from backend.app.core.errors import AppError, app_error_handler, global_exception_handler
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.settings import router as settings_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.memory import router as memory_router
from backend.app.api.v1.profile import router as profile_router
from backend.app.api.v1.interviews import router as interviews_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Personal Branding AI Agent Backend...")
    db.init_db()
    logger.info("Database schema validated and seeded successfully.")
    yield
    logger.info("Personal Branding AI Agent Backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent, authentic, zero-cost personal branding assistant backend.",
    lifespan=lifespan
)

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

@app.get("/")
def root_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
