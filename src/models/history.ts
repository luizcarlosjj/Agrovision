/**
 * History Domain Models
 * Data structures for analysis history and user activity
 */

import { Analysis } from './analysis';

/**
 * User's analysis history with metadata
 */
export interface AnalysisHistory {
  items: Analysis[];
  totalCount: number;
  filteredCount: number;
  lastUpdated: string;
}

/**
 * Statistics about user's analyses
 */
export interface AnalysisStatistics {
  totalAnalyses: number;
  analysisBreakdown: {
    disease: number;
    pest: number;
    species: number;
    nutrient: number;
  };
  averageConfidence: number;
  mostCommonResult: string;
  timeSpanDays: number;
}

/**
 * Filter options for history queries
 */
export interface HistoryFilterOptions {
  analysisType?: 'disease' | 'pest' | 'species' | 'nutrient';
  dateFrom?: string;
  dateTo?: string;
  minConfidence?: number;
  searchQuery?: string;
  sortBy?: 'date' | 'confidence' | 'type';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}

/**
 * Paginated history response
 */
export interface PaginatedHistory {
  items: Analysis[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

/**
 * History entry metadata
 */
export interface HistoryEntryMetadata {
  analysisId: string;
  viewCount: number;
  lastViewed: string;
  starred: boolean;
  notes?: string;
  tags?: string[];
}

/**
 * Exported history data
 */
export interface ExportedHistory {
  exportDate: string;
  entries: Analysis[];
  totalCount: number;
  statistics: AnalysisStatistics;
}
