// ABOUTME: Backend response adapters that transform API responses to frontend format
// ABOUTME: Preserves frontend UI expectations while adapting to actual backend contract

import {
  UploadedFile,
  TableSchema,
  ColumnSchema,
  ChatMessage,
  QueryResult,
  ApiResponse,
  ChatQueryResponse,
  FileUploadResponse
} from '../types';

// Backend response types (based on verified API contract)
interface BackendUploadResponse {
  success: boolean;
  file_id: string;
  schema: {
    table_name: string;
    columns: {
      name: string;
      data_type: 'TEXT' | 'INTEGER' | 'REAL';
      nullable: boolean;
      sample_values: any[];
    }[];
    row_count: number;
  };
  warnings: string[];
}

interface BackendChatResponse {
  sql: string;
  autorun: boolean;
  results: {
    rows: Array<Record<string, any>>;
    columns: { name: string; type: string }[];
    row_count: number;
    execution_time_ms: number;
    query: string;
    metadata: {
      file_id: string;
      database: string;
      limited: boolean;
    };
  } | null;
}

interface BackendSchemaResponse {
  file_id: string;
  filename: string;
  schema: BackendUploadResponse['schema'];
}

export class BackendAdapters {
  /**
   * Transform backend upload response to frontend UploadedFile format
   */
  static adaptUploadResponse(response: BackendUploadResponse): ApiResponse<UploadedFile & { schema: TableSchema }> {
    const filename = this.extractFilenameFromTableName(response.schema.table_name);
    const estimatedSize = this.estimateFileSize(response.schema.row_count);

    const uploadedFile: UploadedFile = {
      id: response.file_id,
      name: filename,
      size: estimatedSize,
      uploadedAt: new Date(),
      processingStatus: 'completed',
      rowCount: response.schema.row_count,
      columnCount: response.schema.columns.length,
    };

    const schema: TableSchema = {
      tableName: response.schema.table_name,
      columns: response.schema.columns.map(col => this.adaptColumnSchema(col)),
      rowCount: response.schema.row_count,
      filePath: response.schema.table_name,
    };

    return {
      success: true,
      data: { ...uploadedFile, schema },
      message: 'File uploaded successfully',
    };
  }

  /**
   * Transform backend schema response to frontend TableSchema format
   */
  static adaptSchemaResponse(response: BackendSchemaResponse): ApiResponse<TableSchema> {
    const schema: TableSchema = {
      tableName: response.schema.table_name,
      columns: response.schema.columns.map(col => this.adaptColumnSchema(col)),
      rowCount: response.schema.row_count,
      filePath: response.schema.table_name,
    };

    return {
      success: true,
      data: schema,
    };
  }

  /**
   * Transform backend chat response to frontend ChatQueryResponse format
   */
  static adaptChatResponse(response: BackendChatResponse): ApiResponse<ChatQueryResponse> {
    const chatResponse: ChatQueryResponse = {
      messageId: this.generateMessageId(),
      sqlQuery: response.sql,
      requiresConfirmation: !response.autorun,
      results: response.results ? this.adaptQueryResult(response.results, response.sql) : undefined,
    };

    return {
      success: true,
      data: chatResponse,
    };
  }

  /**
   * Transform backend query results to frontend QueryResult format
   */
  static adaptQueryResult(backendResult: NonNullable<BackendChatResponse['results']>, originalQuery: string): QueryResult {
    return {
      id: this.generateResultId(),
      query: originalQuery,
      data: backendResult.rows,
      columns: backendResult.columns.map(col => ({
        key: col.name,
        label: this.formatColumnLabel(col.name),
        type: this.inferFrontendColumnType(col.name, backendResult.rows),
      })),
      totalRows: backendResult.row_count,
      executionTime: backendResult.execution_time_ms,
      status: 'success',
    };
  }

  /**
   * Transform backend column schema to frontend ColumnSchema format
   */
  private static adaptColumnSchema(backendColumn: BackendUploadResponse['schema']['columns'][0]): ColumnSchema {
    return {
      name: backendColumn.name,
      type: this.mapBackendTypeToFrontend(backendColumn.data_type),
      nullable: backendColumn.nullable,
      sampleValues: backendColumn.sample_values.map(val => String(val)),
    };
  }

  /**
   * Map backend data types to frontend display types with intelligent inference
   */
  private static mapBackendTypeToFrontend(backendType: string): ColumnSchema['type'] {
    switch (backendType) {
      case 'INTEGER':
        return 'INTEGER';
      case 'REAL':
        return 'DECIMAL';
      case 'TEXT':
      default:
        return 'TEXT';
    }
  }

  /**
   * Infer frontend column type from data for better display formatting
   */
  private static inferFrontendColumnType(columnName: string, rows: Array<Record<string, any>>): 'text' | 'number' | 'date' | 'boolean' {
    if (rows.length === 0) return 'text';

    const sampleValue = rows[0][columnName];
    if (sampleValue === null || sampleValue === undefined) return 'text';

    // Try to infer from actual data
    if (typeof sampleValue === 'number') return 'number';
    if (typeof sampleValue === 'boolean') return 'boolean';

    const stringValue = String(sampleValue);

    // Check for date patterns
    if (this.isDateString(stringValue)) return 'date';

    // Check for numeric strings
    if (this.isNumericString(stringValue)) return 'number';

    return 'text';
  }

  /**
   * Extract original filename from backend table name
   */
  private static extractFilenameFromTableName(tableName: string): string {
    // Table name format: "table_uuid_originalfilename"
    const parts = tableName.split('_');
    if (parts.length >= 3) {
      return parts.slice(2).join('_') + '.csv';
    }
    return 'uploaded-file.csv';
  }

  /**
   * Estimate file size based on row count (for display purposes)
   */
  private static estimateFileSize(rowCount: number): number {
    // Rough estimate: ~100 bytes per row for CSV files
    return Math.max(1024, rowCount * 100);
  }

  /**
   * Format column name for display (convert snake_case to Title Case)
   */
  private static formatColumnLabel(columnName: string): string {
    return columnName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  /**
   * Generate unique message ID for chat messages
   */
  private static generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique result ID for query results
   */
  private static generateResultId(): string {
    return `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Check if string appears to be a date
   */
  private static isDateString(value: string): boolean {
    const dateRegex = /^\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4}|\d{4}\/\d{2}\/\d{2}/;
    return dateRegex.test(value) && !isNaN(Date.parse(value));
  }

  /**
   * Check if string appears to be numeric
   */
  private static isNumericString(value: string): boolean {
    return !isNaN(Number(value)) && !isNaN(parseFloat(value));
  }

  /**
   * Transform backend error responses to frontend format
   */
  static adaptErrorResponse(error: any): ApiResponse<never> {
    // Handle FastAPI validation errors
    if (error.detail && Array.isArray(error.detail)) {
      const validationErrors = error.detail.map((e: any) => e.msg).join(', ');
      return {
        success: false,
        error: `Validation error: ${validationErrors}`,
      };
    }

    // Handle simple error messages
    if (error.detail && typeof error.detail === 'string') {
      return {
        success: false,
        error: error.detail,
      };
    }

    // Fallback for unknown error formats
    return {
      success: false,
      error: error.message || 'An unexpected error occurred',
    };
  }

  /**
   * Create sample data for schema preview (from backend sample_values)
   */
  static createSampleDataFromSchema(schema: TableSchema): Array<Record<string, any>> {
    const sampleData: Array<Record<string, any>> = [];
    const maxSamples = Math.min(3, Math.max(...schema.columns.map(col => col.sampleValues.length)));

    for (let i = 0; i < maxSamples; i++) {
      const row: Record<string, any> = {};
      schema.columns.forEach(col => {
        row[col.name] = col.sampleValues[i] || null;
      });
      sampleData.push(row);
    }

    return sampleData;
  }
}
