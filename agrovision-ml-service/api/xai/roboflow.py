"""
Roboflow classification proxy.

Calls the Roboflow Serverless Inference API for classification and returns a
normalised result dict.

Required Railway env vars:
    ROBOFLOW_API_KEY   — e.g. "nCS2G2BqZxMZoEJxLKGZ"
    ROBOFLOW_MODEL_ID  — workspace/model-slug/version  e.g. "apscivil/corn-maize-leaf-disease-kmpiq/2"
"""

from __future__ import annotations

import base64
import io
import os

import requests as _requests
from PIL import Image

_API_KEY  = os.environ.get("ROBOFLOW_API_KEY", "")
_MODEL_ID = os.environ.get("ROBOFLOW_MODEL_ID", "")

_MAX_SIDE = 640  # px — keeps payload under Roboflow's 1.5 MB limit


def is_configured() -> bool:
    return bool(_API_KEY and _MODEL_ID)


def _resize_image(image_bytes: bytes) -> bytes:
    """Resize to at most _MAX_SIDE on the longest side and re-encode as JPEG."""
    pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if pil.width > _MAX_SIDE or pil.height > _MAX_SIDE:
        pil.thumbnail((_MAX_SIDE, _MAX_SIDE), Image.LANCZOS)
    buf = io.BytesIO()
    pil.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def classify(image_bytes: bytes) -> dict:
    """
    Returns:
        {
            "prediction": str,
            "confidence": float,
            "all_predictions": [{"class": str, "confidence": float}, ...]
        }
    Raises RuntimeError on any failure.
    """
    if not is_configured():
        raise RuntimeError("Roboflow not configured (ROBOFLOW_API_KEY / ROBOFLOW_MODEL_ID missing)")

    image_bytes = _resize_image(image_bytes)
    b64 = base64.b64encode(image_bytes).decode("ascii")

    # MODEL_ID may be "workspace/slug/version" or "slug/version"
    parts = _MODEL_ID.strip("/").split("/")
    if len(parts) == 3:
        _workspace, slug, version = parts
    elif len(parts) == 2:
        slug, version = parts
    else:
        raise RuntimeError(f"Invalid ROBOFLOW_MODEL_ID format: {_MODEL_ID!r}")

    # Roboflow Serverless API — workspace is NOT part of the URL
    url = f"https://serverless.roboflow.com/{slug}/{version}?api_key={_API_KEY}"

    resp = _requests.post(
        url,
        data=b64,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    preds = data.get("predictions") or data.get("top") or []
    if not preds:
        raise RuntimeError(f"Roboflow returned no predictions: {data}")

    # Support both list-of-dicts and single-prediction formats
    if isinstance(preds, list):
        top = preds[0]
    else:
        top = {"class": preds, "confidence": data.get("confidence", 0.0)}

    return {
        "prediction": top.get("class", "unknown"),
        "confidence": float(top.get("confidence", 0.0)),
        "all_predictions": preds if isinstance(preds, list) else [top],
    }
