# AgroVision XAI Backend

Serviço FastAPI que roda **Grad-CAM** no modelo Keras original e calcula a métrica **Attention Leakage (AL)** + **Attention Focus Score (AFS)** usada pelo modo científico do app mobile.

> Grad-CAM precisa de gradientes e feature maps intermediários — isso **não é possível no TFLite**, por isso esse backend roda em Python, no modelo Keras salvo durante o treinamento (`model_species.keras`).

---

## Pré-requisitos

1. Treinar o modelo primeiro:
   ```bash
   python prepare_species.py --max-per-class 500
   python train_species.py
   ```
   Isso gera:
   - `model_species.keras` ← usado pelo backend XAI
   - `model_species.tflite` ← usado pelo app (inferência offline)
   - `labels_species.json`

2. Instalar dependências do backend (já incluídas em `requirements.txt`):
   ```bash
   pip install -r requirements.txt
   ```

---

## Rodar localmente

Na pasta `agrovision-ml-service/`:

```bash
uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload
```

Saída esperada no startup:
```
[XAI] Loading Keras model from model_species.keras ...
[XAI] Model loaded. Classes: 25. Conv layers available: 52
[XAI] Last 5 conv layers: [..., 'Conv_1']
```

Se o modelo estiver em outro caminho:
```bash
export AGROVISION_MODEL_PATH=/caminho/para/model_species.keras
export AGROVISION_LABELS_PATH=/caminho/para/labels_species.json
```
(No Windows PowerShell: `$env:AGROVISION_MODEL_PATH = "..."`)

---

## Endpoints

### `GET /api/health`
Check de conectividade (o app usa antes de abrir o Modo Teste).

```json
{
  "status": "ok",
  "model_path": "model_species.keras",
  "num_classes": 25,
  "conv_layers_tail": ["block_16_project", "Conv_1", ...]
}
```

### `POST /api/xai/gradcam`
`multipart/form-data`:

| campo | tipo | default | descrição |
|---|---|---|---|
| `image` | file | — | imagem JPG/PNG |
| `bbox_strategy` | string | `fixed` | `fixed` \| `green` \| `manual` |
| `bbox_manual` | string | — | obrigatório se `manual` — `"x,y,w,h"` em pixels |
| `coverage` | float | `0.8` | fração da imagem coberta pelo bbox fixo |
| `threshold` | float | `0.5` | threshold de ativação para AL |
| `layer_name` | string | — | nome da camada conv; default = última Conv2D |

Resposta:
```json
{
  "prediction": "Solanum lycopersicum",
  "predicted_index": 0,
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

---

## Teste rápido (curl)

```bash
curl -X POST http://localhost:5000/api/xai/gradcam \
  -F "image=@minha_planta.jpg" \
  -F "bbox_strategy=green" \
  -F "threshold=0.5"
```

---

## Como o mobile consome

O app usa `EXPO_PUBLIC_XAI_URL` (default `http://localhost:5000`). Ajuste no `.env` ou antes de `expo start`:

```bash
export EXPO_PUBLIC_XAI_URL=http://192.168.x.x:5000   # IP da máquina rodando o backend
```
(dispositivos físicos precisam de um IP acessível na rede local, não `localhost`)
