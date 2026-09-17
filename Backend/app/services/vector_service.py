import os
import logging
from typing import List, Dict, Any
import chromadb
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        persist_dir = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(persist_dir, exist_ok=True)
        logger.info(f"Initializing ChromaDB PersistentClient at {persist_dir}")
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="cloudspawn_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not chunks:
            return
        
        ids = [chunk["chunk_id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"]
            }
            for chunk in chunks
        ]

        logger.info(f"Upserting {len(ids)} chunks to ChromaDB collection...")
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info(f"Performing similarity search in ChromaDB with top_k={top_k}")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        matched_items = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

            for i in range(len(ids)):
                matched_items.append({
                    "chunk_id": ids[i],
                    "text": docs[i],
                    "document_id": metas[i]["document_id"],
                    "filename": metas[i]["filename"],
                    "chunk_index": metas[i]["chunk_index"],
                    "score": float(distances[i])
                })

        return matched_items

    def delete_document(self, document_id: str):
        logger.info(f"Deleting vector chunks for document_id: {document_id}")
        self.collection.delete(where={"document_id": document_id})

vector_service = VectorService()
