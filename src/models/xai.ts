/**
 * XAI (Explainable AI) domain types.
 *
 * These types describe the contract with the Python FastAPI backend at
 * `/api/xai/gradcam`, plus the local persistence shape used by the mobile
 * app (SQLite + CSV export).
 */

export type BBoxStrategy = 'fixed' | 'green' | 'manual';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type FramingLabel = 'bem_enquadrada' | 'mal_enquadrada' | 'nao_classificada';

/**
 * Request parameters sent to the XAI backend.
 */
export interface XAIRequest {
  imageUri: string;
  bboxStrategy: BBoxStrategy;
  bboxManual?: BoundingBox;
  threshold?: number;
  coverage?: number;
  layerName?: string;
  /** Classe predita (do classificador) passada ao Grad-CAM como alvo. */
  predictedClass?: string;
}

/**
 * Raw JSON returned by the backend (matches api/server.py::GradCAMResponse).
 */
export interface XAIBackendResponse {
  prediction: string;
  predicted_index: number;
  confidence: number;
  al: number;
  afs: number;
  threshold: number;
  bbox_used: [number, number, number, number];
  bbox_strategy: string;
  heatmap_b64: string;
  overlay_b64: string;
  image_width: number;
  image_height: number;
  layer_used: string;
  processing_time_ms: number;
}

/**
 * Parsed / camelCased result used by the UI.
 */
export interface XAIResult {
  prediction: string;
  predictedIndex: number;
  confidence: number;
  al: number;
  afs: number;
  threshold: number;
  bboxUsed: BoundingBox;
  bboxStrategy: string;
  heatmapB64: string;
  overlayB64: string;
  imageWidth: number;
  imageHeight: number;
  layerUsed: string;
  processingTimeMs: number;
}

/**
 * Persisted test record (one row in the `xai_tests` SQLite table).
 */
export interface XAITestRecord {
  id: string;
  imageUri: string;
  prediction: string;
  confidence: number;
  al: number;
  afs: number;
  threshold: number;
  bbox: BoundingBox;
  bboxStrategy: string;
  overlayB64: string;
  label: FramingLabel;
  createdAt: string;
}

/**
 * Backend health payload.
 */
export interface XAIHealth {
  status: string;
  modelPath: string;
  numClasses: number;
  convLayersTail: string[];
}
