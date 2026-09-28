import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

_model: Optional[Any] = None

def _get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("[EmbeddingService] Loading 'sentence-transformers/all-MiniLM-L6-v2' model for query vectorization...")
            _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("[EmbeddingService] Model loaded successfully.")
        except Exception as e:
            logger.error(f"[EmbeddingService] Failed to load SentenceTransformer: {e}")
            _model = False
    return _model if _model is not False else None


class EmbeddingService:
    """Vector embedding service using sentence-transformers/all-MiniLM-L6-v2 (384d)."""

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """Converts string query into a 384-dimensional normalized float embedding."""
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")

        model = _get_model()
        if model is not None:
            embedding = model.encode(text.strip(), normalize_embeddings=True, convert_to_numpy=True)
            return embedding.astype(float).tolist()

        logger.warning("[EmbeddingService] Fallback to zero vector embedding.")
        return [0.0] * 384

    @classmethod
    def embed_documents(cls, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Vectorizes a list of document text chunks into 384d embeddings."""
        if not chunks:
            return []

        texts = [c.get("text", "") for c in chunks if isinstance(c, dict) and c.get("text")]
        if not texts:
            return [[0.0] * 384 for _ in chunks]

        model = _get_model()
        if model is not None:
            embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
            return embeddings.astype(float).tolist()

        return [[0.0] * 384 for _ in chunks]

embedding_service = EmbeddingService
