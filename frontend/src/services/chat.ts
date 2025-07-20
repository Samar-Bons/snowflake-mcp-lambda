// ABOUTME: Chat service for backend API integration and message handling
// ABOUTME: Manages chat requests, SQL execution, and response processing

import api from './api';
import type { ChatRequest, ChatResponse } from '../types/chat';

export class ChatService {
  /**
   * Send a chat message to the backend for NL-to-SQL conversion and optional execution
   */
  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/chat', request);
      return response.data;
    } catch (error) {
      console.error('Chat request failed:', error);
      throw error;
    }
  }

  /**
   * Execute SQL directly (for edited queries from confirmation modal)
   */
  static async executeSQL(sql: string): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>('/chat', {
        prompt: `Execute this SQL: ${sql}`,
        autorun: true
      });
      return response.data;
    } catch (error) {
      console.error('SQL execution failed:', error);
      throw error;
    }
  }

  /**
   * Test Snowflake connection
   */
  static async testConnection(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await api.post<{ success: boolean; message: string }>('/snowflake/test');
      return response.data;
    } catch (error) {
      console.error('Connection test failed:', error);
      throw error;
    }
  }

  /**
   * Get schema information
   */
  static async getSchema(): Promise<any> {
    try {
      const response = await api.get('/snowflake/schema');
      return response.data;
    } catch (error) {
      console.error('Schema fetch failed:', error);
      throw error;
    }
  }
}
