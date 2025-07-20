// ABOUTME: React hook for authentication context management
// ABOUTME: Provides auth state, user data, and auth actions throughout the app

import { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';
import type { ReactNode } from 'react';
import { AuthService } from '../services/auth';
import type { User, AuthContextType } from '../types/auth';
import { authEvents } from '../utils/auth-events';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  const login = useCallback(async (): Promise<void> => {
    return AuthService.login();
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    AuthService.logout();
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      setIsLoading(true);
      const userData = await AuthService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check auth status on mount
  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  // Listen for logout events from API client (401 errors)
  useEffect(() => {
    const handleLogout = () => {
      logout();
    };

    authEvents.on('logout', handleLogout);

    return () => {
      authEvents.off('logout', handleLogout);
    };
  }, [logout]);

  const value: AuthContextType = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated,
      login,
      logout,
      refreshUser,
    }),
    [user, isLoading, isAuthenticated, login, logout, refreshUser]
  );

  return (
    <AuthContext.Provider value={value}>
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
