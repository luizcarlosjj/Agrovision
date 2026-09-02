#!/usr/bin/env python3
"""
Processamento em lote para o experimento do TCC - AgroVision Grad-CAM.

Envia imagens para o backend Railway (/api/xai/gradcam), descarta resultados
com confiança abaixo do mínimo e gera um arquivo Excel em testes/resultados/.

Estrutura esperada:
    testes/
        dataset/
            bem_enquadradas/    <- fotos bem enquadradas (JPG / PNG)
            mal_enquadradas/    <- fotos mal enquadradas (JPG / PNG)
        resultados/             <- Excel gerado aqui
        .env                    <- sua chave real (nunca commitar)

Configuração:
    Copie .env.example para .env e preencha AGROVISION_API_KEY

Uso rápido:
    cd testes/
    pip install -r requirements.txt
    python batch_tcc.py

Opções avançadas:
    python batch_tcc.py --confidence-min 0.65 --threshold 0.5 --strategy fixed
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ─── Verificação de dependências ──────────────────────────────────────────────

missing = []
try:
    import requests
except ImportError:
    missing.append("requests")
try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
except ImportError:
    missing.append("openpyxl")

if missing:
    sys.exit(
        f"Dependências ausentes: {', '.join(missing)}\n"
        f"Execute dentro de testes/: pip install -r requirements.txt"
    )

try:
    from dotenv import load_dotenv
    # Carrega .env da pasta onde este script está
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # sem python-dotenv: use variáveis de ambiente diretamente

# ─── Constantes ───────────────────────────────────────────────────────────────

DEFAULT_API_URL  = "https://agrovision-production-bdc3.up.railway.app"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_RETRIES      = 3
RETRY_DELAY_S    = 6

# Pasta deste script (testes/)
SCRIPT_DIR   = Path(__file__).parent
DATASET_DIR  = SCRIPT_DIR / "dataset"
RESULTS_DIR  = SCRIPT_DIR / "resultados"

COLUMNS = [
    ("arquivo",            "Arquivo"),
    ("label",              "Label"),
    ("status",             "Status"),
    ("motivo_descarte",    "Motivo Descarte"),
    ("prediction",         "Predição"),
    ("confidence",         "Confiança"),
    ("al",                 "AL (Attention Leakage)"),
    ("afs",                "AFS (Focus Score)"),
    ("threshold",          "Threshold"),
    ("layer_used",         "Camada Grad-CAM"),
    ("bbox_strategy",      "Estratégia BBox"),
    ("bbox_x",             "BBox X"),
    ("bbox_y",             "BBox Y"),
    ("bbox_w",             "BBox W"),
    ("bbox_h",             "BBox H"),
    ("image_width",        "Largura (px)"),
    ("image_height",       "Altura (px)"),
    ("processing_time_ms", "Tempo (ms)"),
    ("processado_em",      "Processado Em"),
]

STATUS_COLORS = {
    "ok":         "C6EFCE",  # verde
    "descartado": "FFEB9C",  # amarelo
    "erro":       "FFC7CE",  # vermelho
}


# ─── Processamento de uma imagem ──────────────────────────────────────────────

def _mime(path: Path) -> str:
    return {"png": "image/png", "webp": "image/webp"}.get(
        path.suffix.lower().lstrip("."), "image/jpeg"
    )


def process_image(
    image_path: Path,
    label: str,
    api_url: str,
    api_key: str,
    bbox_strategy: str,
    threshold: float,
    coverage: float,
    confidence_min: float,
) -> dict:
    empty = {k: "" for k, _ in COLUMNS if k not in ("arquivo", "label", "status", "motivo_descarte", "processado_em")}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with open(image_path, "rb") as fh:
                resp = requests.post(
                    f"{api_url}/api/xai/gradcam",
                    files={"image": (image_path.name, fh, _mime(image_path))},
                    data={
                        "bbox_strategy": bbox_strategy,
                        "threshold":     str(threshold),
                        "coverage":      str(coverage),
                    },
                    headers={"X-API-Key": api_key},
                    timeout=120,
                )

            if resp.status_code == 403:
                sys.exit("\n❌  API key inválida. Verifique o arquivo testes/.env")

            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")

            r    = resp.json()
            conf = float(r["confidence"])
            bbox = r.get("bbox_used", [0, 0, 0, 0])
            ok   = conf >= confidence_min

            return {
                "arquivo":            image_path.name,
                "label":              label,
                "status":             "ok" if ok else "descartado",
                "motivo_descarte":    "" if ok else f"confiança {conf:.1%} < mínimo {confidence_min:.0%}",
                "prediction":         r.get("prediction", ""),
                "confidence":         round(conf, 4),
                "al":                 round(float(r["al"]), 4),
                "afs":                round(float(r["afs"]), 4),
                "threshold":          round(float(r["threshold"]), 2),
                "layer_used":         r.get("layer_used", ""),
                "bbox_strategy":      r.get("bbox_strategy", ""),
                "bbox_x":             bbox[0] if len(bbox) > 0 else "",
                "bbox_y":             bbox[1] if len(bbox) > 1 else "",
                "bbox_w":             bbox[2] if len(bbox) > 2 else "",
                "bbox_h":             bbox[3] if len(bbox) > 3 else "",
                "image_width":        r.get("image_width", ""),
                "image_height":       r.get("image_height", ""),
                "processing_time_ms": r.get("processing_time_ms", ""),
                "processado_em":      datetime.now().isoformat(timespec="seconds"),
            }

        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < MAX_RETRIES:
                print(f"\n     ⚠  Timeout (tentativa {attempt}/{MAX_RETRIES}). Aguardando {RETRY_DELAY_S}s...", flush=True)
                time.sleep(RETRY_DELAY_S)
            else:
                return {"arquivo": image_path.name, "label": label,
                        "status": "erro", "motivo_descarte": f"Timeout após {MAX_RETRIES} tentativas: {exc}",
                        "processado_em": datetime.now().isoformat(timespec="seconds"), **empty}

        except Exception as exc:
            return {"arquivo": image_path.name, "label": label,
                    "status": "erro", "motivo_descarte": str(exc)[:300],
                    "processado_em": datetime.now().isoformat(timespec="seconds"), **empty}

    return {"arquivo": image_path.name, "label": label, "status": "erro",
            "motivo_descarte": "Falha inesperada", "processado_em": datetime.now().isoformat(), **empty}


# ─── Exportação Excel ─────────────────────────────────────────────────────────

def export_excel(results: list[dict], output_path: Path) -> None:
    wb = openpyxl.Workbook()

    # ── Aba: Resultados ────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "Resultados"

    hdr_font = Font(bold=True, color="FFFFFF")
    hdr_fill = PatternFill("solid", fgColor="1B5E20")

    for col_i, (_, header) in enumerate(COLUMNS, 1):
        c = ws.cell(row=1, column=col_i, value=header)
        c.font = hdr_font
        c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"

    for row_i, rec in enumerate(results, 2):
        fill = PatternFill("solid", fgColor=STATUS_COLORS.get(rec.get("status", ""), "FFFFFF"))
        for col_i, (key, _) in enumerate(COLUMNS, 1):
            c = ws.cell(row=row_i, column=col_i, value=rec.get(key, ""))
            c.fill = fill

    for col in ws.columns:
        width = max((len(str(cell.value or "")) for cell in col), default=8)
        ws.column_dimensions[col[0].column_letter].width = min(width + 3, 52)

    # ── Aba: Resumo ────────────────────────────────────────────────────────────
    ws2 = wb.create_sheet("Resumo")

    ok_all = [r for r in results if r.get("status") == "ok"]
    bem_ok = [r for r in ok_all if r.get("label") == "bem_enquadradas"]
    mal_ok = [r for r in ok_all if r.get("label") == "mal_enquadradas"]

    def avg(lst: list[dict], key: str) -> float | str:
        vals = [r[key] for r in lst if isinstance(r.get(key), (int, float))]
        return round(sum(vals) / len(vals), 4) if vals else "—"

    sec = Font(bold=True, color="1B5E20")
    rows: list[tuple[str, object]] = [
        ("=== GERAL ===",                               ""),
        ("Total processado",                            len(results)),
        ("Aprovados (ok)",                              len(ok_all)),
        ("Descartados (baixa confiança)",               sum(1 for r in results if r.get("status") == "descartado")),
        ("Erros de rede / backend",                     sum(1 for r in results if r.get("status") == "erro")),
        ("", ""),
        ("=== BEM ENQUADRADAS (aprovadas) ===",         ""),
        ("Quantidade",                                  len(bem_ok)),
        ("Confiança média",                             avg(bem_ok, "confidence")),
        ("AL médio (Attention Leakage)",                avg(bem_ok, "al")),
        ("AFS médio (Focus Score)",                     avg(bem_ok, "afs")),
        ("Tempo médio de inferência (ms)",              avg(bem_ok, "processing_time_ms")),
        ("", ""),
        ("=== MAL ENQUADRADAS (aprovadas) ===",         ""),
        ("Quantidade",                                  len(mal_ok)),
        ("Confiança média",                             avg(mal_ok, "confidence")),
        ("AL médio (Attention Leakage)",                avg(mal_ok, "al")),
        ("AFS médio (Focus Score)",                     avg(mal_ok, "afs")),
        ("Tempo médio de inferência (ms)",              avg(mal_ok, "processing_time_ms")),
        ("", ""),
        ("Gerado em",                                   datetime.now().isoformat(timespec="seconds")),
    ]

    for i, (lbl, val) in enumerate(rows, 1):
        c1 = ws2.cell(row=i, column=1, value=lbl)
        ws2.cell(row=i, column=2, value=val)
        if lbl.startswith("==="):
            c1.font = sec

    ws2.column_dimensions["A"].width = 40
    ws2.column_dimensions["B"].width = 22

    wb.save(output_path)


# ─── Coleta de imagens ────────────────────────────────────────────────────────

def collect_images(folder_name: str) -> list[tuple[Path, str]]:
    folder = DATASET_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    imgs = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    if not imgs:
        print(f"  ⚠  Pasta vazia: {folder}")
    return [(img, folder_name) for img in imgs]


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AgroVision — Batch TCC",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--api-key",        default="",         help="AGROVISION_API_KEY (ou use .env)")
    parser.add_argument("--api-url",        default="",         help="URL do backend")
    parser.add_argument("--confidence-min", type=float, default=0.60, help="Confiança mínima (0-1)")
    parser.add_argument("--threshold",      type=float, default=0.50, help="Threshold do heatmap Grad-CAM (0-1)")
    parser.add_argument("--coverage",       type=float, default=0.80, help="Cobertura da bounding box central (0-1)")
    parser.add_argument("--strategy",       default="fixed",          help="Estratégia: fixed | green")
    parser.add_argument("--delay",          type=float, default=0.5,  help="Pausa entre requests (s)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("AGROVISION_API_KEY", "").strip()
    api_url = (args.api_url or os.environ.get("AGROVISION_API_URL", DEFAULT_API_URL)).rstrip("/")

    if not api_key:
        sys.exit(
            "\n❌  AGROVISION_API_KEY não encontrada.\n\n"
            "   Copie o arquivo .env.example para .env:\n"
            "       cp .env.example .env\n\n"
            "   Edite .env e coloque sua chave:\n"
            "       AGROVISION_API_KEY=sua_chave_aqui\n\n"
            "   (A chave está no Railway Dashboard → seu projeto → Variables)\n"
        )

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"resultados_tcc_{timestamp}.xlsx"

    sep = "─" * 64
    print(f"\n{sep}")
    print("  AgroVision — Processamento em Lote (TCC)")
    print(sep)
    print(f"  Backend:       {api_url}")
    print(f"  Estratégia:    bbox={args.strategy}  threshold={args.threshold}  coverage={args.coverage}")
    print(f"  Conf. mínima:  {args.confidence_min:.0%}  (abaixo → descartado)")
    print(f"  Saída:         {output_path.relative_to(SCRIPT_DIR)}")
    print(f"{sep}\n")

    images = collect_images("bem_enquadradas") + collect_images("mal_enquadradas")

    if not images:
        sys.exit(
            "❌  Nenhuma imagem encontrada.\n"
            "   Coloque fotos JPG/PNG em:\n"
            f"     {DATASET_DIR / 'bem_enquadradas'}\n"
            f"     {DATASET_DIR / 'mal_enquadradas'}\n"
        )

    total  = len(images)
    t0     = time.perf_counter()
    results: list[dict] = []

    print(f"  {total} imagem(ns) encontrada(s). Iniciando...\n")

    try:
        for i, (img_path, label) in enumerate(images, 1):
            lbl_short = label.replace("_enquadradas", "")
            print(f"  [{i:>3}/{total}]  {lbl_short:<5}  {img_path.name:<38}", end=" ", flush=True)

            row = process_image(
                image_path=img_path,
                label=label,
                api_url=api_url,
                api_key=api_key,
                bbox_strategy=args.strategy,
                threshold=args.threshold,
                coverage=args.coverage,
                confidence_min=args.confidence_min,
            )
            results.append(row)

            s = row["status"]
            if s == "ok":
                print(f"✅  conf={row['confidence']:.1%}  AL={row['al']:.3f}  AFS={row['afs']:.3f}  {row['processing_time_ms']}ms")
            elif s == "descartado":
                print(f"⚠   {row['motivo_descarte']}")
            else:
                print(f"❌  {str(row['motivo_descarte'])[:60]}")

            if i < total and args.delay > 0:
                time.sleep(args.delay)

    except KeyboardInterrupt:
        print(f"\n\n  ⏹  Interrompido. Salvando {len(results)} resultado(s) parciais...")

    if not results:
        print("  Nenhum resultado para exportar.")
        return

    print(f"\n  Exportando {output_path.name}...", flush=True)
    export_excel(results, output_path)

    elapsed = time.perf_counter() - t0
    ok_n    = sum(1 for r in results if r["status"] == "ok")
    disc_n  = sum(1 for r in results if r["status"] == "descartado")
    err_n   = sum(1 for r in results if r["status"] == "erro")

    print(f"\n{sep}")
    print("  Concluído!")
    print(f"  ✅  Aprovados:    {ok_n}")
    print(f"  ⚠   Descartados: {disc_n}  (conf < {args.confidence_min:.0%})")
    print(f"  ❌  Erros:        {err_n}")
    print(f"  ⏱   Tempo total:  {elapsed:.0f}s")
    print(f"  📄  Arquivo:      {output_path}")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
