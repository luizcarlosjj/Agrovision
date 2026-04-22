/**
 * Custom Error Classes
 * Application-specific error types
 */

/**
 * Base application error
 */
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public details?: unknown,
  ) {
    super(message);
    this.name = 'AppError';
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

/**
 * Camera permission error
 */
export class CameraPermissionError extends AppError {
  constructor(message = 'Camera permission denied') {
    super('CAMERA_PERMISSION_DENIED', message);
    this.name = 'CameraPermissionError';
    Object.setPrototypeOf(this, CameraPermissionError.prototype);
  }
}

/**
 * Image analysis error
 */
export class AnalysisError extends AppError {
  constructor(message = 'Image analysis failed') {
    super('ANALYSIS_FAILED', message);
    this.name = 'AnalysisError';
    Object.setPrototypeOf(this, AnalysisError.prototype);
  }
}

/**
 * Network/API error
 */
export class NetworkError extends AppError {
  constructor(
    public statusCode?: number,
    message = 'Network request failed',
  ) {
    super('NETWORK_ERROR', message);
    this.name = 'NetworkError';
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

/**
 * Database error
 */
export class DatabaseError extends AppError {
  constructor(message = 'Database operation failed') {
    super('DATABASE_ERROR', message);
    this.name = 'DatabaseError';
    Object.setPrototypeOf(this, DatabaseError.prototype);
  }
}

/**
 * Validation error
 */
export class ValidationError extends AppError {
  constructor(
    public fieldName?: string,
    message = 'Validation failed',
  ) {
    super('VALIDATION_ERROR', message);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * Not found error
 */
export class NotFoundError extends AppError {
  constructor(
    public resource: string,
    message = `${resource} not found`,
  ) {
    super('NOT_FOUND', message);
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * Timeout error
 */
export class TimeoutError extends AppError {
  constructor(message = 'Operation timed out') {
    super('TIMEOUT', message);
    this.name = 'TimeoutError';
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}

/**
 * Type guard to check if error is AppError
 */
export function isAppError(error: unknown): error is AppError {
  return error instanceof AppError;
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AppError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unexpected error occurred';
}

/**
 * Get error code for error tracking
 */
export function getErrorCode(error: unknown): string {
  if (error instanceof AppError) {
    return error.code;
  }

  if (error instanceof Error) {
    return error.name;
  }

  return 'UNKNOWN_ERROR';
}
