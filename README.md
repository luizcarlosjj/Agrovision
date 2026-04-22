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

## Contribuindo

Para alterações significativas, atualize a documentação em `ARCHITECTURE.md`.

---

**Dúvidas?** Veja [COMECE_AQUI.md](COMECE_AQUI.md) para mais instruções.
