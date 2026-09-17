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
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}")
            cls._client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        return cls._client

    @classmethod
    def get_db(cls) -> Database:
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[settings.MONGODB_DATABASE]
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
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("Closed MongoDB connection.")

db_manager = DatabaseManager
