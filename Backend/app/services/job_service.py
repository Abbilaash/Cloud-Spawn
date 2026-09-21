import os
import sys
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.config import settings
from app.core.database import db_manager
from app.models.job import JobStatus
from app.models.document import DocumentStatus

logger = logging.getLogger(__name__)

# Ensure dox-splitter agent folder is on Python path for direct fallback
dox_splitter_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../dox-splitter"))
if dox_splitter_path not in sys.path:
    sys.path.insert(0, dox_splitter_path)


def process_knowledge_base_build_job(job_id: str):
    """Background task handler connecting file upload system to Formicx docx-splitter agent."""
    logger.info(f"[Job Runner] Starting Formicx-orchestrated build job for job_id: {job_id}")
    jobs_col = db_manager.get_jobs_collection()
    docs_col = db_manager.get_documents_collection()

    job = jobs_col.find_one({"job_id": job_id})
    if not job:
        logger.error(f"[MongoDB] Job {job_id} not found in 'jobs' collection.")
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    jobs_col.update_one(
        {"job_id": job_id},
        {"$set": {"status": JobStatus.PROCESSING, "started_at": now_iso}}
    )
    logger.info(f"[MongoDB] Updated job {job_id} status to '{JobStatus.PROCESSING}' in 'jobs' collection.")

    document_ids = job.get("document_ids", [])
    total_docs = len(document_ids)
    
    # Update documents status to processing and set telemetry step
    docs_col.update_many(
        {"document_id": {"$in": document_ids}},
        {"$set": {
            "status": DocumentStatus.PROCESSING,
            "processing_step": "Extracting Text & TF-IDF Vectorization"
        }}
    )
    logger.info(f"[MongoDB] Updated {total_docs} document record(s) status to '{DocumentStatus.PROCESSING}' (Step: 'Extracting Text & TF-IDF Vectorization') in 'documents' collection.")

    upload_dir = os.path.abspath(settings.UPLOAD_DIRECTORY)
    logger.info(f"[Formicx Agent] Dispatching document clustering task to Formicx 'docx-splitter' agent for directory: {upload_dir}")

    cluster_result: Dict[str, Any] = {}

    # 1. Attempt Formicx Daemon IPC Client Call
    try:
        from formicx import DaemonClient
        client = DaemonClient()

        # Send request message to docx-splitter agent via formicxd
        logger.info("[Formicx Agent] Sending IPC REQUEST message to 'docx-splitter' agent via Formicx Daemon...")
        client.send_message(
            sender="docx-splitter",
            recipient="docx-splitter",
            message_type="REQUEST",
            payload={
                "action": "cluster_documents",
                "folder_path": upload_dir,
                "distance_threshold": 0.6
            }
        )

        time.sleep(1.0)
        history = client.get_inbox("docx-splitter", history=True)
        for msg in reversed(history):
            payload = msg.get("payload", {})
            if payload.get("status") == "success" and "clusters" in payload:
                cluster_result = payload
                break

        if cluster_result:
            logger.info(f"[Formicx Agent] Successfully received IPC cluster response: {cluster_result.get('cluster_count')} dynamic clusters formed.")
    except Exception as e:
        logger.warning(f"[Formicx Agent] Formicx daemon IPC communication notice ({str(e)}). Running direct agent invocation.")

    # 2. Fallback: Direct Formicx Agent Invocation if daemon is not running
    if not cluster_result or cluster_result.get("status") != "success":
        try:
            logger.info("[Formicx Agent] Executing DocumentSplitterAgent instance directly...")
            from main import DocumentSplitterAgent
            agent = DocumentSplitterAgent(agent_name="cloudspawn-job-worker")
            agent.on_start()
            cluster_result = agent.process_document_clustering(folder_path=upload_dir, distance_threshold=0.6)
            logger.info(f"[Formicx Agent] Direct DocumentSplitterAgent execution completed: {cluster_result.get('cluster_count')} dynamic clusters formed.")
        except Exception as exc:
            logger.error(f"[Formicx Agent] Failed to execute Formicx docx-splitter agent: {str(exc)}", exc_info=True)
            cluster_result = {"status": "failed", "clusters": [], "cluster_count": 0}

    # 3. Finalize Job & Document Statuses in MongoDB
    completed_iso = datetime.now(timezone.utc).isoformat()
    is_success = cluster_result.get("status") == "success"
    final_status = JobStatus.COMPLETED if is_success else JobStatus.FAILED

    clusters = cluster_result.get("clusters", [])
    cluster_count = cluster_result.get("cluster_count", 0)

    # Map filename -> cluster_id
    doc_cluster_map: Dict[str, int] = {}
    for cl in clusters:
        c_id = cl.get("cluster_id", 0)
        for doc_name in cl.get("documents", []):
            doc_cluster_map[doc_name] = c_id

    # Update Job record in MongoDB
    jobs_col.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": final_status,
            "processed_documents": total_docs if is_success else 0,
            "failed_documents": 0 if is_success else total_docs,
            "progress": 100 if is_success else 0,
            "cluster_count": cluster_count,
            "clusters": clusters,
            "completed_at": completed_iso
        }}
    )
    logger.info(f"[MongoDB] Updated build job {job_id} record in 'jobs' collection. Status: '{final_status}', Clusters: {cluster_count}.")

    # Update Document records with telemetry and cluster ID assignments in MongoDB
    final_doc_status = DocumentStatus.COMPLETED if is_success else DocumentStatus.FAILED
    for doc_id in document_ids:
        doc_record = docs_col.find_one({"document_id": doc_id})
        filename = doc_record.get("filename", "") if doc_record else ""
        c_id = doc_cluster_map.get(filename)
        
        step_text = f"Formicx Partitioned (Cluster #{c_id})" if (is_success and c_id is not None) else ("Formicx Partitioned" if is_success else "Processing Failed")
        
        update_fields: Dict[str, Any] = {
            "status": final_doc_status,
            "processing_step": step_text
        }
        if c_id is not None:
            update_fields["cluster_id"] = c_id

        docs_col.update_one(
            {"document_id": doc_id},
            {"$set": update_fields}
        )
        logger.info(f"[MongoDB] Updated document '{filename}' (ID: {doc_id}) in 'documents' collection. Status: '{final_doc_status}', Cluster: #{c_id if c_id is not None else 'N/A'}.")

    logger.info(f"[Job Runner] Build job {job_id} finalized with status: '{final_status}' ({cluster_count} dynamic clusters).")


