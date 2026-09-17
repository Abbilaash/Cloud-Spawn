import uuid
import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from app.core.database import db_manager
from app.models.job import create_job_model, JobStatus
from app.schemas.job import BuildJobRequest, BuildJobResponse, JobStatusResponse
from app.services.job_service import process_knowledge_base_build_job

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("/build", response_model=BuildJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_build_job(
    request: BuildJobRequest,
    background_tasks: BackgroundTasks
):
    """Trigger background job for DOCX ingestion, chunking, embedding, and vector indexing."""
    if not request.document_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_ids list cannot be empty."
        )

    docs_col = db_manager.get_documents_collection()
    jobs_col = db_manager.get_jobs_collection()

    # Validate that at least one requested document exists
    existing_docs_count = docs_col.count_documents({"document_id": {"$in": request.document_ids}})
    if existing_docs_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="None of the specified document_ids were found."
        )

    job_id = str(uuid.uuid4())
    job_doc = create_job_model(
        job_id=job_id,
        document_ids=request.document_ids,
        total_documents=len(request.document_ids),
        status=JobStatus.QUEUED
    )

    jobs_col.insert_one(job_doc)
    logger.info(f"Created knowledge base build job_id: {job_id} for {len(request.document_ids)} documents.")

    # Schedule background processing
    background_tasks.add_task(process_knowledge_base_build_job, job_id)

    return BuildJobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Retrieve execution status and progress metrics for a knowledge base job."""
    jobs_col = db_manager.get_jobs_collection()
    job = jobs_col.find_one({"job_id": job_id})

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        total_documents=job.get("total_documents", 0),
        processed_documents=job.get("processed_documents", 0),
        failed_documents=job.get("failed_documents", 0),
        progress=job.get("progress", 0),
        created_at=job.get("created_at"),
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at")
    )
