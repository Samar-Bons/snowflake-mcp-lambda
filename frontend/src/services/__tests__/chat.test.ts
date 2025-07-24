// ABOUTME: Unit tests for chat service functionality
// ABOUTME: Tests natural language processing, query execution, and chat management

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { chatService } from '../chat';
import { apiClient } from '../api';
import { mockTableSchema, mockQueryResult } from '../../test/utils';

// Mock the API client
vi.mock('../api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('ChatService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('sendMessage', () => {
    it('should send a chat message and return SQL response', async () => {
      const mockResponse = {
        data: {
          sql_query: 'SELECT * FROM customers LIMIT 10;',
          explanation: 'This query shows the first 10 customer records.',
          message_id: 'msg-123',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.sendMessage(
        'Show me the first 10 customers',
        'file-123',
        'session-456'
      );

      expect(apiClient.post).toHaveBeenCalledWith('/chat/generate-sql', {
        message: 'Show me the first 10 customers',
        file_id: 'file-123',
        session_id: 'session-456',
      });

      expect(result).toEqual({
        sqlQuery: 'SELECT * FROM customers LIMIT 10;',
        explanation: 'This query shows the first 10 customer records.',
        messageId: 'msg-123',
      });
    });

    it('should handle API errors gracefully', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('API Error'));

      await expect(
        chatService.sendMessage('Test message', 'file-123')
      ).rejects.toThrow('API Error');
    });
  });

  describe('executeQuery', () => {
    it('should execute SQL query and return formatted results', async () => {
      const mockResponse = {
        data: {
          id: 'result-123',
          columns: mockQueryResult.columns,
          data: mockQueryResult.data,
          total_rows: 5,
          execution_time: 45,
          status: 'success',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.executeQuery(
        'SELECT * FROM customers LIMIT 5;',
        'file-123',
        'msg-123'
      );

      expect(apiClient.post).toHaveBeenCalledWith('/chat/execute-query', {
        sql_query: 'SELECT * FROM customers LIMIT 5;',
        file_id: 'file-123',
        message_id: 'msg-123',
      });

      expect(result).toEqual({
        id: 'result-123',
        columns: mockQueryResult.columns,
        data: mockQueryResult.data,
        totalRows: 5,
        executionTime: 45,
        status: 'success',
      });
    });
  });

  describe('getChatHistory', () => {
    it('should fetch and format chat history', async () => {
      const mockResponse = {
        data: {
          messages: [
            {
              id: 'msg-1',
              role: 'user',
              content: 'Show me customers',
              timestamp: '2025-01-20T10:00:00Z',
              sql_query: null,
              query_status: null,
              query_results: null,
            },
            {
              id: 'msg-2',
              role: 'assistant',
              content: 'Here are your customers',
              timestamp: '2025-01-20T10:00:30Z',
              sql_query: 'SELECT * FROM customers;',
              query_status: 'success',
              query_results: {
                id: 'result-1',
                columns: mockQueryResult.columns,
                data: mockQueryResult.data,
                total_rows: 5,
                execution_time: 45,
                status: 'success',
              },
            },
          ],
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await chatService.getChatHistory('file-123');

      expect(apiClient.get).toHaveBeenCalledWith('/chat/history/file-123');
      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        id: 'msg-1',
        role: 'user',
        content: 'Show me customers',
        timestamp: new Date('2025-01-20T10:00:00Z'),
        sqlQuery: null,
        queryStatus: null,
        queryResults: undefined,
      });
      expect(result[1].queryResults).toBeDefined();
    });
  });

  describe('downloadResults', () => {
    it('should download CSV results', async () => {
      const mockBlob = new Blob(['csv,data'], { type: 'text/csv' });
      const mockResponse = { data: mockBlob };

      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => mockLink as any);
      const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => mockLink as any);

      await chatService.downloadResults('result-123', 'test-results', 'csv');

      expect(apiClient.get).toHaveBeenCalledWith('/chat/export/result-123', {
        params: { format: 'csv' },
        responseType: 'blob',
      });

      expect(createElementSpy).toHaveBeenCalledWith('a');
      expect(mockLink.download).toBe('test-results.csv');
      expect(mockLink.click).toHaveBeenCalled();
      expect(appendChildSpy).toHaveBeenCalled();
      expect(removeChildSpy).toHaveBeenCalled();

      createElementSpy.mockRestore();
      appendChildSpy.mockRestore();
      removeChildSpy.mockRestore();
    });
  });

  describe('getSampleQueries', () => {
    it('should generate appropriate sample queries based on schema', () => {
      const samples = chatService.getSampleQueries(mockTableSchema);


      expect(samples).toContain('Show me the first 10 rows of data');
      expect(samples).toContain('How many total rows are in this dataset?');

      // Should include queries for numeric columns
      expect(samples.some(s => s.includes('revenue'))).toBe(true);

      // Should include queries for text columns
      expect(samples.some(s => s.includes('name'))).toBe(true);

      // Should include queries for date columns
      expect(samples.some(s => s.includes('created_at'))).toBe(true);

      expect(samples.length).toBeLessThanOrEqual(12);
    });

    it('should handle schema with no columns gracefully', () => {
      const emptySchema = { ...mockTableSchema, columns: [] };
      const samples = chatService.getSampleQueries(emptySchema);

      expect(samples).toContain('Show me the first 10 rows of data');
      expect(samples).toContain('How many total rows are in this dataset?');
    });
  });

  describe('getQuerySuggestions', () => {
    it('should return empty array for short queries', async () => {
      const result = await chatService.getQuerySuggestions('a', mockTableSchema);
      expect(result).toEqual([]);
    });

    it('should fetch suggestions from API for longer queries', async () => {
      const mockResponse = {
        data: {
          suggestions: ['Show me top customers', 'Show me recent orders'],
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.getQuerySuggestions('show me', mockTableSchema);

      expect(apiClient.post).toHaveBeenCalledWith('/chat/suggestions', {
        partial_query: 'show me',
        schema: {
          columns: mockTableSchema.columns,
          row_count: mockTableSchema.rowCount,
        },
      });

      expect(result).toEqual(['Show me top customers', 'Show me recent orders']);
    });

    it('should fallback to local suggestions on API error', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('API Error'));

      const result = await chatService.getQuerySuggestions('revenue', mockTableSchema);

      expect(result.length).toBeGreaterThan(0);
      expect(result.some(s => s.toLowerCase().includes('revenue'))).toBe(true);
    });
  });

  describe('clearChatHistory', () => {
    it('should clear chat history for a file', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({});

      await chatService.clearChatHistory('file-123');

      expect(apiClient.delete).toHaveBeenCalledWith('/chat/history/file-123');
    });
  });

  describe('explainQuery', () => {
    it('should get query explanation', async () => {
      const mockResponse = {
        data: {
          explanation: 'This query retrieves customer data ordered by revenue.',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.explainQuery('SELECT * FROM customers ORDER BY revenue DESC;');

      expect(apiClient.post).toHaveBeenCalledWith('/chat/explain-query', {
        sql_query: 'SELECT * FROM customers ORDER BY revenue DESC;',
      });

      expect(result).toBe('This query retrieves customer data ordered by revenue.');
    });
  });
});
