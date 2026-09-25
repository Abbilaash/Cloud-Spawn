#!/usr/bin/env python3
import os
import sys
import json
import time
import logging

# Set PYTHONPATH to Backend, dox-splitter, lambda-worker, vector-orchestrator
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dox_splitter_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dox-splitter"))
lambda_worker_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../lambda-worker"))
vector_orchestration_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../vector-orchestrator"))

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.services.lambda_dispatcher import lambda_dispatcher
from app.services.vector_service import vector_service
from app.services.embedding_service import embedding_service

import importlib.util

def load_module_from_file(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

dox_splitter_mod = load_module_from_file("dox_splitter_main", os.path.join(dox_splitter_dir, "main.py"))
DocumentSplitterAgent = dox_splitter_mod.DocumentSplitterAgent

orchestrator_mod = load_module_from_file("orchestrator_main", os.path.join(vector_orchestration_dir, "main.py"))
VectorOrchestratorAgent = orchestrator_mod.VectorOrchestratorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline_test")


def main():
    print("=========================================================================")
    print("  CloudSpawn End-to-End Pipeline Verification Test")
    print("=========================================================================\n")

    test_upload_dir = os.path.abspath("./data/test_uploads")
    test_faiss_dir = os.path.abspath("./data/test_faiss_output")
    settings.UPLOAD_DIRECTORY = test_upload_dir
    settings.FAISS_OUTPUT_DIRECTORY = test_faiss_dir

    os.makedirs(test_upload_dir, exist_ok=True)
    os.makedirs(test_faiss_dir, exist_ok=True)

    # 1. Create test document files locally
    doc1_content = (
        "Quantum computing harnesses superposition and entanglement to perform complex computations. "
        "Quantum bits or qubits allow parallel state processing beyond classical binary hardware."
    )
    doc2_content = (
        "Autonomous Formicx AI agents execute multi-step task workflows using inter-process communication. "
        "The vector orchestrator agent aggregates vector embeddings from serverless Lambda container workers."
    )

    doc1_path = os.path.join(test_upload_dir, "doc1_quantum.docx")
    doc2_path = os.path.join(test_upload_dir, "doc2_formicx.docx")

    # Helper to create simple docx file
    import docx
    for path, text in [(doc1_path, doc1_content), (doc2_path, doc2_content)]:
        doc = docx.Document()
        doc.add_paragraph(text)
        doc.save(path)

    print(f"1. Created test document files in '{test_upload_dir}':")
    print(f"   - doc1_quantum.docx")
    print(f"   - doc2_formicx.docx\n")

    # 2. Step 1: Document Splitter Dynamic Clustering
    print("2. [Formicx Agent] Executing DocumentSplitterAgent dynamic clustering over all uploaded files...")
    splitter = DocumentSplitterAgent()
    cluster_result = splitter.process_document_clustering(folder_path=test_upload_dir, distance_threshold=0.6)

    clusters = cluster_result.get("clusters", [])
    print(f"   - Clustering Status: {cluster_result.get('status')}")
    print(f"   - Cluster Count: {len(clusters)}")
    for cl in clusters:
        print(f"     * Cluster #{cl['cluster_id']}: {cl['documents']}")

    assert cluster_result.get("status") == "success", "Clustering failed!"

    # 3. Step 2: Lambda Worker Chunk Vectorization & Partition FAISS Index Generation
    print("\n3. [Lambda Dispatcher] Spawning Lambda container workers per dynamic cluster...")
    job_id = "test_pipeline_job_100"
    doc_map = {"doc1_quantum.docx": "doc_1", "doc2_formicx.docx": "doc_2"}

    embedding_summary = lambda_dispatcher.dispatch_clusters(
        job_id=job_id,
        clusters=clusters,
        upload_dir=test_upload_dir,
        doc_filename_id_map=doc_map
    )

    print(f"   - Lambda Worker Status: {embedding_summary.get('status')}")
    print(f"   - Successful Clusters: {embedding_summary.get('successful_clusters')}/{len(clusters)}")
    print(f"   - Chunks Vectorized: {embedding_summary.get('total_chunks_vectorized')}")

    assert embedding_summary.get("status") in ["success", "partial_success"], "Lambda dispatch failed!"

    # 4. Step 3: Vector Orchestrator Agent Consolidation
    print("\n4. [Formicx Orchestrator] Triggering VectorOrchestratorAgent to consolidate partition FAISS indices...")
    orchestrator = VectorOrchestratorAgent()
    orchestrator.register_job(job_id=job_id, total_clusters=len(clusters), output_dir=test_faiss_dir)

    for c_res in embedding_summary.get("cluster_results", []):
        orchestrator.submit_cluster_output(
            job_id=job_id,
            cluster_id=c_res.get("cluster_id", 0),
            index_file_path=c_res.get("index_file_path"),
            metadata_file_path=c_res.get("metadata_file_path"),
            total_chunks=c_res.get("total_chunks", 0)
        )

    merge_res = orchestrator.merge_job_indices(job_id)
    master_index_path = merge_res.get("master_index_path")
    master_meta_path = merge_res.get("master_metadata_path")

    print(f"   - Master FAISS Vector DB Status: {merge_res.get('status')}")
    print(f"   - Merged Vector Count: {merge_res.get('total_vectors')}")
    print(f"   - Master Index File: {master_index_path} (Exists: {os.path.exists(master_index_path)})")

    assert os.path.exists(master_index_path), "Master index file not created!"

    # 5. Step 4: RAG Vector Search Verification
    print("\n5. [Vector Service] Executing RAG Search Query over Consolidated Master FAISS Index...")
    query = "How do Formicx AI agents aggregate vector embeddings?"
    query_vector = embedding_service.embed_text(query)

    search_results = vector_service.search(query_embedding=query_vector, top_k=2)

    print(f"\nQuery: '{query}'")
    print(f"Search Matches ({len(search_results)}):")
    for r in search_results:
        print(f"  - Document: {r.get('filename')} | Score: {r.get('score'):.4f}")
        print(f"    Snippet: \"{r.get('text')}\"\n")

    assert len(search_results) > 0, "No search matches returned!"
    print("[SUCCESS] CloudSpawn End-to-End Pipeline Test Completed Successfully!")


if __name__ == "__main__":
    main()
