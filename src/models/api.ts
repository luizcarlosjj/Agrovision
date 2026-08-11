/**
 * API Models and Types
 * Definitions for API requests and responses
 */

export type AnalysisType = 'disease';

/**
 * Response from analysis service
 * Contains diagnosis information with confidence scores
 */
export interface AnalysisResponse {
  id: string;
  type: AnalysisType;
  result: string;
  confidence: number; // 0.0 - 1.0
  description: string;
  recommendations: string[];
  timestamp: string; // ISO 8601
  processingTime: number; // milliseconds
}

/**
 * Request payload for analysis
 * Sent to the API service
 */
export interface AnalysisRequest {
  imageUri: string;
  analysisType: AnalysisType;
}

/**
 * Error response from API
 */
export interface ApiErrorResponse {
  error: string;
  code: string;
  timestamp: string;
  details?: Record<string, unknown>;
}

/**
 * Metadata about the analysis result
 */
export interface AnalysisMetadata {
  imageWidth?: number;
  imageHeight?: number;
  imageFormat?: string;
  processingDevice?: 'cpu' | 'gpu' | 'neural_engine';
  modelVersion?: string;
}
