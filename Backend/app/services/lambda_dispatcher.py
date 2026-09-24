import os
import sys
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.services.document_service import LocalDocumentProcessor

logger = logging.getLogger(__name__)


class LambdaDispatcherService:
    """Service responsible for spawning AWS Lambda processes per document cluster to perform vector embeddings."""

    def __init__(self):
        self.doc_processor = LocalDocumentProcessor()

    def invoke_lambda_for_cluster(
        self,
        job_id: str,
        cluster_id: int,
        text_chunks: List[Dict[str, Any]],
        output_dir: str
    ) -> Dict[str, Any]:
        """Spawns an AWS Lambda process invocation for a single document cluster.
        
        Args:
            job_id: Unique build job identifier.
            cluster_id: Numeric cluster identifier from docx-splitter.
            text_chunks: List of chunk dictionaries containing text, chunk_id, filename, document_id, etc.
            output_dir: Target directory for FAISS index and metadata.
            
        Returns:
            Dict containing status, cluster_id, chunk count, index paths, and execution info.
        """
        if not text_chunks:
            logger.warning(f"[AWS Lambda Dispatcher] Cluster #{cluster_id} contains no text chunks. Skipping worker spawn.")
            return {
                "cluster_id": cluster_id,
                "status": "skipped",
                "message": "No text chunks found for cluster.",
                "total_chunks": 0
            }

        payload = {
            "job_id": job_id,
            "cluster_id": cluster_id,
            "text_chunks": text_chunks,
            "output_dir": output_dir
        }

        try:
            import boto3
            logger.info(f"[AWS Lambda Dispatcher] Spawning AWS Lambda worker process for Cluster #{cluster_id} (Function: '{settings.AWS_LAMBDA_FUNCTION_NAME}', Region: '{settings.AWS_REGION}')...")
            
            lambda_client = boto3.client(
                "lambda",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None
            )

            response = lambda_client.invoke(
                FunctionName=settings.AWS_LAMBDA_FUNCTION_NAME,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload)
            )

            response_payload_raw = response["Payload"].read().decode("utf-8")
            response_data = json.loads(response_payload_raw)

            if response_data.get("statusCode") == 200:
                body = response_data.get("body", {})
                logger.info(f"[AWS Lambda Dispatcher] AWS Lambda worker for Cluster #{cluster_id} completed successfully. Vectorized {body.get('total_chunks')} chunks.")
                return body
            else:
                logger.error(f"[AWS Lambda Dispatcher] AWS Lambda worker for Cluster #{cluster_id} returned error: {response_data}")
                return {
                    "cluster_id": cluster_id,
                    "status": "error",
                    "message": response_data.get("body", {}).get("message", "Lambda execution failed")
                }
        except Exception as exc:
            logger.error(f"[AWS Lambda Dispatcher] AWS Lambda worker process failed for Cluster #{cluster_id}: {str(exc)}", exc_info=True)
            return {
                "cluster_id": cluster_id,
                "status": "error",
                "message": str(exc)
            }

    def dispatch_clusters(
        self,
        job_id: str,
        clusters: List[Dict[str, Any]],
        upload_dir: str,
        doc_filename_id_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Dispatches parallel Lambda processes for all clusters produced by docx-splitter.
        
        Args:
            job_id: Build job ID.
            clusters: List of cluster metadata dicts from docx-splitter agent.
            upload_dir: Directory where uploaded source documents reside.
            doc_filename_id_map: Mapping of filename -> document_id.
            
        Returns:
            Summary dict with cluster embedding results.
        """
        output_dir = os.path.abspath(settings.FAISS_OUTPUT_DIRECTORY)
        os.makedirs(output_dir, exist_ok=True)
        doc_map = doc_filename_id_map or {}

        cluster_tasks = []

        logger.info(f"[Lambda Dispatcher] Extracting text chunks and preparing Lambda workers for {len(clusters)} cluster(s)...")

        for cluster_info in clusters:
            cluster_id = cluster_info.get("cluster_id", 0)
            doc_names = cluster_info.get("documents", [])

            cluster_chunks: List[Dict[str, Any]] = []

            for doc_name in doc_names:
                file_path = os.path.join(upload_dir, doc_name)
                if not os.path.exists(file_path):
                    logger.warning(f"[Lambda Dispatcher] Document file '{file_path}' not found on disk. Skipping.")
                    continue

                document_id = doc_map.get(doc_name, f"doc_{doc_name.replace('.', '_')}")
                try:
                    chunks = self.doc_processor.extract_text_and_chunk(
                        file_path=file_path,
                        document_id=document_id,
                        filename=doc_name
                    )
                    cluster_chunks.extend(chunks)
                except Exception as exc:
                    logger.error(f"[Lambda Dispatcher] Text extraction error for file '{doc_name}': {str(exc)}")

            cluster_tasks.append((cluster_id, cluster_chunks))

        # Spawn Lambda workers in parallel per cluster using ThreadPoolExecutor
        cluster_results: List[Dict[str, Any]] = []
        max_workers = max(1, min(10, len(cluster_tasks)))

        logger.info(f"[Lambda Dispatcher] Spawning {len(cluster_tasks)} Lambda process worker(s) across {max_workers} thread(s)...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_cluster = {
                executor.submit(
                    self.invoke_lambda_for_cluster,
                    job_id=job_id,
                    cluster_id=cid,
                    text_chunks=chunks,
                    output_dir=output_dir
                ): cid
                for cid, chunks in cluster_tasks
            }

            for future in as_completed(future_to_cluster):
                cid = future_to_cluster[future]
                try:
                    res = future.result()
                    cluster_results.append(res)
                except Exception as exc:
                    logger.error(f"[Lambda Dispatcher] Exception executing worker for Cluster #{cid}: {str(exc)}")
                    cluster_results.append({
                        "cluster_id": cid,
                        "status": "error",
                        "message": str(exc)
                    })

        successful_count = sum(1 for r in cluster_results if r.get("status") == "success")
        total_chunks = sum(r.get("total_chunks", 0) for r in cluster_results if r.get("status") == "success")

        logger.info(f"[Lambda Dispatcher] Lambda embedding workers complete. Success: {successful_count}/{len(clusters)} clusters. Total chunks: {total_chunks}.")

        return {
            "status": "success" if successful_count == len(clusters) else ("partial_success" if successful_count > 0 else "failed"),
            "total_clusters": len(clusters),
            "successful_clusters": successful_count,
            "total_chunks_vectorized": total_chunks,
            "cluster_results": cluster_results
        }


lambda_dispatcher = LambdaDispatcherService()
