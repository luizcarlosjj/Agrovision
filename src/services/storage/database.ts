/**
 * Database Service
 * SQLite wrapper for local data persistence
 * Handles analysis history storage and retrieval
 */

import * as SQLite from 'expo-sqlite';
import * as FileSystem from 'expo-file-system/legacy';
import { Analysis, AnalysisType, XAITestRecord, FramingLabel } from '@models';
import { logger } from '@utils/logger';

const OVERLAY_DIR = `${FileSystem.documentDirectory}xai_overlays/`;

/**
 * Database service for SQLite operations
 */
class DatabaseService {
  private db: SQLite.SQLiteDatabase | null = null;
  private dbName = process.env.DB_NAME || 'agrovision.db';
  private isInitialized = false;

  /**
   * Initialize database and create tables
   */
  async initialize(): Promise<void> {
    try {
      if (this.isInitialized) {
        logger.log('[Database] Already initialized');
        return;
      }

      this.db = await SQLite.openDatabaseAsync(this.dbName);
      logger.log(`[Database] Database opened: ${this.dbName}`);

      await this.createTables();
      this.isInitialized = true;

      logger.log('[Database] Initialization complete');
    } catch (error) {
      logger.error('[Database] Initialization failed:', error);
      throw error;
    }
  }

  /**
   * Create necessary tables
   */
  private async createTables(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    // Analysis table
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        result TEXT NOT NULL,
        confidence REAL NOT NULL,
        description TEXT NOT NULL,
        recommendations TEXT NOT NULL,
        imageUri TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        processingTime INTEGER NOT NULL,
        createdAt TEXT NOT NULL,
        updatedAt TEXT NOT NULL
      );
    `);

    // Create index for faster queries
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_analyses_type ON analyses(type);
      CREATE INDEX IF NOT EXISTS idx_analyses_timestamp ON analyses(timestamp);
    `);

    // XAI test runs (Grad-CAM + Attention Leakage scientific mode)
    await this.db.execAsync(`
      CREATE TABLE IF NOT EXISTS xai_tests (
        id TEXT PRIMARY KEY,
        imageUri TEXT NOT NULL,
        prediction TEXT NOT NULL,
        confidence REAL NOT NULL,
        al REAL NOT NULL,
        afs REAL NOT NULL,
        threshold REAL NOT NULL,
        bboxJson TEXT NOT NULL,
        bboxStrategy TEXT NOT NULL,
        overlayB64 TEXT NOT NULL,
        overlayPath TEXT,
        layerUsed TEXT,
        label TEXT NOT NULL,
        createdAt TEXT NOT NULL
      );
    `);
    await this.db.execAsync(`
      CREATE INDEX IF NOT EXISTS idx_xai_tests_created ON xai_tests(createdAt);
      CREATE INDEX IF NOT EXISTS idx_xai_tests_label ON xai_tests(label);
    `);

    await this.runMigrations();

    logger.log('[Database] Tables created successfully');
  }

  private async runMigrations(): Promise<void> {
    if (!this.db) return;
    try {
      await this.db.execAsync(`ALTER TABLE xai_tests ADD COLUMN overlayPath TEXT`);
    } catch { /* column already exists */ }
    try {
      await this.db.execAsync(`ALTER TABLE xai_tests ADD COLUMN layerUsed TEXT`);
    } catch { /* column already exists */ }
  }

  private async saveOverlayFile(id: string, b64: string): Promise<string | null> {
    try {
      const info = await FileSystem.getInfoAsync(OVERLAY_DIR);
      if (!info.exists) {
        await FileSystem.makeDirectoryAsync(OVERLAY_DIR, { intermediates: true });
      }
      const path = `${OVERLAY_DIR}${id}.png`;
      await FileSystem.writeAsStringAsync(path, b64, {
        encoding: FileSystem.EncodingType.Base64,
      });
      return path;
    } catch (err) {
      logger.error('[Database] Failed to save overlay file', err);
      return null;
    }
  }

  private async deleteOverlayFile(path: string | undefined): Promise<void> {
    if (!path) return;
    try {
      await FileSystem.deleteAsync(path, { idempotent: true });
    } catch { /* ignore */ }
  }

  async saveXAITest(record: XAITestRecord): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    const overlayPath = record.overlayB64
      ? await this.saveOverlayFile(record.id, record.overlayB64)
      : null;
    await this.db.runAsync(
      `INSERT INTO xai_tests (
        id, imageUri, prediction, confidence, al, afs, threshold,
        bboxJson, bboxStrategy, overlayB64, overlayPath, layerUsed, label, createdAt
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        record.id,
        record.imageUri,
        record.prediction,
        record.confidence,
        record.al,
        record.afs,
        record.threshold,
        JSON.stringify(record.bbox),
        record.bboxStrategy,
        '',
        overlayPath ?? null,
        record.layerUsed ?? null,
        record.label,
        record.createdAt,
      ],
    );
    logger.log(`[Database] XAI test saved: ${record.id}`);
  }

  async getAllXAITests(limit = 200): Promise<XAITestRecord[]> {
    if (!this.db) throw new Error('Database not initialized');
    const rows = await this.db.getAllAsync<any>(
      `SELECT * FROM xai_tests ORDER BY createdAt DESC LIMIT ?`,
      [limit],
    );
    return rows.map((r) => this.mapRowToXAITest(r));
  }

  async deleteXAITest(id: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    const row = await this.db.getFirstAsync<{ overlayPath: string | null }>(
      `SELECT overlayPath FROM xai_tests WHERE id = ?`,
      [id],
    );
    await this.db.runAsync(`DELETE FROM xai_tests WHERE id = ?`, [id]);
    await this.deleteOverlayFile(row?.overlayPath ?? undefined);
    logger.log(`[Database] XAI test deleted: ${id}`);
  }

  async clearAllXAITests(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    const rows = await this.db.getAllAsync<{ overlayPath: string | null }>(
      `SELECT overlayPath FROM xai_tests WHERE overlayPath IS NOT NULL`,
    );
    await this.db.runAsync(`DELETE FROM xai_tests`);
    await Promise.all(rows.map((r) => this.deleteOverlayFile(r.overlayPath ?? undefined)));
    logger.log('[Database] All XAI tests cleared');
  }

  async updateXAITestLabel(id: string, label: FramingLabel): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');
    await this.db.runAsync(
      `UPDATE xai_tests SET label = ? WHERE id = ?`,
      [label, id],
    );
  }

  private mapRowToXAITest(row: any): XAITestRecord {
    let bbox = { x: 0, y: 0, width: 0, height: 0 };
    try {
      bbox = JSON.parse(row.bboxJson);
    } catch {
      // ignore malformed bbox
    }
    return {
      id: row.id,
      imageUri: row.imageUri,
      prediction: row.prediction,
      confidence: row.confidence,
      al: row.al,
      afs: row.afs,
      threshold: row.threshold,
      bbox,
      bboxStrategy: row.bboxStrategy,
      overlayB64: row.overlayB64 ?? '',
      overlayPath: row.overlayPath ?? undefined,
      layerUsed: row.layerUsed ?? '',
      label: row.label as FramingLabel,
      createdAt: row.createdAt,
    };
  }

  /**
   * Save analysis to database
   */
  async saveAnalysis(analysis: Analysis): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      await this.db.runAsync(
        `INSERT INTO analyses (
          id, type, result, confidence, description,
          recommendations, imageUri, timestamp, processingTime,
          createdAt, updatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          analysis.id,
          analysis.type,
          analysis.result,
          analysis.confidence,
          analysis.description,
          JSON.stringify(analysis.recommendations),
          analysis.imageUri,
          analysis.timestamp,
          analysis.processingTime,
          analysis.createdAt,
          analysis.updatedAt,
        ],
      );

      logger.log(`[Database] Analysis saved: ${analysis.id}`);
    } catch (error) {
      logger.error('[Database] Error saving analysis:', error);
      throw error;
    }
  }

  /**
   * Get all analyses from history
   */
  async getAllAnalyses(limit = 50, offset = 0): Promise<Analysis[]> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const results = await this.db.getAllAsync<any>(
        `SELECT * FROM analyses ORDER BY timestamp DESC LIMIT ? OFFSET ?`,
        [limit, offset],
      );

      logger.log(`[Database] Retrieved ${results.length} analyses`);

      return results.map((row) => this.mapRowToAnalysis(row));
    } catch (error) {
      logger.error('[Database] Error getting analyses:', error);
      throw error;
    }
  }

  async getAllAnalysesUnlimited(): Promise<Analysis[]> {
    if (!this.db) throw new Error('Database not initialized');
    const results = await this.db.getAllAsync<any>(
      `SELECT * FROM analyses ORDER BY timestamp DESC`,
    );
    return results.map((row) => this.mapRowToAnalysis(row));
  }

  async getAllXAITestsUnlimited(): Promise<XAITestRecord[]> {
    if (!this.db) throw new Error('Database not initialized');
    const rows = await this.db.getAllAsync<any>(
      `SELECT * FROM xai_tests ORDER BY createdAt DESC`,
    );
    return rows.map((r) => this.mapRowToXAITest(r));
  }

  /**
   * Get analyses by type
   */
  async getAnalysesByType(type: AnalysisType, limit = 50): Promise<Analysis[]> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const results = await this.db.getAllAsync<any>(
        `SELECT * FROM analyses WHERE type = ? ORDER BY timestamp DESC LIMIT ?`,
        [type, limit],
      );

      logger.log(`[Database] Retrieved ${results.length} analyses of type: ${type}`);

      return results.map((row) => this.mapRowToAnalysis(row));
    } catch (error) {
      logger.error('[Database] Error getting analyses by type:', error);
      throw error;
    }
  }

  /**
   * Get single analysis by ID
   */
  async getAnalysisById(id: string): Promise<Analysis | null> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const result = await this.db.getFirstAsync<any>(
        `SELECT * FROM analyses WHERE id = ?`,
        [id],
      );

      if (!result) {
        logger.log(`[Database] Analysis not found: ${id}`);
        return null;
      }

      logger.log(`[Database] Retrieved analysis: ${id}`);
      return this.mapRowToAnalysis(result);
    } catch (error) {
      logger.error('[Database] Error getting analysis by ID:', error);
      throw error;
    }
  }

  /**
   * Delete analysis by ID
   */
  async deleteAnalysis(id: string): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      await this.db.runAsync(`DELETE FROM analyses WHERE id = ?`, [id]);

      logger.log(`[Database] Analysis deleted: ${id}`);
    } catch (error) {
      logger.error('[Database] Error deleting analysis:', error);
      throw error;
    }
  }

  /**
   * Clear all analyses
   */
  async clearAllAnalyses(): Promise<void> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      await this.db.runAsync(`DELETE FROM analyses`);

      logger.log('[Database] All analyses cleared');
    } catch (error) {
      logger.error('[Database] Error clearing analyses:', error);
      throw error;
    }
  }

  /**
   * Get total count of analyses
   */
  async getAnalysisCount(): Promise<number> {
    if (!this.db) throw new Error('Database not initialized');

    try {
      const result = await this.db.getFirstAsync<{ count: number }>(
        `SELECT COUNT(*) as count FROM analyses`,
      );

      const count = result?.count ?? 0;
      logger.log(`[Database] Total analyses: ${count}`);

      return count;
    } catch (error) {
      logger.error('[Database] Error getting count:', error);
      throw error;
    }
  }

  /**
   * Maps database row to Analysis object
   */
  private mapRowToAnalysis(row: any): Analysis {
    return {
      id: row.id,
      type: row.type as AnalysisType,
      result: row.result,
      confidence: row.confidence,
      description: row.description,
      recommendations: row.recommendations ? JSON.parse(row.recommendations) : [],
      imageUri: row.imageUri,
      timestamp: row.timestamp,
      processingTime: row.processingTime,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    };
  }

  /**
   * Close database connection
   */
  async close(): Promise<void> {
    if (this.db) {
      await this.db.closeAsync();
      this.db = null;
      this.isInitialized = false;
      logger.log('[Database] Connection closed');
    }
  }
}

// Export singleton instance
export const databaseService = new DatabaseService();
