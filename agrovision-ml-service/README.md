# AgroVision — Backend

Serviço FastAPI que faz o proxy da classificação para o **Roboflow** e roda o
**Grad-CAM** localmente no modelo Keras para o modo científico do app.

- Classificação: 100% online via Roboflow (o backend só encaminha).
- Grad-CAM / Attention Leakage / Attention Focus Score: computados aqui,
  no modelo Keras (`model_species.keras`), porque a API do Roboflow não
  expõe gradientes.

## Rodar localmente

```powershell
pip install -r requirements.txt
$env:AGROVISION_API_KEY = "chave-forte"
$env:ROBOFLOW_API_KEY   = "sua-chave-roboflow"
$env:ROBOFLOW_MODEL_ID  = "workspace/modelo/versao"
uvicorn api.server:app --host 0.0.0.0 --port 5000 --reload
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET  | `/api/health`        | Status do backend + config Roboflow |
| POST | `/api/xai/gradcam`   | Grad-CAM + AL/AFS (multipart, com API key) |
| WS   | `/ws/classify`       | Classificação Roboflow com progresso |
| WS   | `/ws/gradcam`        | Grad-CAM com progresso em tempo real |

Autenticação:
- HTTP: header `X-API-Key: <AGROVISION_API_KEY>`
- WebSocket: query param `?api_key=<AGROVISION_API_KEY>`

## Deploy (Railway)

O `Procfile` já está pronto:
```
web: uvicorn api.server:app --host 0.0.0.0 --port $PORT
```

Configure em Settings → Variables:
- `AGROVISION_API_KEY` — chave forte, também no app mobile
- `ROBOFLOW_API_KEY`   — chave da conta Roboflow
- `ROBOFLOW_MODEL_ID`  — id do modelo publicado (`workspace/modelo/versao`)

Detalhes técnicos de XAI (Grad-CAM, AL, AFS): ver [api/README.md](api/README.md).
