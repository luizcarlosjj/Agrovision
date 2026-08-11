/**
 * About Screen — sobre o projeto e as doenças detectadas.
 */

import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { SafeAreaWrapper } from '@components';
import { Header } from '@components/common/Header';
import {
  COLORS,
  SPACING_MD,
  SPACING_LG,
  SPACING_SM,
  SPACING_XS,
  FONT_BASE,
  FONT_SM,
  FONT_LG,
  FONT_XS,
  RADIUS_LG,
} from '@utils/constants';

const DISEASES = [
  {
    emoji: '🟢',
    name: 'Milho Saudável',
    key: 'Healthy',
    desc: 'Planta sem sinais visíveis de doença — referência para o modelo.',
  },
  {
    emoji: '🟤',
    name: 'Helmintosporiose (Blight)',
    key: 'Exserohilum turcicum',
    desc: 'Lesões alongadas cinza-esverdeadas a marrons, com formato elíptico nas folhas.',
  },
  {
    emoji: '🟠',
    name: 'Ferrugem-Comum',
    key: 'Puccinia sorghi',
    desc: 'Pústulas marrom-alaranjadas distribuídas em ambas as faces da folha.',
  },
  {
    emoji: '⚫',
    name: 'Mancha-Cinzenta',
    key: 'Cercospora zeae-maydis',
    desc: 'Lesões retangulares cinza a marrons, delimitadas pelas nervuras da folha.',
  },
];

export function AboutScreen() {
  return (
    <SafeAreaWrapper scrollable padding={0}>
      <Header title="Sobre o AgroVision" />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🌾 O projeto</Text>
          <Text style={styles.cardText}>
            AgroVision é um aplicativo mobile de diagnóstico de doenças em folhas de milho por
            visão computacional. A imagem é enviada para um modelo publicado no Roboflow, que
            devolve a classe prevista e a confiança em segundos.
          </Text>
          <Text style={styles.cardText}>
            Desenvolvido como Trabalho de Conclusão de Curso (TCC) em Ciência da Computação, com
            foco em <Text style={styles.bold}>Inteligência Artificial Explicável (XAI)</Text>{' '}
            aplicada à agricultura.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>🔬 Intervenção científica</Text>
          <Text style={styles.cardText}>
            Além da classificação, o app oferece o modo <Text style={styles.bold}>Auditar
            Modelo</Text>, que exibe o mapa de calor (Grad-CAM) das regiões da folha que mais
            influenciaram a decisão da rede neural.
          </Text>
          <Text style={styles.cardText}>
            Duas métricas quantitativas são calculadas para avaliar o quanto a atenção do modelo
            fica dentro da folha (foco) ou vaza para o fundo (leakage):
            {'\n'}• <Text style={styles.bold}>Attention Focus Score (AFS)</Text>
            {'\n'}• <Text style={styles.bold}>Attention Leakage (AL)</Text>
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>🌽 Doenças detectadas</Text>
          {DISEASES.map((d) => (
            <View key={d.key} style={styles.diseaseItem}>
              <Text style={styles.diseaseEmoji}>{d.emoji}</Text>
              <View style={styles.diseaseInfo}>
                <Text style={styles.diseaseName}>{d.name}</Text>
                <Text style={styles.diseaseKey}>{d.key}</Text>
                <Text style={styles.diseaseDesc}>{d.desc}</Text>
              </View>
            </View>
          ))}
        </View>

        <View style={[styles.card, styles.disclaimer]}>
          <Text style={styles.disclaimerText}>
            ⚠️ O diagnóstico é orientativo e serve como apoio à decisão. Recomenda-se validação
            com um engenheiro agrônomo antes de qualquer intervenção química na lavoura.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaWrapper>
  );
}

const styles = StyleSheet.create({
  scroll: {
    padding: SPACING_MD,
    paddingBottom: SPACING_LG * 2,
    gap: SPACING_MD,
  },
  card: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_LG,
    padding: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    gap: SPACING_SM,
  },
  cardTitle: {
    fontSize: FONT_LG,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_XS,
  },
  cardText: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 21,
  },
  bold: {
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  diseaseItem: {
    flexDirection: 'row',
    gap: SPACING_SM,
    marginTop: SPACING_SM,
  },
  diseaseEmoji: {
    fontSize: 22,
    marginTop: 2,
  },
  diseaseInfo: {
    flex: 1,
    gap: 2,
  },
  diseaseName: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  diseaseKey: {
    fontSize: FONT_XS,
    color: COLORS.PRIMARY,
    fontStyle: 'italic',
    marginBottom: 2,
  },
  diseaseDesc: {
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },
  disclaimer: {
    backgroundColor: '#FFF3E0',
    borderColor: '#FFCC80',
  },
  disclaimerText: {
    fontSize: FONT_SM,
    color: '#5D4037',
    lineHeight: 20,
  },
});
