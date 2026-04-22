/**
 * Validator Functions
 * Input validation and data validation helpers
 */

import { CAMERA, CONFIDENCE_THRESHOLDS } from './constants';

/**
 * Validate image URI
 */
export function isValidImageUri(uri: string | null | undefined): boolean {
  if (!uri || typeof uri !== 'string') {
    return false;
  }

  // Check if it's a valid file URI (file://) or base64 data
  return uri.startsWith('file://') || uri.startsWith('data:');
}

/**
 * Validate analysis type
 */
export function isValidAnalysisType(
  type: unknown,
): type is 'disease' | 'pest' | 'species' | 'nutrient' {
  return type === 'disease' || type === 'pest' || type === 'species' || type === 'nutrient';
}

/**
 * Validate confidence score
 */
export function isValidConfidence(value: number): boolean {
  return typeof value === 'number' && value >= 0 && value <= 1;
}

/**
 * Validate confidence is above threshold
 */
export function isHighConfidence(value: number): boolean {
  return value >= CONFIDENCE_THRESHOLDS.HIGH;
}

/**
 * Validate confidence is medium
 */
export function isMediumConfidence(value: number): boolean {
  return value >= CONFIDENCE_THRESHOLDS.MEDIUM && value < CONFIDENCE_THRESHOLDS.HIGH;
}

/**
 * Validate confidence is low
 */
export function isLowConfidence(value: number): boolean {
  return value >= CONFIDENCE_THRESHOLDS.LOW && value < CONFIDENCE_THRESHOLDS.MEDIUM;
}

/**
 * Validate string is not empty
 */
export function isNotEmpty(value: string | null | undefined): boolean {
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Validate array is not empty
 */
export function isArrayNotEmpty<T>(arr: T[] | null | undefined): boolean {
  return Array.isArray(arr) && arr.length > 0;
}

/**
 * Validate object has required properties
 */
export function hasRequiredProps<T extends Record<string, unknown>>(
  obj: unknown,
  requiredProps: (keyof T)[],
): obj is T {
  if (typeof obj !== 'object' || obj === null) {
    return false;
  }

  return requiredProps.every((prop) => prop in obj);
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate URL format
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate JSON string
 */
export function isValidJson(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate UUID format
 */
export function isValidUuid(uuid: string): boolean {
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

/**
 * Validate ISO date format
 */
export function isValidIsoDate(dateString: string): boolean {
  try {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date.getTime());
  } catch {
    return false;
  }
}

/**
 * Validate number is positive
 */
export function isPositive(value: number): boolean {
  return typeof value === 'number' && value > 0;
}

/**
 * Validate number is non-negative
 */
export function isNonNegative(value: number): boolean {
  return typeof value === 'number' && value >= 0;
}
