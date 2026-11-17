import os
import sys
import shutil
import ctypes
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.db import db
from backend.app.models.schemas import ApiResponse, HealthResponse, SystemResourceInfo

router = APIRouter(tags=["System & Health"])

def get_system_resources() -> SystemResourceInfo:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    ms = MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    try:
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        total_ram = round(ms.ullTotalPhys / (1024**3), 2)
        avail_ram = round(ms.ullAvailPhys / (1024**3), 2)
    except Exception:
        total_ram = 16.0
        avail_ram = 4.0

    try:
        total_d, used_d, free_d = shutil.disk_usage(".")
        free_disk = round(free_d / (1024**3), 2)
    except Exception:
        free_disk = 100.0

    return SystemResourceInfo(
        cpu_cores=os.cpu_count() or 4,
        total_ram_gb=total_ram,
        available_ram_gb=avail_ram,
        free_disk_gb=free_disk,
        os_name="Windows",
        python_version=sys.version.split()[0]
    )

@router.get("/health", response_model=ApiResponse[HealthResponse])
def health_check():
    # Verify DB connectivity
    db_status = "connected"
    try:
        row = db.fetch_one("SELECT 1 as ping")
        if not row or row.get("ping") != 1:
            db_status = "degraded"
    except Exception:
        db_status = "disconnected"

    resources = get_system_resources()
    ai_provider = "gemini" if settings.GEMINI_API_KEY else ("groq" if settings.GROQ_API_KEY else "local_fallback")

    health_data = HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        database=f"{db.driver_name} ({db_status})",
        ai_provider=ai_provider,
        resources=resources
    )

    return ApiResponse(
        success=True,
        data=health_data
    )
