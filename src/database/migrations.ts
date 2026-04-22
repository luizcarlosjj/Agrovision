/**
 * Database Migrations
 * Schemas e estrutura SQLite
 */

/**
 * Tabela analyses - Histórico de análises
 * Estendida com metadados para sincronização
 */
export const ANALYSES_TABLE = `
  CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('disease', 'pest', 'species', 'nutrient')),
    result TEXT NOT NULL,
    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
    description TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    imageUri TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    processingTime INTEGER NOT NULL,
    modelVersion TEXT,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL,
    datasetId TEXT,
    isStarred INTEGER DEFAULT 0,
    notes TEXT,
    syncedAt TEXT
  );

  CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type);
  CREATE INDEX IF NOT EXISTS idx_analyses_timestamp ON analyses(timestamp);
  CREATE INDEX IF NOT EXISTS idx_analyses_createdAt ON analyses(createdAt);
  CREATE INDEX IF NOT EXISTS idx_analyses_datasetId ON analyses(datasetId);
`;

/**
 * Tabela sync_queue - Fila de sincronização
 * Rastreia análises pendentes de envio para backend
 */
export const SYNC_QUEUE_TABLE = `
  CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    analysisId TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('pending', 'syncing', 'synced', 'failed')),
    retryCount INTEGER DEFAULT 0,
    maxRetries INTEGER DEFAULT 5,
    nextRetryAt TEXT,
    errorMessage TEXT,
    errorCode TEXT,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL,
    syncedAt TEXT,
    FOREIGN KEY(analysisId) REFERENCES analyses(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
  CREATE INDEX IF NOT EXISTS idx_sync_queue_nextRetryAt ON sync_queue(nextRetryAt);
  CREATE INDEX IF NOT EXISTS idx_sync_queue_createdAt ON sync_queue(createdAt);
`;

/**
 * Tabela users - Dados do usuário autenticado
 * Armazena credenciais e tokens para autenticação
 */
export const USERS_TABLE = `
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    authToken TEXT NOT NULL,
    refreshToken TEXT,
    tokenExpiry TEXT,
    lastLogin TEXT,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL,
    isActive INTEGER DEFAULT 1
  );

  CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
  CREATE INDEX IF NOT EXISTS idx_users_authToken ON users(authToken);
`;

/**
 * Tabela datasets - Coleções de análises do usuário
 * Permite organizar análises em grupos/projetos
 */
export const DATASETS_TABLE = `
  CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    userId TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    analysisCount INTEGER DEFAULT 0,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL,
    FOREIGN KEY(userId) REFERENCES users(id) ON DELETE CASCADE
  );

  CREATE INDEX IF NOT EXISTS idx_datasets_userId ON datasets(userId);
  CREATE INDEX IF NOT EXISTS idx_datasets_createdAt ON datasets(createdAt);
`;

/**
 * Tabela sync_events - Log de eventos de sincronização
 * Rastreia histórico de sincronizações para debugging
 */
export const SYNC_EVENTS_TABLE = `
  CREATE TABLE IF NOT EXISTS sync_events (
    id TEXT PRIMARY KEY,
    event TEXT NOT NULL,
    resourceType TEXT NOT NULL,
    resourceId TEXT,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    duration INTEGER,
    details TEXT,
    createdAt TEXT NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_sync_events_event ON sync_events(event);
  CREATE INDEX IF NOT EXISTS idx_sync_events_timestamp ON sync_events(timestamp);
  CREATE INDEX IF NOT EXISTS idx_sync_events_status ON sync_events(status);
`;

/**
 * Tabela cache_metadata - Cache de dados com TTL
 * Armazena dados em cache com expiração automática
 */
export const CACHE_METADATA_TABLE = `
  CREATE TABLE IF NOT EXISTS cache_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    expiresAt TEXT,
    createdAt TEXT NOT NULL,
    updatedAt TEXT NOT NULL
  );

  CREATE INDEX IF NOT EXISTS idx_cache_metadata_expiresAt ON cache_metadata(expiresAt);
`;

/**
 * Tabela app_config - Configurações da aplicação
 * Armazena preferências do usuário e metadados da app
 */
export const APP_CONFIG_TABLE = `
  CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    type TEXT NOT NULL,
    updatedAt TEXT NOT NULL
  );
`;

/**
 * Todas as tabelas em ordem de criação
 * (Respeitando foreign keys)
 */
export const ALL_MIGRATIONS = [
  USERS_TABLE,
  DATASETS_TABLE,
  ANALYSES_TABLE,
  SYNC_QUEUE_TABLE,
  SYNC_EVENTS_TABLE,
  CACHE_METADATA_TABLE,
  APP_CONFIG_TABLE,
];

/**
 * Version info para controle de migrations
 */
export const MIGRATION_VERSION = '1.0.0';

export const MIGRATION_HISTORY = {
  version: MIGRATION_VERSION,
  createdAt: '2026-03-04',
  tables: [
    { name: 'users', version: '1.0.0' },
    { name: 'datasets', version: '1.0.0' },
    { name: 'analyses', version: '1.0.0' },
    { name: 'sync_queue', version: '1.0.0' },
    { name: 'sync_events', version: '1.0.0' },
    { name: 'cache_metadata', version: '1.0.0' },
    { name: 'app_config', version: '1.0.0' },
  ],
};
