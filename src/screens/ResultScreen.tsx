/**
 * Result Screen
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaWrapper, ImagePreview } from '@components';
import { Header } from '@components/common/Header';
import { ResultScreenProps } from '@navigation/types';
import { formatConfidence, formatDateTime, getAnalysisTypeEmoji } from '@utils/format';
import {
  COLORS,
  UI,
  SPACING_MD,
  SPACING_LG,
  SPACING_SM,
  SPACING_XS,
  FONT_BASE,
  FONT_SM,
  FONT_LG,
  FONT_XL,
  FONT_XS,
  RADIUS_LG,
  RADIUS_MD,
  RADIUS_XL,
} from '@utils/constants';

export function ResultScreen({ route, navigation }: ResultScreenProps) {
  const { analysis } = route.params;

  const conf = analysis.confidence;
  const confColor = conf > 0.8 ? COLORS.SUCCESS : conf > 0.6 ? COLORS.WARNING : COLORS.DANGER;
  const confLabel = conf > 0.8 ? 'Alta' : conf > 0.6 ? 'Média' : 'Baixa';
  const confBg = conf > 0.8 ? '#E8F5E0' : conf > 0.6 ? '#FFF3E0' : '#FFEBEE';

  return (
    <SafeAreaWrapper scrollable padding={0}>
      <Header title="Resultado da Análise" />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Image */}
        <ImagePreview uri={analysis.imageUri} caption="Imagem analisada" />

        {/* ── Result hero ── */}
        <View style={styles.heroCard}>
          <View style={styles.heroTop}>
            <View style={styles.heroIconWrap}>
              <Text style={styles.heroEmoji}>{getAnalysisTypeEmoji(analysis.type)}</Text>
            </View>
            <View style={styles.heroInfo}>
              <Text style={styles.heroResult}>{analysis.result}</Text>
              <View style={[styles.confBadge, { backgroundColor: confBg }]}>
                <View style={[styles.confDot, { backgroundColor: confColor }]} />
                <Text style={[styles.confBadgeText, { color: confColor }]}>
                  {confLabel} confiança · {formatConfidence(conf)}
                </Text>
              </View>
            </View>
          </View>

          {/* Confidence bar */}
          <View style={styles.barWrap}>
            <View style={styles.barBg}>
              <View style={[styles.barFill, { width: `${conf * 100}%`, backgroundColor: confColor }]} />
            </View>
            <Text style={[styles.barPct, { color: confColor }]}>{formatConfidence(conf)}</Text>
          </View>
        </View>

        {/* ── Description ── */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionIcon}>📋</Text>
            <Text style={styles.sectionTitle}>Descrição</Text>
          </View>
          <Text style={styles.sectionText}>{analysis.description}</Text>
        </View>

        {/* ── Recommendations ── */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionIcon}>💡</Text>
            <Text style={styles.sectionTitle}>Recomendações</Text>
          </View>
          {analysis.recommendations.map((rec, i) => (
            <View key={i} style={styles.recItem}>
              <View style={styles.recBullet} />
              <Text style={styles.recText}>{rec}</Text>
            </View>
          ))}
        </View>

        {/* ── Metadata ── */}
        <View style={[styles.section, styles.metaSection]}>
          <MetaRow label="Tipo de análise" value={analysis.type} />
          <MetaRow label="Data" value={formatDateTime(analysis.timestamp)} />
          <MetaRow label="Processamento" value={`${analysis.processingTime}ms`} last />
        </View>

        {/* ── Actions ── */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.btnPrimary}
            activeOpacity={0.82}
            onPress={() => navigation.navigate('AuditarModelo', {
              imageUri: analysis.imageUri,
              prediction: analysis.result,
              classKey: analysis.classKey,
              confidence: analysis.confidence,
            })}
          >
            <Text style={styles.btnPrimaryText}>🔬  Auditar Modelo (Grad-CAM)</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.btnSecondary}
            activeOpacity={0.82}
            onPress={() => navigation.popToTop()}
          >
            <Text style={styles.btnSecondaryText}>📷  Nova Análise</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.btnGhost}
            activeOpacity={0.75}
            onPress={() => navigation.popToTop()}
          >
            <Text style={styles.btnGhostText}>← Voltar ao início</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaWrapper>
  );
}

function MetaRow({ label, value, last }: { label: string; value: string; last?: boolean }) {
  return (
    <View style={[styles.metaRow, last && styles.metaRowLast]}>
      <Text style={styles.metaLabel}>{label}</Text>
      <Text style={styles.metaValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: {
    paddingBottom: SPACING_LG * 2,
  },

  // Hero card
  heroCard: {
    backgroundColor: COLORS.SURFACE,
    margin: SPACING_MD,
    borderRadius: RADIUS_XL,
    padding: SPACING_LG,
    shadowColor: '#1C2B22',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  heroTop: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING_MD,
    gap: SPACING_MD,
  },
  heroIconWrap: {
    width: 60,
    height: 60,
    borderRadius: 18,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  heroEmoji: {
    fontSize: 32,
  },
  heroInfo: {
    flex: 1,
    gap: SPACING_SM,
  },
  heroResult: {
    fontSize: FONT_XL,
    fontWeight: '800',
    color: COLORS.TEXT_PRIMARY,
    letterSpacing: -0.3,
  },
  confBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: UI.borderRadius.round,
    alignSelf: 'flex-start',
    gap: 5,
  },
  confDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  confBadgeText: {
    fontSize: FONT_XS,
    fontWeight: '700',
  },
  barWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING_SM,
  },
  barBg: {
    flex: 1,
    height: 8,
    backgroundColor: COLORS.SURFACE_2,
    borderRadius: 4,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
  barPct: {
    fontSize: FONT_SM,
    fontWeight: '700',
    width: 44,
    textAlign: 'right',
  },

  // Sections
  section: {
    backgroundColor: COLORS.SURFACE,
    marginHorizontal: SPACING_MD,
    marginBottom: SPACING_SM,
    borderRadius: RADIUS_LG,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING_SM,
    gap: SPACING_SM,
  },
  sectionIcon: {
    fontSize: 18,
  },
  sectionTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  sectionText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },

  recItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING_SM,
    gap: SPACING_SM,
  },
  recBullet: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: COLORS.PRIMARY,
    marginTop: 6,
    flexShrink: 0,
  },
  recText: {
    flex: 1,
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },

  // Metadata
  metaSection: {
    padding: 0,
    overflow: 'hidden',
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING_MD,
    paddingVertical: 11,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER,
  },
  metaRowLast: {
    borderBottomWidth: 0,
  },
  metaLabel: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  metaValue: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_PRIMARY,
    fontWeight: '600',
  },

  // Actions
  actions: {
    paddingHorizontal: SPACING_MD,
    paddingTop: SPACING_MD,
    gap: SPACING_SM,
  },
  btnPrimary: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: RADIUS_XL,
    paddingVertical: 16,
    alignItems: 'center',
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 4,
  },
  btnPrimaryText: {
    color: COLORS.WHITE,
    fontWeight: '700',
    fontSize: FONT_BASE,
    letterSpacing: 0.2,
  },
  btnSecondary: {
    backgroundColor: COLORS.SURFACE_2,
    borderRadius: RADIUS_XL,
    paddingVertical: 15,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  btnSecondaryText: {
    color: COLORS.PRIMARY,
    fontWeight: '700',
    fontSize: FONT_BASE,
  },
  btnGhost: {
    paddingVertical: SPACING_SM,
    alignItems: 'center',
  },
  btnGhostText: {
    color: COLORS.TEXT_SECONDARY,
    fontSize: FONT_SM,
    fontWeight: '500',
  },
});
