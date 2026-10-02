import os
import json
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from groq import Groq

app = FastAPI(title="CloudSpawn Local RAG Chatbot Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are CloudSpawn Copilot — an intelligent grounded AI assistant.
CloudSpawn is a system that discovers, indexes, and orchestrates RAG document knowledge bases across Kubernetes clusters.

You will be given a CONTEXT block containing real-time document data retrieved from the CloudSpawn system.
Use this data to answer questions accurately. If the data doesn't contain the answer, say so clearly.

Format your responses using markdown when helpful:
- Use **bold** for emphasis on important values
- Use bullet lists for listing multiple items
- Use code blocks for technical details like document IDs or file paths
- Use tables when comparing multiple documents

Be concise, accurate, and helpful. Always refer to the live data from the CONTEXT block.
"""

class ChatRequest(BaseModel):
    text: str
    context: Optional[str] = "No additional context provided."

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "cloudspawn-rag-chatbot"}

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key or groq_key == "YOUR_GROQ_API_KEY":
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured.")
    
    user_context = payload.context.strip() if payload.context else ""

    context_block = f"""
=== LIVE CLOUDSPAWN RAG CONTEXT ===
{user_context}
===================================
"""
    try:
        client = Groq(api_key=groq_key)
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context_block},
                    {"role": "user", "content": payload.text}
                ],
                temperature=0.3,
                max_completion_tokens=2048,
                stream=False,
            )
        except Exception as first_err:
            print(f"[Chatbot] Fallback to llama3-8b-8192 due to: {first_err}")
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context_block},
                    {"role": "user", "content": payload.text}
                ],
                temperature=0.3,
                max_completion_tokens=2048,
                stream=False,
            )
        answer = completion.choices[0].message.content or ""
        return ChatResponse(response=answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

if __name__ == "__main__":
    print("Starting CloudSpawn RAG Chatbot Service on port 8081...")
    uvicorn.run(app, host="127.0.0.1", port=8081)
