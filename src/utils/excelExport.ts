import * as FileSystem from 'expo-file-system/legacy';
import * as Sharing from 'expo-sharing';
import XLSX from 'xlsx';
import { Analysis, XAITestRecord } from '@models';
import { logger } from '@utils/logger';

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR');
  } catch {
    return iso;
  }
}

function pct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function analysesToSheet(analyses: Analysis[]): XLSX.WorkSheet {
  const rows = analyses.map((a) => ({
    ID: a.id,
    'Data/Hora': formatDate(a.timestamp),
    Resultado: a.result,
    'Confiança (%)': pct(a.confidence),
    Tipo: a.type,
    Descrição: a.description,
    Recomendações: a.recommendations.join(' | '),
    'Tempo de Processamento (ms)': a.processingTime,
    'URI da Imagem': a.imageUri,
    'Criado em': formatDate(a.createdAt),
    'Atualizado em': formatDate(a.updatedAt),
  }));

  const ws = XLSX.utils.json_to_sheet(rows.length ? rows : [{}]);

  // Column widths
  ws['!cols'] = [
    { wch: 36 }, // ID
    { wch: 20 }, // Data/Hora
    { wch: 24 }, // Resultado
    { wch: 14 }, // Confiança
    { wch: 12 }, // Tipo
    { wch: 50 }, // Descrição
    { wch: 60 }, // Recomendações
    { wch: 24 }, // Tempo
    { wch: 40 }, // URI
    { wch: 20 }, // Criado em
    { wch: 20 }, // Atualizado em
  ];

  return ws;
}

function xaiTestsToSheet(tests: XAITestRecord[]): XLSX.WorkSheet {
  const rows = tests.map((t) => ({
    ID: t.id,
    'Data/Hora': formatDate(t.createdAt),
    Predição: t.prediction,
    'Confiança (%)': pct(t.confidence),
    'AL (Attention Leakage)': t.al.toFixed(4),
    'AFS (Area Focus Score)': t.afs.toFixed(4),
    Threshold: t.threshold.toFixed(2),
    'Estratégia BBox': t.bboxStrategy,
    'BBox X': t.bbox.x,
    'BBox Y': t.bbox.y,
    'BBox Largura': t.bbox.width,
    'BBox Altura': t.bbox.height,
    Rótulo: t.label,
    'URI da Imagem': t.imageUri,
  }));

  const ws = XLSX.utils.json_to_sheet(rows.length ? rows : [{}]);

  ws['!cols'] = [
    { wch: 36 }, // ID
    { wch: 20 }, // Data/Hora
    { wch: 24 }, // Predição
    { wch: 14 }, // Confiança
    { wch: 22 }, // AL
    { wch: 22 }, // AFS
    { wch: 10 }, // Threshold
    { wch: 16 }, // Estratégia
    { wch: 8 },  // X
    { wch: 8 },  // Y
    { wch: 12 }, // Largura
    { wch: 12 }, // Altura
    { wch: 20 }, // Rótulo
    { wch: 40 }, // URI
  ];

  return ws;
}

export async function exportLogsToExcel(
  analyses: Analysis[],
  xaiTests: XAITestRecord[],
): Promise<string> {
  const wb = XLSX.utils.book_new();

  XLSX.utils.book_append_sheet(wb, analysesToSheet(analyses), 'Consultas');
  XLSX.utils.book_append_sheet(wb, xaiTestsToSheet(xaiTests), 'Auditorias XAI');

  // Resumo
  const summaryRows = [
    { Métrica: 'Total de Consultas', Valor: analyses.length },
    { Métrica: 'Total de Auditorias XAI', Valor: xaiTests.length },
    { Métrica: 'Exportado em', Valor: formatDate(new Date().toISOString()) },
  ];
  const summaryWs = XLSX.utils.json_to_sheet(summaryRows);
  summaryWs['!cols'] = [{ wch: 26 }, { wch: 30 }];
  XLSX.utils.book_append_sheet(wb, summaryWs, 'Resumo');

  const base64 = XLSX.write(wb, { type: 'base64', bookType: 'xlsx' });

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `agrovision_logs_${timestamp}.xlsx`;
  const path = `${FileSystem.cacheDirectory}${filename}`;

  await FileSystem.writeAsStringAsync(path, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });

  logger.log(`[Excel] Exported ${analyses.length} consultas + ${xaiTests.length} auditorias → ${path}`);

  const canShare = await Sharing.isAvailableAsync();
  if (canShare) {
    await Sharing.shareAsync(path, {
      mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      dialogTitle: 'Exportar logs AgroVision',
      UTI: 'com.microsoft.excel.xlsx',
    });
  }

  return path;
}
