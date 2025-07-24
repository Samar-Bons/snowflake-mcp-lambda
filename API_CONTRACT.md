# Data Chat MVP - API Contract (100% Verified)

**Base URL**: `http://localhost:8000/api/v1`

## Authentication
- **None required** for MVP - all endpoints are public
- All requests should include `credentials: 'include'` for session management

---

## 1. File Upload

### `POST /data/upload`
Upload CSV file and get schema analysis.

**Request**: `multipart/form-data`
```
file: <CSV file>
```

**Response**: `200 OK`
```json
{
  "success": true,
  "file_id": "6771261f-c379-491e-9b10-3c6fd880a95c",
  "schema": {
    "table_name": "table_6771261f_c379_491e_9b10_3c6fd880a95c_filename",
    "columns": [
      {
        "name": "column_name",
        "data_type": "TEXT|INTEGER|REAL",
        "nullable": true|false,
        "sample_values": ["val1", "val2"]  // Only non-null values shown
      }
    ],
    "row_count": 2  // Actual data rows processed (excludes header)
  },
  "warnings": []
}
```

**Error Responses**:
- `400`: `{"detail": "File validation failed: No data rows found in file"}`
- `422`: `{"detail": [{"type": "missing", "loc": ["body", "file"], "msg": "Field required"}]}`

---

## 2. Get Schema

### `GET /data/schema/{file_id}`
Get schema information for uploaded file.

**Response**: `200 OK`
```json
{
  "file_id": "uuid-string",
  "filename": "original.csv",
  "schema": {
    "table_name": "uuid_filename",
    "columns": [...], // Same as upload response
    "row_count": 123
  }
}
```

---

## 3. Natural Language Chat

### `POST /chat/`
Convert natural language to SQL and optionally execute.

**Request** (all fields required):
```json
{
  "prompt": "show me all customers",
  "autorun": false,          // REQUIRED: true = auto-execute, false = just generate SQL
  "file_id": "uuid-string"   // REQUIRED: Must be valid uploaded file ID
}
```

**Response**: `200 OK`
```json
{
  "sql": "SELECT * FROM table_6771261f_c379_491e_9b10_3c6fd880a95c_filename",
  "autorun": false,
  "results": null            // Always null when autorun=false
}
```

**With autorun=true**:
```json
{
  "sql": "SELECT COUNT(*) FROM table_6771261f_c379_491e_9b10_3c6fd880a95c_filename",
  "autorun": true,
  "results": {
    "rows": [
      {"COUNT(*)": 3}          // Object format - column names as keys
    ],
    "columns": [
      {"name": "COUNT(*)", "type": "TEXT"}  // All types are "TEXT" currently
    ],
    "row_count": 1,
    "execution_time_ms": 0,
    "query": "SELECT COUNT(*) FROM table_... LIMIT 500",  // Actual executed query
    "metadata": {
      "file_id": "6771261f-c379-491e-9b10-3c6fd880a95c",
      "database": "6771261f-c379-491e-9b10-3c6fd880a95c",
      "limited": false
    }
  }
}
```

**Error Responses**:
- `400`: `{"detail": "File uuid-string not found or expired"}`
- `400`: `{"detail": "Snowflake is not configured. Please provide a file_id or configure Snowflake credentials."}` (when file_id missing)
- `400`: `{"detail": "Failed to generate SQL: Only SELECT queries are allowed. Generated query must start with SELECT."}`

---

## 4. Direct SQL Execution

### `POST /chat/execute`
Execute SQL query directly (for edited queries).

**Request**:
```json
{
  "sql": "SELECT COUNT(*) FROM table_name",
  "file_id": "uuid-string"
}
```

**Response**: `200 OK`
```json
{
  "results": {
    "rows": [...],           // Same format as chat endpoint
    "columns": [...],
    "row_count": 123,
    "execution_time_ms": 15,
    "query": "actual executed query",
    "metadata": {...}
  }
}
```

---

## Error Responses

**Single Error Format**:
```json
{
  "detail": "Simple error message"
}
```

**Validation Error Format** (Pydantic):
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

**JSON Parse Error Format**:
```json
{
  "detail": [
    {
      "type": "json_invalid",
      "loc": ["body", 0],
      "msg": "JSON decode error",
      "input": {},
      "ctx": {"error": "Expecting value"}
    }
  ]
}
```

**HTTP Status Codes**:
- `400` - Bad request (invalid SQL, file not found, dangerous queries)
- `404` - Endpoint not found (`{"detail": "Not Found"}`)
- `405` - Method not allowed (`{"detail": "Method Not Allowed"}`)
- `422` - Validation error (missing/invalid fields)
- `500` - Server error

---

## Critical Frontend Implementation Notes

1. **Table Names**: Always prefixed with `table_` → `table_6771261f_c379_491e_9b10_3c6fd880a95c_filename`
2. **File Sessions**: Files expire after 24h, stored in backend SQLite
3. **SQL Safety**: Only SELECT/WITH allowed, automatic LIMIT 500 applied
4. **Data Format**: Query results are objects `{"column_name": "value"}`, NOT arrays
5. **Column Types**: All columns return `"type": "TEXT"` regardless of actual data type
6. **NULL Handling**: NULL values preserved as `null` in JSON responses
7. **Required Fields**: All chat endpoints require both `prompt` AND `file_id`
8. **Error Handling**: Must handle both string errors and validation arrays
9. **Row Count**: Schema `row_count` excludes header row, shows actual data rows

---

## Recommended Frontend Flow

```
1. Upload → Get file_id + schema
2. Display schema preview with sample data
3. Chat interface → Send NL query with file_id
4. Show SQL confirmation modal (if autorun=false)
5. Execute SQL → Display results in table format
6. Allow SQL editing → Use /chat/execute endpoint
```
