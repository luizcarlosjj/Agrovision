"""
Grad-CAM implementation.

Given a preprocessed input tensor of shape (1, H, W, 3) and a target conv
layer, computes the class-activation map by combining feature maps weighted
by the gradients of the predicted class w.r.t. those feature maps, then
ReLU-thresholds and normalizes the result to [0, 1].

Works on the full Keras model — not TFLite — because gradients are required.
"""

from typing import Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras


def _find_layer(model: keras.Model, name: str) -> keras.layers.Layer:
    """Recursively find a layer by name, searching nested sub-models too."""
    for layer in model.layers:
        if layer.name == name:
            return layer
        if isinstance(layer, keras.Model):
            try:
                return _find_layer(layer, name)
            except ValueError:
                pass
    raise ValueError(f"Layer '{name}' not found in model")


def _pick_default_conv_layer(model: keras.Model) -> keras.layers.Layer:
    """
    Heuristic: pick the last Conv2D layer in the model (walking into nested
    sub-models). For MobileNetV2 this lands on 'Conv_1' before the GAP head.
    """
    last_conv: Optional[keras.layers.Layer] = None

    def walk(m: keras.Model) -> None:
        nonlocal last_conv
        for layer in m.layers:
            if isinstance(layer, keras.layers.Conv2D):
                last_conv = layer
            if isinstance(layer, keras.Model):
                walk(layer)

    walk(model)
    if last_conv is None:
        raise RuntimeError("No Conv2D layer found in the model")
    return last_conv


def _build_grad_model(
    model: keras.Model, target_layer: keras.layers.Layer
) -> keras.Model:
    """
    Build a sub-model exposing (feature_maps_of_target_layer, model_output)
    given a single input tensor. Handles the case where the target layer is
    inside a nested sub-model (common with MobileNetV2 embedded as a block).
    """
    # Case 1: target layer is a direct top-level layer.
    if target_layer in model.layers:
        return keras.Model(
            inputs=model.inputs,
            outputs=[target_layer.output, model.output],
        )

    # Case 2: target layer lives inside a nested sub-model.
    # Find the parent sub-model that owns it.
    parent: Optional[keras.Model] = None
    for layer in model.layers:
        if isinstance(layer, keras.Model):
            if target_layer in layer.layers:
                parent = layer
                break
    if parent is None:
        raise RuntimeError(
            f"Could not locate parent sub-model for layer '{target_layer.name}'"
        )

    # Build a sub-model of the parent that outputs the target feature maps.
    feature_extractor = keras.Model(
        inputs=parent.inputs,
        outputs=target_layer.output,
        name=f"feat_extractor_{target_layer.name}",
    )

    # Recreate the forward pass: inputs -> (top-level layers until parent)
    # -> parent/feature_extractor -> (remaining top-level layers).
    inputs = model.inputs
    x = inputs[0] if isinstance(inputs, list) and len(inputs) == 1 else inputs
    feature_maps = None
    passed_parent = False
    for layer in model.layers:
        if layer is parent:
            feature_maps = feature_extractor(x)
            x = layer(x)
            passed_parent = True
            continue
        # Skip the InputLayer (it's already `inputs`)
        if isinstance(layer, keras.layers.InputLayer):
            continue
        if not passed_parent:
            # Pre-parent layers may include things like a preprocessing Lambda.
            x = layer(x)
        else:
            x = layer(x)

    if feature_maps is None:
        raise RuntimeError("Failed to re-route through parent sub-model")

    return keras.Model(inputs=model.inputs, outputs=[feature_maps, x])


def generate_gradcam(
    input_tensor: tf.Tensor,
    model: keras.Model,
    layer_name: Optional[str] = None,
    class_index: Optional[int] = None,
) -> Tuple[np.ndarray, int, float]:
    """
    Compute a Grad-CAM heatmap.

    Args:
        input_tensor: (1, H, W, 3) float tensor in the range expected by the
            model's first layer (MobileNetV2's preprocess_input is inside the
            model, so raw 0..255 float is fine for this project's model).
        model: full Keras classification model.
        layer_name: optional name of the target conv layer. Defaults to the
            last Conv2D in the model.
        class_index: optional class index to target. If None, the predicted
            (top-1) class is used.

    Returns:
        heatmap_hw: (H, W) float32 array in [0, 1] (same spatial size as the
            input tensor — NOT the original image).
        predicted_index: int, the class index for which the CAM was computed.
        predicted_confidence: float in [0, 1], softmax probability of that class.
    """
    if layer_name:
        target_layer = _find_layer(model, layer_name)
    else:
        target_layer = _pick_default_conv_layer(model)

    grad_model = _build_grad_model(model, target_layer)

    with tf.GradientTape() as tape:
        feature_maps, predictions = grad_model(input_tensor, training=False)
        if class_index is None:
            class_index = int(tf.argmax(predictions[0]).numpy())
        class_score = predictions[:, class_index]

    grads = tape.gradient(class_score, feature_maps)
    if grads is None:
        raise RuntimeError(
            f"Gradient returned None for layer '{target_layer.name}'. "
            "The layer may not be on the path to the output."
        )

    # Global-average the gradients to get per-channel importance weights.
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))  # (C,)

    # Weight feature maps by their importance and sum across channels.
    feature_maps_0 = feature_maps[0]  # (Hf, Wf, C)
    cam = tf.reduce_sum(feature_maps_0 * pooled_grads, axis=-1)  # (Hf, Wf)

    # ReLU + normalize to [0, 1].
    cam = tf.nn.relu(cam)
    cam_max = tf.reduce_max(cam)
    if cam_max > 0:
        cam = cam / cam_max
    cam_np = cam.numpy().astype(np.float32)

    # Upsample to the input tensor's spatial size.
    input_h = int(input_tensor.shape[1])
    input_w = int(input_tensor.shape[2])
    cam_resized = tf.image.resize(
        cam_np[..., None], size=(input_h, input_w), method="bilinear"
    ).numpy().squeeze(-1)

    # Renormalize after resize (bilinear can drop peak slightly).
    cam_max2 = float(cam_resized.max())
    if cam_max2 > 0:
        cam_resized = cam_resized / cam_max2

    predicted_confidence = float(predictions[0, class_index].numpy())
    return cam_resized.astype(np.float32), int(class_index), predicted_confidence
