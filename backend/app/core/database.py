# ABOUTME: Database management with SQLAlchemy and connection pooling
# ABOUTME: Handles database connections, health checks, and pool monitoring

import logging
import time
from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import redis

if TYPE_CHECKING:
    # Type hint for modern Redis versions with generics
    RedisType = redis.Redis[str]
else:
    # Runtime compatibility for all Redis versions
    RedisType = redis.Redis
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from app.config import Settings

logger = logging.getLogger(__name__)


def get_engine(settings: Settings) -> Engine:
    """
    Create and configure SQLAlchemy engine with connection pooling.

    Args:
        settings: Application settings containing database configuration

    Returns:
        Configured SQLAlchemy engine
    """
    logger.info(
        f"Creating database engine with pool_size={settings.DB_POOL_SIZE}, "
        f"timeout={settings.DB_POOL_TIMEOUT}, echo={settings.DB_ECHO_SQL}"
    )

    # Parse SSL mode for connection URL
    ssl_params = {}
    if settings.DB_SSL_MODE != "disable":
        ssl_params["sslmode"] = settings.DB_SSL_MODE

    # Add SSL parameters to URL if needed
    database_url = settings.DATABASE_URL
    if ssl_params:
        # Add SSL parameters to the URL
        separator = "&" if "?" in database_url else "?"
        ssl_string = "&".join(f"{k}={v}" for k, v in ssl_params.items())
        database_url = f"{database_url}{separator}{ssl_string}"

    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Validate connections before use
        echo=settings.DB_ECHO_SQL,
    )

    logger.info("Database engine created successfully")
    return engine


def check_database_health(engine: Engine) -> dict[str, Any]:
    """
    Check database health by executing a simple query.

    Args:
        engine: SQLAlchemy engine to test

    Returns:
        Dict containing health status information
    """
    start_time = time.time()

    try:
        with engine.connect() as connection:
            # Simple query to test connectivity
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        logger.debug(f"Database health check successful in {response_time:.2f}ms")

        return {
            "status": "healthy",
            "connected": True,
            "response_time_ms": round(response_time, 2),
        }

    except SQLAlchemyError as e:
        response_time = (time.time() - start_time) * 1000
        error_msg = str(e)

        logger.error(f"Database health check failed: {error_msg}")

        return {
            "status": "unhealthy",
            "connected": False,
            "error": error_msg,
            "response_time_ms": round(response_time, 2),
        }


def get_database_status(engine: Engine) -> dict[str, Any]:
    """
    Get detailed database status including pool information.

    Args:
        engine: SQLAlchemy engine to check

    Returns:
        Dict containing detailed database status
    """
    # Get basic health status
    health_status = check_database_health(engine)

    # Get pool statistics
    pool = engine.pool
    pool_info = {
        "size": getattr(pool, "size", lambda: 0)(),
        "checked_in": getattr(pool, "checkedin", lambda: 0)(),
        "checked_out": getattr(pool, "checkedout", lambda: 0)(),
        "overflow": getattr(pool, "overflow", lambda: 0)(),
        "total_connections": getattr(pool, "checkedin", lambda: 0)()
        + getattr(pool, "checkedout", lambda: 0)(),
    }

    return {
        **health_status,
        "pool_info": pool_info,
    }


class DatabaseManager:
    """
    Manages database connections and provides health monitoring.
    """

    def __init__(self, settings: Settings):
        """
        Initialize database manager with settings.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.engine = get_engine(settings)
        logger.info("DatabaseManager initialized")

    def health_check(self) -> dict[str, Any]:
        """
        Perform database health check.

        Returns:
            Dict containing health status
        """
        return check_database_health(self.engine)

    def get_status(self) -> dict[str, Any]:
        """
        Get detailed database status.

        Returns:
            Dict containing detailed status information
        """
        return get_database_status(self.engine)

    def close(self) -> None:
        """
        Close database connections and dispose of engine.
        """
        logger.info("Closing database connections")
        self.engine.dispose()


# Global database manager instance
_database_manager: DatabaseManager | None = None

# Global Redis client
_redis_client: RedisType | None = None


def get_redis_client() -> RedisType | None:
    """
    Get or create global Redis client instance.

    Returns:
        Redis client instance or None if connection fails
    """
    global _redis_client  # noqa: PLW0603

    if _redis_client is None:
        try:
            from app.config import get_settings

            settings = get_settings()
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection
            if _redis_client:
                _redis_client.ping()
                logger.info("Redis client connected successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            return None

    return _redis_client


def get_database_manager() -> DatabaseManager:
    """
    Get or create global database manager instance.

    Returns:
        DatabaseManager instance
    """
    global _database_manager  # noqa: PLW0603

    if _database_manager is None:
        from app.config import get_settings

        settings = get_settings()
        _database_manager = DatabaseManager(settings)

    return _database_manager


def get_database_session() -> Generator[Session, None, None]:
    """
    Get database session from the global database manager.

    Yields:
        SQLAlchemy Session object
    """
    manager = get_database_manager()
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=manager.engine)

    session = session_local()
    try:
        yield session
    finally:
        session.close()
