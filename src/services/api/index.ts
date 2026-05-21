/**
 * API Services Index
 * Central export point for all API-related services
 */

export { institutionalService } from './institutionalService';
export { apiClient, createFormDataHeaders, handleApiError, wrapApiResponse } from './client';
export type { ApiResponse } from './client';
