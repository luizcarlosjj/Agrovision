# AgroVision Mobile - Estrutura de Projeto Detalhada

## 📁 Árvore de Arquivos Completa

```
agrovision-mobile/
│
├── src/
│   ├── App.tsx                                  # Entry point da aplicação
│   ├── index.tsx                                # Inicialização React Native
│   │
│   ├── components/                              # Componentes reutilizáveis
│   │   ├── ui/                                  # Componentes básicos
│   │   │   ├── Button.tsx                       # Botão customizado
│   │   │   ├── Card.tsx                         # Card para seções
│   │   │   ├── LoadingSpinner.tsx               # Indicador de carregamento
│   │   │   ├── ErrorBanner.tsx                  # Exibir erros
│   │   │   ├── ImagePreview.tsx                 # Preview de foto
│   │   │   └── index.ts                         # Exports centralizados
│   │   │
│   │   └── common/                              # Componentes compartilhados
│   │       ├── Header.tsx                       # Header com título
│   │       ├── SafeAreaWrapper.tsx              # Wrapper de safe area
│   │       ├── Layout.tsx                       # Layout base
│   │       └── index.ts
│   │
│   ├── screens/                                 # Telas da aplicação
│   │   ├── HomeScreen.tsx                       # Menu principal
│   │   ├── CameraScreen.tsx                     # Captura de imagem
│   │   ├── ProcessingScreen.tsx                 # Loading da análise
│   │   ├── ResultScreen.tsx                     # Resultado da análise
│   │   ├── HistoryScreen.tsx                    # Histórico (futuro)
│   │   └── index.ts
│   │
│   ├── navigation/                              # Configuração de navegação
│   │   ├── RootNavigator.tsx                    # Stack navigator principal
│   │   ├── types.ts                             # Types de navegação
│   │   └── index.ts
│   │
│   ├── services/                                # Serviços da aplicação
│   │   │
│   │   ├── api/                                 # API e HTTP
│   │   │   ├── analysisService.ts               # Mock service de análise
│   │   │   ├── client.ts                        # axios configurado
│   │   │   └── index.ts
│   │   │
│   │   ├── storage/                             # Persistência de dados
│   │   │   ├── database.ts                      # SQLite setup e operações
│   │   │   ├── migrations.ts                    # Migrações do DB
│   │   │   └── index.ts
│   │   │
│   │   ├── camera/                              # Serviços de câmera
│   │   │   ├── cameraService.ts                 # Wrapper de permissões e foto
│   │   │   └── index.ts
│   │   │
│   │   └── index.ts                             # Exports centralizados
│   │
│   ├── hooks/                                   # Custom hooks
│   │   ├── useAnalysis.ts                       # Hook para análise
│   │   ├── useCamera.ts                         # Hook para câmera
│   │   ├── useHistory.ts                        # Hook para histórico
│   │   ├── useAsyncStorage.ts                   # Hook para AsyncStorage
│   │   ├── useAppState.ts                       # Hook estado global
│   │   └── index.ts
│   │
│   ├── models/                                  # Types e Interfaces
│   │   ├── api.ts                               # Tipos de API
│   │   ├── analysis.ts                          # Tipos de análise
│   │   ├── plant.ts                             # Tipos de planta
│   │   ├── history.ts                           # Tipos de histórico
│   │   └── index.ts
│   │
│   ├── context/                                 # Context API
│   │   ├── AnalysisContext.tsx                  # Context de análise
│   │   ├── AnalysisProvider.tsx                 # Provider wrapper
│   │   ├── AppContext.tsx                       # Context global
│   │   ├── AppProvider.tsx                      # Provider wrapper
│   │   └── index.ts
│   │
│   ├── utils/                                   # Funções utilitárias
│   │   ├── format.ts                            # Formatação de strings/data
│   │   ├── validators.ts                        # Validações
│   │   ├── logger.ts                            # Sistema de logs
│   │   ├── constants.ts                         # Constantes da app
│   │   ├── errors.ts                            # Classes de erro customizadas
│   │   └── index.ts
│   │
│   └── styles/                                  # Estilos globais
│       ├── theme.ts                             # Cores, tipografia, espaçamento
│       ├── globalStyles.ts                      # Estilos globais
│       └── index.ts
│
├── assets/                                      # Imagens, ícones, fontes
│   ├── images/
│   │   ├── logo.png
│   │   ├── plant-icon.png
│   │   └── ...
│   ├── icons/
│   │   ├── camera.png
│   │   ├── disease.png
│   │   ├── pest.png
│   │   ├── species.png
│   │   └── nutrient.png
│   └── fonts/
│       └── (se usar fontes customizadas)
│
├── .env.example                                 # Template de variáveis de ambiente
├── .env                                         # Variáveis de ambiente (git ignored)
├── .gitignore                                   # Arquivos a ignorar no git
│
├── app.json                                     # Configuração do Expo
├── eas.json                                     # Configuração EAS Build
├── tsconfig.json                                # Configuração TypeScript
├── package.json                                 # Dependências do projeto
├── package-lock.json                            # Lock file
│
├── README.md                                    # Documentação do projeto
├── DISCOVERY.md                                 # Documento de discovery (você)
├── ARCHITECTURE.md                              # Documento de arquitetura (você)
├── API_SPECIFICATION.md                         # Especificação de API (você)
└── PROJECT_STRUCTURE.md                         # Este arquivo
```

---

## 📋 Descrição Detalhada de Cada Diretório

### 1. `/src/components/ui/`

Componentes reutilizáveis de UI sem lógica de negócio.

```typescript
// Button.tsx
interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  loading?: boolean;
}

export function Button({ title, onPress, variant = 'primary', ...props }: ButtonProps) {
  return <TouchableOpacity onPress={onPress} {...props}>
    <Text>{title}</Text>
  </TouchableOpacity>;
}

// Utilizável em qualquer tela sem dependências externas
```

---

### 2. `/src/screens/`

Componentes de tela que orquestram a UI e lógica.

**Padrão de implementação:**
```typescript
// Sempre segue esse padrão
function XyzScreen() {
  // 1. Navegação
  const navigation = useNavigation<ScreenNavigationProp>();

  // 2. Hooks customizados
  const { state, action } = useXyzHook();

  // 3. Efeitos
  useEffect(() => {
    // Setup
  }, []);

  // 4. Render
  return (
    <SafeAreaWrapper>
      {/* JSX */}
    </SafeAreaWrapper>
  );
}
```

---

### 3. `/src/services/api/`

**analysisService.ts** - Mock de análise de imagem

```typescript
class AnalysisService {
  // Métodos principais:
  async analyzeImage(imageUri: string, type: AnalysisType): Promise<AnalysisResponse>
  private getRandomMockForType(type: AnalysisType): MockResponse
  private simulateProcessing(): Promise<number>
  private generateUUID(): string
}

// Será substituído por requisição HTTP real quando backend estiver pronto
```

**client.ts** - Cliente axios configurado

```typescript
const apiClient = axios.create({
  baseURL: process.env.API_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptadores para logging, erros, etc
```

---

### 4. `/src/services/storage/`

**database.ts** - Wrapper do SQLite

```typescript
class DatabaseService {
  async initializeDatabase(): Promise<void>
  async saveAnalysis(analysis: Analysis): Promise<void>
  async getAnalysisHistory(limit?: number): Promise<Analysis[]>
  async deleteAnalysis(id: string): Promise<void>
  async clearHistory(): Promise<void>
  async getAnalysisById(id: string): Promise<Analysis | null>
}

// Isolamento de lógica de banco de dados
```

---

### 5. `/src/hooks/`

Encapsulam lógica reutilizável de componentes.

**useAnalysis.ts**
```typescript
function useAnalysis() {
  const { state, dispatch } = useContext(AnalysisContext);

  const analyze = useCallback(async (imageUri: string, type: AnalysisType) => {
    // Lógica de análise orquestrada aqui
  }, [dispatch]);

  return {
    currentAnalysis: state.currentAnalysis,
    isLoading: state.isLoading,
    error: state.error,
    analyze
  };
}
```

**useCamera.ts**
```typescript
function useCamera() {
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    // Pedir permissões
  }, []);

  const takePhoto = useCallback(async () => {
    // Capturar foto
  }, [cameraRef]);

  return { hasPermission, takePhoto, cameraRef };
}
```

---

### 6. `/src/models/`

**Types TypeScript puros - nenhuma lógica aqui!**

```typescript
// analysis.ts
export type AnalysisType = 'disease' | 'pest' | 'species' | 'nutrient';

export interface Analysis {
  id: string;
  type: AnalysisType;
  result: string;
  confidence: number;
  description: string;
  recommendations: string[];
  imageUri: string;
  timestamp: string;
  processingTime: number;
}

// Esses tipos são reutilizados em toda a aplicação
```

---

### 7. `/src/context/`

**AnalysisContext.tsx** + **AnalysisProvider.tsx**

```typescript
// Separação clara entre context e provider

// AnalysisContext.tsx
export const AnalysisContext = React.createContext<AnalysisContextType | undefined>(undefined);

// AnalysisProvider.tsx
export function AnalysisProvider({ children }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  return (
    <AnalysisContext.Provider value={{ state, dispatch }}>
      {children}
    </AnalysisContext.Provider>
  );
}

// Hook de consumo
export function useAnalysisContext() {
  const context = useContext(AnalysisContext);
  if (!context) throw new Error('useAnalysisContext deve ser usado dentro de AnalysisProvider');
  return context;
}
```

---

### 8. `/src/utils/`

Funções utilitárias puras e reutilizáveis.

```typescript
// format.ts
export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatDate(date: Date): string {
  // Formatação de data
}

// validators.ts
export function isValidImageUri(uri: string): boolean {
  // Validar URI de imagem
}

// logger.ts
export const logger = {
  log: (message: string) => console.log(`[APP] ${message}`),
  error: (message: string, error?: any) => console.error(`[ERROR] ${message}`, error),
  warn: (message: string) => console.warn(`[WARN] ${message}`)
};
```

---

### 9. `/src/styles/`

**theme.ts** - Design system centralizado

```typescript
export const COLORS = {
  primary: '#2D8659',      // Verde agrícola
  secondary: '#FFA500',    // Laranja
  danger: '#DC3545',       // Vermelho para doenças
  success: '#28A745',      // Verde para saudável
  background: '#FFFFFF',
  text: '#333333',
  border: '#CCCCCC'
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32
};

export const TYPOGRAPHY = {
  title: { fontSize: 28, fontWeight: 'bold' },
  heading: { fontSize: 20, fontWeight: '600' },
  body: { fontSize: 16, fontWeight: '400' },
  caption: { fontSize: 12, fontWeight: '400' }
};
```

---

## 🔄 Fluxo de Importações

**Sempre preferir imports do index.ts**

```typescript
// ✅ BOM - centralizado
import { Button, Card } from '@/components/ui';
import { HomeScreen } from '@/screens';
import { useAnalysis } from '@/hooks';

// ❌ EVITAR - imports diretos
import Button from '@/components/ui/Button';
import HomeScreen from '@/screens/HomeScreen';
```

---

## 📦 Configurações de Tsconfig

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"],
      "@screens/*": ["src/screens/*"],
      "@services/*": ["src/services/*"],
      "@hooks/*": ["src/hooks/*"],
      "@models/*": ["src/models/*"],
      "@utils/*": ["src/utils/*"],
      "@styles/*": ["src/styles/*"]
    }
  }
}
```

**Permite importações limpas com `@/`**

---

## 📝 Padrões de Arquivo

### Componente de UI
```typescript
import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
}

export function Button({ title, onPress }: ButtonProps) {
  return (
    <TouchableOpacity style={styles.button} onPress={onPress}>
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: { /* estilos */ },
  text: { /* estilos */ }
});
```

### Tela
```typescript
import React, { useEffect } from 'react';
import { View } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAnalysis } from '@hooks';

export function HomeScreen() {
  const navigation = useNavigation();
  const { analyze } = useAnalysis();

  return <View>{/* JSX */}</View>;
}
```

### Service
```typescript
class XyzService {
  async methodName(): Promise<ReturnType> {
    // Implementação
  }
}

export const xyzService = new XyzService();
```

### Hook
```typescript
export function useXyz() {
  const [state, setState] = useState<StateType>(initialValue);

  useEffect(() => {
    // Setup
  }, []);

  return { state, /* métodos */ };
}
```

---

## ✅ Checklist de Estrutura

- [ ] Pasta `/src` criada com todos os subdiretórios
- [ ] Arquivo `index.ts` em cada diretório com exports
- [ ] `tsconfig.json` configurado com path aliases
- [ ] `package.json` com todas as dependências
- [ ] `.env.example` criado
- [ ] `.gitignore` configurado
- [ ] `app.json` do Expo configurado
- [ ] Documentação de estrutura completa

---

**Próxima Etapa:** Gerar código de cada arquivo seguindo essa estrutura
