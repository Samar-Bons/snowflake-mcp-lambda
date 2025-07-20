// ABOUTME: Authentication-related TypeScript type definitions
// ABOUTME: Includes user, session, and OAuth types for frontend

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  created_at: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  output_format: 'table' | 'text' | 'both';
  autorun_queries: boolean;
  row_limit: number;
  theme: 'dark';
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export interface LoginResponse {
  redirect_url: string;
}

export interface AuthError {
  message: string;
  code?: string;
}
