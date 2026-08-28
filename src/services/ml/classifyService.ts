/**
 * Classification Service — 100% online via Roboflow (proxy Railway).
 *
 * Fluxo:
 *   1. Abre WebSocket /ws/classify no backend Railway com progresso em tempo real
 *   2. O backend encaminha a imagem para o modelo publicado no Roboflow e retorna
 *      a classe prevista (Blight, Common_Rust, Gray_Leaf_Spot, Healthy) + confiança
 *   3. Sem fallback local — se a rede/servidor falhar, o app mostra erro ao usuário
 */

import * as FileSystem from 'expo-file-system/legacy';
import { logger } from '@utils/logger';

const BASE_URL   = (process.env.EXPO_PUBLIC_API_URL ?? 'https://agrovision-production-bdc3.up.railway.app').replace(/\/+$/, '');
const API_KEY    = process.env.EXPO_PUBLIC_API_KEY ?? '';
const WS_TIMEOUT = 30_000; // ms — Roboflow can take 10-15s on cold start

function toWsUrl(url: string): string {
  return url.replace(/^https?/, (m) => (m === 'https' ? 'wss' : 'ws'));
}

export type ClassifySource = 'roboflow';

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

// ─── Descrições e recomendações por classe ────────────────────────────────────

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

function openWsConnection(
  b64: string,
  analysisType: string,
  t0: number,
  onProgress?: ProgressCallback,
): Promise<ClassifyResult> {
  return new Promise<ClassifyResult>((resolve, reject) => {
    const wsUrl = `${toWsUrl(BASE_URL)}/ws/classify?api_key=${encodeURIComponent(API_KEY)}`;
    const ws = new WebSocket(wsUrl);
    let settled = false;
    let timerId: ReturnType<typeof setTimeout>;

    const resetTimer = () => {
      clearTimeout(timerId);
      timerId = setTimeout(() => {
        if (!settled) {
          settled = true;
          ws.close();
          reject(new Error('timeout'));
        }
      }, WS_TIMEOUT);
    };
    resetTimer();

    ws.onopen = () => {
      ws.send(JSON.stringify({ image_b64: b64 }));
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data as string);
        if (msg.event === 'progress') {
          resetTimer(); // keep alive while server is actively progressing
          onProgress?.(msg.step, msg.pct);
        } else if (msg.event === 'result') {
          if (settled) return;
          settled = true;
          clearTimeout(timerId);
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
            source: 'roboflow',
          });
        } else if (msg.event === 'error') {
          if (settled) return;
          settled = true;
          clearTimeout(timerId);
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
        clearTimeout(timerId);
        reject(new Error('connection_error'));
      }
    };

    ws.onclose = (ev) => {
      if (!settled) {
        settled = true;
        clearTimeout(timerId);
        // código 4003 = chave de API rejeitada pelo servidor
        if (ev.code === 4003) {
          reject(new Error('invalid_api_key'));
        } else {
          reject(new Error('connection_error'));
        }
      }
    };
  });
}

async function classifyViaRailway(
  imageUri: string,
  analysisType: string,
  onProgress?: ProgressCallback,
): Promise<ClassifyResult> {
  const t0 = Date.now();

  const b64 = await FileSystem.readAsStringAsync(imageUri, {
    encoding: FileSystem.EncodingType.Base64,
  });

  try {
    return await openWsConnection(b64, analysisType, t0, onProgress);
  } catch (err) {
    const code = err instanceof Error ? err.message : '';

    if (code === 'invalid_api_key') {
      throw new Error('Chave de API inválida. Verifique as configurações do servidor.');
    }

    if (code !== 'connection_error' && code !== 'timeout') {
      // erro vindo do servidor (ex.: imagem corrompida) — não retentar
      throw err;
    }

    // O Railway hiberna após inatividade e pode levar alguns segundos para acordar.
    // Aguarda 4 s e tenta uma segunda vez antes de falhar definitivamente.
    logger.warn('[ClassifyService] Conexão falhou — servidor pode estar acordando. Tentando novamente em 4 s...');
    onProgress?.('Aguardando servidor...', 5);

    await new Promise<void>((r) => setTimeout(r, 4_000));

    try {
      return await openWsConnection(b64, analysisType, t0, onProgress);
    } catch {
      throw new Error(
        'Não foi possível conectar ao servidor de IA.\n' +
        'Verifique sua conexão com a internet e tente novamente.',
      );
    }
  }
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
