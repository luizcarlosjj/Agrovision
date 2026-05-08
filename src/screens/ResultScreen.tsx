/**
 * Result Screen
 * Displays analysis results
 */

import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaWrapper, Button, Card, ImagePreview } from '@components';
import { Header } from '@components/common/Header';
import { ResultScreenProps } from '@navigation/types';
import { formatConfidence, formatDateTime, getAnalysisTypeEmoji } from '@utils/format';
import { COLORS, UI } from '@utils/constants';

export function ResultScreen({ route, navigation }: ResultScreenProps) {
  const { analysis } = route.params;

  const confidenceColor = analysis.confidence > 0.8 ? COLORS.SUCCESS :
                         analysis.confidence > 0.6 ? COLORS.WARNING :
                         COLORS.DANGER;

  return (
    <SafeAreaWrapper scrollable>
      <Header title="Resultado da Análise" />

      {/* Image Preview */}
      <ImagePreview
        uri={analysis.imageUri}
        caption="Imagem analisada"
      />

      {/* Main Result Card */}
      <Card style={styles.resultCard}>
        <View style={styles.resultHeader}>
          <Text style={styles.emoji}>
            {getAnalysisTypeEmoji(analysis.type)}
          </Text>
          <View style={styles.resultInfo}>
            <Text style={styles.resultTitle}>{analysis.result}</Text>
            <View style={styles.confidenceContainer}>
              <View
                style={[
                  styles.confidenceBar,
                  { width: `${analysis.confidence * 100}%`, backgroundColor: confidenceColor },
                ]}
              />
            </View>
            <Text style={[styles.confidence, { color: confidenceColor }]}>
              Confiança: {formatConfidence(analysis.confidence)}
            </Text>
          </View>
        </View>

        {/* Description */}
        <View style={styles.descriptionContainer}>
          <Text style={styles.sectionTitle}>Descrição</Text>
          <Text style={styles.description}>{analysis.description}</Text>
        </View>

        {/* Recommendations */}
        <View style={styles.recommendationsContainer}>
          <Text style={styles.sectionTitle}>Recomendações</Text>
          {analysis.recommendations.map((rec, index) => (
            <View key={index} style={styles.recommendationItem}>
              <Text style={styles.bullet}>•</Text>
              <Text style={styles.recommendationText}>{rec}</Text>
            </View>
          ))}
        </View>

        {/* Metadata */}
        <View style={styles.metadataContainer}>
          <Text style={styles.sectionTitle}>Informações</Text>
          <View style={styles.metadataRow}>
            <Text style={styles.metadataLabel}>Tipo de análise:</Text>
            <Text style={styles.metadataValue}>{analysis.type}</Text>
          </View>
          <View style={styles.metadataRow}>
            <Text style={styles.metadataLabel}>Data:</Text>
            <Text style={styles.metadataValue}>
              {formatDateTime(analysis.timestamp)}
            </Text>
          </View>
          <View style={styles.metadataRow}>
            <Text style={styles.metadataLabel}>Tempo de processamento:</Text>
            <Text style={styles.metadataValue}>
              {analysis.processingTime}ms
            </Text>
          </View>
        </View>
      </Card>

      {/* Action Buttons */}
      <View style={styles.actionsContainer}>
        {/* Botão principal: Auditar Modelo (Grad-CAM) */}
        <Button
          title="🔬  Auditar Modelo (Grad-CAM)"
          onPress={() =>
            navigation.navigate('AuditarModelo', {
              imageUri: analysis.imageUri,
              prediction: analysis.result,
              confidence: analysis.confidence,
            })
          }
          variant="primary"
          size="lg"
          fullWidth
          style={styles.button}
        />
        <Button
          title="📷  Fazer Nova Análise"
          onPress={() => navigation.popToTop()}
          variant="secondary"
          size="lg"
          fullWidth
          style={styles.button}
        />
        <Button
          title="← Voltar ao Menu"
          onPress={() => navigation.popToTop()}
          variant="outline"
          size="lg"
          fullWidth
          style={styles.button}
        />
      </View>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  resultCard: {
    marginVertical: UI.SPACING_MD,
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: UI.SPACING_LG,
  },
  emoji: {
    fontSize: 48,
    marginRight: UI.SPACING_MD,
  },
  resultInfo: {
    flex: 1,
  },
  resultTitle: {
    fontSize: UI.FONT_LG,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: UI.SPACING_SM,
  },
  confidenceContainer: {
    height: 8,
    backgroundColor: COLORS.GRAY_200,
    borderRadius: UI.RADIUS_SM,
    marginBottom: UI.SPACING_SM,
    overflow: 'hidden',
  },
  confidenceBar: {
    height: '100%',
    borderRadius: UI.RADIUS_SM,
  },
  confidence: {
    fontSize: UI.FONT_SM,
    fontWeight: '600',
  },
  descriptionContainer: {
    marginBottom: UI.SPACING_LG,
    paddingTop: UI.SPACING_LG,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
  },
  sectionTitle: {
    fontSize: UI.FONT_BASE,
    fontWeight: '600',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: UI.SPACING_SM,
  },
  description: {
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },
  recommendationsContainer: {
    marginBottom: UI.SPACING_LG,
    paddingTop: UI.SPACING_LG,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
  },
  recommendationItem: {
    flexDirection: 'row',
    marginBottom: UI.SPACING_SM,
  },
  bullet: {
    color: COLORS.PRIMARY,
    fontWeight: 'bold',
    marginRight: UI.SPACING_SM,
    fontSize: UI.FONT_BASE,
  },
  recommendationText: {
    flex: 1,
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },
  metadataContainer: {
    paddingTop: UI.SPACING_LG,
    borderTopWidth: 1,
    borderTopColor: COLORS.BORDER,
  },
  metadataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: UI.SPACING_SM,
  },
  metadataLabel: {
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    fontWeight: '500',
  },
  metadataValue: {
    fontSize: UI.FONT_SM,
    color: COLORS.TEXT_PRIMARY,
    fontWeight: '600',
  },
  actionsContainer: {
    gap: UI.SPACING_LG,
    marginVertical: UI.SPACING_LG,
    paddingHorizontal: UI.SPACING_LG,
  },
  button: {
    marginBottom: 0,
  },
});
