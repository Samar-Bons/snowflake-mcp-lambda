# Corrected OpenAPI Specification (Based on Tested Reality)

## Key Discrepancies Found

### 1. **ChatRequest Schema** - WRONG in OpenAPI
**OpenAPI Claims**: `file_id` is optional
**Reality**: `file_id` is REQUIRED for MVP (no Snowflake configured)

**Corrected ChatRequest**:
```json
{
  "properties": {
    "prompt": {
      "type": "string",
      "minLength": 1,
      "title": "Prompt",
      "description": "Natural language query"
    },
    "autorun": {
      "type": "boolean",
      "title": "Autorun",
      "description": "Whether to automatically execute the generated SQL",
      "default": false
    },
    "file_id": {
      "type": "string",
      "title": "File Id",
      "description": "ID of uploaded file to query - REQUIRED for MVP"
    }
  },
  "type": "object",
  "required": ["prompt", "file_id"],  // file_id is REQUIRED
  "title": "ChatRequest"
}
```

### 2. **ChatResponse Schema** - INCOMPLETE in OpenAPI
**OpenAPI Claims**: `results` is generic object
**Reality**: `results` has specific nested structure

**Corrected ChatResponse**:
```json
{
  "properties": {
    "sql": {
      "type": "string",
      "description": "Generated SQL query"
    },
    "autorun": {
      "type": "boolean",
      "description": "Whether query was auto-executed"
    },
    "results": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "rows": {
              "type": "array",
              "items": {
                "type": "object",
                "additionalProperties": true
              },
              "description": "Query result rows as objects"
            },
            "columns": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": {"type": "string"},
                  "type": {"type": "string", "enum": ["TEXT"]}
                },
                "required": ["name", "type"]
              },
              "description": "Column metadata"
            },
            "row_count": {
              "type": "integer",
              "description": "Number of rows returned"
            },
            "execution_time_ms": {
              "type": "integer",
              "description": "Query execution time"
            },
            "query": {
              "type": "string",
              "description": "Actual executed SQL with LIMIT"
            },
            "metadata": {
              "type": "object",
              "properties": {
                "file_id": {"type": "string"},
                "database": {"type": "string"},
                "limited": {"type": "boolean"}
              },
              "required": ["file_id", "database", "limited"]
            }
          },
          "required": ["rows", "columns", "row_count", "execution_time_ms", "query", "metadata"]
        },
        {"type": "null"}
      ],
      "description": "Query results if auto-executed, null otherwise"
    }
  },
  "required": ["sql", "autorun"],
  "type": "object"
}
```

### 3. **Upload Response Schema** - MISSING in OpenAPI
**OpenAPI Claims**: Generic response
**Reality**: Specific schema structure returned

**Missing Upload Response Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {"type": "boolean"},
    "file_id": {"type": "string", "format": "uuid"},
    "schema": {
      "type": "object",
      "properties": {
        "table_name": {
          "type": "string",
          "pattern": "^table_[a-f0-9-]+_.*$"
        },
        "columns": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "data_type": {"type": "string", "enum": ["TEXT", "INTEGER", "REAL"]},
              "nullable": {"type": "boolean"},
              "sample_values": {
                "type": "array",
                "description": "Non-null sample values"
              }
            },
            "required": ["name", "data_type", "nullable", "sample_values"]
          }
        },
        "row_count": {
          "type": "integer",
          "description": "Actual data rows (excludes header)"
        }
      },
      "required": ["table_name", "columns", "row_count"]
    },
    "warnings": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["success", "file_id", "schema", "warnings"]
}
```

## Summary
The **backend OpenAPI spec is outdated/incorrect** and doesn't match the tested API behavior. The above corrections reflect the actual working API that we verified through testing.

For frontend development, use our **tested API contract** rather than the OpenAPI spec until it's updated.
