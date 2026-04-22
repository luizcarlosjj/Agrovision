/**
 * App Context
 * Global application state and configuration
 */

import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback, useRef } from 'react';
import { databaseService } from '@services';
import { logger } from '@utils/logger';

/**
 * App context state
 */
interface AppState {
  isAppInitialized: boolean;
  isDarkMode: boolean;
  appVersion: string;
}

/**
 * App context type
 */
interface AppContextType {
  state: AppState;
  initializeApp: () => Promise<void>;
  toggleDarkMode: () => void;
}

/**
 * Create context
 */
const AppContextInternal = createContext<AppContextType | undefined>(undefined);

/**
 * Initial state
 */
const initialState: AppState = {
  isAppInitialized: false,
  isDarkMode: false,
  appVersion: '1.0.0',
};

/**
 * App Provider Component
 */
export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>(initialState);
  const initializedRef = useRef(false);

  /**
   * Initialize application
   */
  const initializeApp = useCallback(async () => {
    // Skip if already initialized
    if (initializedRef.current) {
      return;
    }

    initializedRef.current = true;

    try {
      logger.log('[AppContext] Initializing application');

      // Initialize database
      await databaseService.initialize();

      setState((prev) => ({
        ...prev,
        isAppInitialized: true,
      }));

      logger.success('[AppContext] Application initialized');
    } catch (error) {
      logger.error('[AppContext] Initialization failed:', error);
      initializedRef.current = false;
      throw error;
    }
  }, []);

  /**
   * Toggle dark mode
   */
  const toggleDarkMode = useCallback(() => {
    setState((prev) => ({
      ...prev,
      isDarkMode: !prev.isDarkMode,
    }));
  }, []);

  const value: AppContextType = {
    state,
    initializeApp,
    toggleDarkMode,
  };

  return (
    <AppContextInternal.Provider value={value}>
      {children}
    </AppContextInternal.Provider>
  );
}

/**
 * Hook to use app context
 */
export function useAppContext(): AppContextType {
  const context = useContext(AppContextInternal);

  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }

  return context;
}
