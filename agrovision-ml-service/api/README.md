# API — Endpoints e formato

## Classes suportadas
O modelo Keras usado para Grad-CAM foi treinado nas 4 classes de doenças foliares
do milho:

- `Blight` — Helmintosporiose (*Exserohilum turcicum*)
- `Common_Rust` — Ferrugem-comum (*Puccinia sorghi*)
- `Gray_Leaf_Spot` — Mancha-cinzenta (*Cercospora zeae-maydis*)
- `Healthy` — Folha saudável

## `GET /api/health`
Verifica se o backend está no ar e se o Roboflow está configurado.

```json
{
  "status": "ok",
  "model_path": "model_species.keras",
  "num_classes": 4,
  "conv_layers_tail": ["...", "Conv_1"],
  "roboflow_configured": true
}
```

## `POST /api/xai/gradcam`
`multipart/form-data`, header `X-API-Key: <chave>`.

| campo | tipo | default | descrição |
|---|---|---|---|
| `image` | file | — | JPG ou PNG |
| `bbox_strategy` | string | `fixed` | `fixed` \| `green` |
| `coverage` | float | `0.8` | fração da imagem coberta pelo bbox fixo |
| `threshold` | float | `0.5` | limiar de ativação para AL/AFS |
| `layer_name` | string | — | camada conv (default: última Conv2D) |
| `predicted_class` | string | — | força a explicação para uma classe específica |

Resposta:
```json
{
  "prediction": "Common_Rust",
  "predicted_index": 1,
  "confidence": 0.94,
  "al": 0.27,
  "afs": 0.73,
  "threshold": 0.5,
  "bbox_used": [32, 48, 384, 512],
  "bbox_strategy": "green",
  "heatmap_b64": "iVBORw0K...",
  "overlay_b64": "iVBORw0K...",
  "image_width": 448,
  "image_height": 608,
  "layer_used": "auto_last_conv",
  "processing_time_ms": 342
}
```

## `WS /ws/classify`
Query `?api_key=<chave>`. Cliente envia `{"image_b64": "..."}`. O servidor
retorna eventos:
- `{"event":"progress","step":"...","pct":30}`
- `{"event":"result","prediction":"Blight","confidence":0.91,"source":"roboflow"}`
- `{"event":"error","message":"..."}`

## `WS /ws/gradcam`
Query `?api_key=<chave>`. Cliente envia:
```json
{"image_b64": "...", "bbox_strategy": "fixed", "threshold": 0.5, "coverage": 0.8}
```
Servidor emite eventos de `progress` e um `result` com o payload completo do
`/api/xai/gradcam`.

## Teste rápido

```powershell
curl.exe -X POST http://localhost:5000/api/xai/gradcam `
  -H "X-API-Key: chave-forte" `
  -F "image=@folha_milho.jpg" `
  -F "bbox_strategy=green"
```
