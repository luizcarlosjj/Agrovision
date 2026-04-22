/**
 * Axios HTTP Client
 * Configured for API communication
 * Ready for future integration with real backend
 */

import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import { ApiErrorResponse } from '@models';
import { logger } from '@utils/logger';

/**
 * Creates and configures axios instance
 */
function createApiClient(): AxiosInstance {
  const apiUrl = process.env.API_URL || 'http://localhost:5000/api';
  const timeout = parseInt(process.env.API_TIMEOUT || '30000', 10);

  const instance = axios.create({
    baseURL: apiUrl,
    timeout,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  /**
   * Request interceptor
   * Logs requests and adds authentication if needed
   */
  instance.interceptors.request.use(
    (config) => {
      logger.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      logger.error('[API] Request error:', error);
      return Promise.reject(error);
    },
  );

  /**
   * Response interceptor
   * Handles errors and logs responses
   */
  instance.interceptors.response.use(
    (response) => {
      logger.log(`[API] Response: ${response.status} ${response.statusText}`);
      return response;
    },
    (error: AxiosError<ApiErrorResponse>) => {
      if (error.response) {
        // Server responded with error status
        const errorData = error.response.data;
        logger.error(
          `[API] Error: ${error.response.status} - ${errorData?.error || error.message}`,
        );
      } else if (error.request) {
        // Request made but no response
        logger.error('[API] No response received:', error.message);
      } else {
        // Error in request setup
        logger.error('[API] Request setup error:', error.message);
      }
      return Promise.reject(error);
    },
  );

  return instance;
}

/**
 * Configured API client instance
 */
export const apiClient = createApiClient();

/**
 * Helper function for multipart form data requests
 * Used for image uploads
 */
export function createFormDataHeaders() {
  return {
    'Content-Type': 'multipart/form-data',
  };
}

/**
 * Generic API error handler
 */
export function handleApiError(error: unknown): ApiErrorResponse {
  if (axios.isAxiosError(error)) {
    const errorData = error.response?.data as ApiErrorResponse;
    return {
      error: errorData?.error || error.message,
      code: errorData?.code || 'UNKNOWN_ERROR',
      timestamp: new Date().toISOString(),
      details: errorData?.details,
    };
  }

  return {
    error: 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR',
    timestamp: new Date().toISOString(),
  };
}

/**
 * Type-safe API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  status: number;
  timestamp: string;
}

/**
 * Helper to wrap API responses
 */
export function wrapApiResponse<T>(response: AxiosResponse<T>): ApiResponse<T> {
  return {
    data: response.data,
    status: response.status,
    timestamp: new Date().toISOString(),
  };
}
