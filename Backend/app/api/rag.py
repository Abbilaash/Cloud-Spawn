import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.rag import RAGSearchRequest, RAGSearchResponse, RAGSearchResultItem
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG Search Engine"])

@router.post("/search", response_model=RAGSearchResponse, status_code=status.HTTP_200_OK)
async def search_rag_context(request: RAGSearchRequest):
    """API endpoint for Kubernetes clusters, external microservices, and AI clients
    to perform vector similarity search over indexed knowledge base documents.
    
    Accepts a user text query string and returns top matching document text snippets,
    filenames, chunk IDs, and similarity scores.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    try:
        top_k = request.top_k or 5
        search_results = rag_service.search_context(query=request.query.strip(), top_k=top_k)
        
        items = [
            RAGSearchResultItem(
                chunk_id=res["chunk_id"],
                document_id=res["document_id"],
                filename=res["filename"],
                chunk_index=res["chunk_index"],
                text=res["text"],
                score=res["score"]
            )
            for res in search_results
        ]

        return RAGSearchResponse(
            query=request.query.strip(),
            top_k=top_k,
            total_matches=len(items),
            results=items
        )
    except Exception as e:
        logger.error(f"Error executing RAG search query '{request.query}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute RAG search: {str(e)}"
        )
