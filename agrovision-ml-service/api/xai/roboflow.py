"""
Roboflow classification proxy.

Calls the Roboflow Hosted Inference API for classification and returns a
normalised result dict.  Falls back gracefully when env vars are absent.

Required Railway env vars:
    ROBOFLOW_API_KEY   — rf_xxxxx…
    ROBOFLOW_MODEL_ID  — workspace/model-slug/version  e.g. "luiz/soja/1"
"""

from __future__ import annotations

import base64
import os
from typing import Optional

import requests as _requests

_API_KEY  = os.environ.get("ROBOFLOW_API_KEY", "")
_MODEL_ID = os.environ.get("ROBOFLOW_MODEL_ID", "")


def is_configured() -> bool:
    return bool(_API_KEY and _MODEL_ID)


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

    b64 = base64.b64encode(image_bytes).decode("ascii")

    # Roboflow classification endpoint
    parts = _MODEL_ID.strip("/").split("/")
    if len(parts) == 3:
        workspace, slug, version = parts
    elif len(parts) == 2:
        slug, version = parts
        workspace = ""
    else:
        raise RuntimeError(f"Invalid ROBOFLOW_MODEL_ID format: {_MODEL_ID!r}")

    url = f"https://classify.roboflow.com/{slug}/{version}?api_key={_API_KEY}"

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
