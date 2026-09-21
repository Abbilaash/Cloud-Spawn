import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VectorService:
    """Lightweight in-memory vector service stub.
    
    All heavy embedding and vector store operations are replaced by scikit-learn dynamic clustering
    in Formicx agents or offloaded to serverless workers.
    """
    def __init__(self):
        logger.info("Initializing lightweight VectorService stub.")
        self._store: Dict[str, Dict[str, Any]] = {}

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not chunks:
            return
        logger.info(f"Storing {len(chunks)} chunks in lightweight VectorService.")
        for chunk in chunks:
            self._store[chunk.get("chunk_id", "")] = chunk

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Performing lightweight vector search with top_k={top_k}.")
        results = list(self._store.values())[:top_k]
        return results

    def delete_document(self, document_id: str):
        logger.info(f"Deleting vector chunks for document_id: {document_id}")
        keys_to_delete = [k for k, v in self._store.items() if v.get("document_id") == document_id]
        for k in keys_to_delete:
            del self._store[k]

vector_service = VectorService()

