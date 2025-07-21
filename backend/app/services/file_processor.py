# ABOUTME: Abstract base class for extensible file processing system
# ABOUTME: Defines interface for all file type processors (CSV, Excel, JSON, Parquet)

import mimetypes
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FileMetadata:
    """Metadata about uploaded file"""

    filename: str
    size: int
    mime_type: str
    file_extension: str
    encoding: str | None = None


@dataclass
class SchemaColumn:
    """Column schema information"""

    name: str
    data_type: str
    nullable: bool = True
    sample_values: list[Any] | None = None

    def __post_init__(self) -> None:
        if self.sample_values is None:
            self.sample_values = []


@dataclass
class FileSchema:
    """Schema information for processed file"""

    table_name: str
    columns: list[SchemaColumn]
    row_count: int
    file_metadata: FileMetadata


@dataclass
class ProcessingResult:
    """Result of file processing operation"""

    success: bool
    schema: FileSchema | None = None
    database_path: str | None = None
    error_message: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


class FileProcessor(ABC):
    """Abstract base class for all file processors"""

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return list of supported file extensions (e.g., ['.csv', '.txt'])"""
        pass

    @property
    @abstractmethod
    def supported_mime_types(self) -> list[str]:
        """Return list of supported MIME types"""
        pass

    @abstractmethod
    def validate_file(self, file_path: Path, metadata: FileMetadata) -> list[str]:
        """
        Validate file format and content.
        Returns list of validation errors (empty if valid).
        """
        pass

    @abstractmethod
    def detect_schema(self, file_path: Path) -> FileSchema:
        """
        Analyze file and detect schema information.
        Raises ValueError if file cannot be processed.
        """
        pass

    @abstractmethod
    def convert_to_database(
        self, file_path: Path, output_db_path: Path
    ) -> ProcessingResult:
        """
        Convert file to SQLite database.
        Returns ProcessingResult with success status and details.
        """
        pass


class FileProcessorRegistry:
    """Registry for managing file processors"""

    def __init__(self) -> None:
        self._processors: dict[str, type[FileProcessor]] = {}
        self._mime_type_map: dict[str, type[FileProcessor]] = {}

    def register(self, processor_class: type[FileProcessor]) -> None:
        """Register a file processor"""
        processor = processor_class()

        # Register by extension
        for ext in processor.supported_extensions:
            self._processors[ext.lower()] = processor_class

        # Register by MIME type
        for mime_type in processor.supported_mime_types:
            self._mime_type_map[mime_type.lower()] = processor_class

    def get_processor(
        self, file_path: Path, mime_type: str | None = None
    ) -> FileProcessor | None:
        """Get appropriate processor for file"""
        file_ext = file_path.suffix.lower()

        # Try by extension first
        if file_ext in self._processors:
            return self._processors[file_ext]()

        # Try by MIME type
        if mime_type and mime_type.lower() in self._mime_type_map:
            return self._mime_type_map[mime_type.lower()]()

        # Try to guess MIME type
        guessed_mime, _ = mimetypes.guess_type(str(file_path))
        if guessed_mime and guessed_mime.lower() in self._mime_type_map:
            return self._mime_type_map[guessed_mime.lower()]()

        return None

    def get_supported_extensions(self) -> list[str]:
        """Get all supported file extensions"""
        return list(self._processors.keys())

    def get_supported_mime_types(self) -> list[str]:
        """Get all supported MIME types"""
        return list(self._mime_type_map.keys())


# Global registry instance
file_processor_registry = FileProcessorRegistry()
