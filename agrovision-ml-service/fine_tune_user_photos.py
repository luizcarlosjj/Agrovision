#!/usr/bin/env python3
"""
Fine-tune TFLite model with user-collected photos
Lightweight fine-tuning for continuous learning
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
from pathlib import Path
import numpy as np

# Configuration
USER_PHOTOS_DIR = Path('user_training_data')  # Where app stores photos
EXISTING_MODEL = Path('model_species.tflite')
EXISTING_LABELS = Path('labels_species.json')
OUTPUT_MODEL = Path('model_species_finetuned.tflite')

IMG_SIZE = 224
FINE_TUNE_EPOCHS = 5  # Fewer epochs since we're fine-tuning
BATCH_SIZE = 8


def prepare_user_dataset():
    """
    Prepare dataset from user photos
    Expected structure:
    user_training_data/
      ├─ Tomate/
      │  ├─ photo1.jpg
      │  └─ photo2.jpg
      ├─ Batata/
      └─ ...
    """

    print("[PREP] Loading user training data...")

    if not USER_PHOTOS_DIR.exists():
        print(f"[ERROR] User data directory not found: {USER_PHOTOS_DIR}")
        print(f"[INFO] Create this structure:")
        print(f"  {USER_PHOTOS_DIR}/")
        print(f"    ├─ Tomate/")
        print(f"    ├─ Batata/")
        print(f"    └─ ...")
        return None

    # Load labels to know existing classes
    try:
        with open(EXISTING_LABELS, 'r', encoding='utf-8') as f:
            labels = json.load(f)
        print(f"[OK] Loaded {len(labels)} existing classes")
    except Exception as e:
        print(f"[ERROR] Failed to load labels: {e}")
        return None

    # Create image dataset from user photos
    try:
        dataset = tf.keras.preprocessing.image_dataset_from_directory(
            USER_PHOTOS_DIR,
            seed=42,
            image_size=(IMG_SIZE, IMG_SIZE),
            batch_size=BATCH_SIZE,
            label_mode='int',
        )
        print(f"[OK] Loaded user photos dataset")
        return dataset

    except Exception as e:
        print(f"[ERROR] Failed to load user photos: {e}")
        return None


def load_tflite_model():
    """Load existing TFLite model for conversion"""

    print("[LOAD] Loading existing TFLite model...")

    if not EXISTING_MODEL.exists():
        print(f"[ERROR] Model not found: {EXISTING_MODEL}")
        return None

    try:
        # For TFLite, we need to convert back to SavedModel format
        # This is a limitation - we'll use the Keras model instead
        print("[INFO] Using Keras model for fine-tuning")
        print("[WARN] Ensure you have the Keras model saved")
        return None

    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None


def fine_tune_model(dataset):
    """Fine-tune model with user data"""

    print("[TRAIN] Starting fine-tuning...")
    print(f"[INFO] Epochs: {FINE_TUNE_EPOCHS}")
    print(f"[INFO] Batch size: {BATCH_SIZE}")

    print("[WARN] NOTE: This requires the original Keras model")
    print("       Not the TFLite version (limitation)")
    print("       Solution: Keep .h5 file alongside .tflite")

    print("\n[RECOMMENDED] Use this workflow:")
    print("  1. Save model after training: model.save('model_species.h5')")
    print("  2. Convert to TFLite: model_species.tflite")
    print("  3. For fine-tuning, load .h5 file")
    print("  4. Fine-tune and save both .h5 and .tflite")


def main():
    print("[START] Fine-tuning Pipeline for User Photos")
    print("=" * 60)

    # Step 1: Prepare user data
    dataset = prepare_user_dataset()
    if dataset is None:
        print("[ERROR] Cannot proceed without user data")
        return

    # Step 2: Fine-tune model
    fine_tune_model(dataset)

    print("\n[INFO] For now, workflow is:")
    print("  1. User takes photos → saved to user_training_data/")
    print("  2. Run this script")
    print("  3. Model gets fine-tuned")
    print("  4. New TFLite exported")
    print("  5. App reloads updated model")


if __name__ == '__main__':
    main()
