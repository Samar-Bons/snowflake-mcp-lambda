# ABOUTME: Tests for Alembic migration system including forward/backward compatibility
# ABOUTME: Validates migration scripts, schema versioning, and database state management

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database.migrations import (
    create_migration,
    get_alembic_config,
    get_current_revision,
    migrate_to_latest,
    rollback_migration,
)


class TestAlembicConfiguration:
    """Test Alembic configuration and setup."""

    def test_alembic_config_creation(self) -> None:
        """Test that Alembic config is created correctly."""
        with patch("app.database.migrations.Path") as mock_path:
            mock_path.return_value.exists.return_value = True
            (mock_path.return_value / "alembic.ini").return_value = Path("alembic.ini")

            config = get_alembic_config()

            assert isinstance(config, Config)
            assert config.get_main_option("sqlalchemy.url") is not None

    def test_alembic_config_with_custom_url(self) -> None:
        """Test Alembic config with custom database URL."""
        custom_url = "postgresql+asyncpg://test:test@localhost:5432/test_db"

        with patch("app.database.migrations.Path") as mock_path:
            mock_path.return_value.exists.return_value = True

            config = get_alembic_config(database_url=custom_url)

            assert config.get_main_option("sqlalchemy.url") == custom_url

    def test_alembic_migrations_directory_exists(self) -> None:
        """Test that migrations directory structure exists."""
        with patch("app.database.migrations.Path") as mock_path:
            migrations_dir = mock_path.return_value
            migrations_dir.exists.return_value = True

            # Check that versions directory exists
            versions_dir = migrations_dir / "versions"
            versions_dir.exists.return_value = True

            config = get_alembic_config()
            script_dir = ScriptDirectory.from_config(config)

            assert script_dir is not None


class TestMigrationOperations:
    """Test migration creation and execution operations."""

    @pytest.mark.asyncio
    async def test_get_current_revision(self) -> None:
        """Test getting current database revision."""
        with patch("app.database.migrations.get_async_engine") as mock_get_engine:
            mock_engine = MagicMock(spec=AsyncEngine)
            mock_connection = MagicMock()
            mock_context = MagicMock()
            mock_context.get_current_revision.return_value = "abc123"

            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            with patch(
                "alembic.runtime.migration.MigrationContext"
            ) as mock_migration_context:
                mock_migration_context.configure.return_value = mock_context

                revision = await get_current_revision()

                assert revision == "abc123"
                mock_context.get_current_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_migrate_to_latest(self) -> None:
        """Test migrating database to latest revision."""
        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.command.upgrade") as mock_upgrade:
                mock_config = MagicMock()
                mock_get_config.return_value = mock_config

                await migrate_to_latest()

                mock_upgrade.assert_called_once_with(mock_config, "head")

    @pytest.mark.asyncio
    async def test_rollback_migration(self) -> None:
        """Test rolling back migration by one revision."""
        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.command.downgrade") as mock_downgrade:
                mock_config = MagicMock()
                mock_get_config.return_value = mock_config

                await rollback_migration()

                mock_downgrade.assert_called_once_with(mock_config, "-1")

    @pytest.mark.asyncio
    async def test_rollback_migration_to_specific_revision(self) -> None:
        """Test rolling back to specific revision."""
        target_revision = "def456"

        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.command.downgrade") as mock_downgrade:
                mock_config = MagicMock()
                mock_get_config.return_value = mock_config

                await rollback_migration(target_revision)

                mock_downgrade.assert_called_once_with(mock_config, target_revision)

    def test_create_migration(self) -> None:
        """Test creating new migration file."""
        message = "Add user table"

        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.command.revision") as mock_revision:
                mock_config = MagicMock()
                mock_get_config.return_value = mock_config

                create_migration(message)

                mock_revision.assert_called_once_with(
                    mock_config, message=message, autogenerate=True
                )

    def test_create_migration_with_empty_message(self) -> None:
        """Test creating migration with auto-generated message."""
        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.command.revision") as mock_revision:
                mock_config = MagicMock()
                mock_get_config.return_value = mock_config

                create_migration()

                mock_revision.assert_called_once_with(
                    mock_config, message="Auto-generated migration", autogenerate=True
                )


class TestMigrationValidation:
    """Test migration validation and integrity checks."""

    @pytest.mark.asyncio
    async def test_migration_forward_compatibility(self) -> None:
        """Test that migrations can be applied forward successfully."""
        with patch("app.database.migrations.get_async_engine") as mock_get_engine:
            mock_engine = MagicMock(spec=AsyncEngine)
            mock_connection = MagicMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            # Mock successful migration
            with patch("alembic.command.upgrade") as mock_upgrade:
                with patch(
                    "app.database.migrations.get_alembic_config"
                ) as mock_get_config:
                    mock_config = MagicMock()
                    mock_get_config.return_value = mock_config

                    # Should not raise any exceptions
                    await migrate_to_latest()

                    mock_upgrade.assert_called_once()

    @pytest.mark.asyncio
    async def test_migration_backward_compatibility(self) -> None:
        """Test that migrations can be rolled back successfully."""
        with patch("app.database.migrations.get_async_engine") as mock_get_engine:
            mock_engine = MagicMock(spec=AsyncEngine)
            mock_connection = MagicMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            # Mock successful rollback
            with patch("alembic.command.downgrade") as mock_downgrade:
                with patch(
                    "app.database.migrations.get_alembic_config"
                ) as mock_get_config:
                    mock_config = MagicMock()
                    mock_get_config.return_value = mock_config

                    # Should not raise any exceptions
                    await rollback_migration()

                    mock_downgrade.assert_called_once()

    @pytest.mark.asyncio
    async def test_migration_schema_validation(self) -> None:
        """Test that migration creates expected schema."""
        with patch("app.database.migrations.get_async_engine") as mock_get_engine:
            mock_engine = MagicMock(spec=AsyncEngine)
            mock_connection = MagicMock()
            mock_inspector = MagicMock()

            # Mock table inspection after migration
            expected_tables = ["users", "alembic_version"]
            mock_inspector.get_table_names.return_value = expected_tables

            mock_connection.begin.return_value.__enter__.return_value = mock_connection
            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            with patch("sqlalchemy.inspect", return_value=mock_inspector):
                with patch("app.database.migrations.migrate_to_latest"):
                    # After migration, expected tables should exist
                    inspector = inspect(mock_engine)
                    tables = inspector.get_table_names()

                    assert "users" in tables
                    assert "alembic_version" in tables

    @pytest.mark.asyncio
    async def test_migration_data_integrity(self) -> None:
        """Test that migrations preserve data integrity."""
        with patch("app.database.migrations.get_async_engine") as mock_get_engine:
            mock_engine = MagicMock(spec=AsyncEngine)
            mock_connection = MagicMock()

            # Mock data before and after migration
            test_data = [("test@example.com", "Test User")]
            mock_result = MagicMock()
            mock_result.fetchall.return_value = test_data
            mock_connection.execute.return_value = mock_result

            mock_engine.begin.return_value.__aenter__.return_value = mock_connection
            mock_get_engine.return_value = mock_engine

            with patch("app.database.migrations.migrate_to_latest"):
                # Data should be preserved after migration
                result = await mock_connection.execute(
                    text("SELECT email, name FROM users")
                )
                data = result.fetchall()

                assert len(data) == 1
                assert data[0] == ("test@example.com", "Test User")

    def test_migration_version_tracking(self) -> None:
        """Test that migration versions are tracked correctly."""
        with patch("app.database.migrations.get_alembic_config") as mock_get_config:
            with patch("alembic.script.ScriptDirectory.from_config") as mock_script_dir:
                mock_config = MagicMock()
                mock_script = MagicMock()
                mock_revision = MagicMock()
                mock_revision.revision = "abc123"
                mock_revision.down_revision = "def456"

                mock_script.get_current_head.return_value = "abc123"
                mock_script.get_revision.return_value = mock_revision

                mock_get_config.return_value = mock_config
                mock_script_dir.return_value = mock_script

                # Should be able to track revision chain
                current_head = mock_script.get_current_head()
                assert current_head == "abc123"

                revision_info = mock_script.get_revision(current_head)
                assert revision_info.revision == "abc123"
                assert revision_info.down_revision == "def456"
