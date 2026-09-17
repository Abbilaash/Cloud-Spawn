import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db_manager
from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.api.chat import router as chat_router

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cloudspawn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CloudSpawn Backend Service...")
    yield
    logger.info("Shutting down CloudSpawn Backend Service...")
    db_manager.close()

app = FastAPI(
    title="CloudSpawn Backend API",
    description="Dynamic Serverless Task Orchestration RAG Backend for Autonomous AI Agents",
    version="1.0.0",
    openapi_tags=[
        {"name": "Documents", "description": "DOCX Document Upload & Metadata Management"},
        {"name": "Jobs", "description": "Knowledge Base Ingestion & Background Task Orchestration"},
        {"name": "Chat", "description": "RAG Q&A Interaction & Conversation Tracking"},
        {"name": "System", "description": "System Health & Operational Status"},
    ],
    lifespan=lifespan
)

# CORS Configuration
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents_router)
app.include_router(jobs_router)
app.include_router(chat_router)

@app.get("/health", tags=["System"], status_code=status.HTTP_200_OK)
async def health_check():
    """System health check endpoint."""
    return {
        "status": "ok",
        "service": "cloudspawn-backend"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
