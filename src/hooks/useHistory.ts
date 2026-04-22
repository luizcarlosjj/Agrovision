/**
 * useHistory Hook
 * Custom hook for analysis history operations
 */

import { useCallback, useState } from 'react';
import { useAnalysisContext } from '@context';
import { Analysis } from '@models';
import { logger } from '@utils/logger';

/**
 * Hook return type
 */
interface UseHistoryReturn {
  history: Analysis[];
  isLoading: boolean;
  error: string | null;
  loadHistory: () => Promise<void>;
  deleteAnalysis: (id: string) => Promise<void>;
  clearHistory: () => Promise<void>;
}

/**
 * Hook for history operations
 */
export function useHistory(): UseHistoryReturn {
  const { state, loadHistory: contextLoadHistory, deleteFromHistory, clearHistory: contextClearHistory } = useAnalysisContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load history
   */
  const loadHistory = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      logger.log('[useHistory] Loading history');

      await contextLoadHistory();

      logger.log(`[useHistory] Loaded ${state.history.length} analyses`);
    } catch (err) {
      const errorMsg = 'Erro ao carregar histórico';
      logger.error('[useHistory] Error loading history:', err);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  }, [contextLoadHistory, state.history.length]);

  /**
   * Delete analysis
   */
  const deleteAnalysis = useCallback(
    async (id: string) => {
      try {
        logger.log(`[useHistory] Deleting analysis: ${id}`);

        await deleteFromHistory(id);

        logger.log('[useHistory] Analysis deleted');
      } catch (err) {
        const errorMsg = 'Erro ao deletar análise';
        logger.error('[useHistory] Error deleting analysis:', err);
        setError(errorMsg);
      }
    },
    [deleteFromHistory],
  );

  /**
   * Clear history
   */
  const clearHistory = useCallback(async () => {
    try {
      logger.log('[useHistory] Clearing history');

      await contextClearHistory();

      logger.log('[useHistory] History cleared');
    } catch (err) {
      const errorMsg = 'Erro ao limpar histórico';
      logger.error('[useHistory] Error clearing history:', err);
      setError(errorMsg);
    }
  }, [contextClearHistory]);

  return {
    history: state.history,
    isLoading,
    error,
    loadHistory,
    deleteAnalysis,
    clearHistory,
  };
}
