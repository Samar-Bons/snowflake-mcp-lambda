// ABOUTME: Chat service for handling natural language to SQL queries
// ABOUTME: Manages communication with backend chat endpoints and query execution

import { apiClient } from './api';
import { BackendAdapters } from './adapters';
import { generateMessageId } from '../utils/id';
import { TableSchema, ChatMessage, QueryResult, ChatQueryResponse, ApiResponse } from '../types';

class ChatService {
  /**
   * Send a chat message and get SQL generation response
   */
  async sendMessage(
    message: string,
    fileId: string,
    autoExecute: boolean = false
  ): Promise<ApiResponse<ChatQueryResponse>> {
    const backendResponse = await apiClient.post('/chat/', {
      prompt: message,
      file_id: fileId,
      autorun: autoExecute,
    });

    return BackendAdapters.adaptChatResponse(backendResponse as any);
  }

  /**
   * Execute a SQL query against the uploaded data
   */
  async executeQuery(
    sqlQuery: string,
    fileId: string
  ): Promise<ApiResponse<QueryResult>> {
    const backendResponse = await apiClient.post('/chat/execute', {
      sql: sqlQuery,
      file_id: fileId,
    });

    // Transform the execute response to match chat response format for adapter
    const chatFormatResponse = {
      sql: sqlQuery,
      autorun: true,
      results: (backendResponse as any).results,
    };

    const adaptedResponse = BackendAdapters.adaptChatResponse(chatFormatResponse);

    return {
      success: true,
      data: adaptedResponse.data!.results!,
    };
  }

  /**
   * Get chat history for a file/session
   * Note: Backend doesn't provide history endpoint, returns empty array for MVP
   */
  async getChatHistory(_fileId: string): Promise<ChatMessage[]> {
    // MVP: No backend persistence, return empty array
    // Frontend maintains chat history in component state
    return [];
  }

  /**
   * Download query results in specified format (client-side implementation)
   * NOTE: This needs to be called with the actual QueryResult object, not just the ID
   */
  downloadResults(
    queryResult: QueryResult,
    filename: string,
    format: 'csv' | 'json'
  ): void {
    let content: string;
    let mimeType: string;

    if (format === 'csv') {
      // Convert to CSV format
      const headers = queryResult.columns.map(col => col.label).join(',');
      const rows = queryResult.data.map(row =>
        queryResult.columns.map(col => {
          const value = row[col.key];
          // Escape values containing commas or quotes
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      );
      content = [headers, ...rows].join('\n');
      mimeType = 'text/csv';
    } else {
      // JSON format
      content = JSON.stringify({
        columns: queryResult.columns,
        data: queryResult.data,
        totalRows: queryResult.totalRows,
        query: queryResult.query,
        executionTime: queryResult.executionTime
      }, null, 2);
      mimeType = 'application/json';
    }

    // Create blob and download
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${filename}.${format}`;
    link.click();

    // Clean up
    setTimeout(() => URL.revokeObjectURL(url), 100);
  }

  /**
   * Generate sample queries based on schema
   */
  getSampleQueries(schema: TableSchema): string[] {
    const columns = schema.columns;
    const samples: string[] = [];

    // Basic data exploration
    samples.push(`Show me the first 10 rows of data`);
    samples.push(`How many total rows are in this dataset?`);

    // Column-specific queries based on detected types
    const numericColumns = columns.filter(col => col.type === 'INTEGER' || col.type === 'DECIMAL');
    const textColumns = columns.filter(col => col.type === 'TEXT');
    const dateColumns = columns.filter(col => col.type === 'DATE' || col.type === 'DATETIME');

    if (numericColumns.length > 0) {
      // Prefer meaningful columns like revenue, price, amount, value, etc.
      const preferredNumCol = numericColumns.find(col =>
        ['revenue', 'price', 'amount', 'value', 'cost', 'total', 'salary'].includes(col.name.toLowerCase())
      ) || numericColumns[0];
      const numCol = preferredNumCol.name;
      samples.push(`What is the average ${numCol}?`);
      samples.push(`Show me the top 5 records by ${numCol}`);
    }

    if (textColumns.length > 1) {
      const textCol = textColumns[0].name;
      samples.push(`Show me unique values in ${textCol}`);
      samples.push(`Count records by ${textCol}`);
    }

    if (dateColumns.length > 0) {
      const dateCol = dateColumns[0].name;
      samples.push(`Show me data from the last month in ${dateCol}`);
      samples.push(`Group data by month using ${dateCol}`);
    }

    // Combination queries
    if (numericColumns.length > 0 && textColumns.length > 0) {
      const preferredNumCol = numericColumns.find(col =>
        ['revenue', 'price', 'amount', 'value', 'cost', 'total', 'salary'].includes(col.name.toLowerCase())
      ) || numericColumns[0];
      const numCol = preferredNumCol.name;
      const textCol = textColumns[0].name;
      samples.push(`Calculate total ${numCol} by ${textCol}`);
    }

    // Data quality
    samples.push(`Show me rows with missing values`);
    samples.push(`Find duplicate records`);

    return samples.slice(0, 12); // Return up to 12 suggestions
  }

  /**
   * Get query suggestions based on current input (client-side implementation)
   */
  async getQuerySuggestions(
    partialQuery: string,
    schema: TableSchema
  ): Promise<string[]> {
    if (partialQuery.length < 3) {
      return [];
    }

    // Client-side suggestion filtering from sample queries
    return this.getSampleQueries(schema)
      .filter(suggestion =>
        suggestion.toLowerCase().includes(partialQuery.toLowerCase())
      )
      .slice(0, 5);
  }

  /**
   * Clear chat history for a file
   * Note: MVP doesn't persist history, this is handled by component state
   */
  async clearChatHistory(_fileId: string): Promise<void> {
    // MVP: No backend persistence, clearing handled in component state
    return Promise.resolve();
  }

  /**
   * Get query explanation (client-side basic implementation)
   */
  async explainQuery(sqlQuery: string): Promise<string> {
    // Basic client-side SQL explanation
    const query = sqlQuery.trim().toLowerCase();

    if (query.startsWith('select')) {
      const hasWhere = query.includes('where');
      const hasGroupBy = query.includes('group by');
      const hasOrderBy = query.includes('order by');
      const hasLimit = query.includes('limit');

      let explanation = 'This query retrieves data from your uploaded file';

      if (hasWhere) explanation += ', filtering results based on specific conditions';
      if (hasGroupBy) explanation += ', grouping the results by specified columns';
      if (hasOrderBy) explanation += ', sorting the results in a specific order';
      if (hasLimit) explanation += ', limiting the number of results returned';

      return explanation + '.';
    }

    if (query.startsWith('with')) {
      return 'This query uses a Common Table Expression (CTE) to create a temporary result set that is then used in the main query.';
    }

    return 'This query retrieves and processes data from your uploaded file.';
  }

  /**
   * Create a typing indicator message
   */
  createTypingMessage(): ChatMessage {
    return {
      id: generateMessageId('typing'),
      type: 'assistant',
      content: 'Thinking...',
      timestamp: new Date(),
      status: 'sending',
    };
  }
}

export const chatService = new ChatService();
