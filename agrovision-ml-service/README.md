# AgroVision ML Training Pipeline

🌱 **Treine um modelo de identificação de espécies vegetais com qualidade offline**

---

## ⚠️ Pré-requisitos

- Python 3.8+
- Windows/Linux/Mac
- ~50GB de espaço livre (para dataset + modelo)
- 4GB RAM mínimo (8GB recomendado)
- Conexão internet (para baixar dataset)

---

## 🚀 Início Rápido

### 1️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

**Tempo:** ~5-10 minutos (depende da internet)

### 2️⃣ Preparar Dataset

```bash
python prepare_species.py --max-per-class 500
```

**O que faz:**
- Baixa 300k imagens do PlantNet300k
- Aplica CLAHE (normaliza iluminação)
- Redimensiona com padding proporcional
- Salva em `datasets/hf_species/`

**Tempo:** 30-60 minutos
**Espaço:** ~20-40GB

**Saída esperada:**
```
✓ Total species: 200-300
✓ Total images: 100k-150k
✓ Output directory: datasets/hf_species/
✓ Labels saved to: labels_species.json
```

### 3️⃣ Treinar Modelo

```bash
python train_species.py
```

**O que faz:**
- Treina MobileNetV2 com transfer learning
- Aplica data augmentation (6 tipos)
- Phase 1: 20 épocas (base congelada)
- Phase 2: 15 épocas (fine-tuning)
- Exporta para TFLite INT8 quantizado

**Tempo:**
- CPU: 1-2 horas
- GPU: ~20 minutos

**Saída esperada:**
```
✓ TFLite model saved: model_species.tflite
  Size: 10-15 MB
✓ Labels saved: labels_species.json
✓ Phase 1 accuracy: ~0.75
✓ Phase 2 accuracy: ~0.85
```

### 4️⃣ Copiar Modelo para App

```bash
# Windows
copy model_species.tflite ..\app_tc\assets\models\
copy labels_species.json ..\app_tc\assets\models\

# Linux/Mac
cp model_species.tflite ../app_tc/assets/models/
cp labels_species.json ../app_tc/assets/models/
```

### 5️⃣ Rodar App com Novo Modelo

```bash
cd ../app_tc
npm start

# Ou
npx expo start
```

---

## 📊 Parâmetros Personalizáveis

### Reduzir Tempo de Preparação

```bash
# Menos imagens por espécie (vai mais rápido)
python prepare_species.py --max-per-class 300

# Resultado esperado:
# ~150 espécies × 300 = 45k imagens
# Tempo: 15-30 min
# Espaço: ~10GB
```

### Aumentar Qualidade

```bash
# Mais imagens por espécie (treino melhor)
python prepare_species.py --max-per-class 1000

# Resultado esperado:
# ~150 espécies × 1000 = 150k imagens
# Tempo: 1-2h download + 3h treino = 4-5h total
# Espaço: ~30GB
# Acertividade: ~90%
```

---

## 🎯 Estimativas de Tempo

| Cenário | Preparação | Treinamento | Total | GPU? |
|---------|-----------|------------|-------|------|
| **Rápido** (max-per-class 300) | 15-30min | 45min | 1-1.5h | Não |
| **Balanceado** (max-per-class 500) | 30-60min | 1-2h | 2-3h | Não |
| **Qualidade** (max-per-class 1000) | 1-2h | 2-3h | 3-5h | Não |
| **Com GPU** (max-per-class 500) | 30-60min | 20-30min | 1-1.5h | Sim |

---

## 📁 Estrutura de Arquivos

```
agrovision-ml-service/
├── prepare_species.py         # Preparar dataset
├── train_species.py           # Treinar modelo
├── requirements.txt           # Dependências
├── datasets/
│   └── hf_species/
│       ├── Solanum lycopersicum/
│       ├── Musa paradisiaca/
│       └── ... (outras espécies)
├── model_species.tflite       # Modelo treinado (gerado)
└── labels_species.json        # Mapeamento classes (gerado)
```

---

## 🖥️ Requisitos de Sistema

### Mínimo
- CPU: 4 cores @ 2GHz
- RAM: 4GB
- Disco: 50GB
- Tempo: 3-4 horas

### Recomendado
- CPU: 8 cores @ 3GHz
- RAM: 8-16GB
- Disco: 50GB SSD
- GPU: NVIDIA GTX 1650+ (reduz para 45 min)
- Tempo: 1-2 horas

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'tensorflow'"
```bash
pip install --upgrade tensorflow==2.15.0
```

### Erro: "Não há espaço em disco"
Reduza `max-per-class`:
```bash
python prepare_species.py --max-per-class 200
```

### Memória insuficiente durante treino
Reduza batch size no `train_species.py`:
```python
BATCH_SIZE = 16  # era 32
```

### Download muito lento
Verifique sua conexão internet. Se necessário, use um dataset local:
```bash
# Colocar imagens em datasets/hf_species/Especie1/, Especie2/, ...
```

---

## 📱 Próximo Passo: Usar no App

Depois que treinar, o app `app_tc` automaticamente usará o modelo em `assets/models/`:

1. ✅ Treinou: `model_species.tflite` + `labels_species.json`
2. ✅ Copiou para: `app_tc/assets/models/`
3. ✅ App agora identifica offline com acertividade real!

---

## 📊 Arquitetura

```
PlantNet300k Dataset (HuggingFace)
        ↓
  CLAHE Normalization (lighting)
  Proportional Padding (aspect ratio)
        ↓
  datasets/hf_species/
        ↓
  MobileNetV2 Transfer Learning
  + Data Augmentation (6 tipos)
  + Two-Phase Training
        ↓
  model_species.tflite (INT8 quantized)
        ↓
  React Native App (100% Offline)
```

---

## 📄 Mais Informações

- **Backend**: Nenhum servidor necessário (offline-first)
- **Modelo**: MobileNetV2 INT8 TFLite (~12MB)
- **Acertividade**: 85-90% para as espécies do dataset
- **Tempo Inferência**: 100-500ms no dispositivo

---

**Pronto! Agora você sabe como treinar o modelo! 🚀**
