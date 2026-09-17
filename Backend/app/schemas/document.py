from pydantic import BaseModel
from typing import List, Optional

class DocumentItem(BaseModel):
    document_id: str
    filename: str
    status: str
    file_size: Optional[int] = None
    uploaded_at: Optional[str] = None

class UploadResponse(BaseModel):
    documents: List[DocumentItem]
