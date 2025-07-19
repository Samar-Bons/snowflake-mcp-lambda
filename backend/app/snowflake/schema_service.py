# ABOUTME: Snowflake schema discovery and query execution service
# ABOUTME: Provides metadata extraction and secure read-only query execution

import re
from dataclasses import dataclass
from typing import Any

import snowflake.connector

from app.config import Settings


class SchemaServiceError(Exception):
    """Custom exception for schema service errors."""

    pass


@dataclass
class ColumnInfo:
    """Information about a database column."""

    name: str
    data_type: str
    is_nullable: bool
    comment: str | None = None


@dataclass
class TableInfo:
    """Information about a database table."""

    name: str
    columns: list[ColumnInfo]
    comment: str | None = None


@dataclass
class DatabaseSchema:
    """Complete database schema information."""

    database: str
    schema_name: str
    tables: list[TableInfo]


class SchemaService:
    """Service for Snowflake schema discovery and query execution."""

    def __init__(self, settings: Settings) -> None:
        """Initialize schema service with Snowflake configuration.

        Args:
            settings: Application settings containing Snowflake configuration

        Raises:
            SchemaServiceError: If required credentials are missing
        """
        self.settings = settings

        # Validate required credentials
        required_fields = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_SCHEMA",
        ]

        missing_fields = []
        for field in required_fields:
            if not getattr(settings, field):
                missing_fields.append(field)

        if missing_fields:
            raise SchemaServiceError(
                f"Missing required Snowflake credentials: {', '.join(missing_fields)}"
            )

        self.account = settings.SNOWFLAKE_ACCOUNT
        self.user = settings.SNOWFLAKE_USER
        self.password = settings.SNOWFLAKE_PASSWORD
        self.warehouse = settings.SNOWFLAKE_WAREHOUSE
        self.database = settings.SNOWFLAKE_DATABASE
        self.schema = settings.SNOWFLAKE_SCHEMA
        self.role = settings.SNOWFLAKE_ROLE
        self.query_timeout = settings.SNOWFLAKE_QUERY_TIMEOUT
        self.max_rows = settings.SNOWFLAKE_MAX_ROWS

    def _get_connection(self) -> Any:
        """Get Snowflake connection.

        Returns:
            Snowflake connection object

        Raises:
            SchemaServiceError: If connection fails
        """
        try:
            connection_params = {
                "account": self.account,
                "user": self.user,
                "password": self.password,
                "warehouse": self.warehouse,
                "database": self.database,
                "schema": self.schema,
            }

            if self.role:
                connection_params["role"] = self.role

            return snowflake.connector.connect(**connection_params)

        except Exception as e:
            raise SchemaServiceError(f"Failed to connect to Snowflake: {e!s}") from e

    def validate_connection(self) -> bool:
        """Validate Snowflake connection.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
            finally:
                conn.close()
        except Exception:
            return False

    def discover_schema(self) -> DatabaseSchema:
        """Discover schema information from Snowflake.

        Returns:
            DatabaseSchema object with complete schema information

        Raises:
            SchemaServiceError: If schema discovery fails
        """
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Get all tables in the schema
                tables_query = """
                    SELECT table_name, comment
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """
                cursor.execute(tables_query, (self.schema.upper(),))
                table_rows = cursor.fetchall()

                tables = []
                for table_name, table_comment in table_rows:
                    # Get columns for this table
                    columns_query = """
                        SELECT column_name, data_type, is_nullable, comment
                        FROM information_schema.columns
                        WHERE table_schema = %s AND table_name = %s
                        ORDER BY ordinal_position
                    """
                    cursor.execute(columns_query, (self.schema.upper(), table_name))
                    column_rows = cursor.fetchall()

                    columns = []
                    for col_name, col_type, nullable, col_comment in column_rows:
                        is_nullable = nullable.upper() == "YES"
                        columns.append(
                            ColumnInfo(
                                name=col_name,
                                data_type=col_type,
                                is_nullable=is_nullable,
                                comment=col_comment,
                            )
                        )

                    tables.append(
                        TableInfo(
                            name=table_name, columns=columns, comment=table_comment
                        )
                    )

                return DatabaseSchema(
                    database=self.database, schema_name=self.schema, tables=tables
                )
            finally:
                conn.close()

        except Exception as e:
            raise SchemaServiceError(f"Failed to discover schema: {e!s}") from e

    def format_schema_context(self, schema: DatabaseSchema) -> str:
        """Format schema information for LLM context.

        Args:
            schema: DatabaseSchema object to format

        Returns:
            Formatted schema context string
        """
        lines = [
            f"Database: {schema.database}",
            f"Schema: {schema.schema_name}",
            "",
            "Tables:",
        ]

        for table in schema.tables:
            lines.append(f"\nTable: {table.name}")
            if table.comment:
                lines.append(f"  Description: {table.comment}")

            lines.append("  Columns:")
            for column in table.columns:
                nullable_str = "NULLABLE" if column.is_nullable else "NOT NULL"
                col_line = f"    {column.name} ({column.data_type}, {nullable_str})"
                if column.comment:
                    col_line += f" - {column.comment}"
                lines.append(col_line)

        return "\n".join(lines)

    def execute_query(self, sql_query: str) -> dict[str, Any]:
        """Execute a read-only SQL query.

        Args:
            sql_query: SQL query to execute (must be SELECT only)

        Returns:
            Dictionary with query results including columns, rows, and metadata

        Raises:
            SchemaServiceError: If query is invalid or execution fails
        """
        # Validate that query is read-only
        self._validate_query(sql_query)

        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # Set query timeout
                cursor.execute(
                    f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {self.query_timeout}"
                )

                # Execute the query
                cursor.execute(sql_query)

                # Get column names
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )

                # Fetch results with row limit
                all_rows = cursor.fetchall()

                # Apply row limit and check for truncation
                truncated = len(all_rows) > self.max_rows
                rows = all_rows[: self.max_rows]

                return {
                    "columns": columns,
                    "rows": [list(row) for row in rows],
                    "row_count": len(rows),
                    "truncated": truncated,
                }
            finally:
                conn.close()

        except Exception as e:
            raise SchemaServiceError(f"Failed to execute query: {e!s}") from e

    def _validate_query(self, sql_query: str) -> None:
        """Validate that SQL query is safe and read-only.

        Args:
            sql_query: SQL query to validate

        Raises:
            SchemaServiceError: If query is invalid or not allowed
        """
        if not sql_query or sql_query.strip() == "":
            raise SchemaServiceError("Query cannot be empty")

        # Normalize query for validation
        normalized_query = sql_query.strip().upper()

        # Check that it starts with SELECT
        if not normalized_query.startswith("SELECT"):
            raise SchemaServiceError(
                "Only SELECT queries are allowed. Query must start with SELECT."
            )

        # Check for dangerous keywords that shouldn't be in SELECT queries
        dangerous_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
            "CALL",
            "MERGE",
            "COPY",
        ]

        for keyword in dangerous_keywords:
            if re.search(r"\b" + keyword + r"\b", normalized_query):
                raise SchemaServiceError(
                    f"Only SELECT queries are allowed. Found prohibited keyword: {keyword}"
                )
