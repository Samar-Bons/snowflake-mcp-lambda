// ABOUTME: Authentication context and hook for managing user authentication state
// ABOUTME: Provides login, logout, and user session management throughout the app

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import { User } from '../types';
import { authService } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (redirectUrl?: string) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = (redirectUrl?: string) => {
    const url = redirectUrl ? `/api/auth/login?redirect=${encodeURIComponent(redirectUrl)}` : '/api/auth/login';
    window.location.href = url;
  };

  const logout = async () => {
    try {
      await authService.logout();
      setUser(null);
      Cookies.remove('session_token');
      // Redirect to landing page
      window.location.href = '/';
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      setUser(null);
      Cookies.remove('session_token');
      window.location.href = '/';
    }
  };

  const checkAuth = async (): Promise<boolean> => {
    const token = Cookies.get('session_token');
    if (!token) {
      setIsLoading(false);
      return false;
    }

    try {
      const userData = await authService.getUser();
      setUser(userData);
      setIsLoading(false);
      return true;
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      Cookies.remove('session_token');
      setIsLoading(false);
      return false;
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  // Handle OAuth callback - check for success/error parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const authSuccess = urlParams.get('auth');
    const authError = urlParams.get('error');

    if (authSuccess === 'success') {
      // Clear URL parameters and refresh auth state
      window.history.replaceState({}, document.title, window.location.pathname);
      checkAuth();
    } else if (authError) {
      console.error('Authentication error:', authError);
      setIsLoading(false);
      // Could show an error toast here
    }
  }, []);

  const contextValue: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
