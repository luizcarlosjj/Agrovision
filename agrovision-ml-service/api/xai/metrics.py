from dataclasses import dataclass

import numpy as np


@dataclass
class AttentionMetrics:
    al: float            # Atenção fora da folha / total — quanto o modelo "escapou"
    afs: float           # 1 - AL — quanto ficou dentro da folha
    inside_sum: float
    outside_sum: float
    total_sum: float
    threshold: float
    roi_area_frac: float  # Tamanho da ROI em relação à imagem inteira
    afs_norm: float       # AFS / roi_area_frac — >1 significa foco real, não por sorte
    pointing_hit: bool    # O pixel de maior ativação está dentro da folha?
    dist_centroide: float # Distância entre centro de atenção e centro da folha (0=perfeito)


def compute_attention_leakage(
    heatmap: np.ndarray,
    mask: np.ndarray,
    threshold: float = 0.5,
) -> AttentionMetrics:
    if heatmap.shape != mask.shape:
        raise ValueError(
            f"Shape mismatch: heatmap {heatmap.shape} vs mask {mask.shape}"
        )
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    H, W = heatmap.shape[:2]
    h = heatmap.astype(np.float32, copy=False)
    m = (mask > 0).astype(np.float32)

    roi_area_frac = float(m.sum()) / float(m.size) if m.size > 0 else 0.0

    # Ignora pixels de baixa ativação (ruído)
    active = np.where(h >= threshold, h, 0.0)

    inside = float((active * m).sum())
    outside = float((active * (1.0 - m)).sum())
    total = inside + outside

    if total <= 0.0:
        return AttentionMetrics(
            al=0.0, afs=1.0, inside_sum=0.0, outside_sum=0.0, total_sum=0.0,
            threshold=threshold, roi_area_frac=roi_area_frac,
            afs_norm=0.0, pointing_hit=False, dist_centroide=1.0,
        )

    # ← OLHE AQUI: fórmulas centrais da intervenção
    al = outside / total          # Attention Leakage
    afs = 1.0 - al                # Attention Focus Score
    afs_norm = afs / roi_area_frac if roi_area_frac > 0.0 else 0.0  # Normalizado pelo tamanho da ROI

    # ← OLHE AQUI: pico de ativação dentro ou fora da folha?
    max_idx = int(active.argmax())
    max_row, max_col = divmod(max_idx, W)
    pointing_hit = bool(m[max_row, max_col] > 0)

    # ← OLHE AQUI: distância entre centróide de atenção e centróide da folha
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
        al=al, afs=afs, inside_sum=inside, outside_sum=outside, total_sum=total,
        threshold=threshold, roi_area_frac=roi_area_frac,
        afs_norm=afs_norm, pointing_hit=pointing_hit, dist_centroide=dist_centroide,
    )
