// ABOUTME: API-related TypeScript type definitions
// ABOUTME: Common API response types and request/response interfaces

export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  error?: string;
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
}

export interface ApiErrorResponse {
  message?: string;
  detail?: string;
  code?: string;
}

// Type guard to check if data is an API error response
export function isApiErrorResponse(data: unknown): data is ApiErrorResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    (typeof (data as ApiErrorResponse).message === 'string' ||
     typeof (data as ApiErrorResponse).detail === 'string')
  );
}

export interface HealthCheckResponse {
  status: 'ok' | 'error';
  checks: {
    database: 'ok' | 'error';
    redis: 'ok' | 'error';
  };
  timestamp: string;
}
