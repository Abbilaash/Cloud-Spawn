from datetime import datetime, timezone
from typing import Dict, Any

class DocumentStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

def create_document_model(
    document_id: str,
    filename: str,
    file_size: int,
    file_path: str,
    status: str = DocumentStatus.UPLOADED
) -> Dict[str, Any]:
    return {
        "document_id": document_id,
        "filename": filename,
        "file_size": file_size,
        "file_path": file_path,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": status
    }
