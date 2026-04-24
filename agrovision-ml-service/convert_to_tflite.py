#!/usr/bin/env python3
"""
Convert trained Keras model to TFLite format
Handles both TFLITE_BUILTINS and SELECT_TF_OPS fallback
"""

import tensorflow as tf
from tensorflow import keras
import json
from pathlib import Path

MODEL_PATH = 'model_species.h5'
OUTPUT_TFLITE = Path('model_species.tflite')
LABELS_FILE = Path('labels_species.json')


def convert_to_tflite():
    """Convert Keras model to TFLite"""

    print("[INFO] Loading trained model...")

    # Try to load the model
    if not Path(MODEL_PATH).exists():
        print(f"[ERROR] Model not found: {MODEL_PATH}")
        print("[INFO] Expected model from train_species.py")
        return False

    try:
        model = keras.models.load_model(MODEL_PATH)
        print("[OK] Model loaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

    # Check if labels exist
    if not LABELS_FILE.exists():
        print(f"[WARN] Labels not found: {LABELS_FILE}")
        print("[INFO] Model will work but without class labels")

    print(f"\n[CONVERT] Converting to TFLite...")
    print(f"[INFO] Model input shape: {model.input_shape}")
    print(f"[INFO] Model output shape: {model.output_shape}")

    try:
        # Try conversion with TFLITE_BUILTINS only (best compatibility)
        print("[STEP1] Trying TFLITE_BUILTINS only...")

        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS
        ]
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        tflite_model = converter.convert()

        with open(OUTPUT_TFLITE, 'wb') as f:
            f.write(tflite_model)

        print(f"[OK] TFLite model saved: {OUTPUT_TFLITE}")
        print(f"[INFO] Size: {len(tflite_model) / 1024 / 1024:.2f} MB")
        print(f"[SUCCESS] Conversion complete!")
        return True

    except Exception as e:
        print(f"[WARN] TFLITE_BUILTINS failed: {str(e)[:150]}")
        print(f"[STEP2] Trying with SELECT_TF_OPS fallback...")

        try:
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS,
                tf.lite.OpsSet.SELECT_TF_OPS
            ]
            converter.optimizations = [tf.lite.Optimize.DEFAULT]

            tflite_model = converter.convert()

            with open(OUTPUT_TFLITE, 'wb') as f:
                f.write(tflite_model)

            print(f"[OK] TFLite model saved (with SELECT ops): {OUTPUT_TFLITE}")
            print(f"[INFO] Size: {len(tflite_model) / 1024 / 1024:.2f} MB")
            print(f"[WARN] Model uses SELECT ops - requires TF Select on device")
            print(f"[SUCCESS] Conversion complete!")
            return True

        except Exception as e2:
            print(f"[ERROR] Both methods failed!")
            print(f"[ERROR] {e2}")
            return False


if __name__ == '__main__':
    success = convert_to_tflite()
    exit(0 if success else 1)
