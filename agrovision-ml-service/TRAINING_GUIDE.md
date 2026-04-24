# AgroVision ML Training Guide - TFLite Compatible

## Overview

Clean training pipeline that produces TFLite-compatible models without augmentation layers embedded in the model.

**Key Points:**
- ✅ Image preprocessing (CLAHE, resize) happens in `prepare_species.py`
- ✅ Data augmentation happens ONLY during training (not saved in model)
- ✅ Final model is 100% TFLite compatible
- ✅ No conversion errors or complex ops

## Pipeline

### Step 1: Prepare Dataset (30-60 min)

```bash
python prepare_species.py --max-per-class 500
```

**What happens:**
- Downloads PlantNet300k from HuggingFace
- Applies CLAHE normalization (lighting equalization)
- Resizes with proportional padding (224×224)
- Saves to `datasets/hf_species/`

**Output:**
- `datasets/hf_species/` (20-40GB)
- `labels_species.json`

---

### Step 2: Train Model (1-2h CPU / 20min GPU)

```bash
python train_species.py
```

**What happens:**

**Phase 1 (20 epochs):**
- MobileNetV2 with frozen base
- Data augmentation applied during training ONLY
- Learning rate: 0.001
- Accuracy: ~75%

**Phase 2 (15 epochs):**
- Fine-tune last 50 layers
- Same augmentation pipeline
- Learning rate: 0.0001
- Accuracy: ~85-90%

**Data Augmentation (training only):**
```
✓ RandomFlip (horizontal + vertical)
✓ RandomRotation (±45°)
✓ RandomZoom (±15%)
✓ RandomTranslation (±10%)
✓ RandomBrightness (±20%)
✓ RandomContrast (±20%)
```

**Output:**
- `model_species.tflite` (10-15 MB)
- `labels_species.json` (class mapping)

---

## Technical Details

### Why This Works

1. **No Augmentation in Model**
   - Augmentation layers are applied via `.map()` on dataset
   - Final model contains only: Input → MobileNetV2 → Dense → Softmax
   - All ops are TFLITE_BUILTINS compatible

2. **TFLite Compatibility**
   - Uses only standard operations
   - No SELECT_TF_OPS needed
   - Smaller model size (~12-15 MB)
   - Faster inference on mobile

3. **Image Preprocessing**
   - CLAHE already applied during `prepare_species.py`
   - Resize already done (224×224)
   - Model receives normalized, ready-to-use images

### Model Architecture

```
Input (224×224×3)
  ↓
MobileNetV2 preprocess
  ↓
MobileNetV2 (ImageNet pretrained)
  ↓
GlobalAveragePooling2D
  ↓
Dropout (0.5)
  ↓
Dense(num_classes, softmax)
  ↓
Output (probabilities)
```

### Conversion to TFLite

Automatic in `train_species.py`:
1. Tries TFLITE_BUILTINS only (recommended)
2. Falls back to SELECT_TF_OPS if needed
3. Applies DEFAULT optimization

---

## Common Issues & Solutions

### Issue: "Memory error during training"
**Solution:** Reduce batch size in `train_species.py`:
```python
BATCH_SIZE = 16  # was 32
```

### Issue: "Out of disk space"
**Solution:** Prepare with fewer images per species:
```bash
python prepare_species.py --max-per-class 300
```

### Issue: "Slow augmentation"
**Solution:** Augmentation happens in parallel. Reduce number of augmentation operations in `get_augmentation_dataset()`.

### Issue: "Model too large for mobile"
**Solution:** Use lighter preprocessing:
```python
IMG_SIZE = 160  # was 224 (reduces by 45%)
```

---

## Files

### Core Scripts
- `prepare_species.py` - Data preparation + CLAHE + resize
- `train_species.py` - Complete training + TFLite conversion

### Output Files
- `model_species.tflite` - Final model (~12 MB)
- `labels_species.json` - Class labels

### Removed Files
- ❌ `convert_only.py` - No longer needed
- ❌ `final_convert.py` - No longer needed
- ❌ `saved_model_species/` - No longer needed
- ❌ `train_log.txt` - No longer needed

---

## Deployment to App

After training completes:

```bash
# Copy model to app
copy model_species.tflite ..\app_tc\assets\models\
copy labels_species.json ..\app_tc\assets\models\

# Start app with new model
cd ..\app_tc
npx expo start
```

---

## Time Breakdown

| Step | Time |
|------|------|
| Install dependencies | 5-10 min |
| Prepare dataset | 30-60 min |
| Train Phase 1 | 30-60 min |
| Train Phase 2 | 30-60 min |
| Convert to TFLite | 1-2 min |
| **TOTAL** | **2-3 hours** |

---

## GPU Acceleration

If you have CUDA:

```bash
pip install tensorflow[and-cuda]==2.15.0
```

This reduces training time to ~20 minutes total.

---

## Troubleshooting

### Check dataset was prepared:
```bash
dir datasets\hf_species
# Should show species folders
```

### Check model was created:
```bash
dir model_species.tflite
# Should be 10-15 MB
```

### Test on mobile with Expo:
```bash
npx expo start
# Scan QR code with Expo Go app
```

---

**Questions? Check the memory file or review the architecture diagrams in README.md**
