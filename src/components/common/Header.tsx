/**
 * Header Component
 * Common header for screens with title and back button
 */

import React, { ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { COLORS, UI } from '@utils/constants';

interface HeaderProps {
  title: string;
  subtitle?: string;
  showBackButton?: boolean;
  rightComponent?: ReactNode;
}

export function Header({
  title,
  subtitle,
  showBackButton = true,
  rightComponent,
}: HeaderProps) {
  const navigation = useNavigation();

  return (
    <View style={styles.container}>
      <View style={styles.leftSection}>
        {showBackButton && (
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={styles.backButton}
          >
            <Text style={styles.backText}>‹</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.titleSection}>
        <Text style={styles.title}>{title}</Text>
        {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
      </View>

      {rightComponent && (
        <View style={styles.rightSection}>
          {rightComponent}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: UI.SPACING_MD,
    paddingVertical: UI.SPACING_MD,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER,
    backgroundColor: COLORS.WHITE,
  },
  leftSection: {
    width: 44,
    alignItems: 'flex-start',
  },
  backButton: {
    padding: UI.SPACING_SM,
  },
  backText: {
    fontSize: UI.FONT_2XL,
    color: COLORS.PRIMARY,
    fontWeight: '600',
  },
  titleSection: {
    flex: 1,
    alignItems: 'center',
  },
  title: {
    fontSize: UI.FONT_LG,
    fontWeight: '600',
    color: COLORS.TEXT_PRIMARY,
  },
  subtitle: {
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  rightSection: {
    width: 44,
    alignItems: 'flex-end',
  },
});
