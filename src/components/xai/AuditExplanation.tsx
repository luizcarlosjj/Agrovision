/**
 * AuditExplanation
 *
 * Painel explicativo dinâmico para a tela de auditoria.
 * Lê os valores reais de AFS/AL e gera um texto interpretativo
 * de acordo com a faixa (focado / moderado / disperso) + explicação
 * do mapa de calor.
 */

import { View, Text, StyleSheet } from 'react-native';
import {
  COLORS,
  FONT_BASE,
  FONT_LG,
  FONT_SM,
  FONT_XS,
  RADIUS_MD,
  SPACING_MD,
  SPACING_SM,
  SPACING_XS,
} from '@utils/constants';

interface Props {
  prediction: string;
  confidence: number;
  afs: number;
  al: number;
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

function afsInterpretation(afs: number) {
  if (afs >= 0.7) {
    return {
      emoji: '✅',
      title: 'Atenção focada',
      color: COLORS.SUCCESS,
      text:
        'O modelo concentrou a maior parte do seu "olhar" diretamente sobre a folha. Resultado de alta confiabilidade — pode tomar decisão de manejo com base nesse diagnóstico.',
    };
  }
  if (afs >= 0.4) {
    return {
      emoji: '⚠️',
      title: 'Atenção moderada',
      color: COLORS.WARNING,
      text:
        'O modelo focou parcialmente na folha, mas também usou áreas adjacentes (bordas, fundo, sombra). O diagnóstico tende a estar correto, porém uma foto melhor enquadrada — folha centralizada, fundo neutro, boa iluminação — daria uma auditoria mais robusta.',
    };
  }
  return {
    emoji: '🚫',
    title: 'Atenção dispersa',
    color: COLORS.DANGER,
    text:
      'A maior parte da atenção do modelo ficou fora da folha. Mesmo que a classe predita esteja correta, o modelo provavelmente se baseou em informação contextual (fundo, iluminação). Recomendado: recapturar a imagem antes de tomar qualquer decisão.',
  };
}

export function AuditExplanation({ prediction, confidence, afs, al }: Props) {
  const interp = afsInterpretation(afs);
  const label = toPtLabel(prediction);
  const pctConf = (confidence * 100).toFixed(1);
  const pctAfs = (afs * 100).toFixed(1);
  const pctAl = (al * 100).toFixed(1);

  return (
    <View style={styles.card}>
      <Text style={styles.title}>O que isso significa?</Text>

      {/* 1. Classificação */}
      <View style={styles.row}>
        <Text style={styles.emoji}>🎯</Text>
        <Text style={styles.text}>
          O modelo de auditoria classificou esta imagem como{' '}
          <Text style={styles.bold}>{label}</Text> com{' '}
          <Text style={styles.bold}>{pctConf}%</Text> de certeza. Quando essa
          classe bate com a identificação inicial (do Roboflow), você tem uma{' '}
          <Text style={styles.bold}>validação cruzada entre dois modelos
          independentes</Text> treinados no mesmo dataset.
        </Text>
      </View>

      {/* 2. Interpretação dinâmica do AFS */}
      <View style={styles.row}>
        <Text style={styles.emoji}>{interp.emoji}</Text>
        <View style={styles.colFlex}>
          <Text style={[styles.bold, { color: interp.color, marginBottom: 4 }]}>
            {interp.title} — AFS {pctAfs}%
          </Text>
          <Text style={styles.text}>{interp.text}</Text>
        </View>
      </View>

      {/* 3. Explicação do mapa de calor */}
      <View style={styles.row}>
        <Text style={styles.emoji}>🌡️</Text>
        <Text style={styles.text}>
          O <Text style={styles.bold}>mapa de calor</Text> sobreposto à imagem
          mostra <Text style={styles.italic}>onde</Text> o modelo "olhou" para
          decidir. Apesar do nome, ele não mede temperatura real: cores quentes
          (vermelho, laranja, amarelo) marcam regiões que mais influenciaram a
          decisão; cores frias (azul, verde) marcam regiões praticamente
          ignoradas pelo modelo. É uma técnica chamada{' '}
          <Text style={styles.bold}>Grad-CAM</Text>, que extrai os gradientes
          internos da rede neural para revelar visualmente seu raciocínio.
        </Text>
      </View>

      <View style={styles.divider} />

      {/* 4. Glossário das métricas */}
      <Text style={styles.glossaryTitle}>Glossário</Text>
      <Text style={styles.metricExplain}>
        <Text style={styles.bold}>AFS — Attention Focus Score ({pctAfs}%):</Text>{' '}
        proporção do "olhar" do modelo que ficou dentro da região da folha.
        Quanto maior, melhor o foco.
      </Text>
      <Text style={styles.metricExplain}>
        <Text style={styles.bold}>AL — Attention Leakage ({pctAl}%):</Text>{' '}
        proporção do "olhar" que vazou para fora da folha (fundo, sombra,
        bordas). Quanto menor, melhor.
      </Text>
      <Text style={styles.metricExplain}>
        <Text style={styles.bold}>AFS + AL = 100%</Text> — são complementares.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: COLORS.SURFACE,
    borderRadius: RADIUS_MD,
    padding: SPACING_MD,
    marginTop: SPACING_MD,
    borderWidth: 1,
    borderColor: COLORS.BORDER,
    gap: SPACING_SM,
  },
  title: {
    fontSize: FONT_LG,
    fontWeight: '800',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: SPACING_XS,
  },
  row: {
    flexDirection: 'row',
    gap: SPACING_SM,
    alignItems: 'flex-start',
  },
  emoji: {
    fontSize: 22,
    width: 28,
    textAlign: 'center',
  },
  colFlex: {
    flex: 1,
  },
  text: {
    flex: 1,
    fontSize: FONT_SM,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 20,
  },
  bold: {
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
  },
  italic: {
    fontStyle: 'italic',
    color: COLORS.TEXT_PRIMARY,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.BORDER,
    marginVertical: SPACING_XS,
  },
  glossaryTitle: {
    fontSize: FONT_BASE,
    fontWeight: '700',
    color: COLORS.TEXT_PRIMARY,
    marginBottom: 2,
  },
  metricExplain: {
    fontSize: FONT_XS,
    color: COLORS.TEXT_SECONDARY,
    lineHeight: 18,
  },
});
