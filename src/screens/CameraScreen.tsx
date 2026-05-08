/**
 * Camera Screen
 */

import React, { useState } from 'react';
import { View, StyleSheet, Text, Image, TouchableOpacity } from 'react-native';
import { SafeAreaWrapper, ErrorBanner } from '@components';
import { Header } from '@components/common/Header';
import { CameraScreenProps } from '@navigation/types';
import { useCamera } from '@hooks';
import {
  COLORS,
  UI,
  SPACING_LG,
  SPACING_SM,
  SPACING_MD,
  FONT_XL,
  FONT_BASE,
  FONT_SM,
  RADIUS_LG,
  RADIUS_XL,
} from '@utils/constants';

export function CameraScreen({ route, navigation }: CameraScreenProps) {
  const { analysisType } = route.params;
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const { permissionError, takePhoto, pickFromGallery } = useCamera();

  const handleCapture = async () => {
    const uri = await takePhoto();
    if (uri) setPhotoUri(uri);
  };

  const handleGallerySelect = async () => {
    const uri = await pickFromGallery();
    if (uri) setPhotoUri(uri);
  };

  const handleConfirm = () => {
    if (photoUri) {
      navigation.navigate('Processing', { imageUri: photoUri, analysisType });
    }
  };

  return (
    <SafeAreaWrapper style={styles.container} padding={0}>
      <Header title="Capturar Imagem" />

      {photoUri ? (
        /* ── Preview state ── */
        <View style={styles.flex}>
          <View style={styles.previewContainer}>
            <Image source={{ uri: photoUri }} style={styles.previewImage} />
            <View style={styles.previewBadge}>
              <Text style={styles.previewBadgeText}>Prévia</Text>
            </View>
          </View>

          <View style={styles.actions}>
            <Text style={styles.actionsHint}>A foto ficou boa?</Text>
            <View style={styles.btnRow}>
              <TouchableOpacity style={styles.btnSecondary} onPress={() => setPhotoUri(null)} activeOpacity={0.8}>
                <Text style={styles.btnSecondaryText}>🔄  Tentar de novo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.btnPrimary} onPress={handleConfirm} activeOpacity={0.8}>
                <Text style={styles.btnPrimaryText}>Confirmar →</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      ) : (
        /* ── Selection state ── */
        <View style={styles.flex}>
          <View style={styles.promptArea}>
            <View style={styles.promptIconWrap}>
              <Text style={styles.promptIcon}>🍃</Text>
            </View>
            <Text style={styles.promptTitle}>Escolha uma foto</Text>
            <Text style={styles.promptDesc}>
              Capture com a câmera ou selecione da galeria.{'\n'}
              Para melhores resultados, fotografe a folha com boa iluminação.
            </Text>
          </View>

          {permissionError && (
            <ErrorBanner visible message={permissionError} onDismiss={() => {}} />
          )}

          <View style={styles.actions}>
            <TouchableOpacity style={styles.pickCard} onPress={handleCapture} activeOpacity={0.82}>
              <View style={styles.pickCardIcon}>
                <Text style={styles.pickCardEmoji}>📷</Text>
              </View>
              <View style={styles.pickCardText}>
                <Text style={styles.pickCardTitle}>Câmera</Text>
                <Text style={styles.pickCardDesc}>Fotografar agora</Text>
              </View>
              <Text style={styles.pickCardArrow}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.pickCard} onPress={handleGallerySelect} activeOpacity={0.82}>
              <View style={[styles.pickCardIcon, { backgroundColor: '#E3F2FD' }]}>
                <Text style={styles.pickCardEmoji}>🖼️</Text>
              </View>
              <View style={styles.pickCardText}>
                <Text style={styles.pickCardTitle}>Galeria</Text>
                <Text style={styles.pickCardDesc}>Selecionar imagem salva</Text>
              </View>
              <Text style={styles.pickCardArrow}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()} activeOpacity={0.75}>
              <Text style={styles.backBtnText}>← Voltar</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  container: { padding: 0 },
  flex: { flex: 1 },

  // Preview
  previewContainer: {
    flex: 1,
    backgroundColor: '#000',
    position: 'relative',
  },
  previewImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'contain',
  },
  previewBadge: {
    position: 'absolute',
    top: SPACING_MD,
    right: SPACING_MD,
    backgroundColor: 'rgba(0,0,0,0.55)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
  },
  previewBadgeText: {
    color: '#FFF',
    fontSize: 12,
    fontWeight: '600',
  },

  // Actions bar
  actions: {
    backgroundColor: COLORS.SURFACE,
    padding: SPACING_LG,
    paddingBottom: SPACING_LG,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
    gap: SPACING_MD,
    shadowColor: '#1C2B22',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 6,
  },
  actionsHint: {
    textAlign: 'center',
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  btnRow: {
    flexDirection: 'row',
    gap: SPACING_MD,
  },
  btnSecondary: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: RADIUS_XL,
    backgroundColor: COLORS.SURFACE_2,
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
    alignItems: 'center',
  },
  btnSecondaryText: {
    fontSize: FONT_BASE,
    fontWeight: '600',
    color: COLORS.TEXT_PRIMARY,
  },
  btnPrimary: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: RADIUS_XL,
    backgroundColor: COLORS.PRIMARY,
    alignItems: 'center',
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  btnPrimaryText: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.WHITE,
  },

  // Prompt area
  promptArea: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: SPACING_LG,
    gap: SPACING_MD,
  },
  promptIconWrap: {
    width: 96,
    height: 96,
    borderRadius: 32,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  promptIcon: {
    fontSize: 52,
  },
  promptTitle: {
    fontSize: FONT_XL,
    fontWeight: '800',
    color: COLORS.TEXT_PRIMARY,
    letterSpacing: -0.3,
  },
  promptDesc: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 20,
  },

  // Pick cards
  pickCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_LG,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    gap: SPACING_MD,
    shadowColor: '#1C2B22',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 6,
    elevation: 2,
  },
  pickCardIcon: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  pickCardEmoji: {
    fontSize: 24,
  },
  pickCardText: {
    flex: 1,
  },
  pickCardTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  pickCardDesc: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  pickCardArrow: {
    fontSize: 22,
    color: COLORS.TEXT_SECONDARY,
  },

  backBtn: {
    alignItems: 'center',
    paddingVertical: SPACING_SM,
  },
  backBtnText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
});
