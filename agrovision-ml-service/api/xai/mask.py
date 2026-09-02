"""
Binary masks for the Attention Leakage metric.

Two strategies are provided:
  1. fixed — a centered bounding box covering a given fraction of the image
  2. green — segmentation by green-hue threshold in HSV, followed by
     morphological cleanup; the enclosing bounding box of the largest blob
     is used.
  3. manual — user-provided bbox (x, y, w, h) in pixel coordinates.

All functions return a uint8 ndarray of shape (H, W) with values in {0, 1}
and, when relevant, the bbox used (x, y, w, h) in pixel coordinates.
"""

from typing import Optional, Tuple

import cv2
import numpy as np


BBox = Tuple[int, int, int, int]  # (x, y, w, h)


def _clamp_bbox(bbox: BBox, image_shape: Tuple[int, int]) -> BBox:
    h, w = image_shape[:2]
    x, y, bw, bh = bbox
    x = max(0, min(w - 1, int(x)))
    y = max(0, min(h - 1, int(y)))
    bw = max(1, min(w - x, int(bw)))
    bh = max(1, min(h - y, int(bh)))
    return x, y, bw, bh


def fixed_center_bbox(image_shape: Tuple[int, int], coverage: float = 0.8) -> BBox:
    """Centered bbox covering `coverage` of each dimension (default 80%)."""
    coverage = max(0.1, min(1.0, float(coverage)))
    h, w = image_shape[:2]
    bw = int(round(w * coverage))
    bh = int(round(h * coverage))
    x = (w - bw) // 2
    y = (h - bh) // 2
    return _clamp_bbox((x, y, bw, bh), image_shape)


def green_segmentation_bbox(
    image_bgr: np.ndarray,
    min_area_ratio: float = 0.02,
) -> Optional[BBox]:
    """
    Segment green-ish regions in the image and return the bbox of the largest
    connected component. Returns None if no sufficiently-large blob is found.
    """
    if image_bgr is None or image_bgr.size == 0:
        return None

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    lower = np.array([25, 40, 70], dtype=np.uint8)
    upper = np.array([95, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    # Morphological cleanup: remove tiny noise, close small holes.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return None

    # stats[0] is the background; find the largest foreground component.
    areas = stats[1:, cv2.CC_STAT_AREA]
    if areas.size == 0:
        return None
    largest_idx = 1 + int(np.argmax(areas))
    h, w = mask.shape[:2]
    if stats[largest_idx, cv2.CC_STAT_AREA] < min_area_ratio * h * w:
        return None

    x = int(stats[largest_idx, cv2.CC_STAT_LEFT])
    y = int(stats[largest_idx, cv2.CC_STAT_TOP])
    bw = int(stats[largest_idx, cv2.CC_STAT_WIDTH])
    bh = int(stats[largest_idx, cv2.CC_STAT_HEIGHT])
    return _clamp_bbox((x, y, bw, bh), mask.shape)


def green_segmentation_mask(
    image_bgr: np.ndarray,
    min_area_ratio: float = 0.02,
) -> Optional[Tuple[np.ndarray, BBox]]:
    """
    Segment green-ish regions and return (pixel_mask, bbox) for the largest
    connected component, or None if no sufficiently-large blob is found.

    pixel_mask: uint8 (H, W) — 1 on pixels of the largest green component,
    0 elsewhere. More precise than converting a bbox back to a rectangle.
    bbox: enclosing bounding box (x, y, w, h) used for overlay drawing.
    """
    if image_bgr is None or image_bgr.size == 0:
        return None

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    # V_min=70 excludes the dark-green augmentation background (V=60 in OpenCV HSV).
    # S_min=40 improves selectivity without cutting healthy leaf tissue.
    lower = np.array([25, 40, 70], dtype=np.uint8)
    upper = np.array([95, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return None

    areas = stats[1:, cv2.CC_STAT_AREA]
    if areas.size == 0:
        return None
    largest_idx = 1 + int(np.argmax(areas))
    h, w = mask.shape[:2]
    if stats[largest_idx, cv2.CC_STAT_AREA] < min_area_ratio * h * w:
        return None

    pixel_mask = (labels == largest_idx).astype(np.uint8)

    x = int(stats[largest_idx, cv2.CC_STAT_LEFT])
    y = int(stats[largest_idx, cv2.CC_STAT_TOP])
    bw = int(stats[largest_idx, cv2.CC_STAT_WIDTH])
    bh = int(stats[largest_idx, cv2.CC_STAT_HEIGHT])
    bbox = _clamp_bbox((x, y, bw, bh), mask.shape)

    return pixel_mask, bbox


def create_mask_from_bbox(image_shape: Tuple[int, int], bbox: BBox) -> np.ndarray:
    """Binary mask (H, W) uint8 with 1s inside `bbox` and 0s outside."""
    h, w = image_shape[:2]
    x, y, bw, bh = _clamp_bbox(bbox, image_shape)
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y:y + bh, x:x + bw] = 1
    return mask


def parse_bbox_string(s: str) -> BBox:
    """Parse 'x,y,w,h' (ints) into a bbox tuple."""
    parts = [p.strip() for p in s.split(",")]
    if len(parts) != 4:
        raise ValueError(f"bbox must be 'x,y,w,h', got: {s!r}")
    x, y, bw, bh = (int(float(p)) for p in parts)
    return (x, y, bw, bh)
