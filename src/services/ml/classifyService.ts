/**
 * Classification Service — online-first com fallback TFLite.
 *
 * Fluxo:
 *   1. Tenta WebSocket /ws/classify no Railway (progresso em tempo real)
 *   2. Em caso de falha/timeout (10 s), cai no TFLite local (offline)
 *
 * O resultado tem o mesmo shape que o analysisService retornava, permitindo
 * que o AnalysisContext funcione sem alterações no esquema do SQLite.
 */

import * as FileSystem from 'expo-file-system/legacy';
import { logger } from '@utils/logger';

const BASE_URL   = (process.env.EXPO_PUBLIC_API_URL ?? 'https://agrovision-production-bdc3.up.railway.app').replace(/\/+$/, '');
const API_KEY    = process.env.EXPO_PUBLIC_API_KEY ?? '';
const WS_TIMEOUT = 12_000; // ms

// Converte https:// → wss://, http:// → ws://
function toWsUrl(url: string): string {
  return url.replace(/^https?/, (m) => (m === 'https' ? 'wss' : 'ws'));
}

export type ClassifySource = 'roboflow' | 'local' | 'tflite';

export interface ClassifyResult {
  id: string;
  type: string;
  result: string;
  classKey: string;
  confidence: number;
  description: string;
  recommendations: string[];
  timestamp: string;
  processingTime: number;
  source: ClassifySource;
}

export type ProgressCallback = (step: string, pct: number) => void;

// ─── Descrições e recomendações por classe (mesmo conteúdo do tfliteService) ─

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

function getClassInfo(className: string) {
  const normalized = className.toLowerCase().replace(/[\s-]/g, '_');
  return (
    CLASS_INFO[className] ??
    CLASS_INFO[normalized] ??
    CLASS_INFO['Healthy']
  );
}

const genId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

// ─── Railway WebSocket ─────────────────────────────────────────────────────────

async function classifyViaRailway(
  imageUri: string,
  analysisType: string,
  onProgress?: ProgressCallback,
): Promise<ClassifyResult> {
  const t0 = Date.now();

  // Lê o arquivo como base64
  const b64 = await FileSystem.readAsStringAsync(imageUri, {
    encoding: FileSystem.EncodingType.Base64,
  });

  return new Promise<ClassifyResult>((resolve, reject) => {
    const wsUrl = `${toWsUrl(BASE_URL)}/ws/classify?api_key=${encodeURIComponent(API_KEY)}`;
    const ws = new WebSocket(wsUrl);
    let settled = false;

    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        ws.close();
        reject(new Error('Railway classify timeout'));
      }
    }, WS_TIMEOUT);

    ws.onopen = () => {
      ws.send(JSON.stringify({ image_b64: b64 }));
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data as string);
        if (msg.event === 'progress') {
          onProgress?.(msg.step, msg.pct);
        } else if (msg.event === 'result') {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          ws.close();

          const info = getClassInfo(msg.prediction);
          resolve({
            id: genId(),
            type: analysisType,
            result: info.label,
            classKey: msg.prediction,
            confidence: msg.confidence,
            description: info.description,
            recommendations: info.recommendations,
            timestamp: new Date().toISOString(),
            processingTime: Date.now() - t0,
            source: (msg.source === 'roboflow' ? 'roboflow' : 'local') as ClassifySource,
          });
        } else if (msg.event === 'error') {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          ws.close();
          reject(new Error(msg.message));
        }
      } catch {
        // ignora mensagens malformadas
      }
    };

    ws.onerror = () => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error('WebSocket connection error'));
      }
    };

    ws.onclose = () => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error('WebSocket closed unexpectedly'));
      }
    };
  });
}

// ─── Ponto de entrada público ──────────────────────────────────────────────────

export async function classify(
  imageUri: string,
  analysisType: string,
  onProgress?: ProgressCallback,
): Promise<ClassifyResult> {
  logger.log('[ClassifyService] Calling Railway WebSocket...');
  return await classifyViaRailway(imageUri, analysisType, onProgress);
}
