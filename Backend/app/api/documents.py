import os
import uuid
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings
from app.core.database import db_manager
from app.models.document import create_document_model, DocumentStatus
from app.schemas.document import UploadResponse, DocumentItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload one or multiple DOCX files to the knowledge base storage."""
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded."
        )

    upload_dir = settings.UPLOAD_DIRECTORY
    os.makedirs(upload_dir, exist_ok=True)

    uploaded_docs: List[DocumentItem] = []
    docs_col = db_manager.get_documents_collection()

    for file in files:
        # Validate filename and extension
        filename = file.filename or ""
        if not filename.lower().endswith(".docx"):
            logger.warning(f"Rejected unsupported file upload: {filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type for '{filename}'. Only .docx files are supported."
            )

        document_id = str(uuid.uuid4())
        safe_filename = f"{document_id}_{os.path.basename(filename)}"
        destination_path = os.path.join(upload_dir, safe_filename)

        try:
            content = await file.read()
            file_size = len(content)

            if file_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Uploaded file '{filename}' is empty."
                )

            with open(destination_path, "wb") as f:
                f.write(content)

            doc_model = create_document_model(
                document_id=document_id,
                filename=filename,
                file_size=file_size,
                file_path=destination_path,
                status=DocumentStatus.UPLOADED
            )

            docs_col.insert_one(doc_model)
            logger.info(f"Successfully uploaded document_id: {document_id} ({filename}, {file_size} bytes)")

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
            logger.error(f"Failed to process file upload for {filename}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save uploaded document '{filename}'."
            )

    return UploadResponse(documents=uploaded_docs)
