# ABOUTME: Tests for QueryHistory model including validation, relationships, and operations
# ABOUTME: Validates query tracking, user relationships, and execution metadata storage

from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import QueryHistory, User


class TestQueryHistoryModel:
    """Test QueryHistory model creation, validation, and constraints."""

    def test_query_history_model_required_fields(self) -> None:
        """Test that QueryHistory model has all required fields."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT * FROM users",
            execution_status="success",
        )

        # Check required fields exist
        assert hasattr(query_history, "id")
        assert hasattr(query_history, "user_id")
        assert hasattr(query_history, "natural_language_input")
        assert hasattr(query_history, "generated_sql")
        assert hasattr(query_history, "execution_status")
        assert hasattr(query_history, "execution_time_ms")
        assert hasattr(query_history, "row_count")
        assert hasattr(query_history, "query_results")
        assert hasattr(query_history, "error_message")
        assert hasattr(query_history, "is_favorite")
        assert hasattr(query_history, "custom_name")
        assert hasattr(query_history, "created_at")
        assert hasattr(query_history, "updated_at")

    def test_query_history_model_default_values(self) -> None:
        """Test that QueryHistory model has correct default values."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT * FROM users",
        )

        assert query_history.execution_status == "pending"
        assert query_history.execution_time_ms is None
        assert query_history.row_count is None
        assert query_history.query_results is None
        assert query_history.error_message is None
        assert query_history.is_favorite is False
        assert query_history.custom_name is None
        assert isinstance(query_history.id, UUID)

    def test_query_history_model_timestamps(self) -> None:
        """Test that timestamps are automatically set."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT * FROM users",
        )

        # Timestamps should be set on creation
        assert query_history.created_at is not None
        assert query_history.updated_at is not None
        assert isinstance(query_history.created_at, datetime)
        assert isinstance(query_history.updated_at, datetime)

        # Should be timezone-aware UTC
        assert query_history.created_at.tzinfo == timezone.utc
        assert query_history.updated_at.tzinfo == timezone.utc

    def test_query_history_execution_status_validation(self) -> None:
        """Test execution status field validation."""
        # Valid statuses should work
        valid_statuses = ["pending", "success", "failed", "cancelled"]

        for status in valid_statuses:
            query_history = QueryHistory(
                user_id=UUID("12345678-1234-5678-1234-567812345678"),
                natural_language_input="Show me all users",
                generated_sql="SELECT * FROM users",
                execution_status=status,
            )
            assert query_history.execution_status == status

    def test_query_history_json_storage(self) -> None:
        """Test that query_results can store JSON data."""
        results_data = {
            "columns": ["id", "name", "email"],
            "rows": [
                [1, "Alice", "alice@example.com"],
                [2, "Bob", "bob@example.com"],
            ],
            "row_count": 2,
        }

        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT id, name, email FROM users",
            query_results=results_data,
        )

        assert query_history.query_results == results_data
        assert isinstance(query_history.query_results, dict)

    def test_query_history_execution_metadata(self) -> None:
        """Test execution metadata storage."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT * FROM users",
            execution_status="success",
            execution_time_ms=1500,
            row_count=25,
        )

        assert query_history.execution_time_ms == 1500
        assert query_history.row_count == 25

    def test_query_history_favorite_functionality(self) -> None:
        """Test favorite and custom naming functionality."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Show me all users",
            generated_sql="SELECT * FROM users",
            is_favorite=True,
            custom_name="All Users Query",
        )

        assert query_history.is_favorite is True
        assert query_history.custom_name == "All Users Query"

    @pytest.mark.asyncio
    async def test_query_history_creation_in_database(
        self, async_session: AsyncSession
    ) -> None:
        """Test creating query history in database."""
        # First create a user
        user = User(
            email="query.user@example.com",
            name="Query User",
            google_id="google_query_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create query history
        query_history = QueryHistory(
            user_id=user.id,
            natural_language_input="Show me all active users",
            generated_sql="SELECT * FROM users WHERE is_active = true",
            execution_status="success",
            execution_time_ms=850,
            row_count=15,
        )

        async_session.add(query_history)
        await async_session.commit()
        await async_session.refresh(query_history)

        # Verify query history was created
        assert query_history.id is not None
        assert isinstance(query_history.id, UUID)
        assert query_history.user_id == user.id
        assert query_history.created_at is not None
        assert query_history.updated_at is not None

    @pytest.mark.asyncio
    async def test_query_history_user_relationship(
        self, async_session: AsyncSession
    ) -> None:
        """Test relationship between QueryHistory and User."""
        # Create a user
        user = User(
            email="relationship.user@example.com",
            name="Relationship User",
            google_id="google_relationship_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create multiple query histories for the user
        query1 = QueryHistory(
            user_id=user.id,
            natural_language_input="Query 1",
            generated_sql="SELECT 1",
        )
        query2 = QueryHistory(
            user_id=user.id,
            natural_language_input="Query 2",
            generated_sql="SELECT 2",
        )

        async_session.add_all([query1, query2])
        await async_session.commit()

        # Test accessing user from query history
        result = await async_session.execute(
            select(QueryHistory).where(QueryHistory.id == query1.id)
        )
        found_query = result.scalar_one()

        # Load the user relationship
        await async_session.refresh(found_query, ["user"])
        assert found_query.user.email == "relationship.user@example.com"

    @pytest.mark.asyncio
    async def test_query_history_cascade_delete(
        self, async_session: AsyncSession
    ) -> None:
        """Test that query history is deleted when user is deleted."""
        # Create a user
        user = User(
            email="cascade.user@example.com",
            name="Cascade User",
            google_id="google_cascade_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create query history
        query_history = QueryHistory(
            user_id=user.id,
            natural_language_input="Test query",
            generated_sql="SELECT * FROM test",
        )
        async_session.add(query_history)
        await async_session.commit()

        query_id = query_history.id

        # Delete the user
        await async_session.delete(user)
        await async_session.commit()

        # Verify query history was also deleted
        result = await async_session.execute(
            select(QueryHistory).where(QueryHistory.id == query_id)
        )
        found_query = result.scalar_one_or_none()
        assert found_query is None

    @pytest.mark.asyncio
    async def test_query_history_foreign_key_constraint(
        self, async_session: AsyncSession
    ) -> None:
        """Test that foreign key constraint is enforced."""
        # Try to create query history with non-existent user
        query_history = QueryHistory(
            user_id=UUID("99999999-9999-9999-9999-999999999999"),
            natural_language_input="Test query",
            generated_sql="SELECT * FROM test",
        )

        async_session.add(query_history)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_query_history_updated_at_changes(
        self, async_session: AsyncSession
    ) -> None:
        """Test that updated_at changes when query history is modified."""
        # Create a user
        user = User(
            email="update.user@example.com",
            name="Update User",
            google_id="google_update_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create query history
        query_history = QueryHistory(
            user_id=user.id,
            natural_language_input="Original query",
            generated_sql="SELECT * FROM original",
        )
        async_session.add(query_history)
        await async_session.commit()
        await async_session.refresh(query_history)

        original_updated_at = query_history.updated_at

        # Modify query history
        query_history.execution_status = "success"
        query_history.execution_time_ms = 1000
        await async_session.commit()
        await async_session.refresh(query_history)

        # updated_at should have changed
        assert query_history.updated_at > original_updated_at

    @pytest.mark.asyncio
    async def test_query_history_filtering_by_status(
        self, async_session: AsyncSession
    ) -> None:
        """Test filtering query history by execution status."""
        # Create a user
        user = User(
            email="filter.user@example.com",
            name="Filter User",
            google_id="google_filter_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create query histories with different statuses
        queries = [
            QueryHistory(
                user_id=user.id,
                natural_language_input="Success query",
                generated_sql="SELECT 1",
                execution_status="success",
            ),
            QueryHistory(
                user_id=user.id,
                natural_language_input="Failed query",
                generated_sql="SELECT invalid",
                execution_status="failed",
            ),
            QueryHistory(
                user_id=user.id,
                natural_language_input="Pending query",
                generated_sql="SELECT 2",
                execution_status="pending",
            ),
        ]

        async_session.add_all(queries)
        await async_session.commit()

        # Filter by success status
        result = await async_session.execute(
            select(QueryHistory).where(
                QueryHistory.user_id == user.id,
                QueryHistory.execution_status == "success",
            )
        )
        success_queries = result.scalars().all()
        assert len(success_queries) == 1
        assert success_queries[0].natural_language_input == "Success query"

    @pytest.mark.asyncio
    async def test_query_history_favorites_filtering(
        self, async_session: AsyncSession
    ) -> None:
        """Test filtering query history by favorite status."""
        # Create a user
        user = User(
            email="favorite.user@example.com",
            name="Favorite User",
            google_id="google_favorite_user",
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create query histories with different favorite statuses
        queries = [
            QueryHistory(
                user_id=user.id,
                natural_language_input="Favorite query",
                generated_sql="SELECT favorite",
                is_favorite=True,
            ),
            QueryHistory(
                user_id=user.id,
                natural_language_input="Regular query",
                generated_sql="SELECT regular",
                is_favorite=False,
            ),
        ]

        async_session.add_all(queries)
        await async_session.commit()

        # Filter by favorite status
        result = await async_session.execute(
            select(QueryHistory).where(
                QueryHistory.user_id == user.id,
                QueryHistory.is_favorite == True,  # noqa: E712
            )
        )
        favorite_queries = result.scalars().all()
        assert len(favorite_queries) == 1
        assert favorite_queries[0].natural_language_input == "Favorite query"

    def test_query_history_repr(self) -> None:
        """Test QueryHistory model string representation."""
        query_history = QueryHistory(
            user_id=UUID("12345678-1234-5678-1234-567812345678"),
            natural_language_input="Test query",
            generated_sql="SELECT * FROM test",
            execution_status="success",
        )

        repr_str = repr(query_history)
        assert "QueryHistory" in repr_str
        assert str(query_history.id) in repr_str
        assert str(query_history.user_id) in repr_str
        assert "success" in repr_str
