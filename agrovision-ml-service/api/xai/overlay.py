from typing import Tuple

import cv2
import numpy as np


def overlay_heatmap(
    image_bgr: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.45,
    bbox: Tuple[int, int, int, int] | None = None,
) -> np.ndarray:
    if image_bgr.shape[:2] != heatmap.shape:
        heatmap_resized = cv2.resize(
            heatmap, (image_bgr.shape[1], image_bgr.shape[0]),
            interpolation=cv2.INTER_LINEAR,
        )
    else:
        heatmap_resized = heatmap

    # Converte o heatmap [0,1] para colormap JET (azul=baixo, vermelho=alto)
    heatmap_uint8 = np.clip(heatmap_resized * 255.0, 0, 255).astype(np.uint8)
    colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    blended = cv2.addWeighted(image_bgr, 1.0 - alpha, colored, alpha, 0.0)

    # Desenha o contorno da bbox usada no cálculo do AL
    if bbox is not None:
        x, y, w, h = bbox
        cv2.rectangle(blended, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return blended


def encode_png(image_bgr: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", image_bgr)
    if not ok:
        raise RuntimeError("Failed to encode image as PNG")
    return buf.tobytes()
