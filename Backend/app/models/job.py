from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

def create_job_model(
    job_id: str,
    document_ids: List[str],
    total_documents: int,
    status: str = JobStatus.QUEUED
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "job_id": job_id,
        "document_ids": document_ids,
        "status": status,
        "total_documents": total_documents,
        "processed_documents": 0,
        "failed_documents": 0,
        "progress": 0,
        "created_at": now,
        "started_at": None,
        "completed_at": None
    }
