/**
 * Analysis Domain Models — resultado de diagnóstico de doenças do milho.
 */

import { AnalysisType } from './api';

/** Resultado completo persistido no SQLite. */
export interface Analysis {
  id: string;
  type: AnalysisType;
  result: string;
  classKey: string;
  source: 'roboflow';
  confidence: number;
  description: string;
  recommendations: string[];
  imageUri: string;
  timestamp: string;
  processingTime: number;
  createdAt: string;
  updatedAt: string;
}

/** Item resumido usado na lista de histórico. */
export interface AnalysisHistoryItem {
  id: string;
  type: AnalysisType;
  result: string;
  confidence: number;
  timestamp: string;
  thumbnail?: string;
}

export interface AnalysisState {
  currentAnalysis: Analysis | null;
  isLoading: boolean;
  error: string | null;
  history: Analysis[];
  lastAnalysisType?: AnalysisType;
}

export type AnalysisAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ANALYSIS'; payload: Analysis }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'ADD_TO_HISTORY'; payload: Analysis }
  | { type: 'SET_HISTORY'; payload: Analysis[] }
  | { type: 'CLEAR_ANALYSIS' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'DELETE_FROM_HISTORY'; payload: string }
  | { type: 'RESET' };
