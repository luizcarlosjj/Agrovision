"""
AgroVision — Documento de Arquitetura (v2, compacto).

Foca em:
  - Arquitetura completa do sistema (app + backend XAI)
  - Attention Leakage (AL) / AFS: estrutura, fluxos e componentes
    (SEM derivações matemáticas detalhadas)

Uso:
    pip install reportlab matplotlib
    python docs/generate_report_v2.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Ellipse

from reportlab.lib.colors import HexColor, black, grey, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, ListFlowable, ListItem,
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ---------------------------------------------------------------------------
ROOT   = Path(__file__).parent
ASSETS = ROOT / "_assets"
ASSETS.mkdir(exist_ok=True)
OUTPUT = ROOT / "AgroVision_Architecture_v2.pdf"

GREEN  = HexColor("#2D7A4F")
PURPLE = HexColor("#5E35B1")
ORANGE = HexColor("#F57C00")
LIGHT  = HexColor("#F5F5F5")
DARK   = HexColor("#212121")
MUTED  = HexColor("#616161")
RED    = HexColor("#C62828")
BLUE   = HexColor("#1565C0")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save(fig, name: str, dpi: int = 160) -> str:
    p = str(ASSETS / name)
    fig.savefig(p, bbox_inches="tight", dpi=dpi, facecolor="white")
    plt.close(fig)
    return p


def _box(ax, x, y, w, h, txt, fc, ec, fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.07", linewidth=1.4,
        edgecolor=ec, facecolor=fc,
    ))
    weight = "bold" if bold else "normal"
    ax.text(x, y, txt, fontsize=fs, ha="center", va="center", fontweight=weight)


def _arrow(ax, x1, y1, x2, y2, label="", color="#424242", lw=1.2, style="->"):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle=style,
        mutation_scale=14, color=color, linewidth=lw,
    ))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.1, my + 0.1, label, fontsize=7, ha="left", color=color)


# ---------------------------------------------------------------------------
# Diagram 1 — System architecture (3 pillars)
# ---------------------------------------------------------------------------

def render_system_arch() -> str:
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 8); ax.axis("off")

    # ── Mobile App pillar ───────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((0.2, 0.4), 4.0, 7.2,
        boxstyle="round,pad=0.2", lw=2, edgecolor="#2D7A4F", facecolor="#E8F5E9"))
    ax.text(2.2, 7.3, "APLICATIVO MOBILE", fontsize=11, fontweight="bold",
            ha="center", color="#1B5E20")
    ax.text(2.2, 6.95, "React Native + Expo", fontsize=8.5, ha="center", color="#388E3C")

    mobile_layers = [
        ("Screens (UI)  |  Navigation", 6.3, "#C8E6C9", "#388E3C"),
        ("Hooks  |  Context (estado)", 5.5, "#C8E6C9", "#388E3C"),
        ("Services: tfliteService", 4.65, "#A5D6A7", "#2D7A4F"),
        ("Services: xaiService", 3.85, "#FFF9C4", "#F57C00"),
        ("Storage: SQLite", 3.05, "#C8E6C9", "#388E3C"),
        ("Models / Utils / Styles", 2.2, "#DCEDC8", "#558B2F"),
        ("assets: model.tflite + labels", 1.3, "#F3E5F5", "#6A1B9A"),
    ]
    for txt, cy, fc, ec in mobile_layers:
        _box(ax, 2.2, cy, 3.4, 0.55, txt, fc, ec, fs=8)

    # ── XAI Backend pillar ──────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((5.0, 1.8), 4.0, 5.8,
        boxstyle="round,pad=0.2", lw=2, edgecolor="#5E35B1", facecolor="#EDE7F6"))
    ax.text(7.0, 7.25, "BACKEND XAI", fontsize=11, fontweight="bold",
            ha="center", color="#311B92")
    ax.text(7.0, 6.9, "Python + FastAPI (Railway)", fontsize=8.5, ha="center", color="#4527A0")

    backend_layers = [
        ("server.py  (FastAPI app)", 6.3, "#D1C4E9", "#4527A0"),
        ("GET /api/health", 5.55, "#EDE7F6", "#7B1FA2"),
        ("POST /api/xai/gradcam", 4.8, "#EDE7F6", "#7B1FA2"),
        ("gradcam.py  (GradientTape)", 4.0, "#D1C4E9", "#4527A0"),
        ("mask.py  (bbox strategies)", 3.2, "#D1C4E9", "#4527A0"),
        ("metrics.py  (AL / AFS)", 2.4, "#B39DDB", "#311B92"),
    ]
    for txt, cy, fc, ec in backend_layers:
        _box(ax, 7.0, cy, 3.4, 0.55, txt, fc, ec, fs=8)

    # ── ML Training pillar ─────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((9.8, 3.0), 2.9, 4.6,
        boxstyle="round,pad=0.2", lw=2, edgecolor="#F57C00", facecolor="#FFF3E0"))
    ax.text(11.25, 7.25, "ML PIPELINE", fontsize=10, fontweight="bold",
            ha="center", color="#E65100")
    ax.text(11.25, 6.95, "(treinamento offline)", fontsize=8, ha="center", color="#F57C00")

    ml_layers = [
        ("prepare_species.py", 6.3, "#FFE0B2", "#E65100"),
        ("train_species.py", 5.6, "#FFE0B2", "#E65100"),
        ("model_species.keras", 4.85, "#EDE7F6", "#5E35B1"),
        ("model_species.tflite", 4.1, "#E8F5E9", "#2D7A4F"),
        ("labels_species.json", 3.35, "#FFF9C4", "#F9A825"),
    ]
    for txt, cy, fc, ec in ml_layers:
        _box(ax, 11.25, cy, 2.5, 0.5, txt, fc, ec, fs=7.5)

    # ── Arrows ──────────────────────────────────────────────────────────────
    # app → backend (XAI request)
    _arrow(ax, 4.2, 3.85, 5.0, 3.5, color="#F57C00", lw=1.5)
    ax.text(4.55, 3.9, "HTTP\nmultipart", fontsize=7, ha="center", color="#E65100")

    # backend → app (AL + heatmap)
    _arrow(ax, 5.0, 3.2, 4.2, 3.4, color="#5E35B1", lw=1.5)
    ax.text(4.55, 3.15, "JSON\n+base64", fontsize=7, ha="center", color="#4527A0")

    # training → backend
    _arrow(ax, 10.0, 4.85, 8.4, 4.85, color="#5E35B1", lw=1.3, style="->")
    ax.text(9.15, 5.0, ".keras", fontsize=7.5, ha="center", color="#5E35B1", style="italic")

    # training → app
    _arrow(ax, 10.0, 4.05, 4.0, 1.3, color="#2D7A4F", lw=1.2, style="->")
    ax.text(7.5, 2.4, ".tflite (embutido)", fontsize=7.5, ha="center",
            color="#2D7A4F", style="italic")

    plt.title("Arquitetura do Sistema AgroVision — Três Pilares",
              fontsize=13, fontweight="bold", pad=14)
    return _save(fig, "arch_v2_system.png")


# ---------------------------------------------------------------------------
# Diagram 2 — Mobile app internal layers
# ---------------------------------------------------------------------------

def render_app_layers() -> str:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7); ax.axis("off")

    layers = [
        # (label, y_center, color_face, color_edge, sublabels)
        ("Camada de Telas (Screens)",
         6.35, "#C8E6C9", "#388E3C",
         "Home · Camera · Processing · Result · History · TestMode"),
        ("Camada de Componentes",
         5.5, "#B2EBF2", "#00838F",
         "Button · Card · HeatmapOverlay · MetricsPanel · LoadingSpinner"),
        ("Camada de Hooks",
         4.65, "#BBDEFB", "#1565C0",
         "useAnalysis · useCamera · useHistory · useTFLiteAnalysis"),
        ("Camada de Contexto (Estado Global)",
         3.8, "#D1C4E9", "#4527A0",
         "AnalysisContext — useReducer (state + dispatch)"),
        ("Camada de Serviços",
         2.95, "#FFE0B2", "#E65100",
         "tfliteService · xaiService · database · analysisService · cameraService"),
        ("Camada de Modelos / Tipos",
         2.1, "#F8BBD9", "#880E4F",
         "Analysis · XAIRequest · XAIResult · XAITestRecord"),
        ("Camada de Armazenamento",
         1.25, "#DCEDC8", "#558B2F",
         "SQLite — analyses + xai_tests    |    AsyncStorage"),
        ("Ativos Estáticos",
         0.5, "#F3E5F5", "#6A1B9A",
         "model_species.tflite  ·  labels_species.json"),
    ]

    for label, cy, fc, ec, sub in layers:
        rect = FancyBboxPatch((0.3, cy - 0.32), 11.4, 0.64,
            boxstyle="round,pad=0.06", lw=1.5, edgecolor=ec, facecolor=fc)
        ax.add_patch(rect)
        ax.text(0.75, cy + 0.05, label, fontsize=9, fontweight="bold",
                va="center", color="#212121")
        ax.text(0.75, cy - 0.15, sub, fontsize=7.5, va="center", color="#424242",
                style="italic")

    # vertical arrows on right side
    for y_top, y_bot in [(6.03, 5.82), (5.18, 4.97), (4.33, 4.12),
                          (3.48, 3.27), (2.63, 2.42), (1.78, 1.57), (0.93, 0.72)]:
        _arrow(ax, 11.3, y_top, 11.3, y_bot, color="#9E9E9E", lw=0.9)

    plt.title("Arquitetura Interna do Aplicativo Mobile — Camadas",
              fontsize=12, fontweight="bold", pad=12)
    return _save(fig, "arch_v2_app_layers.png")


# ---------------------------------------------------------------------------
# Diagram 3 — XAI backend module dependency
# ---------------------------------------------------------------------------

def render_backend_modules() -> str:
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6.5); ax.axis("off")

    nodes = {
        "server.py":       (6.0, 5.8,  3.0, 0.7,  "#D1C4E9", "#4527A0"),
        "model_loader.py": (2.5, 4.2,  3.0, 0.7,  "#B3E5FC", "#0277BD"),
        "gradcam.py":      (6.0, 4.2,  3.0, 0.7,  "#B39DDB", "#4527A0"),
        "mask.py":         (9.5, 4.2,  2.6, 0.7,  "#C8E6C9", "#2D7A4F"),
        "metrics.py":      (4.5, 2.6,  2.8, 0.7,  "#FFE0B2", "#E65100"),
        "overlay.py":      (7.5, 2.6,  2.8, 0.7,  "#F8BBD9", "#880E4F"),
        "model_species.h5":(2.5, 2.6,  3.0, 0.7,  "#DCEDC8", "#558B2F"),
        "Keras model\n(em memória)": (2.5, 1.1, 3.0, 0.7, "#E8F5E9", "#1B5E20"),
        "GradCAMResponse\n(JSON)": (9.5, 1.1, 2.6, 0.8, "#EDE7F6", "#5E35B1"),
    }

    for name, (x, y, w, h, fc, ec) in nodes.items():
        _box(ax, x, y, w, h, name, fc, ec, fs=8.5)

    edges = [
        ("server.py",       "model_loader.py", "carrega ao iniciar"),
        ("server.py",       "gradcam.py",       "chama por req."),
        ("server.py",       "mask.py",          "obtém bbox"),
        ("server.py",       "metrics.py",       "calcula AL/AFS"),
        ("server.py",       "overlay.py",       "gera overlay PNG"),
        ("model_loader.py", "model_species.h5", "lê do disco"),
        ("model_species.h5","Keras model\n(em memória)", "carregado → singleton"),
        ("gradcam.py",      "Keras model\n(em memória)", "usa para grads"),
        ("metrics.py",      "GradCAMResponse\n(JSON)", "al, afs →"),
        ("gradcam.py",      "GradCAMResponse\n(JSON)", "heatmap, pred →"),
    ]

    def center(name):
        x, y, _, _, _, _ = nodes[name]
        return x, y

    skip_label = {"Keras model\n(em memória)", "GradCAMResponse\n(JSON)"}

    for src, dst, lbl in edges:
        x1, y1 = center(src)
        x2, y2 = center(dst)
        # offset slightly so arrows don't overlap text
        dx, dy = x2 - x1, y2 - y1
        dist = (dx**2 + dy**2) ** 0.5
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        hh = nodes[src][3] / 2
        wh = nodes[src][2] / 2
        # start near border of src box, end near border of dst box
        sx = x1 + ux * wh * 0.95
        sy = y1 + uy * hh * 0.95
        ex = x2 - ux * nodes[dst][2] / 2 * 0.95
        ey = y2 - uy * nodes[dst][3] / 2 * 0.95
        ax.add_patch(FancyArrowPatch(
            (sx, sy), (ex, ey), arrowstyle="->",
            mutation_scale=13, color="#616161", linewidth=1.1,
        ))
        if lbl:
            mx, my = (sx + ex) / 2 + 0.05, (sy + ey) / 2 + 0.1
            ax.text(mx, my, lbl, fontsize=6.5, color="#616161", ha="center")

    plt.title("Dependências entre Módulos do Backend XAI",
              fontsize=12, fontweight="bold", pad=12)
    return _save(fig, "arch_v2_backend.png")


# ---------------------------------------------------------------------------
# Diagram 4 — AL/AFS full pipeline (structural, no math)
# ---------------------------------------------------------------------------

def render_al_pipeline() -> str:
    fig, ax = plt.subplots(figsize=(14, 8.5))
    ax.set_xlim(0, 14); ax.set_ylim(-0.5, 8.5); ax.axis("off")

    # ── Top row: Grad-CAM input → heatmap ──────────────────────────────────
    steps_top = [
        ("Imagem original\n(H × W × 3)", 1.1, 6.5, "#E3F2FD", "#1565C0"),
        ("Pré-processamento\n224×224\n+ MobileNetV2\npreprocess", 3.3, 6.5, "#E3F2FD", "#1565C0"),
        ("MobileNetV2\nblocks 1–16\n+Conv_1", 5.5, 6.5, "#FFF3E0", "#E65100"),
        ("Feature Maps Aᵏ\n(7×7×1280)\núltima conv", 7.7, 6.5, "#FFF3E0", "#E65100"),
        ("Gradientes ∂yᶜ/∂Aᵏ\nvia GradientTape\n(pesos αᵏ)", 9.9, 6.5, "#FCE4EC", "#C2185B"),
        ("Heatmap Grad-CAM\nL(x,y)\nnorm. [0,1]", 12.1, 6.5, "#E8F5E9", "#2D7A4F"),
    ]
    for txt, x, y, fc, ec in steps_top:
        _box(ax, x, y, 1.9, 1.3, txt, fc, ec, fs=7.5)
    for i in range(len(steps_top) - 1):
        x1 = steps_top[i][1] + 0.95
        x2 = steps_top[i + 1][1] - 0.95
        _arrow(ax, x1, 6.5, x2, 6.5, color="#424242", lw=1.3)

    # ── Middle row: bbox strategies ─────────────────────────────────────────
    bbox_label_y = 4.8
    ax.text(7.0, 5.15, "Estratégias de Máscara M  (definição da RoI)",
            fontsize=10, fontweight="bold", ha="center", color="#1B5E20")

    strategies = [
        ("fixed\n(bbox central\n80% da imagem)", 2.5, "#E8F5E9", "#2D7A4F"),
        ("green\n(segmentação HSV\nmaior blob verde)", 7.0, "#C8E6C9", "#2D7A4F"),
        ("manual\n(usuário informa\nx,y,w,h)", 11.5, "#A5D6A7", "#1B5E20"),
    ]
    for txt, x, fc, ec in strategies:
        _box(ax, x, bbox_label_y, 3.8, 1.1, txt, fc, ec, fs=8.5)

    # arrow from heatmap down to strategies
    _arrow(ax, 12.1, 5.85, 7.0, 5.3, color="#2D7A4F", lw=1.5)
    ax.text(10.5, 5.55, "heatmap →", fontsize=7.5, color="#2D7A4F", ha="center")

    # ── AL / AFS computation box ────────────────────────────────────────────
    al_box = FancyBboxPatch((3.5, 2.6), 7.0, 1.5,
        boxstyle="round,pad=0.15", lw=2, edgecolor="#E65100", facecolor="#FFF8E1")
    ax.add_patch(al_box)
    ax.text(7.0, 3.85, "Cálculo de AL / AFS  (metrics.py)",
            fontsize=10.5, fontweight="bold", ha="center", color="#BF360C")
    ax.text(7.0, 3.4,
            "threshold τ aplicado no heatmap → heatmap truncado H'(x,y)",
            fontsize=8.5, ha="center", color="#424242", style="italic")
    ax.text(7.0, 3.0,
            "AL = atenção fora de M  /  atenção total          AFS = 1 − AL",
            fontsize=9, ha="center", color="#212121", fontweight="bold")

    # arrows from strategies to AL box
    for x_src in [2.5, 7.0, 11.5]:
        _arrow(ax, x_src, 4.25, 7.0, 4.1, color="#2D7A4F", lw=1.1)

    # ── Output row ──────────────────────────────────────────────────────────
    outputs = [
        ("AL\n[0,1]", 2.8, 1.3, "#FFCCBC", "#BF360C"),
        ("AFS\n[0,1]", 4.8, 1.3, "#C8E6C9", "#1B5E20"),
        ("Overlay PNG\n(JET + bbox)", 6.9, 1.3, "#B3E5FC", "#0277BD"),
        ("Heatmap PNG\n(grayscale)", 9.0, 1.3, "#D1C4E9", "#4527A0"),
        ("Predição +\nConfiança", 11.1, 1.3, "#FFE0B2", "#E65100"),
    ]
    for txt, x, y, fc, ec in outputs:
        _box(ax, x, y, 1.75, 0.85, txt, fc, ec, fs=8)
        _arrow(ax, 7.0, 2.6, x, 1.73, color="#9E9E9E", lw=1.0)

    # ── GradCAMResponse → app ───────────────────────────────────────────────
    resp_box = FancyBboxPatch((2.2, -0.3), 9.6, 0.7,
        boxstyle="round,pad=0.1", lw=1.8, edgecolor="#5E35B1", facecolor="#EDE7F6")
    ax.add_patch(resp_box)
    ax.text(7.0, 0.05,
            "GradCAMResponse (JSON)  →  xaiService.ts  →  TestModeScreen  →  SQLite",
            fontsize=8.5, ha="center", color="#311B92")
    for x_out in [2.8, 4.8, 6.9, 9.0, 11.1]:
        _arrow(ax, x_out, 0.87, 7.0, 0.4, color="#9E9E9E", lw=0.9)

    plt.title("Pipeline Completo do AL / AFS — Estrutura e Fluxo",
              fontsize=13, fontweight="bold", pad=14)
    return _save(fig, "arch_v2_al_pipeline.png")


# ---------------------------------------------------------------------------
# Diagram 5 — End-to-end XAI flow (sequence-style)
# ---------------------------------------------------------------------------

def render_xai_flow() -> str:
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 13); ax.set_ylim(0, 9); ax.axis("off")

    actors = [
        ("Usuário", 1.2, "#E3F2FD", "#1565C0"),
        ("TestMode\nScreen", 3.5, "#C8E6C9", "#2D7A4F"),
        ("xaiService\n.ts", 6.0, "#FFF9C4", "#F57C00"),
        ("server.py\n(FastAPI)", 8.5, "#D1C4E9", "#4527A0"),
        ("gradcam.py\n+ metrics.py", 11.0, "#FCE4EC", "#C2185B"),
    ]
    for label, x, fc, ec in actors:
        _box(ax, x, 8.5, 1.7, 0.7, label, fc, ec, fs=8.5, bold=True)
        ax.plot([x, x], [8.15, 0.3], color=ec, linewidth=0.9, linestyle="--", alpha=0.5)

    def msg(y, x1, x2, txt, color="#424242", dash=False):
        ls = "--" if dash else "-"
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                     arrowprops=dict(arrowstyle="->", color=color, lw=1.3,
                                     linestyle=ls))
        mx = (x1 + x2) / 2
        ax.text(mx, y + 0.12, txt, fontsize=7.8, ha="center", color=color)

    def act(y, x, txt, fc="#FFF9C4", ec="#F57C00"):
        _box(ax, x, y, 2.2, 0.38, txt, fc, ec, fs=7.5)

    act(7.6, 1.2,  "seleciona imagens\n(galeria)", "#E3F2FD", "#1565C0")
    msg(7.1,  1.2,  3.5,  "imageUri[]")
    act(6.65, 3.5,  "verifica health\ndo backend", "#C8E6C9", "#2D7A4F")
    msg(6.2,  3.5,  6.0,  "GET /api/health")
    msg(5.85, 6.0,  8.5,  "GET /api/health", color="#4527A0")
    msg(5.5,  8.5,  6.0,  "200 OK + conv layers", color="#4527A0", dash=True)
    msg(5.15, 6.0,  3.5,  "XAIHealth", dash=True)
    act(4.7,  3.5,  "enfileira runs\n+ chama analyzeWithXAI", "#C8E6C9", "#2D7A4F")
    msg(4.25, 3.5,  6.0,  "XAIRequest (imageUri, bbox_strategy, τ)")
    msg(3.9,  6.0,  8.5,  "POST /api/xai/gradcam (multipart)", color="#4527A0")
    msg(3.55, 8.5,  11.0, "image + params", color="#C2185B")
    act(3.1,  11.0, "Grad-CAM\n+ bbox\n+ AL/AFS", "#FCE4EC", "#C2185B")
    msg(2.65, 11.0, 8.5,  "heatmap, overlay, AL, AFS, pred", color="#C2185B", dash=True)
    msg(2.3,  8.5,  6.0,  "GradCAMResponse (JSON)", color="#4527A0", dash=True)
    msg(1.95, 6.0,  3.5,  "XAIResult (camelCase)", dash=True)
    act(1.55, 3.5,  "renderiza overlay\n+ MetricsPanel\n+ salva SQLite", "#C8E6C9", "#2D7A4F")
    msg(1.1,  3.5,  1.2,  "exibe heatmap + AL + AFS", dash=True)

    plt.title("Fluxo de Interação — Modo Científico XAI (Sequence)",
              fontsize=12, fontweight="bold", pad=14)
    return _save(fig, "arch_v2_xai_flow.png")


# ---------------------------------------------------------------------------
# Diagram 6 — AL bbox strategies visual
# ---------------------------------------------------------------------------

def render_bbox_strategies() -> str:
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    rng = np.random.default_rng(0)
    H, W = 100, 100

    yy, xx = np.mgrid[0:H, 0:W]
    heat_base = np.exp(-((xx - 55)**2 + (yy - 50)**2) / 400)
    heat_base /= heat_base.max()
    # add some background noise
    heat = heat_base + 0.18 * rng.uniform(size=(H, W))
    heat = np.clip(heat / heat.max(), 0, 1)

    # green mask (simulate leaf area)
    green_mask = np.zeros((H, W))
    green_mask[20:80, 18:82] = 1
    green_blob = green_mask.copy()

    configs = [
        ("Estratégia: fixed\n(bbox central 80%)",
         (10, 10, 80, 80), "#00E676"),
        ("Estratégia: green\n(maior blob HSV verde)",
         (18, 20, 64, 60), "#69F0AE"),
        ("Estratégia: manual\n(usuário define x,y,w,h)",
         (30, 25, 40, 50), "#B9F6CA"),
    ]

    for ax, (title, (bx, by, bw, bh), color) in zip(axes, configs):
        ax.imshow(heat, cmap="jet", vmin=0, vmax=1, origin="upper")
        ax.add_patch(plt.Rectangle((bx, by), bw, bh,
            fill=False, edgecolor=color, linewidth=3))
        # shade outside mask
        mask = np.ones((H, W))
        mask[by:by+bh, bx:bx+bw] = 0
        overlay = np.zeros((H, W, 4))
        overlay[..., 3] = mask * 0.35
        ax.imshow(overlay, origin="upper")

        # compute AL/AFS for display
        m = np.zeros((H, W))
        m[by:by+bh, bx:bx+bw] = 1
        h_thresh = np.where(heat >= 0.5, heat, 0)
        ins = (h_thresh * m).sum()
        out = (h_thresh * (1 - m)).sum()
        tot = ins + out
        al = out / tot if tot > 0 else 0
        afs = 1 - al
        ax.set_title(f"{title}\n→ AL = {al:.2f}   AFS = {afs:.2f}", fontsize=8.5)
        ax.axis("off")

    plt.suptitle(
        "Como a Estratégia de Máscara Afeta AL e AFS  "
        "(heatmap idêntico, bbox diferente)",
        fontsize=11, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    return _save(fig, "arch_v2_bbox.png")


# ---------------------------------------------------------------------------
# ReportLab styles
# ---------------------------------------------------------------------------

def _styles():
    base = getSampleStyleSheet()
    S = {}
    def s(name, parent="BodyText", **kw):
        S[name] = ParagraphStyle(name, parent=base[parent], **kw)
    s("Title",   "Title",    fontSize=30, leading=38, textColor=GREEN,
      alignment=TA_CENTER, spaceAfter=12)
    s("Sub",     "Title",    fontSize=16, leading=22, textColor=PURPLE,
      alignment=TA_CENTER, spaceAfter=30)
    s("Author",  "Normal",   fontSize=13, textColor=DARK, alignment=TA_CENTER)
    s("Date",    "Normal",   fontSize=10, textColor=MUTED, alignment=TA_CENTER,
      spaceBefore=30)
    s("H1",      "Heading1", fontSize=18, leading=24, textColor=GREEN,
      spaceBefore=14, spaceAfter=8)
    s("H2",      "Heading2", fontSize=13, leading=18, textColor=PURPLE,
      spaceBefore=10, spaceAfter=5)
    s("H3",      "Heading3", fontSize=11, leading=15, textColor=DARK,
      spaceBefore=8, spaceAfter=3)
    s("Body",    "BodyText", fontSize=10.5, leading=15.5, textColor=DARK,
      alignment=TA_JUSTIFY, spaceAfter=8)
    s("Caption", "Italic",   fontSize=8.5, leading=12, textColor=MUTED,
      alignment=TA_CENTER, spaceAfter=10)
    s("Box",     "BodyText", fontSize=10.5, leading=15, textColor=DARK,
      alignment=TA_JUSTIFY, backColor=HexColor("#FFF8E1"),
      borderPadding=9, borderColor=ORANGE, borderWidth=1, spaceAfter=10)
    s("Code",    "Code",     fontSize=8, leading=10.5, backColor=LIGHT,
      borderPadding=7, leftIndent=6, rightIndent=6, spaceAfter=8)
    return S


def on_page(c, doc):
    c.saveState()
    if doc.page > 1:
        c.setFillColor(MUTED); c.setFont("Helvetica", 8)
        c.drawRightString(A4[0] - 2*cm, 1.2*cm,
                          f"AgroVision · Arquitetura · p. {doc.page}")
        c.setStrokeColor(grey); c.setLineWidth(0.3)
        c.line(2*cm, A4[1]-1.4*cm, A4[0]-2*cm, A4[1]-1.4*cm)
    c.restoreState()


# ---------------------------------------------------------------------------
# Content sections
# ---------------------------------------------------------------------------

def cover(S):
    return [
        Spacer(1, 3*cm),
        Paragraph("AgroVision", S["Title"]),
        Paragraph("Documento de Arquitetura e Attention Leakage (AL)", S["Sub"]),
        Spacer(1, 0.5*cm),
        HRFlowable(width="55%", color=GREEN, thickness=1.2,
                   hAlign="CENTER", spaceBefore=4, spaceAfter=20),
        Paragraph(
            "Arquitetura do sistema, pipeline XAI e métricas originais "
            "<b>Attention Leakage (AL)</b> e <b>Attention Focus Score (AFS)</b>.",
            ParagraphStyle("CoverAbs", fontSize=12, leading=18,
                           textColor=DARK, alignment=TA_CENTER),
        ),
        Spacer(1, 2*cm),
        Paragraph("<b>Autor:</b> Luiz Carlos", S["Author"]),
        Paragraph("Trabalho de Conclusão de Curso — TCC · 2026", S["Date"]),
        PageBreak(),
    ]


def overview(S):
    return [
        Paragraph("1. Visão Geral do Sistema", S["H1"]),
        Paragraph(
            "O AgroVision é um aplicativo mobile <i>offline-first</i> para identificação "
            "de espécies vegetais. A classificação ocorre integralmente no dispositivo, "
            "usando um modelo TFLite embarcado. Quando o pesquisador precisa inspecionar "
            "o comportamento espacial do modelo, um <b>Modo Científico</b> opt-in consulta "
            "um backend Python (FastAPI) que executa Grad-CAM e devolve métricas de atenção.",
            S["Body"],
        ),
        Paragraph(
            "O sistema é composto por três pilares independentes que se articulam em "
            "tempo de execução:",
            S["Body"],
        ),
        ListFlowable([
            ListItem(Paragraph(
                "<b>Aplicativo Mobile</b> — React Native + Expo. Inferência offline via "
                "TFLite, histórico SQLite, UI nativa. Contém o cliente <code>xaiService.ts</code> "
                "que aciona o modo científico.", S["Body"])),
            ListItem(Paragraph(
                "<b>Backend XAI</b> — FastAPI + Python, rodando no Railway. Recebe a imagem "
                "via HTTP multipart, executa Grad-CAM sobre o modelo Keras, computa as métricas "
                "AL/AFS e devolve heatmap e overlay em base64.", S["Body"])),
            ListItem(Paragraph(
                "<b>Pipeline de Treinamento</b> — scripts Python que produzem dois artefatos: "
                "<code>model_species.h5</code> (para o backend) e "
                "<code>model_species.tflite</code> (para o app).", S["Body"])),
        ], bulletType="bullet"),
        Paragraph(
            "<b>Decisão arquitetural central:</b> o TFLite é um runtime de inferência puro — "
            "não expõe gradientes. Grad-CAM exige gradientes. Por isso o modelo Keras "
            "original é mantido como artefato separado e servido pelo backend.",
            S["Box"],
        ),
        PageBreak(),
    ]


def sys_arch_section(S, img_path):
    return [
        Paragraph("2. Arquitetura dos Três Pilares", S["H1"]),
        Image(img_path, width=17*cm, height=10.4*cm),
        Paragraph(
            "<b>Figura 1.</b> Visão macro do sistema. As setas laranja indicam artefatos "
            "produzidos pelo pipeline de treinamento; as setas verde/roxo indicam o "
            "fluxo HTTP entre app e backend durante o Modo Científico.",
            S["Caption"],
        ),
        Paragraph(
            "O backend é stateless por design: o modelo Keras é carregado uma única vez "
            "na inicialização (singleton <code>ModelRegistry</code>) e reutilizado em todas "
            "as requisições subsequentes. Isso elimina latência de I/O por requisição, "
            "relevante dado o tempo de carregamento do modelo (~2 s).",
            S["Body"],
        ),
        PageBreak(),
    ]


def app_arch_section(S, img_path):
    return [
        Paragraph("3. Arquitetura Interna do Aplicativo Mobile", S["H1"]),
        Image(img_path, width=17*cm, height=9.5*cm),
        Paragraph(
            "<b>Figura 2.</b> Camadas internas do aplicativo. A dependência flui de cima "
            "para baixo: Screens dependem de Hooks/Contexto, que dependem de Services, "
            "que dependem de Models e Storage.",
            S["Caption"],
        ),
        Paragraph("3.1. Camadas e responsabilidades", S["H2"]),
        ListFlowable([
            ListItem(Paragraph(
                "<b>Screens:</b> seis telas principais (Home, Camera, Processing, Result, "
                "History) mais <code>TestModeScreen</code> — exclusiva do Modo Científico. "
                "Cada tela é responsável apenas pela composição visual e pelo despacho de "
                "ações ao Contexto.", S["Body"])),
            ListItem(Paragraph(
                "<b>Componentes XAI:</b> <code>HeatmapOverlay</code> (renderiza o PNG "
                "base64 com toggle original/heatmap) e <code>MetricsPanel</code> "
                "(exibe AL, AFS, confiança, estratégia de bbox e layer usada com barra "
                "de progresso colorida).", S["Body"])),
            ListItem(Paragraph(
                "<b>Hooks:</b> encapsulam lógica reutilizável. <code>useTFLiteAnalysis</code> "
                "orquestra o pipeline offline. A <code>TestModeScreen</code> gerencia seu "
                "próprio estado local (runs, labels, export) sem passar pelo Contexto global.",
                S["Body"])),
            ListItem(Paragraph(
                "<b>AnalysisContext:</b> estado global via <code>useReducer</code>. "
                "Contém <code>currentAnalysis</code>, <code>history</code>, "
                "<code>isLoading</code> e <code>error</code>. O Modo Científico "
                "não usa este contexto — opera de forma isolada.", S["Body"])),
            ListItem(Paragraph(
                "<b>Services:</b> <code>tfliteService</code> (inferência offline, "
                "carrega pesos do bundle, redimensiona a 224×224 com jpeg-js, "
                "executa <code>tf.predict</code> no backend CPU) e <code>xaiService</code> "
                "(cliente Axios para o backend XAI, monta FormData com imagem + parâmetros, "
                "converte resposta snake_case → camelCase).", S["Body"])),
            ListItem(Paragraph(
                "<b>SQLite:</b> duas tabelas independentes. <code>analyses</code> armazena "
                "o histórico do fluxo normal. <code>xai_tests</code> armazena todos os "
                "campos do Modo Científico, incluindo o overlay em base64, para inspeção "
                "offline posterior e exportação CSV.", S["Body"])),
        ], bulletType="bullet"),
        PageBreak(),
    ]


def backend_section(S, img_path):
    return [
        Paragraph("4. Arquitetura do Backend XAI", S["H1"]),
        Image(img_path, width=17*cm, height=10*cm),
        Paragraph(
            "<b>Figura 3.</b> Grafo de dependências entre módulos do backend. "
            "O <code>server.py</code> é o ponto de entrada; os módulos XAI são stateless "
            "e recebem o modelo como parâmetro.",
            S["Caption"],
        ),
        Paragraph("4.1. Endpoints", S["H2"]),
        Paragraph(
            "<code>GET /api/health</code> — chamado pelo app ao abrir a TestModeScreen "
            "(timeout 5 s). Retorna <code>status</code>, caminho do modelo, número de classes "
            "e as últimas camadas Conv2D disponíveis. Permite ao usuário confirmar "
            "conectividade e ver quais layers podem ser selecionadas.",
            S["Body"],
        ),
        Paragraph(
            "<code>POST /api/xai/gradcam</code> — endpoint principal. Recebe "
            "<code>multipart/form-data</code> com a imagem e os parâmetros "
            "(<code>bbox_strategy</code>, <code>threshold</code>, <code>coverage</code>, "
            "<code>layer_name</code> opcional). Retorna o <code>GradCAMResponse</code> JSON "
            "com todos os campos de resultado. Timeout no cliente: 60 s.",
            S["Body"],
        ),
        Paragraph("4.2. Startup e singleton do modelo", S["H2"]),
        Paragraph(
            "Ao subir, o servidor executa <code>registry.load()</code>, que localiza o "
            "arquivo do modelo (prioriza <code>model_species.h5</code> sobre "
            "<code>.keras</code>), carrega via <code>tf_keras.models.load_model</code> "
            "com <code>compile=False</code> e indexa todas as camadas Conv2D — incluindo as "
            "aninhadas dentro do sub-modelo MobileNetV2. O modelo fica em memória para toda "
            "a vida útil do processo; cada requisição recebe uma referência ao mesmo objeto.",
            S["Body"],
        ),
        Paragraph("4.3. Módulo <code>gradcam.py</code>", S["H2"]),
        Paragraph(
            "Implementa <code>generate_gradcam</code>. O passo crítico é construir um "
            "modelo auxiliar (<code>_build_grad_model</code>) que, em uma única passagem "
            "<i>forward</i>, expõe tanto os feature maps da camada-alvo quanto a saída "
            "final. Isso é essencial: se os dois tensores fossem computados em passagens "
            "separadas, o <code>tf.GradientTape</code> não encontraria gradiente algum "
            "(retornaria <code>None</code>). "
            "Como o MobileNetV2 é um sub-modelo aninhado, a função detecta este caso e "
            "reconstrói o grafo externo substituindo a chamada ao sub-modelo por um "
            "modelo interno que expõe ambos os tensores.", S["Body"],
        ),
        PageBreak(),
    ]


def al_section(S, pipeline_img, bbox_img, flow_img):
    story = [
        Paragraph("5. Attention Leakage (AL) e Attention Focus Score (AFS)", S["H1"]),
        Paragraph(
            "AL e AFS são as métricas originais propostas neste trabalho. Elas respondem "
            "a uma pergunta que as métricas clássicas de classificação não respondem: "
            "<i>onde o modelo olhou</i> para tomar sua decisão?",
            S["Box"],
        ),
        Paragraph("5.1. Motivação", S["H2"]),
        Paragraph(
            "Acurácia, precisão e F1 descrevem o <i>quê</i> foi predito. São cegas à "
            "distribuição espacial da atenção do modelo. Dois modelos com acurácia idêntica "
            "podem ter comportamentos espaciais opostos: um pode olhar para a folha; outro, "
            "para um artefato de fundo correlacionado com a classe no dataset de treino. "
            "Em aplicações agrícolas de campo — onde iluminação, ângulo e fundo variam "
            "continuamente — um modelo que generaliza <i>espacialmente</i> é mais robusto.",
            S["Body"],
        ),
        Paragraph("5.2. Conceito e estrutura", S["H2"]),
        Paragraph(
            "O cálculo de AL/AFS envolve três elementos estruturais:",
            S["Body"],
        ),
        ListFlowable([
            ListItem(Paragraph(
                "<b>Heatmap Grad-CAM H(x,y)</b> — mapa 2D no intervalo [0,1] que indica, "
                "para cada pixel, o quanto aquela região contribuiu para a decisão do modelo. "
                "Produzido por <code>gradcam.py</code> e redimensionado para a resolução "
                "original da imagem.", S["Body"])),
            ListItem(Paragraph(
                "<b>Máscara M(x,y)</b> — mapa binário que define a Região de Interesse "
                "(RoI): pixels dentro da planta valem 1, fora valem 0. Produzida por "
                "<code>mask.py</code> com uma das três estratégias (ver 5.4).", S["Body"])),
            ListItem(Paragraph(
                "<b>Threshold τ</b> — parâmetro configurável [0,1] (padrão 0.5) que "
                "zera ativações abaixo do limiar antes do cálculo, reduzindo o impacto "
                "de ativações marginais e ruído de fundo do heatmap.", S["Body"])),
        ], bulletType="bullet"),
        Paragraph(
            "Com esses três elementos, <code>metrics.py</code> computa: "
            "<b>AL</b> = fração da atenção acima de τ que caiu <i>fora</i> da máscara M; "
            "<b>AFS</b> = fração que caiu <i>dentro</i> de M. Como são complementares, "
            "AL + AFS = 1 sempre.",
            S["Body"],
        ),
        Paragraph("5.3. Pipeline estrutural de AL/AFS", S["H2"]),
        Image(pipeline_img, width=17*cm, height=9.5*cm),
        Paragraph(
            "<b>Figura 4.</b> Fluxo completo de AL/AFS. O heatmap é produzido pelo Grad-CAM, "
            "a máscara pela estratégia de bbox e ambos confluem em <code>metrics.py</code>. "
            "O resultado é empacotado no <code>GradCAMResponse</code> e enviado ao app.",
            S["Caption"],
        ),
        PageBreak(),
        Paragraph("5.4. Estratégias de máscara e seu impacto em AL", S["H2"]),
        Paragraph(
            "A máscara determina o que se define como 'região correta'. A mesma imagem "
            "com heatmaps idênticos pode produzir valores de AL radicalmente diferentes "
            "dependendo do bbox usado. Três estratégias estão disponíveis:",
            S["Body"],
        ),
        Image(bbox_img, width=17*cm, height=7*cm),
        Paragraph(
            "<b>Figura 5.</b> Mesmo heatmap Grad-CAM sob três estratégias de máscara. "
            "O bbox mais apertado (green/manual) captura melhor a planta real, tornando "
            "AL mais sensível a vazamentos finos.",
            S["Caption"],
        ),
        ListFlowable([
            ListItem(Paragraph(
                "<b>fixed</b> — retângulo central de 80% da imagem. Rápido, "
                "determinístico, sem análise da imagem. Serve de baseline. "
                "Funciona bem para fotos enquadradas pelo usuário.", S["Body"])),
            ListItem(Paragraph(
                "<b>green</b> — segmentação HSV na faixa de verde (matiz 25–95), "
                "seguida de limpeza morfológica (abertura + fechamento) e extração do "
                "maior componente conexo. Se nenhum blob atinge 2% da área, o sistema "
                "recai para <i>fixed</i> automaticamente e reporta o fallback.", S["Body"])),
            ListItem(Paragraph(
                "<b>manual</b> — o usuário informa <code>x,y,w,h</code> diretamente. "
                "Permite análise sobre sub-regiões específicas (ex.: uma única folha "
                "dentro de uma planta maior).", S["Body"])),
        ], bulletType="bullet"),
        Paragraph("5.5. Interpretação dos valores", S["H2"]),
        Paragraph(
            "Os valores de AL/AFS são exibidos no <code>MetricsPanel</code> com uma "
            "barra de progresso colorida (verde ≥ 0.7 · amarelo 0.4–0.7 · vermelho < 0.4):",
            S["Body"],
        ),
        _table_al_interp(S),
        Spacer(1, 0.3*cm),
        Paragraph("5.6. Fluxo de dados: da imagem ao AFS exibido no app", S["H2"]),
        Image(flow_img, width=17*cm, height=10.5*cm),
        Paragraph(
            "<b>Figura 6.</b> Diagrama de sequência do Modo Científico. O fluxo completo "
            "desde a seleção de imagens até a exibição do heatmap e das métricas AL/AFS, "
            "incluindo persistência local e possibilidade de exportação CSV.",
            S["Caption"],
        ),
        PageBreak(),
    ]
    return story


def _table_al_interp(S):
    data = [
        ["AFS", "AL", "Interpretação", "Ação sugerida"],
        ["≥ 0.7", "≤ 0.3", "Atenção bem concentrada na planta",
         "Resultado confiável; enquadramento adequado"],
        ["0.4 – 0.7", "0.3 – 0.6", "Atenção parcialmente vazando",
         "Verificar se há elementos de fundo próximos à planta"],
        ["< 0.4", "≥ 0.6", "Modelo focando fora da planta",
         "Imagem mal enquadrada ou viés no dataset; resultados suspeitos"],
    ]
    t = Table(data, colWidths=[2.0*cm, 2.0*cm, 6.5*cm, 6.0*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
        ("GRID",       (0, 0), (-1, -1), 0.4, grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 1), (-1, 1), HexColor("#E8F5E9")),
        ("BACKGROUND", (0, 2), (-1, 2), HexColor("#FFF9C4")),
        ("BACKGROUND", (0, 3), (-1, 3), HexColor("#FFEBEE")),
    ]))
    return t


def persistence_section(S):
    return [
        Paragraph("6. Persistência e Exportação", S["H1"]),
        Paragraph(
            "Cada execução do Modo Científico é persistida localmente em "
            "<code>xai_tests</code> (SQLite). O esquema armazena os metadados necessários "
            "para análise posterior — inclusive o overlay PNG em base64 — dispensando "
            "re-execução do backend:",
            S["Body"],
        ),
        Paragraph(
            "<font name='Courier' size='8'>"
            "xai_tests: id · imageUri · prediction · confidence<br/>"
            "           al · afs · threshold<br/>"
            "           bboxJson · bboxStrategy<br/>"
            "           overlayB64  (PNG base64 — revisão offline)<br/>"
            "           label  (bem_enquadrada | mal_enquadrada | nao_classificada)<br/>"
            "           createdAt"
            "</font>",
            ParagraphStyle("SchemaCode", fontSize=8, leading=11.5,
                           backColor=LIGHT, borderPadding=8,
                           leftIndent=6, rightIndent=6, spaceAfter=10,
                           fontName="Courier"),
        ),
        Paragraph(
            "A exportação CSV é gerada por <code>utils/csvExport.ts</code> — uma linha por "
            "teste, com todas as colunas exceto o overlay (para manter o arquivo compacto). "
            "O arquivo é escrito no cache do app e aberto no share sheet do sistema "
            "operacional, permitindo análise imediata em planilhas ou Python/Pandas.",
            S["Body"],
        ),
        PageBreak(),
    ]


def stack_table(S):
    data = [
        ["Componente", "Tecnologia principal", "Papel"],
        ["App UI",          "React Native 0.81 + Expo 54", "Runtime iOS/Android + APIs nativas"],
        ["App ML (offline)","react-native-tflite + TF.js CPU","Inferência TFLite no dispositivo"],
        ["App XAI client",  "Axios (xaiService.ts)",         "HTTP multipart → backend XAI"],
        ["App Storage",     "expo-sqlite",                   "analyses + xai_tests + CSV export"],
        ["Backend API",     "FastAPI 0.110 + Uvicorn 0.29",  "Endpoint /api/xai/gradcam"],
        ["Backend ML",      "TensorFlow 2.15 + tf-keras",    "Grad-CAM (GradientTape)"],
        ["Backend CV",      "OpenCV 4.8 + NumPy",            "HSV mask, overlay JET, CLAHE"],
        ["Deploy backend",  "Railway (Docker/Nixpacks)",     "Servidor público via HTTPS"],
    ]
    t = Table(data, colWidths=[3.5*cm, 5.5*cm, 7.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
        ("GRID",       (0, 0), (-1, -1), 0.4, grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    return [
        Paragraph("7. Stack Tecnológica", S["H1"]),
        t,
        Spacer(1, 0.2*cm),
        Paragraph("<b>Tabela 1.</b> Principais tecnologias e seus papéis.", S["Caption"]),
    ]


# ---------------------------------------------------------------------------
# Build PDF
# ---------------------------------------------------------------------------

def build():
    print("[1/6] Renderizando diagramas...")
    img_sys   = render_system_arch()
    img_app   = render_app_layers()
    img_back  = render_backend_modules()
    img_al    = render_al_pipeline()
    img_bbox  = render_bbox_strategies()
    img_flow  = render_xai_flow()
    print("[2/6] Compondo estilos...")
    S = _styles()

    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        title="AgroVision — Arquitetura e AL",
        author="Luiz Carlos",
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
    )

    print("[3/6] Montando conteúdo...")
    story = []
    story += cover(S)
    story += overview(S)
    story += sys_arch_section(S, img_sys)
    story += app_arch_section(S, img_app)
    story += backend_section(S, img_back)
    story += al_section(S, img_al, img_bbox, img_flow)
    story += persistence_section(S)
    story += stack_table(S)

    print("[4/6] Gerando PDF...")
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"[OK] PDF gerado: {OUTPUT}")


if __name__ == "__main__":
    build()
