/**
 * Safe Area Wrapper Component
 * Wraps content with safe area view and default styling
 */

import React, { ReactNode } from 'react';
import { ScrollView, View, StyleSheet, ViewProps } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { COLORS, UI, SPACING_MD } from '@utils/constants';

interface SafeAreaWrapperProps extends ViewProps {
  children: ReactNode;
  scrollable?: boolean;
  padding?: number;
}

export function SafeAreaWrapper({
  children,
  scrollable = false,
  padding = SPACING_MD,
  style,
  ...props
}: SafeAreaWrapperProps) {
  const insets = useSafeAreaInsets();

  const containerStyle = [
    styles.container,
    {
      paddingTop: insets.top + padding,
      paddingBottom: insets.bottom + padding,
      paddingLeft: insets.left + padding,
      paddingRight: insets.right + padding,
    },
    style,
  ];

  if (scrollable) {
    return (
      <ScrollView
        style={containerStyle}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        {...props}
      >
        {children}
      </ScrollView>
    );
  }

  return (
    <View style={containerStyle} {...props}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.BACKGROUND,
  },
  scrollContent: {
    flexGrow: 1,
  },
});
