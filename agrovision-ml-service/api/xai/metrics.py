"""
Attention Leakage (AL) and Attention Focus Score (AFS).

    AL  = sum(activations outside mask) / sum(all activations)
    AFS = 1 - AL

Additional metrics:
    roi_area_frac  = mask_pixels / total_pixels
    afs_norm       = AFS / roi_area_frac
                     Removes the trivial effect of ROI size. Value 1 means
                     attention is distributed as if random; >1 means the model
                     focuses inside the ROI beyond chance level.
    pointing_hit   = True if the peak activation pixel falls inside the ROI.
    dist_centroide = Euclidean distance between the attention centroid
                     (weighted by activation values) and the ROI centroid,
                     normalized by the image diagonal. 0 = perfectly aligned,
                     1 = maximum possible separation.

A threshold is applied to the heatmap first to cut low-intensity noise; the
raw heatmap is expected to be already normalized to [0, 1] by the Grad-CAM
stage.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class AttentionMetrics:
    al: float
    afs: float
    inside_sum: float
    outside_sum: float
    total_sum: float
    threshold: float
    roi_area_frac: float
    afs_norm: float
    pointing_hit: bool
    dist_centroide: float


def compute_attention_leakage(
    heatmap: np.ndarray,
    mask: np.ndarray,
    threshold: float = 0.5,
) -> AttentionMetrics:
    """
    Compute AL, AFS, and auxiliary XAI metrics given a normalized heatmap
    [0, 1] and a binary mask {0, 1}. Shapes must match; caller is responsible
    for resizing the heatmap to the image size before calling this.
    """
    if heatmap.shape != mask.shape:
        raise ValueError(
            f"Shape mismatch: heatmap {heatmap.shape} vs mask {mask.shape}"
        )
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    H, W = heatmap.shape[:2]
    h = heatmap.astype(np.float32, copy=False)
    m = (mask > 0).astype(np.float32)

    # roi_area_frac: fraction of the image covered by the ROI mask.
    roi_area_frac = float(m.sum()) / float(m.size) if m.size > 0 else 0.0

    # Zero out pixels below threshold to suppress low-attention noise.
    active = np.where(h >= threshold, h, 0.0)

    inside = float((active * m).sum())
    outside = float((active * (1.0 - m)).sum())
    total = inside + outside

    # Degenerate case: no activation above threshold anywhere.
    if total <= 0.0:
        return AttentionMetrics(
            al=0.0,
            afs=1.0,
            inside_sum=0.0,
            outside_sum=0.0,
            total_sum=0.0,
            threshold=threshold,
            roi_area_frac=roi_area_frac,
            afs_norm=0.0,
            pointing_hit=False,
            dist_centroide=1.0,
        )

    al = outside / total
    afs = 1.0 - al

    # afs_norm: AFS / roi_area_frac — concentration above chance.
    # If roi_area_frac == 0 (empty mask), return 0 (undefined, treat as worst case).
    afs_norm = afs / roi_area_frac if roi_area_frac > 0.0 else 0.0

    # pointing_hit: True if the peak activation pixel falls inside the ROI.
    max_idx = int(active.argmax())
    max_row, max_col = divmod(max_idx, W)
    pointing_hit = bool(m[max_row, max_col] > 0)

    # dist_centroide: distance between attention centroid and ROI centroid,
    # normalized by image diagonal so the result is always in [0, 1].
    # Attention centroid uses activation values as weights.
    row_grid = np.arange(H, dtype=np.float32)[:, None] * np.ones(W, dtype=np.float32)
    col_grid = np.ones(H, dtype=np.float32)[:, None] * np.arange(W, dtype=np.float32)

    attn_sum = float(active.sum())
    cy_attn = float((row_grid * active).sum()) / attn_sum
    cx_attn = float((col_grid * active).sum()) / attn_sum

    mask_ys, mask_xs = np.where(m > 0)
    if len(mask_ys) > 0:
        cy_roi = float(mask_ys.mean())
        cx_roi = float(mask_xs.mean())
    else:
        cy_roi, cx_roi = H / 2.0, W / 2.0

    diagonal = float(np.sqrt(H ** 2 + W ** 2))
    dist_centroide = (
        float(np.sqrt((cy_attn - cy_roi) ** 2 + (cx_attn - cx_roi) ** 2)) / diagonal
        if diagonal > 0.0
        else 0.0
    )

    return AttentionMetrics(
        al=al,
        afs=afs,
        inside_sum=inside,
        outside_sum=outside,
        total_sum=total,
        threshold=threshold,
        roi_area_frac=roi_area_frac,
        afs_norm=afs_norm,
        pointing_hit=pointing_hit,
        dist_centroide=dist_centroide,
    )
