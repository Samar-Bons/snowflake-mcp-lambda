// ABOUTME: Unit tests for chat service functionality
// ABOUTME: Tests natural language processing, query execution, and chat management

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { chatService } from '../chat';
import { apiClient } from '../api';
import { mockTableSchema } from '../../test/utils';
import { QueryResult } from '../../types';

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
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('sendMessage', () => {
    it('should send a chat message and return SQL response', async () => {
      const mockResponse = {
        sql: 'SELECT * FROM customers LIMIT 10;',
        autorun: false,
        results: null,
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.sendMessage(
        'Show me the first 10 customers',
        'file-123',
        false
      );

      expect(apiClient.post).toHaveBeenCalledWith('/chat/', {
        prompt: 'Show me the first 10 customers',
        file_id: 'file-123',
        autorun: false,
      });

      // Check that result has the ApiResponse wrapper
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
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
      // Mock response with structure expected by adapter
      const mockResponse = {
        results: {
          columns: [
            { name: 'id', type: 'INTEGER' },
            { name: 'name', type: 'TEXT' },
            { name: 'email', type: 'TEXT' },
            { name: 'created_at', type: 'TEXT' }
          ],
          rows: [
            { id: 1, name: 'John Doe', email: 'john@example.com', created_at: '2024-01-01' },
            { id: 2, name: 'Jane Smith', email: 'jane@example.com', created_at: '2024-01-02' }
          ],
          row_count: 2,
          execution_time_ms: 15,
          query: 'SELECT * FROM customers LIMIT 5;',
          metadata: {
            file_id: 'file-123',
            database: 'sqlite',
            limited: false
          }
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const result = await chatService.executeQuery(
        'SELECT * FROM customers LIMIT 5;',
        'file-123'
      );

      expect(apiClient.post).toHaveBeenCalledWith('/chat/execute', {
        sql: 'SELECT * FROM customers LIMIT 5;',
        file_id: 'file-123',
      });

      // Check that result has the ApiResponse wrapper
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data?.data).toBeDefined();
      expect(result.data?.data.length).toBe(2);
      expect(result.data?.columns).toBeDefined();
      expect(result.data?.columns.length).toBe(4);
    });
  });

  describe('getChatHistory', () => {
    it('should return empty array (MVP - no backend persistence)', async () => {
      const result = await chatService.getChatHistory('file-123');

      expect(result).toEqual([]);
      expect(apiClient.get).not.toHaveBeenCalled();
    });
  });

  describe('downloadResults', () => {
    it('should download CSV results client-side', () => {
      const mockQueryResult: QueryResult = {
        id: 'result-123',
        columns: [
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'age', label: 'Age', type: 'number' }
        ],
        data: [
          { name: 'John', age: 30 },
          { name: 'Jane, Doe', age: 25 },
        ],
        totalRows: 2,
        query: 'SELECT * FROM users',
        executionTime: 123,
        status: 'success'
      };

      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      const createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
      const revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL');

      chatService.downloadResults(mockQueryResult, 'test-results', 'csv');

      // Should create blob and download link
      expect(createElementSpy).toHaveBeenCalledWith('a');
      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(mockLink.download).toBe('test-results.csv');
      expect(mockLink.href).toBe('blob:mock-url');
      expect(mockLink.click).toHaveBeenCalled();

      // Clean up blob URL after delay
      vi.runAllTimers();
      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url');

      createElementSpy.mockRestore();
    });

    it('should download JSON results client-side', () => {
      const mockQueryResult: QueryResult = {
        id: 'result-123',
        columns: [
          { key: 'name', label: 'Name', type: 'text' },
          { key: 'age', label: 'Age', type: 'number' }
        ],
        data: [
          { name: 'John', age: 30 },
          { name: 'Jane', age: 25 },
        ],
        totalRows: 2,
        query: 'SELECT * FROM users',
        executionTime: 123,
        status: 'success'
      };

      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      const createObjectURLSpy = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
      const revokeObjectURLSpy = vi.spyOn(URL, 'revokeObjectURL');

      chatService.downloadResults(mockQueryResult, 'test-results', 'json');

      // Should create blob and download link
      expect(createElementSpy).toHaveBeenCalledWith('a');
      expect(createObjectURLSpy).toHaveBeenCalled();
      expect(mockLink.download).toBe('test-results.json');
      expect(mockLink.href).toBe('blob:mock-url');
      expect(mockLink.click).toHaveBeenCalled();

      // Clean up blob URL after delay
      vi.runAllTimers();
      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:mock-url');

      createElementSpy.mockRestore();
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

    it('should generate local suggestions for longer queries (MVP - no backend suggestions)', async () => {
      const result = await chatService.getQuerySuggestions('show me', mockTableSchema);

      // Should NOT call backend
      expect(apiClient.post).not.toHaveBeenCalled();

      // Should return local suggestions
      expect(result.length).toBeGreaterThan(0);
      expect(result.some(s => s.toLowerCase().includes('show'))).toBe(true);
    });

    it('should fallback to local suggestions on API error', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('API Error'));

      const result = await chatService.getQuerySuggestions('revenue', mockTableSchema);

      expect(result.length).toBeGreaterThan(0);
      expect(result.some(s => s.toLowerCase().includes('revenue'))).toBe(true);
    });
  });

  describe('clearChatHistory', () => {
    it('should do nothing (MVP - no backend persistence)', async () => {
      await chatService.clearChatHistory('file-123');

      // Should NOT call backend
      expect(apiClient.delete).not.toHaveBeenCalled();
    });
  });

  describe('explainQuery', () => {
    it('should generate local explanation (MVP - no backend AI explanation)', async () => {
      const result = await chatService.explainQuery('SELECT * FROM customers ORDER BY revenue DESC;');

      // Should NOT call backend
      expect(apiClient.post).not.toHaveBeenCalled();

      // Should return local explanation as a string
      expect(result).toContain('retrieves');
      expect(result).toContain('sorting');
      expect(typeof result).toBe('string');
    });
  });
});
