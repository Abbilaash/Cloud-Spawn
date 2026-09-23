import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Attempt to import SentenceTransformer; handle missing dependency gracefully
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    logger.warning(
        "sentence_transformers package is not installed. "
        "Install with `pip install sentence-transformers`."
    )


class TextVectorizer:
    """Generalized Text Vectorizer using Hugging Face Sentence Transformers.
    
    Defaults to 'sentence-transformers/all-MiniLM-L6-v2' to convert any string or
    batch of strings into 384-dimensional dense vector embeddings. Suitable for both
    FAISS search indexing and real-time user query vector conversion.
    """

    DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
        preload: bool = False
    ):
        """Initialize the Text Vectorizer.
        
        Args:
            model_name: Hugging Face model identifier (default: 'sentence-transformers/all-MiniLM-L6-v2').
            device: Compute device ('cpu', 'cuda', 'mps', etc.). Auto-detects if None.
            normalize_embeddings: If True, L2-normalizes vector embeddings for cosine similarity.
            preload: If True, loads the SentenceTransformer model immediately during initialization.
        """
        self.model_name: str = model_name
        self.device: Optional[str] = device
        self.normalize_embeddings: bool = normalize_embeddings
        self._model: Optional[Any] = None

        if preload:
            self._load_model()

    def _load_model(self):
        """Lazy-loads the SentenceTransformer model into memory."""
        if self._model is not None:
            return

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence_transformers library is required for text vectorization. "
                "Please run `pip install sentence-transformers`."
            )

        logger.info(f"Loading SentenceTransformer model '{self.model_name}'...")
        try:
            self._model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Successfully loaded SentenceTransformer model '{self.model_name}'.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{self.model_name}': {str(e)}", exc_info=True)
            raise RuntimeError(f"Error loading model '{self.model_name}': {str(e)}") from e

    def encode_text(self, text: str) -> List[float]:
        """Convert a single string or user query into a 1D list of float embeddings.
        
        Args:
            text: Input string or question.
            
        Returns:
            1D list of float values (length 384 for all-MiniLM-L6-v2).
        """
        if not text or not text.strip():
            raise ValueError("Input text for vectorization cannot be empty.")

        self._load_model()
        embedding = self._model.encode(
            text.strip(),
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True
        )
        return embedding.astype(float).tolist()

    def encode_text_numpy(self, text: str) -> np.ndarray:
        """Convert a single string or user query into a 1D float32 NumPy array.
        
        Args:
            text: Input string.
            
        Returns:
            1D NumPy array float32 of shape (384,).
        """
        if not text or not text.strip():
            raise ValueError("Input text for vectorization cannot be empty.")

        self._load_model()
        embedding = self._model.encode(
            text.strip(),
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True
        )
        return embedding.astype(np.float32)

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Convert a list of strings (documents/chunks) into a 2D list of float vectors.
        
        Args:
            texts: List of text strings.
            batch_size: Number of texts per encoding batch (default: 32).
            
        Returns:
            2D list of float vectors (Shape: N x 384).
        """
        if not texts:
            return []

        cleaned_texts = [t.strip() for t in texts if t and t.strip()]
        if not cleaned_texts:
            raise ValueError("None of the provided texts in the batch were valid.")

        self._load_model()
        embeddings = self._model.encode(
            cleaned_texts,
            batch_size=batch_size,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.astype(float).tolist()

    def encode_batch_numpy(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Convert a list of strings into a 2D float32 NumPy array (Shape: N x 384).
        
        Args:
            texts: List of text strings.
            batch_size: Number of texts per encoding batch.
            
        Returns:
            2D NumPy array float32 of shape (N, 384).
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        cleaned_texts = [t.strip() for t in texts if t and t.strip()]
        if not cleaned_texts:
            raise ValueError("None of the provided texts in the batch were valid.")

        self._load_model()
        embeddings = self._model.encode(
            cleaned_texts,
            batch_size=batch_size,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings.astype(np.float32)

    def convert_to_vector(
        self,
        input_data: Union[str, List[str]],
        to_numpy: bool = False,
        batch_size: int = 32
    ) -> Union[List[float], List[List[float]], np.ndarray]:
        """Generalized method to convert any string or list of strings into vector embeddings.
        
        Args:
            input_data: Single string or list of strings.
            to_numpy: If True, returns NumPy array instead of Python lists.
            batch_size: Batch size used when input_data is a list.
            
        Returns:
            - If input is str: 1D list of floats (or 1D NumPy array if to_numpy=True).
            - If input is List[str]: 2D list of float vectors (or 2D NumPy array if to_numpy=True).
        """
        if isinstance(input_data, str):
            return self.encode_text_numpy(input_data) if to_numpy else self.encode_text(input_data)
        elif isinstance(input_data, list):
            return self.encode_batch_numpy(input_data, batch_size=batch_size) if to_numpy else self.encode_batch(input_data, batch_size=batch_size)
        else:
            raise TypeError(f"Unsupported input type: {type(input_data)}. Expected str or List[str].")


# Aliases for flexible import names
VectorizationEngine = TextVectorizer
SentenceVectorizer = TextVectorizer
