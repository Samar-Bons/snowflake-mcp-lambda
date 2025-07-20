// ABOUTME: Authentication service for handling OAuth flow and user session
// ABOUTME: Manages login, logout, and user profile fetching from backend

import api from './api';
import type { User, LoginResponse } from '../types/auth';

export class AuthService {
  /**
   * Initiate Google OAuth login flow
   * Redirects to backend OAuth endpoint
   */
  static async login(): Promise<void> {
    try {
      const response = await api.get<LoginResponse>('/auth/login');
      window.location.href = response.data.redirect_url;
    } catch (error) {
      console.error('Login initiation failed:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   * Used to hydrate user context after authentication
   */
  static async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }

  /**
   * Logout user and clear session
   */
  static async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout failed:', error);
      // Continue with logout even if backend call fails
    }

    // Redirect to login page
    window.location.href = '/login';
  }

  /**
   * Check if user is authenticated by attempting to fetch profile
   */
  static async checkAuthStatus(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }
}
