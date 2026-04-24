#!/usr/bin/env python3
"""
Prepare Agricultural Species Dataset from Multiple Sources
- PlantNet 300K (mikehemberger/plantnet300K)
- PlantVillage (ButterChicken98/plantvillage-image-text-pairs)
- Local directory (optional)
- Applies CLAHE + proportional padding
- 500 images per category by default
"""

import os
import argparse
import json
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np
import cv2
from tqdm import tqdm

# Configuration
IMG_SIZE = 224
QUALITY = 85
MIN_IMG_SIZE = 64
OUTPUT_DIR = Path('datasets/hf_species')
MAX_IMAGES_PER_CLASS = 500


def apply_clahe(image_array):
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    to normalize lighting and improve feature visibility
    """
    try:
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return result
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            return clahe.apply(image_array)
    except Exception as e:
        return image_array


def resize_with_padding(image, size=IMG_SIZE):
    """Resize image while preserving aspect ratio with padding"""
    scale = min(size / image.width, size / image.height)
    new_size = (int(image.width * scale), int(image.height * scale))

    image = image.resize(new_size, Image.Resampling.LANCZOS)

    delta_w = size - image.width
    delta_h = size - image.height
    padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))

    image = ImageOps.expand(image, padding, fill=(255, 255, 255))
    return image.crop((0, 0, size, size))


def process_image(image_input, species_name, output_path):
    """
    Process a single image: convert, apply CLAHE, resize, and save
    Input can be PIL Image or file path
    """
    try:
        # Load image if path
        if isinstance(image_input, str):
            pil_image = Image.open(image_input).convert('RGB')
        else:
            pil_image = image_input.convert('RGB') if hasattr(image_input, 'convert') else image_input

        if pil_image.width < MIN_IMG_SIZE or pil_image.height < MIN_IMG_SIZE:
            return False

        img_array = np.array(pil_image, dtype=np.uint8)
        img_array = apply_clahe(img_array)
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        pil_image = Image.fromarray(img_array)
        pil_image = resize_with_padding(pil_image)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        pil_image.save(output_path, 'JPEG', quality=QUALITY, optimize=True)

        return True
    except Exception as e:
        return False


def download_plantnet300k(max_per_class):
    """Download PlantNet 300K dataset from HuggingFace"""
    print("\n[DOWNLOAD] PlantNet 300K Dataset")
    print("=" * 60)

    try:
        from datasets import load_dataset
    except ImportError:
        print("[ERROR] HuggingFace datasets not installed")
        print("[INFO] Install with: pip install datasets")
        return {}

    try:
        print("[LOAD] Loading PlantNet 300K...")
        ds = load_dataset("mikehemberger/plantnet300K", split='train', streaming=True)

        class_counts = {}
        processed = 0
        failed = 0

        for sample in tqdm(ds, desc="Processing PlantNet 300K"):
            try:
                # Get species/label
                species_name = sample.get('species', sample.get('label', f'Species_{processed}'))
                species_name = str(species_name).strip()

                # Skip if we have enough
                if class_counts.get(species_name, 0) >= max_per_class:
                    continue

                # Get image
                image = sample.get('image', None)
                if image is None:
                    failed += 1
                    continue

                # Process and save
                output_path = OUTPUT_DIR / species_name / f"plantnet_{processed:06d}.jpg"

                if process_image(image, species_name, output_path):
                    class_counts[species_name] = class_counts.get(species_name, 0) + 1
                    processed += 1
                else:
                    failed += 1

                # Safety limit
                if processed >= max_per_class * 200:
                    break

            except Exception as e:
                failed += 1
                continue

        print(f"[OK] PlantNet 300K: {processed} images, {len(class_counts)} species")
        print(f"     Failed: {failed}")
        return class_counts

    except Exception as e:
        print(f"[ERROR] PlantNet 300K failed: {e}")
        return {}


def download_plantvillage(max_per_class):
    """Download PlantVillage dataset from HuggingFace"""
    print("\n[DOWNLOAD] PlantVillage Dataset")
    print("=" * 60)

    try:
        from datasets import load_dataset
    except ImportError:
        print("[ERROR] HuggingFace datasets not installed")
        return {}

    try:
        print("[LOAD] Loading PlantVillage...")
        ds = load_dataset("ButterChicken98/plantvillage-image-text-pairs", split='train', streaming=True)

        class_counts = {}
        processed = 0
        failed = 0

        for sample in tqdm(ds, desc="Processing PlantVillage"):
            try:
                # Get label/species
                species_name = sample.get('label', sample.get('species', f'Species_{processed}'))
                species_name = str(species_name).strip()

                # Skip if we have enough
                if class_counts.get(species_name, 0) >= max_per_class:
                    continue

                # Get image
                image = sample.get('image', None)
                if image is None:
                    failed += 1
                    continue

                # Process and save
                output_path = OUTPUT_DIR / species_name / f"plantvillage_{processed:06d}.jpg"

                if process_image(image, species_name, output_path):
                    class_counts[species_name] = class_counts.get(species_name, 0) + 1
                    processed += 1
                else:
                    failed += 1

                # Safety limit
                if processed >= max_per_class * 150:
                    break

            except Exception as e:
                failed += 1
                continue

        print(f"[OK] PlantVillage: {processed} images, {len(class_counts)} species")
        print(f"     Failed: {failed}")
        return class_counts

    except Exception as e:
        print(f"[ERROR] PlantVillage failed: {e}")
        return {}


def load_from_local_directory(source_dir, max_per_class):
    """Load images from local directory structure"""
    print(f"\n[LOCAL] Loading from: {source_dir}")
    print("=" * 60)

    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"[ERROR] Directory not found: {source_dir}")
        return {}

    class_counts = {}
    processed = 0

    # Iterate through species folders
    for species_dir in source_path.iterdir():
        if not species_dir.is_dir():
            continue

        species_name = species_dir.name

        # Get images
        images = (list(species_dir.glob('*.jpg')) +
                 list(species_dir.glob('*.jpeg')) +
                 list(species_dir.glob('*.png')))

        if not images:
            continue

        # Limit per class
        images = images[:max_per_class]

        for img_file in tqdm(images, desc=f"  {species_name}"):
            output_path = OUTPUT_DIR / species_name / f"local_{processed:06d}.jpg"

            if process_image(str(img_file), species_name, output_path):
                class_counts[species_name] = class_counts.get(species_name, 0) + 1
                processed += 1

    print(f"[OK] Local: {processed} images from {len(class_counts)} species")
    return class_counts


def merge_counts(counts_list):
    """Merge counts from multiple sources"""
    merged = {}
    for counts in counts_list:
        for species, count in counts.items():
            merged[species] = merged.get(species, 0) + count
    return merged


def balance_dataset(max_per_class):
    """Check final dataset balance"""
    print("\n[BALANCE] Final Dataset Check")
    print("=" * 60)

    class_counts = {}
    for species_dir in OUTPUT_DIR.iterdir():
        if not species_dir.is_dir():
            continue

        images = list(species_dir.glob('*.jpg'))
        class_counts[species_dir.name] = len(images)

    if not class_counts:
        return {}

    total_images = sum(class_counts.values())
    total_species = len(class_counts)

    print(f"[OK] Dataset Statistics:")
    print(f"      Total species: {total_species}")
    print(f"      Total images: {total_images}")
    print(f"      Avg per species: {total_images / total_species:.0f}")
    print(f"      Min: {min(class_counts.values())}")
    print(f"      Max: {max(class_counts.values())}")

    return class_counts


def save_labels(class_counts):
    """Save labels mapping"""
    labels = {}
    for idx, species in enumerate(sorted(class_counts.keys())):
        labels[idx] = species

    labels_file = OUTPUT_DIR.parent / 'labels_species.json'
    with open(labels_file, 'w', encoding='utf-8') as f:
        json.dump(labels, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVE] Labels: {labels_file}")
    print(f"       Total classes: {len(labels)}")

    return labels_file


def main():
    parser = argparse.ArgumentParser(description='Prepare agricultural dataset from multiple sources')
    parser.add_argument('--max-per-class', type=int, default=MAX_IMAGES_PER_CLASS,
                        help=f'Max images per species (default: {MAX_IMAGES_PER_CLASS})')
    parser.add_argument('--local', type=str, default=None,
                        help='Path to local dataset directory (optional)')
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("[START] Agricultural Dataset Preparation")
    print("=" * 60)
    print(f"[CONFIG] Output: {OUTPUT_DIR}")
    print(f"[CONFIG] Max per species: {args.max_per_class}")
    print(f"[CONFIG] Image size: {IMG_SIZE}x{IMG_SIZE}")
    print(f"[CONFIG] Datasets: PlantNet 300K + PlantVillage + Local (optional)")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_counts_list = []

    # Download PlantNet 300K
    plantnet_counts = download_plantnet300k(args.max_per_class)
    if plantnet_counts:
        all_counts_list.append(plantnet_counts)
    else:
        print("[WARN] PlantNet 300K download failed, continuing...")

    # Download PlantVillage
    plantvillage_counts = download_plantvillage(args.max_per_class)
    if plantvillage_counts:
        all_counts_list.append(plantvillage_counts)
    else:
        print("[WARN] PlantVillage download failed, continuing...")

    # Load local data if provided
    if args.local:
        local_counts = load_from_local_directory(args.local, args.max_per_class)
        if local_counts:
            all_counts_list.append(local_counts)

    # Check if we got any data
    if not all_counts_list:
        print("\n[ERROR] Failed to download any dataset!")
        print("\n[SOLUTION] Options:")
        print("  1. Check internet connection")
        print("  2. Ensure HuggingFace datasets is installed: pip install datasets")
        print("  3. Provide local data: python prepare_species.py --local path/to/data/")
        return

    # Merge and finalize
    final_counts = balance_dataset(args.max_per_class)

    if final_counts:
        labels_file = save_labels(final_counts)

        print("\n" + "=" * 60)
        print("[COMPLETE] Dataset Preparation Done!")
        print("=" * 60)
        print(f"[NEXT] Train the model:")
        print(f"  python train_species.py")
        print()
    else:
        print("[ERROR] No valid images in output directory")


if __name__ == '__main__':
    main()
