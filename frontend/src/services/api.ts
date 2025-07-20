// ABOUTME: Core API client service using Axios for backend communication
// ABOUTME: Handles authentication headers, error handling, and request/response interceptors

import axios, { AxiosError } from 'axios';
import type { AxiosResponse } from 'axios';
import type { ApiError } from '../types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  withCredentials: true, // Important for httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication if needed
api.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: 'An unexpected error occurred',
      status: error.response?.status || 0,
    };

    if (error.response?.data && typeof error.response.data === 'object') {
      const data = error.response.data as any;
      apiError.message = data.message || data.detail || apiError.message;
      apiError.code = data.code;
    } else if (error.message) {
      apiError.message = error.message;
    }

    // Handle specific status codes
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login or clear session
      window.location.href = '/login';
    }

    return Promise.reject(apiError);
  }
);

export default api;
