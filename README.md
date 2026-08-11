# AgroVision

Aplicativo mobile para **diagnóstico de doenças foliares do milho** por visão
computacional. TCC em Ciência da Computação, com ênfase em **Inteligência
Artificial Explicável (XAI)**.

- Classificação: 100% online via **Roboflow**
- Explicabilidade: **Grad-CAM** + **Attention Leakage (AL)** e **Attention Focus Score (AFS)**
  computados em backend próprio (FastAPI)

Documentação completa e didática: [PROJETO.md](PROJETO.md).

## Arquitetura

```
Mobile (React Native + Expo)
   │
   │  imagem (base64) via WebSocket
   ▼
Backend (FastAPI, Railway)
   │
   ├── /ws/classify → Roboflow Serverless API → classe + confiança
   └── /ws/gradcam  → Modelo Keras local     → Grad-CAM + AL/AFS
```

## Doenças detectadas
- Blight — Helmintosporiose (*Exserohilum turcicum*)
- Common_Rust — Ferrugem-comum (*Puccinia sorghi*)
- Gray_Leaf_Spot — Mancha-cinzenta (*Cercospora zeae-maydis*)
- Healthy — Folha saudável

## Rodar localmente

### 1. Backend
```powershell
cd agrovision-ml-service
pip install -r requirements.txt
$env:AGROVISION_API_KEY = "chave-forte-min-16-chars"
$env:ROBOFLOW_API_KEY   = "sua-chave-roboflow"
$env:ROBOFLOW_MODEL_ID  = "workspace/modelo/versao"
uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload
```

### 2. App mobile
```powershell
npm install
Copy-Item .env.example .env.local
# edite .env.local com EXPO_PUBLIC_API_URL e EXPO_PUBLIC_API_KEY
npx expo start
```
Abra pelo Expo Go (Android/iOS) escaneando o QR Code.

## Estrutura do repositório

```
Agrovision/
├── src/                       # App React Native
│   ├── screens/               # Home, Camera, Processing, Result, Auditar, TestMode, History, About
│   ├── components/            # ui/, common/, xai/
│   ├── services/              # ml/ (Roboflow + Grad-CAM), storage/ (SQLite), camera/
│   ├── context/               # AppContext + AnalysisContext
│   ├── models/                # tipos de domínio (analysis, api, xai)
│   ├── navigation/            # RootNavigator + tipos
│   └── utils/                 # constants, format, logger, csv/excel export
├── agrovision-ml-service/     # Backend FastAPI (Roboflow proxy + XAI)
│   ├── api/
│   │   ├── server.py          # endpoints REST + WebSocket
│   │   └── xai/               # gradcam, mask, metrics, overlay, roboflow
│   ├── model_species.keras    # modelo Keras (usado só para Grad-CAM)
│   └── labels_species.json
├── TCC-docs/                  # 10 documentos acadêmicos do TCC
├── PROJETO.md                 # Documentação didática para leigos
└── README.md
```

## Deploy

- **Backend:** Railway — `Procfile` pronto; configure as env vars em
  Settings → Variables (`AGROVISION_API_KEY`, `ROBOFLOW_API_KEY`, `ROBOFLOW_MODEL_ID`).
- **App:** EAS Build (`npx eas build`) para gerar APK/IPA.

## Segurança

- Autenticação via API key compartilhada (header `X-API-Key` no HTTP, query
  param `?api_key=` no WebSocket).
- Comparação em tempo constante (`hmac.compare_digest`).
- Backend recusa qualquer request se `AGROVISION_API_KEY` não estiver
  configurada (fail-closed).
- CORS explícito (nenhuma origem permitida por default; ajuste
  `AGROVISION_CORS_ORIGINS` se for expor um cliente web).
- Limite de tamanho de imagem (`AGROVISION_MAX_IMAGE_MB`, default 5 MB).

## Licença

MIT.
