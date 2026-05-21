/**
 * MetricsPanel
 *
 * Displays the XAI metrics for a single analysis:
 *   - Prediction + confidence
 *   - Attention Leakage (AL)
 *   - Attention Focus Score (AFS) with color-coded progress bar
 *   - Backend processing time
 */

import { View, Text, StyleSheet } from 'react-native';
import {
  COLORS,
  FONT_BASE,
  FONT_LG,
  FONT_SM,
  FONT_XL,
  RADIUS_MD,
  SPACING_MD,
  SPACING_SM,
  SPACING_XS,
} from '@utils/constants';

interface MetricsPanelProps {
  prediction: string;
  confidence: number;
  al: number;
  afs: number;
  processingTimeMs: number;
  bboxStrategy: string;
  layerUsed?: string;
}

const CLASS_LABELS_PT: Record<string, string> = {
  Blight: 'Helmintosporiose',
  Common_Rust: 'Ferrugem-Comum',
  Gray_Leaf_Spot: 'Mancha-Cinzenta',
  Healthy: 'Milho Saudável',
};

function toPtLabel(raw: string): string {
  return CLASS_LABELS_PT[raw] ?? raw;
}

function focusColor(afs: number): string {
  if (afs >= 0.7) return COLORS.SUCCESS;
  if (afs >= 0.4) return COLORS.WARNING;
  return COLORS.DANGER;
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`;
}

export function MetricsPanel({
  prediction,
  confidence,
  al,
  afs,
  processingTimeMs,
  bboxStrategy,
  layerUsed,
}: MetricsPanelProps) {
  const afsColor = focusColor(afs);

  return (
    <View style={styles.card}>
      <Text style={styles.prediction}>{toPtLabel(prediction)}</Text>
      <Text style={styles.confidence}>Confiança: {pct(confidence)}</Text>

      <View style={styles.metricBlock}>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>Attention Focus Score (AFS)</Text>
          <Text style={[styles.metricValue, { color: afsColor }]}>{pct(afs)}</Text>
        </View>
        <View style={styles.barTrack}>
          <View
            style={[
              styles.barFill,
              { width: `${Math.max(0, Math.min(100, afs * 100))}%`, backgroundColor: afsColor },
            ]}
          />
        </View>
      </View>

      <View style={styles.metricBlock}>
        <View style={styles.metricRow}>
          <Text style={styles.metricLabel}>Attention Leakage (AL)</Text>
          <Text style={styles.metricValueMuted}>{pct(al)}</Text>
        </View>
      </View>

      <View style={styles.meta}>
        <Text style={styles.metaText}>Estratégia bbox: {bboxStrategy}</Text>
        {layerUsed ? (
          <Text style={styles.metaText}>Camada: {layerUsed}</Text>
        ) : null}
        <Text style={styles.metaText}>Tempo: {processingTimeMs} ms</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    gap: SPACING_SM,
  },
  prediction: {
    fontSize: FONT_XL,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  confidence: {
    fontSize: FONT_BASE,
    color: COLORS.TEXT_SECONDARY,
  },
  metricBlock: {
    marginTop: SPACING_SM,
    gap: SPACING_XS,
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  metricValue: {
    fontSize: FONT_LG,
    fontWeight: '700',
  },
  metricValueMuted: {
    fontSize: FONT_LG,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  barTrack: {
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.GRAY_200,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
  meta: {
    marginTop: SPACING_SM,
    paddingTop: SPACING_SM,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
    gap: SPACING_XS,
  },
  metaText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
  },
});
