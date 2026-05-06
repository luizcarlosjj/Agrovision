/**
 * XAI Service — client for the Python Grad-CAM backend.
 *
 * The main app stays fully offline thanks to TFLite, but the scientific
 * "Test Mode" uses this service to query the Keras-backed XAI endpoint.
 * The backend URL is intentionally separate from the app's main API URL
 * (offline-first is preserved; XAI is opt-in, online-only).
 *
 * Configure with `EXPO_PUBLIC_XAI_URL` (defaults to `http://localhost:5000`).
 */

import axios, { AxiosInstance } from 'axios';
import {
  XAIBackendResponse,
  XAIHealth,
  XAIRequest,
  XAIResult,
} from '@models/xai';
import { logger } from '@utils/logger';

const DEFAULT_XAI_URL = 'https://agrovision-production-bdc3.up.railway.app';
const XAI_TIMEOUT_MS = 60_000;

function resolveBaseUrl(): string {
  const fromEnv = process.env.EXPO_PUBLIC_XAI_URL || process.env.XAI_URL;
  return (fromEnv ?? DEFAULT_XAI_URL).replace(/\/+$/, '');
}

function buildClient(): AxiosInstance {
  const client = axios.create({
    baseURL: resolveBaseUrl(),
    timeout: XAI_TIMEOUT_MS,
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

function inferMimeFromUri(uri: string): string {
  const lower = uri.toLowerCase();
  if (lower.endsWith('.png')) return 'image/png';
  if (lower.endsWith('.webp')) return 'image/webp';
  if (lower.endsWith('.heic') || lower.endsWith('.heif')) return 'image/heic';
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

export async function checkXAIBackendHealth(): Promise<XAIHealth | null> {
  try {
    const { data } = await xaiClient.get('/api/health', { timeout: 5_000 });
    return {
      status: data.status,
      modelPath: data.model_path,
      numClasses: data.num_classes,
      convLayersTail: data.conv_layers_tail ?? [],
    };
  } catch (err) {
    logger.log('[XAI] Backend unreachable at', resolveBaseUrl());
    return null;
  }
}

export async function analyzeWithXAI(req: XAIRequest): Promise<XAIResult> {
  const form = new FormData();

  const file = {
    uri: req.imageUri,
    name: inferFilenameFromUri(req.imageUri),
    type: inferMimeFromUri(req.imageUri),
  } as unknown as Blob;
  form.append('image', file);

  form.append('bbox_strategy', req.bboxStrategy);

  if (req.bboxStrategy === 'manual') {
    if (!req.bboxManual) {
      throw new Error("bboxManual is required when bboxStrategy is 'manual'");
    }
    const { x, y, width, height } = req.bboxManual;
    form.append('bbox_manual', `${x},${y},${width},${height}`);
  }

  if (req.threshold != null) {
    form.append('threshold', String(req.threshold));
  }
  if (req.coverage != null) {
    form.append('coverage', String(req.coverage));
  }
  if (req.layerName) {
    form.append('layer_name', req.layerName);
  }

  const { data } = await xaiClient.post<XAIBackendResponse>(
    '/api/xai/gradcam',
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );

  return toResult(data);
}

export function getXAIBaseUrl(): string {
  return resolveBaseUrl();
}
