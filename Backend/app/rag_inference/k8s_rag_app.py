import os
import logging
import requests
from flask import Flask, request, jsonify, Response, stream_with_context
from groq import Groq

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("rag-inference-k8s")

app = Flask(__name__)

# Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY")
BACKEND_RAG_URL = os.environ.get("BACKEND_RAG_URL", "http://cloudspawn-backend-service:8000/api/rag/search")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)


def fetch_rag_context(query: str, top_k: int = 5):
    """Sends HTTP POST request to CloudSpawn Backend RAG Search API to retrieve top matched document snippets."""
    try:
        logger.info(f"Fetching RAG vector context for query: '{query}' from '{BACKEND_RAG_URL}'")
        res = requests.post(
            BACKEND_RAG_URL,
            json={"query": query, "top_k": top_k},
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            logger.info(f"Retrieved {len(results)} matching RAG context snippet(s).")
            return results
        else:
            logger.warning(f"RAG search API returned status {res.status_code}: {res.text}")
            return []
    except Exception as e:
        logger.error(f"Failed to fetch RAG context from backend: {e}")
        return []


@app.route("/health", methods=["GET"])
def health_check():
    """Kubernetes Liveness and Readiness Probe endpoint."""
    return jsonify({"status": "ok", "service": "cloudspawn-rag-inference-k8s"}), 200


@app.route("/chat", methods=["POST"])
def chat():
    """RAG Inference endpoint using Flask & Groq API.
    
    Accepts JSON body: {"query": "user question string", "top_k": 5}
    1. Fetches RAG document context from CloudSpawn backend search API.
    2. Builds grounded context prompt.
    3. Executes Groq API chat completion and returns generated answer.
    """
    body = request.get_json(silent=True) or {}
    user_query = body.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query string is required"}), 400

    top_k = body.get("top_k", 5)

    # 1. Fetch RAG Context
    context_items = fetch_rag_context(user_query, top_k=top_k)

    context_blocks = []
    sources = []
    for item in context_items:
        filename = item.get("filename", "unknown")
        snippet = item.get("text", "")
        chunk_idx = item.get("chunk_index", 0)
        context_blocks.append(f"--- Document: {filename} (Chunk #{chunk_idx}) ---\n{snippet}")
        sources.append({
            "document_id": item.get("document_id"),
            "filename": filename,
            "chunk_index": chunk_idx,
            "score": item.get("score", 0.0)
        })

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant document context found."

    # 2. Construct Prompt for Groq LLM
    system_prompt = (
        "You are CloudSpawn Grounded RAG Assistant. "
        "Answer the user's question using ONLY the provided document context below. "
        "If the answer cannot be determined from the context, state clearly that the answer is not available in the documents."
    )
    user_prompt = f"Retrieved Context:\n{context_str}\n\nUser Question:\n{user_query}"

    # 3. Call Groq API
    try:
        logger.info(f"Calling Groq API (Model: {GROQ_MODEL})...")
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=False,
            stop=None
        )

        answer = completion.choices[0].message.content or ""

        return jsonify({
            "query": user_query,
            "answer": answer,
            "sources": sources,
            "total_sources": len(sources)
        }), 200

    except Exception as err:
        logger.error(f"Groq API Error: {err}", exc_info=True)
        return jsonify({"error": f"Failed to generate completion from Groq API: {str(err)}"}), 500


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Streaming RAG Inference endpoint using Flask & Groq API.
    
    Streams response chunks directly to user/client.
    """
    body = request.get_json(silent=True) or {}
    user_query = body.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query string is required"}), 400

    context_items = fetch_rag_context(user_query, top_k=body.get("top_k", 5))
    context_blocks = [f"--- Document: {i.get('filename')} ---\n{i.get('text')}" for i in context_items]
    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant document context found."

    system_prompt = "You are CloudSpawn Grounded RAG Assistant. Answer using ONLY the provided context."
    user_prompt = f"Retrieved Context:\n{context_str}\n\nUser Question:\n{user_query}"

    try:
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1,
            max_completion_tokens=2048,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None
        )

        def generate():
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield content

        return Response(stream_with_context(generate()), mimetype="text/plain")

    except Exception as err:
        logger.error(f"Groq Streaming Error: {err}", exc_info=True)
        return jsonify({"error": str(err)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Kubernetes RAG Inference Flask Service on port {port}...")
    app.run(host="0.0.0.0", port=port)
