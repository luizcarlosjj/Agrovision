/**
 * Loading Spinner Component
 * Displays loading indicator with optional text
 */

import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface LoadingSpinnerProps {
  visible?: boolean;
  message?: string;
  size?: 'small' | 'large';
  color?: string;
}

export function LoadingSpinner({
  visible = true,
  message,
  size = 'large',
  color = COLORS.PRIMARY,
}: LoadingSpinnerProps) {
  if (!visible) return null;

  return (
    <View style={styles.container}>
      <ActivityIndicator size={size} color={color} />
      {message && (
        <Text style={styles.message}>{message}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: UI.SPACING_LG,
  },
  message: {
    marginTop: UI.SPACING_MD,
    fontSize: UI.FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
  },
});
