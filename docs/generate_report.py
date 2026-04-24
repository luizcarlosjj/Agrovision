"""
AgroVision — Scientific Report Generator (TCC-ready PDF).

Produces ``AgroVision_XAI_Report.pdf`` describing the full project
architecture, the Computer Vision model, the training pipeline, and the
scientific extension based on Grad-CAM with the author's original metrics
Attention Leakage (AL) and Attention Focus Score (AFS).

Usage:
    pip install reportlab matplotlib
    python docs/generate_report.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

from reportlab.lib.colors import HexColor, black, grey, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ==========================================================================
# Paths & constants
# ==========================================================================
ROOT = Path(__file__).parent
ASSETS = ROOT / "_assets"
ASSETS.mkdir(exist_ok=True)
OUTPUT = ROOT / "AgroVision_XAI_Report.pdf"

PRIMARY = HexColor("#2D7A4F")
SECONDARY = HexColor("#5E35B1")
ACCENT = HexColor("#F57C00")
LIGHT_BG = HexColor("#F5F5F5")
DARK = HexColor("#212121")
MUTED = HexColor("#616161")
DANGER = HexColor("#C62828")

# ==========================================================================
# Matplotlib helpers
# ==========================================================================


def save_fig(fig, filename: str, dpi: int = 160) -> str:
    path = ASSETS / filename
    fig.savefig(path, bbox_inches="tight", dpi=dpi, facecolor="white")
    plt.close(fig)
    return str(path)


def render_formula(tex: str, filename: str, fs: int = 22, w: float = 8, h: float = 1.2) -> str:
    fig = plt.figure(figsize=(w, h), dpi=200)
    fig.text(0.5, 0.5, tex, fontsize=fs, ha="center", va="center", color="#212121")
    plt.axis("off")
    return save_fig(fig, filename, dpi=200)


def render_architecture() -> str:
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")

    mobile = FancyBboxPatch(
        (0.3, 1), 4.5, 6, boxstyle="round,pad=0.15",
        linewidth=2, edgecolor="#2D7A4F", facecolor="#E8F5E9",
    )
    ax.add_patch(mobile)
    ax.text(2.55, 6.6, "MOBILE APP", fontsize=13, fontweight="bold", ha="center", color="#1B5E20")
    ax.text(2.55, 6.2, "(React Native + Expo)", fontsize=9, ha="center", color="#388E3C")
    for label, y in [
        ("Camera / Image Picker", 5.5),
        ("TFLite Inference (offline)", 4.7),
        ("SQLite (historico)", 3.7),
        ("Modo Cientifico XAI", 2.7),
        ("Biblioteca Agronomica", 1.5),
    ]:
        sub = FancyBboxPatch(
            (0.7, y - 0.25), 3.7, 0.5, boxstyle="round,pad=0.05",
            linewidth=1, edgecolor="#388E3C", facecolor="white",
        )
        ax.add_patch(sub)
        ax.text(2.55, y, label, fontsize=8.5, ha="center", va="center")

    backend = FancyBboxPatch(
        (5.6, 2.5), 4, 4, boxstyle="round,pad=0.15",
        linewidth=2, edgecolor="#5E35B1", facecolor="#EDE7F6",
    )
    ax.add_patch(backend)
    ax.text(7.6, 6.1, "BACKEND XAI", fontsize=13, fontweight="bold", ha="center", color="#311B92")
    ax.text(7.6, 5.75, "(Python + FastAPI)", fontsize=9, ha="center", color="#4527A0")
    for label, y in [
        ("Modelo Keras (MobileNetV2)", 5.0),
        ("Grad-CAM (tf.GradientTape)", 4.1),
        ("Metricas AL / AFS", 3.2),
    ]:
        sub = FancyBboxPatch(
            (6.0, y - 0.3), 3.2, 0.6, boxstyle="round,pad=0.05",
            linewidth=1, edgecolor="#4527A0", facecolor="white",
        )
        ax.add_patch(sub)
        ax.text(7.6, y, label, fontsize=8.5, ha="center", va="center")

    ml = FancyBboxPatch(
        (10.1, 3), 1.8, 3, boxstyle="round,pad=0.1",
        linewidth=2, edgecolor="#F57C00", facecolor="#FFF3E0",
    )
    ax.add_patch(ml)
    ax.text(11, 5.55, "ML Pipeline", fontsize=10, fontweight="bold", ha="center", color="#E65100")
    ax.text(11, 5.2, "(Treinamento)", fontsize=8, ha="center", color="#F57C00")
    ax.text(11, 4.5, "prepare_species\ntrain_species", fontsize=7.5, ha="center")
    ax.text(11, 3.7, "outputs:\n.keras  .tflite", fontsize=7.5, ha="center")

    ax.add_patch(
        FancyArrowPatch((4.8, 2.8), (5.6, 3.6), arrowstyle="->",
                         mutation_scale=20, color="#5E35B1", linewidth=1.5)
    )
    ax.text(5.2, 3.25, "HTTP\nmultipart", fontsize=7, ha="center", color="#5E35B1")

    ax.add_patch(
        FancyArrowPatch((10.1, 5.2), (9.6, 5.1), arrowstyle="->",
                         mutation_scale=16, color="#F57C00", linewidth=1.3)
    )
    ax.add_patch(
        FancyArrowPatch((10.1, 3.8), (4.8, 4.8), arrowstyle="->",
                         mutation_scale=16, color="#F57C00", linewidth=1.3, linestyle="--")
    )
    ax.text(7.3, 4.35, "model_species.tflite", fontsize=7.5, ha="center",
             color="#E65100", style="italic")

    plt.title("Arquitetura Geral do Sistema AgroVision",
               fontsize=14, fontweight="bold", pad=18)
    return save_fig(fig, "architecture.png")


def render_use_case() -> str:
    fig, ax = plt.subplots(figsize=(12, 8.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")

    boundary = FancyBboxPatch(
        (3.4, 0.4), 6.2, 8.1, boxstyle="round,pad=0.1",
        linewidth=2, edgecolor="#424242", facecolor="#FAFAFA", linestyle="--",
    )
    ax.add_patch(boundary)
    ax.text(6.5, 8.3, "AgroVision", fontsize=12, fontweight="bold", ha="center", color="#212121")

    use_cases = [
        ("Capturar imagem\nda planta", 5, 7.3, True),
        ("Identificar especie\n(offline, TFLite)", 5, 6.1, True),
        ("Visualizar historico", 5, 4.9, True),
        ("Consultar biblioteca\nagronomica", 5, 3.7, True),
        ("Ativar Modo\nCientifico (XAI)", 8, 7.3, False),
        ("Analisar atencao\n(Grad-CAM)", 8, 6.1, False),
        ("Rotular enquadramento\n(bem / mal)", 8, 4.9, False),
        ("Exportar resultados\n(CSV)", 8, 3.7, False),
        ("Limpar historico XAI", 8, 2.5, False),
    ]
    for label, x, y, user_flag in use_cases:
        fc = "#E3F2FD" if user_flag else "#EDE7F6"
        ec = "#1976D2" if user_flag else "#5E35B1"
        e = Ellipse((x, y), 2.3, 0.85, facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax.add_patch(e)
        ax.text(x, y, label, fontsize=8, ha="center", va="center", color="#0D47A1" if user_flag else "#311B92")

    def draw_actor(x: float, y: float, label: str, color: str = "black"):
        ax.plot([x, x], [y, y + 0.8], color=color, linewidth=2)
        ax.add_patch(Ellipse((x, y + 1.1), 0.35, 0.35, facecolor="white", edgecolor=color, linewidth=2))
        ax.plot([x - 0.35, x + 0.35], [y + 0.5, y + 0.5], color=color, linewidth=2)
        ax.plot([x, x - 0.3], [y, y - 0.7], color=color, linewidth=2)
        ax.plot([x, x + 0.3], [y, y - 0.7], color=color, linewidth=2)
        ax.text(x, y - 1.1, label, fontsize=8.5, ha="center", fontweight="bold", color=color)

    draw_actor(1.5, 5.2, "Usuario\n(botanico / estudante)", "#1976D2")
    draw_actor(10.9, 5.2, "Pesquisador\n(TCC / modo cientifico)", "#5E35B1")

    for _, x, y, _ in use_cases[:4]:
        ax.plot([1.8, x - 1.15], [5.8, y], color="#1976D2", linewidth=1)
    for _, x, y, _ in use_cases[4:]:
        ax.plot([10.6, x + 1.15], [5.8, y], color="#5E35B1", linewidth=1)

    plt.title("Diagrama de Casos de Uso (UML)",
               fontsize=14, fontweight="bold", pad=15)
    return save_fig(fig, "use_cases.png")


def render_flowchart() -> str:
    fig, ax = plt.subplots(figsize=(11, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 17)
    ax.axis("off")

    def box(x, y, w, h, txt, color="#E3F2FD", edge="#1976D2", fs=8):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                             linewidth=1.4, edgecolor=edge, facecolor=color)
        ax.add_patch(b)
        ax.text(x, y, txt, fontsize=fs, ha="center", va="center")

    def diamond(x, y, w, h, txt, color="#FFF8E1", edge="#F57C00", fs=8):
        pts = np.array([[x, y + h / 2], [x + w / 2, y], [x, y - h / 2], [x - w / 2, y]])
        ax.add_patch(plt.Polygon(pts, facecolor=color, edgecolor=edge, linewidth=1.4))
        ax.text(x, y, txt, fontsize=fs, ha="center", va="center")

    def oval(x, y, w, h, txt, color="#C8E6C9", edge="#388E3C", fs=9):
        ax.add_patch(Ellipse((x, y), w, h, facecolor=color, edgecolor=edge, linewidth=1.5))
        ax.text(x, y, txt, fontsize=fs, ha="center", va="center", fontweight="bold")

    def arrow(x1, y1, x2, y2, label=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->",
                                        mutation_scale=14, color="#424242", linewidth=1.1))
        if label:
            ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2, label,
                     fontsize=7, ha="left", color="#1976D2", fontweight="bold")

    oval(5, 16.3, 2, 0.6, "Inicio")
    arrow(5, 15.95, 5, 15.5)
    box(5, 15.2, 3, 0.55, "Home Screen")
    arrow(5, 14.9, 5, 14.3)
    diamond(5, 13.9, 3, 0.8, "Tipo de analise?")

    # Left: normal path
    arrow(3.5, 13.9, 2, 13.2, label="Normal")
    box(2, 12.8, 2.8, 0.55, "Capturar foto\n(camera / galeria)")
    arrow(2, 12.5, 2, 11.9)
    box(2, 11.6, 2.8, 0.55, "TFLite (offline)")
    arrow(2, 11.3, 2, 10.7)
    box(2, 10.4, 2.8, 0.55, "Mostrar resultado\n(especie + confianca)")
    arrow(2, 10.1, 2, 9.5)
    box(2, 9.2, 2.8, 0.55, "Salvar historico\n(SQLite)")
    arrow(2, 8.9, 2, 8.2)
    box(2, 7.9, 2.8, 0.55, "Fim do fluxo normal", color="#F1F8E9", edge="#388E3C")

    # Right: XAI path
    arrow(6.5, 13.9, 8, 13.2, label="XAI")
    box(8, 12.8, 2.8, 0.55, "Abrir TestModeScreen")
    arrow(8, 12.5, 8, 11.9)
    diamond(8, 11.55, 2.8, 0.75, "Backend online?")
    arrow(7, 11.55, 5.5, 11, label="Nao")
    box(5.5, 10.75, 2.6, 0.5, "Erro + instrucao\nde setup", color="#FFEBEE", edge="#C62828")
    arrow(8, 11.2, 8, 10.6, label="Sim")
    box(8, 10.3, 2.8, 0.55, "Selecionar imagens\n(multi-select)")
    arrow(8, 10, 8, 9.4)
    box(8, 9.1, 2.8, 0.55, "Escolher estrategia bbox\n(fixed / green / manual)")
    arrow(8, 8.8, 8, 8.2)
    box(8, 7.9, 2.8, 0.55, "POST /api/xai/gradcam\n(multipart + params)")
    arrow(8, 7.6, 8, 7.0)
    box(8, 6.7, 2.8, 0.65, "Backend: Grad-CAM\n+ AL/AFS + overlay PNG",
          color="#EDE7F6", edge="#5E35B1")
    arrow(8, 6.35, 8, 5.7)
    box(8, 5.4, 2.8, 0.55, "Render heatmap\n+ MetricsPanel (AFS/AL)")
    arrow(8, 5.1, 8, 4.5)
    box(8, 4.2, 2.8, 0.55, "Rotular enquadramento\n(bem / mal)")
    arrow(8, 3.9, 8, 3.3)
    box(8, 3.0, 2.8, 0.55, "Salvar XAITestRecord\n(SQLite)")
    arrow(8, 2.7, 8, 2.1)
    diamond(8, 1.7, 2.6, 0.7, "Exportar CSV?")
    arrow(8, 1.35, 8, 0.7, label="Sim")
    box(8, 0.4, 2.8, 0.5, "Gera CSV + Share sheet", color="#FFF3E0", edge="#F57C00")
    arrow(8, 0.1, 8, -0.4)
    oval(8, -0.7, 2, 0.6, "Fim")

    plt.title("Fluxograma do Sistema — Fluxo Normal e Modo Cientifico (XAI)",
               fontsize=13, fontweight="bold", pad=15)
    return save_fig(fig, "flowchart.png")


def render_xai_pipeline() -> str:
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.5, 5.5)
    ax.axis("off")

    steps = [
        ("Imagem\n(H x W x 3)", 1, 3, "#E3F2FD", "#1976D2"),
        ("Preproc.\n(resize 224x224,\nmobilenet_v2)", 2.9, 3, "#E3F2FD", "#1976D2"),
        ("MobileNetV2\n(convolucoes)", 4.8, 3, "#FFF3E0", "#F57C00"),
        ("Feature Maps\nA^k  (ultima conv:\nConv_1)", 6.7, 3, "#FFF3E0", "#F57C00"),
        ("Gradientes\ndelta y^c / delta A^k\n(tf.GradientTape)", 8.6, 3, "#FCE4EC", "#C2185B"),
        ("Grad-CAM\nL^c = ReLU( sum alphaK*A^k )", 10.8, 3, "#EDE7F6", "#5E35B1"),
        ("Heatmap\nnormalizado\n[0,1]", 13, 3, "#E8F5E9", "#388E3C"),
    ]
    for label, x, y, fc, ec in steps:
        b = FancyBboxPatch((x - 0.85, y - 0.75), 1.7, 1.5, boxstyle="round,pad=0.1",
                             linewidth=1.5, edgecolor=ec, facecolor=fc)
        ax.add_patch(b)
        ax.text(x, y, label, fontsize=7, ha="center", va="center")
    for i in range(len(steps) - 1):
        x1 = steps[i][1] + 0.85
        x2 = steps[i + 1][1] - 0.85
        ax.add_patch(FancyArrowPatch((x1, 3), (x2, 3), arrowstyle="->",
                                        mutation_scale=14, color="#424242", linewidth=1.1))

    ax.add_patch(FancyArrowPatch((13, 2.25), (10, 1.1), arrowstyle="->",
                                    mutation_scale=16, color="#388E3C", linewidth=1.5))
    al_box = FancyBboxPatch((3.5, 0.2), 7, 1.2, boxstyle="round,pad=0.1",
                              linewidth=2, edgecolor="#388E3C", facecolor="#F1F8E9")
    ax.add_patch(al_box)
    ax.text(7, 1.05, "Calculo de Attention Leakage (AL) e AFS",
             fontsize=10, fontweight="bold", ha="center", color="#1B5E20")
    ax.text(7, 0.55,
             "AL = (ativacoes fora da mascara M) / (ativacao total)    |    AFS = 1 - AL",
             fontsize=8.5, ha="center", style="italic", color="#2E7D32")

    plt.title("Pipeline do Grad-CAM + metricas XAI (AL, AFS)",
               fontsize=13, fontweight="bold", pad=15)
    return save_fig(fig, "xai_pipeline.png")


def render_al_geometric() -> str:
    """Visual geometric explanation of AL/AFS: mask + heatmap overlay."""
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    rng = np.random.default_rng(42)

    H, W = 100, 100
    yy, xx = np.mgrid[0:H, 0:W]

    # Case 1: well-focused
    cx, cy = 50, 50
    heat_good = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / 300)
    heat_good /= heat_good.max()

    # Case 2: leaked
    heat_leak = (
        0.55 * np.exp(-((xx - 20) ** 2 + (yy - 20) ** 2) / 250)
        + 0.45 * np.exp(-((xx - 80) ** 2 + (yy - 80) ** 2) / 250)
    )
    heat_leak /= heat_leak.max()

    mask = np.zeros((H, W))
    mask[25:75, 25:75] = 1

    cases = [
        ("Exemplo 1 — foco correto", heat_good, 0.91),
        ("Exemplo 2 — atencao vazando", heat_leak, 0.28),
    ]

    for ax_, (title, heat, afs_ref) in zip(axes[:2], cases):
        ax_.imshow(heat, cmap="jet", alpha=0.85)
        ax_.imshow(mask, cmap="Greens", alpha=0.25)
        ax_.add_patch(
            plt.Rectangle((25, 25), 50, 50, fill=False, edgecolor="lime", linewidth=2.5)
        )
        active = np.where(heat >= 0.5, heat, 0)
        inside = (active * mask).sum()
        outside = (active * (1 - mask)).sum()
        total = inside + outside
        al = outside / total if total > 0 else 0
        afs = 1 - al
        ax_.set_title(f"{title}\nAL = {al:.2f}   AFS = {afs:.2f}", fontsize=9)
        ax_.axis("off")

    # Legend panel
    axes[2].axis("off")
    axes[2].text(0.02, 0.95, "Legenda:", fontsize=11, fontweight="bold", va="top")
    axes[2].text(0.02, 0.82, "Retangulo verde: mascara M\n(regiao do objeto)", fontsize=9, va="top")
    axes[2].text(0.02, 0.65, "Cor quente (jet): heatmap\ndo Grad-CAM (0..1)", fontsize=9, va="top")
    axes[2].text(0.02, 0.48,
                   "AL alto  =>  modelo foca\nem regiao irrelevante\n(viés ou enquadramento ruim)",
                   fontsize=9, va="top", color="#C62828")
    axes[2].text(0.02, 0.22,
                   "AFS alto  =>  atencao bem\nalinhada com o objeto\n(sinal de generalizacao\nespacial correta)",
                   fontsize=9, va="top", color="#1B5E20")

    plt.suptitle("Interpretacao geometrica: como AL e AFS se comportam",
                   fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    return save_fig(fig, "al_geometric.png")


def render_training_pipeline() -> str:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, txt, color="#E3F2FD", edge="#1976D2", fs=8):
        b = FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.08",
                             linewidth=1.4, edgecolor=edge, facecolor=color)
        ax.add_patch(b)
        ax.text(x, y, txt, fontsize=fs, ha="center", va="center")

    def arrow(x1, y1, x2, y2, label=""):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->",
                                        mutation_scale=14, color="#424242", linewidth=1.1))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.25, label,
                     fontsize=7.5, ha="center", color="#1976D2", fontweight="bold")

    box(1.5, 3.5, 2.2, 0.9, "HuggingFace\nPlantNet 300K\n+ PlantVillage",
         color="#FFF3E0", edge="#F57C00", fs=8)
    arrow(2.6, 3.5, 3.9, 3.5, "prepare\n_species.py")
    box(5, 3.5, 2.2, 0.9, "datasets/\nhf_species/\n(CLAHE + pad)", color="#E3F2FD", edge="#1976D2")
    arrow(6.1, 3.5, 7.4, 3.5, "train\n_species.py")
    box(8.5, 3.5, 2.2, 1, "MobileNetV2\n+ GAP + Dropout\n+ Dense(N)",
         color="#E8F5E9", edge="#2D7A4F", fs=8)
    arrow(9.6, 3.5, 11.0, 3.5, "augment\n+ fit")

    box(12.2, 4.3, 2.4, 0.7, "Fase 1 (20 ep)\nfrozen backbone",
         color="#FFF8E1", edge="#F57C00", fs=7.5)
    box(12.2, 3.4, 2.4, 0.7, "Fase 2 (15 ep)\nfine-tune top 50",
         color="#FFF8E1", edge="#F57C00", fs=7.5)
    box(12.2, 2.5, 2.4, 0.7, "Converter TFLite\n(dyn. range int8)",
         color="#F3E5F5", edge="#8E24AA", fs=7.5)

    arrow(11.0, 4.0, 11.5, 4.3)
    arrow(11.0, 3.4, 11.5, 3.4)
    arrow(11.0, 2.8, 11.5, 2.5)

    box(5, 1.5, 3.2, 0.7, "model_species.keras\n(backend XAI)",
         color="#EDE7F6", edge="#5E35B1", fs=8)
    box(9, 1.5, 3.2, 0.7, "model_species.tflite\n(app mobile)",
         color="#E8F5E9", edge="#2D7A4F", fs=8)

    arrow(8.5, 2.9, 5, 2.0)
    arrow(12.2, 2.1, 9.5, 1.7)

    plt.title("Pipeline de Treinamento — do dataset ao modelo dual (Keras + TFLite)",
               fontsize=13, fontweight="bold", pad=15)
    return save_fig(fig, "training_pipeline.png")


# ==========================================================================
# ReportLab styles
# ==========================================================================


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "CoverTitle": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontSize=34, leading=42,
            textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=18,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle", parent=base["Title"], fontSize=18, leading=24,
            textColor=SECONDARY, alignment=TA_CENTER, spaceAfter=40,
        ),
        "CoverAuthor": ParagraphStyle(
            "CoverAuthor", parent=base["Normal"], fontSize=14, leading=20,
            textColor=DARK, alignment=TA_CENTER,
        ),
        "CoverDate": ParagraphStyle(
            "CoverDate", parent=base["Normal"], fontSize=11, leading=16,
            textColor=MUTED, alignment=TA_CENTER, spaceBefore=40,
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontSize=20, leading=26,
            textColor=PRIMARY, spaceBefore=16, spaceAfter=10,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=15, leading=20,
            textColor=SECONDARY, spaceBefore=12, spaceAfter=6,
        ),
        "H3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontSize=12, leading=16,
            textColor=DARK, spaceBefore=10, spaceAfter=4,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontSize=10.5, leading=15,
            textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        "Quote": ParagraphStyle(
            "Quote", parent=base["BodyText"], fontSize=10, leading=15,
            textColor=MUTED, alignment=TA_JUSTIFY, leftIndent=14, rightIndent=14,
            borderPadding=4, spaceAfter=8, fontName="Helvetica-Oblique",
        ),
        "Code": ParagraphStyle(
            "Code", parent=base["Code"], fontSize=8.5, leading=11,
            textColor=DARK, backColor=LIGHT_BG, borderPadding=8,
            leftIndent=6, rightIndent=6, spaceAfter=10,
        ),
        "Caption": ParagraphStyle(
            "Caption", parent=base["Italic"], fontSize=9, leading=12,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=12,
        ),
        "Highlight": ParagraphStyle(
            "Highlight", parent=base["BodyText"], fontSize=10.5, leading=15,
            textColor=DARK, alignment=TA_JUSTIFY, backColor=HexColor("#FFF8E1"),
            borderPadding=8, borderColor=ACCENT, borderWidth=1, spaceAfter=10,
        ),
    }
    return styles


# ==========================================================================
# Page templates
# ==========================================================================


def on_page(canvas_obj, doc):
    canvas_obj.saveState()
    page_num = doc.page
    canvas_obj.setFillColor(MUTED)
    canvas_obj.setFont("Helvetica", 8)
    if page_num > 1:
        canvas_obj.drawRightString(
            A4[0] - 2 * cm, 1.2 * cm, f"AgroVision · TCC · p. {page_num}"
        )
        canvas_obj.setStrokeColor(grey)
        canvas_obj.setLineWidth(0.3)
        canvas_obj.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    canvas_obj.restoreState()


# ==========================================================================
# Content blocks
# ==========================================================================


def cover_page(styles) -> list:
    story = [
        Spacer(1, 3 * cm),
        Paragraph("🌾 AgroVision", styles["CoverTitle"]),
        Paragraph(
            "Identificação de Espécies Vegetais com Inteligência Artificial Explicável",
            styles["CoverSubtitle"],
        ),
        Spacer(1, 0.6 * cm),
        HRFlowable(width="60%", color=PRIMARY, thickness=1.2,
                    hAlign="CENTER", spaceBefore=6, spaceAfter=22),
        Paragraph(
            "Uma aplicação mobile <i>offline-first</i> com extensão científica baseada em "
            "<b>Grad-CAM</b> e nas métricas originais "
            "<b>Attention Leakage (AL)</b> e <b>Attention Focus Score (AFS)</b>.",
            ParagraphStyle("CoverAbstract", fontSize=12, leading=18,
                            textColor=DARK, alignment=TA_CENTER),
        ),
        Spacer(1, 2.5 * cm),
        Paragraph("<b>Autor:</b> Luiz Carlos", styles["CoverAuthor"]),
        Paragraph("Trabalho de Conclusão de Curso — TCC", styles["CoverAuthor"]),
        Paragraph("2026", styles["CoverDate"]),
        PageBreak(),
    ]
    return story


def abstract_section(styles) -> list:
    return [
        Paragraph("Resumo", styles["H1"]),
        Paragraph(
            "O AgroVision é um aplicativo móvel de identificação de espécies vegetais "
            "desenvolvido em React Native, projetado para operar integralmente sem conexão "
            "com a internet através de um modelo TensorFlow Lite derivado da arquitetura "
            "MobileNetV2. Este trabalho descreve a arquitetura geral do sistema, o pipeline "
            "de visão computacional envolvido e, de forma central, a extensão científica "
            "adicionada ao projeto para avaliar <i>qualitativamente e espacialmente</i> "
            "a atenção do modelo, utilizando o método Grad-CAM (Selvaraju et al., 2017) "
            "em conjunto com duas métricas originais propostas pelo autor: o "
            "<b>Attention Leakage (AL)</b>, que quantifica a fração da atenção que recai "
            "fora da região de interesse, e o <b>Attention Focus Score (AFS)</b>, seu "
            "complemento, que mede o grau de alinhamento espacial do modelo com o objeto "
            "analisado. Diferentemente de métricas tradicionais de classificação — que "
            "reportam apenas o <i>que</i> foi predito — AL e AFS descrevem <i>onde</i> "
            "o modelo olhou, oferecendo uma lente científica complementar, útil para "
            "auditar vieses de enquadramento, validar processos de <i>fine-tuning</i> e "
            "comparar arquiteturas com desempenho classificatório equivalente. A extensão "
            "é implementada como um modo científico opt-in, com um serviço FastAPI que "
            "expõe o modelo Keras original (necessário porque o TFLite não provê "
            "gradientes) e devolve, ao app, o heatmap Grad-CAM, as métricas AL e AFS e "
            "uma sobreposição visual para inspeção.",
            styles["Body"],
        ),
        Paragraph(
            "<b>Palavras-chave:</b> Explainable AI; Grad-CAM; Visão Computacional; "
            "MobileNetV2; Identificação de Espécies; Attention Leakage; React Native; "
            "TensorFlow Lite.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def toc_section(styles) -> list:
    entries = [
        "1. Introdução e motivação",
        "2. Arquitetura geral do sistema",
        "3. Stack tecnológica",
        "4. Estrutura do projeto",
        "5. Modelo de visão computacional",
        "6. Pipeline de treinamento",
        "7. Fundamentação — Explainable AI e Grad-CAM",
        "8. ★ Attention Leakage (AL) e Attention Focus Score (AFS) — contribuição original",
        "9. Estratégias de máscara para o cálculo de AL",
        "10. Arquitetura do modo científico (XAI)",
        "11. Implementação do Grad-CAM sobre o modelo Keras",
        "12. Persistência e exportação de dados",
        "13. Diagrama de casos de uso",
        "14. Fluxograma do sistema",
        "15. Discussão e trabalhos futuros",
        "16. Referências",
    ]
    items = [
        ListItem(Paragraph(entry, styles["Body"]), leftIndent=10, value=i + 1)
        for i, entry in enumerate(entries)
    ]
    return [
        Paragraph("Sumário", styles["H1"]),
        ListFlowable(items, bulletType="1", leftIndent=10),
        PageBreak(),
    ]


def intro_section(styles) -> list:
    return [
        Paragraph("1. Introdução e motivação", styles["H1"]),
        Paragraph(
            "A agricultura moderna, e em particular a chamada <i>agricultura de precisão</i>, "
            "tem absorvido ferramentas de visão computacional em ritmo crescente para tarefas "
            "que vão da identificação taxonômica de espécies cultivadas à detecção de pragas "
            "e doenças foliares. Em um cenário de uso real — o agricultor em campo, o estudante "
            "em aula prática, o botânico em expedição — a conectividade com a internet é "
            "intermitente, o que restringe soluções puramente baseadas em nuvem. O AgroVision "
            "nasce dessa constatação: um aplicativo móvel desenvolvido em React Native com "
            "Expo, cuja identificação de espécies opera <i>integralmente offline</i> através "
            "de um modelo TensorFlow Lite embarcado.",
            styles["Body"],
        ),
        Paragraph(
            "Porém, a acurácia de um modelo classificatório, por mais elevada que seja, "
            "não conta toda a história. Um modelo pode atingir 95% de precisão em um "
            "conjunto de validação <i>e ainda assim</i> estar olhando para as pistas erradas — "
            "um viés de fundo, uma marca d’água, um padrão de iluminação específico do dataset "
            "de origem. A questão científica central que este trabalho aborda é, portanto, "
            "complementar à acurácia:",
            styles["Body"],
        ),
        Paragraph(
            "“Dado que o modelo acertou, <i>onde</i>, espacialmente, ele olhou para tomar "
            "essa decisão? E o quanto dessa atenção está alinhada com o objeto de interesse?”",
            styles["Quote"],
        ),
        Paragraph(
            "Para responder essa pergunta, o AgroVision foi estendido com um <b>Modo "
            "Científico</b> — um canal opt-in, online, que executa o algoritmo Grad-CAM "
            "sobre o modelo Keras original e reporta, além da predição usual, duas métricas "
            "espaciais propostas pelo autor: o <b>Attention Leakage (AL)</b> e o "
            "<b>Attention Focus Score (AFS)</b>. AL e AFS descrevem, em termos geométricos, "
            "a fração da atenção do modelo que está <i>fora</i> e <i>dentro</i> da região "
            "onde se esperaria que o objeto estivesse. Essa lente complementar permite ao "
            "pesquisador auditar comportamento espacial, comparar diferentes estratégias de "
            "treinamento e quantificar o efeito de enquadramento nas fotos fornecidas ao modelo.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def architecture_section(styles) -> list:
    arch_img = render_architecture()
    return [
        Paragraph("2. Arquitetura geral do sistema", styles["H1"]),
        Paragraph(
            "O sistema é composto por três blocos independentes, orquestrados de modo que "
            "o caminho de inferência comum preserve sua característica <i>offline-first</i>, "
            "enquanto a camada de análise científica, por exigir gradientes do modelo, é "
            "fornecida separadamente por um serviço Python local:",
            styles["Body"],
        ),
        Image(arch_img, width=17 * cm, height=10 * cm),
        Paragraph(
            "<b>Figura 1.</b> Arquitetura macro do AgroVision. A linha tracejada indica o "
            "fluxo de artefatos do pipeline de treinamento: o modelo Keras é consumido pelo "
            "backend XAI e, em paralelo, convertido em TFLite para embarque no app.",
            styles["Caption"],
        ),
        Paragraph(
            "Essa decomposição reflete uma decisão arquitetural deliberada: <b>o TFLite, "
            "por construção, é um runtime otimizado para inferência e não expõe gradientes</b>, "
            "o que torna impossível aplicar Grad-CAM diretamente sobre ele. A alternativa "
            "escolhida foi preservar o modelo Keras original como artefato de primeira classe "
            "(salvo no disco durante o treinamento) e disponibilizá-lo ao app através de um "
            "endpoint HTTP. O resultado é uma separação limpa: o usuário comum nunca depende "
            "da rede para fazer uma identificação, enquanto o pesquisador, no modo científico, "
            "conecta-se ao backend para obter o heatmap e as métricas AL/AFS.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def stack_section(styles) -> list:
    data = [
        ["Camada", "Tecnologia", "Versão", "Papel"],
        ["Mobile UI", "React Native", "0.81.5", "Runtime nativo iOS/Android"],
        ["", "Expo", "~54", "Toolchain + OTA + APIs nativas"],
        ["", "TypeScript", "~5.3", "Tipagem estática"],
        ["", "React Navigation", "~6", "Roteamento (tabs + stack)"],
        ["Mobile ML", "react-native-tflite", "0.0.2", "Inferência offline embarcada"],
        ["Mobile Storage", "expo-sqlite", "~15", "Histórico + testes XAI"],
        ["", "expo-file-system", "~17", "Exportação CSV"],
        ["", "expo-sharing", "~12", "Compartilhamento de arquivos"],
        ["Mobile Captura", "expo-camera", "~17", "Captura de foto"],
        ["", "expo-image-picker", "~15", "Seleção múltipla (modo XAI)"],
        ["Backend XAI", "Python", "3.10 / 3.11", "Runtime"],
        ["", "FastAPI", "0.110", "HTTP framework assíncrono"],
        ["", "Uvicorn", "0.29", "ASGI server"],
        ["ML Training", "TensorFlow", "2.15.0", "Treinamento + Keras + TFLite"],
        ["", "OpenCV", "4.8", "CLAHE, HSV mask, overlay"],
        ["", "NumPy / Pillow", "1.26 / 10", "Tensores e I/O de imagem"],
        ["Datasets", "HuggingFace datasets", "2.18", "Streaming PlantNet 300K + PlantVillage"],
    ]
    tbl = Table(data, colWidths=[2.8 * cm, 4.0 * cm, 2.5 * cm, 7.2 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT_BG]),
                ("GRID", (0, 0), (-1, -1), 0.4, grey),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Paragraph("3. Stack tecnológica", styles["H1"]),
        Paragraph(
            "A stack foi escolhida priorizando (i) a capacidade de rodar inferência "
            "pesada em dispositivos modestos, (ii) a facilidade de desenvolvimento e "
            "iteração em um trabalho acadêmico individual e (iii) compatibilidade entre "
            "os binários gerados pelo treinamento TensorFlow e os runtimes mobile.",
            styles["Body"],
        ),
        tbl,
        Spacer(1, 0.3 * cm),
        Paragraph(
            "<b>Tabela 1.</b> Principais dependências do projeto e seus papéis.",
            styles["Caption"],
        ),
        PageBreak(),
    ]


def structure_section(styles) -> list:
    tree = (
        "Luiz/\n"
        "├── Agrovision/                      # Aplicativo mobile (RN + Expo)\n"
        "│   ├── src/\n"
        "│   │   ├── components/\n"
        "│   │   │   ├── ui/                 # Button, Card, LoadingSpinner, ErrorBanner\n"
        "│   │   │   ├── common/             # SafeAreaWrapper, Header\n"
        "│   │   │   └── xai/                # HeatmapOverlay, MetricsPanel     ← NOVO\n"
        "│   │   ├── screens/\n"
        "│   │   │   ├── HomeScreen.tsx\n"
        "│   │   │   ├── CameraScreen.tsx\n"
        "│   │   │   ├── ProcessingScreen.tsx\n"
        "│   │   │   ├── ResultScreen.tsx\n"
        "│   │   │   ├── InstitutionalScreen.tsx\n"
        "│   │   │   └── TestModeScreen.tsx                                    ← NOVO\n"
        "│   │   ├── services/\n"
        "│   │   │   ├── ml/tfliteService.ts     # inferência offline\n"
        "│   │   │   ├── ml/xaiService.ts        # cliente do backend XAI       ← NOVO\n"
        "│   │   │   ├── storage/database.ts     # SQLite (analyses + xai_tests)\n"
        "│   │   │   └── api/client.ts\n"
        "│   │   ├── models/\n"
        "│   │   │   └── xai.ts                  # tipos do modo científico     ← NOVO\n"
        "│   │   ├── utils/csvExport.ts                                        ← NOVO\n"
        "│   │   └── navigation/\n"
        "│   ├── assets/models/\n"
        "│   │   ├── model_species.tflite       # consumido pelo app\n"
        "│   │   └── labels_species.json\n"
        "│   └── docs/generate_report.py         # este gerador\n"
        "│\n"
        "└── agrovision-ml-service/             # Pipeline de ML + backend XAI\n"
        "    ├── prepare_species.py             # baixa datasets HuggingFace\n"
        "    ├── train_species.py               # treina e exporta .keras + .tflite\n"
        "    ├── model_species.keras            # consumido pelo backend        ← NOVO\n"
        "    ├── labels_species.json\n"
        "    ├── requirements.txt\n"
        "    └── api/\n"
        "        ├── server.py                  # FastAPI app                   ← NOVO\n"
        "        └── xai/\n"
        "            ├── model_loader.py\n"
        "            ├── gradcam.py             # tf.GradientTape\n"
        "            ├── mask.py                # fixed / green / manual\n"
        "            ├── metrics.py             # AL e AFS\n"
        "            └── overlay.py             # JET overlay\n"
    )
    return [
        Paragraph("4. Estrutura do projeto", styles["H1"]),
        Paragraph(
            "O repositório se organiza em dois diretórios paralelos, refletindo a separação "
            "arquitetural descrita na seção anterior. Itens marcados como <i>NOVO</i> foram "
            "introduzidos pela extensão XAI descrita neste documento.",
            styles["Body"],
        ),
        Paragraph(
            f"<font name='Courier' size='7.5'>{tree.replace('<', '&lt;').replace('>', '&gt;').replace(chr(10), '<br/>')}</font>",
            ParagraphStyle("Tree", fontSize=7.5, leading=10.5,
                            textColor=DARK, backColor=LIGHT_BG, borderPadding=8,
                            leftIndent=4, rightIndent=4, spaceAfter=10),
        ),
        PageBreak(),
    ]


def model_section(styles) -> list:
    return [
        Paragraph("5. Modelo de visão computacional", styles["H1"]),
        Paragraph(
            "O classificador de espécies é construído sobre a arquitetura <b>MobileNetV2</b> "
            "(Sandler et al., 2018), escolhida por três razões convergentes: (i) seu compromisso "
            "favorável entre acurácia e custo computacional, viabilizando execução no dispositivo "
            "móvel sem GPU; (ii) a existência de pesos pré-treinados em ImageNet, permitindo "
            "<i>transfer learning</i> com um conjunto de dados botânico de escala moderada; e "
            "(iii) seu bloco final contendo convoluções 2D seguidas de <i>global average pooling</i>, "
            "topologia que se presta naturalmente ao Grad-CAM.",
            styles["Body"],
        ),
        Paragraph("5.1. Topologia", styles["H2"]),
        Paragraph(
            "A cabeça classificatória adicionada sobre o <i>backbone</i> é minimalista:",
            styles["Body"],
        ),
        Paragraph(
            "<font name='Courier' size='8.5'>"
            "Input (224x224x3) → preprocess_input → MobileNetV2 (frozen / unfrozen) "
            "→ GlobalAveragePooling2D → Dropout(0.5) → Dense(N_classes, softmax)"
            "</font>",
            styles["Code"],
        ),
        Paragraph("5.2. Pré-processamento (CLAHE)", styles["H2"]),
        Paragraph(
            "Durante a preparação do dataset, cada imagem é submetida ao filtro "
            "<b>CLAHE</b> (Contrast Limited Adaptive Histogram Equalization, Zuiderveld, 1994), "
            "que realça estruturas foliares sem amplificar ruído, e em seguida recebe "
            "<i>padding</i> proporcional para alcançar a geometria 224×224 sem deformação. "
            "Esse tratamento reduz a variância causada por diferenças de iluminação entre "
            "as fontes de imagens (PlantNet 300K e PlantVillage).",
            styles["Body"],
        ),
        Paragraph("5.3. Data augmentation", styles["H2"]),
        Paragraph(
            "Transformações estocásticas são aplicadas <i>somente</i> durante o treino, "
            "em um <code>tf.data.Dataset</code> à parte — nunca embutidas no modelo. "
            "Isso garante um grafo limpo e determinístico no momento da conversão para "
            "TFLite. As transformações incluem <i>flip horizontal/vertical</i>, rotação "
            "aleatória (±25%), zoom, translação, variação de brilho e contraste.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def training_section(styles) -> list:
    pipe_img = render_training_pipeline()
    return [
        Paragraph("6. Pipeline de treinamento", styles["H1"]),
        Image(pipe_img, width=17 * cm, height=7.2 * cm),
        Paragraph(
            "<b>Figura 2.</b> Pipeline de treinamento — do download dos <i>datasets</i> "
            "HuggingFace até os dois artefatos finais: <i>model_species.keras</i> (para o "
            "backend XAI) e <i>model_species.tflite</i> (para o app).",
            styles["Caption"],
        ),
        Paragraph("6.1. Treinamento em duas fases", styles["H2"]),
        Paragraph(
            "O script <code>train_species.py</code> executa o treinamento em duas fases "
            "sequenciais, prática consolidada em <i>transfer learning</i> com redes "
            "pré-treinadas:",
            styles["Body"],
        ),
        ListFlowable(
            [
                ListItem(Paragraph(
                    "<b>Fase 1 — <i>feature extraction</i>:</b> o <i>backbone</i> "
                    "MobileNetV2 é congelado e apenas o cabeçalho densa é treinada "
                    "(20 épocas, <i>learning rate</i> = 10⁻³). Essa fase é barata "
                    "computacionalmente e adapta rapidamente o espaço latente pré-existente "
                    "ao domínio botânico.", styles["Body"])),
                ListItem(Paragraph(
                    "<b>Fase 2 — <i>fine-tuning</i>:</b> as 50 últimas camadas do "
                    "<i>backbone</i> são descongeladas e o treino continua com "
                    "<i>learning rate</i> reduzido (10⁻⁴) por mais 15 épocas, permitindo "
                    "que as convoluções tardias se especializem em padrões foliares "
                    "específicos do dataset.", styles["Body"])),
            ],
            bulletType="bullet",
        ),
        Paragraph("6.2. Conversão para TFLite", styles["H2"]),
        Paragraph(
            "Concluído o treinamento, o modelo Keras é convertido para TFLite com "
            "<code>Optimize.DEFAULT</code>, o que habilita <i>dynamic range quantization</i> — "
            "pesos são armazenados em int8 com fator de escala, enquanto as ativações "
            "permanecem em float32. Essa combinação gera um artefato compacto "
            "(~10 MB para ~150 classes) com perda de acurácia tipicamente inferior a 1 ponto "
            "percentual, adequada ao runtime móvel.",
            styles["Body"],
        ),
        Paragraph(
            "Uma contribuição recente a este pipeline foi a inclusão explícita da instrução "
            "<code>model.save('model_species.keras')</code> imediatamente antes da conversão "
            "— passo necessário para viabilizar o backend XAI, que exige o modelo Keras completo "
            "para computar gradientes.",
            styles["Highlight"],
        ),
        PageBreak(),
    ]


def xai_theory_section(styles) -> list:
    img = render_xai_pipeline()

    cam_formula = render_formula(
        r"$\alpha_k^c \, = \, \frac{1}{Z} \sum_{i}\sum_{j} \frac{\partial y^c}{\partial A_{ij}^k}$",
        "alpha_formula.png", fs=24,
    )
    cam_map = render_formula(
        r"$L^c_{\mathrm{GradCAM}}(x,y) \, = \, \mathrm{ReLU}\left(\sum_{k} \alpha_k^c \, A^k(x,y)\right)$",
        "cam_map.png", fs=22,
    )
    return [
        Paragraph("7. Fundamentação — Explainable AI e Grad-CAM", styles["H1"]),
        Paragraph(
            "<i>Explainable AI</i> (XAI) é a subárea da aprendizagem de máquina que busca "
            "tornar as decisões de modelos — especialmente redes neurais profundas — "
            "inteligíveis a seres humanos. Entre os métodos mais influentes para explicar "
            "redes convolucionais de classificação de imagens está o <b>Grad-CAM</b> "
            "(Gradient-weighted Class Activation Mapping), introduzido por "
            "Selvaraju et al. (2017). Grad-CAM produz, para uma imagem de entrada e uma "
            "classe-alvo <i>c</i>, um mapa 2D do tamanho do último bloco convolucional que "
            "indica quais regiões da imagem mais contribuíram para a decisão do modelo.",
            styles["Body"],
        ),
        Paragraph("7.1. Formulação matemática", styles["H2"]),
        Paragraph(
            "Seja <i>A<sup>k</sup></i> o <i>k</i>-ésimo mapa de ativação (<i>feature map</i>) "
            "da última camada convolucional de uma rede, e <i>y<sup>c</sup></i> o <i>score</i> "
            "(ou probabilidade pré-softmax) da classe <i>c</i>. Define-se o peso de "
            "importância do canal <i>k</i> como o valor médio das derivadas parciais de "
            "<i>y<sup>c</sup></i> em relação a cada elemento de <i>A<sup>k</sup></i>:",
            styles["Body"],
        ),
        Image(cam_formula, width=11 * cm, height=1.8 * cm, hAlign="CENTER"),
        Paragraph(
            "onde <i>Z</i> é o número total de posições (H·W) em <i>A<sup>k</sup></i>. "
            "O mapa de ativação de classe Grad-CAM é então obtido pela combinação linear "
            "dos mapas de ativação, ponderados pelos coeficientes calculados, seguida de "
            "um <i>rectifier</i>:",
            styles["Body"],
        ),
        Image(cam_map, width=14 * cm, height=1.7 * cm, hAlign="CENTER"),
        Paragraph(
            "A operação ReLU descarta contribuições negativas — regiões que <i>reduzem</i> "
            "a pontuação da classe-alvo — mantendo apenas o sinal positivo, i.e., as regiões "
            "que <i>suportam</i> a decisão. Posteriormente, o heatmap é normalizado para "
            "o intervalo [0, 1] e redimensionado para a resolução da imagem original, o que "
            "permite sobrepô-lo visualmente à foto para inspeção.",
            styles["Body"],
        ),
        Paragraph("7.2. Por que Grad-CAM é adequado ao AgroVision", styles["H2"]),
        Paragraph(
            "MobileNetV2 termina com uma convolução <i>pointwise</i> (tipicamente "
            "chamada <code>Conv_1</code>) seguida de <i>global average pooling</i> e da camada "
            "densa classificatória. Essa topologia é <i>exatamente</i> o cenário em que "
            "Grad-CAM foi formulado — a GAP garante que os gradientes propagados até "
            "<code>Conv_1</code> sejam representativos das contribuições espaciais, e a "
            "última camada convolucional carrega a granularidade visual suficiente (7×7 para "
            "entradas 224×224) para produzir mapas de atenção interpretáveis.",
            styles["Body"],
        ),
        Image(img, width=17 * cm, height=7.8 * cm),
        Paragraph(
            "<b>Figura 3.</b> Pipeline do Grad-CAM integrado ao AgroVision. A saída "
            "(heatmap normalizado) alimenta o cálculo das métricas AL e AFS descritas na seção 8.",
            styles["Caption"],
        ),
        PageBreak(),
    ]


def al_afs_section(styles) -> list:
    al_formula = render_formula(
        r"$AL \, = \, \frac{\sum_{(x,y)\, \mathrm{fora\, de\, } M}\, H'(x,y)}"
        r"{\sum_{(x,y)}\, H'(x,y)}$",
        "al_formula.png", fs=22, w=10, h=2,
    )
    afs_formula = render_formula(
        r"$AFS \, = \, 1 \, - \, AL$", "afs_formula.png", fs=26, w=5, h=1.2
    )
    h_formula = render_formula(
        r"$H'(x,y) \, = \, H(x,y) \;\; \mathrm{se}\;\; H(x,y) \geq \tau,\;\;"
        r" \mathrm{sen{\~a}o}\;\; 0$",
        "h_formula.png", fs=18, w=10, h=1.5,
    )
    geo = render_al_geometric()
    return [
        Paragraph(
            "8. Attention Leakage (AL) e Attention Focus Score (AFS)",
            styles["H1"],
        ),
        Paragraph(
            "<b>Esta é a contribuição original deste trabalho.</b> Grad-CAM responde "
            "<i>onde</i> o modelo olhou, mas por si só não quantifica o quanto essa atenção "
            "está <i>correta</i> do ponto de vista espacial. Propõe-se, portanto, um par "
            "de métricas complementares que <b>reduzem o heatmap Grad-CAM a dois escalares "
            "interpretáveis</b>, permitindo comparações objetivas entre imagens, modelos "
            "ou estratégias de treinamento.",
            styles["Highlight"],
        ),
        Paragraph("8.1. Motivação", styles["H2"]),
        Paragraph(
            "Métricas tradicionais de classificação — acurácia, precisão, F1, matriz de "
            "confusão — operam sobre a saída escalar do modelo e descrevem <i>o que</i> foi "
            "predito. Elas são cegas ao <i>onde</i>: dois modelos com a mesma acurácia podem "
            "ter comportamentos espaciais radicalmente diferentes. Um poderia olhar "
            "majoritariamente para a planta; outro poderia acertar por correlação com o fundo, "
            "um padrão de iluminação ou uma assinatura do dataset de origem. No contexto "
            "agrícola essa distinção é operacionalmente relevante — um modelo que generaliza "
            "espacialmente bem tende a ser mais robusto a enquadramentos de campo, mudanças "
            "de iluminação e diferentes dispositivos de captura.",
            styles["Body"],
        ),
        Paragraph("8.2. Definições formais", styles["H2"]),
        Paragraph(
            "Seja <i>H(x,y) ∈ [0, 1]</i> o heatmap Grad-CAM normalizado, avaliado em cada "
            "pixel (<i>x,y</i>) da imagem original de dimensões <i>(W × H)</i>. Seja "
            "<i>M(x,y) ∈ {0, 1}</i> uma máscara binária que delimita a região de interesse "
            "(RoI) — tipicamente, o <i>bounding box</i> da planta alvo da análise.",
            styles["Body"],
        ),
        Paragraph(
            "Introduz-se um <i>threshold</i> τ ∈ [0, 1] que elimina ativações marginais, "
            "consideradas ruído, produzindo o heatmap truncado <i>H'(x,y)</i>:",
            styles["Body"],
        ),
        Image(h_formula, width=11 * cm, height=2 * cm, hAlign="CENTER"),
        Paragraph(
            "Define-se então o <b>Attention Leakage</b> como a fração da atenção pós-threshold "
            "que recai <i>fora</i> da máscara:",
            styles["Body"],
        ),
        Image(al_formula, width=10 * cm, height=2.4 * cm, hAlign="CENTER"),
        Paragraph(
            "e, simetricamente, o <b>Attention Focus Score</b> como seu complemento:",
            styles["Body"],
        ),
        Image(afs_formula, width=7 * cm, height=1.4 * cm, hAlign="CENTER"),
        Paragraph("8.3. Propriedades matemáticas", styles["H2"]),
        ListFlowable(
            [
                ListItem(Paragraph(
                    "<b>Complementaridade:</b> por construção, <i>AL + AFS = 1</i> em "
                    "qualquer imagem. AFS é, portanto, redundante do ponto de vista "
                    "informacional, mas sua leitura é mais natural (quanto maior, melhor).",
                    styles["Body"])),
                ListItem(Paragraph(
                    "<b>Domínio:</b> <i>AL, AFS ∈ [0, 1]</i>. Valores intermediários admitem "
                    "leitura percentual direta.", styles["Body"])),
                ListItem(Paragraph(
                    "<b>Invariância a escala linear:</b> como AL é uma razão, multiplicar "
                    "todo o heatmap por uma constante positiva não altera o valor — o que "
                    "é desejável dado que Grad-CAM já normaliza para [0, 1] mas diferenças "
                    "de magnitude entre amostras deveriam ser irrelevantes para comparações.",
                    styles["Body"])),
                ListItem(Paragraph(
                    "<b>Caso degenerado:</b> se <i>H'(x,y) = 0</i> em toda a imagem — "
                    "situação possível quando o modelo não ativa acima do threshold — "
                    "define-se, por convenção, <i>AL = 0</i> e <i>AFS = 1</i>, "
                    "evitando divisão por zero.", styles["Body"])),
                ListItem(Paragraph(
                    "<b>Sensibilidade a τ:</b> thresholds baixos (τ → 0) consideram "
                    "quase toda a ativação e aumentam o ruído em regiões irrelevantes; "
                    "thresholds altos (τ → 1) concentram a avaliação nos picos, tornando "
                    "a métrica mais robusta mas potencialmente subsensível. τ = 0.5 é "
                    "adotado como <i>default</i> por produzir bom equilíbrio empiricamente.",
                    styles["Body"])),
            ],
            bulletType="bullet",
        ),
        Paragraph("8.4. Interpretação qualitativa", styles["H2"]),
        Paragraph(
            "Um <i>AFS</i> próximo de 1 indica que o modelo concentrou sua atenção "
            "dentro da região esperada — seja porque o enquadramento da foto era adequado, "
            "seja porque o modelo aprendeu a isolar a planta. Valores intermediários "
            "(0.4 ≤ AFS &lt; 0.7) sugerem que parte relevante da atenção vazou para o fundo, "
            "o que pode ser aceitável em cenários com plantas pequenas em cenas amplas, mas "
            "alerta para possível viés ao ser cruzado com erros de predição. Valores baixos "
            "(AFS &lt; 0.4) sinalizam que o modelo tomou a decisão por pistas contextuais, "
            "não pelo objeto — um padrão especialmente perigoso em datasets com viés sistemático.",
            styles["Body"],
        ),
        Image(geo, width=17 * cm, height=5.8 * cm),
        Paragraph(
            "<b>Figura 4.</b> Interpretação geométrica das métricas. À esquerda, um heatmap "
            "bem concentrado na região objeto (quadrado verde) resulta em <i>AFS</i> elevado. "
            "Ao centro, dois focos de ativação fora da máscara produzem <i>AL</i> alto.",
            styles["Caption"],
        ),
        Paragraph("8.5. Casos de uso científicos", styles["H2"]),
        ListFlowable(
            [
                ListItem(Paragraph(
                    "<b>Auditoria de viés:</b> comparar AFS médio em subconjuntos "
                    "do dataset onde a planta ocupa diferentes porções do quadro. Se o AFS "
                    "cai acentuadamente em imagens com planta pequena, há indício de "
                    "dependência do modelo em pistas de fundo.",
                    styles["Body"])),
                ListItem(Paragraph(
                    "<b>Validação de <i>fine-tuning</i>:</b> espera-se que, ao refinar o "
                    "modelo com dados mais representativos da condição de campo, o AFS "
                    "médio aumente — indicando que o modelo passou a localizar melhor "
                    "o objeto, mesmo que a acurácia global já estivesse saturada.",
                    styles["Body"])),
                ListItem(Paragraph(
                    "<b>Comparação entre arquiteturas:</b> duas redes com acurácia "
                    "equivalente podem ter AFS distintos. A de maior AFS tende a ser "
                    "preferível operacionalmente, por sua robustez espacial.",
                    styles["Body"])),
                ListItem(Paragraph(
                    "<b>Enquadramento no app:</b> comparar AFS em imagens tiradas pelo "
                    "usuário final (bem e mal enquadradas) permite decidir se vale "
                    "introduzir um guia visual de captura, reduzindo erros em produção.",
                    styles["Body"])),
            ],
            bulletType="bullet",
        ),
        PageBreak(),
    ]


def mask_section(styles) -> list:
    return [
        Paragraph("9. Estratégias de máscara para o cálculo de AL", styles["H1"]),
        Paragraph(
            "A máscara <i>M</i> define o que se entende por “região do objeto” e é, portanto, "
            "determinante para a interpretação de AL/AFS. Três estratégias são oferecidas "
            "pelo backend e selecionáveis pela interface:",
            styles["Body"],
        ),
        Paragraph("9.1. Bbox central fixo (<i>fixed</i>)", styles["H2"]),
        Paragraph(
            "Um retângulo centralizado cobrindo 80% da imagem em cada dimensão. É a "
            "estratégia mais simples e serve como <i>baseline</i>. Em imagens "
            "razoavelmente enquadradas — situação típica quando o próprio usuário captura "
            "a planta no centro — a cobertura de 80% tende a envolver o objeto sem incluir "
            "muito fundo. Essa estratégia é rápida e determinística.",
            styles["Body"],
        ),
        Paragraph("9.2. Segmentação por verde (<i>green</i>)", styles["H2"]),
        Paragraph(
            "Imagem é convertida para HSV e limiarizada em uma faixa ampla de verde "
            "(matiz 25–95), cobrindo folhagem de tons variados. A máscara é limpa por "
            "operações morfológicas (abertura + fechamento com <i>kernel</i> elíptico "
            "5×5) e o maior componente conexo é extraído como bounding box do objeto. "
            "Se nenhum componente atinge 2% da área da imagem, o sistema recua "
            "graciosamente para a estratégia <i>fixed</i>, reportando o fallback na "
            "resposta HTTP. Essa heurística é adequada para fotos com planta razoavelmente "
            "isolada e é muito mais precisa do que a estratégia fixa para compor a RoI.",
            styles["Body"],
        ),
        Paragraph("9.3. Manual", styles["H2"]),
        Paragraph(
            "O usuário fornece um bbox no formato <code>x,y,w,h</code>. Essa estratégia "
            "é útil quando se deseja avaliar AL sobre uma sub-região específica — por "
            "exemplo, uma única folha dentro de uma planta maior.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def arch_xai_section(styles) -> list:
    return [
        Paragraph("10. Arquitetura do modo científico (XAI)", styles["H1"]),
        Paragraph(
            "O modo científico é acessado a partir de um cartão dedicado na tela principal "
            "do app. Ao abrir a tela <code>TestModeScreen</code>, o app faz uma verificação "
            "de saúde contra o endpoint <code>GET /api/health</code> — se o backend não "
            "responde, exibe instruções de setup. Em seguida, o usuário pode:",
            styles["Body"],
        ),
        ListFlowable(
            [
                ListItem(Paragraph(
                    "Selecionar uma ou várias imagens da galeria (multi-seleção, até 20 "
                    "por lote).", styles["Body"])),
                ListItem(Paragraph(
                    "Escolher a estratégia de máscara (<i>fixed</i> ou <i>green</i>) e o "
                    "<i>threshold</i> τ (valores pré-definidos: 0.3, 0.5, 0.7).",
                    styles["Body"])),
                ListItem(Paragraph(
                    "Executar o processamento — cada imagem é enviada via HTTP <i>multipart</i> "
                    "para <code>POST /api/xai/gradcam</code>. O backend retorna predição, "
                    "confiança, AL, AFS, a bbox efetivamente usada e a imagem com o overlay "
                    "Grad-CAM codificada em <i>base64</i>.", styles["Body"])),
                ListItem(Paragraph(
                    "Rotular manualmente o enquadramento de cada imagem como "
                    "<i>bem_enquadrada</i>, <i>mal_enquadrada</i> ou <i>nao_classificada</i>. "
                    "Esse rótulo é opcional e serve para análise estatística posterior.",
                    styles["Body"])),
                ListItem(Paragraph(
                    "Exportar o histórico completo em CSV — o arquivo é gerado localmente "
                    "no cache do app e aberto no <i>share sheet</i> do sistema operacional.",
                    styles["Body"])),
            ],
            bulletType="bullet",
        ),
        Paragraph(
            "Todos os resultados são persistidos em uma tabela SQLite independente "
            "(<code>xai_tests</code>), preservando o histórico entre sessões sem interferir "
            "no histórico do fluxo normal de identificação.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def implementation_section(styles) -> list:
    snippet = (
        "with tf.GradientTape() as tape:\n"
        "    feature_maps, predictions = grad_model(input_tensor, training=False)\n"
        "    class_index = int(tf.argmax(predictions[0]).numpy())\n"
        "    class_score = predictions[:, class_index]\n"
        "\n"
        "grads = tape.gradient(class_score, feature_maps)\n"
        "pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))  # alpha_k^c\n"
        "\n"
        "cam = tf.reduce_sum(feature_maps[0] * pooled_grads, axis=-1)\n"
        "cam = tf.nn.relu(cam)            # mantem so contribuicoes positivas\n"
        "cam = cam / (tf.reduce_max(cam) + 1e-8)   # normaliza para [0,1]\n"
        "cam = tf.image.resize(cam[..., None], (H, W)).numpy().squeeze(-1)\n"
    )
    al_snip = (
        "active = np.where(heatmap >= threshold, heatmap, 0.0)\n"
        "inside  = float((active * mask).sum())\n"
        "outside = float((active * (1.0 - mask)).sum())\n"
        "total   = inside + outside\n"
        "\n"
        "al  = outside / total if total > 0 else 0.0\n"
        "afs = 1.0 - al\n"
    )
    return [
        Paragraph(
            "11. Implementação do Grad-CAM sobre o modelo Keras", styles["H1"]
        ),
        Paragraph(
            "O núcleo do Grad-CAM reside em duas operações: acessar os <i>feature maps</i> "
            "da última camada convolucional e obter os gradientes da pontuação da classe-alvo "
            "em relação a esses mapas. Ambas exigem o modelo Keras íntegro, o que só é "
            "possível graças ao artefato <code>model_species.keras</code> salvo durante o "
            "treinamento. O TensorFlow expõe essa capacidade através do mecanismo "
            "<code>tf.GradientTape</code>:",
            styles["Body"],
        ),
        Paragraph(
            f"<font name='Courier' size='8'>{snippet.replace(chr(10), '<br/>')}</font>",
            styles["Code"],
        ),
        Paragraph(
            "Uma complicação prática surge do fato de o <i>backbone</i> MobileNetV2 estar "
            "embutido como sub-modelo dentro do modelo de classificação. O método "
            "<code>_build_grad_model</code> localiza recursivamente a camada convolucional "
            "alvo (tipicamente <code>Conv_1</code>), reconstrói o grafo de maneira a expor "
            "tanto os <i>feature maps</i> quanto a saída final do modelo em um único passe "
            "<i>forward</i>, e devolve esse modelo auxiliar ao algoritmo principal.",
            styles["Body"],
        ),
        Paragraph(
            "Para o cálculo de AL/AFS, a implementação é deliberadamente direta:",
            styles["Body"],
        ),
        Paragraph(
            f"<font name='Courier' size='8'>{al_snip.replace(chr(10), '<br/>')}</font>",
            styles["Code"],
        ),
        Paragraph(
            "O <i>threshold</i> é aplicado por <code>np.where</code>, zerando "
            "elementos abaixo de τ e preservando o valor original dos demais. "
            "A multiplicação elemento a elemento com a máscara binária separa as "
            "contribuições dentro e fora da RoI, e a razão final produz AL. O caso "
            "degenerado (ativação total zero) é tratado explicitamente.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def persistence_section(styles) -> list:
    schema = (
        "CREATE TABLE IF NOT EXISTS xai_tests (\n"
        "    id           TEXT PRIMARY KEY,\n"
        "    imageUri     TEXT NOT NULL,\n"
        "    prediction   TEXT NOT NULL,\n"
        "    confidence   REAL NOT NULL,\n"
        "    al           REAL NOT NULL,\n"
        "    afs          REAL NOT NULL,\n"
        "    threshold    REAL NOT NULL,\n"
        "    bboxJson     TEXT NOT NULL,\n"
        "    bboxStrategy TEXT NOT NULL,\n"
        "    overlayB64   TEXT NOT NULL,\n"
        "    label        TEXT NOT NULL,\n"
        "    createdAt    TEXT NOT NULL\n"
        ");"
    )
    return [
        Paragraph("12. Persistência e exportação de dados", styles["H1"]),
        Paragraph(
            "Cada execução do modo científico é armazenada na tabela <code>xai_tests</code> "
            "do SQLite local do aplicativo. O esquema preserva os metadados necessários para "
            "análise posterior sem depender do backend — o <i>overlay</i> é guardado em "
            "base64 para que o usuário possa revisitar resultados anteriores sem necessidade "
            "de re-executar o Grad-CAM.",
            styles["Body"],
        ),
        Paragraph(
            f"<font name='Courier' size='8'>{schema.replace(chr(10), '<br/>')}</font>",
            styles["Code"],
        ),
        Paragraph(
            "A exportação em CSV, implementada em <code>utils/csvExport.ts</code>, gera um "
            "arquivo com uma linha por teste contendo as colunas: <i>id, createdAt, "
            "prediction, confidence, al, afs, threshold, bboxStrategy, bboxX, bboxY, "
            "bboxW, bboxH, label, imageUri</i>. O arquivo é escrito no diretório de cache "
            "do app e compartilhado através do <i>share sheet</i> do sistema operacional, "
            "permitindo integração imediata com ferramentas analíticas externas "
            "(planilhas, Pandas, R).",
            styles["Body"],
        ),
        PageBreak(),
    ]


def use_case_diagram_section(styles) -> list:
    img = render_use_case()
    return [
        Paragraph("13. Diagrama de casos de uso", styles["H1"]),
        Paragraph(
            "O diagrama de casos de uso explicita a divisão de responsabilidades entre os "
            "dois perfis de usuário atendidos pelo sistema. O <b>Usuário</b> (botânico, "
            "estudante, agricultor) interage com o fluxo tradicional de identificação, "
            "inteiramente offline. O <b>Pesquisador</b> — tipicamente o autor ou leitores "
            "deste trabalho em contexto de análise científica — ativa o modo XAI e "
            "interage com casos de uso específicos de avaliação de atenção e exportação "
            "de dados.",
            styles["Body"],
        ),
        Image(img, width=17 * cm, height=11 * cm),
        Paragraph(
            "<b>Figura 5.</b> Casos de uso. As elipses em azul representam funcionalidades "
            "consumidas pelo usuário comum; as em roxo, aquelas acessíveis apenas a partir "
            "do modo científico.",
            styles["Caption"],
        ),
        PageBreak(),
    ]


def flowchart_section(styles) -> list:
    img = render_flowchart()
    return [
        Paragraph("14. Fluxograma do sistema", styles["H1"]),
        Paragraph(
            "O fluxograma a seguir descreve, em nível macro, os dois caminhos "
            "concorrentes do sistema a partir da tela inicial. O caminho à esquerda "
            "é o fluxo canônico de identificação, concluído integralmente no dispositivo; "
            "o caminho à direita, condicional à disponibilidade do backend XAI, conduz ao "
            "modo científico com persistência e exportação de resultados.",
            styles["Body"],
        ),
        Image(img, width=15.5 * cm, height=19 * cm),
        Paragraph(
            "<b>Figura 6.</b> Fluxograma macro do AgroVision, cobrindo ambos os caminhos "
            "operacionais.",
            styles["Caption"],
        ),
        PageBreak(),
    ]


def discussion_section(styles) -> list:
    return [
        Paragraph("15. Discussão e trabalhos futuros", styles["H1"]),
        Paragraph(
            "As métricas AL e AFS, por serem razões construídas sobre o heatmap Grad-CAM "
            "normalizado, herdam vantagens e limitações desse método. Entre as vantagens, "
            "destacam-se a facilidade de cálculo — duas operações vetoriais após o Grad-CAM "
            "já disponível — e a interpretabilidade direta em termos percentuais. Entre as "
            "limitações, observa-se que (i) a qualidade da métrica depende fortemente da "
            "qualidade da máscara <i>M</i> escolhida: bbox grosseiros tendem a reduzir a "
            "capacidade da métrica de discriminar vazamentos finos; (ii) o valor do "
            "<i>threshold</i> τ influencia a sensibilidade da métrica a ruído, demandando "
            "calibração quando se compara entre diferentes modelos ou <i>datasets</i>; "
            "(iii) AL/AFS capturam <i>vazamento espacial</i>, mas não explicam <i>qual</i> "
            "pista extraclasse o modelo está usando — essa análise requer inspeção "
            "qualitativa das regiões de alta ativação fora de <i>M</i>.",
            styles["Body"],
        ),
        Paragraph(
            "Entre os caminhos naturais de extensão deste trabalho incluem-se: substituir "
            "o bbox pela segmentação fina da planta obtida por um detector "
            "(ex.: YOLO ou MobileNet-SSD), o que estreita a fronteira da RoI e torna AL/AFS "
            "mais discriminativos; introduzir uma versão pixel-wise da métrica (baseada em "
            "IoU ponderado pela intensidade do heatmap); oferecer ao usuário final, dentro "
            "do app, o desenho interativo do bbox manual; e avaliar sistematicamente como "
            "AL/AFS evoluem ao longo de épocas de treinamento, fornecendo um sinal de "
            "convergência espacial complementar à <i>loss</i>.",
            styles["Body"],
        ),
        PageBreak(),
    ]


def references_section(styles) -> list:
    refs = [
        "Selvaraju, R. R., Cogswell, M., Das, A., Vedantam, R., Parikh, D., & "
        "Batra, D. (2017). <b>Grad-CAM: Visual explanations from deep networks "
        "via gradient-based localization.</b> ICCV 2017, 618–626.",
        "Sandler, M., Howard, A., Zhu, M., Zhmoginov, A., & Chen, L.-C. (2018). "
        "<b>MobileNetV2: Inverted residuals and linear bottlenecks.</b> "
        "CVPR 2018, 4510–4520.",
        "Zuiderveld, K. (1994). <b>Contrast Limited Adaptive Histogram "
        "Equalization.</b> In Graphics Gems IV (pp. 474–485). Academic Press.",
        "Garcin, C., Joly, A., Bonnet, P., et al. (2021). <b>Pl@ntNet-300K: "
        "a plant image dataset with high label ambiguity and a long-tailed "
        "distribution.</b> NeurIPS Datasets and Benchmarks Track.",
        "Hughes, D. P., & Salathé, M. (2015). <b>An open access repository of "
        "images on plant health to enable the development of mobile disease "
        "diagnostics (PlantVillage).</b> arXiv:1511.08060.",
        "Abadi, M. et al. (2015). <b>TensorFlow: Large-Scale Machine Learning on "
        "Heterogeneous Systems.</b> Disponível em: https://www.tensorflow.org/.",
        "Ramírez, S. (2018–). <b>FastAPI: Modern, fast web framework for building "
        "APIs with Python.</b> Disponível em: https://fastapi.tiangolo.com/.",
        "Meta. (2015–). <b>React Native Documentation.</b> "
        "Disponível em: https://reactnative.dev/.",
    ]
    items = [
        ListItem(Paragraph(r, styles["Body"]), leftIndent=16, bulletColor=MUTED)
        for r in refs
    ]
    return [
        Paragraph("16. Referências", styles["H1"]),
        ListFlowable(items, bulletType="1"),
    ]


# ==========================================================================
# Main
# ==========================================================================


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        title="AgroVision — Identificação de Espécies com IA Explicável",
        author="Luiz Carlos",
        subject="TCC — Grad-CAM + Attention Leakage",
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2.2 * cm, bottomMargin=2 * cm,
    )

    styles = build_styles()

    story: list = []
    story += cover_page(styles)
    story += abstract_section(styles)
    story += toc_section(styles)
    story += intro_section(styles)
    story += architecture_section(styles)
    story += stack_section(styles)
    story += structure_section(styles)
    story += model_section(styles)
    story += training_section(styles)
    story += xai_theory_section(styles)
    story += al_afs_section(styles)
    story += mask_section(styles)
    story += arch_xai_section(styles)
    story += implementation_section(styles)
    story += persistence_section(styles)
    story += use_case_diagram_section(styles)
    story += flowchart_section(styles)
    story += discussion_section(styles)
    story += references_section(styles)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"[OK] PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
