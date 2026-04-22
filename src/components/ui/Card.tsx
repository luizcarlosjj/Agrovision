/**
 * Card Component
 * Container for grouped content
 */

import React, { ReactNode } from 'react';
import { View, StyleSheet, ViewProps } from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface CardProps extends ViewProps {
  children: ReactNode;
  padding?: number;
  shadow?: boolean;
}

export function Card({
  children,
  padding = UI.SPACING_MD,
  shadow = true,
  style,
  ...props
}: CardProps) {
  return (
    <View
      style={[
        styles.card,
        { padding },
        shadow && styles.shadow,
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.WHITE,
    borderRadius: UI.RADIUS_LG,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  shadow: {
    shadowColor: COLORS.BLACK,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
});
