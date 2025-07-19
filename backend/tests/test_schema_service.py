# ABOUTME: Tests for Snowflake schema discovery service
# ABOUTME: Tests metadata extraction, connection management, and schema caching

from unittest.mock import Mock, patch

import pytest

from app.config import Settings
from app.snowflake.schema_service import (
    ColumnInfo,
    DatabaseSchema,
    SchemaService,
    SchemaServiceError,
    TableInfo,
)


class TestSchemaService:
    """Test suite for Snowflake schema discovery service."""

    @pytest.fixture
    def mock_settings(self) -> Settings:
        """Create mock settings for testing."""
        settings = Settings()
        settings.SNOWFLAKE_ACCOUNT = "test_account"
        settings.SNOWFLAKE_USER = "test_user"
        settings.SNOWFLAKE_PASSWORD = "test_password"
        settings.SNOWFLAKE_WAREHOUSE = "test_warehouse"
        settings.SNOWFLAKE_DATABASE = "test_database"
        settings.SNOWFLAKE_SCHEMA = "test_schema"
        settings.SNOWFLAKE_ROLE = "test_role"
        settings.SNOWFLAKE_QUERY_TIMEOUT = 300
        settings.SNOWFLAKE_MAX_ROWS = 500
        return settings

    @pytest.fixture
    def schema_service(self, mock_settings: Settings) -> SchemaService:
        """Create SchemaService instance for testing."""
        with patch("app.snowflake.schema_service.snowflake.connector.connect"):
            return SchemaService(settings=mock_settings)

    def test_schema_service_initialization(self, mock_settings: Settings) -> None:
        """Test that SchemaService initializes correctly."""
        with patch("app.snowflake.schema_service.snowflake.connector.connect"):
            service = SchemaService(settings=mock_settings)

        assert service.settings == mock_settings
        assert service.account == "test_account"
        assert service.user == "test_user"
        assert service.warehouse == "test_warehouse"
        assert service.database == "test_database"
        assert service.schema == "test_schema"

    def test_schema_service_initialization_missing_credentials(self) -> None:
        """Test that SchemaService raises error when credentials are missing."""
        settings = Settings()
        settings.SNOWFLAKE_ACCOUNT = ""

        with pytest.raises(SchemaServiceError) as exc_info:
            SchemaService(settings=settings)

        assert "Missing required Snowflake credentials" in str(exc_info.value)

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_get_connection_success(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test successful Snowflake connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        connection = schema_service._get_connection()

        assert connection == mock_connection
        mock_connect.assert_called_once_with(
            account="test_account",
            user="test_user",
            password="test_password",
            warehouse="test_warehouse",
            database="test_database",
            schema="test_schema",
            role="test_role",
        )

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_get_connection_failure(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test Snowflake connection failure."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(SchemaServiceError) as exc_info:
            schema_service._get_connection()

        assert "Failed to connect to Snowflake" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)

    def test_column_info_creation(self) -> None:
        """Test ColumnInfo dataclass creation."""
        column = ColumnInfo(
            name="customer_id",
            data_type="NUMBER",
            is_nullable=False,
            comment="Primary key for customer table",
        )

        assert column.name == "customer_id"
        assert column.data_type == "NUMBER"
        assert column.is_nullable is False
        assert column.comment == "Primary key for customer table"

    def test_table_info_creation(self) -> None:
        """Test TableInfo dataclass creation."""
        columns = [
            ColumnInfo("id", "NUMBER", False, "Primary key"),
            ColumnInfo("name", "VARCHAR", True, "Customer name"),
        ]

        table = TableInfo(
            name="customers", columns=columns, comment="Customer information table"
        )

        assert table.name == "customers"
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[1].name == "name"
        assert table.comment == "Customer information table"

    def test_database_schema_creation(self) -> None:
        """Test DatabaseSchema dataclass creation."""
        tables = [
            TableInfo("customers", [], "Customer data"),
            TableInfo("orders", [], "Order data"),
        ]

        schema = DatabaseSchema(database="test_db", schema_name="public", tables=tables)

        assert schema.database == "test_db"
        assert schema.schema_name == "public"
        assert len(schema.tables) == 2
        assert schema.tables[0].name == "customers"
        assert schema.tables[1].name == "orders"

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_discover_schema_success(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test successful schema discovery."""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock table discovery query results
        mock_cursor.fetchall.side_effect = [
            # Tables query result
            [
                ("customers", "Customer information table"),
                ("orders", "Order information table"),
            ],
            # Columns query result for customers table
            [
                ("id", "NUMBER", "NO", "Customer ID"),
                ("name", "VARCHAR", "YES", "Customer name"),
                ("email", "VARCHAR", "YES", "Customer email"),
            ],
            # Columns query result for orders table
            [
                ("id", "NUMBER", "NO", "Order ID"),
                ("customer_id", "NUMBER", "NO", "Customer reference"),
                ("amount", "NUMBER", "YES", "Order amount"),
            ],
        ]

        result = schema_service.discover_schema()

        assert isinstance(result, DatabaseSchema)
        assert result.database == "test_database"
        assert result.schema_name == "test_schema"
        assert len(result.tables) == 2

        # Check customers table
        customers_table = result.tables[0]
        assert customers_table.name == "customers"
        assert customers_table.comment == "Customer information table"
        assert len(customers_table.columns) == 3
        assert customers_table.columns[0].name == "id"
        assert customers_table.columns[0].data_type == "NUMBER"
        assert customers_table.columns[0].is_nullable is False

        # Check orders table
        orders_table = result.tables[1]
        assert orders_table.name == "orders"
        assert orders_table.comment == "Order information table"
        assert len(orders_table.columns) == 3

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_discover_schema_connection_error(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test schema discovery with connection error."""
        mock_connect.side_effect = Exception("Database error")

        with pytest.raises(SchemaServiceError) as exc_info:
            schema_service.discover_schema()

        assert "Failed to discover schema" in str(exc_info.value)
        assert "Database error" in str(exc_info.value)

    def test_format_schema_context(self, schema_service: SchemaService) -> None:
        """Test schema context formatting for LLM."""
        # Create test schema
        customers_columns = [
            ColumnInfo("id", "NUMBER", False, "Customer ID"),
            ColumnInfo("name", "VARCHAR", True, "Customer name"),
            ColumnInfo("email", "VARCHAR", True, "Customer email"),
        ]
        orders_columns = [
            ColumnInfo("id", "NUMBER", False, "Order ID"),
            ColumnInfo("customer_id", "NUMBER", False, "Customer reference"),
            ColumnInfo("amount", "NUMBER", True, "Order amount"),
        ]

        schema = DatabaseSchema(
            database="test_db",
            schema_name="public",
            tables=[
                TableInfo("customers", customers_columns, "Customer data"),
                TableInfo("orders", orders_columns, "Order data"),
            ],
        )

        context = schema_service.format_schema_context(schema)

        assert "Database: test_db" in context
        assert "Schema: public" in context
        assert "Table: customers" in context
        assert "Table: orders" in context
        assert "id (NUMBER, NOT NULL)" in context
        assert "name (VARCHAR, NULLABLE)" in context
        assert "Customer data" in context
        assert "Order data" in context

    def test_validate_connection_success(self, schema_service: SchemaService) -> None:
        """Test connection validation success."""
        with patch.object(schema_service, "_get_connection") as mock_get_conn:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            mock_get_conn.return_value = mock_connection

            result = schema_service.validate_connection()

            assert result is True
            mock_cursor.execute.assert_called_once_with("SELECT 1")

    def test_validate_connection_failure(self, schema_service: SchemaService) -> None:
        """Test connection validation failure."""
        with patch.object(schema_service, "_get_connection") as mock_get_conn:
            mock_get_conn.side_effect = Exception("Connection failed")

            result = schema_service.validate_connection()

            assert result is False

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_execute_query_success(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test successful query execution."""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock query results
        mock_cursor.description = [
            ("id", None, None, None, None, None, None),
            ("name", None, None, None, None, None, None),
        ]
        mock_cursor.fetchall.return_value = [
            (1, "John Doe"),
            (2, "Jane Smith"),
        ]

        sql_query = "SELECT id, name FROM customers LIMIT 2"
        result = schema_service.execute_query(sql_query)

        assert "columns" in result
        assert "rows" in result
        assert "row_count" in result
        assert "truncated" in result

        assert result["columns"] == ["id", "name"]
        assert len(result["rows"]) == 2
        assert result["rows"][0] == [1, "John Doe"]
        assert result["rows"][1] == [2, "Jane Smith"]
        assert result["row_count"] == 2
        assert result["truncated"] is False

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_execute_query_with_truncation(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test query execution with result truncation."""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mock query results (more than max_rows)
        mock_cursor.description = [("id", None, None, None, None, None, None)]
        mock_rows = [(i,) for i in range(600)]  # More than default 500 limit
        mock_cursor.fetchall.return_value = mock_rows

        sql_query = "SELECT id FROM large_table"
        result = schema_service.execute_query(sql_query)

        assert result["row_count"] == 500  # Should be truncated
        assert result["truncated"] is True
        assert len(result["rows"]) == 500

    def test_execute_query_invalid_sql(self, schema_service: SchemaService) -> None:
        """Test query execution with invalid SQL."""
        sql_query = "INSERT INTO customers VALUES (1, 'test')"

        with pytest.raises(SchemaServiceError) as exc_info:
            schema_service.execute_query(sql_query)

        assert "Only SELECT queries are allowed" in str(exc_info.value)

    @patch("app.snowflake.schema_service.snowflake.connector.connect")
    def test_execute_query_database_error(
        self, mock_connect: Mock, schema_service: SchemaService
    ) -> None:
        """Test query execution with database error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        mock_cursor.execute.side_effect = Exception("SQL error")

        sql_query = "SELECT * FROM non_existent_table"

        with pytest.raises(SchemaServiceError) as exc_info:
            schema_service.execute_query(sql_query)

        assert "Failed to execute query" in str(exc_info.value)
        assert "SQL error" in str(exc_info.value)
