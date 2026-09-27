import os
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3StorageService:
    """Service handling document file uploads, downloads, and deletions in AWS S3."""

    def __init__(self):
        self._client = None

    def get_client(self):
        access_key = settings.s3_access_key
        secret_key = settings.s3_secret_key
        region = settings.s3_region

        if not access_key or not secret_key:
            logger.warning("[S3 Storage] AWS S3 access credentials not fully configured in settings.")
            return None

        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    "s3",
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
                logger.info(f"[S3 Storage] boto3 S3 client initialized for region '{region}'.")
            except Exception as e:
                logger.error(f"[S3 Storage] Failed to initialize boto3 S3 client: {e}", exc_info=True)
                return None

        return self._client

    def is_configured(self) -> bool:
        return bool(settings.s3_access_key and settings.s3_secret_key and settings.AWS_S3_BUCKET_NAME)

    def upload_file_bytes(self, content: bytes, s3_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """Uploads raw binary content to S3 bucket. Returns S3 URI / key on success."""
        client = self.get_client()
        bucket_name = settings.AWS_S3_BUCKET_NAME

        if not client or not bucket_name:
            logger.warning(f"[S3 Storage] S3 client or bucket name missing. Skipping S3 upload for key '{s3_key}'.")
            return None

        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=content,
                **extra_args
            )
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            logger.info(f"[S3 Storage] Successfully uploaded {len(content)} bytes to '{s3_uri}'.")
            return s3_uri
        except Exception as e:
            logger.error(f"[S3 Storage] Failed to upload object '{s3_key}' to S3 bucket '{bucket_name}': {e}", exc_info=True)
            return None

    def upload_file_from_disk(self, local_path: str, s3_key: str) -> Optional[str]:
        """Uploads a local file from disk to S3 bucket."""
        if not os.path.exists(local_path):
            logger.error(f"[S3 Storage] File not found at local path: '{local_path}'")
            return None

        with open(local_path, "rb") as f:
            content = f.read()

        return self.upload_file_bytes(content=content, s3_key=s3_key)

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """Downloads an object from S3 bucket to a local file path."""
        client = self.get_client()
        bucket_name = settings.AWS_S3_BUCKET_NAME

        if not client or not bucket_name:
            return False

        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            client.download_file(bucket_name, s3_key, local_path)
            logger.info(f"[S3 Storage] Downloaded '{s3_key}' from S3 bucket '{bucket_name}' to '{local_path}'.")
            return True
        except Exception as e:
            logger.error(f"[S3 Storage] Failed to download '{s3_key}' from S3 bucket '{bucket_name}': {e}")
            return False

    def delete_file(self, s3_key: str) -> bool:
        """Deletes a single object from S3 bucket."""
        client = self.get_client()
        bucket_name = settings.AWS_S3_BUCKET_NAME

        if not client or not bucket_name:
            return False

        try:
            client.delete_object(Bucket=bucket_name, Key=s3_key)
            logger.info(f"[S3 Storage] Deleted object '{s3_key}' from S3 bucket '{bucket_name}'.")
            return True
        except Exception as e:
            logger.warning(f"[S3 Storage] Failed to delete object '{s3_key}' from S3 bucket '{bucket_name}': {e}")
            return False

    def purge_bucket(self) -> int:
        """Deletes all objects stored in the configured S3 bucket."""
        client = self.get_client()
        bucket_name = settings.AWS_S3_BUCKET_NAME

        if not client or not bucket_name:
            return 0

        try:
            deleted_count = 0
            paginator = client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name):
                if "Contents" in page:
                    delete_keys = [{"Key": obj["Key"]} for obj in page["Contents"]]
                    client.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_keys})
                    deleted_count += len(delete_keys)

            logger.info(f"[S3 Storage] Purged {deleted_count} object(s) from S3 bucket '{bucket_name}'.")
            return deleted_count
        except Exception as e:
            logger.warning(f"[S3 Storage] Notice during S3 bucket purge: {e}")
            return 0

s3_service = S3StorageService()
