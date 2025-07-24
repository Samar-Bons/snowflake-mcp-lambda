// ABOUTME: TypeScript type definitions for the CSV Data Chat application
// ABOUTME: Includes types for file upload, chat messages, data results, and API responses

export interface User {
  id: string;
  email: string;
  name: string;
  picture: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
  processingStatus: 'uploading' | 'processing' | 'completed' | 'error';
  errorMessage?: string;
  rowCount?: number;
  columnCount?: number;
  estimatedRows?: number;
}

export interface ColumnSchema {
  name: string;
  type: 'TEXT' | 'INTEGER' | 'DECIMAL' | 'DATE' | 'DATETIME' | 'BOOLEAN';
  nullable: boolean;
  sampleValues: string[];
}

export interface TableSchema {
  tableName: string;
  columns: ColumnSchema[];
  rowCount: number;
  filePath: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string | JSX.Element;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  sqlQuery?: string;
  queryResults?: QueryResult;
}

export interface QueryResult {
  id: string;
  query: string;
  data: Array<Record<string, any>>;
  columns: Array<{
    key: string;
    label: string;
    type: 'text' | 'number' | 'date' | 'boolean';
  }>;
  totalRows: number;
  executionTime: number;
  status: 'success' | 'error';
  errorMessage?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadProgress {
  percentage: number;
  currentOperation: string;
  bytesUploaded: number;
  totalBytes: number;
}

export interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  currentQuery?: string;
  awaitingConfirmation?: {
    messageId: string;
    sqlQuery: string;
    userQuestion: string;
  };
}

export interface AppSettings {
  rowLimit: number;
  autoRunQueries: boolean;
  exportFormat: 'csv' | 'json';
  theme: 'dark' | 'light';
}

export interface FileUploadError {
  code: 'FILE_TOO_LARGE' | 'INVALID_FORMAT' | 'PROCESSING_FAILED' | 'NETWORK_ERROR' | 'SAMPLE_LOAD_ERROR';
  message: string;
  details?: string;
}

export interface SessionInfo {
  id: string;
  files: UploadedFile[];
  activeFileId?: string;
  queryHistory: ChatMessage[];
  settings: AppSettings;
  expiresAt: Date;
}

// API endpoint types
export interface AuthCallbackResponse {
  access_token: string;
  user: User;
}

export interface FileUploadResponse {
  fileId: string;
  status: 'uploaded' | 'processing';
  message: string;
}

export interface FileProcessingResponse {
  fileId: string;
  status: 'completed' | 'error';
  schema?: TableSchema;
  errorMessage?: string;
}

export interface ChatQueryRequest {
  message: string;
  fileId: string;
  autoExecute?: boolean;
}

export interface ChatQueryResponse {
  messageId: string;
  sqlQuery: string;
  requiresConfirmation: boolean;
  results?: QueryResult;
}

export interface QueryExecutionRequest {
  messageId: string;
  sqlQuery: string;
  fileId: string;
}

export interface QueryExecutionResponse {
  results: QueryResult;
}

// Component props types
export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export interface FileUploadProps {
  onUpload: (file: File) => void;
  maxSize: number; // in MB
  acceptedTypes: string[];
  state: 'idle' | 'uploading' | 'processing' | 'success' | 'error';
  progress?: UploadProgress;
  error?: FileUploadError;
  className?: string;
}

export interface DataTableProps {
  data: Array<Record<string, any>>;
  columns: Array<{
    key: string;
    label: string;
    type: 'text' | 'number' | 'date' | 'boolean';
  }>;
  totalRows: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  onExport?: (format: 'csv' | 'json') => void;
  loading?: boolean;
  className?: string;
}
