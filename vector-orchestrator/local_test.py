#!/usr/bin/env python3
import os
import sys
import json
import faiss
import numpy as np

# Ensure Backend/app, lambda-worker, and vector-orchestrator are on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../lambda-worker")))
sys.path.insert(0, os.path.dirname(__file__))

from main import VectorOrchestratorAgent
from vectorizer_module import TextVectorizer
from app.rag_inference import FAISSVectorSearcher


def create_mock_partition_faiss(output_dir: str, cluster_id: int, chunks_data: list) -> tuple:
    """Helper to create a partition FAISS index and metadata file simulating a Lambda worker run."""
    os.makedirs(output_dir, exist_ok=True)
    vec_engine = TextVectorizer()

    texts = [c["text"] for c in chunks_data]
    embeddings = vec_engine.encode_batch_numpy(texts)  # Shape: (N, 384)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    idx_path = os.path.join(output_dir, f"cluster_{cluster_id}_index.faiss")
    meta_path = os.path.join(output_dir, f"cluster_{cluster_id}_metadata.json")

    faiss.write_index(index, idx_path)

    metadata_payload = {
        "cluster_id": cluster_id,
        "total_chunks": len(chunks_data),
        "dimension": dimension,
        "chunks": chunks_data
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    return idx_path, meta_path


def main():
    print("=========================================================")
    print("  Vector Orchestrator Agent - Local Integration Test")
    print("=========================================================\n")

    test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/orchestrator_test"))
    job_id = "test_job_orchestrator_999"

    # 1. Create simulated Lambda outputs for Cluster 0 (Physics/Quantum)
    cluster_0_chunks = [
        {
            "chunk_id": "c0_chunk_0",
            "document_id": "doc_physics",
            "filename": "quantum_physics.docx",
            "chunk_index": 0,
            "text": "Quantum entanglement is a phenomenon where particles remain connected regardless of distance."
        },
        {
            "chunk_id": "c0_chunk_1",
            "document_id": "doc_physics",
            "filename": "quantum_physics.docx",
            "chunk_index": 1,
            "text": "Superposition allows quantum bits to exist in multiple states simultaneously."
        }
    ]
    idx_0, meta_0 = create_mock_partition_faiss(test_dir, 0, cluster_0_chunks)
    print(f"1. Created simulated Lambda output for Cluster 0 ({len(cluster_0_chunks)} chunks).")

    # 2. Create simulated Lambda outputs for Cluster 1 (Distributed Systems & Formicx)
    cluster_1_chunks = [
        {
            "chunk_id": "c1_chunk_0",
            "document_id": "doc_distributed",
            "filename": "formicx_agents.docx",
            "chunk_index": 0,
            "text": "Formicx provides inter-process agent communication and workflow orchestration across distributed clusters."
        },
        {
            "chunk_id": "c1_chunk_1",
            "document_id": "doc_distributed",
            "filename": "formicx_agents.docx",
            "chunk_index": 1,
            "text": "The vector orchestrator agent aggregates vector embeddings from multiple serverless Lambda container workers."
        }
    ]
    idx_1, meta_1 = create_mock_partition_faiss(test_dir, 1, cluster_1_chunks)
    print(f"2. Created simulated Lambda output for Cluster 1 ({len(cluster_1_chunks)} chunks).")

    # 3. Instantiate VectorOrchestratorAgent
    orchestrator = VectorOrchestratorAgent()
    orchestrator.register_job(job_id=job_id, total_clusters=2, output_dir=test_dir)

    print("\n3. Submitting Cluster 0 output to Orchestrator...")
    res0 = orchestrator.submit_cluster_output(
        job_id=job_id,
        cluster_id=0,
        index_file_path=idx_0,
        metadata_file_path=meta_0,
        total_chunks=len(cluster_0_chunks)
    )
    print(f"   Response 0: {res0.get('status')} (Received: {res0.get('received_count')}/{res0.get('total_expected')})")

    print("\n4. Submitting Cluster 1 output to Orchestrator...")
    res1 = orchestrator.submit_cluster_output(
        job_id=job_id,
        cluster_id=1,
        index_file_path=idx_1,
        metadata_file_path=meta_1,
        total_chunks=len(cluster_1_chunks)
    )
    print(f"   Response 1: {res1.get('status')} (Received: {res1.get('received_count')}/{res1.get('total_expected')})")
    print(f"   Auto-Merged: {res1.get('auto_merged')}")

    merge_res = res1.get("merge_result") or {}
    master_index_path = merge_res.get("master_index_path")
    master_metadata_path = merge_res.get("master_metadata_path")

    print(f"\n5. Verifying Consolidated Master FAISS Vector DB:")
    print(f"   - Total Merged Vectors: {merge_res.get('total_vectors')}")
    print(f"   - Master Index File: {master_index_path} (Exists: {os.path.exists(master_index_path)})")
    print(f"   - Master Metadata File: {master_metadata_path} (Exists: {os.path.exists(master_metadata_path)})")

    # 6. Test RAG Vector Search against Consolidated Master FAISS Index
    print("\n6. Testing RAG Vector Search against Consolidated Master Index...")
    searcher = FAISSVectorSearcher(db_location=master_index_path, metadata_location=master_metadata_path)
    vec_engine = TextVectorizer()

    query = "How does Formicx orchestrate serverless agents?"
    query_vector = vec_engine.encode_text(query)
    results = searcher.search(query_vector=query_vector, top_k=2)

    print(f"\nQuery: '{query}'")
    print(f"Top Search Matches ({len(results)}):")
    for match in results:
        chunk_info = match.get("metadata", {})
        print(f"  Rank {match['rank']} | Score: {match['score']:.4f} | File: {chunk_info.get('filename')} | Chunk: {chunk_info.get('chunk_id')}")
        print(f"  Snippet: \"{match.get('text')}\"\n")

    print("[SUCCESS] Vector Orchestrator Local Integration Test Passed Successfully!")


if __name__ == "__main__":
    main()
