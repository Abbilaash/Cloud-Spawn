# CloudSpawn Backend — Local RAG & Task Orchestration Interface

CloudSpawn is a research/coursework system exploring **dynamic serverless task orchestration for autonomous AI agents**.

> [!NOTE]
> **Phase 1 Status**: This initial version delivers a clean, modular **Local RAG (Retrieval-Augmented Generation) Backend**. The document processing and job execution interfaces are abstracts designed to seamlessly integrate with the **Formicx agent-native runtime** and **AWS Lambda** in future phases.

---

## 1. Project Description

CloudSpawn allows users to upload `.docx` research documents, extract text, chunk and index them into a vector database (ChromaDB), and execute grounded RAG queries via an LLM. Application metadata, background jobs, and conversation history are persisted in MongoDB.

---

## 2. Project Directory Structure & File Overview

```text
Backend/
│
├── app/
│   ├── main.py                          # FastAPI app entry point, CORS configuration, health check endpoint, and API router registration.
│   │
│   ├── api/                             # API Request Handlers & Routes
│   │   ├── documents.py                 # Handles DOCX file upload, file validation, disk storage, and MongoDB document metadata creation.
│   │   ├── jobs.py                      # Handles triggering knowledge base build background tasks and polling ingestion job progress.
│   │   └── chat.py                      # Handles executing RAG Q&A queries and retrieving complete conversation history.
│   │
│   ├── core/                            # Application Core & Database Setup
│   │   ├── config.py                    # Loads central environment settings via Pydantic BaseSettings from .env.
│   │   └── database.py                  # Manages PyMongo connection client and provides handles for MongoDB collections.
│   │
│   ├── models/                          # MongoDB Document Data Structures
│   │   ├── document.py                  # Defines document status constants and document metadata dictionary generator.
│   │   ├── job.py                       # Defines job status constants and background build job metadata dictionary generator.
│   │   └── chat.py                      # Defines conversation history and chat message model dictionary generators.
│   │
│   ├── schemas/                         # Pydantic Request & Response Schemas
│   │   ├── document.py                  # Pydantic models for upload file responses and document list items.
│   │   ├── job.py                       # Pydantic models for build job requests, trigger responses, and status progress details.
│   │   └── chat.py                      # Pydantic models for RAG chat requests, answers with sources, and conversation history.
│   │
│   └── services/                        # Business Logic & External Integrations
│       ├── document_service.py          # Abstract processing interface and local python-docx text extraction and chunking implementation.
│       ├── embedding_service.py         # Generates vector embeddings for text and document chunks using SentenceTransformers (all-MiniLM-L6-v2).
│       ├── vector_service.py            # Manages persistent ChromaDB vector store for chunk insertion, deletion, and similarity search.
│       ├── job_service.py               # Executes background ingestion workflow (extraction, embedding, vector storage, and status updates).
│       └── rag_service.py               # Coordinates end-to-end RAG pipeline (retrieval, prompt construction, LLM completion, and history tracking).
│
├── data/                                # Storage Directory
│   ├── uploads/                         # Directory storing raw uploaded DOCX files.
│   └── chroma/                          # Persistence directory storing local ChromaDB vector database index files.
│
├── .env                                 # Environment variables for database URIs, API keys, and server settings.
├── .env.example                         # Environment configuration template file.
├── requirements.txt                     # List of Python dependencies required for the backend service.
└── README.md                            # Comprehensive project documentation and API guide.
```

---

## 3. Requirements

* **Python**: 3.11 or higher
* **Database**: MongoDB (local or MongoDB Atlas)
* **Vector Store**: ChromaDB (locally persisted at `./data/chroma`)
* **Key Dependencies**: `fastapi`, `uvicorn`, `pymongo`, `chromadb`, `sentence-transformers`, `python-docx`, `pydantic-settings`, `openai`

---

## 4. Environment Setup

Copy `.env.example` to `.env` and fill in your settings:

```bash
cp .env.example .env
```

Configuration parameters:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=cloudspawn

CHROMA_PERSIST_DIRECTORY=./data/chroma

LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

UPLOAD_DIRECTORY=./data/uploads
CORS_ORIGINS=http://localhost:3000

EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
TOP_K_CHUNKS=5
```

---

## 5. Installation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

---

## 6. MongoDB Setup

Ensure MongoDB is running locally on port 27017, or specify a valid remote `MONGODB_URI` in `.env`:

```bash
# Example starting local MongoDB via Docker:
docker run -d -p 27017:27017 --name cloudspawn-mongo mongo:latest
```

---

## 7. Running the Backend

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
* **Server Base**: `http://localhost:8000`
* **Swagger UI Documentation**: `http://localhost:8000/docs`
* **ReDoc Documentation**: `http://localhost:8000/redoc`

---

## 8. API Endpoints

### System
* `GET /health` — Health check endpoint (`{"status": "ok", "service": "cloudspawn-backend"}`)

### Documents
* `POST /api/documents/upload` — Upload one or multiple `.docx` files.
  * **Form Data**: `files` (file list)
  * **Response**: List of document items with `document_id`, `filename`, and `status`.

### Jobs
* `POST /api/jobs/build` — Trigger background text extraction, chunking, embedding, and vector indexing.
  * **Payload**: `{"document_ids": ["doc-uuid-1", "doc-uuid-2"]}`
  * **Response**: `{"job_id": "job-uuid", "status": "queued"}`
* `GET /api/jobs/{job_id}` — Get progress and status for an ingestion job.
  * **Response**: Includes `total_documents`, `processed_documents`, `failed_documents`, `progress`, and timestamps.

### Chat
* `POST /api/chat` — Execute grounded RAG Q&A query against indexed document vectors.
  * **Payload**: `{"message": "What are the key conclusions?", "conversation_id": "optional-uuid"}`
  * **Response**: `{"conversation_id": "...", "answer": "...", "sources": [...]}`
* `GET /api/chat/{conversation_id}` — Retrieve complete message history for a conversation.

---

## 9. RAG Workflow

1. **Upload**: User uploads DOCX files via `POST /api/documents/upload`. Metadata is logged in MongoDB with status `uploaded`.
2. **Knowledge Base Build**: User calls `POST /api/jobs/build` with `document_ids`. A background job is launched.
3. **Extraction & Chunking**: `LocalDocumentProcessor` reads DOCX text using `python-docx` and chunks it into ~800-word blocks with metadata (`document_id`, `filename`, `chunk_index`).
4. **Embedding**: `EmbeddingService` generates dense vectors using `sentence-transformers` (`all-MiniLM-L6-v2`).
5. **Vector Store**: `VectorService` upserts chunks and embeddings into ChromaDB (`./data/chroma`).
6. **Query & Grounded Response**: When a user queries `/api/chat`, the query is embedded, top $K$ matching context chunks are retrieved, and a grounded prompt is sent to the LLM.

---

## 10. Future Formicx + AWS Lambda Architecture

In future releases, local background processing will be upgraded to distributed serverless agent orchestration:

```text
FastAPI API Gateway
        ↓
   Job Service
        ↓
Formicx Runtime Orchestrator
        ↓
Task Decomposition & Agent Allocation
        ↓
Formicx Worker Agents (AWS Lambda Functions)
        ↓
Parallel Document Chunking & Embedding Generation
        ↓
Vector Database & Storage
        ↓
RAG Chat Interface
```

The current service abstraction (`DocumentProcessingInterface`, `job_service.py`) ensures that replacing the local processor with Formicx orchestrators requires zero modifications to API endpoints or contracts.
