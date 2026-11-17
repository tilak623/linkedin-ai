from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from backend.app.core.logging_config import logger

class AppError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = "BAD_REQUEST", details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}

class ResourceNotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} '{identifier}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )

class ValidationError(AppError):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )

class ApprovalRequiredError(AppError):
    def __init__(self, action: str):
        super().__init__(
            message=f"Action '{action}' requires explicit user approval before execution.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="APPROVAL_REQUIRED"
        )

async def app_error_handler(request: Request, exc: AppError):
    logger.warning(f"Handled AppError: {exc.error_code} - {exc.message} on {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Server Error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please consult backend logs.",
                "details": {"exception": str(exc)} if logger.level <= 10 else {}
            },
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )
