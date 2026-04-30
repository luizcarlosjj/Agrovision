"""
Roboflow Soy Leaf Disease Detection - Isolated Experiment
Model: soy-leaf-disease/1 (https://detect.roboflow.com)
"""

import os
import sys
import json
import base64
import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

ROBOFLOW_API_URL = "https://detect.roboflow.com/soy-leaf-disease/1"
RESULTS_DIR = Path(__file__).parent / "results"


def _get_api_key() -> str:
    key = os.environ.get("ROBOFLOW_API_KEY", "")
    if not key:
        print("ERROR: Environment variable ROBOFLOW_API_KEY is not set.")
        print("  Windows CMD:  set ROBOFLOW_API_KEY=your_key_here")
        print("  Windows PS:   $env:ROBOFLOW_API_KEY='your_key_here'")
        print("  Linux/macOS:  export ROBOFLOW_API_KEY=your_key_here")
        sys.exit(1)
    return key


def predict_image(image_path: str) -> dict:
    """
    Send image to Roboflow API and return prediction result.

    Returns a dict with keys:
      - 'file': original filename
      - 'predictions': list of detection objects (class, confidence, x, y, width, height)
      - 'error': error message string (only present on failure)
    """
    path = Path(image_path)
    result = {"file": path.name, "predictions": []}

    try:
        with open(path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        result["error"] = f"File not found: {image_path}"
        print(f"  [ERROR] {result['error']}")
        return result
    except OSError as e:
        result["error"] = f"Cannot read file: {e}"
        print(f"  [ERROR] {result['error']}")
        return result

    api_key = _get_api_key()
    params = {"api_key": api_key}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = image_b64

    try:
        response = requests.post(
            ROBOFLOW_API_URL,
            params=params,
            data=payload,
            headers=headers,
            timeout=30,
        )
    except requests.exceptions.ConnectionError:
        result["error"] = "Network error: could not connect to Roboflow API. Check your internet connection."
        print(f"  [ERROR] {result['error']}")
        return result
    except requests.exceptions.Timeout:
        result["error"] = "Request timed out after 30 seconds."
        print(f"  [ERROR] {result['error']}")
        return result

    if response.status_code != 200:
        try:
            api_message = response.json().get("message", response.text[:200])
        except Exception:
            api_message = response.text[:200]
        result["error"] = f"API returned HTTP {response.status_code}: {api_message}"
        print(f"  [ERROR] {result['error']}")
        return result

    try:
        data = response.json()
    except ValueError:
        result["error"] = "API returned non-JSON response."
        print(f"  [ERROR] {result['error']}")
        return result

    predictions = data.get("predictions", [])
    result["predictions"] = predictions
    result["image_width"] = data.get("image", {}).get("width")
    result["image_height"] = data.get("image", {}).get("height")

    if predictions:
        for p in predictions:
            print(f"    {p.get('class', '?'):30s}  conf={p.get('confidence', 0):.2%}  "
                  f"box=({p.get('x')}, {p.get('y')}, {p.get('width')}, {p.get('height')})")
    else:
        print("    (no detections)")

    return result


def test_folder(folder_path: str) -> None:
    """
    Run predict_image() on all .jpg and .png files in folder_path.
    Saves aggregated results to results/resultado_{timestamp}.json.
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"ERROR: Folder not found: {folder.resolve()}")
        sys.exit(1)

    images = sorted(
        list(folder.glob("*.jpg")) +
        list(folder.glob("*.jpeg")) +
        list(folder.glob("*.png"))
    )

    if not images:
        print(f"No .jpg / .png images found in: {folder.resolve()}")
        print("Add images to the sample_images/ folder and try again.")
        return

    print(f"Found {len(images)} image(s) in {folder.resolve()}\n")
    print(f"Model: {ROBOFLOW_API_URL}\n")

    all_results = []
    for i, img_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] {img_path.name}")
        result = predict_image(str(img_path))
        all_results.append(result)
        print()

    # Summary
    total = len(all_results)
    with_detections = sum(1 for r in all_results if r.get("predictions"))
    errors = sum(1 for r in all_results if "error" in r)
    print(f"--- Summary ---")
    print(f"  Total images   : {total}")
    print(f"  With detections: {with_detections}")
    print(f"  Errors         : {errors}")

    # Save JSON
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"resultado_{timestamp}.json"

    output = {
        "timestamp": timestamp,
        "model": ROBOFLOW_API_URL,
        "total_images": total,
        "images_with_detections": with_detections,
        "errors": errors,
        "results": all_results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {output_path.resolve()}")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "sample_images"
    test_folder(folder)
