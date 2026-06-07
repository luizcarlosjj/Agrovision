import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaWrapper } from '@components';
import { databaseService } from '@services/storage/database';
import { Analysis, XAITestRecord } from '@models';
import { exportLogsToExcel } from '@utils/excelExport';
import { COLORS, UI } from '@utils/constants';

type Tab = 'consultas' | 'auditorias';

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR');
  } catch {
    return iso;
  }
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 80 ? COLORS.SUCCESS : pct >= 60 ? COLORS.WARNING : COLORS.ERROR;
  return (
    <View style={[styles.badge, { backgroundColor: color + '22' }]}>
      <Text style={[styles.badgeText, { color }]}>{pct}%</Text>
    </View>
  );
}

function AnalysisCard({ item }: { item: Analysis }) {
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle} numberOfLines={1}>
          {item.result}
        </Text>
        <ConfidenceBadge value={item.confidence} />
      </View>
      <Text style={styles.cardMeta}>{formatDate(item.timestamp)}</Text>
      <Text style={styles.cardDesc} numberOfLines={2}>
        {item.description}
      </Text>
      {item.recommendations.length > 0 && (
        <Text style={styles.cardRec} numberOfLines={1}>
          💡 {item.recommendations[0]}
        </Text>
      )}
      <Text style={styles.cardSub}>
        Processamento: {item.processingTime} ms · Tipo: {item.type}
      </Text>
    </View>
  );
}

function XAICard({ item }: { item: XAITestRecord }) {
  const labelColor =
    item.label === 'bem_enquadrada'
      ? COLORS.SUCCESS
      : item.label === 'mal_enquadrada'
      ? COLORS.WARNING
      : COLORS.TEXT_SECONDARY;
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle} numberOfLines={1}>
          {item.prediction}
        </Text>
        <ConfidenceBadge value={item.confidence} />
      </View>
      <Text style={styles.cardMeta}>{formatDate(item.createdAt)}</Text>
      <View style={styles.metricsRow}>
        <View style={styles.metricChip}>
          <Text style={styles.metricLabel}>AL</Text>
          <Text style={styles.metricValue}>{item.al.toFixed(3)}</Text>
        </View>
        <View style={styles.metricChip}>
          <Text style={styles.metricLabel}>AFS</Text>
          <Text style={styles.metricValue}>{item.afs.toFixed(3)}</Text>
        </View>
        <View style={styles.metricChip}>
          <Text style={styles.metricLabel}>Threshold</Text>
          <Text style={styles.metricValue}>{item.threshold.toFixed(2)}</Text>
        </View>
        <View style={[styles.metricChip, { backgroundColor: labelColor + '22' }]}>
          <Text style={[styles.metricLabel, { color: labelColor }]}>Rótulo</Text>
          <Text style={[styles.metricValue, { color: labelColor }]}>
            {item.label.replace('_', ' ')}
          </Text>
        </View>
      </View>
      <Text style={styles.cardSub}>Estratégia: {item.bboxStrategy}</Text>
    </View>
  );
}

export function HistoryScreen() {
  const [activeTab, setActiveTab] = useState<Tab>('consultas');
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [xaiTests, setXAITests] = useState<XAITestRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [a, x] = await Promise.all([
        databaseService.getAllAnalysesUnlimited(),
        databaseService.getAllXAITestsUnlimited(),
      ]);
      setAnalyses(a);
      setXAITests(x);
    } catch (e) {
      Alert.alert('Erro', 'Não foi possível carregar o histórico.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleExport = useCallback(async () => {
    if (analyses.length === 0 && xaiTests.length === 0) {
      Alert.alert('Nenhum dado', 'Não há registros para exportar ainda.');
      return;
    }
    setExporting(true);
    try {
      await exportLogsToExcel(analyses, xaiTests);
    } catch (e: any) {
      Alert.alert('Erro na exportação', e?.message ?? 'Tente novamente.');
    } finally {
      setExporting(false);
    }
  }, [analyses, xaiTests]);

  const currentList = activeTab === 'consultas' ? analyses : xaiTests;

  return (
    <SafeAreaWrapper scrollable={false} padding={0}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📋 Histórico</Text>
        <TouchableOpacity
          style={[styles.exportBtn, exporting && styles.exportBtnDisabled]}
          onPress={handleExport}
          disabled={exporting}
          activeOpacity={0.8}
        >
          {exporting ? (
            <ActivityIndicator size="small" color={COLORS.WHITE} />
          ) : (
            <Text style={styles.exportBtnText}>⬇ Exportar Excel</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'consultas' && styles.tabActive]}
          onPress={() => setActiveTab('consultas')}
        >
          <Text style={[styles.tabText, activeTab === 'consultas' && styles.tabTextActive]}>
            🌱 Consultas ({analyses.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'auditorias' && styles.tabActive]}
          onPress={() => setActiveTab('auditorias')}
        >
          <Text style={[styles.tabText, activeTab === 'auditorias' && styles.tabTextActive]}>
            🔬 Auditorias XAI ({xaiTests.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.loadingText}>Carregando histórico...</Text>
        </View>
      ) : currentList.length === 0 ? (
        <View style={styles.center}>
          <Text style={styles.emptyIcon}>
            {activeTab === 'consultas' ? '🌾' : '🔬'}
          </Text>
          <Text style={styles.emptyTitle}>Nenhum registro</Text>
          <Text style={styles.emptyDesc}>
            {activeTab === 'consultas'
              ? 'Faça sua primeira análise para ver o histórico aqui.'
              : 'Use o Modo Científico para gerar auditorias XAI.'}
          </Text>
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={styles.list}
          showsVerticalScrollIndicator={false}
        >
          {activeTab === 'consultas'
            ? (analyses as Analysis[]).map((item) => (
                <AnalysisCard key={item.id} item={item} />
              ))
            : (xaiTests as XAITestRecord[]).map((item) => (
                <XAICard key={item.id} item={item} />
              ))}
          <View style={{ height: 32 }} />
        </ScrollView>
      )}
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: UI.spacing.md,
    paddingVertical: UI.spacing.md,
    backgroundColor: COLORS.SURFACE,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER,
  },
  headerTitle: {
    fontSize: UI.fontSize.xl,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  exportBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: UI.spacing.md,
    paddingVertical: UI.spacing.sm,
    borderRadius: UI.borderRadius.md,
    minWidth: 140,
    justifyContent: 'center',
  },
  exportBtnDisabled: {
    opacity: 0.6,
  },
  exportBtnText: {
    color: COLORS.WHITE,
    fontWeight: '600',
    fontSize: UI.fontSize.sm,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: COLORS.SURFACE,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.BORDER,
  },
  tab: {
    flex: 1,
    paddingVertical: UI.spacing.sm + 2,
    alignItems: 'center',
  },
  tabActive: {
    borderBottomWidth: 2,
    borderBottomColor: COLORS.PRIMARY,
  },
  tabText: {
    fontSize: UI.fontSize.sm,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  tabTextActive: {
    color: COLORS.PRIMARY,
    fontWeight: '700',
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: UI.spacing.xl,
  },
  loadingText: {
    marginTop: UI.spacing.md,
    color: COLORS.TEXT_SECONDARY,
    fontSize: UI.fontSize.sm,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: UI.spacing.md,
  },
  emptyTitle: {
    fontSize: UI.fontSize.lg,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: UI.spacing.sm,
  },
  emptyDesc: {
    fontSize: UI.fontSize.sm,
    color: COLORS.TEXT_SECONDARY,
    textAlign: 'center',
    lineHeight: 20,
  },
  list: {
    padding: UI.spacing.md,
    gap: UI.spacing.sm,
  },
  card: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: UI.borderRadius.md,
    padding: UI.spacing.md,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    ...UI.shadows.small,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: UI.fontSize.md,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    flex: 1,
    marginRight: UI.spacing.sm,
  },
  cardMeta: {
    fontSize: UI.fontSize.xs,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: UI.spacing.sm,
  },
  cardDesc: {
    fontSize: UI.fontSize.sm,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 18,
    marginBottom: 4,
  },
  cardRec: {
    fontSize: UI.fontSize.xs,
    color: COLORS.PRIMARY,
    marginBottom: 4,
  },
  cardSub: {
    fontSize: UI.fontSize.xs,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 4,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: UI.borderRadius.round,
  },
  badgeText: {
    fontSize: UI.fontSize.xs,
    fontWeight: '700',
  },
  metricsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 4,
  },
  metricChip: {
    backgroundColor: COLORS.GRAY_100,
    borderRadius: UI.borderRadius.sm,
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 10,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  metricValue: {
    fontSize: UI.fontSize.xs,
    color: COLORS.TEXT_PRIMARY,
    fontWeight: '700',
  },
});
