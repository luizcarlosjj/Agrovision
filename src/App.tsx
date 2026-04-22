/**
 * App Component
 * Root application component with providers
 */

import React, { useEffect } from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { StatusBar } from 'react-native';
import { RootNavigator } from '@navigation';
import { AppProvider, useAppContext, AnalysisProvider } from '@context';
import { logger } from '@utils/logger';

/**
 * Inner app component with access to context
 */
function AppContent() {
  const { state, initializeApp } = useAppContext();

  /**
   * Initialize app on mount
   */
  useEffect(() => {
    const init = async () => {
      try {
        logger.log('[App] Initializing application');
        await initializeApp();
        logger.success('[App] Application ready');
      } catch (error) {
        logger.error('[App] Initialization error:', error);
      }
    };

    init();
  }, [initializeApp]);

  if (!state.isAppInitialized) {
    return null; // Splash screen could be shown here
  }

  return <RootNavigator />;
}

/**
 * Root App Component
 * Wraps entire application with providers
 */
export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="dark-content" translucent backgroundColor="transparent" />
      <AppProvider>
        <AnalysisProvider>
          <AppContent />
        </AnalysisProvider>
      </AppProvider>
    </SafeAreaProvider>
  );
}
