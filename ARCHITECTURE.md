# AgroVision Mobile - Arquitetura e Design

## 🏗️ Visão Geral da Arquitetura

O projeto segue uma **arquitetura modular em camadas**, com separação clara de responsabilidades:

```
┌─────────────────────────────────────────┐
│           UI Layer (Screens)            │
│   (HomeScreen, CameraScreen, etc)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Components & Hooks Layer         │
│  (useAnalysis, useCamera, useHistory)   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Context API / State Layer        │
│   (AnalysisContext, AppContext)         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Services Layer                  │
│   (API, Database, Camera, Logger)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Models / Types Layer             │
│  (TypeScript Interfaces & Types)        │
└─────────────────────────────────────────┘
```

---

## 📋 Detalhamento de Cada Camada

### 1️⃣ Models/Types Layer (`src/models/`)

Define toda a tipagem TypeScript do projeto.

**Responsabilidades:**
- Interfaces de dados da API
- Types de análise
- Tipos de resposta do servidor
- Enums para tipos de análise

**Arquivos:**
- `api.ts` - Tipos de requisição/resposta
- `analysis.ts` - Dados de análise
- `plant.ts` - Dados da planta
- `history.ts` - Histórico de diagnósticos

---

### 2️⃣ Services Layer (`src/services/`)

Lógica de negócio isolada, pronta para trocar implementações.

#### **API Service** (`services/api/`)
```typescript
// analysisService.ts - Mock da API
export interface AnalysisResponse {
  type: AnalysisType;
  result: string;
  confidence: number;
  description: string;
  recommendations: string[];
}

class AnalysisService {
  async analyzeImage(
    imageUri: string,
    type: AnalysisType
  ): Promise<AnalysisResponse> {
    // Simula delay de processamento
    // Retorna mock response baseado no tipo
  }
}
```

#### **Database Service** (`services/storage/`)
```typescript
// database.ts - SQLite wrapper
class DatabaseService {
  async initializeDatabase(): Promise<void>
  async saveAnalysis(analysis: Analysis): Promise<void>
  async getAnalysisHistory(): Promise<Analysis[]>
  async deleteAnalysis(id: string): Promise<void>
}
```

#### **Camera Service** (`services/camera/`)
```typescript
// cameraService.ts - Wrapper da câmera
class CameraService {
  async requestPermissions(): Promise<boolean>
  async takePhoto(): Promise<string> // Retorna URI
  async getPhoto(uri: string): Promise<Buffer>
}
```

---

### 3️⃣ Context API / State Layer (`src/context/`)

Gerenciamento de estado global usando Context API com useReducer.

#### **AnalysisContext**
```typescript
interface AnalysisState {
  currentAnalysis: Analysis | null;
  isLoading: boolean;
  error: string | null;
  history: Analysis[];
}

type AnalysisAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ANALYSIS'; payload: Analysis }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'ADD_TO_HISTORY'; payload: Analysis }
  | { type: 'CLEAR_ANALYSIS' };

// useAnalysisContext() hook customizado
```

**Vantagens dessa abordagem:**
- ✅ Isolamento de estado global
- ✅ Fácil de testar
- ✅ Escalável para Zustand se necessário
- ✅ Sem dependências externas no MVP

---

### 4️⃣ Hooks Layer (`src/hooks/`)

Hooks customizados que encapsulam lógica repetida.

```typescript
// useAnalysis.ts - Hook para análise
export function useAnalysis() {
  const { state, dispatch } = useContext(AnalysisContext);

  const analyze = useCallback(async (imageUri: string, type: AnalysisType) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const result = await analysisService.analyzeImage(imageUri, type);
      dispatch({ type: 'SET_ANALYSIS', payload: result });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  }, []);

  return { ...state, analyze };
}

// useCamera.ts - Hook para câmera
export function useCamera() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    checkPermissions();
  }, []);

  const takePhoto = useCallback(async () => {
    // Lógica de captura
  }, []);

  return { hasPermission, takePhoto, cameraRef };
}

// useHistory.ts - Hook para histórico
export function useHistory() {
  const { history } = useContext(AnalysisContext);
  // Lógica de histórico
}
```

---

### 5️⃣ Components Layer (`src/components/`)

Componentes reutilizáveis da UI, sem lógica de negócio pesada.

```
components/
├── ui/
│   ├── Button.tsx           # Botão genérico
│   ├── Card.tsx             # Card genérico
│   ├── LoadingSpinner.tsx    # Indicador de carregamento
│   ├── ImagePreview.tsx      # Preview de imagem
│   └── ErrorBanner.tsx       # Exibição de erros
├── common/
│   ├── Header.tsx            # Header comum
│   ├── SafeAreaWrapper.tsx    # Wrapper de safe area
│   └── Layout.tsx            # Layout base
```

**Princípios:**
- Componentes "burros" (dumb components)
- Props bem tipadas
- Sem lógica de estado complexa
- Reutilizáveis em múltiplas telas

---

### 6️⃣ Screens Layer (`src/screens/`)

Telas principais do aplicativo. Cada tela:
- Usa hooks customizados
- Integra com Context
- Compõe componentes
- Gerencia navegação

```
screens/
├── HomeScreen.tsx           # Menu principal
├── CameraScreen.tsx         # Captura de foto
├── ProcessingScreen.tsx      # Loading da análise
├── ResultScreen.tsx          # Exibição de resultado
└── HistoryScreen.tsx         # Histórico (futuro)
```

---

### 7️⃣ Navigation Layer (`src/navigation/`)

Configuração centralizados de navegação com React Navigation.

```typescript
// RootNavigator.tsx
type RootStackParamList = {
  Home: undefined;
  Camera: { analysisType: AnalysisType };
  Processing: { imageUri: string; type: AnalysisType };
  Result: { analysis: Analysis };
};

export function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Camera" component={CameraScreen} />
        {/* ... */}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**Type-safe navigation** com TypeScript

---

## 🔄 Fluxo de Dados

### Exemplo: Fluxo de Análise de Doença

```
HomeScreen (user selects "Detect Disease")
    ↓
    navigate("Camera", { analysisType: "disease" })
    ↓
CameraScreen (user takes photo)
    ↓
    navigate("Processing", { imageUri, analysisType })
    ↓
ProcessingScreen
    ├─ dispatch(SET_LOADING, true)
    ├─ call analysisService.analyzeImage()
    ├─ dispatch(SET_ANALYSIS, result)
    ├─ dispatch(ADD_TO_HISTORY, result)
    └─ navigate("Result", { analysis })
    ↓
ResultScreen (displays diagnosis)
    ↓
User can navigate back to Home or Camera
```

---

## 📦 Dependências Principais

```json
{
  "dependencies": {
    "react-native": "latest via expo",
    "expo": "^51.x",
    "react-navigation": "^6.x",
    "react-native-screens": "^3.x",
    "expo-camera": "^14.x",
    "expo-sqlite": "^14.x",
    "axios": "^1.x",
    "typescript": "^5.x"
  }
}
```

---

## 🔐 Preparação para ML Integration

### Estrutura preparada para TensorFlow Lite:

```typescript
// services/ml/tensorflowService.ts (Será criado depois)
class TensorFlowService {
  async loadModel(modelPath: string): Promise<void>
  async predict(imageBuffer: Buffer): Promise<Prediction>
  async unloadModel(): Promise<void>
}

// Integração futura:
const result = await tensorflowService.predict(imageBuffer);
// Substitui analysisService.analyzeImage()
```

---

## 🔄 Preparação para Backend Python

### API Service atual (mock):
```typescript
// Fase 1: Mock local (CurrentState)
class AnalysisService {
  async analyzeImage(imageUri: string, type: AnalysisType) {
    return generateMockResponse(type); // Fake
  }
}

// Fase 2: Backend Python (Próximo)
class AnalysisService {
  async analyzeImage(imageUri: string, type: AnalysisType) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('type', type);

    const response = await apiClient.post('/analyze', formData);
    return response.data; // Real backend
  }
}
```

---

## 📊 State Management Escalability

### Atual (Context API)
```typescript
// MVP - simples e eficaz
const { state, dispatch } = useContext(AnalysisContext);
```

### Futuro (Zustand - se necessário)
```typescript
// Mais poderoso quando escala
const state = useAnalysisStore((state) => state);
```

**Padrão usado deixa fácil a migração** ✅

---

## ✅ Checklist de Implementação

- [ ] Estrutura de pastas criada
- [ ] package.json e dependências instaladas
- [ ] TypeScript configurado
- [ ] Models/Types definidos
- [ ] Services implementados (mock)
- [ ] Context API configurado
- [ ] Hooks customizados criados
- [ ] Components básicos desenvolvidos
- [ ] Screens implementadas
- [ ] Navegação funcionando
- [ ] Teste E2E do fluxo completo

---

**Próxima Etapa:** Geração de código seguindo esta arquitetura
