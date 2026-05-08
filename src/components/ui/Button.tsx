/**
 * Button Component
 * Reusable button with multiple variants
 */

import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  TouchableOpacityProps,
  ActivityIndicator,
  View,
} from 'react-native';
import { COLORS, UI } from '@utils/constants';

interface ButtonProps extends TouchableOpacityProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success';
  disabled?: boolean;
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  icon?: React.ReactNode;
}

const LIGHT_VARIANTS = ['secondary', 'outline'];

export function Button({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  size = 'md',
  fullWidth = false,
  icon,
  style,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;
  const isLight = LIGHT_VARIANTS.includes(variant);

  return (
    <TouchableOpacity
      style={[
        styles.button,
        styles[variant],
        styles[`size_${size}`],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.75}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={isLight ? COLORS.PRIMARY : '#FFF'} size="small" />
      ) : (
        <View style={styles.inner}>
          {icon && <View style={styles.iconWrap}>{icon}</View>}
          <Text style={[
            styles.text,
            styles[`textSize_${size}`],
            isLight && styles.textDark,
          ]}>
            {title}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: UI.borderRadius.xl,
    minHeight: UI.MIN_TOUCH_TARGET,
    shadowColor: '#1C2B22',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.12,
    shadowRadius: 8,
    elevation: 4,
  },
  inner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrap: {
    marginRight: 8,
  },
  text: {
    fontWeight: '700',
    color: '#FFF',
    letterSpacing: 0.3,
  },
  textDark: {
    color: COLORS.PRIMARY,
  },

  // Variants
  primary: {
    backgroundColor: COLORS.PRIMARY,
  },
  secondary: {
    backgroundColor: COLORS.SURFACE_2,
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
    shadowOpacity: 0.05,
    elevation: 1,
  },
  outline: {
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
    shadowOpacity: 0,
    elevation: 0,
  },
  danger: {
    backgroundColor: COLORS.DANGER,
  },
  success: {
    backgroundColor: COLORS.SUCCESS,
  },

  // Sizes
  size_sm: {
    paddingHorizontal: UI.spacing.md,
    paddingVertical: 9,
    minHeight: 38,
  },
  size_md: {
    paddingHorizontal: UI.spacing.lg,
    paddingVertical: 13,
  },
  size_lg: {
    paddingHorizontal: 28,
    paddingVertical: 16,
    minHeight: 56,
  },

  // Text sizes
  textSize_sm: {
    fontSize: UI.fontSize.sm,
  },
  textSize_md: {
    fontSize: UI.fontSize.md,
  },
  textSize_lg: {
    fontSize: UI.fontSize.lg,
    letterSpacing: 0.2,
  },

  disabled: {
    opacity: 0.5,
  },
  fullWidth: {
    width: '100%',
  },
});
