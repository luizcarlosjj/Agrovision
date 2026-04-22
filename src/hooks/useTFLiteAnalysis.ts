/**
 * Hook para análise com TFLite
 * Carrega modelos e executa predições offline
 */

import { useState, useEffect } from 'react';
import { getTFLiteService, PredictionResult } from '../services/ml/tfliteService';

type AnalysisType = 'disease' | 'health' | 'species' | 'pest';

interface UseTFLiteAnalysisState {
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  modelsReady: Record<AnalysisType, boolean>;
}

export function useTFLiteAnalysis() {
  const [state, setState] = useState<UseTFLiteAnalysisState>({
    isLoading: true,
    isInitialized: false,
    error: null,
    modelsReady: {
      disease: false,
      health: false,
      species: false,
      pest: false,
    },
  });

  // Inicializar modelos ao montar o hook
  useEffect(() => {
    const initModels = async () => {
      try {
        const tflite = await getTFLiteService();
        const status = tflite.getStatus();

        setState((prev) => ({
          ...prev,
          isInitialized: true,
          isLoading: false,
          modelsReady: status as Record<AnalysisType, boolean>,
        }));
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Failed to initialize models',
        }));
      }
    };

    initModels();
  }, []);

  // Função para fazer predição
  const predict = async (
    imageUri: string,
    analysisType: AnalysisType
  ): Promise<PredictionResult | null> => {
    try {
      if (!state.modelsReady[analysisType]) {
        console.warn(`Model '${analysisType}' not ready`);
        return null;
      }

      const tflite = await getTFLiteService();
      const result = await tflite.predict(imageUri, analysisType);

      return result;
    } catch (error) {
      console.error(`Error predicting ${analysisType}:`, error);
      return null;
    }
  };

  return {
    ...state,
    predict,
    isReady: state.isInitialized && !state.isLoading,
  };
}
