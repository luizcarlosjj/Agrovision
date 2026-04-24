#!/usr/bin/env python3
"""
Combine multiple agricultural datasets
Merges images from different sources into single training dataset
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm

# Configuration
OUTPUT_DIR = Path('datasets/combined_agricultural')
SOURCES = [
    # ('path/to/plantnet300k', 'plantnet'),
    # ('path/to/fvhq', 'fvhq'),
    # ('path/to/your_photos', 'custom'),
]

# Species mapping (if different datasets use different names)
SPECIES_MAPPING = {
    'tomato': 'Tomate',
    'potato': 'Batata',
    'corn': 'Milho',
    'maize': 'Milho',
    'bean': 'Feijão',
    'watermelon': 'Melancia',
    'carrot': 'Cenoura',
    'lettuce': 'Alface',
    'cabbage': 'Repolho',
    'pepper': 'Pimentão',
    'onion': 'Cebola',
    'cucumber': 'Pepino',
    'squash': 'Abóbora',
    'pumpkin': 'Abóbora',
    'eggplant': 'Berinjela',
}

def normalize_species_name(name):
    """Convert species name to standard Portuguese name"""
    name_lower = name.lower().strip()
    return SPECIES_MAPPING.get(name_lower, name)

def combine_datasets():
    """Merge multiple datasets into single directory"""

    print("[INFO] Starting dataset combination...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_images = 0
    species_counts = {}

    for source_path, source_name in SOURCES:
        source_path = Path(source_path)

        if not source_path.exists():
            print(f"[WARN] Source not found: {source_path}")
            continue

        print(f"\n[PROCESSING] {source_name}: {source_path}")

        # Iterate through species folders
        for species_dir in source_path.iterdir():
            if not species_dir.is_dir():
                continue

            # Normalize species name
            species_name = normalize_species_name(species_dir.name)
            output_species_dir = OUTPUT_DIR / species_name
            output_species_dir.mkdir(parents=True, exist_ok=True)

            # Copy images
            images = list(species_dir.glob('*.*'))
            valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

            for img_file in tqdm(images, desc=f"  {species_name}"):
                if img_file.suffix.lower() not in valid_extensions:
                    continue

                # Create unique filename to avoid overwrites
                new_name = f"{source_name}_{img_file.name}"
                dest_file = output_species_dir / new_name

                try:
                    shutil.copy2(img_file, dest_file)
                    total_images += 1
                    species_counts[species_name] = species_counts.get(species_name, 0) + 1
                except Exception as e:
                    print(f"    [ERROR] Failed to copy {img_file}: {e}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"[SUMMARY] Dataset Combination Complete")
    print(f"{'='*50}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Total images: {total_images}")
    print(f"Total species: {len(species_counts)}")
    print(f"\nSpecies breakdown:")
    for species, count in sorted(species_counts.items()):
        print(f"  {species}: {count} images")

    print(f"\nNext step: Train with combined dataset")
    print(f"  Edit train_species.py:")
    print(f"  DATASET_DIR = Path('{OUTPUT_DIR}')")

if __name__ == '__main__':
    print("[INFO] Configure SOURCES before running:")
    print("  SOURCES = [")
    print("      ('path/to/plantnet300k', 'plantnet'),")
    print("      ('path/to/fvhq', 'fvhq'),")
    print("      ('path/to/your_photos', 'custom'),")
    print("  ]")
    print()

    if not SOURCES:
        print("[ERROR] Please configure SOURCES first!")
        exit(1)

    combine_datasets()
