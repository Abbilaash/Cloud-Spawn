import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db_manager
from app.core.logger_handler import system_log_handler
from app.api.documents import router as documents_router
from app.api.jobs import router as jobs_router
from app.api.logs import router as logs_router
from app.api.chat import router as chat_router

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
root_logger = logging.getLogger()
root_logger.addHandler(system_log_handler)

logger = logging.getLogger("cloudspawn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CloudSpawn Backend Service...")
    yield
    logger.info("Shutting down CloudSpawn Backend Service...")
    db_manager.close()

app = FastAPI(
    title="CloudSpawn Backend API",
    description="Dynamic Serverless Task Orchestration Backend for Autonomous AI Agents",
    version="1.0.0",
    openapi_tags=[
        {"name": "Documents", "description": "DOCX/PDF Document Upload & Metadata Management"},
        {"name": "Jobs", "description": "Document Splitting & Formicx Agent Task Orchestration"},
        {"name": "System Logs", "description": "Real-time System & Formicx Agent Execution Logs"},
        {"name": "System", "description": "System Health & Operational Status"},
    ],
    lifespan=lifespan
)

# CORS Configuration
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents_router)
app.include_router(jobs_router)
app.include_router(logs_router)
app.include_router(chat_router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handle browser favicon request cleanly with 204 No Content."""
    return Response(status_code=204)

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
