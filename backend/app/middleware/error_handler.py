from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import traceback
import logging

logger = logging.getLogger(__name__)

async def api_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler that standardizes all unhandled exceptions
    into the ApiError schema.
    """
    logger.error(f"Unhandled exception: {exc}")
    # In production, do not expose stack trace
    
    error_response = {
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred processing your request.",
        "details": {"exception": str(exc)},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )
