from typing import Optional, Tuple

import numpy as np
import tensorflow as tf
from tensorflow import keras


def _find_layer(model: keras.Model, name: str) -> keras.layers.Layer:
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
    # Usa a última Conv2D — no MobileNetV2 isso cai na camada Conv_1, antes do GAP
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
    # Caso simples: camada alvo está diretamente no modelo principal
    if any(layer is target_layer for layer in model.layers):
        try:
            return keras.Model(
                inputs=model.inputs,
                outputs=[target_layer.output, model.output],
            )
        except Exception as exc:
            raise RuntimeError(
                f"Cannot build Grad-CAM model for layer '{target_layer.name}': {exc}. "
                "Try specifying a different conv layer via layer_name."
            ) from exc

    # Caso MobileNetV2 embutido como sub-modelo: precisa de um modelo interno que
    # exponha os feature maps E a saída do sub-modelo em um único forward pass,
    # senão o GradientTape retorna None para o gradiente.
    parent: Optional[keras.Model] = None
    for layer in model.layers:
        if isinstance(layer, keras.Model):
            if any(l is target_layer for l in layer.layers):
                parent = layer
                break

    if parent is None:
        raise RuntimeError(
            f"Layer '{target_layer.name}' not found at the top level or inside any "
            "direct sub-model.  Try specifying a top-level layer via layer_name."
        )

    try:
        inner_grad = keras.Model(
            inputs=parent.inputs,
            outputs=[target_layer.output, parent.output],
        )
    except Exception as exc:
        raise RuntimeError(
            f"Cannot build inner grad model for layer '{target_layer.name}': {exc}"
        ) from exc

    x = model.inputs[0] if len(model.inputs) == 1 else model.inputs
    feature_maps_sym = None

    for layer in model.layers:
        if isinstance(layer, keras.layers.InputLayer):
            continue
        if layer is parent:
            feature_maps_sym, x = inner_grad(x)
        else:
            x = layer(x)

    if feature_maps_sym is None:
        raise RuntimeError(
            f"Sub-model '{parent.name}' was not encountered while reconstructing "
            "the outer forward pass."
        )

    try:
        return keras.Model(inputs=model.inputs, outputs=[feature_maps_sym, x])
    except Exception as exc:
        raise RuntimeError(f"Cannot build outer Grad-CAM model: {exc}") from exc


def generate_gradcam(
    input_tensor: tf.Tensor,
    model: keras.Model,
    layer_name: Optional[str] = None,
    class_index: Optional[int] = None,
) -> Tuple[np.ndarray, int, float]:
    if layer_name:
        target_layer = _find_layer(model, layer_name)
    else:
        target_layer = _pick_default_conv_layer(model)

    grad_model = _build_grad_model(model, target_layer)

    # Grava o forward pass para poder calcular os gradientes depois
    with tf.GradientTape() as tape:
        feature_maps, predictions = grad_model(input_tensor, training=False)
        if class_index is None:
            class_index = int(tf.argmax(predictions[0]).numpy())
        class_score = predictions[:, class_index]

    # Gradiente da classe alvo em relação aos feature maps da camada escolhida
    grads = tape.gradient(class_score, feature_maps)
    if grads is None:
        raise RuntimeError(
            f"Gradient returned None for layer '{target_layer.name}'. "
            "The layer may not be on the path to the output."
        )

    # Média global dos gradientes → peso de importância por canal
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Cada canal dos feature maps é multiplicado pelo seu peso e somado
    feature_maps_0 = feature_maps[0]
    cam = tf.reduce_sum(feature_maps_0 * pooled_grads, axis=-1)

    # ReLU remove ativações negativas; normaliza para [0, 1]
    cam = tf.nn.relu(cam)
    cam_max = tf.reduce_max(cam)
    if cam_max > 0:
        cam = cam / cam_max
    cam_np = cam.numpy().astype(np.float32)

    # Redimensiona o CAM para o tamanho da imagem de entrada
    input_h = int(input_tensor.shape[1])
    input_w = int(input_tensor.shape[2])
    cam_resized = tf.image.resize(
        cam_np[..., None], size=(input_h, input_w), method="bilinear"
    ).numpy().squeeze(-1)

    cam_max2 = float(cam_resized.max())
    if cam_max2 > 0:
        cam_resized = cam_resized / cam_max2

    predicted_confidence = float(predictions[0, class_index].numpy())
    return cam_resized.astype(np.float32), int(class_index), predicted_confidence
