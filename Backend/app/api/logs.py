import logging
from typing import List, Optional
from fastapi import APIRouter, Query, status
from pydantic import BaseModel
from app.core.logger_handler import get_system_logs, clear_system_logs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/logs", tags=["System Logs"])

class LogItem(BaseModel):
    id: str
    timestamp: str
    level: str
    logger: str
    message: str

class LogResponse(BaseModel):
    total: int
    logs: List[LogItem]

@router.get("", response_model=LogResponse)
async def fetch_logs(
    limit: int = Query(default=200, ge=1, le=500),
    level: Optional[str] = Query(default=None)
):
    """Retrieve system log stream recorded by the backend and Formicx background services."""
    logs = get_system_logs(limit=limit, level=level)
    return LogResponse(
        total=len(logs),
        logs=logs
    )

@router.delete("", status_code=status.HTTP_200_OK)
async def clear_logs():
    """Clear all recorded system logs."""
    clear_system_logs()
    logger.info("Cleared system logs buffer.")
    return {"status": "ok", "message": "System logs buffer cleared."}
