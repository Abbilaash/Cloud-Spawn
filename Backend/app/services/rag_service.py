import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.database import db_manager
from app.models.chat import create_conversation_model, create_message_model
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CloudSpawn AI Assistant, a grounded document Q&A assistant.
Answer the user's question using ONLY the provided document context below.
- Avoid inventing facts or relying on outside information not mentioned in the context.
- If the answer cannot be found in the documents, clearly state: "I cannot find the answer to your question in the provided documents."
- Use the retrieved context as your primary source.
- Keep answers concise, factual, and useful."""

class RAGService:
    def __init__(self):
        self._llm_client: Optional[OpenAI] = None

    def _get_llm_client(self) -> Optional[OpenAI]:
        if not settings.LLM_API_KEY or settings.LLM_API_KEY == "your_llm_api_key_here":
            logger.warning("LLM_API_KEY is not configured.")
            return None
        if self._llm_client is None:
            self._llm_client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL if settings.LLM_BASE_URL else "https://api.openai.com/v1"
            )
        return self._llm_client

    def process_chat(self, user_message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        conv_col = db_manager.get_conversations_collection()

        # 1. Manage Conversation ID
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conv_doc = create_conversation_model(conversation_id)
            conv_col.insert_one(conv_doc)
        else:
            conv_doc = conv_col.find_one({"conversation_id": conversation_id})
            if not conv_doc:
                conv_doc = create_conversation_model(conversation_id)
                conv_col.insert_one(conv_doc)

        # 2. Append User Message to MongoDB history
        user_msg_model = create_message_model("user", user_message)
        conv_col.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": user_msg_model},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )

        # 3. Vector Similarity Search
        query_embedding = embedding_service.embed_text(user_message)
        matched_chunks = vector_service.search(query_embedding, top_k=settings.TOP_K_CHUNKS)

        # 4. Construct Context & Source Items
        sources = []
        context_blocks = []
        seen_sources = set()

        for chunk in matched_chunks:
            context_blocks.append(f"--- Source: {chunk['filename']} (Chunk {chunk['chunk_index']}) ---\n{chunk['text']}")
            source_key = (chunk["document_id"], chunk["chunk_index"])
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                sources.append({
                    "document_id": chunk["document_id"],
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"]
                })

        context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant document chunks found."

        # 5. Call LLM
        client = self._get_llm_client()
        if not client:
            if sources:
                answer = f"Retrieved {len(sources)} relevant context sources from indexed documents. (Note: LLM_API_KEY is not configured in .env. Top context snippet: {context_blocks[0][:250]}...)"
            else:
                answer = "I cannot find the answer to your question in the provided documents."
        else:
            try:
                user_prompt = f"Context:\n{context_str}\n\nQuestion:\n{user_message}"
                response = client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2
                )
                answer = response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Error calling LLM API: {str(e)}")
                answer = f"Error generating answer from LLM: {str(e)}"

        # 6. Append Assistant Message to MongoDB history
        assistant_msg_model = create_message_model("assistant", answer)
        conv_col.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": assistant_msg_model},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )

        return {
            "conversation_id": conversation_id,
            "answer": answer,
            "sources": sources
        }

rag_service = RAGService()
