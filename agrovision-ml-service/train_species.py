#!/usr/bin/env python3
"""
Train Species Identification Model with TensorFlow/Keras (TFLite-Compatible)
- MobileNetV2 base (ImageNet pretrained)
- Data augmentation ONLY during training (not in model)
- Two-phase training: frozen base + fine-tune
- Clean TFLite export without augmentation layers
"""

import os
import json
import argparse
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import mobilenet_v2

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_FROZEN = 20
EPOCHS_FINETUNE = 15
FINE_TUNE_LAYERS = 50
DATASET_DIR = Path('datasets/hf_species')
MODEL_OUTPUT = Path('model_species.tflite')
KERAS_MODEL_OUTPUT = Path('model_species.keras')
LABELS_OUTPUT = Path('labels_species.json')


def get_augmentation_dataset(base_dataset):
    """
    Create augmented dataset pipeline for training only
    This augmentation is NOT saved in the model (training-only)
    """
    augmentation = keras.Sequential([
        layers.RandomFlip('horizontal_and_vertical'),
        layers.RandomRotation(0.25),
        layers.RandomZoom(0.15),
        layers.RandomTranslation(0.1, 0.1),
        layers.RandomBrightness(0.2),
        layers.RandomContrast(0.2),
    ], name='augmentation')

    # Apply augmentation to dataset
    def augment_fn(image, label):
        return augmentation(image, training=True), label

    return base_dataset.map(augment_fn, num_parallel_calls=tf.data.AUTOTUNE)


def build_model(num_classes):
    """
    Build MobileNetV2 model - CLEAN, no augmentation layers
    This model is TFLite-compatible
    """
    # Input
    inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))

    # Preprocess for MobileNetV2
    preprocessed = mobilenet_v2.preprocess_input(inputs)

    # Base MobileNetV2 (pretrained on ImageNet)
    base_model = mobilenet_v2.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )

    # Freeze base model initially
    base_model.trainable = False

    # Extract features
    features = base_model(preprocessed, training=False)

    # Global average pooling
    pooled = layers.GlobalAveragePooling2D()(features)

    # Dense layers for classification
    dropout = layers.Dropout(0.5)(pooled)
    outputs = layers.Dense(num_classes, activation='softmax')(dropout)

    # Build model
    model = models.Model(inputs=inputs, outputs=outputs, name='species_classifier')
    return model, base_model


def train_model(dataset_dir=DATASET_DIR):
    """
    Train species classification model with TFLite compatibility
    """
    print("[START] Species Classification Model Training")
    print("=" * 50)

    # Validate dataset directory
    if not dataset_dir.exists():
        print(f"[ERROR] Dataset directory not found: {dataset_dir}")
        print(f"   Run: python prepare_species.py --max-per-class 500")
        return

    # Get number of classes
    classes = sorted([d.name for d in dataset_dir.iterdir() if d.is_dir()])
    num_classes = len(classes)
    print(f"[INFO] Found {num_classes} species classes")

    if num_classes < 2:
        print("[ERROR] Need at least 2 classes")
        return

    # Create image datasets
    print(f"\n[LOAD] Loading images from {dataset_dir}...")

    train_dataset = image_dataset_from_directory(
        dataset_dir,
        seed=42,
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        label_mode='categorical',
    )

    # Create augmented dataset for training
    augmented_dataset = get_augmentation_dataset(train_dataset)

    print(f"[OK] Loaded {len(train_dataset)} batches")

    # Build model
    print(f"\n[BUILD] Building MobileNetV2 model (TFLite-compatible)...")
    model, base_model = build_model(num_classes)
    print(f"[INFO] Model layers: {len(model.layers)}")
    print(f"[INFO] Trainable params: {model.count_params():,}")

    # Phase 1: Train with frozen base
    print(f"\n[PHASE1] Phase 1: Training head layers (frozen base)")
    print(f"   Epochs: {EPOCHS_FROZEN}")
    print(f"   Batch size: {BATCH_SIZE}")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history_frozen = model.fit(
        augmented_dataset,
        epochs=EPOCHS_FROZEN,
        verbose=1,
    )

    # Phase 2: Fine-tune last layers
    print(f"\n[PHASE2] Phase 2: Fine-tuning last {FINE_TUNE_LAYERS} layers")
    print(f"   Epochs: {EPOCHS_FINETUNE}")

    base_model.trainable = True
    for layer in base_model.layers[:-FINE_TUNE_LAYERS]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history_finetune = model.fit(
        augmented_dataset,
        epochs=EPOCHS_FINETUNE,
        verbose=1,
    )

    # Save full Keras model (needed for Grad-CAM / XAI backend — gradients are not exposed by TFLite)
    print(f"\n[SAVE] Saving Keras model for XAI backend...")
    model.save(KERAS_MODEL_OUTPUT)
    print(f"[OK] Keras model saved: {KERAS_MODEL_OUTPUT}")

    # Convert to TFLite
    print(f"\n[CONVERT] Converting to TFLite (TFLITE_BUILTINS only)...")

    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS
        ]
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        print("[INFO] Converting...")
        tflite_model = converter.convert()

        with open(MODEL_OUTPUT, 'wb') as f:
            f.write(tflite_model)

        print(f"[OK] TFLite model saved: {MODEL_OUTPUT}")
        print(f"  Size: {len(tflite_model) / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"[WARN] Conversion failed: {str(e)[:200]}")
        print(f"[INFO] Trying with SELECT_TF_OPS...")

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]

        tflite_model = converter.convert()

        with open(MODEL_OUTPUT, 'wb') as f:
            f.write(tflite_model)

        print(f"[OK] TFLite model saved (with SELECT ops): {MODEL_OUTPUT}")
        print(f"  Size: {len(tflite_model) / 1024 / 1024:.2f} MB")

    # Save labels mapping
    labels = {idx: class_name for idx, class_name in enumerate(classes)}
    with open(LABELS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(labels, f, indent=2, ensure_ascii=False)

    print(f"[OK] Labels saved: {LABELS_OUTPUT}")

    # Training summary
    print(f"\n[DONE] Training complete!")
    print(f"   Model: {MODEL_OUTPUT}")
    print(f"   Labels: {LABELS_OUTPUT}")
    print(f"   Classes: {num_classes}")
    print(f"   Phase 1 accuracy: {history_frozen.history['accuracy'][-1]:.4f}")
    print(f"   Phase 2 accuracy: {history_finetune.history['accuracy'][-1]:.4f}")

    print(f"\n[NEXT] Copy to app:")
    print(f"   copy {MODEL_OUTPUT} ..\\app_tc\\assets\\models\\")
    print(f"   copy {LABELS_OUTPUT} ..\\app_tc\\assets\\models\\")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train species classification model')
    parser.add_argument('--model', choices=['species'], default='species',
                        help='Model type to train (currently species only)')
    args = parser.parse_args()

    train_model()
