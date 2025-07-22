# ABOUTME: File management utilities for session-based storage and cleanup
# ABOUTME: Handles temporary file storage, metadata tracking, and automatic cleanup

import json
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import redis

logger = logging.getLogger(__name__)


class FileManager:
    """Manages uploaded files and metadata with session-based storage"""

    def __init__(self, redis_client: redis.Redis[str] | None = None):
        self.redis_client = redis_client or self._get_redis_client()
        self.base_dir = Path(tempfile.gettempdir()) / "data_chat_files"
        self.base_dir.mkdir(exist_ok=True)

        # File expiry settings
        self.file_expiry_hours = 24  # Files expire after 24 hours
        self.metadata_key_prefix = "file_metadata:"

    def _get_redis_client(self) -> redis.Redis[str] | None:
        """Get Redis client for metadata storage"""
        try:
            # Use default Redis connection (same as sessions)
            from ..core.database import get_redis_client

            return get_redis_client()
        except Exception:
            logger.warning("Redis not available, using in-memory storage")
            return None

    def get_user_dir(self, user_id: str) -> Path:
        """Get user-specific directory for file storage"""
        user_dir = self.base_dir / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir

    def get_user_db_path(self, user_id: str, file_id: str) -> Path:
        """Get SQLite database path for user file"""
        user_dir = self.get_user_dir(user_id)
        return user_dir / f"{file_id}.db"

    def store_file_info(
        self, user_id: str, file_id: str, file_info: dict[str, Any]
    ) -> bool:
        """Store file metadata"""
        try:
            # Add timestamp for expiry tracking
            file_info["created_at"] = datetime.utcnow().isoformat()
            file_info["expires_at"] = (
                datetime.utcnow() + timedelta(hours=self.file_expiry_hours)
            ).isoformat()

            metadata_key = f"{self.metadata_key_prefix}{user_id}:{file_id}"

            if self.redis_client:
                # Store in Redis with expiry
                self.redis_client.setex(
                    metadata_key,
                    timedelta(hours=self.file_expiry_hours),
                    json.dumps(file_info),
                )
            else:
                # Fallback to file-based storage
                metadata_file = self.get_user_dir(user_id) / f"{file_id}_metadata.json"
                with open(metadata_file, "w") as f:
                    json.dump(file_info, f)

            return True

        except Exception as e:
            logger.error(f"Failed to store file info: {e}")
            return False

    def get_file_info(self, user_id: str, file_id: str) -> dict[str, Any] | None:
        """Retrieve file metadata"""
        try:
            metadata_key = f"{self.metadata_key_prefix}{user_id}:{file_id}"

            if self.redis_client:
                # Get from Redis
                data = self.redis_client.get(metadata_key)
                if data:
                    return json.loads(data)  # type: ignore[no-any-return]
            else:
                # Fallback to file-based storage
                metadata_file = self.get_user_dir(user_id) / f"{file_id}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        file_info = json.load(f)

                    # Check if expired
                    expires_at = datetime.fromisoformat(file_info["expires_at"])
                    if datetime.utcnow() > expires_at:
                        # Clean up expired file
                        self.delete_file(user_id, file_id)
                        return None

                    return file_info  # type: ignore[no-any-return]

            return None

        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None

    def delete_file(self, user_id: str, file_id: str) -> bool:
        """Delete file and associated metadata"""
        try:
            success = True

            # Delete metadata
            metadata_key = f"{self.metadata_key_prefix}{user_id}:{file_id}"

            if self.redis_client:
                self.redis_client.delete(metadata_key)
            else:
                metadata_file = self.get_user_dir(user_id) / f"{file_id}_metadata.json"
                if metadata_file.exists():
                    metadata_file.unlink()

            # Delete database file
            db_path = self.get_user_db_path(user_id, file_id)
            if db_path.exists():
                db_path.unlink()

            return success

        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    def list_user_files(self, user_id: str) -> list[dict[str, Any]]:
        """List all files for a user"""
        files = []

        try:
            if self.redis_client:
                # Get all keys for user
                pattern = f"{self.metadata_key_prefix}{user_id}:*"
                for key in self.redis_client.scan_iter(match=pattern):
                    data = self.redis_client.get(key)
                    if data:
                        file_info = json.loads(data)
                        # Ensure key is a string for split operation
                        key_str = str(key)
                        file_id = key_str.split(":")[-1]
                        files.append(
                            {
                                "file_id": file_id,
                                "filename": file_info["filename"],
                                "created_at": file_info["created_at"],
                                "row_count": file_info["schema"]["row_count"],
                                "table_name": file_info["schema"]["table_name"],
                            }
                        )
            else:
                # Fallback to file scanning
                user_dir = self.get_user_dir(user_id)
                for metadata_file in user_dir.glob("*_metadata.json"):
                    try:
                        with open(metadata_file) as f:
                            file_info = json.load(f)

                        # Check if expired
                        expires_at = datetime.fromisoformat(file_info["expires_at"])
                        if datetime.utcnow() > expires_at:
                            continue

                        file_id = metadata_file.stem.replace("_metadata", "")
                        files.append(
                            {
                                "file_id": file_id,
                                "filename": file_info["filename"],
                                "created_at": file_info["created_at"],
                                "row_count": file_info["schema"]["row_count"],
                                "table_name": file_info["schema"]["table_name"],
                            }
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to read metadata file {metadata_file}: {e}"
                        )

        except Exception as e:
            logger.error(f"Failed to list user files: {e}")

        # Sort by creation time (newest first)
        files.sort(key=lambda x: x["created_at"], reverse=True)
        return files

    def cleanup_expired_files(self) -> int:
        """Clean up expired files across all users"""
        cleaned_count = 0

        try:
            if self.redis_client:
                # Redis handles expiry automatically, but clean up orphaned files
                for user_dir in self.base_dir.iterdir():
                    if not user_dir.is_dir():
                        continue

                    for db_file in user_dir.glob("*.db"):
                        file_id = db_file.stem
                        metadata_key = (
                            f"{self.metadata_key_prefix}{user_dir.name}:{file_id}"
                        )

                        # If no metadata exists, file is orphaned
                        if not self.redis_client.exists(metadata_key):
                            db_file.unlink()
                            cleaned_count += 1
                            logger.info(f"Cleaned up orphaned file: {db_file}")

            else:
                # Manual cleanup for file-based storage
                current_time = datetime.utcnow()

                for user_dir in self.base_dir.iterdir():
                    if not user_dir.is_dir():
                        continue

                    for metadata_file in user_dir.glob("*_metadata.json"):
                        try:
                            with open(metadata_file) as f:
                                file_info = json.load(f)

                            expires_at = datetime.fromisoformat(file_info["expires_at"])
                            if current_time > expires_at:
                                file_id = metadata_file.stem.replace("_metadata", "")
                                if self.delete_file(user_dir.name, file_id):
                                    cleaned_count += 1
                                    logger.info(f"Cleaned up expired file: {file_id}")

                        except Exception as e:
                            logger.warning(
                                f"Error processing metadata file {metadata_file}: {e}"
                            )

        except Exception as e:
            logger.error(f"Cleanup operation failed: {e}")

        return cleaned_count

    def get_file_database_path(self, user_id: str, file_id: str) -> Path | None:
        """Get database path for file if it exists"""
        file_info = self.get_file_info(user_id, file_id)
        if not file_info:
            return None

        db_path = Path(file_info["database_path"])
        return db_path if db_path.exists() else None

    def cleanup_user_files(self, user_id: str) -> int:
        """Clean up all files for a specific user"""
        cleaned_count = 0

        try:
            user_files = self.list_user_files(user_id)
            for file_info in user_files:
                if self.delete_file(user_id, file_info["file_id"]):
                    cleaned_count += 1

            # Remove empty user directory
            user_dir = self.get_user_dir(user_id)
            if user_dir.exists() and not any(user_dir.iterdir()):
                user_dir.rmdir()

        except Exception as e:
            logger.error(f"Failed to cleanup user files: {e}")

        return cleaned_count
