import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Lightweight embedding service abstraction for FastAPI backend.
    
    Heavy embedding and clustering model execution is offloaded to Formicx agents.
    """

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """Lightweight 384-dimensional vector representation."""
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")
        return [0.0] * 384

    @classmethod
    def embed_documents(cls, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Lightweight document vector embedding generator."""
        if not chunks:
            return []
        return [[0.0] * 384 for _ in chunks]

embedding_service = EmbeddingService
