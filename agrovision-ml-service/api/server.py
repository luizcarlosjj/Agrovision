"""
AgroVision XAI Backend (FastAPI).

REST endpoints (compatibilidade):
  GET  /api/health
  POST /api/xai/gradcam

WebSocket endpoints (online-first, progresso em tempo real):
  WS   /ws/classify   — classifica imagem (Roboflow → local Keras fallback)
  WS   /ws/gradcam    — Grad-CAM + AL/AFS com progresso

Autenticação:
  HTTP  → header X-API-Key
  WS    → query param ?api_key=...

Variáveis de ambiente:
  AGROVISION_API_KEY   — chave compartilhada com o app mobile
  ROBOFLOW_API_KEY     — opcional, melhora classificação
  ROBOFLOW_MODEL_ID    — opcional, id do modelo Roboflow
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
from typing import List, Optional

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, Form, Header, HTTPException, Query, UploadFile, WebSocket
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from api.xai import gradcam as gradcam_mod
from api.xai import mask as mask_mod
from api.xai import overlay as overlay_mod
from api.xai import roboflow as roboflow_mod
from api.xai.metrics import compute_attention_leakage
from api.xai.model_loader import registry

IMG_SIZE = 224
_API_KEY = os.environ.get("AGROVISION_API_KEY", "")

app = FastAPI(
    title="AgroVision XAI Backend",
    description="Grad-CAM + Attention Leakage + WebSocket progress.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _load_model_on_startup() -> None:
    registry.load()


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def _check_api_key(key: str) -> bool:
    if not _API_KEY:
        return True  # não configurado → sem restrição (útil em dev local)
    return key == _API_KEY


def _require_http_key(key: str) -> None:
    if not _check_api_key(key):
        raise HTTPException(status_code=403, detail="Invalid API key")


# ─── Image helpers ─────────────────────────────────────────────────────────────

def _read_image_bytes(data: bytes) -> np.ndarray:
    try:
        pil = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Invalid image: {exc}")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def _preprocess_for_model(image_bgr: np.ndarray) -> tf.Tensor:
    resized = cv2.resize(image_bgr, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32)
    return tf.convert_to_tensor(rgb[None, ...])


def _encode_b64_png(image_bgr: np.ndarray) -> str:
    return base64.b64encode(overlay_mod.encode_png(image_bgr)).decode("ascii")


def _heatmap_to_gray_b64(heatmap: np.ndarray) -> str:
    gray = np.clip(heatmap * 255.0, 0, 255).astype(np.uint8)
    ok, buf = cv2.imencode(".png", gray)
    if not ok:
        raise RuntimeError("Failed to encode heatmap PNG")
    return base64.b64encode(buf.tobytes()).decode("ascii")


# ─── Sync computation functions (executadas em threadpool) ────────────────────

def _classify_sync(image_bytes: bytes) -> dict:
    """Classifica imagem: tenta Roboflow, cai no modelo Keras local."""
    if roboflow_mod.is_configured():
        try:
            result = roboflow_mod.classify(image_bytes)
            return {
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "source": "roboflow",
            }
        except Exception as exc:
            print(f"[classify] Roboflow failed ({exc}), falling back to local model")

    image_bgr = _read_image_bytes(image_bytes)
    input_tensor = _preprocess_for_model(image_bgr)
    preds = registry.model(input_tensor, training=False).numpy()
    pred_idx = int(np.argmax(preds[0]))
    confidence = float(preds[0, pred_idx])
    return {
        "prediction": registry.label_for(pred_idx),
        "predicted_index": pred_idx,
        "confidence": confidence,
        "source": "local",
    }


def _gradcam_sync(
    image_bytes: bytes,
    bbox_strategy: str,
    threshold: float,
    coverage: float,
    layer_name: Optional[str],
    predicted_class: Optional[str],
) -> dict:
    """Executa Grad-CAM + AL/AFS. Retorna dict compatível com GradCAMResponse."""
    t0 = time.perf_counter()

    image_bgr = _read_image_bytes(image_bytes)
    h, w = image_bgr.shape[:2]
    input_tensor = _preprocess_for_model(image_bgr)

    # Resolve o índice de classe a partir do nome (se fornecido pelo cliente)
    class_index: Optional[int] = None
    if predicted_class:
        for idx, label in registry.labels.items():
            if label.lower() == predicted_class.lower():
                class_index = idx
                break

    cam_hw, pred_idx, confidence = gradcam_mod.generate_gradcam(
        input_tensor=input_tensor,
        model=registry.model,
        layer_name=layer_name,
        class_index=class_index,
    )

    heatmap_full = cv2.resize(cam_hw, (w, h), interpolation=cv2.INTER_LINEAR)
    heatmap_full = np.clip(heatmap_full, 0.0, 1.0).astype(np.float32)

    strategy = (bbox_strategy or "fixed").lower()
    if strategy == "green":
        detected = mask_mod.green_segmentation_bbox(image_bgr)
        if detected is None:
            bbox = mask_mod.fixed_center_bbox((h, w), coverage=coverage)
            strategy = "fixed_fallback_from_green"
        else:
            bbox = detected
    else:
        bbox = mask_mod.fixed_center_bbox((h, w), coverage=coverage)
        strategy = "fixed"

    bin_mask = mask_mod.create_mask_from_bbox((h, w), bbox)
    metrics = compute_attention_leakage(heatmap_full, bin_mask, threshold=threshold)

    overlay_img = overlay_mod.overlay_heatmap(
        image_bgr=image_bgr, heatmap=heatmap_full, alpha=0.45, bbox=bbox,
    )

    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return {
        "prediction": registry.label_for(pred_idx),
        "predicted_index": pred_idx,
        "confidence": confidence,
        "al": metrics.al,
        "afs": metrics.afs,
        "threshold": metrics.threshold,
        "bbox_used": list(bbox),
        "bbox_strategy": strategy,
        "heatmap_b64": _heatmap_to_gray_b64(heatmap_full),
        "overlay_b64": _encode_b64_png(overlay_img),
        "image_width": w,
        "image_height": h,
        "layer_used": layer_name or "auto_last_conv",
        "processing_time_ms": elapsed_ms,
    }


# ─── WebSocket endpoints ───────────────────────────────────────────────────────

@app.websocket("/ws/classify")
async def ws_classify(websocket: WebSocket, api_key: str = Query(default="")):
    if not _check_api_key(api_key):
        await websocket.close(code=4003)
        return
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        req = json.loads(raw)
        image_bytes = base64.b64decode(req["image_b64"])

        await websocket.send_json({"event": "progress", "step": "preprocessing", "pct": 30})
        await websocket.send_json({"event": "progress", "step": "classifying", "pct": 65})

        result = await run_in_threadpool(_classify_sync, image_bytes)

        await websocket.send_json({"event": "progress", "step": "done", "pct": 100})
        await websocket.send_json({"event": "result", **result})
    except Exception as exc:
        try:
            await websocket.send_json({"event": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@app.websocket("/ws/gradcam")
async def ws_gradcam(websocket: WebSocket, api_key: str = Query(default="")):
    if not _check_api_key(api_key):
        await websocket.close(code=4003)
        return
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        req = json.loads(raw)
        image_bytes = base64.b64decode(req["image_b64"])

        bbox_strategy = req.get("bbox_strategy", "fixed")
        threshold     = float(req.get("threshold", 0.5))
        coverage      = float(req.get("coverage", 0.8))
        layer_name    = req.get("layer_name") or None
        predicted_class = req.get("predicted_class") or None

        await websocket.send_json({"event": "progress", "step": "preprocessing",       "pct": 10})
        await websocket.send_json({"event": "progress", "step": "building_model",      "pct": 25})
        await websocket.send_json({"event": "progress", "step": "computing_gradients", "pct": 55})

        result = await run_in_threadpool(
            _gradcam_sync,
            image_bytes, bbox_strategy, threshold, coverage, layer_name, predicted_class,
        )

        await websocket.send_json({"event": "progress", "step": "computing_metrics",  "pct": 80})
        await websocket.send_json({"event": "progress", "step": "rendering_overlay",  "pct": 95})
        await websocket.send_json({"event": "progress", "step": "done",               "pct": 100})
        await websocket.send_json({"event": "result", "data": result})
    except Exception as exc:
        try:
            await websocket.send_json({"event": "error", "message": str(exc)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# ─── REST endpoints (compatibilidade com versão anterior) ─────────────────────

class HealthResponse(BaseModel):
    status: str
    model_path: str
    num_classes: int
    conv_layers_tail: List[str]
    roboflow_configured: bool


class GradCAMResponse(BaseModel):
    prediction: str
    predicted_index: int
    confidence: float
    al: float
    afs: float
    threshold: float
    bbox_used: List[int]
    bbox_strategy: str
    heatmap_b64: str
    overlay_b64: str
    image_width: int
    image_height: int
    layer_used: str
    processing_time_ms: int


@app.get("/api/health", response_model=HealthResponse)
def health(x_api_key: str = Header(default="")) -> HealthResponse:
    _require_http_key(x_api_key)
    return HealthResponse(
        status="ok",
        model_path=str(registry._model_path),
        num_classes=len(registry.labels),
        conv_layers_tail=registry.conv_layer_names[-5:],
        roboflow_configured=roboflow_mod.is_configured(),
    )


@app.post("/api/xai/gradcam", response_model=GradCAMResponse)
async def xai_gradcam(
    image: UploadFile = File(...),
    bbox_strategy: str = Form("fixed"),
    coverage: float = Form(0.8),
    threshold: float = Form(0.5),
    layer_name: Optional[str] = Form(None),
    predicted_class: Optional[str] = Form(None),
    x_api_key: str = Header(default=""),
) -> GradCAMResponse:
    _require_http_key(x_api_key)
    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty image upload")
    try:
        result = await run_in_threadpool(
            _gradcam_sync,
            raw, bbox_strategy, threshold, coverage, layer_name, predicted_class,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return GradCAMResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=5000, reload=True)
