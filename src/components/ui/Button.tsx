/**
 * Button Component
 * Reusable button with multiple variants - Modern & Spacious Design
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  TouchableOpacityProps,
  ActivityIndicator,
  View,
  Platform,
} from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface ButtonProps extends TouchableOpacityProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  disabled?: boolean;
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  size = 'md',
  fullWidth = false,
  icon,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      style={[
        styles.button,
        styles[variant],
        styles[`size_${size}`],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color="#FFF" size="small" />
      ) : (
        <>
          {icon && icon}
          <Text style={[styles.text, styles[`textSize_${size}`]]}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 18,
    minHeight: UI.MIN_TOUCH_TARGET,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.18,
        shadowRadius: 10,
      },
      android: {
        elevation: 8,
      },
    }),
  },
  text: {
    fontWeight: '700',
    color: '#FFF',
    letterSpacing: 0.5,
  },
  // Variants - Modern Colors
  primary: {
    backgroundColor: COLORS.PRIMARY,
  },
  secondary: {
    backgroundColor: COLORS.SECONDARY,
    borderWidth: 2,
    borderColor: COLORS.PRIMARY,
  },
  danger: {
    backgroundColor: COLORS.DANGER,
  },
  success: {
    backgroundColor: COLORS.SUCCESS,
  },
  // Sizes - More Spacious
  size_sm: {
    paddingHorizontal: UI.SPACING_MD,
    paddingVertical: 10,
  },
  size_md: {
    paddingHorizontal: UI.SPACING_LG,
    paddingVertical: 14,
  },
  size_lg: {
    paddingHorizontal: 28,
    paddingVertical: 22,
    minHeight: 64,
  },
  // Text sizes
  textSize_sm: {
    fontSize: UI.FONT_SM,
  },
  textSize_md: {
    fontSize: UI.FONT_BASE,
  },
  textSize_lg: {
    fontSize: 18,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  // Disabled state
  disabled: {
    opacity: 0.6,
  },
  fullWidth: {
    width: '100%',
  },
});
