/**
 * Home Screen
 */

import { View, Text, StyleSheet, TouchableOpacity, StatusBar } from 'react-native';
import { SafeAreaWrapper } from '@components';
import { HomeScreenProps } from '@navigation/types';
import {
  COLORS,
  SPACING_MD,
  SPACING_LG,
  SPACING_SM,
  SPACING_XL,
  FONT_2XL,
  FONT_XL,
  FONT_BASE,
  FONT_SM,
  FONT_XS,
  RADIUS_LG,
  RADIUS_XL,
  UI,
} from '@utils/constants';

export function HomeScreen({ navigation }: HomeScreenProps) {
  return (
    <SafeAreaWrapper scrollable padding={0}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.BACKGROUND} />

      {/* ── Brand Header ── */}
      <View style={styles.brandHeader}>
        <View style={styles.logoWrap}>
          <Text style={styles.logoEmoji}>🌾</Text>
        </View>
        <View>
          <Text style={styles.brandName}>AgroVision</Text>
          <Text style={styles.brandTagline}>Diagnóstico de doenças do milho por IA</Text>
        </View>
      </View>

      <View style={styles.content}>
        {/* ── Main Action Card ── */}
        <TouchableOpacity
          activeOpacity={0.82}
          onPress={() => navigation.navigate('Camera', { analysisType: 'disease' })}
          style={styles.mainCard}
        >
          <View style={styles.mainCardTopBar} />
          <View style={styles.mainCardBody}>
            <Text style={styles.mainCardEmoji}>🌽</Text>
            <Text style={styles.mainCardTitle}>Diagnosticar Doença</Text>
            <Text style={styles.mainCardDesc}>
              Fotografe uma folha de milho e a IA identifica a doença e sugere o manejo em segundos.
            </Text>
            <View style={styles.mainCardCta}>
              <Text style={styles.mainCardCtaText}>Iniciar análise →</Text>
            </View>
          </View>
        </TouchableOpacity>

        {/* ── How it works ── */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Como funciona</Text>
          <View style={styles.stepsRow}>
            {STEPS.map((s, i) => (
              <View key={i} style={styles.stepItem}>
                <View style={styles.stepCircle}>
                  <Text style={styles.stepEmoji}>{s.emoji}</Text>
                </View>
                <Text style={styles.stepLabel}>{s.label}</Text>
              </View>
            ))}
          </View>
        </View>

      </View>
    </SafeAreaWrapper>
  );
}

const STEPS = [
  { emoji: '📸', label: 'Fotografe\na folha' },
  { emoji: '🧠', label: 'IA analisa\na imagem' },
  { emoji: '📋', label: 'Receba o\ndiagnóstico' },
];

const styles = StyleSheet.create({
  brandHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING_LG,
    paddingTop: SPACING_LG,
    paddingBottom: SPACING_MD,
    backgroundColor: COLORS.SURFACE,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER,
    gap: SPACING_MD,
  },
  logoWrap: {
    width: 52,
    height: 52,
    borderRadius: 16,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  logoEmoji: {
    fontSize: 28,
  },
  brandName: {
    fontSize: FONT_XL,
    fontWeight: '800',
    color: COLORS.PRIMARY,
    letterSpacing: -0.5,
  },
  brandTagline: {
    fontSize: FONT_XS,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
    fontWeight: '500',
  },

  content: {
    padding: SPACING_MD,
    gap: SPACING_MD,
  },

  mainCard: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_XL,
    overflow: 'hidden',
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.14,
    shadowRadius: 16,
    elevation: 6,
    marginTop: SPACING_SM,
  },
  mainCardTopBar: {
    height: 5,
    backgroundColor: COLORS.PRIMARY,
  },
  mainCardBody: {
    padding: SPACING_LG,
    alignItems: 'center',
  },
  mainCardEmoji: {
    fontSize: 72,
    marginBottom: SPACING_MD,
  },
  mainCardTitle: {
    fontSize: FONT_2XL,
    fontWeight: '800',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_SM,
    letterSpacing: -0.5,
  },
  mainCardDesc: {
    fontSize: FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: SPACING_LG,
  },
  mainCardCta: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: SPACING_XL,
    paddingVertical: 14,
    borderRadius: UI.borderRadius.round,
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  mainCardCtaText: {
    color: COLORS.WHITE,
    fontWeight: '700',
    fontSize: FONT_BASE,
    letterSpacing: 0.3,
  },

  section: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_LG,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  sectionTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_MD,
  },
  stepsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stepItem: {
    alignItems: 'center',
    flex: 1,
  },
  stepCircle: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING_SM,
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  stepEmoji: {
    fontSize: 26,
  },
  stepLabel: {
    fontSize: FONT_XS,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 16,
    fontWeight: '500',
  },

});
