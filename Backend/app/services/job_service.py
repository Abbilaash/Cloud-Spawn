import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.database import db_manager
from app.models.job import create_job_model, JobStatus
from app.models.document import DocumentStatus
from app.services.document_service import get_document_processor
from app.services.embedding_service import embedding_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

def process_knowledge_base_build_job(job_id: str):
    """Background task handler for processing documents into ChromaDB."""
    logger.info(f"Starting background job execution for job_id: {job_id}")
    jobs_col = db_manager.get_jobs_collection()
    docs_col = db_manager.get_documents_collection()

    job = jobs_col.find_one({"job_id": job_id})
    if not job:
        logger.error(f"Job {job_id} not found in database.")
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    jobs_col.update_one(
        {"job_id": job_id},
        {"$set": {"status": JobStatus.PROCESSING, "started_at": now_iso}}
    )

    processor = get_document_processor()
    document_ids = job.get("document_ids", [])
    total_docs = len(document_ids)
    processed_count = 0
    failed_count = 0

    for doc_id in document_ids:
        try:
            doc_data = docs_col.find_one({"document_id": doc_id})
            if not doc_data:
                logger.error(f"Document {doc_id} not found in MongoDB")
                failed_count += 1
                continue

            # Update document status to processing
            docs_col.update_one(
                {"document_id": doc_id},
                {"$set": {"status": DocumentStatus.PROCESSING}}
            )

            file_path = doc_data.get("file_path")
            filename = doc_data.get("filename")

            # 1. Text extraction & chunking
            chunks = processor.extract_text_and_chunk(
                file_path=file_path,
                document_id=doc_id,
                filename=filename
            )

            if chunks:
                # 2. Embedding generation
                embeddings = embedding_service.embed_documents(chunks)

                # 3. Vector database storage
                vector_service.add_chunks(chunks, embeddings)

            # Update document status to completed
            docs_col.update_one(
                {"document_id": doc_id},
                {"$set": {"status": DocumentStatus.COMPLETED}}
            )

            processed_count += 1

        except Exception as e:
            logger.error(f"Failed to process document {doc_id}: {str(e)}", exc_info=True)
            failed_count += 1
            docs_col.update_one(
                {"document_id": doc_id},
                {"$set": {"status": DocumentStatus.FAILED}}
            )

        # Update job progress after each document
        progress = int(((processed_count + failed_count) / total_docs) * 100) if total_docs > 0 else 100
        jobs_col.update_one(
            {"job_id": job_id},
            {"$set": {
                "processed_documents": processed_count,
                "failed_documents": failed_count,
                "progress": progress
            }}
        )

    # Finalize job status
    completed_iso = datetime.now(timezone.utc).isoformat()
    final_status = JobStatus.COMPLETED if failed_count < total_docs else JobStatus.FAILED
    jobs_col.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": final_status,
            "completed_at": completed_iso
        }}
    )
    logger.info(f"Job {job_id} finished with status: {final_status}")
