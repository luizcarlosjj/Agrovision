/**
 * Serviço de inferência — 100% JavaScript, sem módulos nativos.
 * Funciona direto no Expo Go.
 *
 * Stack:
 *   @tensorflow/tfjs          → motor de inferência (CPU backend)
 *   expo-asset                → lê arquivos do bundle (.bin)
 *   expo-file-system          → lê bytes dos assets
 *   expo-image-manipulator    → redimensiona imagem para 224×224
 *   jpeg-js                   → decodifica JPEG → pixels RGB (pure JS)
 */

// Explicitly load CPU backend BEFORE importing tf to avoid Metro circular-dep
// issue where util module resolves to undefined and isTypedArray fails.
import '@tensorflow/tfjs-backend-cpu';
import * as tf from '@tensorflow/tfjs';
import { Asset } from 'expo-asset';
import * as FileSystem from 'expo-file-system';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import * as jpeg from 'jpeg-js';

export interface PredictionResult {
  result: string;
  classKey: string;
  confidence: number;
  description: string;
  recommendations: string[];
  processingTime: number;
}

type Labels = Record<string, string>;

// ─── Assets do modelo ────────────────────────────────────────────────────────
// model.json  → Metro devolve objeto JS (JSON parseado automaticamente)
// .bin        → Metro devolve asset ID (carregado via expo-asset)
const MODEL_JSON    = require('../../../assets/models/tfjs_model/model.json');
const MODEL_BIN     = require('../../../assets/models/tfjs_model/group1-shard1of1.bin');
const LABELS: Labels = require('../../../assets/models/labels_species.json');

const INPUT_SIZE = 224;

// ─── Descrições por classe ───────────────────────────────────────────────────
const CLASS_INFO: Record<string, { label: string; description: string; recommendations: string[] }> = {
  Blight: {
    label: 'Helmintosporiose',
    description: 'Helmintosporiose (Exserohilum turcicum): lesões alongadas cinza-esverdeadas a marrons, com formato elíptico nas folhas.',
    recommendations: [
      'Aplicar fungicida à base de azoxistrobina + propiconazol',
      'Usar híbridos resistentes na próxima safra',
      'Evitar plantio em áreas com histórico da doença sem rotação de culturas',
      'Monitorar umidade — doença favorecida por noites frias e úmidas',
    ],
  },
  Common_Rust: {
    label: 'Ferrugem-Comum',
    description: 'Ferrugem-comum (Puccinia sorghi): pústulas marrom-alaranjadas (urédias) distribuídas em ambas as faces da folha.',
    recommendations: [
      'Aplicar fungicida triazol + estrobilurina no início da infecção',
      'Monitorar a lavoura semanalmente no período crítico (V6 a VT)',
      'Preferir híbridos com resistência genética à ferrugem',
      'Realizar controle preventivo em anos com histórico da doença',
    ],
  },
  Gray_Leaf_Spot: {
    label: 'Mancha-Cinzenta',
    description: 'Mancha-cinzenta (Cercospora zeae-maydis): lesões retangulares cinza a marrons, delimitadas pelas nervuras da folha.',
    recommendations: [
      'Aplicar fungicida à base de trifloxistrobina + protioconazol',
      'Realizar rotação de culturas para reduzir inóculo no solo',
      'Evitar irrigação por aspersão no período noturno',
      'Usar híbridos com tolerância à mancha-cinzenta',
    ],
  },
  Healthy: {
    label: 'Milho Saudável',
    description: 'Planta de milho saudável, sem sinais visíveis de doença ou estresse foliar.',
    recommendations: [
      'Manter monitoramento regular da lavoura',
      'Continuar o programa de adubação e irrigação',
      'Inspecionar semanalmente para detecção precoce de problemas',
    ],
  },
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

// Pure-JS base64 decoder — avoids atob() quirks in Hermes / React Native
const _B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const _B64_LUT = new Uint8Array(256);
for (let _i = 0; _i < _B64.length; _i++) _B64_LUT[_B64.charCodeAt(_i)] = _i;

function base64ToUint8Array(base64: string): Uint8Array {
  const src = base64.replace(/=+$/, '');
  const len = src.length;
  const out = new Uint8Array(Math.floor(len * 3 / 4));
  let j = 0;
  for (let i = 0; i < len; i += 4) {
    const a = _B64_LUT[src.charCodeAt(i)];
    const b = _B64_LUT[src.charCodeAt(i + 1)];
    const c = _B64_LUT[src.charCodeAt(i + 2)];
    const d = _B64_LUT[src.charCodeAt(i + 3)];
    out[j++] = (a << 2) | (b >> 4);
    if (j < out.length) out[j++] = ((b & 0xf) << 4) | (c >> 2);
    if (j < out.length) out[j++] = ((c & 0x3) << 6) | d;
  }
  return out;
}

async function buildIOHandler(): Promise<tf.io.IOHandler> {
  // Carrega o arquivo .bin do bundle via expo-asset
  const [asset] = await Asset.loadAsync(MODEL_BIN);
  const base64 = await FileSystem.readAsStringAsync(asset.localUri!, {
    encoding: FileSystem.EncodingType.Base64,
  });
  const weightData = base64ToUint8Array(base64).buffer;

  return {
    load: async (): Promise<tf.io.ModelArtifacts> => ({
      modelTopology: MODEL_JSON.modelTopology,
      weightSpecs:   MODEL_JSON.weightsManifest[0].weights,
      weightData,
      format:        MODEL_JSON.format,
      generatedBy:   MODEL_JSON.generatedBy,
      convertedBy:   MODEL_JSON.convertedBy,
    }),
  };
}

async function preprocessImage(uri: string): Promise<tf.Tensor4D> {
  // 1. Redimensiona para 224×224 e obtém base64 JPEG
  const resized = await manipulateAsync(
    uri,
    [{ resize: { width: INPUT_SIZE, height: INPUT_SIZE } }],
    { format: SaveFormat.JPEG, base64: true },
  );
  if (!resized.base64) throw new Error('[TFLite] manipulateAsync não retornou base64');

  // 2. Decodifica JPEG → pixels RGBA (pure JS via jpeg-js)
  const bytes = base64ToUint8Array(resized.base64);
  console.log(`[TFLite] bytes JPEG: ${bytes.length}`);

  const decoded = jpeg.decode(bytes, { useTArray: true });
  if (!decoded || !decoded.data) throw new Error('[TFLite] jpeg.decode falhou — dados inválidos');
  const rgba = decoded.data as Uint8Array;
  console.log(`[TFLite] pixels RGBA: ${rgba.length} (esperado: ${INPUT_SIZE * INPUT_SIZE * 4})`);

  // 3. RGBA → Float32 RGB normalizado [0, 1]
  const float32 = new Float32Array(INPUT_SIZE * INPUT_SIZE * 3);
  for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
    float32[j]     = rgba[i]     / 255; // R
    float32[j + 1] = rgba[i + 1] / 255; // G
    float32[j + 2] = rgba[i + 2] / 255; // B
  }

  // 4. Cria tensor CPU — usa tf.tensor() em vez de tf.tensor4d() para evitar
  //    bug de resolução circular do Metro com util.isTypedArray
  return tf.tensor(float32, [1, INPUT_SIZE, INPUT_SIZE, 3], 'float32') as tf.Tensor4D;
}

// ─── Serviço principal ────────────────────────────────────────────────────────

class TFLiteService {
  private model: tf.LayersModel | null = null;
  private ready = false;

  async init(): Promise<void> {
    await tf.setBackend('cpu');
    await tf.ready();
    console.log(`[TFLite] Backend: ${tf.getBackend()}`);

    const handler = await buildIOHandler();
    this.model = await tf.loadLayersModel(handler);
    this.ready = true;

    const classes = Object.values(LABELS).join(', ');
    console.log(`[TFLite] Modelo carregado — classes: ${classes}`);

    // Aquece o modelo (elimina latência na primeira predição real)
    const dummy = tf.zeros([1, INPUT_SIZE, INPUT_SIZE, 3]);
    (this.model.predict(dummy) as tf.Tensor).dispose();
    dummy.dispose();
  }

  async predict(
    imageUri: string,
    _modelType: 'disease' | 'health' | 'species' | 'pest',
  ): Promise<PredictionResult | null> {
    if (!this.ready || !this.model) {
      throw new Error('[TFLite] Modelo não carregado. Aguarde a inicialização.');
    }
    if (!imageUri) {
      throw new Error('[TFLite] imageUri não fornecido.');
    }

    const t0 = Date.now();

    const input = await preprocessImage(imageUri);
    console.log(`[TFLite] tensor shape: ${input.shape}`);

    // tf.tidy disposes intermediate tensors automatically
    let probs: number[];
    try {
      const output = this.model.predict(input) as tf.Tensor;
      probs = Array.from(await output.data() as Float32Array);
      output.dispose();
    } finally {
      input.dispose();
    }
    console.log(`[TFLite] probs (${probs!.length}): ${probs!.map(p => p.toFixed(3)).join(', ')}`);

    const topIdx    = probs.indexOf(Math.max(...probs));
    const className = LABELS[String(topIdx)] ?? `class_${topIdx}`;
    const info      = CLASS_INFO[className] ?? CLASS_INFO['Healthy'];

    return {
      result:          info.label,
      classKey:        className,
      confidence:      probs[topIdx],
      description:     info.description,
      recommendations: info.recommendations,
      processingTime:  Date.now() - t0,
    };
  }

  isModelLoaded(_modelType: string): boolean {
    return this.ready;
  }

  getStatus() {
    return {
      ready:   this.ready,
      backend: tf.getBackend() ?? 'não inicializado',
      classes: Object.keys(LABELS).length,
    };
  }
}

let instance: TFLiteService | null = null;

export async function getTFLiteService(): Promise<TFLiteService> {
  if (!instance) {
    instance = new TFLiteService();
    await instance.init();
  }
  return instance;
}

export default TFLiteService;
