# ABOUTME: SQLite adapter for uploaded file data integration with LLM pipeline
# ABOUTME: Compatible interface with existing schema service for seamless CSV querying

import logging
import sqlite3
from datetime import datetime
from pathlib import Path  # noqa: TCH003
from typing import Any

from ..services.file_management import FileManager

logger = logging.getLogger(__name__)


class SQLiteSchemaError(Exception):
    """SQLite schema service specific errors"""

    pass


class SQLiteSchemaService:
    """Schema service for SQLite databases created from uploaded files"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.file_manager = FileManager()
        self._current_file_id: str | None = None
        self._current_db_path: Path | None = None

    def set_active_file(self, file_id: str) -> bool:
        """Set the active file for querying"""
        db_path = self.file_manager.get_file_database_path(self.user_id, file_id)
        if not db_path or not db_path.exists():
            return False

        self._current_file_id = file_id
        self._current_db_path = db_path
        return True

    def discover_schema(self) -> dict[str, Any]:
        """Discover schema from the active SQLite database"""
        if not self._current_db_path:
            raise SQLiteSchemaError("No active file set. Please upload a file first.")

        try:
            with sqlite3.connect(self._current_db_path) as conn:
                cursor = conn.cursor()

                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                if not tables:
                    raise SQLiteSchemaError("No tables found in database")

                schema = {
                    "databases": {},
                    "metadata": {
                        "discovered_at": datetime.utcnow().isoformat(),
                        "file_id": self._current_file_id,
                        "database_path": str(self._current_db_path),
                    },
                }

                # For uploaded files, we typically have one database and schema
                db_name = self._current_db_path.stem
                schema["databases"][db_name] = {"schemas": {}}  # type: ignore[assignment]

                # Use 'main' as schema name for SQLite
                schema_name = "main"
                schema["databases"][db_name]["schemas"][schema_name] = {"tables": {}}  # type: ignore[index]

                for (table_name,) in tables:
                    # Get table info
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()

                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa: S608
                    row_count = cursor.fetchone()[0]

                    table_info = {
                        "columns": {},
                        "metadata": {"row_count": row_count, "table_type": "table"},
                    }

                    for row in columns:
                        cid, name, data_type, not_null, default_value, pk = row
                        table_info["columns"][name] = {
                            "data_type": self._map_sqlite_to_standard_type(data_type),
                            "nullable": not bool(not_null),
                            "is_primary_key": bool(pk),
                            "default_value": default_value,
                        }

                    tables_dict = schema["databases"][db_name]["schemas"][schema_name]["tables"]
                    tables_dict[table_name] = table_info

                return schema

        except sqlite3.Error as e:
            raise SQLiteSchemaError(f"Database error: {e}") from e
        except Exception as e:
            raise SQLiteSchemaError(f"Failed to discover schema: {e}") from e

    def format_schema_context(self, schema: dict[str, Any]) -> str:
        """Format schema for LLM context (compatible with existing interface)"""
        context_parts = []

        for db_name, db_info in schema.get("databases", {}).items():
            _ = db_name  # Used in context formatting
            for schema_name, schema_info in db_info.get("schemas", {}).items():
                _ = schema_name  # Used in context formatting
                for table_name, table_info in schema_info.get("tables", {}).items():
                    table_context = f"Table: {table_name}\n"
                    table_context += f"Rows: {table_info.get('metadata', {}).get('row_count', 'Unknown')}\n"
                    table_context += "Columns:\n"

                    for col_name, col_info in table_info.get("columns", {}).items():
                        nullable = (
                            "NULL" if col_info.get("nullable", True) else "NOT NULL"
                        )
                        pk = (
                            " (PRIMARY KEY)"
                            if col_info.get("is_primary_key", False)
                            else ""
                        )
                        table_context += f"  - {col_name}: {col_info.get('data_type', 'TEXT')} {nullable}{pk}\n"

                    context_parts.append(table_context)

        if not context_parts:
            return "No tables available. Please upload a CSV file first."

        file_context = f"You are working with uploaded file data (File ID: {self._current_file_id}).\n\n"
        return file_context + "\n\n".join(context_parts)

    def execute_query(self, sql: str, limit: int = 500) -> dict[str, Any]:
        """Execute SQL query on the active database"""
        if not self._current_db_path:
            raise SQLiteSchemaError("No active file set. Please upload a file first.")

        # Validate query is read-only
        self._validate_readonly_query(sql)

        try:
            with sqlite3.connect(self._current_db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column name access
                cursor = conn.cursor()

                # Add LIMIT if not present
                sql_with_limit = self._add_limit_to_query(sql, limit)

                start_time = datetime.utcnow()
                cursor.execute(sql_with_limit)
                results = cursor.fetchall()
                end_time = datetime.utcnow()

                # Convert to list of dictionaries
                rows = [dict(row) for row in results]

                # Get column information
                columns = []
                if cursor.description:
                    for desc in cursor.description:
                        columns.append(
                            {
                                "name": desc[0],
                                "type": "TEXT",  # SQLite doesn't provide detailed type info in cursor
                            }
                        )

                return {
                    "rows": rows,
                    "columns": columns,
                    "row_count": len(rows),
                    "execution_time_ms": int(
                        (end_time - start_time).total_seconds() * 1000
                    ),
                    "query": sql_with_limit,
                    "metadata": {
                        "file_id": self._current_file_id,
                        "database": self._current_db_path.stem,
                        "limited": limit < len(rows) if results else False,
                    },
                }

        except sqlite3.Error as e:
            raise SQLiteSchemaError(f"Query execution failed: {e}") from e
        except Exception as e:
            raise SQLiteSchemaError(
                f"Unexpected error during query execution: {e}"
            ) from e

    def _validate_readonly_query(self, sql: str) -> None:
        """Validate that SQL query is read-only"""
        sql_upper = sql.upper().strip()

        # Allowed statements
        allowed_statements = ["SELECT", "WITH"]

        # Check if query starts with allowed statement
        if not any(sql_upper.startswith(stmt) for stmt in allowed_statements):
            raise SQLiteSchemaError("Only SELECT and WITH statements are allowed")

        # Blocked keywords that might modify data
        blocked_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "CREATE",
            "ALTER",
            "TRUNCATE",
            "REPLACE",
            "PRAGMA",
            "ATTACH",
            "DETACH",
        ]

        for keyword in blocked_keywords:
            if keyword in sql_upper:
                raise SQLiteSchemaError(
                    f"Statement contains blocked keyword: {keyword}"
                )

    def _add_limit_to_query(self, sql: str, limit: int) -> str:
        """Add LIMIT clause to query if not present"""
        sql_upper = sql.upper().strip()

        # If query already has LIMIT, don't modify
        if "LIMIT" in sql_upper:
            return sql

        # Add LIMIT clause
        return f"{sql.rstrip(';')} LIMIT {limit}"

    def _map_sqlite_to_standard_type(self, sqlite_type: str) -> str:
        """Map SQLite type to standard SQL type"""
        type_mapping = {
            "INTEGER": "INTEGER",
            "REAL": "DECIMAL",
            "TEXT": "VARCHAR",
            "BLOB": "BLOB",
            "NUMERIC": "DECIMAL",
        }

        sqlite_type_upper = sqlite_type.upper()
        return type_mapping.get(sqlite_type_upper, "VARCHAR")

    def get_current_file_info(self) -> dict[str, Any] | None:
        """Get information about the currently active file"""
        if not self._current_file_id:
            return None

        return self.file_manager.get_file_info(self.user_id, self._current_file_id)

    def list_available_files(self) -> list[dict[str, Any]]:
        """List all available files for the user"""
        return self.file_manager.list_user_files(self.user_id)

    def test_connection(self) -> dict[str, Any]:
        """Test connection to the active database"""
        if not self._current_db_path or not self._current_db_path.exists():
            return {
                "status": "error",
                "message": "No active file set or file not found",
            }

        try:
            with sqlite3.connect(self._current_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return {
                "status": "success",
                "message": "Connection successful",
                "file_id": self._current_file_id,
                "database_path": str(self._current_db_path),
            }

        except Exception as e:
            return {"status": "error", "message": f"Connection failed: {e}"}
