import os
import json
import logging
from typing import Dict, Any, List
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("lambda-worker")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS package is not installed.")

from vectorizer_module import TextVectorizer

# Initialize global vectorizer instance for Lambda container warm starts
vectorizer = TextVectorizer(normalize_embeddings=True)


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """AWS Lambda Container event handler for serverless chunk vectorization and FAISS index generation.
    
    Args:
        event: Dict containing:
            - cluster_id (int/str): Cluster identifier dispatched by dox-splitter.
            - job_id (str): Associated job ID.
            - text_chunks (List[Dict]): List of chunk objects containing 'text', 'chunk_id', 'filename', etc.
              OR 'texts' (List[str]): List of plain text strings.
            - output_dir (str, optional): Target output directory for FAISS index & metadata.
        context: AWS Lambda context object.
        
    Returns:
        Dict with HTTP status code and execution summary payload.
    """
    logger.info("[AWS Lambda Worker] Received invocation event...")

    # Support event directly or event body if JSON string from API Gateway
    if isinstance(event, dict) and "body" in event and isinstance(event["body"], str):
        try:
            payload = json.loads(event["body"])
        except Exception:
            payload = event
    else:
        payload = event or {}

    cluster_id = payload.get("cluster_id", 0)
    job_id = payload.get("job_id", "unknown_job")
    output_dir = payload.get("output_dir", "/tmp")
    # If running inside AWS Lambda runtime environment, force output_dir to /tmp
    if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT"):
        if not str(output_dir).startswith("/tmp"):
            output_dir = "/tmp"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception:
        output_dir = "/tmp"
        os.makedirs(output_dir, exist_ok=True)

    raw_chunks = payload.get("text_chunks", payload.get("chunks", []))
    raw_texts = payload.get("texts", [])

    # Format chunks list
    formatted_chunks: List[Dict[str, Any]] = []
    texts_to_vectorize: List[str] = []

    if raw_chunks:
        for idx, item in enumerate(raw_chunks):
            if isinstance(item, dict):
                text_content = item.get("text", item.get("content", ""))
                if text_content and text_content.strip():
                    texts_to_vectorize.append(text_content.strip())
                    formatted_chunks.append({
                        "vector_id": len(formatted_chunks),
                        "chunk_id": item.get("chunk_id", f"chunk_{idx}"),
                        "document_id": item.get("document_id", ""),
                        "filename": item.get("filename", ""),
                        "chunk_index": item.get("chunk_index", idx),
                        "text": text_content.strip()
                    })
            elif isinstance(item, str) and item.strip():
                texts_to_vectorize.append(item.strip())
                formatted_chunks.append({
                    "vector_id": len(formatted_chunks),
                    "chunk_id": f"chunk_{idx}",
                    "text": item.strip()
                })
    elif raw_texts:
        for idx, text in enumerate(raw_texts):
            if text and text.strip():
                texts_to_vectorize.append(text.strip())
                formatted_chunks.append({
                    "vector_id": idx,
                    "chunk_id": f"chunk_{idx}",
                    "text": text.strip()
                })

    if not texts_to_vectorize:
        logger.warning(f"[AWS Lambda Worker] No valid text chunks provided for cluster_id={cluster_id}.")
        return {
            "statusCode": 400,
            "body": {
                "status": "error",
                "message": "No valid text chunks provided in invocation payload.",
                "cluster_id": cluster_id,
                "job_id": job_id
            }
        }

    logger.info(f"[AWS Lambda Worker] Vectorizing {len(texts_to_vectorize)} text chunk(s) for cluster_id={cluster_id} (job_id={job_id})...")

    # 1. Vectorize text chunks using all-MiniLM-L6-v2 (384-dimensional dense vectors)
    try:
        embeddings = vectorizer.encode_batch_numpy(texts_to_vectorize)
    except Exception as exc:
        logger.error(f"[AWS Lambda Worker] Vectorization failed: {str(exc)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {
                "status": "error",
                "message": f"Vectorization failed: {str(exc)}",
                "cluster_id": cluster_id,
                "job_id": job_id
            }
        }

    total_vectors, dimension = embeddings.shape
    logger.info(f"[AWS Lambda Worker] Generated embeddings matrix shape ({total_vectors} x {dimension}).")

    # 2. Build FAISS Index
    index_file_name = f"cluster_{cluster_id}_index.faiss"
    metadata_file_name = f"cluster_{cluster_id}_metadata.json"
    index_file_path = os.path.join(output_dir, index_file_name)
    metadata_file_path = os.path.join(output_dir, metadata_file_name)

    if FAISS_AVAILABLE:
        # IndexFlatIP uses Inner Product (exact Cosine Similarity on L2 normalized vectors)
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        faiss.write_index(index, index_file_path)
        logger.info(f"[AWS Lambda Worker] FAISS index written to '{index_file_path}'. Total indexed: {index.ntotal}")
    else:
        logger.warning("[AWS Lambda Worker] FAISS package not present. Saving raw embeddings array...")
        np.save(index_file_path.replace(".faiss", ".npy"), embeddings)

    # 3. Save Metadata Mapping File
    with open(metadata_file_path, "w", encoding="utf-8") as f:
        json.dump(formatted_chunks, f, indent=2)
    logger.info(f"[AWS Lambda Worker] Metadata mapping saved to '{metadata_file_path}'.")

    response_payload = {
        "status": "success",
        "job_id": job_id,
        "cluster_id": cluster_id,
        "total_chunks": total_vectors,
        "dimension": dimension,
        "index_file_path": index_file_path,
        "metadata_file_path": metadata_file_path,
        "index_file_name": index_file_name,
        "metadata_file_name": metadata_file_name
    }

    return {
        "statusCode": 200,
        "body": response_payload
    }
