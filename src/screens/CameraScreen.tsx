/**
 * Camera Screen
 * Simplified camera/gallery hybrid system
 * Uses expo-image-picker for reliable camera and gallery access
 */

import React, { useState } from 'react';
import { View, StyleSheet, Text, Image } from 'react-native';
import { SafeAreaWrapper, Button, ErrorBanner } from '@components';
import { Header } from '@components/common/Header';
import { CameraScreenProps } from '@navigation/types';
import { useCamera } from '@hooks';
import { getAnalysisTypeLabel } from '@utils/format';
import {
  COLORS,
  UI,
  SPACING_LG,
  SPACING_SM,
  SPACING_MD,
  SPACING_XL,
  FONT_XL,
  FONT_BASE,
} from '@utils/constants';

export function CameraScreen({ route, navigation }: CameraScreenProps) {
  const { analysisType } = route.params;
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const { permissionError, takePhoto, pickFromGallery } = useCamera();

  /**
   * Handle camera capture with fallback to gallery
   */
  const handleCapture = async () => {
    const uri = await takePhoto();
    if (uri) {
      setPhotoUri(uri);
    }
  };

  /**
   * Open gallery directly
   */
  const handleGallerySelect = async () => {
    const uri = await pickFromGallery();
    if (uri) {
      setPhotoUri(uri);
    }
  };

  /**
   * Handle confirm photo
   */
  const handleConfirm = () => {
    if (photoUri) {
      navigation.navigate('Processing', {
        imageUri: photoUri,
        analysisType,
      });
    }
  };

  /**
   * Handle discard photo
   */
  const handleDiscard = () => {
    setPhotoUri(null);
  };

  /**
   * Main render
   */
  return (
    <SafeAreaWrapper style={styles.container} padding={0}>
      <Header title={`Capturar - ${getAnalysisTypeLabel(analysisType)}`} />

      <View style={styles.content}>
        {photoUri ? (
          <>
            {/* Photo preview */}
            <View style={styles.previewContainer}>
              <Image
                source={{ uri: photoUri }}
                style={styles.previewImage}
              />
            </View>

            {/* Actions */}
            <View style={styles.actionsContainer}>
              <Text style={styles.instructionText}>
                Confirme a foto ou tente novamente
              </Text>

              <View style={styles.buttonGroup}>
                <View style={styles.actionButtonWrapper}>
                  <Button
                    title="🔄 Tentar Novamente"
                    onPress={handleDiscard}
                    variant="secondary"
                    fullWidth
                    size="lg"
                  />
                </View>
                <View style={styles.actionButtonWrapper}>
                  <Button
                    title="✅ Confirmar Foto"
                    onPress={handleConfirm}
                    variant="primary"
                    fullWidth
                    size="lg"
                  />
                </View>
              </View>
            </View>
          </>
        ) : (
          <>
            {/* Selection prompt */}
            <View style={styles.promptContainer}>
              <Text style={styles.promptEmoji}>📸</Text>
              <Text style={styles.promptTitle}>Escolha uma Foto</Text>
              <Text style={styles.promptText}>
                Use a câmera para capturar ou selecione da galeria
              </Text>
            </View>

            {/* Actions */}
            <View style={styles.actionsContainer}>
              {permissionError && (
                <ErrorBanner
                  visible
                  message={permissionError}
                  onDismiss={() => {}}
                />
              )}

              <View style={styles.mainActionsContainer}>
                <View style={styles.actionButton}>
                  <Text style={styles.actionButtonEmoji}>📷</Text>
                  <Button
                    title="Capturar com Câmera"
                    onPress={handleCapture}
                    variant="primary"
                    fullWidth
                  />
                </View>

                <View style={styles.actionButton}>
                  <Text style={styles.actionButtonEmoji}>🖼️</Text>
                  <Button
                    title="Abrir Galeria"
                    onPress={handleGallerySelect}
                    variant="primary"
                    fullWidth
                  />
                </View>
              </View>

              <Button
                title="← Voltar"
                onPress={() => navigation.goBack()}
                variant="secondary"
                size="md"
                fullWidth
              />
            </View>
          </>
        )}
      </View>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 0,
  },
  content: {
    flex: 1,
    justifyContent: 'space-between',
  },
  previewContainer: {
    flex: 1,
    backgroundColor: COLORS.GRAY_100,
    alignItems: 'center',
    justifyContent: 'center',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  promptContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: SPACING_LG,
  },
  promptEmoji: {
    fontSize: 72,
    marginBottom: SPACING_LG,
  },
  promptTitle: {
    fontSize: FONT_XL,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_SM,
    textAlign: 'center',
  },
  promptText: {
    fontSize: FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 22,
  },
  actionsContainer: {
    padding: SPACING_LG,
    backgroundColor: COLORS.WHITE,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
    gap: SPACING_MD,
    paddingBottom: SPACING_XL,
  },
  instructionText: {
    textAlign: 'center',
    fontSize: FONT_BASE,
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_MD,
    fontWeight: '600',
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: SPACING_MD,
    justifyContent: 'space-between',
  },
  actionButtonWrapper: {
    flex: 1,
    borderRadius: 18,
    overflow: 'hidden',
    elevation: 6,
    shadowColor: COLORS.BLACK,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
  },
  mainActionsContainer: {
    gap: SPACING_LG,
    marginBottom: SPACING_LG,
  },
  actionButton: {
    backgroundColor: COLORS.WHITE,
    borderRadius: 20,
    padding: SPACING_LG,
    borderWidth: 2,
    borderColor: COLORS.BORDER,
    alignItems: 'center',
    elevation: 8,
    shadowColor: COLORS.BLACK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
  },
  actionButtonEmoji: {
    fontSize: 40,
    marginBottom: UI.SPACING_MD,
  },
});
