// ABOUTME: Authentication service for Google OAuth login and user management
// ABOUTME: Handles login redirects, user profile fetching, and logout functionality

import { apiClient } from './api';
import { User, AuthCallbackResponse } from '../types';

class AuthService {
  async getUser(): Promise<User> {
    return apiClient.get<User>('/auth/user');
  }

  async logout(): Promise<void> {
    return apiClient.post<void>('/auth/logout');
  }

  // Handle OAuth callback (called by backend redirect)
  async handleCallback(code: string, state?: string): Promise<AuthCallbackResponse> {
    return apiClient.post<AuthCallbackResponse>('/auth/callback', {
      code,
      state,
    });
  }

  // Get login URL (for manual redirect if needed)
  getLoginUrl(redirectUrl?: string): string {
    const params = new URLSearchParams();
    if (redirectUrl) {
      params.set('redirect', redirectUrl);
    }
    return `/api/auth/login?${params.toString()}`;
  }
}

export const authService = new AuthService();
