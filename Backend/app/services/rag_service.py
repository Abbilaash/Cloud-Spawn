import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

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
        self._llm_client: Any = None

    def _get_api_key(self) -> Optional[str]:
        api_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY
        if not api_key or api_key in ["your_llm_api_key_here", "your_gemini_api_key_here"]:
            logger.warning("Neither GEMINI_API_KEY nor LLM_API_KEY is configured.")
            return None
        return api_key

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

        # 5. Call LLM (Gemini)
        api_key = self._get_api_key()
        if not api_key:
            if sources:
                answer = f"Retrieved {len(sources)} relevant context sources from indexed documents. (Note: GEMINI_API_KEY / LLM_API_KEY is not configured in .env. Top context snippet: {context_blocks[0][:250]}...)"
            else:
                answer = "I cannot find the answer to your question in the provided documents."
        else:
            try:
                user_prompt = f"Context:\n{context_str}\n\nQuestion:\n{user_message}"
                model_name = settings.LLM_MODEL or "gemini-3.6-flash"

                if HAS_GENAI:
                    client = genai.Client(api_key=api_key)
                    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    answer = response.text.strip()
                else:
                    client = OpenAI(
                        api_key=api_key,
                        base_url=settings.LLM_BASE_URL if settings.LLM_BASE_URL else "https://generativelanguage.googleapis.com/v1beta/openai/"
                    )
                    response = client.chat.completions.create(
                        model=model_name,
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
