/**
 * useCamera Hook
 * Custom hook for camera operations
 * Handles camera and gallery access with automatic permission management
 */

import { useState, useCallback } from 'react';
import { cameraService } from '@services';
import { logger } from '@utils/logger';

/**
 * Hook return type
 */
interface UseCameraReturn {
  permissionError: string | null;
  takePhoto: () => Promise<string | null>;
  pickFromGallery: () => Promise<string | null>;
}

/**
 * Hook for camera operations
 * Simplified version that handles permissions transparently
 */
export function useCamera(): UseCameraReturn {
  const [permissionError, setPermissionError] = useState<string | null>(null);

  /**
   * Take photo with camera (with auto permission handling)
   */
  const takePhoto = useCallback(async (): Promise<string | null> => {
    try {
      setPermissionError(null);
      logger.log('[useCamera] Opening camera');

      // This will handle permissions internally
      const photoUri = await cameraService.launchCamera();

      if (photoUri) {
        logger.success('[useCamera] Photo captured');
        return photoUri;
      }

      // User cancelled the camera
      logger.log('[useCamera] Photo capture cancelled');
      return null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao capturar foto';
      logger.error('[useCamera] Error taking photo:', error);
      setPermissionError(message);
      return null;
    }
  }, []);

  /**
   * Pick image from gallery
   */
  const pickFromGallery = useCallback(async (): Promise<string | null> => {
    try {
      setPermissionError(null);
      logger.log('[useCamera] Opening gallery');

      const imageUri = await cameraService.pickImageFromGallery();

      if (imageUri) {
        logger.success('[useCamera] Image selected');
        return imageUri;
      }

      // User cancelled the gallery
      logger.log('[useCamera] Gallery selection cancelled');
      return null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao selecionar imagem';
      logger.error('[useCamera] Error picking image:', error);
      setPermissionError(message);
      return null;
    }
  }, []);

  return {
    permissionError,
    takePhoto,
    pickFromGallery,
  };
}
