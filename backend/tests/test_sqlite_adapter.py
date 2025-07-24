# ABOUTME: Comprehensive tests for SQLite adapter functionality
# ABOUTME: Tests schema discovery, query execution, and security validation

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.data.sqlite_adapter import SQLiteSchemaError, SQLiteSchemaService


class TestSQLiteSchemaService:
    """Test SQLite schema service for uploaded file data"""

    @pytest.fixture
    def mock_file_manager(self):
        """Mock file manager with test database paths"""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def service(self, mock_file_manager):
        """Create service instance with mocked file manager"""
        with patch("app.data.sqlite_adapter.FileManager", return_value=mock_file_manager):
            return SQLiteSchemaService("test-user-123")

    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database with test data"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        # Create test tables and data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create customers table
        cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                revenue REAL,
                created_at TEXT
            )
        """)

        # Insert test data
        test_data = [
            (1, "John Doe", "john@example.com", 1500.50, "2024-01-01"),
            (2, "Jane Smith", "jane@example.com", 2500.75, "2024-01-02"),
            (3, "Bob Johnson", None, 1000.00, "2024-01-03"),
        ]
        cursor.executemany(
            "INSERT INTO customers (id, name, email, revenue, created_at) VALUES (?, ?, ?, ?, ?)",
            test_data
        )

        # Create orders table
        cursor.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                amount REAL,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        db_path.unlink(missing_ok=True)

    def test_init(self, service):
        """Test service initialization"""
        assert service.user_id == "test-user-123"
        assert service._current_file_id is None
        assert service._current_db_path is None

    def test_set_active_file_success(self, service, mock_file_manager, temp_db):
        """Test setting active file successfully"""
        mock_file_manager.get_file_database_path.return_value = temp_db

        result = service.set_active_file("file-123")

        assert result is True
        assert service._current_file_id == "file-123"
        assert service._current_db_path == temp_db
        mock_file_manager.get_file_database_path.assert_called_once_with("test-user-123", "file-123")

    def test_set_active_file_not_found(self, service, mock_file_manager):
        """Test setting active file when database doesn't exist"""
        mock_file_manager.get_file_database_path.return_value = None

        result = service.set_active_file("file-123")

        assert result is False
        assert service._current_file_id is None

    def test_discover_schema_success(self, service, mock_file_manager, temp_db):
        """Test successful schema discovery"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        schema = service.discover_schema()

        # Verify schema structure
        assert "databases" in schema
        assert "metadata" in schema
        assert schema["metadata"]["file_id"] == "file-123"

        # Get database name from path
        db_name = temp_db.stem
        assert db_name in schema["databases"]

        # Check tables
        tables = schema["databases"][db_name]["schemas"]["main"]["tables"]
        assert "customers" in tables
        assert "orders" in tables

        # Check customers table columns
        customers = tables["customers"]
        assert customers["metadata"]["row_count"] == 3
        assert "id" in customers["columns"]
        assert customers["columns"]["id"]["is_primary_key"] is True
        assert customers["columns"]["name"]["nullable"] is False
        assert customers["columns"]["email"]["nullable"] is True

    def test_discover_schema_no_active_file(self, service):
        """Test schema discovery without active file"""
        with pytest.raises(SQLiteSchemaError, match="No active file set"):
            service.discover_schema()

    def test_discover_schema_empty_database(self, service, mock_file_manager):
        """Test schema discovery on empty database"""
        # Create empty database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            empty_db = Path(tmp.name)

        try:
            conn = sqlite3.connect(empty_db)
            conn.close()

            mock_file_manager.get_file_database_path.return_value = empty_db
            service.set_active_file("empty-file")

            with pytest.raises(SQLiteSchemaError, match="No tables found"):
                service.discover_schema()

        finally:
            empty_db.unlink(missing_ok=True)

    def test_format_schema_context(self, service, mock_file_manager, temp_db):
        """Test formatting schema for LLM context"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        schema = service.discover_schema()
        context = service.format_schema_context(schema)

        assert "File ID: file-123" in context
        assert "Table: customers" in context
        assert "Rows: 3" in context
        # SQLite primary keys allow NULL by default unless explicitly NOT NULL
        assert "- id: INTEGER NULL (PRIMARY KEY)" in context
        assert "- name: VARCHAR NOT NULL" in context
        assert "Table: orders" in context

    def test_format_schema_context_empty(self, service):
        """Test formatting empty schema"""
        context = service.format_schema_context({})
        assert context == "No tables available. Please upload a CSV file first."

    def test_execute_query_success(self, service, mock_file_manager, temp_db):
        """Test successful query execution"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        result = service.execute_query("SELECT * FROM customers WHERE revenue > 1500")

        assert result["row_count"] == 2
        assert len(result["rows"]) == 2
        assert result["rows"][0]["name"] == "John Doe"
        assert result["rows"][1]["name"] == "Jane Smith"
        assert result["metadata"]["file_id"] == "file-123"
        assert result["execution_time_ms"] >= 0

    def test_execute_query_with_limit(self, service, mock_file_manager, temp_db):
        """Test query execution with automatic limit"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        result = service.execute_query("SELECT * FROM customers", limit=2)

        assert result["row_count"] == 2
        assert "LIMIT 2" in result["query"]

    def test_execute_query_existing_limit(self, service, mock_file_manager, temp_db):
        """Test query with existing LIMIT clause"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        result = service.execute_query("SELECT * FROM customers LIMIT 1")

        assert result["row_count"] == 1
        assert result["query"].count("LIMIT") == 1

    def test_execute_query_no_active_file(self, service):
        """Test query execution without active file"""
        with pytest.raises(SQLiteSchemaError, match="No active file set"):
            service.execute_query("SELECT 1")

    def test_execute_query_readonly_validation(self, service, mock_file_manager, temp_db):
        """Test read-only query validation"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        # Test blocked statements
        blocked_queries = [
            "INSERT INTO customers (name) VALUES ('test')",
            "UPDATE customers SET name = 'test'",
            "DELETE FROM customers",
            "DROP TABLE customers",
            "CREATE TABLE new_table (id INT)",
            "ALTER TABLE customers ADD COLUMN test TEXT",
            "TRUNCATE TABLE customers",
            "PRAGMA table_info(customers)",
        ]

        for query in blocked_queries:
            with pytest.raises(SQLiteSchemaError):
                service.execute_query(query)

    def test_execute_query_with_cte(self, service, mock_file_manager, temp_db):
        """Test query with Common Table Expression (WITH clause)"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        query = """
        WITH high_revenue AS (
            SELECT * FROM customers WHERE revenue > 1500
        )
        SELECT name FROM high_revenue
        """

        result = service.execute_query(query)
        assert result["row_count"] == 2

    def test_execute_query_sql_injection_attempt(self, service, mock_file_manager, temp_db):
        """Test SQL injection prevention"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        # Attempt SQL injection
        with pytest.raises(SQLiteSchemaError):
            service.execute_query("SELECT * FROM customers; DROP TABLE customers;")

    def test_map_sqlite_to_standard_type(self, service):
        """Test SQLite type mapping"""
        assert service._map_sqlite_to_standard_type("INTEGER") == "INTEGER"
        assert service._map_sqlite_to_standard_type("REAL") == "DECIMAL"
        assert service._map_sqlite_to_standard_type("TEXT") == "VARCHAR"
        assert service._map_sqlite_to_standard_type("BLOB") == "BLOB"
        assert service._map_sqlite_to_standard_type("NUMERIC") == "DECIMAL"
        assert service._map_sqlite_to_standard_type("UNKNOWN") == "VARCHAR"
        assert service._map_sqlite_to_standard_type("text") == "VARCHAR"  # Case insensitive

    def test_get_current_file_info(self, service, mock_file_manager):
        """Test getting current file information"""
        # No active file
        assert service.get_current_file_info() is None

        # With active file
        service._current_file_id = "file-123"
        mock_file_manager.get_file_info.return_value = {"id": "file-123", "name": "test.csv"}

        info = service.get_current_file_info()
        assert info == {"id": "file-123", "name": "test.csv"}
        mock_file_manager.get_file_info.assert_called_once_with("test-user-123", "file-123")

    def test_list_available_files(self, service, mock_file_manager):
        """Test listing available files"""
        mock_files = [
            {"id": "file-1", "name": "data1.csv"},
            {"id": "file-2", "name": "data2.csv"},
        ]
        mock_file_manager.list_user_files.return_value = mock_files

        files = service.list_available_files()
        assert files == mock_files
        mock_file_manager.list_user_files.assert_called_once_with("test-user-123")

    def test_test_connection_success(self, service, mock_file_manager, temp_db):
        """Test successful connection test"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        result = service.test_connection()

        assert result["status"] == "success"
        assert result["file_id"] == "file-123"
        assert "Connection successful" in result["message"]

    def test_test_connection_no_active_file(self, service):
        """Test connection test without active file"""
        result = service.test_connection()

        assert result["status"] == "error"
        assert "No active file" in result["message"]

    def test_test_connection_database_error(self, service):
        """Test connection test with database error"""
        service._current_file_id = "file-123"
        service._current_db_path = Path("/nonexistent/path.db")

        result = service.test_connection()

        assert result["status"] == "error"
        assert "No active file" in result["message"] or "Connection failed" in result["message"]

    def test_validate_readonly_query_edge_cases(self, service):
        """Test edge cases in query validation"""
        # Case insensitive
        with pytest.raises(SQLiteSchemaError):
            service._validate_readonly_query("iNsErT INTO test VALUES (1)")

        # Keywords in string literals should be allowed
        service._validate_readonly_query("SELECT 'DROP TABLE' as msg")

        # Leading whitespace
        service._validate_readonly_query("  \n\t SELECT * FROM test")

        # Empty query
        with pytest.raises(SQLiteSchemaError):
            service._validate_readonly_query("")

    def test_add_limit_to_query_edge_cases(self, service):
        """Test edge cases in adding LIMIT clause"""
        # Query with semicolon
        assert service._add_limit_to_query("SELECT * FROM test;", 10) == "SELECT * FROM test LIMIT 10"

        # Query with existing limit in subquery
        query = "SELECT * FROM (SELECT * FROM test LIMIT 5) t"
        result = service._add_limit_to_query(query, 10)
        assert result == query  # Should not add another LIMIT

        # Query with LIMIT in different case
        assert service._add_limit_to_query("SELECT * FROM test limit 5", 10) == "SELECT * FROM test limit 5"

    def test_discover_schema_with_special_characters(self, service, mock_file_manager):
        """Test schema discovery with special characters in table/column names"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create table with special characters (using brackets for SQLite)
            cursor.execute("""
                CREATE TABLE [user-data] (
                    [user id] INTEGER PRIMARY KEY,
                    [full name] TEXT,
                    [email@address] TEXT
                )
            """)
            conn.commit()
            conn.close()

            mock_file_manager.get_file_database_path.return_value = db_path
            service.set_active_file("special-file")

            schema = service.discover_schema()
            tables = schema["databases"][db_path.stem]["schemas"]["main"]["tables"]

            assert "user-data" in tables
            assert "user id" in tables["user-data"]["columns"]
            assert "email@address" in tables["user-data"]["columns"]

        finally:
            db_path.unlink(missing_ok=True)

    def test_execute_query_with_null_values(self, service, mock_file_manager, temp_db):
        """Test query execution with NULL values"""
        mock_file_manager.get_file_database_path.return_value = temp_db
        service.set_active_file("file-123")

        result = service.execute_query("SELECT * FROM customers WHERE email IS NULL")

        assert result["row_count"] == 1
        assert result["rows"][0]["name"] == "Bob Johnson"
        assert result["rows"][0]["email"] is None
