/**
 * useAnalysis Hook
 * Custom hook for analysis operations
 */

import { useCallback } from 'react';
import { useAnalysisContext } from '@context';
import { AnalysisType, Analysis } from '@models';

/**
 * Hook return type
 */
interface UseAnalysisReturn {
  currentAnalysis: Analysis | null;
  isLoading: boolean;
  error: string | null;
  analyze: (imageUri: string, type: AnalysisType) => Promise<void>;
  clearAnalysis: () => void;
  clearError: () => void;
}

/**
 * Hook for analysis operations
 */
export function useAnalysis(): UseAnalysisReturn {
  const { state, dispatch, analyze: contextAnalyze } = useAnalysisContext();

  const analyze = useCallback(
    async (imageUri: string, type: AnalysisType) => {
      await contextAnalyze(imageUri, type);
    },
    [contextAnalyze],
  );

  const clearAnalysis = useCallback(() => {
    dispatch({ type: 'CLEAR_ANALYSIS' });
  }, [dispatch]);

  const clearError = useCallback(() => {
    dispatch({ type: 'CLEAR_ERROR' });
  }, [dispatch]);

  return {
    currentAnalysis: state.currentAnalysis,
    isLoading: state.isLoading,
    error: state.error,
    analyze,
    clearAnalysis,
    clearError,
  };
}
