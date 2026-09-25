import os
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    """Vector Service performing RAG search over consolidated master FAISS vector indices."""

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        faiss_dir = os.path.abspath(settings.FAISS_OUTPUT_DIRECTORY)
        master_idx = os.path.join(faiss_dir, "master_index.faiss")
        master_meta = os.path.join(faiss_dir, "master_metadata.json")

        if not os.path.exists(master_idx) and os.path.exists(faiss_dir):
            candidates = [f for f in os.listdir(faiss_dir) if f.endswith(".faiss")]
            if candidates:
                master_idx = os.path.join(faiss_dir, candidates[0])
                meta_candidate = master_idx.replace(".faiss", "_metadata.json").replace("_index.faiss", "_metadata.json")
                if os.path.exists(meta_candidate):
                    master_meta = meta_candidate

        if not os.path.exists(master_idx):
            logger.warning(f"[Vector Service] No FAISS vector index found at '{master_idx}'. Returning empty search results.")
            return []

        try:
            from app.rag_inference import FAISSVectorSearcher
            searcher = FAISSVectorSearcher(db_location=master_idx, metadata_location=master_meta)
            results = searcher.search(query_vector=query_embedding, top_k=top_k)

            formatted_results = []
            for r in results:
                meta = r.get("metadata", {})
                formatted_results.append({
                    "chunk_id": meta.get("chunk_id", f"vec_{r.get('vector_id')}"),
                    "document_id": meta.get("document_id", r.get("document_id", "")),
                    "filename": meta.get("filename", r.get("filename", "unknown")),
                    "chunk_index": meta.get("chunk_index", 0),
                    "text": r.get("text") or meta.get("text", ""),
                    "score": r.get("score", 0.0)
                })

            logger.info(f"[Vector Service] FAISS vector search completed. Retrieved {len(formatted_results)} matching chunk(s).")
            return formatted_results

        except Exception as err:
            logger.error(f"[Vector Service] Error executing FAISS search: {str(err)}", exc_info=True)
            return []

    def delete_document(self, document_id: str):
        logger.info(f"[Vector Service] Delete document request received for document_id: {document_id}")

    def clear(self):
        faiss_dir = os.path.abspath(settings.FAISS_OUTPUT_DIRECTORY)
        if os.path.exists(faiss_dir):
            for f in os.listdir(faiss_dir):
                fp = os.path.join(faiss_dir, f)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                except Exception as e:
                    logger.warning(f"Could not remove FAISS index file '{fp}': {e}")

vector_service = VectorService()

