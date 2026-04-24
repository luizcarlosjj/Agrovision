"""
Attention Leakage (AL) and Attention Focus Score (AFS).

    AL  = sum(activations outside mask) / sum(all activations)
    AFS = 1 - AL

A threshold is applied to the heatmap first to cut low-intensity noise; the
raw heatmap is expected to be already normalized to [0, 1] by the Grad-CAM
stage.
"""

from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class AttentionMetrics:
    al: float
    afs: float
    inside_sum: float
    outside_sum: float
    total_sum: float
    threshold: float


def compute_attention_leakage(
    heatmap: np.ndarray,
    mask: np.ndarray,
    threshold: float = 0.5,
) -> AttentionMetrics:
    """
    Compute AL and AFS given a normalized heatmap [0, 1] and a binary mask
    {0, 1}. Shapes must match; caller is responsible for resizing the heatmap
    to the image size before calling this.
    """
    if heatmap.shape != mask.shape:
        raise ValueError(
            f"Shape mismatch: heatmap {heatmap.shape} vs mask {mask.shape}"
        )
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    h = heatmap.astype(np.float32, copy=False)
    m = (mask > 0).astype(np.float32)

    # Zero out pixels below threshold to suppress low-attention noise.
    active = np.where(h >= threshold, h, 0.0)

    inside = float((active * m).sum())
    outside = float((active * (1.0 - m)).sum())
    total = inside + outside

    if total <= 0.0:
        # No activation above threshold anywhere — degenerate case.
        return AttentionMetrics(
            al=0.0,
            afs=1.0,
            inside_sum=0.0,
            outside_sum=0.0,
            total_sum=0.0,
            threshold=threshold,
        )

    al = outside / total
    afs = 1.0 - al
    return AttentionMetrics(
        al=al,
        afs=afs,
        inside_sum=inside,
        outside_sum=outside,
        total_sum=total,
        threshold=threshold,
    )
