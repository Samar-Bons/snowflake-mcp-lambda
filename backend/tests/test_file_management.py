# ABOUTME: Comprehensive tests for file management service functionality
# ABOUTME: Tests session-based storage, Redis integration, and cleanup utilities

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import redis

from app.services.file_management import FileManager


class TestFileManager:
    """Test file management and session-based storage"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        mock = MagicMock(spec=redis.Redis)
        return mock

    @pytest.fixture
    def file_manager_with_redis(self, mock_redis):
        """Create FileManager with mocked Redis"""
        return FileManager(redis_client=mock_redis)

    @pytest.fixture
    def file_manager_without_redis(self):
        """Create FileManager without Redis (file-based storage)"""
        with patch("app.services.file_management.FileManager._get_redis_client", return_value=None):
            return FileManager()

    @pytest.fixture
    def sample_file_info(self):
        """Create sample file metadata"""
        return {
            "filename": "sales_data.csv",
            "database_path": "/tmp/data_chat_files/user123/file456.db",
            "schema": {
                "table_name": "sales_data",
                "row_count": 1000,
                "columns": [
                    {"name": "id", "data_type": "INTEGER"},
                    {"name": "product", "data_type": "TEXT"},
                    {"name": "revenue", "data_type": "REAL"}
                ]
            }
        }

    def test_init_with_redis(self, mock_redis):
        """Test initialization with Redis client"""
        fm = FileManager(redis_client=mock_redis)
        assert fm.redis_client == mock_redis
        assert fm.base_dir.exists()
        assert fm.file_expiry_hours == 24
        assert fm.metadata_key_prefix == "file_metadata:"

    def test_init_without_redis(self):
        """Test initialization without Redis (fallback to file storage)"""
        with patch("app.services.file_management.FileManager._get_redis_client", return_value=None):
            fm = FileManager()
            assert fm.redis_client is None
            assert fm.base_dir.exists()

    def test_get_redis_client_success(self):
        """Test successful Redis client retrieval"""
        mock_redis = MagicMock()
        with patch("app.core.database.get_redis_client", return_value=mock_redis):
            fm = FileManager()
            assert fm.redis_client == mock_redis

    def test_get_redis_client_failure(self):
        """Test Redis client retrieval failure"""
        with patch("app.core.database.get_redis_client", side_effect=Exception("Redis error")):
            fm = FileManager()
            assert fm.redis_client is None

    def test_get_user_dir(self, file_manager_with_redis):
        """Test user directory creation"""
        user_id = "test_user_123"
        user_dir = file_manager_with_redis.get_user_dir(user_id)

        assert user_dir.exists()
        assert user_dir.is_dir()
        assert user_dir.name == user_id
        assert user_dir.parent == file_manager_with_redis.base_dir

    def test_get_user_db_path(self, file_manager_with_redis):
        """Test database path generation"""
        user_id = "test_user"
        file_id = "file_123"
        db_path = file_manager_with_redis.get_user_db_path(user_id, file_id)

        expected_path = file_manager_with_redis.base_dir / user_id / f"{file_id}.db"
        assert db_path == expected_path

    def test_store_file_info_with_redis(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test storing file info with Redis"""
        user_id = "user123"
        file_id = "file456"

        # Mock Redis setex to succeed
        mock_redis.setex.return_value = True

        result = file_manager_with_redis.store_file_info(user_id, file_id, sample_file_info)

        assert result is True

        # Verify Redis was called correctly
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args

        # Check key
        assert call_args[0][0] == f"file_metadata:{user_id}:{file_id}"

        # Check expiry time
        assert isinstance(call_args[0][1], timedelta)
        assert call_args[0][1] == timedelta(hours=24)

        # Check stored data
        stored_data = json.loads(call_args[0][2])
        assert stored_data["filename"] == sample_file_info["filename"]
        assert "created_at" in stored_data
        assert "expires_at" in stored_data

    def test_store_file_info_without_redis(self, file_manager_without_redis, sample_file_info):
        """Test storing file info with file-based storage"""
        user_id = "user123"
        file_id = "file456"

        result = file_manager_without_redis.store_file_info(user_id, file_id, sample_file_info)

        assert result is True

        # Verify file was created
        metadata_file = file_manager_without_redis.get_user_dir(user_id) / f"{file_id}_metadata.json"
        assert metadata_file.exists()

        # Verify content
        with open(metadata_file) as f:
            stored_data = json.load(f)

        assert stored_data["filename"] == sample_file_info["filename"]
        assert "created_at" in stored_data
        assert "expires_at" in stored_data

        # Cleanup
        metadata_file.unlink()

    def test_store_file_info_redis_error(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test handling Redis errors during store"""
        mock_redis.setex.side_effect = Exception("Redis error")

        result = file_manager_with_redis.store_file_info("user123", "file456", sample_file_info)

        assert result is False

    def test_get_file_info_with_redis(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test retrieving file info from Redis"""
        user_id = "user123"
        file_id = "file456"

        # Add timestamps to match stored format
        sample_file_info["created_at"] = datetime.utcnow().isoformat()
        sample_file_info["expires_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()

        mock_redis.get.return_value = json.dumps(sample_file_info)

        result = file_manager_with_redis.get_file_info(user_id, file_id)

        assert result is not None
        assert result["filename"] == sample_file_info["filename"]
        mock_redis.get.assert_called_once_with(f"file_metadata:{user_id}:{file_id}")

    def test_get_file_info_not_found(self, file_manager_with_redis, mock_redis):
        """Test retrieving non-existent file info"""
        mock_redis.get.return_value = None

        result = file_manager_with_redis.get_file_info("user123", "nonexistent")

        assert result is None

    def test_get_file_info_without_redis(self, file_manager_without_redis, sample_file_info):
        """Test retrieving file info from file storage"""
        user_id = "user123"
        file_id = "file456"

        # Store file first
        file_manager_without_redis.store_file_info(user_id, file_id, sample_file_info)

        # Retrieve it
        result = file_manager_without_redis.get_file_info(user_id, file_id)

        assert result is not None
        assert result["filename"] == sample_file_info["filename"]

        # Cleanup
        metadata_file = file_manager_without_redis.get_user_dir(user_id) / f"{file_id}_metadata.json"
        metadata_file.unlink()

    def test_get_file_info_expired_file(self, file_manager_without_redis, sample_file_info):
        """Test retrieving expired file info"""
        user_id = "user123"
        file_id = "file456"

        # Create expired file metadata
        sample_file_info["created_at"] = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        sample_file_info["expires_at"] = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        # Write directly to avoid validation
        metadata_file = file_manager_without_redis.get_user_dir(user_id) / f"{file_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(sample_file_info, f)

        # Create dummy db file
        db_path = file_manager_without_redis.get_user_db_path(user_id, file_id)
        db_path.touch()

        # Try to retrieve - should return None and clean up
        result = file_manager_without_redis.get_file_info(user_id, file_id)

        assert result is None
        assert not metadata_file.exists()
        assert not db_path.exists()

    def test_delete_file_with_redis(self, file_manager_with_redis, mock_redis):
        """Test deleting file with Redis"""
        user_id = "user123"
        file_id = "file456"

        # Create dummy db file
        db_path = file_manager_with_redis.get_user_db_path(user_id, file_id)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.touch()

        result = file_manager_with_redis.delete_file(user_id, file_id)

        assert result is True
        assert not db_path.exists()
        mock_redis.delete.assert_called_once_with(f"file_metadata:{user_id}:{file_id}")

    def test_delete_file_without_redis(self, file_manager_without_redis, sample_file_info):
        """Test deleting file with file-based storage"""
        user_id = "user123"
        file_id = "file456"

        # Store file first
        file_manager_without_redis.store_file_info(user_id, file_id, sample_file_info)

        # Create dummy db file
        db_path = file_manager_without_redis.get_user_db_path(user_id, file_id)
        db_path.touch()

        # Delete
        result = file_manager_without_redis.delete_file(user_id, file_id)

        assert result is True

        # Verify deletion
        metadata_file = file_manager_without_redis.get_user_dir(user_id) / f"{file_id}_metadata.json"
        assert not metadata_file.exists()
        assert not db_path.exists()

    def test_delete_file_error_handling(self, file_manager_with_redis, mock_redis):
        """Test delete file error handling"""
        mock_redis.delete.side_effect = Exception("Redis error")

        # Should still return False on error
        result = file_manager_with_redis.delete_file("user123", "file456")
        assert result is False

    def test_list_user_files_with_redis(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test listing user files with Redis"""
        user_id = "user123"

        # Mock Redis scan_iter to return keys
        mock_redis.scan_iter.return_value = [
            f"file_metadata:{user_id}:file1",
            f"file_metadata:{user_id}:file2"
        ]

        # Mock get to return file info
        sample_file_info["created_at"] = datetime.utcnow().isoformat()
        sample_file_info["expires_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()

        file_info_1 = sample_file_info.copy()
        file_info_1["filename"] = "file1.csv"

        file_info_2 = sample_file_info.copy()
        file_info_2["filename"] = "file2.csv"
        file_info_2["created_at"] = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        mock_redis.get.side_effect = [
            json.dumps(file_info_1),
            json.dumps(file_info_2)
        ]

        result = file_manager_with_redis.list_user_files(user_id)

        assert len(result) == 2
        # Should be sorted by creation time (newest first)
        assert result[0]["filename"] == "file1.csv"
        assert result[1]["filename"] == "file2.csv"
        assert result[0]["file_id"] == "file1"
        assert result[1]["file_id"] == "file2"

    def test_list_user_files_without_redis(self, file_manager_without_redis, sample_file_info):
        """Test listing user files with file-based storage"""
        user_id = "user123"

        # Store multiple files
        for i in range(3):
            file_id = f"file{i}"
            file_info = sample_file_info.copy()
            file_info["filename"] = f"file{i}.csv"
            file_manager_without_redis.store_file_info(user_id, file_id, file_info)

        result = file_manager_without_redis.list_user_files(user_id)

        assert len(result) == 3

        # Cleanup
        user_dir = file_manager_without_redis.get_user_dir(user_id)
        for f in user_dir.glob("*.json"):
            f.unlink()

    def test_list_user_files_empty(self, file_manager_with_redis, mock_redis):
        """Test listing files for user with no files"""
        mock_redis.scan_iter.return_value = []

        result = file_manager_with_redis.list_user_files("user123")

        assert result == []

    def test_list_user_files_error_handling(self, file_manager_with_redis, mock_redis):
        """Test error handling in list_user_files"""
        mock_redis.scan_iter.side_effect = Exception("Redis error")

        result = file_manager_with_redis.list_user_files("user123")

        # Should return empty list on error
        assert result == []

    def test_cleanup_expired_files_with_redis(self, file_manager_with_redis, mock_redis):
        """Test cleanup of expired files with Redis"""
        # Create orphaned db files
        user_dir = file_manager_with_redis.get_user_dir("user123")
        orphaned_file1 = user_dir / "orphan1.db"
        orphaned_file2 = user_dir / "orphan2.db"
        orphaned_file1.touch()
        orphaned_file2.touch()

        # Mock Redis exists to return False (no metadata)
        mock_redis.exists.return_value = False

        cleaned_count = file_manager_with_redis.cleanup_expired_files()

        assert cleaned_count == 2
        assert not orphaned_file1.exists()
        assert not orphaned_file2.exists()

    def test_cleanup_expired_files_without_redis(self, file_manager_without_redis, sample_file_info):
        """Test cleanup of expired files with file-based storage"""
        user_id = "user123"

        # Create expired file
        expired_file_id = "expired_file"
        expired_info = sample_file_info.copy()
        expired_info["created_at"] = (datetime.utcnow() - timedelta(hours=25)).isoformat()
        expired_info["expires_at"] = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        # Create valid file
        valid_file_id = "valid_file"
        valid_info = sample_file_info.copy()
        file_manager_without_redis.store_file_info(user_id, valid_file_id, valid_info)

        # Write expired file directly
        metadata_file = file_manager_without_redis.get_user_dir(user_id) / f"{expired_file_id}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(expired_info, f)

        # Create db files
        expired_db = file_manager_without_redis.get_user_db_path(user_id, expired_file_id)
        valid_db = file_manager_without_redis.get_user_db_path(user_id, valid_file_id)
        expired_db.touch()
        valid_db.touch()

        cleaned_count = file_manager_without_redis.cleanup_expired_files()

        assert cleaned_count == 1
        assert not metadata_file.exists()
        assert not expired_db.exists()
        assert valid_db.exists()  # Valid file should remain

        # Cleanup
        valid_db.unlink()
        for f in file_manager_without_redis.get_user_dir(user_id).glob("*.json"):
            f.unlink()

    def test_cleanup_expired_files_error_handling(self, file_manager_with_redis, mock_redis):
        """Test error handling in cleanup_expired_files"""
        # Mock iterdir to raise exception
        with patch.object(Path, 'iterdir', side_effect=Exception("OS error")):
            cleaned_count = file_manager_with_redis.cleanup_expired_files()

        assert cleaned_count == 0

    def test_get_file_database_path_exists(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test getting database path for existing file"""
        user_id = "user123"
        file_id = "file456"

        # Create the database file
        db_path = Path(sample_file_info["database_path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.touch()

        # Mock get_file_info
        sample_file_info["created_at"] = datetime.utcnow().isoformat()
        sample_file_info["expires_at"] = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        mock_redis.get.return_value = json.dumps(sample_file_info)

        result = file_manager_with_redis.get_file_database_path(user_id, file_id)

        assert result == db_path

        # Cleanup
        db_path.unlink()
        db_path.parent.rmdir()

    def test_get_file_database_path_not_exists(self, file_manager_with_redis, mock_redis, sample_file_info):
        """Test getting database path when file doesn't exist"""
        mock_redis.get.return_value = json.dumps(sample_file_info)

        result = file_manager_with_redis.get_file_database_path("user123", "file456")

        assert result is None

    def test_get_file_database_path_no_metadata(self, file_manager_with_redis, mock_redis):
        """Test getting database path when no metadata exists"""
        mock_redis.get.return_value = None

        result = file_manager_with_redis.get_file_database_path("user123", "nonexistent")

        assert result is None

    def test_cleanup_user_files(self, file_manager_without_redis, sample_file_info):
        """Test cleaning up all files for a user"""
        user_id = "user123"

        # Create multiple files
        file_ids = ["file1", "file2", "file3"]
        for file_id in file_ids:
            file_manager_without_redis.store_file_info(user_id, file_id, sample_file_info)
            db_path = file_manager_without_redis.get_user_db_path(user_id, file_id)
            db_path.touch()

        cleaned_count = file_manager_without_redis.cleanup_user_files(user_id)

        assert cleaned_count == 3

        # Verify all files deleted
        user_dir = file_manager_without_redis.get_user_dir(user_id)
        # The directory might still exist due to mkdir(exist_ok=True) in get_user_dir
        # but it should be empty
        if user_dir.exists():
            assert not list(user_dir.glob("*"))
        else:
            # Directory was removed - also acceptable
            assert True

    def test_cleanup_user_files_error_handling(self, file_manager_with_redis, mock_redis):
        """Test error handling in cleanup_user_files"""
        # Mock list_user_files to raise exception
        with patch.object(file_manager_with_redis, 'list_user_files', side_effect=Exception("Error")):
            cleaned_count = file_manager_with_redis.cleanup_user_files("user123")

        assert cleaned_count == 0

    def test_concurrent_file_access(self, file_manager_without_redis, sample_file_info):
        """Test handling concurrent file operations"""
        user_id = "user123"
        file_id = "file456"

        # Store file
        file_manager_without_redis.store_file_info(user_id, file_id, sample_file_info)

        # Simulate concurrent read
        result1 = file_manager_without_redis.get_file_info(user_id, file_id)
        result2 = file_manager_without_redis.get_file_info(user_id, file_id)

        assert result1 is not None
        assert result2 is not None
        assert result1["filename"] == result2["filename"]

        # Cleanup
        file_manager_without_redis.delete_file(user_id, file_id)

    def test_large_file_metadata(self, file_manager_with_redis, mock_redis):
        """Test handling large file metadata"""
        user_id = "user123"
        file_id = "large_file"

        # Create large metadata
        large_metadata = {
            "filename": "large_data.csv",
            "database_path": "/tmp/large.db",
            "schema": {
                "table_name": "large_table",
                "row_count": 1000000,
                "columns": [{"name": f"col_{i}", "data_type": "TEXT"} for i in range(100)]
            }
        }

        result = file_manager_with_redis.store_file_info(user_id, file_id, large_metadata)

        assert result is True
        mock_redis.setex.assert_called_once()

    def test_special_characters_in_filenames(self, file_manager_without_redis):
        """Test handling special characters in filenames"""
        user_id = "user123"
        file_id = "file456"

        special_metadata = {
            "filename": "sales & revenue (2024).csv",
            "database_path": "/tmp/test.db",
            "schema": {
                "table_name": "sales_revenue_2024",
                "row_count": 100,
                "columns": []
            }
        }

        result = file_manager_without_redis.store_file_info(user_id, file_id, special_metadata)
        assert result is True

        retrieved = file_manager_without_redis.get_file_info(user_id, file_id)
        assert retrieved is not None
        assert retrieved["filename"] == special_metadata["filename"]

        # Cleanup
        file_manager_without_redis.delete_file(user_id, file_id)

    def test_file_manager_with_custom_expiry(self, mock_redis):
        """Test FileManager with custom expiry settings"""
        fm = FileManager(redis_client=mock_redis)
        fm.file_expiry_hours = 48  # Override default

        sample_info = {"filename": "test.csv", "schema": {"table_name": "test", "row_count": 10}}
        fm.store_file_info("user123", "file456", sample_info)

        # Verify custom expiry was used
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == timedelta(hours=48)
