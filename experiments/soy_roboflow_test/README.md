# Experimento: Detecção de Doenças em Soja (Roboflow Dataset)

Treina um MobileNetV2 no dataset `soy-leaf-disease` do Roboflow.
Gera `.keras` + `.tflite` + `labels_soy.json` prontos para o app.
**Nenhum arquivo do projeto principal é modificado.**

## Estrutura

```
soy_roboflow_test/
├── download_dataset.py    ← baixa o dataset do Roboflow
├── train_soy_disease.py   ← treina MobileNetV2 + exporta TFLite
├── test_roboflow_model.py ← testa via API hospedada (alternativo)
├── dataset/               ← criada pelo download_dataset.py
│   ├── train/
│   ├── valid/
│   └── test/
├── sample_images/         ← imagens avulsas para testar a API
└── results/               ← JSONs gerados pelo test_roboflow_model.py
```

## Passo a passo completo

### 1. Instalar dependências

```bash
pip install roboflow tensorflow pillow
```

### 2. Configurar a API Key

**Windows PowerShell:**
```powershell
$env:ROBOFLOW_API_KEY="sua_chave_aqui"
```

**Windows CMD:**
```cmd
set ROBOFLOW_API_KEY=sua_chave_aqui
```

### 3. Baixar o dataset

```bash
python download_dataset.py
```

Cria a pasta `dataset/` com splits `train/valid/test` organizados por classe (ex: `bacterial_pustule/`, `frogeye_leaf_spot/`).

### 4. Treinar o modelo

```bash
python train_soy_disease.py
```

Processo (igual ao pipeline principal do AgroVision):
- **Fase 1** — 20 épocas com backbone MobileNetV2 congelado
- **Fase 2** — 15 épocas de fine-tune nas últimas 50 camadas

Gera na mesma pasta:
- `model_soy.keras` — para o backend Grad-CAM / XAI
- `model_soy.tflite` — para o app offline
- `labels_soy.json` — mapa `índice → nome da doença`

### 5. Integrar ao app (quando validado)

```
model_soy.tflite  →  agrovision-ml-service/model_species.tflite  (substitui)
labels_soy.json   →  agrovision-ml-service/labels.json           (substitui)
model_soy.keras   →  agrovision-ml-service/model_species.keras   (para Grad-CAM)
```

Nenhum código do app precisa mudar — ele já carrega esses arquivos pelo nome.

---

## Alternativa: Testar via API hospedada (sem treinar)

Se quiser só testar as predições antes de treinar:

```bash
# Coloque imagens em sample_images/
python test_roboflow_model.py
```

Retorna JSON com `class`, `confidence` e bounding boxes em `results/`.

---

## Interpretar o JSON de resultado (API hospedada)

```json
{
  "predictions": [
    {
      "class": "bacterial_pustule",
      "confidence": 0.87,
      "x": 320,   "y": 240,
      "width": 150, "height": 120
    }
  ]
}
```

| Campo        | Descrição                                              |
|--------------|--------------------------------------------------------|
| `class`      | Nome da doença detectada                               |
| `confidence` | Confiança (0.0 – 1.0)                                  |
| `x`, `y`     | Centro da bounding box (pixels)                        |
| `width/height` | Dimensões da bounding box                            |

> Coordenadas centralizadas: `x_min = x - width/2`, `y_min = y - height/2`

---

## Visão futura

A bounding box retornada pela API (ou predita pelo modelo treinado) pode
substituir a segmentação por cor verde atual no cálculo de **Attention Leakage**,
fornecendo uma máscara mais precisa para o Grad-CAM do backend XAI.
