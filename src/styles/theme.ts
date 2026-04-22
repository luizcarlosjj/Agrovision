/**
 * Theme Configuration
 * Centralized design system tokens
 */

import {
  COLORS,
  UI,
  RADIUS_SM,
  RADIUS_MD,
  RADIUS_LG,
  RADIUS_XL,
  FONT_2XL,
  FONT_XL,
  FONT_LG,
  FONT_BASE,
  FONT_SM,
} from '@utils/constants';

/**
 * Complete theme object
 */
export const theme = {
  colors: COLORS,
  spacing: UI,

  /**
   * Shadow styles
   */
  shadows: {
    sm: {
      shadowColor: COLORS.BLACK,
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.08,
      shadowRadius: 2,
      elevation: 1,
    },
    md: {
      shadowColor: COLORS.BLACK,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    lg: {
      shadowColor: COLORS.BLACK,
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.15,
      shadowRadius: 8,
      elevation: 5,
    },
  },

  /**
   * Border radius
   */
  radius: {
    sm: RADIUS_SM,
    md: RADIUS_MD,
    lg: RADIUS_LG,
    xl: RADIUS_XL,
    full: 999,
  },

  /**
   * Typography styles
   */
  typography: {
    h1: {
      fontSize: FONT_2XL,
      fontWeight: '700',
      lineHeight: 32,
    },
    h2: {
      fontSize: FONT_XL,
      fontWeight: '700',
      lineHeight: 28,
    },
    h3: {
      fontSize: FONT_LG,
      fontWeight: '600',
      lineHeight: 24,
    },
    body: {
      fontSize: FONT_BASE,
      fontWeight: '400',
      lineHeight: 20,
    },
    caption: {
      fontSize: FONT_SM,
      fontWeight: '400',
      lineHeight: 16,
    },
  },
};

export type Theme = typeof theme;
