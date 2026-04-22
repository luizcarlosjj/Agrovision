/**
 * Auto Sync Service
 * Monitors internet connection and syncs training data automatically
 * Stores user photos for dynamic fine-tuning
 */

import * as FileSystem from 'expo-file-system';
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TRAINING_DIR = `${FileSystem.documentDirectory}user_training_data/`;
const SYNC_LOG = `${FileSystem.documentDirectory}sync_history.json`;

export interface SyncHistory {
  syncs: Array<{
    timestamp: string;
    species_count: number;
    image_count: number;
  }>;
  last_sync: string | null;
  next_sync: string | null;
}

class AutoSyncService {
  private isMonitoring = false;
  private syncInProgress = false;

  /**
   * Start monitoring internet connection
   */
  async startMonitoring() {
    if (this.isMonitoring) return;

    console.log('[SYNC] Starting auto-sync monitoring...');
    this.isMonitoring = true;

    // Check internet periodically
    const unsubscribe = NetInfo.addEventListener(async (state) => {
      if (state.isConnected && state.isInternetReachable) {
        await this.attemptSync();
      }
    });

    // Also check on app startup
    const netState = await NetInfo.fetch();
    if (netState.isConnected && netState.isInternetReachable) {
      await this.attemptSync();
    }

    return unsubscribe;
  }

  /**
   * Store user photo for training
   */
  async storeUserPhoto(
    imageUri: string,
    species: string
  ): Promise<boolean> {
    try {
      // Create directory for species
      const speciesDir = `${TRAINING_DIR}${species}/`;
      const dirInfo = await FileSystem.getInfoAsync(speciesDir);

      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(speciesDir, { intermediates: true });
      }

      // Generate filename
      const timestamp = Date.now();
      const filename = `${species}_${timestamp}.jpg`;
      const destPath = `${speciesDir}${filename}`;

      // Copy photo
      await FileSystem.copyAsync({
        from: imageUri,
        to: destPath,
      });

      console.log(`[SYNC] Stored photo: ${destPath}`);

      // Update storage metadata
      await this.updateStorageMetadata();

      // Check if should sync
      await this.checkAndSync();

      return true;
    } catch (error) {
      console.error('[SYNC] Failed to store photo:', error);
      return false;
    }
  }

  /**
   * Get count of pending training images
   */
  async getPendingCount(): Promise<number> {
    try {
      const dirInfo = await FileSystem.getInfoAsync(TRAINING_DIR);

      if (!dirInfo.exists) {
        return 0;
      }

      const files = await FileSystem.readDirectoryAsync(TRAINING_DIR);
      let count = 0;

      for (const item of files) {
        const itemPath = `${TRAINING_DIR}${item}`;
        const itemInfo = await FileSystem.getInfoAsync(itemPath);

        if (itemInfo.isDirectory) {
          const speciesFiles = await FileSystem.readDirectoryAsync(itemPath);
          count += speciesFiles.length;
        }
      }

      return count;
    } catch (error) {
      console.error('[SYNC] Failed to get pending count:', error);
      return 0;
    }
  }

  /**
   * Check if should sync (has data + internet)
   */
  private async checkAndSync() {
    const pendingCount = await this.getPendingCount();

    if (pendingCount > 5) {
      console.log(`[SYNC] Found ${pendingCount} pending images, checking internet...`);

      const netState = await NetInfo.fetch();
      if (netState.isConnected && netState.isInternetReachable) {
        await this.attemptSync();
      }
    }
  }

  /**
   * Attempt to sync if conditions are met
   */
  private async attemptSync() {
    // Prevent concurrent syncs
    if (this.syncInProgress) {
      console.log('[SYNC] Sync already in progress');
      return;
    }

    const lastSync = await AsyncStorage.getItem('last_sync_time');
    const now = Date.now();
    const lastSyncTime = lastSync ? parseInt(lastSync) : 0;

    // Don't sync more than once per hour
    if (now - lastSyncTime < 3600000) {
      console.log('[SYNC] Sync too recent, skipping');
      return;
    }

    // Check if there's data to sync
    const pendingCount = await this.getPendingCount();
    if (pendingCount === 0) {
      console.log('[SYNC] No pending data');
      return;
    }

    await this.performSync();
  }

  /**
   * Perform actual synchronization
   */
  private async performSync() {
    this.syncInProgress = true;

    try {
      console.log('[SYNC] Starting synchronization...');

      // Get pending images info
      const pendingCount = await this.getPendingCount();
      console.log(`[SYNC] Syncing ${pendingCount} images...`);

      // In real implementation:
      // 1. Upload photos to backend
      // 2. Trigger fine-tuning job
      // 3. Download updated model
      // For now, just log and update metadata

      // Prepare sync data
      const syncData = {
        timestamp: new Date().toISOString(),
        images_synced: pendingCount,
        status: 'pending_finetuning',
      };

      console.log('[SYNC] Sync data prepared:', syncData);

      // Update sync history
      await this.recordSync(pendingCount);

      // In production: upload to backend
      // await this.uploadToBackend(syncData);

      console.log('[SYNC] Sync completed successfully');
      await AsyncStorage.setItem('last_sync_time', Date.now().toString());

    } catch (error) {
      console.error('[SYNC] Sync failed:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * Record sync in history
   */
  private async recordSync(imageCount: number) {
    try {
      let history: SyncHistory = {
        syncs: [],
        last_sync: null,
        next_sync: null,
      };

      // Try to load existing history
      try {
        const historyJson = await FileSystem.readAsStringAsync(SYNC_LOG);
        history = JSON.parse(historyJson);
      } catch {
        // First sync
      }

      // Add new sync
      history.syncs.push({
        timestamp: new Date().toISOString(),
        species_count: 0, // Updated later
        image_count: imageCount,
      });

      history.last_sync = new Date().toISOString();
      history.next_sync = new Date(Date.now() + 3600000).toISOString();

      // Save history
      await FileSystem.writeAsStringAsync(
        SYNC_LOG,
        JSON.stringify(history, null, 2)
      );

      console.log('[SYNC] History updated');
    } catch (error) {
      console.error('[SYNC] Failed to record sync:', error);
    }
  }

  /**
   * Update storage metadata
   */
  private async updateStorageMetadata() {
    try {
      const pending = await this.getPendingCount();
      await AsyncStorage.setItem('pending_training_images', pending.toString());
    } catch (error) {
      console.error('[SYNC] Failed to update metadata:', error);
    }
  }

  /**
   * Get sync status
   */
  async getSyncStatus() {
    try {
      const pendingCount = await this.getPendingCount();
      const lastSyncStr = await AsyncStorage.getItem('last_sync_time');
      const lastSync = lastSyncStr ? new Date(parseInt(lastSyncStr)) : null;

      const netState = await NetInfo.fetch();

      return {
        pending_images: pendingCount,
        last_sync: lastSync?.toISOString() || null,
        is_connected: netState.isConnected,
        is_syncing: this.syncInProgress,
      };
    } catch (error) {
      console.error('[SYNC] Failed to get status:', error);
      return null;
    }
  }

  /**
   * Stop monitoring
   */
  stopMonitoring() {
    this.isMonitoring = false;
    console.log('[SYNC] Stopped monitoring');
  }

  /**
   * Clear all pending data (after successful sync)
   */
  async clearPendingData() {
    try {
      await FileSystem.deleteAsync(TRAINING_DIR, { idempotent: true });
      await FileSystem.makeDirectoryAsync(TRAINING_DIR, { intermediates: true });
      console.log('[SYNC] Cleared pending data');
      return true;
    } catch (error) {
      console.error('[SYNC] Failed to clear pending data:', error);
      return false;
    }
  }
}

export const autoSyncService = new AutoSyncService();
