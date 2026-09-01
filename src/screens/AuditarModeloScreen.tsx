/**
 * AuditarModeloScreen — Modo Científico inline (single-image).
 *
 * Acessado via botão "Auditar Modelo" na ResultScreen.
 * Recebe imageUri + prediction da identificação já realizada,
 * executa Grad-CAM via WebSocket e exibe heatmap + AL/AFS.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { SafeAreaWrapper, HeatmapOverlay, MetricsPanel, AuditExplanation } from '@components';
import { Header } from '@components/common/Header';
import { analyzeWithXAIWS, XAIProgressCallback } from '@services/ml/xaiService';
import { databaseService } from '@services/storage';
import { BBoxStrategy, FramingLabel, XAIResult } from '@models';
import { COLORS, SPACING_LG, SPACING_MD, SPACING_SM, RADIUS_MD, RADIUS_LG, FONT_BASE, FONT_SM, FONT_LG } from '@utils/constants';
import { logger } from '@utils/logger';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '@navigation/types';

type Props = NativeStackScreenProps<RootStackParamList, 'AuditarModelo'>;

const genId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

const STEP_LABELS: Record<string, string> = {
  preprocessing:        'Pré-processando imagem...',
  building_model:       'Construindo modelo Grad-CAM...',
  computing_gradients:  'Calculando gradientes...',
  computing_metrics:    'Calculando AL / AFS...',
  rendering_overlay:    'Gerando visualização...',
  done:                 'Concluído!',
};

const LABEL_OPTIONS: { value: FramingLabel; label: string; color: string }[] = [
  { value: 'bem_enquadrada',   label: '✅ Bem enquadrada',  color: '#2D7A4F' },
  { value: 'mal_enquadrada',   label: '⚠️ Mal enquadrada',  color: '#F57C00' },
  { value: 'nao_classificada', label: '❓ Não classificada', color: '#616161' },
];

export function AuditarModeloScreen({ route, navigation }: Props) {
  const { imageUri, prediction, classKey, confidence } = route.params;

  const [status,   setStatus]   = useState<'running' | 'done' | 'error'>('running');
  const [step,     setStep]     = useState('Conectando ao backend...');
  const [pct,      setPct]      = useState(0);
  const [result,   setResult]   = useState<XAIResult | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [label,    setLabel]    = useState<FramingLabel>('nao_classificada');
  const [saving,   setSaving]   = useState(false);
  const [saved,    setSaved]    = useState(false);

  const wsRef = useRef<WebSocket | null>(null);

  const runGradCAM = useCallback(async () => {
    setStatus('running');
    setStep('Conectando ao backend...');
    setPct(0);

    const onProgress: XAIProgressCallback = (s, p) => {
      setStep(STEP_LABELS[s] ?? s);
      setPct(p);
    };

    try {
      const xaiResult = await analyzeWithXAIWS(
        {
          imageUri,
          bboxStrategy: 'fixed' as BBoxStrategy,
          threshold: 0.5,
          coverage: 0.8,
          predictedClass: classKey,
        },
        onProgress,
      );
      setResult(xaiResult);
      setStatus('done');
    } catch (err: any) {
      logger.error('[AuditarModelo] Grad-CAM failed:', err);
      setErrorMsg(err?.message ?? 'Erro desconhecido');
      setStatus('error');
    }
  }, [imageUri, prediction]);

  useEffect(() => {
    runGradCAM();
    return () => {
      wsRef.current?.close();
    };
  }, [runGradCAM]);

  const handleSave = useCallback(async () => {
    if (!result) return;
    setSaving(true);
    try {
      await databaseService.saveXAITest({
        id: genId(),
        imageUri,
        prediction: result.prediction,
        confidence: result.confidence,
        al: result.al,
        afs: result.afs,
        threshold: result.threshold,
        bbox: result.bboxUsed,
        bboxStrategy: result.bboxStrategy,
        overlayB64: result.overlayB64,
        layerUsed: result.layerUsed,
        label,
        createdAt: new Date().toISOString(),
      });
      setSaved(true);
    } catch (err: any) {
      Alert.alert('Erro ao salvar', err?.message ?? 'Não foi possível salvar o resultado.');
    } finally {
      setSaving(false);
    }
  }, [result, imageUri, label]);

  const handleExport = useCallback(async () => {
    if (!result) return;
    try {
      const isAvailable = await Sharing.isAvailableAsync();
      if (!isAvailable) {
        Alert.alert('Indisponível', 'Compartilhamento não está disponível neste dispositivo.');
        return;
      }

      // Salva overlay como PNG temporário
      const tmpPath = `${FileSystem.cacheDirectory}agrovision_gradcam_${Date.now()}.png`;
      await FileSystem.writeAsStringAsync(tmpPath, result.overlayB64, {
        encoding: FileSystem.EncodingType.Base64,
      });

      // Gera relatório de texto junto ao arquivo
      const report = [
        '=== AgroVision — Relatório Grad-CAM ===',
        `Data: ${new Date().toLocaleString('pt-BR')}`,
        '',
        `Predição: ${result.prediction}`,
        `Confiança: ${(result.confidence * 100).toFixed(1)}%`,
        '',
        `AL (Atenção Extravasada): ${(result.al * 100).toFixed(1)}%`,
        `AFS (Foco na Área): ${(result.afs * 100).toFixed(1)}%`,
        `Threshold: ${result.threshold}`,
        `Estratégia BBox: ${result.bboxStrategy}`,
        `Camada usada: ${result.layerUsed}`,
        `Tempo de processamento: ${result.processingTimeMs}ms`,
        `Enquadramento: ${label}`,
      ].join('\n');

      const reportPath = `${FileSystem.cacheDirectory}agrovision_relatorio_${Date.now()}.txt`;
      await FileSystem.writeAsStringAsync(reportPath, report, {
        encoding: FileSystem.EncodingType.UTF8,
      });

      await Sharing.shareAsync(tmpPath, {
        mimeType: 'image/png',
        dialogTitle: 'Exportar resultado Grad-CAM',
      });
    } catch (err: any) {
      Alert.alert('Erro ao exportar', err?.message ?? 'Não foi possível exportar o resultado.');
    }
  }, [result, label]);

  return (
    <SafeAreaWrapper scrollable>
      <Header title="Auditar Modelo (Grad-CAM)" />

      {/* Identificação original */}
      <View style={styles.identCard}>
        <Text style={styles.identTitle}>Identificação: <Text style={styles.identValue}>{prediction}</Text></Text>
        <Text style={styles.identConf}>Confiança: {(confidence * 100).toFixed(1)}%</Text>
      </View>

      {/* ── Running state ── */}
      {status === 'running' && (
        <View style={styles.progressContainer}>
          <ActivityIndicator size="large" color={COLORS.PRIMARY} />
          <Text style={styles.stepText}>{step}</Text>
          <View style={styles.barBg}>
            <View style={[styles.barFill, { width: `${pct}%` }]} />
          </View>
          <Text style={styles.pctText}>{pct}%</Text>
        </View>
      )}

      {/* ── Error state ── */}
      {status === 'error' && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Falha na análise</Text>
          <Text style={styles.errorMsg}>{errorMsg}</Text>
          <TouchableOpacity style={styles.retryBtn} onPress={runGradCAM}>
            <Text style={styles.retryText}>↺  Tentar novamente</Text>
          </TouchableOpacity>
          <Text style={styles.errorHint}>
            Verifique se o backend Railway está disponível e se há conexão com a internet.
          </Text>
        </View>
      )}

      {/* ── Done state ── */}
      {status === 'done' && result && (
        <>
          <HeatmapOverlay
            originalUri={imageUri}
            overlayB64={result.overlayB64}
          />

          <MetricsPanel
            prediction={result.prediction}
            confidence={result.confidence}
            al={result.al}
            afs={result.afs}
            processingTimeMs={result.processingTimeMs}
            bboxStrategy={result.bboxStrategy}
            layerUsed={result.layerUsed}
          />

          {/* Texto explicativo dinâmico */}
          <AuditExplanation
            prediction={result.prediction}
            confidence={result.confidence}
            afs={result.afs}
            al={result.al}
          />

          {/* Rótulo de enquadramento */}
          <View style={styles.labelSection}>
            <Text style={styles.labelTitle}>Enquadramento da imagem:</Text>
            <View style={styles.labelRow}>
              {LABEL_OPTIONS.map((opt) => (
                <TouchableOpacity
                  key={opt.value}
                  style={[
                    styles.labelBtn,
                    label === opt.value && { borderColor: opt.color, backgroundColor: opt.color + '18' },
                  ]}
                  onPress={() => setLabel(opt.value)}
                >
                  <Text style={[styles.labelBtnText, label === opt.value && { color: opt.color }]}>
                    {opt.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Botão salvar / exportar */}
          {!saved ? (
            <TouchableOpacity
              style={[styles.saveBtn, saving && styles.saveBtnDisabled]}
              onPress={handleSave}
              disabled={saving}
            >
              {saving
                ? <ActivityIndicator color={COLORS.WHITE} size="small" />
                : <Text style={styles.saveBtnText}>💾  Salvar resultado</Text>
              }
            </TouchableOpacity>
          ) : (
            <View style={styles.savedActions}>
              <View style={styles.savedBadge}>
                <Text style={styles.savedText}>✅  Salvo no histórico científico</Text>
              </View>
              <TouchableOpacity style={styles.exportBtn} onPress={handleExport}>
                <Text style={styles.exportBtnText}>📤  Exportar resultado</Text>
              </TouchableOpacity>
            </View>
          )}
        </>
      )}

      {/* Voltar */}
      <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
        <Text style={styles.backText}>← Voltar ao resultado</Text>
      </TouchableOpacity>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  identCard: {
    backgroundColor: COLORS.SURFACE_2,
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    marginVertical: SPACING_SM,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.PRIMARY,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  identTitle: { fontSize: FONT_BASE, color: COLORS.TEXT_PRIMARY, fontWeight: '500' },
  identValue: { fontWeight: '800', color: COLORS.PRIMARY },
  identConf:  { fontSize: FONT_SM, color: COLORS.TEXT_SECONDARY, marginTop: 2 },

  progressContainer: {
    alignItems: 'center',
    paddingVertical: SPACING_LG * 2,
    gap: SPACING_MD,
  },
  stepText: { fontSize: FONT_BASE, color: COLORS.PRIMARY, textAlign: 'center', fontWeight: '600' },
  barBg: {
    width: '80%', height: 8, backgroundColor: COLORS.BORDER,
    borderRadius: 4, overflow: 'hidden',
  },
  barFill: { height: '100%', backgroundColor: COLORS.PRIMARY, borderRadius: 4 },
  pctText: { fontSize: FONT_SM, color: COLORS.TEXT_SECONDARY, fontWeight: '600' },

  errorContainer: {
    alignItems: 'center',
    paddingVertical: SPACING_LG,
    paddingHorizontal: SPACING_LG,
    gap: SPACING_MD,
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_MD,
    borderWidth: 1,
    borderColor: '#FFCDD2',
  },
  errorTitle: { fontSize: FONT_LG, fontWeight: '800', color: COLORS.DANGER },
  errorMsg:   { fontSize: FONT_SM, color: COLORS.TEXT_SECONDARY, textAlign: 'center' },
  retryBtn: {
    backgroundColor: COLORS.PRIMARY,
    paddingHorizontal: SPACING_LG,
    paddingVertical: 12,
    borderRadius: RADIUS_LG,
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  retryText: { color: '#FFF', fontWeight: '700', fontSize: FONT_BASE },
  errorHint: { fontSize: FONT_SM - 1, color: COLORS.TEXT_SECONDARY, textAlign: 'center', marginTop: SPACING_SM },

  labelSection: { marginTop: SPACING_LG },
  labelTitle: { fontSize: FONT_BASE, fontWeight: '700', color: COLORS.TEXT_PRIMARY, marginBottom: SPACING_SM },
  labelRow: { flexDirection: 'row', flexWrap: 'wrap', gap: SPACING_SM },
  labelBtn: {
    paddingHorizontal: SPACING_MD,
    paddingVertical: SPACING_SM,
    borderRadius: RADIUS_LG,
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
    backgroundColor: COLORS.SURFACE,
  },
  labelBtnText: { fontSize: FONT_SM, color: COLORS.TEXT_SECONDARY, fontWeight: '500' },

  saveBtn: {
    backgroundColor: COLORS.PRIMARY,
    borderRadius: RADIUS_LG,
    paddingVertical: 15,
    alignItems: 'center',
    marginTop: SPACING_LG,
    shadowColor: COLORS.PRIMARY_DARK,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.22,
    shadowRadius: 8,
    elevation: 4,
  },
  saveBtnDisabled: { opacity: 0.5 },
  saveBtnText: { color: '#FFF', fontWeight: '700', fontSize: FONT_BASE },

  savedActions: {
    marginTop: SPACING_LG,
    gap: SPACING_SM,
  },
  savedBadge: {
    backgroundColor: COLORS.SURFACE_2,
    borderRadius: RADIUS_LG,
    paddingVertical: SPACING_MD,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  savedText: { color: COLORS.PRIMARY, fontWeight: '700', fontSize: FONT_BASE },
  exportBtn: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_LG,
    paddingVertical: 15,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: COLORS.PRIMARY,
  },
  exportBtnText: { color: COLORS.PRIMARY, fontWeight: '700', fontSize: FONT_BASE },

  backBtn: { alignItems: 'center', paddingVertical: SPACING_LG, marginTop: SPACING_SM },
  backText: { color: COLORS.TEXT_SECONDARY, fontSize: FONT_SM, fontWeight: '500' },
});
