/**
 * Logger Utility
 * Centralized logging system for debugging and monitoring
 */

const isDev = process.env.NODE_ENV === 'development';
const enableDebugLogging = process.env.ENABLE_DEBUG_LOGGING === 'true';

/**
 * Logger object with methods for different log levels
 */
export const logger = {
  /**
   * Log informational messages
   */
  log: (message: string, data?: any) => {
    if (isDev || enableDebugLogging) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] ${message}`, data ? data : '');
    }
  },

  /**
   * Log warning messages
   */
  warn: (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    console.warn(`[${timestamp}] ⚠️  ${message}`, data ? data : '');
  },

  /**
   * Log error messages
   */
  error: (message: string, error?: any) => {
    const timestamp = new Date().toISOString();
    console.error(`[${timestamp}] ❌ ${message}`, error ? error : '');
  },

  /**
   * Log debug messages (only in dev)
   */
  debug: (message: string, data?: any) => {
    if (isDev) {
      const timestamp = new Date().toISOString();
      console.debug(`[${timestamp}] 🔍 ${message}`, data ? data : '');
    }
  },

  /**
   * Log success messages
   */
  success: (message: string, data?: any) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ✅ ${message}`, data ? data : '');
  },
};
