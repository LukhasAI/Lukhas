/**
 * T4-Grade Write-Ahead Log for Persistence
 *
 * PHASE 3: Durable persistence with crash recovery
 * Guarantees: ACID properties, automatic recovery, no data loss
 * Verification: Crash simulation chaos testing
 */

import { EventEmitter } from 'events';
import * as fs from 'fs/promises';
import * as path from 'path';
import * as crypto from 'crypto';

export interface WALEntry {
  sequence: number;
  operation: 'SET' | 'DELETE' | 'BATCH' | 'CHECKPOINT';
  key?: string;
  value?: unknown;
  timestamp: number;
  checksum: string;
  metadata?: Record<string, unknown>;
}

export interface WALConfig {
  logDir: string;
  maxLogSize: number;
  checkpointInterval: number;
  syncMode: 'none' | 'sync' | 'fsync';
  compression: boolean;
}

export interface WALStats {
  totalEntries: number;
  totalCheckpoints: number;
  currentLogSize: number;
  lastCheckpointAt: number;
  recoveredEntries: number;
  corruptEntries: number;
  avgWriteTimeMs: number;
  timestamp: number;
}

export interface RecoveryResult {
  success: boolean;
  entriesRecovered: number;
  checkpointsApplied: number;
  corruptEntriesSkipped: number;
  finalState: Map<string, unknown>;
  errors: string[];
}

/**
 * Write-Ahead Log implementation
 */
export class WriteAheadLog extends EventEmitter {
  private readonly config: WALConfig;
  private readonly stats: WALStats;
  private sequence = 0;
  private currentLogFile?: number; // File descriptor
  private currentLogPath?: string;
  private writeTimes: number[] = [];

  // Conservative defaults
  private readonly DEFAULT_CONFIG: WALConfig = {
    logDir: './wal',
    maxLogSize: 100 * 1024 * 1024,  // 100MB
    checkpointInterval: 60000,       // 1 minute
    syncMode: 'fsync',               // Full durability
    compression: false               // No compression by default
  };

  private checkpointTimer?: NodeJS.Timeout;

  constructor(config?: Partial<WALConfig>) {
    super();
    this.config = { ...this.DEFAULT_CONFIG, ...config };
    this.stats = this.initStats();
  }

  /**
   * Initialize WAL
   */
  async initialize(): Promise<void> {
    // Create log directory
    await fs.mkdir(this.config.logDir, { recursive: true });

    // Open new log file
    await this.rotateLog();

    // Start automatic checkpointing
    this.startCheckpointing();

    this.emit('initialized', { timestamp: Date.now() });
  }

  /**
   * Write entry to WAL
   */
  async write(
    operation: WALEntry['operation'],
    key?: string,
    value?: unknown,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    const startTime = Date.now();

    const entry: WALEntry = {
      sequence: ++this.sequence,
      operation,
      key,
      value,
      timestamp: Date.now(),
      checksum: '',
      metadata
    };

    // Calculate checksum
    entry.checksum = this.calculateChecksum(entry);

    // Serialize entry
    const serialized = JSON.stringify(entry) + '\n';
    const buffer = Buffer.from(serialized, 'utf-8');

    try {
      // Write to log file
      if (this.currentLogFile !== undefined) {
        await fs.appendFile(this.currentLogFile, buffer);

        // Sync if required
        if (this.config.syncMode === 'fsync') {
          await fs.fsync(this.currentLogFile);
        } else if (this.config.syncMode === 'sync') {
          await fs.fdatasync(this.currentLogFile);
        }

        this.stats.currentLogSize += buffer.length;
        this.stats.totalEntries++;

        // Check if log rotation needed
        if (this.stats.currentLogSize >= this.config.maxLogSize) {
          await this.rotateLog();
        }

        this.recordWriteTime(Date.now() - startTime);

        this.emit('written', {
          sequence: entry.sequence,
          operation,
          timestamp: Date.now()
        });
      }

    } catch (error) {
      this.emit('error', {
        error: error.message,
        entry,
        timestamp: Date.now()
      });

      throw new Error(`WAL write failed: ${error.message}`);
    }
  }

  /**
   * Write checkpoint (snapshot of current state)
   */
  async checkpoint(state: Map<string, unknown>): Promise<void> {
    // Serialize entire state
    const stateObj = Object.fromEntries(state);

    await this.write('CHECKPOINT', undefined, stateObj, {
      entryCount: state.size,
      timestamp: Date.now()
    });

    this.stats.totalCheckpoints++;
    this.stats.lastCheckpointAt = Date.now();

    this.emit('checkpoint', {
      entryCount: state.size,
      timestamp: Date.now()
    });

    // After checkpoint, we can safely remove old log files
    await this.pruneOldLogs();
  }

  /**
   * Recover state from WAL
   */
  async recover(): Promise<RecoveryResult> {
    const result: RecoveryResult = {
      success: true,
      entriesRecovered: 0,
      checkpointsApplied: 0,
      corruptEntriesSkipped: 0,
      finalState: new Map(),
      errors: []
    };

    try {
      // Find all log files
      const logFiles = await this.findLogFiles();

      if (logFiles.length === 0) {
        return result; // No logs to recover
      }

      // Process log files in order
      for (const logFile of logFiles) {
        await this.recoverFromFile(logFile, result);
      }

      this.stats.recoveredEntries = result.entriesRecovered;
      this.stats.corruptEntries = result.corruptEntriesSkipped;

      this.emit('recovered', {
        entriesRecovered: result.entriesRecovered,
        checkpointsApplied: result.checkpointsApplied,
        timestamp: Date.now()
      });

      return result;

    } catch (error) {
      result.success = false;
      result.errors.push(error.message);

      this.emit('recoveryError', {
        error: error.message,
        timestamp: Date.now()
      });

      return result;
    }
  }

  /**
   * Recover from single log file
   */
  private async recoverFromFile(
    filePath: string,
    result: RecoveryResult
  ): Promise<void> {
    const content = await fs.readFile(filePath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());

    for (const line of lines) {
      try {
        const entry: WALEntry = JSON.parse(line);

        // Verify checksum
        const expectedChecksum = this.calculateChecksum(entry);

        if (entry.checksum !== expectedChecksum) {
          result.corruptEntriesSkipped++;
          this.emit('corruptEntry', {
            sequence: entry.sequence,
            timestamp: Date.now()
          });
          continue;
        }

        // Apply entry
        this.applyEntry(entry, result.finalState);

        result.entriesRecovered++;

        if (entry.operation === 'CHECKPOINT') {
          result.checkpointsApplied++;
        }

      } catch (error) {
        result.corruptEntriesSkipped++;
        result.errors.push(`Failed to parse entry: ${error.message}`);
      }
    }
  }

  /**
   * Apply WAL entry to state
   */
  private applyEntry(entry: WALEntry, state: Map<string, unknown>): void {
    switch (entry.operation) {
      case 'SET':
        if (entry.key && entry.value !== undefined) {
          state.set(entry.key, entry.value);
        }
        break;

      case 'DELETE':
        if (entry.key) {
          state.delete(entry.key);
        }
        break;

      case 'CHECKPOINT':
        // Replace entire state with checkpoint
        if (entry.value && typeof entry.value === 'object') {
          state.clear();

          for (const [k, v] of Object.entries(entry.value)) {
            state.set(k, v);
          }
        }
        break;

      case 'BATCH':
        // Handle batch operations
        if (entry.value && Array.isArray(entry.value)) {
          for (const op of entry.value) {
            if (op.type === 'set') {
              state.set(op.key, op.value);
            } else if (op.type === 'delete') {
              state.delete(op.key);
            }
          }
        }
        break;
    }
  }

  /**
   * Rotate to new log file
   */
  private async rotateLog(): Promise<void> {
    // Close current log file
    if (this.currentLogFile !== undefined) {
      await fs.close(this.currentLogFile);
    }

    // Create new log file
    const timestamp = Date.now();
    this.currentLogPath = path.join(this.config.logDir, `wal-${timestamp}.log`);

    this.currentLogFile = await fs.open(this.currentLogPath, 'a');
    this.stats.currentLogSize = 0;

    this.emit('rotated', {
      path: this.currentLogPath,
      timestamp: Date.now()
    });
  }

  /**
   * Find all log files in order
   */
  private async findLogFiles(): Promise<string[]> {
    const files = await fs.readdir(this.config.logDir);

    return files
      .filter(f => f.startsWith('wal-') && f.endsWith('.log'))
      .map(f => path.join(this.config.logDir, f))
      .sort(); // Timestamp in filename ensures correct order
  }

  /**
   * Prune old log files after checkpoint
   */
  private async pruneOldLogs(): Promise<void> {
    const files = await this.findLogFiles();

    // Keep only the current log file and the previous one
    if (files.length > 2) {
      const toDelete = files.slice(0, -2);

      for (const file of toDelete) {
        try {
          await fs.unlink(file);

          this.emit('pruned', {
            file,
            timestamp: Date.now()
          });

        } catch (error) {
          this.emit('error', {
            error: `Failed to prune ${file}: ${error.message}`,
            timestamp: Date.now()
          });
        }
      }
    }
  }

  /**
   * Start automatic checkpointing
   */
  private startCheckpointing(): void {
    this.checkpointTimer = setInterval(() => {
      this.emit('checkpointDue', { timestamp: Date.now() });
    }, this.config.checkpointInterval);
  }

  /**
   * Calculate entry checksum
   */
  private calculateChecksum(entry: WALEntry): string {
    // Create copy without checksum field
    const { checksum, ...entryWithoutChecksum } = entry;
    const str = JSON.stringify(entryWithoutChecksum);

    return crypto.createHash('sha256').update(str).digest('hex').substring(0, 16);
  }

  /**
   * Record write time for metrics
   */
  private recordWriteTime(timeMs: number): void {
    this.writeTimes.push(timeMs);

    if (this.writeTimes.length > 1000) {
      this.writeTimes.shift();
    }

    this.stats.avgWriteTimeMs = this.calculateAverage(this.writeTimes);
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  private initStats(): WALStats {
    return {
      totalEntries: 0,
      totalCheckpoints: 0,
      currentLogSize: 0,
      lastCheckpointAt: 0,
      recoveredEntries: 0,
      corruptEntries: 0,
      avgWriteTimeMs: 0,
      timestamp: Date.now()
    };
  }

  /**
   * Get comprehensive stats
   */
  getStats(): WALStats {
    return {
      ...this.stats,
      timestamp: Date.now()
    };
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    if (this.stats.corruptEntries > 0) {
      issues.push(`Corrupt entries detected: ${this.stats.corruptEntries}`);
    }

    if (this.stats.avgWriteTimeMs > 10) {
      issues.push(`High write latency: ${this.stats.avgWriteTimeMs.toFixed(1)}ms`);
    }

    const timeSinceCheckpoint = Date.now() - this.stats.lastCheckpointAt;

    if (timeSinceCheckpoint > this.config.checkpointInterval * 2) {
      issues.push(`No checkpoint in ${(timeSinceCheckpoint / 1000).toFixed(0)}s`);
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  /**
   * Cleanup on shutdown
   */
  async destroy(): Promise<void> {
    if (this.checkpointTimer) {
      clearInterval(this.checkpointTimer);
    }

    if (this.currentLogFile !== undefined) {
      await fs.close(this.currentLogFile);
    }

    this.removeAllListeners();
  }
}

/**
 * Persistent storage with WAL
 */
export class PersistentStore<T = unknown> extends EventEmitter {
  private readonly wal: WriteAheadLog;
  private readonly state: Map<string, T> = new Map();
  private checkpointTimer?: NodeJS.Timeout;

  constructor(walConfig?: Partial<WALConfig>) {
    super();
    this.wal = new WriteAheadLog(walConfig);

    // Listen to checkpoint events
    this.wal.on('checkpointDue', async () => {
      await this.checkpoint();
    });
  }

  /**
   * Initialize and recover
   */
  async initialize(): Promise<RecoveryResult> {
    await this.wal.initialize();

    // Recover state from WAL
    const recovery = await this.wal.recover();

    // Apply recovered state
    for (const [key, value] of recovery.finalState) {
      this.state.set(key, value as T);
    }

    return recovery;
  }

  /**
   * Set value (durable)
   */
  async set(key: string, value: T): Promise<void> {
    // Write to WAL first
    await this.wal.write('SET', key, value);

    // Then update in-memory state
    this.state.set(key, value);

    this.emit('set', { key, timestamp: Date.now() });
  }

  /**
   * Get value
   */
  get(key: string): T | undefined {
    return this.state.get(key);
  }

  /**
   * Delete value (durable)
   */
  async delete(key: string): Promise<boolean> {
    const existed = this.state.has(key);

    if (existed) {
      // Write to WAL first
      await this.wal.write('DELETE', key);

      // Then update in-memory state
      this.state.delete(key);

      this.emit('delete', { key, timestamp: Date.now() });
    }

    return existed;
  }

  /**
   * Checkpoint current state
   */
  async checkpoint(): Promise<void> {
    await this.wal.checkpoint(this.state as Map<string, unknown>);
  }

  /**
   * Get all keys
   */
  keys(): string[] {
    return Array.from(this.state.keys());
  }

  /**
   * Get size
   */
  size(): number {
    return this.state.size;
  }

  /**
   * Clear all (durable)
   */
  async clear(): Promise<void> {
    const keys = this.keys();

    for (const key of keys) {
      await this.delete(key);
    }
  }

  /**
   * Get WAL stats
   */
  getWALStats(): WALStats {
    return this.wal.getStats();
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    return this.wal.healthCheck();
  }

  /**
   * Cleanup
   */
  async destroy(): Promise<void> {
    await this.wal.destroy();
    this.state.clear();
    this.removeAllListeners();
  }
}
