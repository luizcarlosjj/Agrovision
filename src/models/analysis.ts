/**
 * Analysis Domain Models
 * Core data structures for plant analysis
 */

import { AnalysisType } from './api';

/**
 * Complete analysis result stored in database
 */
export interface Analysis {
  id: string;
  type: AnalysisType;
  result: string;
  classKey: string;
  confidence: number;
  description: string;
  recommendations: string[];
  imageUri: string;
  timestamp: string;
  processingTime: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Simplified analysis for history display
 */
export interface AnalysisHistoryItem {
  id: string;
  type: AnalysisType;
  result: string;
  confidence: number;
  timestamp: string;
  thumbnail?: string;
}

/**
 * Analysis state for context management
 */
export interface AnalysisState {
  currentAnalysis: Analysis | null;
  isLoading: boolean;
  error: string | null;
  history: Analysis[];
  lastAnalysisType?: AnalysisType;
}

/**
 * Actions for analysis reducer
 */
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

/**
 * Disease detection specific data
 */
export interface DiseaseResult {
  type: 'disease';
  diseaseName: string;
  affectedAreas: string[];
  severity: 'mild' | 'moderate' | 'severe';
  treatment: string[];
}

/**
 * Pest detection specific data
 */
export interface PestResult {
  type: 'pest';
  pestName: string;
  pestType: 'insect' | 'arachnid' | 'nematode' | 'disease_vector';
  severity: 'low' | 'medium' | 'high';
  treatment: string[];
}

/**
 * Species identification specific data
 */
export interface SpeciesResult {
  type: 'species';
  scientificName: string;
  commonName: string;
  family: string;
  careInstructions: string[];
}

/**
 * Nutrient deficiency detection specific data
 */
export interface NutrientResult {
  type: 'nutrient';
  deficientNutrient: string;
  symptoms: string[];
  recommendation: string[];
}

/**
 * Union type for any analysis result
 */
export type AnalysisResultType =
  | DiseaseResult
  | PestResult
  | SpeciesResult
  | NutrientResult;
