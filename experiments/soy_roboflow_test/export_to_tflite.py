"""
Baixa os pesos YOLOv8 treinados no Roboflow e converte para TFLite.

Requer: pip install roboflow ultralytics
Requer: ROBOFLOW_API_KEY no ambiente

Edite as 3 constantes abaixo com seus dados do Roboflow.
"""

import os
import sys
from pathlib import Path

ROBOFLOW_WORKSPACE = "SEU-WORKSPACE"      # ex: "luiz-carlos-xyz"  ← pegar do código de deploy
ROBOFLOW_PROJECT   = "soy-leaf-disease-fivve"
ROBOFLOW_VERSION   = 1

BASE_DIR = Path(__file__).parent


def get_api_key() -> str:
    key = os.environ.get("ROBOFLOW_API_KEY", "")
    if not key:
        print("ERROR: ROBOFLOW_API_KEY não definida.")
        print("  PowerShell: $env:ROBOFLOW_API_KEY='sua_chave'")
        sys.exit(1)
    return key


def download_weights(api_key: str) -> Path:
    try:
        from roboflow import Roboflow
    except ImportError:
        print("ERROR: pip install roboflow")
        sys.exit(1)

    print(f"Baixando pesos de '{ROBOFLOW_PROJECT}' v{ROBOFLOW_VERSION}...")
    rf      = Roboflow(api_key=api_key)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    version = project.version(ROBOFLOW_VERSION)

    # Baixa os pesos YOLOv8 (.pt) na pasta weights/
    weights_dir = BASE_DIR / "weights"
    version.download("yolov8", location=str(weights_dir))

    # Localiza o arquivo .pt
    pt_files = list(weights_dir.rglob("*.pt"))
    if not pt_files:
        print("ERROR: Arquivo .pt não encontrado após download.")
        print(f"Conteúdo de {weights_dir}:")
        for p in weights_dir.rglob("*"):
            print(f"  {p}")
        sys.exit(1)

    pt_path = pt_files[0]
    print(f"Pesos encontrados: {pt_path}")
    return pt_path


def convert_to_tflite(pt_path: Path):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: pip install ultralytics")
        sys.exit(1)

    print(f"\nCarregando modelo: {pt_path}")
    model = YOLO(str(pt_path))

    print("Convertendo para TFLite (int8 quantization)...")
    # Exporta na pasta do .pt, gera arquivo *_saved_model/*.tflite
    model.export(format="tflite", int8=False, imgsz=640)

    tflite_files = list(pt_path.parent.rglob("*.tflite"))
    if tflite_files:
        out = tflite_files[0]
        dest = BASE_DIR / "model_soy_yolo.tflite"
        dest.write_bytes(out.read_bytes())
        print(f"\nTFLite salvo em: {dest}")
        print(f"Tamanho: {dest.stat().st_size / 1_048_576:.1f} MB")
    else:
        print("AVISO: .tflite não encontrado — verifique a pasta weights/")


def main():
    api_key  = get_api_key()
    pt_path  = download_weights(api_key)
    convert_to_tflite(pt_path)

    print("\nPróximos passos:")
    print("  1. Copie model_soy_yolo.tflite para o app")
    print("  2. O modelo YOLO é detecção (bounding boxes), não classificação")
    print("     → integração diferente do modelo atual MobileNetV2")


if __name__ == "__main__":
    main()
