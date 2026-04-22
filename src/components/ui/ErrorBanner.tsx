/**
 * Error Banner Component
 * Displays error messages to user
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface ErrorBannerProps {
  visible?: boolean;
  message?: string;
  onDismiss?: () => void;
  onRetry?: () => void;
}

export function ErrorBanner({
  visible = true,
  message = 'Algo deu errado. Tente novamente.',
  onDismiss,
  onRetry,
}: ErrorBannerProps) {
  if (!visible || !message) return null;

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>⚠️</Text>
        <Text style={styles.message}>{message}</Text>
      </View>
      <View style={styles.actions}>
        {onRetry && (
          <TouchableOpacity onPress={onRetry} style={styles.actionButton}>
            <Text style={styles.actionText}>Tentar</Text>
          </TouchableOpacity>
        )}
        {onDismiss && (
          <TouchableOpacity onPress={onDismiss} style={styles.actionButton}>
            <Text style={styles.actionText}>✕</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.DANGER,
    borderRadius: UI.RADIUS_MD,
    padding: UI.SPACING_MD,
    marginVertical: UI.SPACING_MD,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  icon: {
    fontSize: UI.FONT_LG,
    marginRight: UI.SPACING_SM,
  },
  message: {
    flex: 1,
    color: COLORS.WHITE,
    fontSize: UI.FONT_SM,
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    gap: UI.SPACING_SM,
  },
  actionButton: {
    paddingHorizontal: UI.SPACING_MD,
    paddingVertical: UI.SPACING_SM,
  },
  actionText: {
    color: COLORS.WHITE,
    fontWeight: '600',
    fontSize: UI.FONT_SM,
  },
});
