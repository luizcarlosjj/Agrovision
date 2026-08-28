/**
 * Camera Service
 * Wrapper for media picker functionality
 * Handles camera and gallery access with automatic permission management
 */

import * as ImagePicker from 'expo-image-picker';
import { logger } from '@utils/logger';

/**
 * Camera service for handling device camera and gallery
 */
class CameraService {
  /**
   * Launch camera and capture photo
   * Automatically handles permissions
   */
  async launchCamera(): Promise<string | null> {
    try {
      logger.log('[CameraService] Requesting camera permissions');

      // Request camera permission
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();

      if (permissionResult.status !== 'granted') {
        const message = 'Permissão de câmera foi negada. Use a galeria para continuar.';
        logger.warn(`[CameraService] ${message}`);
        throw new Error(message);
      }

      logger.log('[CameraService] Camera permission granted, launching camera');

      // Launch camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ['images'],
        allowsEditing: false,
        quality: 0.5,
        aspect: [4, 3],
        base64: false,
      });

      // Check if user cancelled
      if (result.canceled) {
        logger.log('[CameraService] Camera capture cancelled by user');
        return null;
      }

      // Get the photo URI
      if (!result.assets || result.assets.length === 0) {
        logger.error('[CameraService] No assets returned from camera');
        return null;
      }

      const photoUri = result.assets[0].uri;
      logger.log(`[CameraService] Photo captured successfully: ${photoUri}`);

      return photoUri;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao capturar foto';
      logger.error('[CameraService] Error launching camera:', error);
      throw new Error(message);
    }
  }

  /**
   * Pick image from gallery
   */
  async pickImageFromGallery(): Promise<string | null> {
    try {
      logger.log('[CameraService] Opening image gallery');

      // Request library permission
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (permissionResult.status !== 'granted') {
        const message = 'Permissão de galeria foi negada';
        logger.warn(`[CameraService] ${message}`);
        throw new Error(message);
      }

      // Launch library
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: false,
        quality: 0.5,
        aspect: [4, 3],
        base64: false,
      });

      // Check if user cancelled
      if (result.canceled) {
        logger.log('[CameraService] Gallery selection cancelled by user');
        return null;
      }

      // Get the image URI
      if (!result.assets || result.assets.length === 0) {
        logger.error('[CameraService] No assets returned from gallery');
        return null;
      }

      const imageUri = result.assets[0].uri;
      logger.log(`[CameraService] Image selected successfully: ${imageUri}`);

      return imageUri;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Erro ao selecionar imagem';
      logger.error('[CameraService] Error picking image:', error);
      throw new Error(message);
    }
  }
}

// Export singleton instance
export const cameraService = new CameraService();
