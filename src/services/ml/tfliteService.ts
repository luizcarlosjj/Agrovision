/**
 * TFLite Service — Inferência real via @tensorflow/tfjs-react-native
 * Carrega o modelo TFJS de assets/models/tfjs_model/ e roda offline.
 *
 * Pré-requisito: converter o modelo com
 *   experiments/soy_roboflow_test/convert_to_tfjs.py
 *
 * Se o modelo não estiver disponível, cai em modo simulado (desenvolvimento).
 */

import * as FileSystem from 'expo-file-system';

export interface PredictionResult {
  result: string;
  confidence: number;
  description: string;
  recommendations: string[];
  processingTime: number;
}

// Descrições detalhadas para as espécies do modelo original
const SPECIES_INFO: Record<string, { name: string; description: string; recommendations: string[] }> = {
  'Solanum lycopersicum': {
    name: 'Tomate',
    description: 'Solanácea cultivada amplamente no Brasil. Planta herbácea com crescimento determinado ou indeterminado que produz frutos vermelhos com alto valor nutricional.',
    recommendations: ['Plantar em local com 6-8 horas de luz solar direta', 'Usar solo fértil, bem drenado com pH 6,0-6,8', 'Regar regularmente (1-2 cm/semana) mantendo consistência', 'Tutor e podas para melhor circulação de ar', 'Adubação quinzenal com fertilizante balanceado'],
  },
  'Glycine max': {
    name: 'Soja',
    description: 'Leguminosa de alto valor proteico e grande importância no agronegócio brasileiro.',
    recommendations: ['Plantar em épocas adequadas (setembro-dezembro)', 'Solos com boa drenagem e pH 6,0-7,0', 'Inoculação com Bradyrhizobium japonicum', 'Espaçamento de 45-50cm entre linhas', 'Monitorar pragas como lagarta-da-soja'],
  },
  'Zea mays': {
    name: 'Milho',
    description: 'Cereal de maior produção no Brasil com aplicações alimentares, industriais e forrageiras.',
    recommendations: ['Plantar em períodos com temperatura >15°C', 'Solo fértil com boa drenagem, pH 6,0-7,5', 'Espaçamento de 80-100cm entre linhas', 'Irrigação em períodos secos (5-7mm/dia)'],
  },
};

// Recomendações genéricas para doenças identificadas pelo modelo de soja
const DISEASE_RECOMMENDATIONS = [
  'Isolar a área afetada para evitar propagação',
  'Consultar um engenheiro agrônomo para diagnóstico preciso',
  'Registrar a ocorrência com foto e data para histórico',
  'Avaliar aplicação de fungicida/bactericida conforme indicação técnica',
  'Monitorar plantas vizinhas para detectar disseminação',
];

function buildResult(
  className: string,
  confidence: number,
  processingTime: number,
): PredictionResult {
  // Tenta casar com INFO de espécies conhecidas
  const speciesKey = Object.keys(SPECIES_INFO).find(
    k => k === className || SPECIES_INFO[k].name === className,
  );

  if (speciesKey) {
    const info = SPECIES_INFO[speciesKey];
    return { result: info.name, confidence, description: info.description, recommendations: info.recommendations, processingTime };
  }

  // Classe não mapeada (doença ou espécie nova): exibe o nome retornado pelo modelo
  const displayName = className.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  return {
    result: displayName,
    confidence,
    description: `Diagnóstico: ${displayName}. Confiança: ${(confidence * 100).toFixed(1)}%. Consulte um especialista para confirmação e plano de manejo.`,
    recommendations: DISEASE_RECOMMENDATIONS,
    processingTime,
  };
}

// ─── Núcleo de inferência ─────────────────────────────────────────────────────

const INPUT_SIZE = 224;
type TF = typeof import('@tensorflow/tfjs');
type LayersModel = import('@tensorflow/tfjs').LayersModel;
type Labels = Record<string, string>;

class TFLiteService {
  private model: LayersModel | null = null;
  private labels: Labels = {};
  private tf: TF | null = null;
  private isInitialized = false;
  private usingFallback = false;

  async init() {
    try {
      // Importação dinâmica para não quebrar em ambientes sem native GL
      const tfModule   = await import('@tensorflow/tfjs');
      const tfRNModule = await import('@tensorflow/tfjs-react-native');

      await tfModule.ready();
      this.tf = tfModule;

      // Carrega o modelo bundled
      const modelJson    = require('../../../assets/models/tfjs_model/model.json');
      const modelWeights = [require('../../../assets/models/tfjs_model/group1-shard1of1.bin')];

      this.model = await tfModule.loadLayersModel(
        tfRNModule.bundleResourceIO(modelJson, modelWeights),
      );

      // Carrega labels
      this.labels = require('../../../assets/models/labels_species.json') as Labels;

      this.isInitialized = true;
      console.log('[TFLite] Modelo carregado. Classes:', Object.keys(this.labels).length);
    } catch (err) {
      console.warn('[TFLite] Modelo TFJS não disponível — usando modo simulado.', err);
      this.usingFallback = true;
      this.isInitialized = true;
    }
  }

  async predict(
    imageUri: string,
    _modelType: 'disease' | 'health' | 'species' | 'pest',
  ): Promise<PredictionResult | null> {
    const startTime = Date.now();

    if (!imageUri) return null;

    if (this.usingFallback || !this.model || !this.tf) {
      return this.simulatePredict(startTime);
    }

    try {
      const input = await this.preprocessImage(imageUri);
      const outputTensor = this.model.predict(input) as import('@tensorflow/tfjs').Tensor;
      const probs = Array.from(await outputTensor.data() as Float32Array);

      input.dispose();
      outputTensor.dispose();

      const topIdx   = probs.indexOf(Math.max(...probs));
      const className = this.labels[String(topIdx)] ?? `class_${topIdx}`;
      const confidence = probs[topIdx];

      return buildResult(className, confidence, Date.now() - startTime);
    } catch (err) {
      console.error('[TFLite] Erro na predição:', err);
      return null;
    }
  }

  private async preprocessImage(uri: string): Promise<import('@tensorflow/tfjs').Tensor4D> {
    const tf = this.tf!;
    const { decodeJpeg } = await import('@tensorflow/tfjs-react-native');

    // Lê a imagem como base64
    const base64 = await FileSystem.readAsStringAsync(uri, {
      encoding: FileSystem.EncodingType.Base64,
    });

    // Decodifica JPEG → tensor [H, W, 3]
    const rawBytes = tf.util.encodeString(base64, 'base64') as Uint8Array;
    const decoded  = decodeJpeg(rawBytes, 3);

    // Redimensiona para 224×224, normaliza e adiciona dimensão de batch
    const resized     = tf.image.resizeBilinear(decoded as import('@tensorflow/tfjs').Tensor3D, [INPUT_SIZE, INPUT_SIZE]);
    const normalized  = tf.div(resized, 255.0);
    const batched     = normalized.expandDims(0) as import('@tensorflow/tfjs').Tensor4D;

    decoded.dispose();
    resized.dispose();
    normalized.dispose();

    return batched;
  }

  private simulatePredict(startTime: number): PredictionResult {
    const classes = Object.values(SPECIES_INFO);
    const picked  = classes[Math.floor(Math.random() * classes.length)];
    return {
      result: picked.name,
      confidence: 0.85 + Math.random() * 0.12,
      description: `[SIMULADO] ${picked.description}`,
      recommendations: picked.recommendations,
      processingTime: Date.now() - startTime,
    };
  }

  isModelLoaded(_modelType: string): boolean {
    return this.isInitialized;
  }

  getStatus(): Record<string, boolean> {
    return {
      initialized: this.isInitialized,
      realModel: !this.usingFallback && this.model !== null,
      fallback: this.usingFallback,
    };
  }
}

let tfliteService: TFLiteService | null = null;

export async function getTFLiteService(): Promise<TFLiteService> {
  if (!tfliteService) {
    tfliteService = new TFLiteService();
    await tfliteService.init();
  }
  return tfliteService;
}

export default TFLiteService;
