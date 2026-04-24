/**
 * HeatmapOverlay
 *
 * Renders the base64 PNG overlay returned by the XAI backend. A toggle lets
 * the user switch between the original photo and the Grad-CAM overlay for
 * visual comparison.
 */

import { useState } from 'react';
import { View, Image, StyleSheet, TouchableOpacity, Text } from 'react-native';
import {
  COLORS,
  RADIUS_MD,
  SPACING_SM,
  SPACING_MD,
  FONT_SM,
} from '@utils/constants';

interface HeatmapOverlayProps {
  imageUri: string;
  overlayB64: string;
  aspectRatio?: number;
}

export function HeatmapOverlay({
  imageUri,
  overlayB64,
  aspectRatio = 1,
}: HeatmapOverlayProps) {
  const [showOverlay, setShowOverlay] = useState(true);

  const overlayUri = `data:image/png;base64,${overlayB64}`;
  const currentUri = showOverlay ? overlayUri : imageUri;

  return (
    <View style={styles.container}>
      <Image
        source={{ uri: currentUri }}
        style={[styles.image, { aspectRatio }]}
        resizeMode="contain"
      />
      <TouchableOpacity
        style={styles.toggle}
        onPress={() => setShowOverlay((v) => !v)}
        activeOpacity={0.75}
      >
        <Text style={styles.toggleText}>
          {showOverlay ? 'Ver original' : 'Ver heatmap'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: RADIUS_MD,
    overflow: 'hidden',
    backgroundColor: COLORS.GRAY_100,
    position: 'relative',
  },
  image: {
    width: '100%',
    backgroundColor: COLORS.BLACK,
  },
  toggle: {
    position: 'absolute',
    bottom: SPACING_SM,
    right: SPACING_SM,
    backgroundColor: 'rgba(0, 0, 0, 0.55)',
    paddingHorizontal: SPACING_MD,
    paddingVertical: SPACING_SM,
    borderRadius: RADIUS_MD,
  },
  toggleText: {
    color: COLORS.WHITE,
    fontWeight: '600',
    fontSize: FONT_SM,
  },
});
