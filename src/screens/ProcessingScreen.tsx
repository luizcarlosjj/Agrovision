/**
 * Processing Screen
 */

import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Animated } from 'react-native';
import { SafeAreaWrapper, ErrorBanner } from '@components';
import { ProcessingScreenProps } from '@navigation/types';
import { useAnalysis } from '@hooks';
import { COLORS, UI, SPACING_LG, SPACING_MD, SPACING_SM, FONT_XL, FONT_BASE, FONT_SM, RADIUS_XL, RADIUS_LG } from '@utils/constants';
import { getAnalysisTypeLabel } from '@utils/format';

const STEPS = [
  'Conectando ao servidor...',
  'Pré-processando imagem...',
  'Classificando com IA...',
  'Gerando diagnóstico...',
];

export function ProcessingScreen({ route, navigation }: ProcessingScreenProps) {
  const { imageUri, analysisType } = route.params;
  const { analyze, isLoading, error, currentAnalysis } = useAnalysis();
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const stepIndex = useRef(0);
  const [currentStep, setCurrentStep] = React.useState(STEPS[0]);

  // Pulse animation
  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.08, duration: 900, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 900, useNativeDriver: true }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, [pulseAnim]);

  // Cycle through step labels
  useEffect(() => {
    const interval = setInterval(() => {
      stepIndex.current = (stepIndex.current + 1) % STEPS.length;
      setCurrentStep(STEPS[stepIndex.current]);
    }, 2200);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    analyze(imageUri, analysisType).catch(() => {});
  }, [imageUri, analysisType]);

  useEffect(() => {
    if (currentAnalysis && !isLoading) {
      const t = setTimeout(() => {
        navigation.replace('Result', { analysis: currentAnalysis });
      }, 400);
      return () => clearTimeout(t);
    }
  }, [currentAnalysis, isLoading, navigation]);

  const handleRetry = () => analyze(imageUri, analysisType).catch(() => {});
  const handleCancel = () => navigation.goBack();

  return (
    <SafeAreaWrapper style={styles.container}>
      <View style={styles.card}>
        {/* Animated icon */}
        <Animated.View style={[styles.iconWrap, { transform: [{ scale: pulseAnim }] }]}>
          <Text style={styles.icon}>🧠</Text>
        </Animated.View>

        <Text style={styles.title}>Analisando imagem</Text>
        <Text style={styles.subtitle}>
          {getAnalysisTypeLabel(analysisType)} · IA em processamento
        </Text>

        <ActivityIndicator
          size="large"
          color={COLORS.PRIMARY}
          style={styles.spinner}
        />

        <Text style={styles.stepText}>{currentStep}</Text>

        {/* Step dots */}
        <View style={styles.dotsRow}>
          {STEPS.map((_, i) => (
            <View
              key={i}
              style={[
                styles.dot,
                STEPS[i] === currentStep && styles.dotActive,
              ]}
            />
          ))}
        </View>
      </View>

      {error && (
        <View style={styles.errorWrap}>
          <ErrorBanner
            visible
            message={error}
            onRetry={handleRetry}
            onDismiss={handleCancel}
          />
        </View>
      )}

      {!error && !isLoading && (
        <View style={styles.doneWrap}>
          <Text style={styles.doneText}>✓  Análise concluída!</Text>
        </View>
      )}
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.BACKGROUND,
    paddingHorizontal: SPACING_LG,
  },
  card: {
    width: '100%',
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_XL,
    padding: SPACING_LG * 1.5,
    alignItems: 'center',
    shadowColor: '#1C2B22',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 6,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  iconWrap: {
    width: 88,
    height: 88,
    borderRadius: 28,
    backgroundColor: COLORS.SURFACE_2,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING_LG,
    borderWidth: 1.5,
    borderColor: COLORS.BORDER,
  },
  icon: {
    fontSize: 48,
  },
  title: {
    fontSize: FONT_XL,
    fontWeight: '800',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_SM,
    letterSpacing: -0.3,
  },
  subtitle: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    marginBottom: SPACING_LG,
    fontWeight: '500',
  },
  spinner: {
    marginBottom: SPACING_MD,
    transform: [{ scale: 1.2 }],
  },
  stepText: {
    fontSize: FONT_BASE,
    color: COLORS.PRIMARY,
    fontWeight: '600',
    marginBottom: SPACING_MD,
    textAlign: 'center',
  },
  dotsRow: {
    flexDirection: 'row',
    gap: 6,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.BORDER,
  },
  dotActive: {
    backgroundColor: COLORS.PRIMARY,
    width: 18,
  },
  errorWrap: {
    width: '100%',
    marginTop: SPACING_LG,
  },
  doneWrap: {
    marginTop: SPACING_LG,
    backgroundColor: COLORS.SURFACE_2,
    paddingHorizontal: SPACING_LG,
    paddingVertical: SPACING_MD,
    borderRadius: RADIUS_LG,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
  },
  doneText: {
    fontSize: FONT_BASE,
    color: COLORS.PRIMARY,
    fontWeight: '700',
  },
});
