/**
 * Image Preview Component
 * Displays image with optional caption
 */

import React from 'react';
import { Image, View, Text, StyleSheet } from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface ImagePreviewProps {
  uri: string;
  caption?: string;
  width?: number | string;
  height?: number | string;
}

export function ImagePreview({
  uri,
  caption,
  width = '100%',
  height = 300,
}: ImagePreviewProps) {
  return (
    <View style={styles.container}>
      <Image
        source={{ uri }}
        style={[styles.image, { width, height }]}
      />
      {caption && (
        <Text style={styles.caption}>{caption}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: UI.RADIUS_LG,
    overflow: 'hidden',
    marginVertical: UI.SPACING_MD,
  },
  image: {
    backgroundColor: COLORS.GRAY_100,
  },
  caption: {
    paddingHorizontal: UI.SPACING_MD,
    paddingVertical: UI.SPACING_SM,
    backgroundColor: COLORS.GRAY_100,
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
});
