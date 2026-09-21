import logging
from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    _client: MongoClient | None = None
    _db: Database | None = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            logger.info(f"[MongoDB] Opening MongoDB connection at {settings.MONGODB_URI}...")
            cls._client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            logger.info("[MongoDB] MongoDB connection established successfully.")
        return cls._client

    @classmethod
    def get_db(cls) -> Database:
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_DATABASE]
            logger.info(f"[MongoDB] Selected database: '{settings.MONGODB_DATABASE}'")
        return cls._db

    @classmethod
    def get_documents_collection(cls):
        return cls.get_db()["documents"]

    @classmethod
    def get_jobs_collection(cls):
        return cls.get_db()["jobs"]

    @classmethod
    def get_conversations_collection(cls):
        return cls.get_db()["conversations"]

    @classmethod
    def close(cls):
        if cls._client is not None:
            logger.info("[MongoDB] Closing MongoDB client connection...")
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("[MongoDB] MongoDB connection closed.")

db_manager = DatabaseManager

