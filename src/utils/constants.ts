/**
 * App Constants
 * Colors, spacing, and UI dimensions
 */

export const COLORS = {
  PRIMARY: '#2D7A4F',
  SECONDARY: '#7CB342',
  ACCENT: '#FFA726',

  WHITE: '#FFFFFF',
  BLACK: '#000000',
  LIGHT_GRAY: '#F5F5F5',
  GRAY_100: '#F9F9F9',
  GRAY: '#E0E0E0',
  GRAY_200: '#EEEEEE',
  DARK_GRAY: '#424242',

  SUCCESS: '#4CAF50',
  ERROR: '#F44336',
  DANGER: '#F44336',
  WARNING: '#FF9800',
  INFO: '#2196F3',

  BACKGROUND: '#FFFFFF',
  SURFACE: '#FAFAFA',
  TEXT_PRIMARY: '#212121',
  TEXT_SECONDARY: '#757575',
  BORDER: '#E0E0E0',
};

export const UI = {
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 24,
    xxl: 32,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    round: 999,
  },
  shadows: {
    small: {
      shadowColor: '#000',
      shadowOpacity: 0.1,
      shadowRadius: 2,
      shadowOffset: { width: 0, height: 1 },
      elevation: 2,
    },
    medium: {
      shadowColor: '#000',
      shadowOpacity: 0.15,
      shadowRadius: 4,
      shadowOffset: { width: 0, height: 2 },
      elevation: 4,
    },
    large: {
      shadowColor: '#000',
      shadowOpacity: 0.2,
      shadowRadius: 8,
      shadowOffset: { width: 0, height: 4 },
      elevation: 8,
    },
  },
  MIN_TOUCH_TARGET: 44,
};

// Flat aliases for backward compatibility
export const SPACING_XS = UI.spacing.xs;
export const SPACING_SM = UI.spacing.sm;
export const SPACING_MD = UI.spacing.md;
export const SPACING_LG = UI.spacing.lg;
export const SPACING_XL = UI.spacing.xl;
export const SPACING_XXL = UI.spacing.xxl;

export const FONT_XS = UI.fontSize.xs;
export const FONT_SM = UI.fontSize.sm;
export const FONT_BASE = UI.fontSize.md;
export const FONT_LG = UI.fontSize.lg;
export const FONT_XL = UI.fontSize.xl;
export const FONT_XXL = UI.fontSize.xxl;
export const FONT_2XL = 32;

export const RADIUS_SM = UI.borderRadius.sm;
export const RADIUS_MD = UI.borderRadius.md;
export const RADIUS_LG = UI.borderRadius.lg;
export const RADIUS_XL = UI.borderRadius.xl;

// Camera and confidence thresholds
export const CAMERA = {
  ASPECT_RATIO: 1,
  QUALITY: 0.8,
};

export const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.6,
  LOW: 0.4,
};

// Analysis Descriptions
export const ANALYSIS_DESCRIPTIONS = {
  species: 'Identifica a espécie de sua planta com inteligência artificial',
};
