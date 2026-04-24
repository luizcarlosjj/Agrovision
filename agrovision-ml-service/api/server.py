"""
AgroVision XAI Backend (FastAPI).

Exposes endpoints that run Grad-CAM on the trained Keras model and return
the Attention Leakage / Attention Focus Score metrics plus a PNG overlay
for visualization inside the mobile app.

Run locally:
    uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload
"""

from __future__ import annotations

import base64
import io
import time
from typing import List, Optional

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from api.xai import gradcam as gradcam_mod
from api.xai import mask as mask_mod
from api.xai import overlay as overlay_mod
from api.xai.metrics import compute_attention_leakage
from api.xai.model_loader import registry


IMG_SIZE = 224  # Matches train_species.py


app = FastAPI(
    title="AgroVision XAI Backend",
    description="Grad-CAM + Attention Leakage metrics on the Keras model.",
    version="1.0.0",
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


class HealthResponse(BaseModel):
    status: str
    model_path: str
    num_classes: int
    conv_layers_tail: List[str]


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
def health() -> HealthResponse:
    labels = registry.labels
    conv_tail = registry.conv_layer_names[-5:]
    return HealthResponse(
        status="ok",
        model_path=str(registry._model_path),
        num_classes=len(labels),
        conv_layers_tail=conv_tail,
    )


def _read_image_bytes(data: bytes) -> np.ndarray:
    """Decode uploaded bytes into a BGR uint8 ndarray."""
    try:
        pil = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid image: {exc}")
    arr_rgb = np.array(pil)
    return cv2.cvtColor(arr_rgb, cv2.COLOR_RGB2BGR)


def _preprocess_for_model(image_bgr: np.ndarray) -> tf.Tensor:
    """Resize to model input and return a float tensor (1, H, W, 3)."""
    resized = cv2.resize(image_bgr, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32)
    # MobileNetV2 preprocessing is baked into the model, so pass raw 0..255 float.
    return tf.convert_to_tensor(rgb[None, ...])


def _encode_b64_png(image_bgr: np.ndarray) -> str:
    return base64.b64encode(overlay_mod.encode_png(image_bgr)).decode("ascii")


def _heatmap_to_gray_png(heatmap: np.ndarray) -> bytes:
    gray = np.clip(heatmap * 255.0, 0, 255).astype(np.uint8)
    ok, buf = cv2.imencode(".png", gray)
    if not ok:
        raise RuntimeError("Failed to encode heatmap PNG")
    return buf.tobytes()


@app.post("/api/xai/gradcam", response_model=GradCAMResponse)
async def xai_gradcam(
    image: UploadFile = File(...),
    bbox_strategy: str = Form("fixed"),
    bbox_manual: Optional[str] = Form(None),
    coverage: float = Form(0.8),
    threshold: float = Form(0.5),
    layer_name: Optional[str] = Form(None),
) -> GradCAMResponse:
    t0 = time.perf_counter()

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty image upload")

    image_bgr = _read_image_bytes(raw)
    h, w = image_bgr.shape[:2]

    # 1) Inference + Grad-CAM at model input resolution
    input_tensor = _preprocess_for_model(image_bgr)
    cam_input_size, pred_idx, confidence = gradcam_mod.generate_gradcam(
        input_tensor=input_tensor,
        model=registry.model,
        layer_name=layer_name,
    )

    # 2) Resize heatmap to the original image size for AL computation + overlay
    heatmap_full = cv2.resize(cam_input_size, (w, h), interpolation=cv2.INTER_LINEAR)
    heatmap_full = np.clip(heatmap_full, 0.0, 1.0).astype(np.float32)

    # 3) Build bbox according to strategy
    strategy = (bbox_strategy or "fixed").lower()
    if strategy == "manual":
        if not bbox_manual:
            raise HTTPException(
                status_code=400,
                detail="bbox_manual is required when bbox_strategy='manual'",
            )
        try:
            bbox = mask_mod.parse_bbox_string(bbox_manual)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    elif strategy == "green":
        detected = mask_mod.green_segmentation_bbox(image_bgr)
        if detected is None:
            # Graceful fallback so the endpoint still returns usable metrics.
            bbox = mask_mod.fixed_center_bbox((h, w), coverage=coverage)
            strategy = "fixed_fallback_from_green"
        else:
            bbox = detected
    else:
        bbox = mask_mod.fixed_center_bbox((h, w), coverage=coverage)
        strategy = "fixed"

    bin_mask = mask_mod.create_mask_from_bbox((h, w), bbox)

    # 4) Attention Leakage + Focus Score
    metrics = compute_attention_leakage(heatmap_full, bin_mask, threshold=threshold)

    # 5) Overlay render
    overlay_img = overlay_mod.overlay_heatmap(
        image_bgr=image_bgr,
        heatmap=heatmap_full,
        alpha=0.45,
        bbox=bbox,
    )

    heatmap_b64 = base64.b64encode(_heatmap_to_gray_png(heatmap_full)).decode("ascii")
    overlay_b64 = _encode_b64_png(overlay_img)

    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    return GradCAMResponse(
        prediction=registry.label_for(pred_idx),
        predicted_index=pred_idx,
        confidence=confidence,
        al=metrics.al,
        afs=metrics.afs,
        threshold=metrics.threshold,
        bbox_used=list(bbox),
        bbox_strategy=strategy,
        heatmap_b64=heatmap_b64,
        overlay_b64=overlay_b64,
        image_width=w,
        image_height=h,
        layer_used=layer_name or "auto_last_conv",
        processing_time_ms=elapsed_ms,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.server:app", host="0.0.0.0", port=5000, reload=True)
