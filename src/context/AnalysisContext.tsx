/**
 * Analysis Context
 * Context for managing analysis state and operations
 */

import React, { createContext, useContext, useReducer, ReactNode, useCallback } from 'react';
import { Analysis, AnalysisAction, AnalysisState, AnalysisType } from '@models';
import { analysisService, databaseService } from '@services';
import { logger } from '@utils/logger';

/**
 * Analysis context type
 */
interface AnalysisContextType {
  state: AnalysisState;
  dispatch: React.Dispatch<AnalysisAction>;
  analyze: (imageUri: string, type: AnalysisType) => Promise<void>;
  loadHistory: () => Promise<void>;
  deleteFromHistory: (id: string) => Promise<void>;
  clearHistory: () => Promise<void>;
}

/**
 * Create context
 */
const AnalysisContextInternal = createContext<AnalysisContextType | undefined>(undefined);

/**
 * Initial state
 */
const initialState: AnalysisState = {
  currentAnalysis: null,
  isLoading: false,
  error: null,
  history: [],
  lastAnalysisType: undefined,
};

/**
 * Reducer function
 */
function analysisReducer(state: AnalysisState, action: AnalysisAction): AnalysisState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };

    case 'SET_ANALYSIS':
      return {
        ...state,
        currentAnalysis: action.payload,
        lastAnalysisType: action.payload.type,
      };

    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };

    case 'ADD_TO_HISTORY':
      return {
        ...state,
        history: [action.payload, ...state.history],
      };

    case 'SET_HISTORY':
      return { ...state, history: action.payload };

    case 'CLEAR_ANALYSIS':
      return { ...state, currentAnalysis: null };

    case 'CLEAR_ERROR':
      return { ...state, error: null };

    case 'DELETE_FROM_HISTORY':
      return {
        ...state,
        history: state.history.filter((item) => item.id !== action.payload),
      };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

/**
 * Analysis Provider Component
 */
export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  /**
   * Perform image analysis
   */
  const analyze = useCallback(
    async (imageUri: string, type: AnalysisType) => {
      try {
        dispatch({ type: 'SET_LOADING', payload: true });
        dispatch({ type: 'CLEAR_ERROR' });

        logger.log(`[AnalysisContext] Starting analysis: ${type}`);

        // Call analysis service
        const analysisResult = await analysisService.analyzeImage(imageUri, type);

        // Create full analysis object with metadata
        const analysis: Analysis = {
          ...analysisResult,
          imageUri,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        // Save to database
        await databaseService.saveAnalysis(analysis);

        // Update state
        dispatch({ type: 'SET_ANALYSIS', payload: analysis });
        dispatch({ type: 'ADD_TO_HISTORY', payload: analysis });
        dispatch({ type: 'SET_LOADING', payload: false });

        logger.log('[AnalysisContext] Analysis complete and saved');
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Erro na análise';
        logger.error('[AnalysisContext] Analysis failed:', error);
        dispatch({ type: 'SET_ERROR', payload: errorMessage });
        dispatch({ type: 'SET_LOADING', payload: false });
        throw error;
      }
    },
    [],
  );

  /**
   * Load analysis history from database
   */
  const loadHistory = useCallback(async () => {
    try {
      logger.log('[AnalysisContext] Loading history');

      const analyses = await databaseService.getAllAnalyses(50, 0);
      dispatch({ type: 'SET_HISTORY', payload: analyses });

      logger.log(`[AnalysisContext] Loaded ${analyses.length} analyses`);
    } catch (error) {
      logger.error('[AnalysisContext] Failed to load history:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Falha ao carregar histórico' });
    }
  }, []);

  /**
   * Delete analysis from history
   */
  const deleteFromHistory = useCallback(async (id: string) => {
    try {
      logger.log(`[AnalysisContext] Deleting analysis: ${id}`);

      await databaseService.deleteAnalysis(id);
      dispatch({ type: 'DELETE_FROM_HISTORY', payload: id });

      logger.log('[AnalysisContext] Analysis deleted');
    } catch (error) {
      logger.error('[AnalysisContext] Failed to delete analysis:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Falha ao deletar análise' });
    }
  }, []);

  /**
   * Clear all history
   */
  const clearHistory = useCallback(async () => {
    try {
      logger.log('[AnalysisContext] Clearing history');

      await databaseService.clearAllAnalyses();
      dispatch({ type: 'SET_HISTORY', payload: [] });

      logger.log('[AnalysisContext] History cleared');
    } catch (error) {
      logger.error('[AnalysisContext] Failed to clear history:', error);
      dispatch({ type: 'SET_ERROR', payload: 'Falha ao limpar histórico' });
    }
  }, []);

  const value: AnalysisContextType = {
    state,
    dispatch,
    analyze,
    loadHistory,
    deleteFromHistory,
    clearHistory,
  };

  return (
    <AnalysisContextInternal.Provider value={value}>
      {children}
    </AnalysisContextInternal.Provider>
  );
}

/**
 * Hook to use analysis context
 */
export function useAnalysisContext(): AnalysisContextType {
  const context = useContext(AnalysisContextInternal);

  if (!context) {
    throw new Error('useAnalysisContext must be used within AnalysisProvider');
  }

  return context;
}
