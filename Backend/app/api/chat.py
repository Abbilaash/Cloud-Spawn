import logging
from fastapi import APIRouter, HTTPException, status
from app.core.database import db_manager
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    MessageItem
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest):
    """Execute RAG question-answering query over indexed knowledge base documents."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat message cannot be empty."
        )

    try:
        result = rag_service.process_chat(
            user_message=request.message.strip(),
            conversation_id=request.conversation_id
        )
        return ChatResponse(
            conversation_id=result["conversation_id"],
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Error executing chat interaction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process RAG chat query."
        )


@router.get("/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str):
    """Retrieve complete message history for a given conversation ID."""
    conv_col = db_manager.get_conversations_collection()
    conv = conv_col.find_one({"conversation_id": conversation_id})

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with ID '{conversation_id}' not found."
        )

    messages = [
        MessageItem(
            role=msg["role"],
            content=msg["content"],
            timestamp=msg["timestamp"]
        )
        for msg in conv.get("messages", [])
    ]

    return ConversationHistoryResponse(
        conversation_id=conv["conversation_id"],
        messages=messages,
        created_at=conv.get("created_at", ""),
        updated_at=conv.get("updated_at", "")
    )
