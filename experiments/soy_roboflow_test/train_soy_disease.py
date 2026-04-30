"""
Treina MobileNetV2 no dataset soy-leaf-disease baixado do Roboflow.
Gera: model_soy.keras  |  model_soy.tflite  |  labels_soy.json

Requer: pip install tensorflow pillow
Dataset deve estar em dataset/ (rode download_dataset.py primeiro)
"""

import sys
import json
import shutil
from pathlib import Path

# Verifica TensorFlow antes de importar tudo
try:
    import tensorflow as tf
    print(f"TensorFlow {tf.__version__} carregado.")
except ImportError:
    print("ERROR: TensorFlow não instalado.  pip install tensorflow")
    sys.exit(1)

import numpy as np

# ── Caminhos (todos relativos a este script) ──────────────────────────────────
BASE_DIR     = Path(__file__).parent
DATASET_DIR  = BASE_DIR / "dataset"
TRAIN_DIR    = DATASET_DIR / "train"
VALID_DIR    = DATASET_DIR / "valid"
TEST_DIR     = DATASET_DIR / "test"

MODEL_KERAS  = BASE_DIR / "model_soy.keras"
MODEL_TFLITE = BASE_DIR / "model_soy.tflite"
LABELS_JSON  = BASE_DIR / "labels_soy.json"

# ── Hiperparâmetros ───────────────────────────────────────────────────────────
IMG_SIZE       = (224, 224)
BATCH_SIZE     = 16
EPOCHS_FROZEN  = 20      # backbone congelado
EPOCHS_FINETUNE = 15     # fine-tune top 50 camadas
LEARNING_RATE  = 1e-3
FINETUNE_LR    = 1e-5
UNFREEZE_LAYERS = 50


def check_dataset():
    if not TRAIN_DIR.exists():
        print(f"ERROR: Pasta de treino não encontrada: {TRAIN_DIR}")
        print("  Execute primeiro: python download_dataset.py")
        sys.exit(1)

    classes = sorted([d.name for d in TRAIN_DIR.iterdir() if d.is_dir()])
    if not classes:
        print("ERROR: Nenhuma classe encontrada em dataset/train/")
        sys.exit(1)

    return classes


def build_datasets(classes):
    n_classes = len(classes)
    print(f"\n{n_classes} classes encontradas: {classes}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        str(TRAIN_DIR),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=True,
        seed=42,
        class_names=classes,
    )

    valid_ds = tf.keras.utils.image_dataset_from_directory(
        str(VALID_DIR) if VALID_DIR.exists() else str(TRAIN_DIR),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        shuffle=False,
        class_names=classes,
    )

    # Augmentação e normalização
    augment = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.15),
        tf.keras.layers.RandomBrightness(0.1),
    ], name="augmentation")

    normalize = tf.keras.layers.Rescaling(1.0 / 255)

    train_ds = (
        train_ds
        .map(lambda x, y: (augment(x, training=True), y), num_parallel_calls=tf.data.AUTOTUNE)
        .map(lambda x, y: (normalize(x), y), num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )

    valid_ds = (
        valid_ds
        .map(lambda x, y: (normalize(x), y), num_parallel_calls=tf.data.AUTOTUNE)
        .prefetch(tf.data.AUTOTUNE)
    )

    return train_ds, valid_ds, n_classes


def build_model(n_classes):
    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False

    inputs  = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x       = base(inputs, training=False)
    x       = tf.keras.layers.GlobalAveragePooling2D()(x)
    x       = tf.keras.layers.Dropout(0.3)(x)
    x       = tf.keras.layers.Dense(256, activation="relu")(x)
    x       = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(n_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs, name="soy_disease_classifier")
    return model, base


def train(model, base, train_ds, valid_ds):
    # Fase 1: backbone congelado
    print(f"\n=== FASE 1: backbone congelado ({EPOCHS_FROZEN} épocas) ===")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_1 = [
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-6),
    ]

    model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=EPOCHS_FROZEN,
        callbacks=callbacks_1,
        verbose=1,
    )

    # Fase 2: fine-tune últimas camadas
    print(f"\n=== FASE 2: fine-tune top {UNFREEZE_LAYERS} camadas ({EPOCHS_FINETUNE} épocas) ===")
    base.trainable = True
    for layer in base.layers[:-UNFREEZE_LAYERS]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(FINETUNE_LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_2 = [
        tf.keras.callbacks.EarlyStopping(patience=7, restore_best_weights=True, monitor="val_accuracy"),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, min_lr=1e-7),
        tf.keras.callbacks.ModelCheckpoint(
            str(MODEL_KERAS), save_best_only=True, monitor="val_accuracy", verbose=1
        ),
    ]

    model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=EPOCHS_FINETUNE,
        callbacks=callbacks_2,
        verbose=1,
    )

    return model


def evaluate(model, classes):
    if not TEST_DIR.exists():
        print("Pasta test/ não encontrada, pulando avaliação final.")
        return

    normalize = tf.keras.layers.Rescaling(1.0 / 255)
    test_ds = tf.keras.utils.image_dataset_from_directory(
        str(TEST_DIR),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="categorical",
        class_names=classes,
    )
    test_ds = test_ds.map(lambda x, y: (normalize(x), y)).prefetch(tf.data.AUTOTUNE)

    loss, acc = model.evaluate(test_ds, verbose=1)
    print(f"\nTest accuracy: {acc:.2%}   loss: {loss:.4f}")


def save_keras(model):
    model.save(str(MODEL_KERAS))
    print(f"Modelo Keras salvo: {MODEL_KERAS}")


def convert_tflite():
    print("\nConvertendo para TFLite (quantização dinâmica)...")
    model = tf.keras.models.load_model(str(MODEL_KERAS))
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    with open(MODEL_TFLITE, "wb") as f:
        f.write(tflite_model)

    size_mb = MODEL_TFLITE.stat().st_size / 1_048_576
    print(f"TFLite salvo: {MODEL_TFLITE}  ({size_mb:.1f} MB)")


def save_labels(classes):
    labels = {str(i): cls for i, cls in enumerate(classes)}
    with open(LABELS_JSON, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)
    print(f"Labels salvo: {LABELS_JSON}")


def main():
    print("=== AgroVision – Treino: Doenças de Soja ===\n")

    classes   = check_dataset()
    train_ds, valid_ds, n_classes = build_datasets(classes)

    model, base = build_model(n_classes)
    model.summary(line_length=80)

    model = train(model, base, train_ds, valid_ds)
    evaluate(model, classes)

    save_keras(model)
    save_labels(classes)
    convert_tflite()

    print("\n=== Treinamento concluído ===")
    print(f"  Keras  : {MODEL_KERAS}")
    print(f"  TFLite : {MODEL_TFLITE}")
    print(f"  Labels : {LABELS_JSON}")
    print("\nPara usar no app: copie model_soy.tflite e labels_soy.json para")
    print("  agrovision-ml-service/  e  src/assets/models/")


if __name__ == "__main__":
    main()
