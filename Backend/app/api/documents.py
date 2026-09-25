import os
import uuid
import logging
from typing import List,Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings
from app.core.database import db_manager
from app.models.document import create_document_model, DocumentStatus
from app.schemas.document import UploadResponse, DocumentItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload one or multiple DOCX/PDF files to knowledge base storage."""
    if not files:
        logger.warning("[File Upload] Upload request received with empty file list.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded."
        )

    logger.info(f"[File Upload] Starting upload processing for {len(files)} file(s). Purging previous documents...")
    upload_dir = settings.UPLOAD_DIRECTORY
    faiss_dir = settings.FAISS_OUTPUT_DIRECTORY
    docs_col = db_manager.get_documents_collection()
    jobs_col = db_manager.get_jobs_collection()

    # 1. Purge previous uploaded files from disk
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if not f.startswith(".gitkeep"):
                fp = os.path.join(upload_dir, f)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                except Exception as e:
                    logger.warning(f"[File Upload Cleanup] Could not remove file '{fp}': {e}")
    os.makedirs(upload_dir, exist_ok=True)

    # 2. Purge previous FAISS index files
    if os.path.exists(faiss_dir):
        for f in os.listdir(faiss_dir):
            fp = os.path.join(faiss_dir, f)
            try:
                if os.path.isfile(fp):
                    os.remove(fp)
            except Exception as e:
                logger.warning(f"[File Upload Cleanup] Could not remove FAISS file '{fp}': {e}")

    # 3. Purge previous document and job records from MongoDB
    purged_res = docs_col.delete_many({})
    jobs_col.delete_many({})
    logger.info(f"[File Upload Cleanup] Purged {purged_res.deleted_count} previous document record(s) and job histories from MongoDB.")

    uploaded_docs: List[DocumentItem] = []

    for file in files:
        filename = file.filename or ""
        if not filename.lower().endswith((".docx", ".pdf")):
            logger.warning(f"[File Upload] Rejected unsupported file extension: '{filename}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type for '{filename}'. Only .docx and .pdf files are supported."
            )

        document_id = str(uuid.uuid4())
        safe_filename = f"{document_id}_{os.path.basename(filename)}"
        destination_path = os.path.join(upload_dir, safe_filename)

        try:
            content = await file.read()
            file_size = len(content)

            if file_size == 0:
                logger.warning(f"[File Upload] Rejected 0-byte empty file: '{filename}'")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uploaded file '{filename}' is empty."
                )

            with open(destination_path, "wb") as f:
                f.write(content)
            logger.info(f"[File Upload] Saved file bytes to disk at '{destination_path}' ({file_size} bytes)")

            doc_model = create_document_model(
                document_id=document_id,
                filename=filename,
                file_size=file_size,
                file_path=destination_path,
                status=DocumentStatus.UPLOADED
            )

            docs_col.insert_one(doc_model)
            logger.info(f"[MongoDB] Inserted document record for '{filename}' (ID: {document_id}) into 'documents' collection.")

            uploaded_docs.append(DocumentItem(
                document_id=document_id,
                filename=filename,
                status=DocumentStatus.UPLOADED,
                file_size=file_size,
                uploaded_at=doc_model["uploaded_at"]
            ))

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[File Upload] Error saving file '{filename}': {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded document '{filename}'."
            )

    logger.info(f"[File Upload] Upload complete. {len(uploaded_docs)} document(s) saved and indexed.")
    return UploadResponse(documents=uploaded_docs)



from app.schemas.document import UploadResponse, DocumentItem, DocumentDetailResponse

@router.get("", response_model=UploadResponse)
async def list_documents():
    """List all uploaded documents stored in the database with telemetry indicators."""
    docs_col = db_manager.get_documents_collection()
    documents_cursor = docs_col.find({}, {"_id": 0})
    
    docs_list: List[DocumentItem] = []
    for doc in documents_cursor:
        docs_list.append(DocumentItem(
            document_id=doc.get("document_id", ""),
            filename=doc.get("filename", ""),
            status=doc.get("status", DocumentStatus.UPLOADED),
            file_size=doc.get("file_size"),
            file_type=doc.get("file_type"),
            processing_step=doc.get("processing_step"),
            cluster_id=doc.get("cluster_id"),
            uploaded_at=doc.get("uploaded_at")
        ))

    return UploadResponse(documents=docs_list)


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_detail(document_id: str):
    """Retrieve detailed document telemetry, processing steps, and dynamic cluster splitups."""
    docs_col = db_manager.get_documents_collection()
    jobs_col = db_manager.get_jobs_collection()

    doc = docs_col.find_one({"document_id": document_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    # Find associated job
    job = jobs_col.find_one({"document_ids": document_id})
    job_id = job.get("job_id") if job else None

    cluster_id = doc.get("cluster_id")
    cluster_docs: List[str] = []
    cluster_size: Optional[int] = None

    # If job has clusters, find the cluster matching this document
    if job and job.get("clusters"):
        filename = doc.get("filename", "")
        for cl in job["clusters"]:
            if filename in cl.get("documents", []):
                cluster_id = cl.get("cluster_id")
                cluster_docs = cl.get("documents", [])
                cluster_size = cl.get("size", len(cluster_docs))
                break

    return DocumentDetailResponse(
        document_id=doc["document_id"],
        filename=doc.get("filename", ""),
        file_type=doc.get("file_type"),
        file_size=doc.get("file_size"),
        status=doc.get("status", DocumentStatus.UPLOADED),
        processing_step=doc.get("processing_step", "Uploaded"),
        cluster_id=cluster_id,
        cluster_documents=cluster_docs if cluster_docs else None,
        cluster_size=cluster_size,
        uploaded_at=doc.get("uploaded_at"),
        job_id=job_id
    )


from app.services.vector_service import vector_service

@router.delete("", status_code=status.HTTP_200_OK)
async def delete_all_documents():
    """Purge all uploaded documents from disk, S3, vector store, and MongoDB."""
    docs_col = db_manager.get_documents_collection()
    jobs_col = db_manager.get_jobs_collection()

    deleted_count = 0
    # 1. Clean disk files
    upload_dir = settings.UPLOAD_DIRECTORY
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if not f.startswith(".gitkeep"):
                fp = os.path.join(upload_dir, f)
                try:
                    if os.path.isfile(fp):
                        os.remove(fp)
                except Exception as e:
                    logger.warning(f"Could not remove file '{fp}': {e}")

    # 2. Clean S3 bucket if configured
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_S3_BUCKET_NAME:
        try:
            import boto3
            s3 = boto3.client(
                "s3",
                region_name=settings.AWS_REGION or "us-east-1",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            objects = s3.list_objects_v2(Bucket=settings.AWS_S3_BUCKET_NAME)
            if "Contents" in objects:
                delete_keys = [{"Key": obj["Key"]} for obj in objects["Contents"]]
                s3.delete_objects(Bucket=settings.AWS_S3_BUCKET_NAME, Delete={"Objects": delete_keys})
                logger.info(f"[S3 Cleanup] Deleted {len(delete_keys)} objects from S3 bucket '{settings.AWS_S3_BUCKET_NAME}'.")
        except Exception as e:
            logger.warning(f"[S3 Cleanup] S3 deletion notice: {e}")

    # 3. Clean Vector Service
    vector_service._store.clear()

    # 4. Clean MongoDB
    res = docs_col.delete_many({})
    jobs_col.delete_many({})
    deleted_count = res.deleted_count

    logger.info(f"[Cleanup] Purged {deleted_count} document record(s) and cleared database.")
    return {"status": "ok", "message": f"Successfully deleted {deleted_count} document(s) and purged all stores."}


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: str):
    """Delete a single document from disk, S3, vector store, and MongoDB."""
    docs_col = db_manager.get_documents_collection()
    doc = docs_col.find_one({"document_id": document_id})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found."
        )

    file_path = doc.get("file_path", "")
    filename = doc.get("filename", "")

    # 1. Delete file from disk
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"[Cleanup] Removed file from disk: '{file_path}'")
        except Exception as e:
            logger.warning(f"Could not remove file '{file_path}': {e}")

    upload_dir = settings.UPLOAD_DIRECTORY
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.startswith(f"{document_id}_"):
                fp = os.path.join(upload_dir, f)
                try:
                    os.remove(fp)
                    logger.info(f"[Cleanup] Removed file from upload directory: '{fp}'")
                except Exception as e:
                    logger.warning(f"Could not remove file '{fp}': {e}")

    # 2. Delete from Vector Service
    vector_service.delete_document(document_id)

    # 3. Delete from MongoDB
    docs_col.delete_one({"document_id": document_id})

    logger.info(f"[Cleanup] Deleted document '{filename}' (ID: {document_id}).")
    return {"status": "ok", "message": f"Document '{filename}' deleted successfully."}



