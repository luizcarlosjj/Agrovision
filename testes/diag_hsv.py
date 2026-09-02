"""Diagnóstico do limiar HSV e geração de máscaras de debug."""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

TESTES_DIR = Path(__file__).parent
DATASET_DIR = TESTES_DIR / "dataset"
DEBUG_DIR   = TESTES_DIR / "resultados" / "debug_masks"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)

# ── 1. Cor do fundo das augmentações ──────────────────────────────────────────
bg_rgb = (30, 60, 20)
bg_bgr = np.array([[[bg_rgb[2], bg_rgb[1], bg_rgb[0]]]], dtype=np.uint8)
bg_hsv = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2HSV)[0, 0]
print(f"Fundo Pillow RGB{bg_rgb}  ->  HSV OpenCV  H={bg_hsv[0]}  S={bg_hsv[1]}  V={bg_hsv[2]}")

LOWER_CUR = np.array([25, 30, 30])
UPPER_CUR = np.array([95, 255, 255])
inside_cur = all(LOWER_CUR[i] <= int(bg_hsv[i]) <= UPPER_CUR[i] for i in range(3))
print(f"Fundo está dentro do limiar ATUAL  [{LOWER_CUR}]→[{UPPER_CUR}]? {inside_cur}")
print()

print("Teste de limiares alternativos (aumentando V_min e S_min):")
for v_min, s_min in [(30,30),(40,40),(60,50),(70,50),(80,50),(80,60)]:
    low2 = np.array([25, s_min, v_min])
    hi2  = np.array([95, 255, 255])
    inc  = all(int(low2[i]) <= int(bg_hsv[i]) <= int(hi2[i]) for i in range(3))
    print(f"  V_min={v_min:3d}  S_min={s_min:3d}  → fundo incluído? {str(inc):<5}  limiar=[{low2}]→[{hi2}]")
print()

# ── 2. Testar em imagens zoom_out conhecidas ───────────────────────────────────
meta_path = DATASET_DIR / "aug_metadata.csv"
if not meta_path.exists():
    print("aug_metadata.csv não encontrado — abortando.")
    sys.exit(1)

zoom_out_rows = []
with open(meta_path, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["transformacao"] == "zoom_out":
            zoom_out_rows.append(row)

zoom_out_rows = zoom_out_rows[:6]   # primeiras 6 para não demorar

CANDIDATES = [
    ("atual",       np.array([25, 30, 30]),  np.array([95, 255, 255])),
    ("V80_S50",     np.array([25, 50, 80]),  np.array([95, 255, 255])),
    ("V80_S60",     np.array([25, 60, 80]),  np.array([95, 255, 255])),
    ("V90_S60",     np.array([25, 60, 90]),  np.array([95, 255, 255])),
]

print(f"{'Arquivo':<40} {'Escala':>7} {'Área esp.':>9}  " +
      "  ".join(f"{name:>12}" for name, *_ in CANDIDATES))
print("-" * 120)

for row in zoom_out_rows:
    mal_path = DATASET_DIR / "mal_enquadradas" / row["mal_arquivo"]
    if not mal_path.exists():
        print(f"  ⚠  {row['mal_arquivo']} não encontrado")
        continue

    img_bgr = cv2.imread(str(mal_path))
    H, W = img_bgr.shape[:2]
    scale = float(row["parametro"])
    expected_area = scale ** 2      # área proporcional da folha no quadro

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    areas = {}
    masks_to_save = {}
    for name, lower, upper in CANDIDATES:
        raw_mask = cv2.inRange(hsv, lower, upper)
        m = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN,  kernel, iterations=1)
        m = cv2.morphologyEx(m,        cv2.MORPH_CLOSE, kernel, iterations=2)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        if num_labels > 1:
            comp_areas = stats[1:, cv2.CC_STAT_AREA]
            largest_idx = 1 + int(np.argmax(comp_areas))
            roi_px = int(stats[largest_idx, cv2.CC_STAT_AREA])
            frac = roi_px / (H * W)
        else:
            frac = 0.0

        areas[name] = frac

        # Salvar máscara do limiar atual e do V80_S50 para inspeção visual
        if name in ("atual", "V80_S50"):
            component_mask = (labels == largest_idx if num_labels > 1 else np.zeros((H, W))).astype(np.uint8) * 255
            overlay = img_bgr.copy()
            overlay[component_mask == 0] = (overlay[component_mask == 0] * 0.3).astype(np.uint8)
            tag = row['mal_arquivo'].replace('.jpg', '')
            cv2.imwrite(str(DEBUG_DIR / f"{tag}_mask_{name}.png"), overlay)

    area_str = "  ".join(f"{areas[n]:>12.3f}" for n, *_ in CANDIDATES)
    print(f"{row['mal_arquivo']:<40} {scale:>7.3f} {expected_area:>9.3f}  {area_str}")

print(f"\nMáscaras de debug salvas em: {DEBUG_DIR}")
