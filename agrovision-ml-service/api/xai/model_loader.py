"""
Model loader singleton for the XAI backend.

Loads the Keras model (.keras or .h5) once and keeps it in memory for
subsequent inference + Grad-CAM computation. Labels are loaded from the
JSON mapping produced by train_species.py.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import tensorflow as tf
import tf_keras as keras


DEFAULT_MODEL_CANDIDATES = [
    Path("model_species.keras"),
    Path("model_species.h5"),
    Path("../model_species.keras"),
    Path("../model_species.h5"),
]

DEFAULT_LABELS_CANDIDATES = [
    Path("labels_species.json"),
    Path("../labels_species.json"),
]


class ModelRegistry:
    def __init__(self) -> None:
        self._model: Optional[keras.Model] = None
        self._labels: Optional[Dict[int, str]] = None
        self._model_path: Optional[Path] = None
        self._conv_layer_names: List[str] = []

    def _resolve_model_path(self) -> Path:
        env_path = os.environ.get("AGROVISION_MODEL_PATH")
        if env_path:
            p = Path(env_path)
            if not p.exists():
                raise FileNotFoundError(
                    f"AGROVISION_MODEL_PATH={env_path} does not exist"
                )
            return p

        for candidate in DEFAULT_MODEL_CANDIDATES:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            "Could not find model file. Train the model first (python train_species.py) "
            "or set AGROVISION_MODEL_PATH env var to the .keras/.h5 file."
        )

    def _resolve_labels_path(self) -> Path:
        env_path = os.environ.get("AGROVISION_LABELS_PATH")
        if env_path:
            p = Path(env_path)
            if p.exists():
                return p

        for candidate in DEFAULT_LABELS_CANDIDATES:
            if candidate.exists():
                return candidate

        raise FileNotFoundError(
            "Could not find labels_species.json. Train the model first or set "
            "AGROVISION_LABELS_PATH env var."
        )

    def load(self) -> None:
        model_path = self._resolve_model_path()
        labels_path = self._resolve_labels_path()

        print(f"[XAI] Loading Keras model from {model_path} ...")
        self._model = keras.models.load_model(model_path, compile=False)
        self._model_path = model_path

        with open(labels_path, "r", encoding="utf-8") as f:
            raw_labels = json.load(f)

        self._labels = {int(k): v for k, v in raw_labels.items()}

        self._conv_layer_names = [
            layer.name for layer in self._model.layers if isinstance(layer, keras.layers.Conv2D)
        ]
        # When MobileNetV2 is embedded as a sub-model, conv layers are nested.
        # Walk the graph to collect conv layer names inside nested models too.
        nested_convs: List[str] = []
        for layer in self._model.layers:
            if isinstance(layer, keras.Model):
                for sub in layer.layers:
                    if isinstance(sub, keras.layers.Conv2D):
                        nested_convs.append(sub.name)
        if nested_convs:
            self._conv_layer_names.extend(nested_convs)

        print(f"[XAI] Model loaded. Classes: {len(self._labels)}. "
              f"Conv layers available: {len(self._conv_layer_names)}")
        if self._conv_layer_names:
            print(f"[XAI] Last 5 conv layers: {self._conv_layer_names[-5:]}")

    @property
    def model(self) -> keras.Model:
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        return self._model

    @property
    def labels(self) -> Dict[int, str]:
        if self._labels is None:
            raise RuntimeError("Labels not loaded. Call load() first.")
        return self._labels

    @property
    def conv_layer_names(self) -> List[str]:
        return list(self._conv_layer_names)

    def label_for(self, idx: int) -> str:
        return self.labels.get(idx, f"class_{idx}")


registry = ModelRegistry()
