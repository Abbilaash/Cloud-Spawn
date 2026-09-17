import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = Field(default="mongodb://localhost:27017")
    MONGODB_DATABASE: str = Field(default="cloudspawn")
    
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./data/chroma")
    
    LLM_API_KEY: str = Field(default="")
    LLM_MODEL: str = Field(default="gpt-4o-mini")
    LLM_BASE_URL: str = Field(default="https://api.openai.com/v1")
    
    UPLOAD_DIRECTORY: str = Field(default="./data/uploads")
    CORS_ORIGINS: str = Field(default="http://localhost:3000")
    
    EMBEDDING_MODEL_NAME: str = Field(default="all-MiniLM-L6-v2")
    TOP_K_CHUNKS: int = Field(default=5)
    
    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["http://localhost:3000"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
