/**
 * App Context — inicialização global (SQLite).
 */

import React, { createContext, useContext, useState, ReactNode, useCallback, useRef } from 'react';
import { databaseService } from '@services';
import { logger } from '@utils/logger';

interface AppState {
  isAppInitialized: boolean;
  appVersion: string;
}

interface AppContextType {
  state: AppState;
  initializeApp: () => Promise<void>;
}

const AppContextInternal = createContext<AppContextType | undefined>(undefined);

const initialState: AppState = {
  isAppInitialized: false,
  appVersion: '1.0.0',
};

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>(initialState);
  const initializedRef = useRef(false);

  const initializeApp = useCallback(async () => {
    if (initializedRef.current) return;
    initializedRef.current = true;

    try {
      logger.log('[AppContext] Initializing application');
      await databaseService.initialize();
      setState((prev) => ({ ...prev, isAppInitialized: true }));
      logger.success('[AppContext] Application initialized');
    } catch (error) {
      logger.error('[AppContext] Initialization failed:', error);
      initializedRef.current = false;
      throw error;
    }
  }, []);

  return (
    <AppContextInternal.Provider value={{ state, initializeApp }}>
      {children}
    </AppContextInternal.Provider>
  );
}

export function useAppContext(): AppContextType {
  const context = useContext(AppContextInternal);
  if (!context) throw new Error('useAppContext must be used within AppProvider');
  return context;
}
