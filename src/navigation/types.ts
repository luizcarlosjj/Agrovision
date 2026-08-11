/**
 * Navigation Types
 * Type-safe navigation definitions using React Navigation
 */

import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { AnalysisType, Analysis } from '@models';

export type RootStackParamList = {
  Home: undefined;
  Camera: {
    analysisType: AnalysisType;
  };
  Processing: {
    imageUri: string;
    analysisType: AnalysisType;
  };
  Result: {
    analysis: Analysis;
  };
  /** Modo Científico inline — acesso via botão "Auditar Modelo" na ResultScreen. */
  AuditarModelo: {
    imageUri: string;
    prediction: string;
    classKey: string;
    confidence: number;
  };
  TestMode: undefined;
  History: undefined;
  HistoryTab: undefined;
  About: undefined;
};

export type HomeScreenProps = NativeStackScreenProps<RootStackParamList, 'Home'>;
export type CameraScreenProps = NativeStackScreenProps<RootStackParamList, 'Camera'>;
export type ProcessingScreenProps = NativeStackScreenProps<RootStackParamList, 'Processing'>;
export type ResultScreenProps = NativeStackScreenProps<RootStackParamList, 'Result'>;
export type AuditarModeloScreenProps = NativeStackScreenProps<RootStackParamList, 'AuditarModelo'>;
export type TestModeScreenProps = NativeStackScreenProps<RootStackParamList, 'TestMode'>;
export type AboutScreenProps = NativeStackScreenProps<RootStackParamList, 'About'>;

/**
 * Type-safe navigation prop
 */
export type RootStackNavigationProp = NativeStackScreenProps<RootStackParamList>['navigation'];
