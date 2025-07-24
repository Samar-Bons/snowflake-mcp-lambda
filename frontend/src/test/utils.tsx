// ABOUTME: Test utilities and helpers for component testing
// ABOUTME: Custom render function with providers and mock data factories

import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth';
import { UploadedFile, TableSchema, ChatMessage, User } from '../types';

// Mock providers wrapper
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </BrowserRouter>
  );
};

// Custom render function with providers
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };

// Mock data factories
export const mockUser: User = {
  id: 'test-user-id',
  email: 'test@example.com',
  name: 'Test User',
  picture: 'https://example.com/avatar.jpg',
  sub: 'google-oauth-sub',
};

export const mockUploadedFile: UploadedFile = {
  id: 'test-file-id',
  name: 'test-data.csv',
  size: 1024000,
  type: 'text/csv',
  uploadedAt: new Date('2025-01-20T10:00:00Z'),
  status: 'completed',
  estimatedRows: 1000,
  processingProgress: 100,
};

export const mockTableSchema: TableSchema = {
  tableName: 'test_data',
  rowCount: 1000,
  columns: [
    {
      name: 'id',
      type: 'number',
      nullable: false,
    },
    {
      name: 'name',
      type: 'text',
      nullable: false,
    },
    {
      name: 'email',
      type: 'text',
      nullable: true,
    },
    {
      name: 'created_at',
      type: 'date',
      nullable: false,
    },
    {
      name: 'revenue',
      type: 'number',
      nullable: true,
    },
  ],
};

export const mockChatMessage: ChatMessage = {
  id: 'test-message-id',
  role: 'user',
  content: 'Show me the top 5 customers by revenue',
  timestamp: new Date('2025-01-20T10:05:00Z'),
  status: 'sent',
};

export const mockAssistantMessage: ChatMessage = {
  id: 'test-assistant-message-id',
  role: 'assistant',
  content: 'I\'ll help you find the top customers by revenue.',
  timestamp: new Date('2025-01-20T10:05:30Z'),
  status: 'sent',
  sqlQuery: 'SELECT name, email, revenue FROM customers ORDER BY revenue DESC LIMIT 5;',
  queryStatus: 'success',
  executionTime: 45,
  resultRowCount: 5,
};

export const mockQueryResult = {
  id: 'test-result-id',
  columns: [
    { key: 'name', label: 'Customer Name', type: 'text' },
    { key: 'email', label: 'Email', type: 'text' },
    { key: 'revenue', label: 'Revenue', type: 'number' },
  ],
  data: [
    { name: 'John Smith', email: 'john@example.com', revenue: 15420 },
    { name: 'Sarah Johnson', email: 'sarah@example.com', revenue: 12890 },
    { name: 'Mike Wilson', email: 'mike@example.com', revenue: 11230 },
    { name: 'Alice Brown', email: 'alice@example.com', revenue: 9870 },
    { name: 'Tom Davis', email: 'tom@example.com', revenue: 8540 },
  ],
  totalRows: 5,
  executionTime: 45,
  status: 'success' as const,
};

// File creation helper for upload tests
export const createMockFile = (
  name: string = 'test.csv',
  size: number = 1024,
  type: string = 'text/csv'
): File => {
  const content = 'id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com';
  const file = new File([content], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

// Async utility for waiting for state updates
export const waitForNextUpdate = () =>
  new Promise(resolve => setTimeout(resolve, 0));

// Mock API response helper
export const mockApiResponse = (data: any, status: number = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    blob: () => Promise.resolve(new Blob([JSON.stringify(data)])),
  });
};

// Error boundary for testing
export class TestErrorBoundary extends React.Component<
  { children: React.ReactNode; onError?: (error: Error) => void },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    this.props.onError?.(error);
  }

  render() {
    if (this.state.hasError) {
      return <div data-testid="error-boundary">Something went wrong</div>;
    }

    return this.props.children;
  }
}
