"""
Converte model_soy.keras para formato TensorFlow.js SEM precisar do pacote tensorflowjs.
Usa apenas tensorflow e numpy (já instalados no venv_agro).

Saída:
  src/assets/models/tfjs_model/model.json
  src/assets/models/tfjs_model/group1-shard1of1.bin

Uso: venv_agro/Scripts/python.exe convert_to_tfjs_manual.py
"""

import json
import struct
import sys
from pathlib import Path

try:
    import numpy as np
    import tensorflow as tf
except ImportError:
    print("ERROR: pip install tensorflow numpy")
    sys.exit(1)

EXPERIMENT_DIR = Path(__file__).parent
REPO_ROOT      = EXPERIMENT_DIR.parent.parent
MODEL_PATH     = EXPERIMENT_DIR / "model_soy.keras"
OUTPUT_DIR     = REPO_ROOT / "src" / "assets" / "models" / "tfjs_model"
SHARD_NAME     = "group1-shard1of1.bin"


def keras_to_tfjs_dtype(dtype) -> str:
    mapping = {
        "float32": "float32",
        "float16": "float16",
        "int32": "int32",
        "bool": "bool",
        "complex64": "complex64",
    }
    return mapping.get(str(dtype), "float32")


def main():
    if not MODEL_PATH.exists():
        print(f"ERROR: {MODEL_PATH} não encontrado. Execute train_soy_disease.py primeiro.")
        sys.exit(1)

    print(f"Carregando {MODEL_PATH.name}...")
    model = tf.keras.models.load_model(str(MODEL_PATH))
    print(f"  Classes: {model.output_shape[-1]}  |  Params: {model.count_params():,}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Coleta todos os pesos ──────────────────────────────────────────────
    weight_entries = []
    all_bytes = bytearray()

    for layer in model.layers:
        weights = layer.weights
        if not weights:
            continue
        for w in weights:
            arr   = w.numpy().astype(np.float32)
            raw   = arr.tobytes()
            entry = {
                "name": w.name,
                "shape": list(arr.shape),
                "dtype": keras_to_tfjs_dtype(arr.dtype),
            }
            weight_entries.append(entry)
            all_bytes.extend(raw)

    # ── 2. Salva o arquivo .bin ───────────────────────────────────────────────
    bin_path = OUTPUT_DIR / SHARD_NAME
    with open(bin_path, "wb") as f:
        f.write(all_bytes)
    print(f"Pesos salvos: {bin_path.name}  ({len(all_bytes) / 1024 / 1024:.1f} MB)")

    # ── 3. Gera model.json ────────────────────────────────────────────────────
    model_json = {
        "format": "layers-model",
        "generatedBy": f"tensorflow {tf.__version__}",
        "convertedBy": "convert_to_tfjs_manual.py",
        "modelTopology": json.loads(model.to_json()),
        "weightsManifest": [
            {
                "paths": [SHARD_NAME],
                "weights": weight_entries,
            }
        ],
    }

    json_path = OUTPUT_DIR / "model.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(model_json, f, separators=(",", ":"))
    print(f"Manifesto salvo: {json_path.name}  ({json_path.stat().st_size / 1024:.0f} KB)")

    # ── 4. Resumo ─────────────────────────────────────────────────────────────
    print(f"\nArquivos em {OUTPUT_DIR}:")
    for p in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {p.name:<40s}  {p.stat().st_size / 1024:>8.0f} KB")

    print("\nConversão concluída. Próximo passo: npx expo start")


if __name__ == "__main__":
    main()
