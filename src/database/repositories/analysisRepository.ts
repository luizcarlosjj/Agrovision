/**
 * Analysis Repository
 * Gerencia dados de análises no banco de dados local
 */

import { Analysis } from '@models';
import { BaseRepository, PaginatedResult, PaginationOptions } from './baseRepository';
import { logger } from '@utils/logger';

export class AnalysisRepository extends BaseRepository<Analysis> {
  protected tableName = 'analyses';

  protected mapRow(row: any): Analysis {
    return {
      id: row.id,
      type: row.type as any,
      result: row.result,
      confidence: row.confidence,
      description: row.description,
      recommendations: JSON.parse(row.recommendations || '[]'),
      imageUri: row.imageUri,
      timestamp: row.timestamp,
      processingTime: row.processingTime,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
      modelVersion: row.modelVersion,
      datasetId: row.datasetId,
      isStarred: row.isStarred === 1,
      notes: row.notes,
      syncedAt: row.syncedAt,
    };
  }

  protected toColumns(entity: any): Record<string, any> {
    return {
      id: entity.id,
      type: entity.type,
      result: entity.result,
      confidence: entity.confidence,
      description: entity.description,
      recommendations: JSON.stringify(entity.recommendations || []),
      imageUri: entity.imageUri,
      timestamp: entity.timestamp,
      processingTime: entity.processingTime,
      createdAt: entity.createdAt,
      updatedAt: entity.updatedAt,
      modelVersion: entity.modelVersion,
      datasetId: entity.datasetId || null,
      isStarred: entity.isStarred ? 1 : 0,
      notes: entity.notes || null,
      syncedAt: entity.syncedAt || null,
    };
  }

  /**
   * Obter análises por tipo
   */
  async getByType(
    type: 'disease' | 'pest' | 'species' | 'nutrient',
    pagination?: PaginationOptions,
  ): Promise<PaginatedResult<Analysis>> {
    try {
      return await this.getAll(pagination, { type });
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting by type:', error);
      throw error;
    }
  }

  /**
   * Obter análises recentes
   */
  async getRecent(limit: number = 10): Promise<Analysis[]> {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        ORDER BY createdAt DESC
        LIMIT ?
      `;
      const results = await this.execQuery<any>(query, [limit]);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting recent:', error);
      throw error;
    }
  }

  /**
   * Obter análises não sincronizadas
   */
  async getUnsyncedAnalyses(): Promise<Analysis[]> {
    try {
      const query = `
        SELECT a.* FROM ${this.tableName} a
        WHERE a.syncedAt IS NULL
        ORDER BY a.createdAt ASC
      `;
      const results = await this.execQuery<any>(query);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting unsynced:', error);
      throw error;
    }
  }

  /**
   * Marcar análise como sincronizada
   */
  async markAsSynced(id: string): Promise<void> {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET syncedAt = datetime('now'), updatedAt = datetime('now')
        WHERE id = ?
      `;
      await this.db.runAsync(query, [id]);
      logger.log(`[AnalysisRepository] Analysis marked as synced: ${id}`);
    } catch (error) {
      logger.error('[AnalysisRepository] Error marking as synced:', error);
      throw error;
    }
  }

  /**
   * Buscar análises por dataset
   */
  async getByDatasetId(datasetId: string, pagination?: PaginationOptions): Promise<PaginatedResult<Analysis>> {
    try {
      return await this.getAll(pagination, { datasetId });
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting by dataset:', error);
      throw error;
    }
  }

  /**
   * Buscar análises por intervalo de datas
   */
  async getByDateRange(startDate: string, endDate: string): Promise<Analysis[]> {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
      `;
      const results = await this.execQuery<any>(query, [startDate, endDate]);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting by date range:', error);
      throw error;
    }
  }

  /**
   * Contar por tipo
   */
  async countByType(): Promise<Record<string, number>> {
    try {
      const query = `
        SELECT type, COUNT(*) as count
        FROM ${this.tableName}
        GROUP BY type
      `;
      const results = await this.execQuery<any>(query);
      return results.reduce(
        (acc, row) => ({
          ...acc,
          [row.type]: row.count,
        }),
        {}
      );
    } catch (error) {
      logger.error('[AnalysisRepository] Error counting by type:', error);
      throw error;
    }
  }

  /**
   * Obter análises com maior confiança
   */
  async getHighConfidence(minConfidence: number = 0.85, limit: number = 10): Promise<Analysis[]> {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE confidence >= ?
        ORDER BY confidence DESC
        LIMIT ?
      `;
      const results = await this.execQuery<any>(query, [minConfidence, limit]);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting high confidence:', error);
      throw error;
    }
  }

  /**
   * Marcar/desmarcar como favorita
   */
  async toggleStarred(id: string): Promise<void> {
    try {
      const analysis = await this.getById(id);
      if (!analysis) {
        throw new Error(`Analysis not found: ${id}`);
      }

      const query = `
        UPDATE ${this.tableName}
        SET isStarred = ?, updatedAt = datetime('now')
        WHERE id = ?
      `;
      await this.db.runAsync(query, [analysis.isStarred ? 0 : 1, id]);
    } catch (error) {
      logger.error('[AnalysisRepository] Error toggling starred:', error);
      throw error;
    }
  }

  /**
   * Obter análises favoritas
   */
  async getStarred(): Promise<Analysis[]> {
    try {
      const query = `
        SELECT * FROM ${this.tableName}
        WHERE isStarred = 1
        ORDER BY createdAt DESC
      `;
      const results = await this.execQuery<any>(query);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting starred:', error);
      throw error;
    }
  }

  /**
   * Adicionar nota à análise
   */
  async addNote(id: string, note: string): Promise<void> {
    try {
      const query = `
        UPDATE ${this.tableName}
        SET notes = ?, updatedAt = datetime('now')
        WHERE id = ?
      `;
      await this.db.runAsync(query, [note, id]);
    } catch (error) {
      logger.error('[AnalysisRepository] Error adding note:', error);
      throw error;
    }
  }

  /**
   * Buscar por texto (result ou description)
   */
  async search(query: string): Promise<Analysis[]> {
    try {
      const searchQuery = `%${query}%`;
      const sql = `
        SELECT * FROM ${this.tableName}
        WHERE result LIKE ? OR description LIKE ? OR notes LIKE ?
        ORDER BY createdAt DESC
      `;
      const results = await this.execQuery<any>(sql, [searchQuery, searchQuery, searchQuery]);
      return results.map(row => this.mapRow(row));
    } catch (error) {
      logger.error('[AnalysisRepository] Error searching:', error);
      throw error;
    }
  }

  /**
   * Obter estatísticas gerais
   */
  async getStats(): Promise<{
    total: number;
    avgConfidence: number;
    byType: Record<string, number>;
    lastAnalysis: Analysis | null;
  }> {
    try {
      const totalCount = await this.count();
      const countByType = await this.countByType();
      const recent = await this.getRecent(1);

      const countQuery = `
        SELECT AVG(confidence) as avgConfidence
        FROM ${this.tableName}
      `;
      const statsResult = await this.execQuerySingle<any>(countQuery);

      return {
        total: totalCount,
        avgConfidence: statsResult?.avgConfidence || 0,
        byType: countByType,
        lastAnalysis: recent[0] || null,
      };
    } catch (error) {
      logger.error('[AnalysisRepository] Error getting stats:', error);
      throw error;
    }
  }
}
