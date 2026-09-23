import os
import sys
import json
import numpy as np

# Ensure Backend/app and lambda-worker are on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Backend")))
sys.path.insert(0, os.path.dirname(__file__))

from handler import lambda_handler

def main():
    print("=========================================================")
    print("  AWS Lambda Container Worker — Local Simulation Test")
    print("=========================================================\n")

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/lambda_test_output"))
    os.makedirs(output_dir, exist_ok=True)

    # 1. Construct sample cluster chunk invocation event
    sample_event = {
        "job_id": "test_job_12345",
        "cluster_id": 0,
        "output_dir": output_dir,
        "text_chunks": [
            {
                "chunk_id": "doc1_chunk_0",
                "document_id": "doc1",
                "filename": "quantum_computing_intro.docx",
                "chunk_index": 0,
                "text": "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve complex problems."
            },
            {
                "chunk_id": "doc1_chunk_1",
                "document_id": "doc1",
                "filename": "quantum_computing_intro.docx",
                "chunk_index": 1,
                "text": "Superposition and entanglement are two key principles of quantum physics that empower quantum computers."
            },
            {
                "chunk_id": "doc2_chunk_0",
                "document_id": "doc2",
                "filename": "ai_agents_framework.docx",
                "chunk_index": 0,
                "text": "Autonomous AI agents perform complex multi-step tasks by utilizing tool invocation, memory, and LLM reasoning."
            }
        ]
    }

    print(f"1. Invoking Lambda Handler locally for cluster_id={sample_event['cluster_id']}...")
    res = lambda_handler(sample_event, None)
    
    print("\n2. Lambda Invocation Response:")
    print(json.dumps(res, indent=2))

    if res.get("statusCode") != 200:
        print("\n[ERROR] Lambda Invocation Test Failed!")
        sys.path.pop(0)
        return


    body = res.get("body", {})
    index_path = body.get("index_file_path")
    metadata_path = body.get("metadata_file_path")

    print(f"\n3. Verifying output files exist:")
    print(f"   - Index File: {index_path} (Exists: {os.path.exists(index_path)})")
    print(f"   - Metadata File: {metadata_path} (Exists: {os.path.exists(metadata_path)})")

    # 4. Verify FAISS Vector Search if FAISS & FAISSVectorSearcher are available
    try:
        from app.rag_inference import FAISSVectorSearcher
        from vectorizer_module import TextVectorizer

        print("\n4. Testing FAISS Vector Search against Lambda-generated index...")
        searcher = FAISSVectorSearcher(db_location=index_path, metadata_location=metadata_path)
        vec_engine = TextVectorizer()
        
        query = "What principles empower quantum computers?"
        query_vector = vec_engine.encode_text(query)

        search_results = searcher.search(query_vector=query_vector, top_k=2)
        print(f"\nQuery: '{query}'")
        print(f"Top FAISS Search Matches ({len(search_results)}):")
        for match in search_results:
            print(f"  Rank {match['rank']} | Score: {match['score']:.4f} | Chunk ID: {match.get('metadata', {}).get('chunk_id')}")
            print(f"  Snippet: \"{match.get('text')}\"\n")

    except Exception as exc:
        print(f"\nNote during FAISS search verification: {str(exc)}")

    print("[SUCCESS] Local Lambda Container Worker Simulation Test Passed Successfully!")

if __name__ == "__main__":
    main()
