from pydantic import BaseModel, Field
from typing import List, Optional, Any

class BuildJobRequest(BaseModel):
    document_ids: List[str] = Field(..., description="List of document IDs to process into knowledge base")

class BuildJobResponse(BaseModel):
    job_id: str
    status: str

class ClusterItem(BaseModel):
    cluster_id: int
    size: int
    documents: List[str]

class DocumentTelemetry(BaseModel):
    document_id: str
    filename: str
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    status: str
    processing_step: Optional[str] = None
    cluster_id: Optional[int] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total_documents: int
    processed_documents: int
    failed_documents: int
    progress: int
    cluster_count: Optional[int] = None
    clusters: Optional[List[ClusterItem]] = None
    documents: Optional[List[DocumentTelemetry]] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

