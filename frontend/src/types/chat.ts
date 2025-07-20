// ABOUTME: Type definitions for chat interface and messaging system
// ABOUTME: Defines message structure, chat states, and API response types

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sql?: string;
  results?: QueryResults;
  error?: string;
}

export interface QueryResults {
  columns: string[];
  rows: any[][];
  rowCount: number;
  truncated: boolean;
  executionTimeMs?: number;
}

export interface ChatRequest {
  prompt: string;
  autorun: boolean;
}

export interface ChatResponse {
  sql: string;
  rows?: any[][];
  columns?: string[];
  rowCount?: number;
  truncated?: boolean;
  executionTimeMs?: number;
  message?: string;
}

export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  autorun: boolean;
  pendingSql?: string;
  showSqlModal: boolean;
}
