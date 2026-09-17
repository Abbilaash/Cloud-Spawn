from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context history")

class SourceItem(BaseModel):
    document_id: str
    filename: str
    chunk_index: int

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[SourceItem]

class MessageItem(BaseModel):
    role: str
    content: str
    timestamp: str

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[MessageItem]
    created_at: str
    updated_at: str
