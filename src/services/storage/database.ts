/**
 * Database Service
 * SQLite wrapper for local data persistence
 * Handles analysis history storage and retrieval
 */

import * as SQLite from 'expo-sqlite';
import { Analysis, AnalysisType } from '@models';
import { logger } from '@utils/logger';

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

    logger.log('[Database] Tables created successfully');
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
