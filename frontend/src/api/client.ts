import type { ApiError } from '../types/document';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export class ApiClientError extends Error {
  public apiError: ApiError;

  constructor(apiError: ApiError) {
    super(apiError.message);
    this.name = 'ApiClientError';
    this.apiError = apiError;
  }
}

export const apiClient = {
  async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const apiError: ApiError = {
        errorCode: errorData.error_code || 'UNKNOWN_ERROR',
        message: errorData.message || 'An unknown error occurred.',
        details: errorData.details,
        timestamp: errorData.timestamp || new Date().toISOString(),
      };
      throw new ApiClientError(apiError);
    }

    return response.json();
  }
};
