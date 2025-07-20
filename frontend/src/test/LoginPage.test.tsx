// ABOUTME: Unit tests for the LoginPage component
// ABOUTME: Tests authentication flow, rendering, and user interactions

import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from '../pages/LoginPage';
import { AuthProvider } from '../hooks/useAuth';

// Mock the auth service
vi.mock('../services/auth', () => ({
  AuthService: {
    login: vi.fn(),
    getCurrentUser: vi.fn().mockRejectedValue(new Error('Not authenticated')),
    logout: vi.fn(),
    checkAuthStatus: vi.fn().mockResolvedValue(false),
  },
}));

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {ui}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('LoginPage', () => {
  it('renders login page with Google OAuth button', async () => {
    renderWithProviders(<LoginPage />);

    expect(screen.getByText('Snowflake Chat')).toBeInTheDocument();
    expect(screen.getByText('Welcome back')).toBeInTheDocument();
    expect(screen.getByText('Continue with Google')).toBeInTheDocument();
  });

  it('displays app description', async () => {
    renderWithProviders(<LoginPage />);

    expect(screen.getByText(/Connect to your Snowflake database/)).toBeInTheDocument();
    expect(screen.getByText(/query with natural language/)).toBeInTheDocument();
  });
});
