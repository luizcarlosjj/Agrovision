/**
 * TestModeScreen (Modo Científico XAI)
 *
 * Modo científico para inspeção do modelo. Permite selecionar uma ou várias
 * imagens, roda Grad-CAM em cada uma no backend Python, exibe o overlay do
 * heatmap + métricas (Attention Leakage / Focus Score), persiste cada execução
 * em SQLite e exporta os resultados acumulados como CSV.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ActivityIndicator,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
const genId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

import { SafeAreaWrapper, Button, HeatmapOverlay, MetricsPanel } from '@components';
import { Header } from '@components/common/Header';
import {
  COLORS,
  FONT_BASE,
  FONT_LG,
  FONT_SM,
  FONT_XL,
  RADIUS_MD,
  SPACING_LG,
  SPACING_MD,
  SPACING_SM,
  SPACING_XS,
} from '@utils/constants';
import {
  analyzeWithXAI,
  checkXAIBackendHealth,
  getXAIBaseUrl,
} from '@services/ml/xaiService';
import { databaseService } from '@services/storage';
import { exportXAITestsToCSV } from '@utils/csvExport';
import {
  BBoxStrategy,
  FramingLabel,
  XAIHealth,
  XAIResult,
  XAITestRecord,
} from '@models';
import { logger } from '@utils/logger';

interface RunEntry {
  id: string;
  imageUri: string;
  status: 'pending' | 'running' | 'done' | 'error';
  error?: string;
  result?: XAIResult;
  label: FramingLabel;
}

const THRESHOLD_OPTIONS = [0.3, 0.5, 0.7];

export function TestModeScreen() {
  const [strategy, setStrategy] = useState<BBoxStrategy>('fixed');
  const [threshold, setThreshold] = useState<number>(0.5);
  const [runs, setRuns] = useState<RunEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [health, setHealth] = useState<XAIHealth | null | 'checking'>('checking');
  const [historyCount, setHistoryCount] = useState(0);

  const refreshHealth = useCallback(async () => {
    setHealth('checking');
    const h = await checkXAIBackendHealth();
    setHealth(h);
  }, []);

  const refreshHistoryCount = useCallback(async () => {
    try {
      const all = await databaseService.getAllXAITests(1000);
      setHistoryCount(all.length);
    } catch (err) {
      logger.error('[TestMode] Failed to load history count', err);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    refreshHistoryCount();
  }, [refreshHealth, refreshHistoryCount]);

  const pickImages = useCallback(async () => {
    try {
      const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!perm.granted) {
        Alert.alert('Permissão negada', 'Conceda acesso à galeria para continuar.');
        return;
      }
      const res = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'] as any,
        allowsMultipleSelection: true,
        selectionLimit: 20,
        quality: 0.9,
      });
      if (res.canceled) return;
      const entries: RunEntry[] = res.assets.map((a) => ({
        id: genId(),
        imageUri: a.uri,
        status: 'pending',
        label: 'nao_classificada',
      }));
      setRuns((prev) => [...entries, ...prev]);
    } catch (err: any) {
      Alert.alert('Erro ao abrir galeria', err?.message ?? 'Erro desconhecido');
    }
  }, []);

  const runOne = useCallback(
    async (entry: RunEntry): Promise<RunEntry> => {
      try {
        const result = await analyzeWithXAI({
          imageUri: entry.imageUri,
          bboxStrategy: strategy,
          threshold,
        });
        const record: XAITestRecord = {
          id: entry.id,
          imageUri: entry.imageUri,
          prediction: result.prediction,
          confidence: result.confidence,
          al: result.al,
          afs: result.afs,
          threshold: result.threshold,
          bbox: result.bboxUsed,
          bboxStrategy: result.bboxStrategy,
          overlayB64: result.overlayB64,
          label: entry.label,
          createdAt: new Date().toISOString(),
        };
        await databaseService.saveXAITest(record);
        return { ...entry, status: 'done', result };
      } catch (err: any) {
        logger.error('[TestMode] Run failed', err);
        const msg =
          err?.response?.data?.detail ||
          err?.message ||
          'Erro desconhecido ao contatar o backend XAI';
        return { ...entry, status: 'error', error: msg };
      }
    },
    [strategy, threshold],
  );

  const runAll = useCallback(async () => {
    const pending = runs.filter((r) => r.status === 'pending');
    if (pending.length === 0) return;
    if (health === 'checking' || health == null) {
      Alert.alert(
        'Backend offline',
        `Não consegui falar com o backend XAI em ${getXAIBaseUrl()}. Suba com "uvicorn api.server:app --port 5000" e tente novamente.`,
      );
      await refreshHealth();
      return;
    }
    setIsRunning(true);
    for (const entry of pending) {
      setRuns((prev) =>
        prev.map((r) => (r.id === entry.id ? { ...r, status: 'running' } : r)),
      );
      const updated = await runOne(entry);
      setRuns((prev) => prev.map((r) => (r.id === entry.id ? updated : r)));
    }
    setIsRunning(false);
    refreshHistoryCount();
  }, [runs, health, runOne, refreshHealth, refreshHistoryCount]);

  const clearQueue = useCallback(() => {
    setRuns([]);
  }, []);

  const setEntryLabel = useCallback((id: string, label: FramingLabel) => {
    setRuns((prev) => prev.map((r) => (r.id === id ? { ...r, label } : r)));
    databaseService.updateXAITestLabel(id, label).catch((e) => {
      logger.error('[TestMode] Failed to update label', e);
    });
  }, []);

  const exportCSV = useCallback(async () => {
    try {
      const all = await databaseService.getAllXAITests(1000);
      if (all.length === 0) {
        Alert.alert('Nada para exportar', 'Rode pelo menos um teste primeiro.');
        return;
      }
      await exportXAITestsToCSV(all);
    } catch (err: any) {
      Alert.alert('Erro ao exportar', err?.message ?? 'Erro desconhecido');
    }
  }, []);

  const clearHistory = useCallback(() => {
    Alert.alert(
      'Limpar histórico',
      `Remover todos os ${historyCount} testes XAI salvos?`,
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar',
          style: 'destructive',
          onPress: async () => {
            await databaseService.clearAllXAITests();
            refreshHistoryCount();
          },
        },
      ],
    );
  }, [historyCount, refreshHistoryCount]);

  const stats = useMemo(() => {
    const done = runs.filter((r) => r.status === 'done' && r.result);
    if (done.length === 0) return null;
    const sumAFS = done.reduce((acc, r) => acc + (r.result?.afs ?? 0), 0);
    const sumAL = done.reduce((acc, r) => acc + (r.result?.al ?? 0), 0);
    return {
      count: done.length,
      avgAFS: sumAFS / done.length,
      avgAL: sumAL / done.length,
    };
  }, [runs]);

  return (
    <SafeAreaWrapper padding={0} style={styles.safe}>
      <Header title="🔬 Modo Científico (XAI)" />

      <ScrollView contentContainerStyle={styles.scroll}>
        <BackendStatus health={health} onRefresh={refreshHealth} />

        <View style={styles.controlsCard}>
          <Text style={styles.sectionTitle}>Parâmetros</Text>

          <Text style={styles.controlLabel}>Estratégia de bounding box</Text>
          <View style={styles.pillRow}>
            {(['fixed', 'green'] as BBoxStrategy[]).map((s) => (
              <Pill
                key={s}
                label={s === 'fixed' ? 'Central fixo (80%)' : 'Segmentação verde'}
                active={strategy === s}
                onPress={() => setStrategy(s)}
              />
            ))}
          </View>

          <Text style={[styles.controlLabel, { marginTop: SPACING_MD }]}>
            Threshold (cut-off do heatmap)
          </Text>
          <View style={styles.pillRow}>
            {THRESHOLD_OPTIONS.map((t) => (
              <Pill
                key={t}
                label={t.toFixed(1)}
                active={threshold === t}
                onPress={() => setThreshold(t)}
              />
            ))}
          </View>
        </View>

        <View style={styles.actionsRow}>
          <Button
            title="Selecionar imagens"
            onPress={pickImages}
            variant="primary"
            size="md"
            fullWidth
          />
        </View>

        {runs.length > 0 && (
          <View style={styles.actionsRow}>
            <View style={{ flex: 1 }}>
              <Button
                title={isRunning ? 'Processando…' : `Rodar ${runs.filter((r) => r.status === 'pending').length} pendente(s)`}
                onPress={runAll}
                variant="success"
                size="md"
                disabled={isRunning || runs.every((r) => r.status !== 'pending')}
                fullWidth
              />
            </View>
            <View style={{ width: SPACING_SM }} />
            <View style={{ flex: 1 }}>
              <Button
                title="Limpar fila"
                onPress={clearQueue}
                variant="danger"
                size="md"
                disabled={isRunning}
                fullWidth
              />
            </View>
          </View>
        )}

        {stats && (
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>Resumo desta sessão</Text>
            <Text style={styles.summaryText}>Imagens processadas: {stats.count}</Text>
            <Text style={styles.summaryText}>
              AFS médio: {(stats.avgAFS * 100).toFixed(1)}%
            </Text>
            <Text style={styles.summaryText}>
              AL médio: {(stats.avgAL * 100).toFixed(1)}%
            </Text>
          </View>
        )}

        {runs.map((entry) => (
          <RunCard
            key={entry.id}
            entry={entry}
            onLabelChange={(label) => setEntryLabel(entry.id, label)}
          />
        ))}

        <View style={[styles.historyCard, { marginTop: SPACING_LG }]}>
          <Text style={styles.sectionTitle}>Histórico persistido</Text>
          <Text style={styles.historyText}>
            {historyCount} teste(s) salvos no SQLite
          </Text>
          <View style={[styles.actionsRow, { marginTop: SPACING_SM }]}>
            <View style={{ flex: 1 }}>
              <Button
                title="Exportar CSV"
                onPress={exportCSV}
                variant="secondary"
                size="md"
                fullWidth
              />
            </View>
            <View style={{ width: SPACING_SM }} />
            <View style={{ flex: 1 }}>
              <Button
                title="Limpar histórico"
                onPress={clearHistory}
                variant="danger"
                size="md"
                disabled={historyCount === 0}
                fullWidth
              />
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaWrapper>
  );
}

interface PillProps {
  label: string;
  active: boolean;
  onPress: () => void;
}

function Pill({ label, active, onPress }: PillProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[styles.pill, active && styles.pillActive]}
      activeOpacity={0.7}
    >
      <Text style={[styles.pillText, active && styles.pillTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

interface BackendStatusProps {
  health: XAIHealth | null | 'checking';
  onRefresh: () => void;
}

function BackendStatus({ health, onRefresh }: BackendStatusProps) {
  const isChecking = health === 'checking';
  const isOnline = health && health !== 'checking';
  const color = isChecking ? COLORS.WARNING : isOnline ? COLORS.SUCCESS : COLORS.DANGER;
  const label = isChecking
    ? 'Verificando backend…'
    : isOnline
      ? 'Backend XAI online'
      : 'Backend XAI offline';

  return (
    <TouchableOpacity
      style={[styles.statusCard, { borderLeftColor: color }]}
      onPress={onRefresh}
      activeOpacity={0.75}
    >
      <View style={{ flex: 1 }}>
        <Text style={[styles.statusTitle, { color }]}>{label}</Text>
        <Text style={styles.statusUrl}>{getXAIBaseUrl()}</Text>
        {isOnline && typeof health !== 'string' && (
          <Text style={styles.statusMeta}>
            {health.numClasses} classes • {health.convLayersTail.slice(-1)[0] ?? '—'}
          </Text>
        )}
        {health === null && (
          <Text style={styles.statusMeta}>
            Suba o backend: uvicorn api.server:app --port 5000
          </Text>
        )}
      </View>
      {isChecking ? (
        <ActivityIndicator color={color} />
      ) : (
        <Text style={[styles.statusAction, { color }]}>↻</Text>
      )}
    </TouchableOpacity>
  );
}

interface RunCardProps {
  entry: RunEntry;
  onLabelChange: (label: FramingLabel) => void;
}

function RunCard({ entry, onLabelChange }: RunCardProps) {
  return (
    <View style={styles.runCard}>
      {entry.status === 'running' && (
        <View style={styles.runningBanner}>
          <ActivityIndicator color={COLORS.PRIMARY} />
          <Text style={styles.runningText}>Processando…</Text>
        </View>
      )}
      {entry.status === 'error' && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>❌ {entry.error}</Text>
        </View>
      )}
      {entry.status === 'pending' && (
        <View style={styles.pendingBanner}>
          <Text style={styles.pendingText}>⏳ Aguardando na fila</Text>
        </View>
      )}

      {entry.result ? (
        <>
          <HeatmapOverlay
            imageUri={entry.imageUri}
            overlayB64={entry.result.overlayB64}
            aspectRatio={
              entry.result.imageWidth && entry.result.imageHeight
                ? entry.result.imageWidth / entry.result.imageHeight
                : 1
            }
          />
          <View style={{ height: SPACING_SM }} />
          <MetricsPanel
            prediction={entry.result.prediction}
            confidence={entry.result.confidence}
            al={entry.result.al}
            afs={entry.result.afs}
            processingTimeMs={entry.result.processingTimeMs}
            bboxStrategy={entry.result.bboxStrategy}
            layerUsed={entry.result.layerUsed}
          />
          <View style={styles.framingRow}>
            <Text style={styles.framingLabel}>Enquadramento:</Text>
            <Pill
              label="Bem"
              active={entry.label === 'bem_enquadrada'}
              onPress={() => onLabelChange('bem_enquadrada')}
            />
            <View style={{ width: SPACING_XS }} />
            <Pill
              label="Mal"
              active={entry.label === 'mal_enquadrada'}
              onPress={() => onLabelChange('mal_enquadrada')}
            />
            <View style={{ width: SPACING_XS }} />
            <Pill
              label="—"
              active={entry.label === 'nao_classificada'}
              onPress={() => onLabelChange('nao_classificada')}
            />
          </View>
        </>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {
    backgroundColor: COLORS.BACKGROUND,
  },
  scroll: {
    padding: SPACING_MD,
    paddingBottom: SPACING_LG * 2,
    gap: SPACING_MD,
  },
  statusCard: {
    backgroundColor: COLORS.SURFACE,
    borderLeftWidth: 4,
    borderRadius: RADIUS_MD,
    paddingVertical: SPACING_MD,
    paddingHorizontal: SPACING_MD,
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
  },
  statusUrl: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  statusMeta: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    marginTop: 2,
  },
  statusAction: {
    fontSize: FONT_XL,
    fontWeight: '700',
    marginLeft: SPACING_SM,
  },
  controlsCard: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  sectionTitle: {
    fontSize: FONT_LG,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_SM,
  },
  controlLabel: {
    fontSize: FONT_SM,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginBottom: SPACING_XS,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING_XS,
  },
  pill: {
    borderRadius: 999,
    paddingHorizontal: SPACING_MD,
    paddingVertical: SPACING_XS,
    backgroundColor: COLORS.GRAY_100,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  pillActive: {
    backgroundColor: COLORS.PRIMARY,
    borderColor: COLORS.PRIMARY,
  },
  pillText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_PRIMARY,
    fontWeight: '600',
  },
  pillTextActive: {
    color: COLORS.WHITE,
  },
  actionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  summaryCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.SUCCESS,
  },
  summaryTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.SUCCESS,
    marginBottom: SPACING_XS,
  },
  summaryText: {
    fontSize: FONT_SM,
    color: COLORS.SUCCESS,
  },
  runCard: {
    backgroundColor: COLORS.BACKGROUND,
    borderRadius: RADIUS_MD,
    padding: SPACING_SM,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    gap: SPACING_SM,
  },
  runningBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING_SM,
    backgroundColor: '#FFF8E1',
    padding: SPACING_SM,
    borderRadius: RADIUS_MD,
  },
  runningText: {
    color: COLORS.WARNING,
    fontWeight: '600',
  },
  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: SPACING_SM,
    borderRadius: RADIUS_MD,
  },
  errorText: {
    color: COLORS.DANGER,
    fontWeight: '600',
  },
  pendingBanner: {
    backgroundColor: COLORS.GRAY_100,
    padding: SPACING_SM,
    borderRadius: RADIUS_MD,
  },
  pendingText: {
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '600',
  },
  framingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: SPACING_SM,
    flexWrap: 'wrap',
    gap: SPACING_XS,
  },
  framingLabel: {
    fontSize: FONT_SM,
    fontWeight: '600',
    color: COLORS.TEXT_SECONDARY,
    marginRight: SPACING_XS,
  },
  historyCard: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  historyText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
  },
});
