#!/usr/bin/env python3
"""Quick test of TFLite model"""

import numpy as np
import tensorflow as tf
from PIL import Image
import json
from pathlib import Path

# Paths
MODEL_PATH = 'assets/models/model_species.tflite'
LABELS_PATH = 'assets/models/labels_species.json'
TEST_IMAGE = 'test_plant.jpg'  # Provide a test image

print("[TEST] Loading TFLite model...")

try:
    # Load interpreter
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    print("[OK] Model loaded!")

    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"[INFO] Input shape: {input_details[0]['shape']}")
    print(f"[INFO] Output shape: {output_details[0]['shape']}")

    # Load labels
    with open(LABELS_PATH, 'r', encoding='utf-8') as f:
        labels = json.load(f)
    print(f"[OK] Loaded {len(labels)} species labels")

    # Test with dummy image
    if not Path(TEST_IMAGE).exists():
        print(f"\n[INFO] Creating dummy test image (224x224)...")
        dummy_img = Image.new('RGB', (224, 224), color=(100, 150, 100))
        dummy_img.save(TEST_IMAGE)

    # Load and preprocess image
    print(f"[INFO] Loading test image: {TEST_IMAGE}")
    img = Image.open(TEST_IMAGE).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Run inference
    print("[RUN] Running inference...")
    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    # Get predictions
    probabilities = output[0]
    top_idx = np.argmax(probabilities)
    top_prob = probabilities[top_idx]

    species_name = labels.get(str(top_idx), f"Unknown ({top_idx})")

    print(f"\n[RESULT] Top prediction:")
    print(f"  Species: {species_name}")
    print(f"  Confidence: {top_prob*100:.2f}%")

    print(f"\n[TOP 5] Predictions:")
    top_5_idx = np.argsort(probabilities)[-5:][::-1]
    for i, idx in enumerate(top_5_idx, 1):
        name = labels.get(str(idx), f"Unknown ({idx})")
        prob = probabilities[idx]
        print(f"  {i}. {name}: {prob*100:.2f}%")

    print(f"\n[SUCCESS] Model is working!")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
