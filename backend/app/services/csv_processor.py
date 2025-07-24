# ABOUTME: CSV file processor with pandas integration and SQLite conversion
# ABOUTME: First concrete implementation of FileProcessor interface

import logging
import sqlite3
from pathlib import Path
from typing import ClassVar

import chardet
import pandas as pd

from .file_processor import (
    FileMetadata,
    FileProcessor,
    FileSchema,
    ProcessingResult,
    SchemaColumn,
    file_processor_registry,
)

logger = logging.getLogger(__name__)


class CSVProcessor(FileProcessor):
    """Processor for CSV files with automatic delimiter and encoding detection"""

    MAX_SAMPLE_SIZE = 10240  # 10KB for encoding detection
    MAX_ROWS_FOR_SCHEMA = 1000  # Sample rows for schema detection
    MIN_ENCODING_CONFIDENCE = 0.7  # Minimum confidence for encoding detection
    SUPPORTED_ENCODINGS: ClassVar[list[str]] = [
        "utf-8",
        "latin1",
        "cp1252",
        "iso-8859-1",
    ]

    @property
    def supported_extensions(self) -> list[str]:
        return [".csv", ".tsv", ".txt"]

    @property
    def supported_mime_types(self) -> list[str]:
        return [
            "text/csv",
            "text/plain",
            "text/tab-separated-values",
            "application/csv",
        ]

    def validate_file(self, file_path: Path, metadata: FileMetadata) -> list[str]:
        """Validate CSV file format and basic structure"""
        errors = []

        try:
            # Check file size (max 100MB)
            if metadata.size > 100 * 1024 * 1024:
                errors.append("File size exceeds 100MB limit")

            # Check if file is empty
            if metadata.size == 0:
                errors.append("File is empty")

            # Try to detect encoding and read a sample
            encoding = self._detect_encoding(file_path)
            if not encoding:
                errors.append("Unable to detect file encoding")
                return errors

            # Try to read first few rows
            try:
                sample_df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    nrows=10,
                    sep=None,  # Auto-detect separator
                    engine="python",
                )

                if sample_df.empty:
                    errors.append("No data rows found in file")
                elif len(sample_df.columns) == 1:
                    # Might be delimiter issue
                    errors.append("Warning: Only one column detected - check delimiter")

            except pd.errors.EmptyDataError:
                errors.append("File contains no data")
            except Exception as e:
                errors.append(f"Unable to parse CSV: {e!s}")

        except Exception as e:
            errors.append(f"File validation failed: {e!s}")

        return errors

    def detect_schema(self, file_path: Path) -> FileSchema:
        """Detect schema by analyzing CSV structure and data types"""
        encoding = self._detect_encoding(file_path)
        if not encoding:
            raise ValueError("Unable to detect file encoding")

        try:
            # Read sample for schema detection
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                nrows=self.MAX_ROWS_FOR_SCHEMA,
                sep=None,  # Auto-detect separator
                engine="python",
            )

            if df.empty:
                raise ValueError("No data found in CSV file")

            # Get file metadata
            file_stats = file_path.stat()
            file_metadata = FileMetadata(
                filename=file_path.name,
                size=file_stats.st_size,
                mime_type="text/csv",
                file_extension=file_path.suffix,
                encoding=encoding,
            )

            # Analyze columns
            columns = []
            for col_name in df.columns:
                col_data = df[col_name]

                # Determine data type
                data_type = self._infer_column_type(col_data)

                # Check for nulls
                has_nulls = col_data.isnull().any()

                # Get sample values (non-null, unique)
                sample_values = col_data.dropna().unique()[:5].tolist()

                columns.append(
                    SchemaColumn(
                        name=str(col_name),
                        data_type=data_type,
                        nullable=bool(has_nulls),  # Convert numpy bool to Python bool
                        sample_values=sample_values,
                    )
                )

            # Get approximate row count
            row_count = self._estimate_row_count(file_path, encoding)

            table_name = file_path.stem.lower().replace(" ", "_").replace("-", "_")
            # Ensure table name starts with letter (SQL requirement)
            if table_name and table_name[0].isdigit():
                table_name = f"table_{table_name}"

            return FileSchema(
                table_name=table_name,
                columns=columns,
                row_count=row_count,
                file_metadata=file_metadata,
            )

        except Exception as e:
            raise ValueError(f"Schema detection failed: {e!s}") from e

    def convert_to_database(
        self, file_path: Path, output_db_path: Path
    ) -> ProcessingResult:
        """Convert CSV to SQLite database"""
        warnings = []

        try:
            encoding = self._detect_encoding(file_path)
            if not encoding:
                return ProcessingResult(
                    success=False, error_message="Unable to detect file encoding"
                )

            # Read CSV with pandas
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    sep=None,  # Auto-detect separator
                    engine="python",
                )
            except Exception as e:
                return ProcessingResult(
                    success=False, error_message=f"Failed to read CSV: {e!s}"
                )

            if df.empty:
                return ProcessingResult(
                    success=False, error_message="CSV file contains no data"
                )

            # Clean column names for SQLite
            df.columns = [self._clean_column_name(col) for col in df.columns]

            # Check for duplicate column names
            if len(set(df.columns)) != len(df.columns):
                warnings.append("Duplicate column names detected and renamed")
                # Generate unique column names
                cols = []
                seen = set()
                for col in df.columns:
                    if col in seen:
                        i = 1
                        while f"{col}_{i}" in seen:
                            i += 1
                        col = f"{col}_{i}"
                    cols.append(col)
                    seen.add(col)
                df.columns = cols

            # Convert to SQLite
            table_name = file_path.stem.lower().replace(" ", "_").replace("-", "_")
            # Ensure table name starts with letter (SQL requirement)
            if table_name and table_name[0].isdigit():
                table_name = f"table_{table_name}"

            try:
                with sqlite3.connect(output_db_path) as conn:
                    df.to_sql(table_name, conn, index=False, if_exists="replace")

                    # Verify the data was written
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")  # noqa: S608
                    row_count = cursor.fetchone()[0]

                    if row_count != len(df):
                        warnings.append(
                            f"Row count mismatch: expected {len(df)}, got {row_count}"
                        )

            except Exception as e:
                return ProcessingResult(
                    success=False, error_message=f"Database conversion failed: {e!s}"
                )

            # Generate schema for result
            schema = self.detect_schema(file_path)

            return ProcessingResult(
                success=True,
                schema=schema,
                database_path=str(output_db_path),
                warnings=warnings,
            )

        except Exception as e:
            logger.exception("Unexpected error in CSV conversion")
            return ProcessingResult(
                success=False, error_message=f"Conversion failed: {e!s}"
            )

    def _detect_encoding(self, file_path: Path) -> str | None:
        """Detect file encoding using chardet"""
        try:
            with open(file_path, "rb") as f:
                sample = f.read(self.MAX_SAMPLE_SIZE)

            result = chardet.detect(sample)
            detected_encoding = result.get("encoding")
            confidence = result.get("confidence", 0)

            # If confidence is low, try common encodings
            if confidence < self.MIN_ENCODING_CONFIDENCE:
                for encoding in self.SUPPORTED_ENCODINGS:
                    try:
                        with open(file_path, encoding=encoding) as f:
                            f.read(1024)  # Try to read a sample
                        return encoding
                    except (UnicodeDecodeError, UnicodeError):
                        continue

            return detected_encoding

        except Exception as e:
            logger.error(f"Encoding detection failed: {e}")
            return None

    def _infer_column_type(self, series: pd.Series) -> str:
        """Infer SQLite-compatible data type from pandas series"""
        # Remove nulls for type inference
        non_null_series = series.dropna()

        if non_null_series.empty:
            return "TEXT"

        # Try to infer pandas type
        dtype = non_null_series.dtype

        if pd.api.types.is_integer_dtype(dtype):
            return "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            return "REAL"
        elif pd.api.types.is_bool_dtype(dtype):
            return "INTEGER"  # SQLite doesn't have boolean
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "TEXT"  # Store as ISO format
        else:
            # Check if it looks like numbers stored as text
            try:
                pd.to_numeric(non_null_series)
                return "REAL"
            except (ValueError, TypeError):
                pass

            return "TEXT"

    def _clean_column_name(self, name: str) -> str:
        """Clean column name for SQLite compatibility"""
        # Replace spaces and special characters with underscores
        cleaned = str(name).strip()
        cleaned = "".join(c if c.isalnum() else "_" for c in cleaned)

        # Ensure it starts with letter or underscore
        if cleaned and not (cleaned[0].isalpha() or cleaned[0] == "_"):
            cleaned = f"col_{cleaned}"

        # Ensure it's not empty
        if not cleaned:
            cleaned = "unnamed_column"

        return cleaned

    def _estimate_row_count(self, file_path: Path, encoding: str) -> int:
        """Estimate total row count without loading entire file"""
        try:
            with open(file_path, encoding=encoding) as f:
                # Count lines in first chunk
                chunk_size = 8192
                chunk = f.read(chunk_size)
                lines_in_chunk = chunk.count("\n")

                # If file is small, count all lines
                if len(chunk) < chunk_size:
                    return max(0, lines_in_chunk - 1)  # Subtract header

                # Estimate based on file size
                file_size = file_path.stat().st_size
                estimated_lines = int(
                    (lines_in_chunk / len(chunk.encode(encoding))) * file_size
                )
                return max(0, estimated_lines - 1)  # Subtract header

        except Exception:
            return 0


# Register the CSV processor
file_processor_registry.register(CSVProcessor)
