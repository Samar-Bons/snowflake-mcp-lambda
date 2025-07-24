// ABOUTME: Test utilities and helpers for component testing
// ABOUTME: Custom render function with providers and mock data factories

import { Component } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../hooks/useAuth';
import { UploadedFile, TableSchema, ChatMessage, User, QueryResult } from '../types';

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
};

export const mockUploadedFile: UploadedFile = {
  id: 'test-file-id',
  name: 'test-data.csv',
  size: 1024000,
  uploadedAt: new Date('2025-01-20T10:00:00Z'),
  processingStatus: 'completed',
  estimatedRows: 1000,
  rowCount: 1000,
  columnCount: 5,
};

export const mockTableSchema: TableSchema = {
  tableName: 'test_data',
  rowCount: 1000,
  filePath: '/tmp/test_data.db',
  columns: [
    {
      name: 'id',
      type: 'INTEGER',
      nullable: false,
      sampleValues: ['1', '2', '3'],
    },
    {
      name: 'name',
      type: 'TEXT',
      nullable: false,
      sampleValues: ['John', 'Jane', 'Bob'],
    },
    {
      name: 'email',
      type: 'TEXT',
      nullable: true,
      sampleValues: ['john@example.com', 'jane@example.com'],
    },
    {
      name: 'created_at',
      type: 'DATE',
      nullable: false,
      sampleValues: ['2025-01-01', '2025-01-02'],
    },
    {
      name: 'revenue',
      type: 'DECIMAL',
      nullable: true,
      sampleValues: ['1000.50', '2000.75'],
    },
  ],
};

export const mockChatMessage: ChatMessage = {
  id: 'test-message-id',
  type: 'user',
  content: 'Show me the top 5 customers by revenue',
  timestamp: new Date('2025-01-20T10:05:00Z'),
  status: 'sent',
};

export const mockAssistantMessage: ChatMessage = {
  id: 'test-assistant-message-id',
  type: 'assistant',
  content: 'I\'ll help you find the top customers by revenue.',
  timestamp: new Date('2025-01-20T10:05:30Z'),
  status: 'sent',
  sqlQuery: 'SELECT name, email, revenue FROM customers ORDER BY revenue DESC LIMIT 5;',
};

export const mockQueryResult: QueryResult = {
  id: 'test-result-id',
  query: 'SELECT name, email, revenue FROM customers ORDER BY revenue DESC LIMIT 5',
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
export class TestErrorBoundary extends Component<
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
