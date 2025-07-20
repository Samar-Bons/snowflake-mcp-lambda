// ABOUTME: Unit tests for ChatWindow component and chat functionality
// ABOUTME: Tests message handling, API integration, and component interactions

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatWindow } from '../components/chat/ChatWindow';
import { ChatService } from '../services/chat';
import '@testing-library/jest-dom';

// Mock scrollIntoView for JSDOM environment
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  value: vi.fn(),
  writable: true,
});

// Mock the ChatService
vi.mock('../services/chat', () => ({
  ChatService: {
    sendMessage: vi.fn(),
    executeSQL: vi.fn(),
  },
}));

describe('ChatWindow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders welcome message on initial load', () => {
    render(<ChatWindow />);

    expect(screen.getByText(/Welcome to Snowflake Chat/)).toBeInTheDocument();
    expect(screen.getByText(/Ask me anything about your data/)).toBeInTheDocument();
  });

  it('displays chat input with autorun toggle', () => {
    render(<ChatWindow />);

    expect(screen.getByPlaceholderText(/Ask a question about your data/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Auto-run queries/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send/ })).toBeInTheDocument();
  });

  it('sends message when send button is clicked', async () => {
    const mockResponse = {
      sql: 'SELECT * FROM customers',
      message: 'Query generated successfully'
    };

    (ChatService.sendMessage as any).mockResolvedValue(mockResponse);

    render(<ChatWindow />);

    const input = screen.getByPlaceholderText(/Ask a question about your data/);
    const sendButton = screen.getByRole('button', { name: /Send/ });

    fireEvent.change(input, { target: { value: 'Show me all customers' } });
    fireEvent.click(sendButton);

    expect(ChatService.sendMessage).toHaveBeenCalledWith({
      prompt: 'Show me all customers',
      autorun: false
    });

    await waitFor(() => {
      expect(screen.getByText('Show me all customers')).toBeInTheDocument();
    });
  });

  it('shows SQL confirmation modal when autorun is disabled', async () => {
    const mockResponse = {
      sql: 'SELECT * FROM customers',
      message: 'Query generated successfully'
    };

    (ChatService.sendMessage as any).mockResolvedValue(mockResponse);

    render(<ChatWindow />);

    const input = screen.getByPlaceholderText(/Ask a question about your data/);
    const sendButton = screen.getByRole('button', { name: /Send/ });

    fireEvent.change(input, { target: { value: 'Show me all customers' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Confirm SQL Execution')).toBeInTheDocument();
      expect(screen.getByText('SELECT * FROM customers')).toBeInTheDocument();
    });
  });

  it('enables autorun toggle and executes immediately', async () => {
    const mockResponse = {
      sql: 'SELECT * FROM customers',
      columns: ['id', 'name'],
      rows: [['1', 'John'], ['2', 'Jane']],
      rowCount: 2,
      truncated: false
    };

    (ChatService.sendMessage as any).mockResolvedValue(mockResponse);

    render(<ChatWindow />);

    // Enable autorun
    const autorunToggle = screen.getByLabelText(/Auto-run queries/);
    fireEvent.click(autorunToggle);

    const input = screen.getByPlaceholderText(/Ask a question about your data/);
    const sendButton = screen.getByRole('button', { name: /Send/ });

    fireEvent.change(input, { target: { value: 'Show me all customers' } });
    fireEvent.click(sendButton);

    expect(ChatService.sendMessage).toHaveBeenCalledWith({
      prompt: 'Show me all customers',
      autorun: true
    });

    await waitFor(() => {
      expect(screen.getByText('Query executed successfully')).toBeInTheDocument();
      expect(screen.getByText('2 rows')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const mockError = new Error('Connection failed');
    (ChatService.sendMessage as any).mockRejectedValue(mockError);

    render(<ChatWindow />);

    const input = screen.getByPlaceholderText(/Ask a question about your data/);
    const sendButton = screen.getByRole('button', { name: /Send/ });

    fireEvent.change(input, { target: { value: 'Show me all customers' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/Sorry, I encountered an error/)).toBeInTheDocument();
    });
  });

  it('shows loading state while processing', async () => {
    let resolvePromise: (value: any) => void;
    const promise = new Promise((resolve) => {
      resolvePromise = resolve;
    });

    (ChatService.sendMessage as any).mockReturnValue(promise);

    render(<ChatWindow />);

    const input = screen.getByPlaceholderText(/Ask a question about your data/);
    const sendButton = screen.getByRole('button', { name: /Send/ });

    fireEvent.change(input, { target: { value: 'Show me all customers' } });
    fireEvent.click(sendButton);

    // Should show loading state
    expect(screen.getByText('Thinking...')).toBeInTheDocument();
    expect(sendButton).toHaveTextContent('Sending...');

    // Resolve the promise
    resolvePromise!({
      sql: 'SELECT * FROM customers',
      message: 'Success'
    });

    await waitFor(() => {
      expect(screen.queryByText('Thinking...')).not.toBeInTheDocument();
    });
  });
});
