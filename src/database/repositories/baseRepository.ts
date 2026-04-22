/**
 * Base Repository
 * Classe abstrata com operações CRUD comuns
 */

import { logger } from '@utils/logger';

/**
 * Resultado de consulta com paginação
 */
export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/**
 * Opções de paginação
 */
export interface PaginationOptions {
  page?: number;
  pageSize?: number;
  offset?: number;
  limit?: number;
}

/**
 * Opções de filtro
 */
export interface FilterOptions {
  [key: string]: any;
}

/**
 * Classe base para repositórios
 */
export abstract class BaseRepository<T> {
  protected abstract tableName: string;

  /**
   * Função para mapear resultado do banco para o tipo T
   */
  protected abstract mapRow(row: any): T;

  /**
   * Função para mapear objeto T para colunas do banco
   */
  protected abstract toColumns(entity: T): Record<string, any>;

  /**
   * Construtor com acesso ao banco de dados
   */
  constructor(protected db: any) {} // SQLite database instance

  /**
   * Obter registro por ID
   */
  async getById(id: string): Promise<T | null> {
    try {
      const query = `SELECT * FROM ${this.tableName} WHERE id = ?`;
      const result = await this.db.getAsync(query, [id]);

      if (!result) {
        return null;
      }

      return this.mapRow(result);
    } catch (error) {
      logger.error(`[${this.tableName}] Error getting by ID:`, error);
      throw error;
    }
  }

  /**
   * Obter todos os registros
   */
  async getAll(
    pagination?: PaginationOptions,
    filters?: FilterOptions,
  ): Promise<PaginatedResult<T>> {
    try {
      let query = `SELECT * FROM ${this.tableName}`;
      const params: any[] = [];

      // Aplicar filtros
      if (filters && Object.keys(filters).length > 0) {
        const filterClauses = Object.entries(filters)
          .map(([key, value]) => {
            if (value === null) {
              return `${key} IS NULL`;
            }
            params.push(value);
            return `${key} = ?`;
          });
        query += ` WHERE ${filterClauses.join(' AND ')}`;
      }

      // Contar total
      const countQuery = `SELECT COUNT(*) as count FROM ${this.tableName}` +
        (filters ? ` WHERE ${Object.keys(filters).map(k => `${k} = ?`).join(' AND ')}` : '');
      const countResult = await this.db.getAsync(countQuery, params);
      const total = countResult?.count || 0;

      // Paginação
      const { page = 1, pageSize = 20 } = pagination || {};
      const offset = (page - 1) * pageSize;

      query += ` ORDER BY createdAt DESC LIMIT ? OFFSET ?`;
      params.push(pageSize, offset);

      const results = await this.db.allAsync(query, params);

      return {
        data: results.map((row: any) => this.mapRow(row)),
        total,
        page,
        pageSize,
        hasMore: offset + results.length < total,
      };
    } catch (error) {
      logger.error(`[${this.tableName}] Error getting all:`, error);
      throw error;
    }
  }

  /**
   * Criar novo registro
   */
  async create(entity: T): Promise<T> {
    try {
      const columns = this.toColumns(entity);
      const keys = Object.keys(columns);
      const placeholders = keys.map(() => '?').join(', ');

      const query = `INSERT INTO ${this.tableName} (${keys.join(', ')})
                     VALUES (${placeholders})`;

      const params = keys.map(key => columns[key]);

      await this.db.runAsync(query, params);

      return entity;
    } catch (error) {
      logger.error(`[${this.tableName}] Error creating:`, error);
      throw error;
    }
  }

  /**
   * Atualizar registro
   */
  async update(id: string, partialEntity: Partial<T>): Promise<void> {
    try {
      const columns = this.toColumns(partialEntity as T);
      delete (columns as any).id; // Não permitir mudar ID

      const keys = Object.keys(columns);
      if (keys.length === 0) {
        return; // Nada para atualizar
      }

      const setClauses = keys.map(key => `${key} = ?`).join(', ');
      const params = [...keys.map(key => columns[key]), id];

      const query = `UPDATE ${this.tableName}
                     SET ${setClauses}, updatedAt = datetime('now')
                     WHERE id = ?`;

      await this.db.runAsync(query, params);
    } catch (error) {
      logger.error(`[${this.tableName}] Error updating:`, error);
      throw error;
    }
  }

  /**
   * Deletar registro
   */
  async delete(id: string): Promise<void> {
    try {
      const query = `DELETE FROM ${this.tableName} WHERE id = ?`;
      await this.db.runAsync(query, [id]);
    } catch (error) {
      logger.error(`[${this.tableName}] Error deleting:`, error);
      throw error;
    }
  }

  /**
   * Deletar múltiplos registros
   */
  async deleteMany(ids: string[]): Promise<number> {
    try {
      const placeholders = ids.map(() => '?').join(', ');
      const query = `DELETE FROM ${this.tableName} WHERE id IN (${placeholders})`;

      const result = await this.db.runAsync(query, ids);
      return result.changes || 0;
    } catch (error) {
      logger.error(`[${this.tableName}] Error deleting many:`, error);
      throw error;
    }
  }

  /**
   * Contar registros
   */
  async count(filters?: FilterOptions): Promise<number> {
    try {
      let query = `SELECT COUNT(*) as count FROM ${this.tableName}`;
      const params: any[] = [];

      if (filters && Object.keys(filters).length > 0) {
        const filterClauses = Object.entries(filters).map(([key, value]) => {
          if (value === null) {
            return `${key} IS NULL`;
          }
          params.push(value);
          return `${key} = ?`;
        });
        query += ` WHERE ${filterClauses.join(' AND ')}`;
      }

      const result = await this.db.getAsync(query, params);
      return result?.count || 0;
    } catch (error) {
      logger.error(`[${this.tableName}] Error counting:`, error);
      throw error;
    }
  }

  /**
   * Executar query customizada
   */
  protected async execQuery<R>(query: string, params?: any[]): Promise<R[]> {
    try {
      const results = await this.db.allAsync(query, params || []);
      return results as R[];
    } catch (error) {
      logger.error(`[${this.tableName}] Error executing query:`, error);
      throw error;
    }
  }

  /**
   * Executar query que retorna um resultado
   */
  protected async execQuerySingle<R>(query: string, params?: any[]): Promise<R | null> {
    try {
      const result = await this.db.getAsync(query, params || []);
      return (result as R) || null;
    } catch (error) {
      logger.error(`[${this.tableName}] Error executing single query:`, error);
      throw error;
    }
  }

  /**
   * Limpar tabela (apenas para desenvolvimento)
   */
  async clear(): Promise<void> {
    try {
      const query = `DELETE FROM ${this.tableName}`;
      await this.db.runAsync(query);
    } catch (error) {
      logger.error(`[${this.tableName}] Error clearing:`, error);
      throw error;
    }
  }
}
