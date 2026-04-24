/**
 * Home Screen
 * Main menu for selecting analysis type with colorful gradient cards
 */

import { View, Text, StyleSheet, TouchableOpacity, Dimensions } from 'react-native';
import { SafeAreaWrapper } from '@components';
import { HomeScreenProps } from '@navigation/types';
import {
  ANALYSIS_DESCRIPTIONS,
  COLORS,
  SPACING_MD,
  SPACING_LG,
  SPACING_SM,
  SPACING_XS,
  FONT_2XL,
  FONT_XL,
  FONT_BASE,
  FONT_SM,
  RADIUS_MD,
  RADIUS_LG,
} from '@utils/constants';
import { getAnalysisTypeLabel } from '@utils/format';

// Cores e gradiente para identificação de espécie
const SPECIES_COLOR = {
  gradient: ['#E5F5E5', '#B3FFB3'],
  accent: '#28A745',
  textColor: '#1B6B2B',
};

export function HomeScreen({ navigation }: HomeScreenProps) {
  const handleStartAnalysis = () => {
    navigation.navigate('Camera', { analysisType: 'species' });
  };

  const handleOpenTestMode = () => {
    navigation.navigate('TestMode');
  };

  return (
    <SafeAreaWrapper scrollable padding={SPACING_MD}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🌾 AgroVision</Text>
        <Text style={styles.subtitle}>Identificação de Espécies Vegetais</Text>
      </View>

      {/* Main Card */}
      <TouchableOpacity
        activeOpacity={0.75}
        onPress={handleStartAnalysis}
        style={[
          styles.mainCard,
          {
            backgroundColor: SPECIES_COLOR.gradient[0],
            borderColor: SPECIES_COLOR.accent,
          },
        ]}
      >
        {/* Accent bar */}
        <View style={[styles.accentBar, { backgroundColor: SPECIES_COLOR.accent }]} />

        {/* Emoji */}
        <Text style={styles.cardEmoji}>🌱</Text>

        {/* Title */}
        <Text style={[styles.cardTitle, { color: SPECIES_COLOR.textColor }]}>
          Identificar Espécie
        </Text>

        {/* Description */}
        <Text style={styles.cardDescription}>
          {ANALYSIS_DESCRIPTIONS.species}
        </Text>

        {/* CTA Button */}
        <View style={[styles.ctaButton, { backgroundColor: SPECIES_COLOR.accent }]}>
          <Text style={styles.ctaButtonText}>Iniciar Análise</Text>
        </View>
      </TouchableOpacity>

      {/* XAI / Scientific Mode entry */}
      <TouchableOpacity
        activeOpacity={0.75}
        onPress={handleOpenTestMode}
        style={styles.xaiCard}
      >
        <Text style={styles.xaiEmoji}>🔬</Text>
        <View style={{ flex: 1 }}>
          <Text style={styles.xaiTitle}>Modo Científico (XAI)</Text>
          <Text style={styles.xaiDescription}>
            Grad-CAM + Attention Leakage para avaliar onde o modelo realmente olha.
          </Text>
        </View>
        <Text style={styles.xaiArrow}>›</Text>
      </TouchableOpacity>

      {/* Info Cards */}
      <View style={styles.infoSection}>
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>📸 Como Usar</Text>
          <Text style={styles.infoText}>
            Tire uma foto clara da folha ou da planta em boa iluminação para obter melhores resultados.
          </Text>
        </View>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>✨ Recurso</Text>
          <Text style={styles.infoText}>
            100% offline - sem necessidade de conexão com internet para análise.
          </Text>
        </View>
      </View>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  header: {
    alignItems: 'center',
    marginVertical: SPACING_LG,
  },
  title: {
    fontSize: FONT_2XL,
    fontWeight: '700',
    color: COLORS.PRIMARY,
  },
  subtitle: {
    fontSize: FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
    marginTop: SPACING_SM,
  },
  mainCard: {
    borderRadius: RADIUS_LG,
    borderWidth: 2,
    padding: SPACING_LG,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    elevation: 6,
    shadowColor: COLORS.BLACK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    marginVertical: SPACING_LG,
    minHeight: 280,
  },
  accentBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 6,
  },
  cardEmoji: {
    fontSize: 64,
    marginBottom: SPACING_MD,
    marginTop: SPACING_MD,
  },
  cardTitle: {
    fontSize: FONT_XL,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: SPACING_SM,
  },
  cardDescription: {
    fontSize: FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    marginBottom: SPACING_LG,
    lineHeight: 22,
  },
  ctaButton: {
    borderRadius: RADIUS_MD,
    paddingHorizontal: SPACING_LG,
    paddingVertical: SPACING_MD,
    alignItems: 'center',
    elevation: 4,
    shadowColor: COLORS.BLACK,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  ctaButtonText: {
    color: COLORS.WHITE,
    fontWeight: '700',
    fontSize: FONT_BASE,
    letterSpacing: 0.5,
  },
  xaiCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EDE7F6',
    borderRadius: RADIUS_MD,
    borderLeftWidth: 4,
    borderLeftColor: '#5E35B1',
    padding: SPACING_MD,
    marginTop: SPACING_SM,
    gap: SPACING_SM,
  },
  xaiEmoji: {
    fontSize: 28,
    marginRight: SPACING_SM,
  },
  xaiTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: '#4527A0',
  },
  xaiDescription: {
    fontSize: FONT_SM,
    color: '#4527A0',
    marginTop: SPACING_XS,
    lineHeight: 18,
  },
  xaiArrow: {
    fontSize: 28,
    color: '#5E35B1',
    fontWeight: '700',
    marginLeft: SPACING_SM,
  },
  infoSection: {
    gap: SPACING_MD,
    marginTop: SPACING_LG,
  },
  infoCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: RADIUS_MD,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.SUCCESS,
    padding: SPACING_MD,
  },
  infoTitle: {
    fontSize: FONT_BASE,
    fontWeight: '600',
    color: COLORS.SUCCESS,
    marginBottom: SPACING_SM,
  },
  infoText: {
    fontSize: FONT_SM,
    color: COLORS.SUCCESS,
    lineHeight: 20,
  },
});
