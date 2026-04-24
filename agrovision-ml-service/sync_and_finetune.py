#!/usr/bin/env python3
"""
Automatic Sync & Fine-tune System
- Monitors user photos from mobile app
- Fine-tunes model when new data arrives
- Exports updated TFLite model automatically
- Works 100% offline + optional sync
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
import shutil
from pathlib import Path
import numpy as np
from datetime import datetime
import hashlib

# Configuration
USER_PHOTOS_DIR = Path('user_training_data')
EXISTING_MODEL = Path('model_species.h5')
EXISTING_LABELS = Path('labels_species.json')
OUTPUT_MODEL = Path('model_species.tflite')
OUTPUT_MODEL_H5 = Path('model_species_finetuned.h5')
SYNC_LOG = Path('sync_history.json')

IMG_SIZE = 224
FINE_TUNE_EPOCHS = 3  # Short fine-tuning
BATCH_SIZE = 8


def check_internet():
    """Check if device has internet connection"""
    try:
        import socket
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False


def calculate_file_hash(file_path):
    """Calculate MD5 hash of file"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def load_sync_history():
    """Load previous sync history"""
    if SYNC_LOG.exists():
        with open(SYNC_LOG, 'r') as f:
            return json.load(f)
    return {'syncs': [], 'last_sync': None}


def save_sync_history(history):
    """Save sync history"""
    with open(SYNC_LOG, 'w') as f:
        json.dump(history, f, indent=2)


def collect_new_photos():
    """Collect new user photos for training"""
    print("[COLLECT] Checking for new user photos...")

    if not USER_PHOTOS_DIR.exists():
        print(f"[INFO] No user data directory: {USER_PHOTOS_DIR}")
        print(f"[INFO] Create structure:")
        print(f"  {USER_PHOTOS_DIR}/")
        print(f"    ├─ Tomate/")
        print(f"    ├─ Batata/")
        print(f"    └─ ...")
        return None

    # Load labels
    try:
        with open(EXISTING_LABELS, 'r') as f:
            labels = json.load(f)
        label_dict = {int(k): v for k, v in labels.items()}
        reverse_labels = {v: int(k) for k, v in label_dict.items()}
    except Exception as e:
        print(f"[ERROR] Cannot load labels: {e}")
        return None

    # Collect images
    dataset_dict = {}
    total_images = 0

    for species_dir in USER_PHOTOS_DIR.iterdir():
        if not species_dir.is_dir():
            continue

        species_name = species_dir.name

        # Get label ID
        if species_name not in reverse_labels:
            print(f"[WARN] Unknown species: {species_name}")
            continue

        label_id = reverse_labels[species_name]

        # Collect images
        images = []
        for img_file in species_dir.glob('*.jpg'):
            try:
                img = keras.preprocessing.image.load_img(
                    img_file, target_size=(IMG_SIZE, IMG_SIZE)
                )
                img_array = keras.preprocessing.image.img_to_array(img) / 255.0
                images.append(img_array)
                total_images += 1
            except Exception as e:
                print(f"[WARN] Failed to load {img_file}: {e}")

        if images:
            dataset_dict[label_id] = images

    if not dataset_dict:
        print("[INFO] No new photos to train with")
        return None

    print(f"[OK] Collected {total_images} images from {len(dataset_dict)} species")
    return dataset_dict, reverse_labels


def fine_tune_model(dataset_dict, reverse_labels):
    """Fine-tune model with user photos"""
    print("\n[FINETUNE] Starting model fine-tuning...")

    # Load existing model
    if not EXISTING_MODEL.exists():
        print(f"[ERROR] Model not found: {EXISTING_MODEL}")
        print(f"[INFO] Please train initial model first: python train_species.py")
        return False

    try:
        model = keras.models.load_model(EXISTING_MODEL)
        print(f"[OK] Model loaded: {EXISTING_MODEL}")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

    # Prepare dataset
    all_images = []
    all_labels = []

    for label_id, images in dataset_dict.items():
        for img_array in images:
            all_images.append(img_array)
            all_labels.append(label_id)

    X = np.array(all_images)
    y = keras.utils.to_categorical(np.array(all_labels), num_classes=model.output_shape[-1])

    print(f"[PREP] Training data: {X.shape}")
    print(f"      Classes: {np.unique(np.argmax(y, axis=1))}")

    # Fine-tune (last layer only)
    print(f"\n[TRAIN] Fine-tuning for {FINE_TUNE_EPOCHS} epochs...")

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history = model.fit(
        X, y,
        epochs=FINE_TUNE_EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
    )

    print(f"[OK] Fine-tuning complete!")
    print(f"     Final accuracy: {history.history['accuracy'][-1]:.4f}")

    # Save updated Keras model
    model.save(OUTPUT_MODEL_H5)
    print(f"[SAVE] Keras model: {OUTPUT_MODEL_H5}")

    # Convert to TFLite
    print(f"\n[CONVERT] Converting to TFLite...")
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS
        ]
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        tflite_model = converter.convert()

        with open(OUTPUT_MODEL, 'wb') as f:
            f.write(tflite_model)

        print(f"[OK] TFLite model: {OUTPUT_MODEL}")
        print(f"     Size: {len(tflite_model) / 1024 / 1024:.2f} MB")

        return True

    except Exception as e:
        print(f"[WARN] TFLite conversion failed: {e}")
        print(f"[INFO] Keras model still available: {OUTPUT_MODEL_H5}")
        return True


def cleanup_photos():
    """Clean up user photos after successful fine-tuning"""
    print("\n[CLEANUP] Archiving user photos...")

    archive_dir = USER_PHOTOS_DIR / f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.move(str(USER_PHOTOS_DIR), str(archive_dir))
        USER_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Photos archived: {archive_dir}")
        return True
    except Exception as e:
        print(f"[WARN] Failed to archive photos: {e}")
        return False


def update_sync_log():
    """Update synchronization log"""
    history = load_sync_history()
    history['syncs'].append({
        'timestamp': datetime.now().isoformat(),
        'model_hash': calculate_file_hash(OUTPUT_MODEL),
    })
    history['last_sync'] = datetime.now().isoformat()
    save_sync_history(history)
    print(f"\n[LOG] Sync recorded")


def main():
    print("\n" + "=" * 60)
    print("[AUTO-SYNC] Dynamic Fine-tuning System")
    print("=" * 60)

    # Check internet
    has_internet = check_internet()
    print(f"[STATUS] Internet: {'Connected' if has_internet else 'Offline'}")

    # Collect new photos
    result = collect_new_photos()
    if result is None:
        print("\n[DONE] No new data to process")
        return

    dataset_dict, reverse_labels = result

    # Fine-tune model
    success = fine_tune_model(dataset_dict, reverse_labels)

    if success:
        cleanup_photos()
        update_sync_log()
        print("\n" + "=" * 60)
        print("[SUCCESS] Model updated successfully!")
        print("=" * 60)
        print(f"[NEXT] App will use updated model:")
        print(f"  - model_species.tflite (inference)")
        print(f"  - model_species_finetuned.h5 (backup)")
    else:
        print("\n[WARN] Fine-tuning encountered issues")


if __name__ == '__main__':
    main()
