/**
 * CSV export for XAI test results.
 *
 * Writes a CSV with one row per test into the app's cache directory and
 * opens the system share sheet so the user can save it / send it elsewhere.
 */

import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import { XAITestRecord } from '@models';
import { logger } from '@utils/logger';

const CSV_COLUMNS = [
  'id',
  'createdAt',
  'prediction',
  'confidence',
  'al',
  'afs',
  'threshold',
  'bboxStrategy',
  'bboxX',
  'bboxY',
  'bboxW',
  'bboxH',
  'label',
  'imageUri',
] as const;

function escapeCsv(value: string | number): string {
  const s = String(value ?? '');
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function recordToRow(r: XAITestRecord): string {
  return [
    r.id,
    r.createdAt,
    r.prediction,
    r.confidence.toFixed(4),
    r.al.toFixed(4),
    r.afs.toFixed(4),
    r.threshold.toFixed(2),
    r.bboxStrategy,
    r.bbox.x,
    r.bbox.y,
    r.bbox.width,
    r.bbox.height,
    r.label,
    r.imageUri,
  ]
    .map(escapeCsv)
    .join(',');
}

export function buildCSV(records: XAITestRecord[]): string {
  const header = CSV_COLUMNS.join(',');
  const body = records.map(recordToRow).join('\n');
  return `${header}\n${body}\n`;
}

export async function exportXAITestsToCSV(records: XAITestRecord[]): Promise<string> {
  if (records.length === 0) {
    throw new Error('Nenhum teste para exportar');
  }

  const csv = buildCSV(records);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `agrovision_xai_tests_${timestamp}.csv`;
  const path = `${FileSystem.cacheDirectory}${filename}`;

  await FileSystem.writeAsStringAsync(path, csv, {
    encoding: FileSystem.EncodingType.UTF8,
  });
  logger.log(`[CSV] Wrote ${records.length} rows to ${path}`);

  const canShare = await Sharing.isAvailableAsync();
  if (canShare) {
    await Sharing.shareAsync(path, {
      mimeType: 'text/csv',
      dialogTitle: 'Exportar testes XAI',
      UTI: 'public.comma-separated-values-text',
    });
  }

  return path;
}
