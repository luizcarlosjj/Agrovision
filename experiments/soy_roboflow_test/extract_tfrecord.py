"""
Lê o TFRecord exportado pelo Roboflow (object detection) e extrai cada
bounding box como um crop JPEG, organizando por classe:

  dataset/
    train/{classe}/img_000001_000001.jpg
    valid/{classe}/...
    test/{classe}/...

Depois rode: python train_soy_disease.py

Requer: pip install tensorflow pillow
Uso:    python extract_tfrecord.py caminho/para/tfrecord.zip
        python extract_tfrecord.py          ← busca automaticamente na pasta
"""

import io
import sys
import zipfile
from pathlib import Path

try:
    import tensorflow as tf
    print(f"TensorFlow {tf.__version__} carregado.")
except ImportError:
    print("ERROR: pip install tensorflow")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: pip install pillow")
    sys.exit(1)

BASE_DIR    = Path(__file__).parent
RAW_DIR     = BASE_DIR / "tfrecord_raw"
DATASET_DIR = BASE_DIR / "dataset"

# Features do TFRecord no formato Roboflow
FEATURE_SPEC = {
    "image/encoded":          tf.io.FixedLenFeature([], tf.string),
    "image/filename":         tf.io.FixedLenFeature([], tf.string, default_value=""),
    "image/object/bbox/xmin": tf.io.VarLenFeature(tf.float32),
    "image/object/bbox/xmax": tf.io.VarLenFeature(tf.float32),
    "image/object/bbox/ymin": tf.io.VarLenFeature(tf.float32),
    "image/object/bbox/ymax": tf.io.VarLenFeature(tf.float32),
    "image/object/class/text":tf.io.VarLenFeature(tf.string),
    "image/width":            tf.io.FixedLenFeature([], tf.int64, default_value=0),
    "image/height":           tf.io.FixedLenFeature([], tf.int64, default_value=0),
}


def find_zip() -> Path:
    """Busca o tfrecord.zip automaticamente na pasta do script."""
    zips = list(BASE_DIR.glob("*.zip")) + list(BASE_DIR.glob("**/*.zip"))
    tfzips = [z for z in zips if "tfrecord" in z.name.lower() or "tf" in z.name.lower()]
    if tfzips:
        return tfzips[0]
    if zips:
        print(f"Nenhum zip com 'tfrecord' no nome. Usando: {zips[0]}")
        return zips[0]
    print("ERROR: Nenhum arquivo .zip encontrado.")
    print("  Coloque o tfrecord.zip na pasta soy_roboflow_test/ ou passe o caminho como argumento.")
    sys.exit(1)


def extract_zip(zip_path: Path):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Extraindo {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(RAW_DIR)

    print("Estrutura extraída:")
    for p in sorted(RAW_DIR.rglob("*"))[:30]:
        print(f"  {p.relative_to(RAW_DIR)}")


def process_tfrecord(tfrecord_path: Path, split: str) -> int:
    """Processa um arquivo .tfrecord e salva crops por classe."""
    print(f"\n[{split}] Lendo: {tfrecord_path.name}")
    dataset = tf.data.TFRecordDataset(str(tfrecord_path))
    total = 0

    for raw_record in dataset:
        try:
            features = tf.io.parse_single_example(raw_record, FEATURE_SPEC)
        except Exception as e:
            print(f"  AVISO: erro ao parsear record: {e}")
            continue

        # Imagem
        img_bytes = features["image/encoded"].numpy()
        try:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            print(f"  AVISO: imagem inválida: {e}")
            continue

        w_img, h_img = img.size

        # Bounding boxes e classes (coordenadas normalizadas 0-1)
        xmins  = tf.sparse.to_dense(features["image/object/bbox/xmin"]).numpy()
        xmaxs  = tf.sparse.to_dense(features["image/object/bbox/xmax"]).numpy()
        ymins  = tf.sparse.to_dense(features["image/object/bbox/ymin"]).numpy()
        ymaxs  = tf.sparse.to_dense(features["image/object/bbox/ymax"]).numpy()
        labels = tf.sparse.to_dense(features["image/object/class/text"], default_value=b"").numpy()

        img_id = features["image/filename"].numpy().decode("utf-8", errors="replace")
        img_id = Path(img_id).stem or f"img_{total:06d}"

        for i, label_bytes in enumerate(labels):
            cat_name = label_bytes.decode("utf-8", errors="replace").strip()
            if not cat_name:
                continue

            # Converte coordenadas normalizadas → pixels
            x1 = int(xmins[i] * w_img)
            y1 = int(ymins[i] * h_img)
            x2 = int(xmaxs[i] * w_img)
            y2 = int(ymaxs[i] * h_img)

            if (x2 - x1) < 5 or (y2 - y1) < 5:
                continue

            dest_dir = DATASET_DIR / split / cat_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            crop = img.crop((x1, y1, x2, y2))
            out_name = f"{img_id}_{i:03d}.jpg"
            crop.save(dest_dir / out_name, "JPEG", quality=92)
            total += 1

    return total


def main():
    zip_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_zip()

    if not zip_path.exists():
        print(f"ERROR: Arquivo não encontrado: {zip_path}")
        sys.exit(1)

    # Extrai apenas se ainda não foi extraído
    if not RAW_DIR.exists() or not any(RAW_DIR.rglob("*.tfrecord")):
        extract_zip(zip_path)
    else:
        print(f"Arquivos já extraídos em {RAW_DIR}. Pulando extração.")

    # Localiza arquivos .tfrecord por split
    tfrecords = list(RAW_DIR.rglob("*.tfrecord"))
    if not tfrecords:
        print(f"ERROR: Nenhum arquivo .tfrecord encontrado em {RAW_DIR}")
        sys.exit(1)

    print(f"\nArquivos .tfrecord encontrados: {[t.name for t in tfrecords]}")

    total_crops = 0
    for tf_path in sorted(tfrecords):
        name = tf_path.stem.lower()
        # Detecta o split pelo nome do arquivo
        if "train" in name:
            split = "train"
        elif "valid" in name or "val" in name:
            split = "valid"
        elif "test" in name:
            split = "test"
        else:
            split = "train"  # fallback

        count = process_tfrecord(tf_path, split)
        print(f"  [{split}] {count} crops gerados")
        total_crops += count

    # Resumo por classe
    print(f"\nTotal de crops: {total_crops}")
    if total_crops > 0:
        print(f"Dataset em: {DATASET_DIR.resolve()}")
        print("\nClasses e quantidades:")
        for split_dir in sorted(DATASET_DIR.iterdir()):
            if split_dir.is_dir():
                for cls_dir in sorted(split_dir.iterdir()):
                    if cls_dir.is_dir():
                        n = len(list(cls_dir.glob("*.jpg")))
                        print(f"  {split_dir.name:6s} / {cls_dir.name:30s} : {n}")
        print("\nPróximo passo: python train_soy_disease.py")
    else:
        print("AVISO: Nenhum crop gerado. Verifique se o ZIP é do formato TFRecord correto.")


if __name__ == "__main__":
    main()
