from pydantic import BaseModel, Field
from typing import List, Optional

class BuildJobRequest(BaseModel):
    document_ids: List[str] = Field(..., description="List of document IDs to process into knowledge base")

class BuildJobResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total_documents: int
    processed_documents: int
    failed_documents: int
    progress: int
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
