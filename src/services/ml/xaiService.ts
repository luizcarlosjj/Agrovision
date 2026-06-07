/**
 * XAI Service — Grad-CAM via Railway.
 *
 * Dois modos:
 *   analyzeWithXAIWS   — WebSocket com progresso em tempo real (preferido)
 *   analyzeWithXAI     — HTTP multipart (fallback / compatibilidade)
 *   checkXAIBackendHealth — verifica disponibilidade do backend
 */

import axios, { AxiosInstance } from 'axios';
import * as FileSystem from 'expo-file-system/legacy';
import {
  XAIBackendResponse,
  XAIHealth,
  XAIRequest,
  XAIResult,
} from '@models/xai';
import { logger } from '@utils/logger';

const BASE_URL    = (process.env.EXPO_PUBLIC_API_URL ?? 'https://agrovision-production-bdc3.up.railway.app').replace(/\/+$/, '');
const API_KEY     = process.env.EXPO_PUBLIC_API_KEY ?? '';
const WS_TIMEOUT  = 90_000; // ms — Grad-CAM pode demorar até ~20s no cold start

function toWsUrl(url: string): string {
  return url.replace(/^https?/, (m) => (m === 'https' ? 'wss' : 'ws'));
}

// ─── HTTP client (com API key no header) ──────────────────────────────────────

function buildClient(): AxiosInstance {
  const client = axios.create({ baseURL: BASE_URL, timeout: 90_000 });
  client.interceptors.request.use((config) => {
    if (API_KEY) {
      config.headers = config.headers ?? {};
      config.headers['X-API-Key'] = API_KEY;
    }
    return config;
  });
  client.interceptors.response.use(
    (r) => r,
    (err) => {
      logger.error('[XAI] Request failed:', err?.message ?? err);
      return Promise.reject(err);
    },
  );
  return client;
}

const xaiClient = buildClient();

// ─── Helpers ──────────────────────────────────────────────────────────────────

function inferMimeFromUri(uri: string): string {
  const l = uri.toLowerCase();
  if (l.endsWith('.png')) return 'image/png';
  if (l.endsWith('.webp')) return 'image/webp';
  if (l.endsWith('.heic') || l.endsWith('.heif')) return 'image/heic';
  return 'image/jpeg';
}

function inferFilenameFromUri(uri: string): string {
  const clean = uri.split('?')[0].split('#')[0];
  const last = clean.split('/').pop();
  return last && last.length > 0 ? last : 'upload.jpg';
}

function toResult(raw: XAIBackendResponse): XAIResult {
  const [x, y, w, h] = raw.bbox_used;
  return {
    prediction: raw.prediction,
    predictedIndex: raw.predicted_index,
    confidence: raw.confidence,
    al: raw.al,
    afs: raw.afs,
    threshold: raw.threshold,
    bboxUsed: { x, y, width: w, height: h },
    bboxStrategy: raw.bbox_strategy,
    heatmapB64: raw.heatmap_b64,
    overlayB64: raw.overlay_b64,
    imageWidth: raw.image_width,
    imageHeight: raw.image_height,
    layerUsed: raw.layer_used,
    processingTimeMs: raw.processing_time_ms,
  };
}

// ─── Health check ─────────────────────────────────────────────────────────────

export async function checkXAIBackendHealth(): Promise<XAIHealth | null> {
  try {
    const { data } = await xaiClient.get('/api/health', { timeout: 5_000 });
    return {
      status: data.status,
      modelPath: data.model_path,
      numClasses: data.num_classes,
      convLayersTail: data.conv_layers_tail ?? [],
    };
  } catch {
    logger.log('[XAI] Backend unreachable at', BASE_URL);
    return null;
  }
}

// ─── WebSocket Grad-CAM (preferido) ───────────────────────────────────────────

export type XAIProgressCallback = (step: string, pct: number) => void;

export async function analyzeWithXAIWS(
  req: XAIRequest,
  onProgress?: XAIProgressCallback,
): Promise<XAIResult> {
  const b64 = await FileSystem.readAsStringAsync(req.imageUri, {
    encoding: FileSystem.EncodingType.Base64,
  });

  return new Promise<XAIResult>((resolve, reject) => {
    const wsUrl = `${toWsUrl(BASE_URL)}/ws/gradcam?api_key=${encodeURIComponent(API_KEY)}`;
    const ws = new WebSocket(wsUrl);
    let settled = false;

    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        ws.close();
        reject(new Error('XAI WebSocket timeout'));
      }
    }, WS_TIMEOUT);

    ws.onopen = () => {
      ws.send(JSON.stringify({
        image_b64: b64,
        bbox_strategy: req.bboxStrategy,
        threshold: req.threshold ?? 0.5,
        coverage: req.coverage ?? 0.8,
        layer_name: req.layerName ?? null,
        predicted_class: req.predictedClass ?? null,
      }));
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
          resolve(toResult(msg.data as XAIBackendResponse));
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
        reject(new Error('XAI WebSocket connection error'));
      }
    };

    ws.onclose = () => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error('XAI WebSocket closed unexpectedly'));
      }
    };
  });
}

// ─── HTTP Grad-CAM (fallback / TestModeScreen batch) ─────────────────────────

export async function analyzeWithXAI(req: XAIRequest): Promise<XAIResult> {
  const form = new FormData();
  form.append('image', {
    uri: req.imageUri,
    name: inferFilenameFromUri(req.imageUri),
    type: inferMimeFromUri(req.imageUri),
  } as unknown as Blob);
  form.append('bbox_strategy', req.bboxStrategy);
  if (req.threshold != null) form.append('threshold', String(req.threshold));
  if (req.coverage != null)  form.append('coverage',  String(req.coverage));
  if (req.layerName)         form.append('layer_name', req.layerName);
  if (req.predictedClass)    form.append('predicted_class', req.predictedClass);

  const { data } = await xaiClient.post<XAIBackendResponse>(
    '/api/xai/gradcam',
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return toResult(data);
}

export function getXAIBaseUrl(): string {
  return BASE_URL;
}
