# ABOUTME: Database models and SQLAlchemy configuration for PostgreSQL
# ABOUTME: Manages user data, query history, and application state persistence

# Core models
from .models import Base, QueryHistory, User

# Configuration classes
from .config import DatabaseConfig, RedisConfig

# Connection management
from .connections import get_async_engine, get_redis_client

# Session management
from .session import (
    DatabaseSessionManager,
    cleanup_database,
    get_async_session,
    get_session_manager,
    initialize_database,
)

# Migration utilities
from .migrations import (
    create_migration,
    get_alembic_config,
    get_current_revision,
    initialize_migrations,
    migrate_to_latest,
    rollback_migration,
    validate_migration_state,
)

__all__ = [
    # Models
    "Base",
    "User",
    "QueryHistory",
    # Configuration
    "DatabaseConfig",
    "RedisConfig",
    # Connections
    "get_async_engine",
    "get_redis_client",
    # Session management
    "DatabaseSessionManager",
    "get_session_manager",
    "get_async_session",
    "initialize_database",
    "cleanup_database",
    # Migrations
    "get_alembic_config",
    "create_migration",
    "migrate_to_latest",
    "rollback_migration",
    "get_current_revision",
    "initialize_migrations",
    "validate_migration_state",
]
