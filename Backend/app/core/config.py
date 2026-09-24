import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = Field(default="mongodb://localhost:27017")
    MONGODB_DATABASE: str = Field(default="cloudspawn")
    
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./data/chroma")
    
    GEMINI_API_KEY: str = Field(default="")
    LLM_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gemini-3.6-flash")
    LLM_BASE_URL: str = Field(default="https://generativelanguage.googleapis.com/v1beta/openai/")
    
    UPLOAD_DIRECTORY: str = Field(default="./data/uploads")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001")
    
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2")
    TOP_K_CHUNKS: int = Field(default=5)
    
    # AWS Lambda & S3 Worker Configurations
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_LAMBDA_FUNCTION_NAME: str = Field(default="cloudspawn-lambda-worker")
    AWS_S3_BUCKET_NAME: str = Field(default="cloudspawn-faiss-indexes")
    FAISS_OUTPUT_DIRECTORY: str = Field(default="./data/faiss_indexes")
    
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
