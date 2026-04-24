# AgroVision - Species Identification App

Aplicativo offline-first para identificação de espécies de plantas usando inteligência artificial.

## Quick Start

**Novo no projeto?** Comece por aqui: [COMECE_AQUI.md](COMECE_AQUI.md)

## Documentação

- **[COMECE_AQUI.md](COMECE_AQUI.md)** - Guia de início rápido (português)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arquitetura geral do projeto
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estrutura de pastas e arquivos

## Overview

```
App (React Native/Expo)
  ├─ TFLite Inference (100% offline)
  │  └─ Identifica espécies de plantas
  │
  ├─ Modo Científico / XAI (opt-in, online)
  │  └─ Grad-CAM + Attention Leakage via backend Python
  │
  └─ Institutional Tab (Biblioteca agronômica)
     └─ AGRIS + OpenAgriData
```

## Requisitos

- Node.js 18+
- Expo CLI
- Python 3.8+ (para ML training)

## Instalação Rápida

```bash
# Frontend
npm install
npx expo start

# ML Training (em agrovision-ml-service/)
pip install -r requirements.txt
python train_species.py
```

## Features

✅ Identificação de espécies 100% offline
✅ Modelo TFLite (~12MB)
✅ Interface em português
✅ Sem internet necessária
✅ Rápido (<500ms por análise)

## Status

- ✅ Frontend refatorado
- ✅ ML training pipeline
- ✅ TFLite integration
- ✅ Offline-first architecture
- ✅ Modo Científico com Grad-CAM + Attention Leakage (backend opcional)

## Modo Científico (XAI)

O app tem um card "🔬 Modo Científico" na Home que roda **Grad-CAM** sobre o
modelo Keras original (não o TFLite) e calcula **Attention Leakage (AL)** e
**Attention Focus Score (AFS)** para avaliar quanto o modelo foca
corretamente na planta.

Como é feature opt-in e requer gradientes (impossível no TFLite), há um
backend Python separado em [`agrovision-ml-service/api/`](agrovision-ml-service/api/README.md).

```bash
# Treine o modelo (gera .keras + .tflite + labels.json)
cd agrovision-ml-service
python train_species.py

# Suba o backend XAI
uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload

# No app, configure a URL do backend antes do expo start:
#   EXPO_PUBLIC_XAI_URL=http://<IP-da-máquina>:5000
```

## Contribuindo

Para alterações significativas, atualize a documentação em `ARCHITECTURE.md`.

---

**Dúvidas?** Veja [COMECE_AQUI.md](COMECE_AQUI.md) para mais instruções.
