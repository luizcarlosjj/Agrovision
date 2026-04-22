/**
 * Processing Screen
 * Shows loading state while analyzing image
 */

import React, { useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SafeAreaWrapper, LoadingSpinner, ErrorBanner } from '@components';
import { ProcessingScreenProps } from '@navigation/types';
import { useAnalysis } from '@hooks';
import { COLORS, UI } from '@utils/constants';
import { getAnalysisTypeLabel } from '@utils/format';

export function ProcessingScreen({ route, navigation }: ProcessingScreenProps) {
  const { imageUri, analysisType } = route.params;
  const { analyze, isLoading, error, currentAnalysis } = useAnalysis();

  /**
   * Start analysis when screen mounts
   */
  useEffect(() => {
    const startAnalysis = async () => {
      try {
        await analyze(imageUri, analysisType);
      } catch (err) {
        // Error handled in context
      }
    };

    startAnalysis();
  }, [imageUri, analysisType]);

  /**
   * Navigate to result when analysis completes
   */
  useEffect(() => {
    if (currentAnalysis && !isLoading) {
      // Small delay to show completion animation
      const timer = setTimeout(() => {
        navigation.replace('Result', { analysis: currentAnalysis });
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [currentAnalysis, isLoading, navigation]);

  /**
   * Handle retry
   */
  const handleRetry = async () => {
    await analyze(imageUri, analysisType);
  };

  /**
   * Handle cancel
   */
  const handleCancel = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaWrapper style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>
          Analisando {getAnalysisTypeLabel(analysisType).toLowerCase()}...
        </Text>

        <LoadingSpinner
          visible={isLoading}
          message="Processando imagem"
          size="large"
          color={COLORS.PRIMARY}
        />

        {error && (
          <ErrorBanner
            visible
            message={error}
            onRetry={handleRetry}
            onDismiss={handleCancel}
          />
        )}

        {!error && !isLoading && (
          <View style={styles.completeContainer}>
            <Text style={styles.completeText}>✓ Análise completa!</Text>
          </View>
        )}
      </View>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: UI.SPACING_LG,
  },
  title: {
    fontSize: UI.FONT_LG,
    fontWeight: '600',
    color: COLORS.TEXT_PRIMARY,
    textAlign: 'center',
    marginBottom: UI.SPACING_LG,
  },
  completeContainer: {
    marginTop: UI.SPACING_LG,
  },
  completeText: {
    fontSize: UI.FONT_BASE,
    color: COLORS.SUCCESS,
    fontWeight: '600',
  },
});
