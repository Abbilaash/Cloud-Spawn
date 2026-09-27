from pydantic import BaseModel, Field
from typing import List, Optional

class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="User query or text string input to search RAG vector DB")
    top_k: Optional[int] = Field(default=5, ge=1, le=50, description="Number of top nearest matching text chunks to return")

class RAGSearchResultItem(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Document ID")
    filename: str = Field(..., description="Original filename of source document")
    chunk_index: int = Field(..., description="0-indexed position of chunk in source file")
    text: str = Field(..., description="Extracted text context snippet")
    score: float = Field(..., description="Similarity score matching query embedding")

class RAGSearchResponse(BaseModel):
    query: str = Field(..., description="Input query string")
    top_k: int = Field(..., description="Requested top_k matches limit")
    total_matches: int = Field(..., description="Total matches found in master FAISS DB")
    results: List[RAGSearchResultItem] = Field(..., description="List of top matching text chunk snippets and metadata")
