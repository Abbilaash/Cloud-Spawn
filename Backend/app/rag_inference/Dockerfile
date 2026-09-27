# Dockerfile for CloudSpawn Kubernetes RAG Inference Microservice
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application script
COPY k8s_rag_app.py .

# Expose Flask port
EXPOSE 5000

# Environment variables (overridable in Kubernetes manifest)
ENV PORT=5000
ENV GROQ_API_KEY="YOUR_GROQ_API_KEY"
ENV BACKEND_RAG_URL="http://cloudspawn-backend-service:8000/api/rag/search"
ENV GROQ_MODEL="openai/gpt-oss-120b"

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "k8s_rag_app.py"]
