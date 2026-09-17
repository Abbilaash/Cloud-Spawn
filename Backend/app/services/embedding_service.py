import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model: SentenceTransformer | None = None

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL_NAME}")
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return cls._model

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        """Generate vector embedding for a single string query."""
        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")
        model = cls._get_model()
        embedding = model.encode(text, convert_to_numpy=True).tolist()
        return embedding

    @classmethod
    def embed_documents(cls, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate vector embeddings for a list of document chunk objects."""
        if not chunks:
            return []
        
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Generating embeddings for {len(texts)} document chunks...")
        model = cls._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True).tolist()
        return embeddings

embedding_service = EmbeddingService
