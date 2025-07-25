# ABOUTME: Data upload and processing endpoints for file upload functionality
# ABOUTME: Handles multi-format file uploads with processor routing and validation

import logging
import re
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from ..auth.endpoints import get_current_user
from ..models.user import User

# Import CSV processor to register it
from ..services.csv_processor import CSVProcessor  # noqa: F401
from ..services.file_management import FileManager
from ..services.file_processor import FileMetadata, file_processor_registry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["data"])

# File upload limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = [".csv", ".tsv", ".txt"]
MAX_FILENAME_LENGTH = 30  # Maximum length for clean filename part


def _generate_meaningful_file_id(filename: str) -> str:
    """Generate a meaningful file ID from filename.

    Format: clean_filename_YYYYMMDD_HHMMSS_shortid
    Example: customer_data_20250125_100630_a1b2
    """
    # Clean the filename
    base_name = Path(filename).stem
    # Remove special characters and normalize
    clean_name = re.sub(r"[^\w\s-]", "", base_name)
    clean_name = re.sub(r"[-\s]+", "_", clean_name)
    clean_name = clean_name.strip("_").lower()

    # Limit length to keep IDs reasonable
    if len(clean_name) > MAX_FILENAME_LENGTH:
        clean_name = clean_name[:MAX_FILENAME_LENGTH].rstrip("_")

    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Add short unique identifier (4 chars from UUID)
    short_id = str(uuid.uuid4())[:4]

    # Combine parts
    file_id = f"{clean_name}_{timestamp}_{short_id}"
    return file_id


def _validate_uploaded_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file extension
    file_path = Path(file.filename)
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


def _process_file_content(
    content: bytes, filename: str, temp_file_path: Path
) -> FileMetadata:
    """Process and save file content"""
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit",
        )

    with open(temp_file_path, "wb") as f:
        f.write(content)

    # Create file metadata
    return FileMetadata(
        filename=filename,
        size=len(content),
        mime_type="application/octet-stream",
        file_extension=Path(filename).suffix,
    )


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile,
) -> JSONResponse:
    """Upload and process a data file"""
    _validate_uploaded_file(file)

    # Create temporary file for processing
    temp_file_path = None
    try:
        # Create temp file
        temp_dir = Path(tempfile.gettempdir()) / "data_chat_uploads"
        temp_dir.mkdir(exist_ok=True)

        temp_file_id = _generate_meaningful_file_id(file.filename or "unnamed_file")
        temp_file_path = temp_dir / f"{temp_file_id}_{file.filename}"

        # Read and save file content
        content = await file.read()
        file_metadata = _process_file_content(
            content, file.filename or "unknown", temp_file_path
        )
        file_metadata.mime_type = file.content_type or "application/octet-stream"

        # Get appropriate processor
        processor = file_processor_registry.get_processor(
            temp_file_path, file.content_type
        )
        if not processor:
            raise HTTPException(
                status_code=400, detail="No processor available for this file type"
            )

        # Validate file
        validation_errors = processor.validate_file(temp_file_path, file_metadata)
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {'; '.join(validation_errors)}",
            )

        # Detect schema
        try:
            schema = processor.detect_schema(temp_file_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        # Convert to database
        file_manager = FileManager()
        # Generate or get session ID for the user
        session_id = request.session.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session["session_id"] = session_id

        db_path = file_manager.get_user_db_path(session_id, temp_file_id)

        result = processor.convert_to_database(temp_file_path, db_path)

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"File processing failed: {result.error_message}",
            )

        # Store file metadata in session
        file_info = {
            "file_id": temp_file_id,
            "filename": file.filename,
            "schema": {
                "table_name": schema.table_name,
                "columns": [
                    {
                        "name": col.name,
                        "data_type": col.data_type,
                        "nullable": col.nullable,
                        "sample_values": col.sample_values,
                    }
                    for col in schema.columns
                ],
                "row_count": schema.row_count,
            },
            "database_path": str(db_path),
            "warnings": result.warnings or [],
        }

        file_manager.store_file_info(session_id, temp_file_id, file_info)

        return JSONResponse(
            content={
                "success": True,
                "file_id": temp_file_id,
                "schema": file_info["schema"],
                "warnings": file_info["warnings"],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in file upload")
        raise HTTPException(status_code=500, detail="Internal server error") from e

    finally:
        # Clean up temporary file
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


@router.get("/schema/{file_id}")
async def get_file_schema(
    file_id: str,
    request: Request,
) -> JSONResponse:
    """Get schema information for uploaded file"""

    file_manager = FileManager()
    # Get session ID from request
    session_id = request.session.get("session_id", "anonymous")
    file_info = file_manager.get_file_info(session_id, file_id)

    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    return JSONResponse(
        content={
            "file_id": file_id,
            "filename": file_info["filename"],
            "schema": file_info["schema"],
        }
    )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> JSONResponse:
    """Delete uploaded file and associated data"""

    file_manager = FileManager()
    success = file_manager.delete_file(str(current_user.id), file_id)

    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return JSONResponse(content={"success": True, "message": "File deleted"})


@router.get("/files")
async def list_files(current_user: User = Depends(get_current_user)) -> JSONResponse:  # noqa: B008
    """List uploaded files for user"""

    file_manager = FileManager()
    files = file_manager.list_user_files(str(current_user.id))

    return JSONResponse(content={"files": files})


@router.post("/cleanup")
async def cleanup_expired_files(
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> JSONResponse:
    """Clean up expired files (admin endpoint, could be automated)"""

    file_manager = FileManager()
    cleaned_count = file_manager.cleanup_expired_files()

    return JSONResponse(content={"success": True, "cleaned_files": cleaned_count})


# HTML template for testing file upload
@router.get("/upload", response_class=HTMLResponse)
async def upload_form() -> HTMLResponse:
    """Basic HTML form for testing file uploads"""

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Chat - File Upload</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
            .upload-area.dragover { border-color: #007bff; background-color: #f8f9fa; }
            .file-info { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .schema-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            .schema-table th, .schema-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .schema-table th { background-color: #f2f2f2; }
            .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; }
            .success { color: #155724; background: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0; }
            button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
        </style>
    </head>
    <body>
        <h1>Data Chat - File Upload Test</h1>

        <div class="upload-area" id="uploadArea">
            <p>Drag and drop a CSV file here, or click to select</p>
            <input type="file" id="fileInput" accept=".csv,.tsv,.txt" style="display: none;">
            <button onclick="document.getElementById('fileInput').click()">Choose File</button>
        </div>

        <div id="fileInfo" style="display: none;" class="file-info">
            <h3>Selected File:</h3>
            <p id="fileName"></p>
            <p id="fileSize"></p>
            <button id="uploadButton" onclick="uploadFile()">Upload File</button>
        </div>

        <div id="result"></div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            let selectedFile = null;

            // Drag and drop handlers
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileSelect(files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });

            function handleFileSelect(file) {
                selectedFile = file;
                document.getElementById('fileName').textContent = 'Name: ' + file.name;
                document.getElementById('fileSize').textContent = 'Size: ' + (file.size / 1024).toFixed(1) + ' KB';
                document.getElementById('fileInfo').style.display = 'block';
            }

            async function uploadFile() {
                if (!selectedFile) return;

                const uploadButton = document.getElementById('uploadButton');
                uploadButton.disabled = true;
                uploadButton.textContent = 'Uploading...';

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const response = await fetch('/data/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (response.ok) {
                        showResult(result, 'success');
                    } else {
                        showResult(result, 'error');
                    }

                } catch (error) {
                    showResult({detail: 'Upload failed: ' + error.message}, 'error');
                }

                uploadButton.disabled = false;
                uploadButton.textContent = 'Upload File';
            }

            function showResult(result, type) {
                const resultDiv = document.getElementById('result');

                if (type === 'success') {
                    let html = '<div class="success">';
                    html += '<h3>Upload Successful!</h3>';
                    html += '<p>File ID: ' + result.file_id + '</p>';

                    if (result.warnings && result.warnings.length > 0) {
                        html += '<h4>Warnings:</h4><ul>';
                        result.warnings.forEach(warning => html += '<li>' + warning + '</li>');
                        html += '</ul>';
                    }

                    html += '<h4>Schema:</h4>';
                    html += '<table class="schema-table">';
                    html += '<tr><th>Column</th><th>Type</th><th>Nullable</th><th>Sample Values</th></tr>';

                    result.schema.columns.forEach(col => {
                        html += '<tr>';
                        html += '<td>' + col.name + '</td>';
                        html += '<td>' + col.data_type + '</td>';
                        html += '<td>' + (col.nullable ? 'Yes' : 'No') + '</td>';
                        html += '<td>' + (col.sample_values || []).join(', ') + '</td>';
                        html += '</tr>';
                    });

                    html += '</table>';
                    html += '<p>Total rows: ' + result.schema.row_count + '</p>';
                    html += '</div>';

                    resultDiv.innerHTML = html;

                } else {
                    resultDiv.innerHTML = '<div class="error"><h3>Upload Failed</h3><p>' +
                                        (result.detail || 'Unknown error') + '</p></div>';
                }
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
