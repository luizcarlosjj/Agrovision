/**
 * Analysis Service - Simplified for Offline Species Identification
 * Uses TFLite for local inference, falls back to mock if needed
 */

import { AnalysisResponse, AnalysisType } from '@models';
import { logger } from '@utils/logger';
import { getTFLiteService } from '../ml/tfliteService';

/**
 * Mock species identification responses (fallback only)
 */
const speciesMocks: Omit<AnalysisResponse, 'id' | 'timestamp' | 'processingTime'>[] = [
  {
    type: 'species',
    result: 'Espécie não identificada',
    confidence: 0.45,
    description: 'A imagem não apresentou características suficientes para identificar com confiança.',
    recommendations: [
      'Capturar uma foto mais clara da folha ou planta',
      'Usar boa iluminação (luz natural de preferência)',
      'Mostrar múltiplas folhas e o caule',
      'Incluir flores ou frutos se disponíveis',
      'Fotografar diferentes ângulos da planta',
      'Consultar um especialista agrícola local',
    ],
  },
];

/**
 * AnalysisService class
 * Offline-first species identification using TFLite
 */
class AnalysisService {
  /**
   * Analyzes an image for species identification
   * Priority: 1. TFLite (offline), 2. Mock fallback
   */
  async analyzeImage(
    imageUri: string,
    type: AnalysisType,
  ): Promise<AnalysisResponse> {
    try {
      // Step 1: Try TFLite first (offline)
      logger.log(`[AnalysisService] Analyzing with TFLite: ${type}`);
      const tfliteResult = await this.analyzeWithTFLite(imageUri, type);
      if (tfliteResult) {
        logger.log(`[AnalysisService] TFLite analysis successful: ${tfliteResult.result}`);
        return tfliteResult;
      }
    } catch (tfliteError) {
      logger.warn('[AnalysisService] TFLite analysis failed:', tfliteError);
    }

    // Step 2: Fallback to mock
    logger.log('[AnalysisService] Using mock fallback');
    return this.getOfflineFallback(type);
  }

  /**
   * Attempt analysis with TFLite models (offline)
   */
  private async analyzeWithTFLite(
    imageUri: string,
    type: AnalysisType,
  ): Promise<AnalysisResponse | null> {
    try {
      const tfliteService = await getTFLiteService();

      // Check if model is loaded
      if (!tfliteService.isModelLoaded(type)) {
        logger.warn(`[AnalysisService] TFLite model not loaded: ${type}`);
        return null;
      }

      // Run prediction
      const prediction = await tfliteService.predict(imageUri, type);

      if (!prediction) {
        return null;
      }

      // Convert prediction to AnalysisResponse format
      return {
        id: this.generateUUID(),
        type,
        result: prediction.result,
        confidence: prediction.confidence,
        description: prediction.description,
        recommendations: prediction.recommendations,
        timestamp: new Date().toISOString(),
        processingTime: prediction.processingTime,
      };
    } catch (error) {
      logger.error('[AnalysisService] TFLite error:', error);
      return null;
    }
  }

  /**
   * Fallback to mock response for offline mode
   */
  private getOfflineFallback(type: AnalysisType): AnalysisResponse {
    logger.log('[AnalysisService] Using mock fallback');
    const mockResult = speciesMocks[0];

    return {
      id: this.generateUUID(),
      type,
      ...mockResult,
      timestamp: new Date().toISOString(),
      processingTime: 500,
    };
  }

  /**
   * Generates a unique ID for analysis
   * Uses timestamp + random number for React Native compatibility
   */
  private generateUUID(): string {
    const timestamp = Date.now().toString(36);
    const randomStr = Math.random().toString(36).substring(2, 15);
    return `${timestamp}-${randomStr}`;
  }
}

// Export singleton instance
export const analysisService = new AnalysisService();
