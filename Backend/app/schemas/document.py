from pydantic import BaseModel
from typing import List, Optional

class DocumentItem(BaseModel):
    document_id: str
    filename: str
    status: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    processing_step: Optional[str] = None
    cluster_id: Optional[int] = None
    uploaded_at: Optional[str] = None

class UploadResponse(BaseModel):
    documents: List[DocumentItem]

class DocumentDetailResponse(BaseModel):
    document_id: str
    filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    processing_step: Optional[str] = None
    cluster_id: Optional[int] = None
    cluster_documents: Optional[List[str]] = None
    cluster_size: Optional[int] = None
    uploaded_at: Optional[str] = None
    job_id: Optional[str] = None

