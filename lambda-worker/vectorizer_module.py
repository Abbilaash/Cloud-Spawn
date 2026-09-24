import logging
from typing import List, Union, Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    logger.warning("sentence_transformers package is not installed.")


class TextVectorizer:
    """Standalone Text Vectorizer for AWS Lambda Container.
    
    Converts string text chunks into 384-dimensional dense vector embeddings
    using 'sentence-transformers/all-MiniLM-L6-v2'.
    """

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = "cpu",
        normalize_embeddings: bool = True
    ):
        self.model_name: str = model_name
        self.device: Optional[str] = device
        self.normalize_embeddings: bool = normalize_embeddings
        self._model: Optional[Any] = None

    def _load_model(self):
        if self._model is not None:
            return

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence_transformers package is required for vectorization. "
                "Please install `sentence-transformers`."
            )

        logger.info(f"[Lambda Vectorizer] Loading model '{self.model_name}' on device '{self.device}'...")
        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"[Lambda Vectorizer] Model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"[Lambda Vectorizer] Failed to load model '{self.model_name}': {str(e)}", exc_info=True)
            raise RuntimeError(f"Error loading model '{self.model_name}': {str(e)}") from e

    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Fallback vector encoder producing normalized 384-d pseudo-vectors if sentence-transformers is missing."""
        logger.warning(f"[Lambda Vectorizer] sentence_transformers unavailable. Generating {len(texts)} fallback 384-d vectors.")
        vectors = []
        for text in texts:
            # Deterministic pseudo vector based on text hash
            seed = sum(ord(c) for c in text) % (2**32)
            rng = np.random.RandomState(seed)
            vec = rng.randn(384).astype(np.float32)
            if self.normalize_embeddings:
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            vectors.append(vec)
        return np.vstack(vectors)

    def encode_text(self, text: str) -> List[float]:
        """Convert single text string to 1D vector list of floats (384-d)."""
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return self._fallback_encode([text.strip()])[0].tolist()
        self._load_model()
        embedding = self._model.encode(
            text.strip(),
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True
        )
        return embedding.astype(float).tolist()

    def encode_batch_numpy(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Convert list of text strings into 2D float32 numpy array (Shape: N x 384)."""
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        cleaned_texts = [t.strip() for t in texts if t and t.strip()]
        if not cleaned_texts:
            raise ValueError("No valid texts in batch for encoding.")

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return self._fallback_encode(cleaned_texts)

        self._load_model()
        embeddings = self._model.encode(
            cleaned_texts,
            batch_size=batch_size,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.astype(np.float32)
