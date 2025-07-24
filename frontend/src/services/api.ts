// ABOUTME: Core API client with authentication, error handling, and request/response types
// ABOUTME: Provides base functionality for all backend communication with proper error handling

import { BackendAdapters } from './adapters';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session management
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle non-JSON responses (like redirects)
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response as unknown as T;
      }

      const data = await response.json();

      if (!response.ok) {
        // Handle FastAPI error format and transform to frontend format
        const errorResponse = BackendAdapters.adaptErrorResponse(data);
        throw new Error(errorResponse.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Return the raw backend response - adapters will be applied at service level
      return data as T;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // GET request
  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = params
      ? `${endpoint}?${new URLSearchParams(params).toString()}`
      : endpoint;

    return this.request<T>(url, {
      method: 'GET',
    });
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  // File upload with progress tracking
  async uploadFile<T>(
    endpoint: string,
    file: File,
    onProgress?: (progress: { percentage: number; bytesUploaded: number; totalBytes: number }) => void
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentage = Math.round((event.loaded / event.total) * 100);
            onProgress({
              percentage,
              bytesUploaded: event.loaded,
              totalBytes: event.total,
            });
          }
        });
      }

      xhr.onload = () => {
        try {
          if (xhr.status >= 200 && xhr.status < 300) {
            // Parse raw backend response - adapters will be applied at service level
            const backendResponse = JSON.parse(xhr.responseText);
            resolve(backendResponse as T);
          } else {
            // Handle error response with adapter
            const errorData = JSON.parse(xhr.responseText);
            const errorResponse = BackendAdapters.adaptErrorResponse(errorData);
            reject(new Error(errorResponse.error || `HTTP ${xhr.status}: ${xhr.statusText}`));
          }
        } catch (error) {
          reject(new Error('Failed to parse response'));
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network error during upload'));
      };

      xhr.open('POST', `${this.baseUrl}${endpoint}`);
      xhr.withCredentials = true; // Include cookies
      xhr.send(formData);
    });
  }

  // Server-Sent Events for real-time updates
  createEventSource(endpoint: string): EventSource {
    const url = `${this.baseUrl}${endpoint}`;
    const eventSource = new EventSource(url, {
      withCredentials: true,
    });
    return eventSource;
  }
}

export const apiClient = new ApiClient();
