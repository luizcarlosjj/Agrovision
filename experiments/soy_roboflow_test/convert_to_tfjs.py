"""
Converte model_soy.keras para TensorFlow.js, gerando os arquivos que o app
mobile carrega via @tensorflow/tfjs-react-native.

Saída em: src/assets/models/tfjs_model/
  model.json               ← arquitetura + manifest de pesos
  group1-shard1of1.bin     ← pesos (único shard para modelos < 100 MB)

Requer: pip install tensorflowjs tensorflow
"""

import sys
from pathlib import Path

try:
    import tensorflowjs as tfjs
    import tensorflow as tf
except ImportError:
    print("ERROR: execute  pip install tensorflowjs tensorflow")
    sys.exit(1)

EXPERIMENT_DIR = Path(__file__).parent
REPO_ROOT      = EXPERIMENT_DIR.parent.parent
MODEL_PATH     = EXPERIMENT_DIR / "model_soy.keras"
OUTPUT_PATH    = REPO_ROOT / "src" / "assets" / "models" / "tfjs_model"


def main():
    if not MODEL_PATH.exists():
        print(f"ERROR: modelo não encontrado: {MODEL_PATH}")
        print("  Execute train_soy_disease.py primeiro.")
        sys.exit(1)

    print(f"Carregando {MODEL_PATH.name}...")
    model = tf.keras.models.load_model(str(MODEL_PATH))
    print(f"  Input shape : {model.input_shape}")
    print(f"  Output shape: {model.output_shape}")
    print(f"  Parâmetros  : {model.count_params():,}")

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    print(f"\nConvertendo para TFJS em {OUTPUT_PATH}...")

    tfjs.converters.save_keras_model(
        model,
        str(OUTPUT_PATH),
        weight_shard_size_bytes=100 * 1024 * 1024,  # único shard (até 100 MB)
    )

    print("\nArquivos gerados:")
    for f in sorted(OUTPUT_PATH.iterdir()):
        print(f"  {f.name:<40s}  {f.stat().st_size / 1024:>8.0f} KB")

    print("\nPróximos passos:")
    print("  1. cd ../..   (pasta raiz do projeto Agrovision)")
    print("  2. npm install @tensorflow/tfjs @tensorflow/tfjs-react-native expo-gl expo-asset expo-image-manipulator")
    print("  3. npx expo start")


if __name__ == "__main__":
    main()
