#!/usr/bin/env python3
"""
Preparação automática do dataset para o experimento do TCC.

Etapa 1 — Download:
    Baixa 50 imagens de milho (bem enquadradas) do dataset PlantVillage
    hospedado no Hugging Face (sem login, sem chave de API).

Etapa 2 — Augmentação:
    Gera 50 variantes "mal enquadradas" a partir das imagens baixadas,
    aplicando transformações que simulam erros reais de enquadramento:
      - zoom_out    → planta pequena, fundo aparente
      - offset      → planta deslocada para uma das bordas
      - rotate      → rotação forte (40-80 graus)
      - partial     → parte da folha cortada pelo frame

Por que usar as mesmas imagens?
    Garante que a única variável entre os grupos seja o enquadramento.
    Isso é mais rigoroso cientificamente para o TCC.

Uso:
    pip install -r requirements.txt
    python preparar_dataset.py

    # Só download (se já tiver as bem_enquadradas):
    python preparar_dataset.py --etapa download

    # Só gerar mal enquadradas a partir das que já estão na pasta:
    python preparar_dataset.py --etapa augmentar
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from pathlib import Path

# ─── Verificação de dependências ──────────────────────────────────────────────

missing = []
try:
    from PIL import Image, ImageFilter
except ImportError:
    missing.append("Pillow")
try:
    import requests
except ImportError:
    missing.append("requests")

if missing:
    sys.exit(f"Instale: pip install {' '.join(missing)}")


# ─── Configuração ─────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
BEM_DIR    = SCRIPT_DIR / "dataset" / "bem_enquadradas"
MAL_DIR    = SCRIPT_DIR / "dataset" / "mal_enquadradas"

# Classes de milho no PlantVillage (HuggingFace mohanty/PlantVillage)
CORN_CLASS_KEYWORDS = [
    "corn",
    "maize",
    "Corn",
    "Maize",
]

OUTPUT_SIZE = (512, 512)   # tamanho final das imagens salvas
N_BEM       = 50           # imagens bem enquadradas a baixar
N_MAL       = 50           # imagens mal enquadradas a gerar

random.seed(42)            # reprodutibilidade

# ─── Augmentações para "mal enquadradas" ──────────────────────────────────────

AugType = str  # 'zoom_out' | 'offset' | 'rotate' | 'partial'


def _aug_zoom_out(img: Image.Image) -> Image.Image:
    """Planta pequena no centro — parece que a câmera estava longe."""
    w, h = img.size
    scale = random.uniform(0.35, 0.55)
    small = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), color=(30, 60, 20))
    x = (w - small.width)  // 2
    y = (h - small.height) // 2
    canvas.paste(small, (x, y))
    return canvas


def _aug_offset(img: Image.Image) -> Image.Image:
    """Planta empurrada para uma das bordas."""
    w, h = img.size
    scale = random.uniform(0.50, 0.70)
    small = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), color=(30, 60, 20))
    side = random.choice(["top_left", "top_right", "bottom_left", "bottom_right"])
    if side == "top_left":
        x, y = 0, 0
    elif side == "top_right":
        x, y = w - small.width, 0
    elif side == "bottom_left":
        x, y = 0, h - small.height
    else:
        x, y = w - small.width, h - small.height
    canvas.paste(small, (x, y))
    return canvas


def _aug_rotate(img: Image.Image) -> Image.Image:
    """Rotação forte — câmera inclinada ou folha deitada."""
    angle = random.choice([-80, -65, -50, 50, 65, 80])
    return img.rotate(angle, expand=False, fillcolor=(30, 60, 20))


def _aug_partial(img: Image.Image) -> Image.Image:
    """Parte da folha cortada pelo frame — câmera muito perto ou deslocada."""
    w, h = img.size
    cut_pct = random.uniform(0.25, 0.42)
    side    = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        box = (int(w * cut_pct), 0, w, h)
    elif side == "right":
        box = (0, 0, int(w * (1 - cut_pct)), h)
    elif side == "top":
        box = (0, int(h * cut_pct), w, h)
    else:
        box = (0, 0, w, int(h * (1 - cut_pct)))
    cropped = img.crop(box)
    return cropped.resize((w, h), Image.LANCZOS)


AUG_FUNCS = {
    "zoom_out": _aug_zoom_out,
    "offset":   _aug_offset,
    "rotate":   _aug_rotate,
    "partial":  _aug_partial,
}


def apply_random_augmentation(img: Image.Image) -> tuple[Image.Image, AugType]:
    aug_type = random.choice(list(AUG_FUNCS.keys()))
    result   = AUG_FUNCS[aug_type](img)
    # leve blur opcional (simula foco ruim)
    if random.random() < 0.35:
        result = result.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.8, 2.0)))
    return result, aug_type


# ─── Etapa 1: Download ────────────────────────────────────────────────────────

def download_bem_enquadradas(n: int = N_BEM) -> None:
    """
    Baixa imagens diretamente do repositório GitHub do PlantVillage
    (spMohanty/PlantVillage-Dataset). Sem login, sem chave, sem biblioteca pesada.

    Usa a GitHub Contents API para listar arquivos (60 req/hora gratuito) e
    depois baixa as imagens via raw.githubusercontent.com (sem limite de taxa).
    """
    import io as _io

    BEM_DIR.mkdir(parents=True, exist_ok=True)

    existing = list(BEM_DIR.glob("*.jpg")) + list(BEM_DIR.glob("*.png"))
    if len(existing) >= n:
        print(f"  ✅  {len(existing)} imagens já existem em bem_enquadradas/ — pulando download.")
        return

    GITHUB_API  = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color"
    CORN_DIRS   = [
        "Corn_(maize)___Common_rust_",
        "Corn_(maize)___Northern_Leaf_Blight",
        "Corn_(maize)___healthy",
        "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    ]

    # ── 1. Busca lista de arquivos de cada classe de milho ────────────────────
    print("  Listando imagens disponíveis no GitHub PlantVillage...")
    all_entries: list[tuple[str, str]] = []  # (class_short_name, download_url)

    for class_dir in CORN_DIRS:
        api_url = f"{GITHUB_API}/{requests.utils.quote(class_dir)}"
        try:
            resp = requests.get(api_url, timeout=20, headers={"Accept": "application/vnd.github.v3+json"})
            resp.raise_for_status()
            files = resp.json()
            label_short = class_dir.split("___")[-1][:25]
            entries = [(label_short, f["download_url"]) for f in files if f.get("download_url")]
            random.shuffle(entries)
            all_entries.extend(entries)
            print(f"    ✅  {class_dir.split('___')[-1][:35]}: {len(entries)} imagens")
        except Exception as exc:
            print(f"    ⚠  Erro ao listar {class_dir}: {exc}")

    if not all_entries:
        sys.exit("❌  Não foi possível listar imagens do GitHub. Verifique a conexão.")

    # Embaralha para ter diversidade de classes
    random.shuffle(all_entries)

    # ── 2. Baixa as imagens ───────────────────────────────────────────────────
    print(f"\n  Baixando {n} imagens (pode demorar 1-3 min)...\n")
    saved = 0

    for label_short, url in all_entries:
        if saved >= n:
            break
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            pil_img = Image.open(_io.BytesIO(resp.content)).convert("RGB")
            pil_img = pil_img.resize(OUTPUT_SIZE, Image.LANCZOS)

            label_safe = label_short.replace(" ", "_")
            fname = f"bem_{saved+1:03d}_{label_safe}.jpg"
            pil_img.save(BEM_DIR / fname, "JPEG", quality=92)
            saved += 1
            print(f"  [{saved:>3}/{n}]  ✅  {label_short:<28}  →  {fname}")
            time.sleep(0.05)   # pausa mínima para não sobrecarregar o CDN
        except Exception as exc:
            print(f"  ⚠  Ignorada ({url.split('/')[-1][:30]}): {exc}")

    print(f"\n  Download concluído: {saved} imagem(ns) salvas em {BEM_DIR}\n")


# ─── Etapa 2: Augmentação ─────────────────────────────────────────────────────

def gerar_mal_enquadradas(n: int = N_MAL) -> None:
    MAL_DIR.mkdir(parents=True, exist_ok=True)

    sources = sorted(BEM_DIR.glob("*.jpg")) + sorted(BEM_DIR.glob("*.png"))
    if not sources:
        sys.exit(
            "❌  Nenhuma imagem encontrada em bem_enquadradas/\n"
            "   Execute primeiro: python preparar_dataset.py --etapa download"
        )

    existing = list(MAL_DIR.glob("*.jpg")) + list(MAL_DIR.glob("*.png"))
    if len(existing) >= n:
        print(f"  ✅  {len(existing)} imagens já existem em mal_enquadradas/ — pulando geração.")
        return

    print(f"  Gerando {n} imagens mal enquadradas a partir de {len(sources)} fontes...\n")

    # Se temos menos fontes que o necessário, repetimos com augmentações diferentes
    pool = sources * (n // len(sources) + 2)
    random.shuffle(pool)

    count_per_type: dict[str, int] = {k: 0 for k in AUG_FUNCS}
    saved = 0

    for i, src_path in enumerate(pool):
        if saved >= n:
            break
        try:
            img = Image.open(src_path).convert("RGB")
            aug_img, aug_type = apply_random_augmentation(img)
            aug_img = aug_img.resize(OUTPUT_SIZE, Image.LANCZOS)

            src_stem = src_path.stem.replace("bem_", "")
            fname = f"mal_{saved+1:03d}_{aug_type}_{src_stem[:30]}.jpg"
            aug_img.save(MAL_DIR / fname, "JPEG", quality=88)

            saved += 1
            count_per_type[aug_type] += 1
            print(f"  [{saved:>3}/{n}]  ✅  {aug_type:<10}  {fname}")
        except Exception as exc:
            print(f"  ⚠  Erro ao processar {src_path.name}: {exc}")

    print(f"\n  Geração concluída: {saved} imagem(ns) salvas em {MAL_DIR}")
    print(f"  Distribuição de augmentações:")
    for atype, cnt in count_per_type.items():
        bar = "█" * cnt
        print(f"    {atype:<12}: {cnt:>3}  {bar}")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preparação do dataset TCC — AgroVision",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--etapa",
        choices=["tudo", "download", "augmentar"],
        default="tudo",
        help="Qual etapa executar",
    )
    parser.add_argument("--n-bem", type=int, default=N_BEM, help="Nº de imagens bem enquadradas")
    parser.add_argument("--n-mal", type=int, default=N_MAL, help="Nº de imagens mal enquadradas")
    args = parser.parse_args()

    sep = "─" * 64
    print(f"\n{sep}")
    print("  AgroVision — Preparação do Dataset TCC")
    print(sep)
    print(f"  Fonte:   HuggingFace mohanty/PlantVillage (sem login)")
    print(f"  Bem enquadradas: {args.n_bem} imagens  →  {BEM_DIR}")
    print(f"  Mal enquadradas: {args.n_mal} imagens  →  {MAL_DIR}")
    print(f"{sep}\n")

    if args.etapa in ("tudo", "download"):
        print("=== ETAPA 1: Download (bem_enquadradas) ===\n")
        download_bem_enquadradas(args.n_bem)

    if args.etapa in ("tudo", "augmentar"):
        print("=== ETAPA 2: Augmentação (mal_enquadradas) ===\n")
        gerar_mal_enquadradas(args.n_mal)

    bem_count = len(list(BEM_DIR.glob("*.jpg"))) + len(list(BEM_DIR.glob("*.png")))
    mal_count = len(list(MAL_DIR.glob("*.jpg"))) + len(list(MAL_DIR.glob("*.png")))

    print(f"{sep}")
    print("  Dataset pronto!")
    print(f"  bem_enquadradas: {bem_count} imagens")
    print(f"  mal_enquadradas: {mal_count} imagens")
    print(f"\n  Agora rode: python batch_tcc.py")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
