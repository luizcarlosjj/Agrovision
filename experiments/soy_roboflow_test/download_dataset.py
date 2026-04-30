"""
Baixa o dataset soy-leaf-disease (object detection) do Roboflow via REST API
e recorta cada bounding box por classe, gerando um dataset de classificação em:

  dataset/
    train/{classe}/img_001.jpg
    valid/{classe}/img_002.jpg
    test/{classe}/img_003.jpg

Requer: pip install requests pillow
Requer: variável de ambiente ROBOFLOW_API_KEY
"""

import io
import json
import os
import sys
import time
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' não instalado.  pip install requests")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: 'pillow' não instalado.  pip install pillow")
    sys.exit(1)

ROBOFLOW_WORKSPACE = "roboflow-universe-projects"
ROBOFLOW_PROJECT   = "soy-leaf-disease"
ROBOFLOW_VERSION   = 1

BASE_DIR    = Path(__file__).parent
RAW_DIR     = BASE_DIR / "dataset_raw"
DATASET_DIR = BASE_DIR / "dataset"
ZIP_PATH    = RAW_DIR / "roboflow.zip"


def get_api_key() -> str:
    key = os.environ.get("ROBOFLOW_API_KEY", "")
    if not key:
        print("ERROR: ROBOFLOW_API_KEY não definida.")
        print("  PowerShell: $env:ROBOFLOW_API_KEY='sua_chave'")
        sys.exit(1)
    return key


def is_valid_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            bad = zf.testzip()
            return bad is None
    except Exception:
        return False


def get_export_link(api_key: str) -> str:
    url = (
        f"https://api.roboflow.com/{ROBOFLOW_WORKSPACE}"
        f"/{ROBOFLOW_PROJECT}/{ROBOFLOW_VERSION}/coco"
    )
    print(f"Solicitando export: {url}")
    resp = requests.get(url, params={"api_key": api_key}, timeout=60)

    if resp.status_code != 200:
        print(f"ERROR: API retornou HTTP {resp.status_code}")
        print(resp.text[:400])
        sys.exit(1)

    try:
        data = resp.json()
    except ValueError:
        print("ERROR: Resposta não é JSON:", resp.text[:200])
        sys.exit(1)

    link = data.get("export", {}).get("link") or data.get("link")
    if not link:
        print("ERROR: Link não encontrado:", json.dumps(data, indent=2)[:400])
        sys.exit(1)

    return link


def download_zip(api_key: str):
    """Baixa o ZIP com até 3 tentativas (link signed expira em 15 min)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, 4):
        link = get_export_link(api_key)
        print(f"Tentativa {attempt}/3 — baixando ZIP...")

        try:
            resp = requests.get(link, stream=True, timeout=300)
            if resp.status_code == 404:
                print("  Link ainda não disponível (404). Aguardando 10s...")
                time.sleep(10)
                continue
            resp.raise_for_status()

            content = resp.content
            print(f"  Recebido: {len(content) / 1024:.0f} KB")

            if content[:4] != b"PK\x03\x04":
                print(f"  Arquivo não é ZIP (bytes: {content[:8]}). Tentando novamente...")
                time.sleep(5)
                continue

            ZIP_PATH.write_bytes(content)
            print(f"  ZIP salvo: {ZIP_PATH}")
            return

        except requests.exceptions.RequestException as e:
            print(f"  Erro de rede: {e}")
            time.sleep(5)

    print("ERROR: Não foi possível baixar o ZIP após 3 tentativas.")
    sys.exit(1)


def extract_zip():
    print(f"Extraindo {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(RAW_DIR)

    print("Arquivos extraídos:")
    for p in sorted(RAW_DIR.rglob("*"))[:30]:
        marker = "/" if p.is_dir() else ""
        print(f"  {p.relative_to(RAW_DIR)}{marker}")


def crop_split(split: str) -> dict:
    """Recorta bounding boxes de um split e organiza por classe."""
    candidates = list(RAW_DIR.glob(f"**/{split}")) + [RAW_DIR / split]
    split_dir = next((p for p in candidates if p.is_dir()), None)

    if split_dir is None:
        return {}

    json_files = list(split_dir.glob("*.json")) + list(split_dir.glob("**/*.json"))
    if not json_files:
        print(f"  [{split}] JSON de anotações não encontrado em {split_dir}")
        return {}

    with open(json_files[0], "r", encoding="utf-8") as f:
        coco = json.load(f)

    cat_map   = {c["id"]: c["name"] for c in coco.get("categories", [])}
    image_map = {img["id"]: img for img in coco.get("images", [])}
    counts: dict = {}

    images_dir = split_dir / "images" if (split_dir / "images").exists() else split_dir

    for ann in coco.get("annotations", []):
        img_info = image_map.get(ann["image_id"])
        cat_name = cat_map.get(ann["category_id"], "unknown")
        if img_info is None:
            continue

        fname = img_info["file_name"]
        img_file = next(
            (p for p in [
                images_dir / fname,
                split_dir / fname,
                RAW_DIR / fname,
                images_dir / Path(fname).name,
            ] if p.exists()),
            None,
        )
        if img_file is None:
            continue

        dest_dir = DATASET_DIR / split / cat_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        x, y, w, h = [int(v) for v in ann["bbox"]]
        if w < 5 or h < 5:
            continue

        try:
            img  = Image.open(img_file).convert("RGB")
            crop = img.crop((x, y, x + w, y + h))
            out_name = f"{img_info['id']:06d}_{ann['id']:06d}.jpg"
            crop.save(dest_dir / out_name, "JPEG", quality=92)
            counts[cat_name] = counts.get(cat_name, 0) + 1
        except Exception as e:
            print(f"  AVISO: erro ao recortar {img_file.name}: {e}")

    return counts


def main():
    api_key = get_api_key()

    # Reutiliza o ZIP já baixado se for válido
    if ZIP_PATH.exists():
        print(f"ZIP já existe: {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024:.0f} KB)")
        if is_valid_zip(ZIP_PATH):
            print("ZIP válido — pulando download.")
        else:
            print("ZIP inválido ou corrompido — baixando novamente.")
            ZIP_PATH.unlink()
            download_zip(api_key)
    else:
        download_zip(api_key)

    # Extrai apenas se dataset_raw ainda não tiver subpastas
    already_extracted = any(p.is_dir() for p in RAW_DIR.iterdir() if p != ZIP_PATH)
    if not already_extracted:
        extract_zip()
    else:
        print("Arquivos já extraídos — pulando extração.")

    print("\nRecortando bounding boxes por classe...")
    total_crops = 0
    for split in ["train", "valid", "test"]:
        counts = crop_split(split)
        if counts:
            total = sum(counts.values())
            total_crops += total
            print(f"  {split:6s}: {total:4d} recortes  |  {dict(sorted(counts.items()))}")

    if total_crops == 0:
        print("\nAVISO: Nenhum recorte gerado.")
        print(f"Verifique a estrutura em: {RAW_DIR.resolve()}")
    else:
        print(f"\nTotal: {total_crops} recortes → {DATASET_DIR.resolve()}")
        print("Próximo passo: python train_soy_disease.py")


if __name__ == "__main__":
    main()
