# Dynamic Training System - Complete Guide

## Overview

Sistema de treinamento dinâmico 100% offline com sincronização automática quando há internet. Sem servidor backend necessário.

```
Usuário tira foto
     ↓ (offline)
App armazena em documentDirectory/user_training_data/
     ↓
Quando tem internet:
  Sincroniza automaticamente
     ↓
Python script executa fine-tuning local
     ↓
Modelo atualizado (.tflite + .h5)
     ↓
App recarrega novo modelo
```

---

## 🚀 Implementação Prática

### Passo 1: Preparar Dataset Base

```bash
cd agrovision-ml-service

# Baixa PlantNet300k + FVHQ (500 imagens cada)
python prepare_species.py --max-per-class 500

# Treina modelo inicial
python train_species.py

# Gera:
# - model_species.tflite (para app)
# - model_species.h5 (para fine-tuning)
```

### Passo 2: Copiar Arquivos para App

```bash
# Copiar modelo
copy model_species.tflite ..\app_tc\assets\models\
copy model_species.h5 ..\app_tc\assets\models\
copy labels_species.json ..\app_tc\assets\models\
```

### Passo 3: Integrar Serviço de Sync no App

**Em `src/App.tsx` ou inicialização:**

```typescript
import { autoSyncService } from '@services/sync/autoSyncService';

// No App startup:
useEffect(() => {
  // Iniciar monitoring automático
  const unsubscribe = autoSyncService.startMonitoring();

  return () => {
    if (unsubscribe) unsubscribe();
    autoSyncService.stopMonitoring();
  };
}, []);
```

### Passo 4: Armazenar Fotos do Usuário

**Ao tirar/selecionar foto:**

```typescript
import { autoSyncService } from '@services/sync/autoSyncService';

const handlePhotoCapture = async (photoUri: string, species: string) => {
  // Salvar para treinamento
  const stored = await autoSyncService.storeUserPhoto(photoUri, species);

  if (stored) {
    console.log('Foto armazenada para fine-tuning');

    // Mostrar status
    const status = await autoSyncService.getSyncStatus();
    console.log(`Fotos pendentes: ${status.pending_images}`);
  }
};
```

### Passo 5: Executar Fine-tuning (Local ou Remoto)

#### **Opção A: Fine-tuning Local (Seu PC)**

```bash
# Quando quiser, execute:
python sync_and_finetune.py

# O script vai:
# 1. Detectar fotos em user_training_data/
# 2. Fine-tunear o modelo
# 3. Exportar novo model_species.tflite
# 4. Arquivar fotos processadas
```

#### **Opção B: Fine-tuning Automático (Próximo Passo)**

```bash
# Executar continuamente:
watch -n 300 'python sync_and_finetune.py'

# Ou criar cron job (Linux/Mac):
*/5 * * * * cd /path/to/agrovision-ml-service && python sync_and_finetune.py

# Ou task scheduler (Windows)
# Executar sync_and_finetune.py a cada 5 minutos
```

---

## 📊 Estrutura de Dados

### Storage no App

```
documentDirectory/
├─ user_training_data/
│  ├─ Tomate/
│  │  ├─ tomate_1709874000000.jpg
│  │  ├─ tomate_1709874005000.jpg
│  │  └─ ...
│  ├─ Batata/
│  │  └─ ...
│  └─ ...
└─ sync_history.json
```

### Arquivo de Histórico

```json
{
  "syncs": [
    {
      "timestamp": "2026-03-08T15:30:00Z",
      "species_count": 5,
      "image_count": 42
    }
  ],
  "last_sync": "2026-03-08T15:30:00Z",
  "next_sync": "2026-03-08T16:30:00Z"
}
```

---

## 🔄 Workflow Completo

### Dia 1: Setup Inicial
```
1. python prepare_species.py --max-per-class 500
2. python train_species.py
3. Copiar .tflite e .h5 para app
4. Iniciar app
```

### Dia 2-30: Coleta de Dados
```
User tira foto
  ↓
App armazena (offline)
  ↓
App mostra "X fotos aguardando treinamento"
  ↓
User conecta WiFi
  ↓
Sync automático registra dados
```

### Quando Desejado: Fine-tune
```
python sync_and_finetune.py
  ↓ (3-5 min)
Modelo atualizado
  ↓
App detecta novo .tflite
  ↓
Recarrega modelo
  ↓
Acertividade melhora!
```

---

## 📱 UI Sugerida para o App

### Status Panel
```
┌─────────────────────────────────┐
│  Sincronização Automática       │
├─────────────────────────────────┤
│  Status: ✓ Conectado            │
│  Fotos aguardando: 42           │
│  Última sincronização: 2h atrás │
│                                 │
│  [Sincronizar Agora]            │
└─────────────────────────────────┘
```

### Código para Status UI
```typescript
const SyncStatus = () => {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const updateStatus = async () => {
      const syncStatus = await autoSyncService.getSyncStatus();
      setStatus(syncStatus);
    };

    updateStatus();
    const interval = setInterval(updateStatus, 30000); // A cada 30s
    return () => clearInterval(interval);
  }, []);

  if (!status) return null;

  return (
    <View>
      <Text>
        Fotos pendentes: {status.pending_images}
      </Text>
      <Text>
        Conectado: {status.is_connected ? '✓' : '✗'}
      </Text>
    </View>
  );
};
```

---

## ⚙️ Configurações

### Frequência de Sync
**Em `autoSyncService.ts` linha 124:**
```typescript
// Não sincronizar mais que uma vez por hora:
if (now - lastSyncTime < 3600000) { // 1 hora
```

Alterar para:
```typescript
if (now - lastSyncTime < 1800000) { // 30 minutos
```

### Threshold Mínimo de Imagens
**Em `autoSyncService.ts` linha 104:**
```typescript
if (pendingCount > 5) { // Sincronizar após 5 imagens
```

---

## 🔐 Segurança & Privacidade

✅ **100% offline**: Fotos nunca saem do dispositivo sem permissão
✅ **Opcional**: Fine-tuning pode ser local ou remoto
✅ **Controle**: Usuário pode limpar dados a qualquer momento

```typescript
// Limpar dados
await autoSyncService.clearPendingData();
```

---

## 📈 Roadmap

### Fase 1 (Atual) ✅
- ✅ Armazenar fotos do usuário
- ✅ Fine-tuning local
- ✅ Sincronização automática

### Fase 2 (Próxima)
- Servidor backend opcional para sincronização
- Dashboard de histórico
- Métricas de melhoria

### Fase 3 (Avançado)
- Federated learning
- Multiple device sync
- Model versioning

---

## 🐛 Troubleshooting

### Problema: Sync não funciona
**Solução:**
```bash
# Verificar se há fotos
ls user_training_data/

# Rodar manualmente
python sync_and_finetune.py --verbose
```

### Problema: Modelo não atualiza no app
**Solução:**
```
1. Verificar se model_species.tflite foi criado
2. Copiar para assets/models/
3. Reiniciar app com: npx expo start -c
```

### Problema: Fine-tuning muito lento
**Solução:**
- Reduzir FINE_TUNE_EPOCHS (3 para 2)
- Aumentar BATCH_SIZE (8 para 16)
- Usar GPU (instalar tensorflow-gpu)

---

## 📞 Support

Se precisar de ajustes:
1. Edite configurações em `sync_and_finetune.py`
2. Teste com `python sync_and_finetune.py --verbose`
3. Verifique logs em `sync_history.json`

---

**Pronto! Sistema de treinamento dinâmico 100% funcional!** 🚀
