import os
import json
import pickle
import logging
from typing import List, Dict, Any, Union, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Attempt to import faiss; handle missing library gracefully
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS package is not installed. Install with `pip install faiss-cpu` or `pip install faiss-gpu`.")


class FAISSVectorSearcher:
    """Generalized FAISS Vector Database Search Engine.
    
    Performs similarity search on a FAISS vector index given a query vector
    and database location. Supports automatic index caching, metadata loading,
    and vector normalization.
    """

    def __init__(
        self,
        db_location: Optional[str] = None,
        metadata_location: Optional[str] = None,
        normalize_vectors: bool = True
    ):
        """Initialize the FAISS Vector Searcher.
        
        Args:
            db_location: Path to the FAISS index file (.index, .faiss, .bin) or directory.
            metadata_location: Optional path to JSON or PKL file storing document metadata.
            normalize_vectors: If True, L2-normalizes query vectors for cosine similarity.
        """
        self.db_location: Optional[str] = db_location
        self.metadata_location: Optional[str] = metadata_location
        self.normalize_vectors: bool = normalize_vectors
        self.index: Any = None
        self.metadata: Optional[List[Dict[str, Any]]] = None

        if db_location:
            self.load_index(db_location)
        if metadata_location:
            self.load_metadata(metadata_location)

    def load_index(self, db_location: str):
        """Load a FAISS index from disk.
        
        Args:
            db_location: Path to FAISS index file or directory containing an index.
        """
        resolved_path = self._resolve_index_path(db_location)
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"FAISS index file not found at location: '{resolved_path}'")

        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS library is required to read FAISS index files. "
                "Please run `pip install faiss-cpu`."
            )

        logger.info(f"Loading FAISS vector index from '{resolved_path}'...")
        try:
            self.index = faiss.read_index(resolved_path)
            self.db_location = resolved_path
            logger.info(f"Successfully loaded FAISS index. Total vectors: {self.index.ntotal}, Dimension: {self.index.d}")
        except Exception as e:
            logger.error(f"Failed to load FAISS index from '{resolved_path}': {str(e)}", exc_info=True)
            raise RuntimeError(f"Error reading FAISS index from '{resolved_path}': {str(e)}") from e

    def load_metadata(self, metadata_location: str):
        """Load metadata file associated with the FAISS index.
        
        Args:
            metadata_location: Path to .json or .pkl file mapping index positions to metadata dicts.
        """
        if not os.path.exists(metadata_location):
            logger.warning(f"Metadata file not found at '{metadata_location}'")
            return

        try:
            if metadata_location.endswith(".json"):
                with open(metadata_location, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, dict) and "chunks" in loaded_data:
                        self.metadata = loaded_data["chunks"]
                    elif isinstance(loaded_data, dict) and "items" in loaded_data:
                        self.metadata = loaded_data["items"]
                    else:
                        self.metadata = loaded_data
            elif metadata_location.endswith((".pkl", ".pickle")):
                with open(metadata_location, "rb") as f:
                    self.metadata = pickle.load(f)
            self.metadata_location = metadata_location
            logger.info(f"Successfully loaded metadata entries: {len(self.metadata) if self.metadata else 0}")
        except Exception as e:
            logger.error(f"Failed to load metadata file '{metadata_location}': {str(e)}")

    def _resolve_index_path(self, path: str) -> str:
        """Helper to resolve index file path if a directory path was provided."""
        if os.path.isdir(path):
            for candidate in ["index.faiss", "vector.index", "faiss.index", "index.bin"]:
                full_path = os.path.join(path, candidate)
                if os.path.exists(full_path):
                    return full_path
            # Fallback: look for any .index or .faiss file in directory
            for f in os.listdir(path):
                if f.endswith((".index", ".faiss", ".bin")):
                    return os.path.join(path, f)
        return path

    def search(
        self,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 5,
        db_location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search the FAISS vector database for nearest matches to the user query vector.
        
        Args:
            query_vector: 1D or 2D list/array of floats representing the query embedding.
            top_k: Number of top nearest neighbors to retrieve (default: 5).
            db_location: Optional database location to search (overrides initialized index).
            
        Returns:
            List of result dicts containing vector_id, distance/score, rank, and optional metadata.
        """
        target_location = db_location or self.db_location
        if not target_location and self.index is None:
            raise ValueError("Database location must be specified either at initialization or in search call.")

        # Reload index if a new db_location is passed
        if db_location and db_location != self.db_location:
            self.load_index(db_location)

        if self.index is None:
            raise RuntimeError(f"No active FAISS index loaded for location: '{target_location}'")

        # 1. Format and preprocess query vector
        query_arr = self._format_query_vector(query_vector)

        # Validate vector dimension matches FAISS index dimension
        if query_arr.shape[1] != self.index.d:
            raise ValueError(
                f"Dimension mismatch: Query vector dimension is {query_arr.shape[1]}, "
                f"but FAISS index expects dimension {self.index.d}."
            )

        # 2. Perform FAISS nearest neighbor search
        top_k = min(top_k, max(1, self.index.ntotal))
        logger.info(f"Executing FAISS vector search with top_k={top_k}...")
        distances, indices = self.index.search(query_arr, top_k)

        # 3. Format structured search results
        results: List[Dict[str, Any]] = []
        raw_distances = distances[0]
        raw_indices = indices[0]

        for rank, (dist, idx) in enumerate(zip(raw_distances, raw_indices), start=1):
            if idx == -1:
                # FAISS returns -1 when fewer vectors than top_k exist in the index
                continue

            vector_id = int(idx)
            distance_val = float(dist)

            result_entry: Dict[str, Any] = {
                "rank": rank,
                "vector_id": vector_id,
                "score": distance_val,
                "distance": distance_val
            }

            # Attach document metadata if available
            meta_item = None
            if self.metadata:
                if isinstance(self.metadata, list) and 0 <= vector_id < len(self.metadata):
                    meta_item = self.metadata[vector_id]
                elif isinstance(self.metadata, dict):
                    meta_item = self.metadata.get(vector_id) or self.metadata.get(str(vector_id))

            if meta_item:
                if isinstance(meta_item, dict):
                    result_entry["metadata"] = meta_item
                    result_entry["text"] = meta_item.get("text", "")
                    result_entry["document_id"] = meta_item.get("document_id", "")
                    result_entry["filename"] = meta_item.get("filename", "")
                else:
                    result_entry["metadata"] = meta_item

            results.append(result_entry)

        logger.info(f"FAISS vector search completed. Retrieved {len(results)} match(es).")
        return results

    def _format_query_vector(self, query_vector: Union[List[float], np.ndarray]) -> np.ndarray:
        """Converts query vector into a 2D float32 numpy array with optional L2 normalization."""
        if isinstance(query_vector, list):
            arr = np.array(query_vector, dtype=np.float32)
        elif isinstance(query_vector, np.ndarray):
            arr = query_vector.astype(np.float32)
        else:
            raise TypeError(f"Unsupported query_vector type: {type(query_vector)}. Expected List[float] or np.ndarray.")

        # Ensure 2D shape (1, D)
        if arr.ndim == 1:
            arr = np.expand_dims(arr, axis=0)
        elif arr.ndim > 2:
            arr = arr.reshape(1, -1)

        # Optional L2 normalization for cosine similarity compatibility
        if self.normalize_vectors:
            faiss.normalize_L2(arr) if FAISS_AVAILABLE else None

        return arr

    @classmethod
    def search_vector_db(
        cls,
        db_location: str,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 5,
        metadata_location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Convenience class method to perform a search directly on a database location.
        
        Args:
            db_location: Path to the FAISS index file.
            query_vector: User query embedding vector.
            top_k: Number of nearest neighbors to retrieve.
            metadata_location: Optional path to metadata file.
        """
        searcher = cls(db_location=db_location, metadata_location=metadata_location)
        return searcher.search(query_vector=query_vector, top_k=top_k)


# Alias for flexible class naming conventions
FAISSSearchEngine = FAISSVectorSearcher
