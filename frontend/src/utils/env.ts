// ABOUTME: Environment configuration utilities for frontend
// ABOUTME: Handles environment variables and configuration validation

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
} as const;
