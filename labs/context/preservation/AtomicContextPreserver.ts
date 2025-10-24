/**
 * T4-Grade Atomic Context Preservation
 *
 * CRITICAL FIX F2: Two-phase commit prevents orphaned contexts
 * Conservative: 10s timeout, automatic rollback on failure
 * Machine-parsable transaction logs
 */

import { EventEmitter } from 'events';
import { AsyncMemoryStore } from '../cache/AsyncMemoryStore';

// Transaction states for 2PC protocol
export enum TransactionState {
  INITIAL = 'INITIAL',
  PREPARING = 'PREPARING',
  PREPARED = 'PREPARED',
  COMMITTING = 'COMMITTING',
  COMMITTED = 'COMMITTED',
  ABORTING = 'ABORTING',
  ABORTED = 'ABORTED'
}

export interface ContextSnapshot {
  id: string;
  state: Record<string, unknown>;
  metadata: {
    timestamp: number;
    version: number;
    checksum: string;
    size: number;
  };
}

export interface Transaction {
  id: string;
  state: TransactionState;
  participants: Set<string>;
  preparedParticipants: Set<string>;
  committedParticipants: Set<string>;
  snapshot: ContextSnapshot;
  startTime: number;
  prepareDeadline: number;
  commitDeadline: number;
  rollbackData: Map<string, unknown>;
}

export interface PreservationMetrics {
  totalTransactions: number;
  successfulCommits: number;
  failedTransactions: number;
  rolledBack: number;
  avgLatencyMs: number;
  p99LatencyMs: number;
  orphanedContexts: number;
  timestamp: number;
}

export class AtomicContextPreserver extends EventEmitter {
  private readonly transactions: Map<string, Transaction> = new Map();
  private readonly store: AsyncMemoryStore<ContextSnapshot>;
  private readonly metrics: PreservationMetrics;

  // Conservative timeouts for 2PC
  private readonly PREPARE_TIMEOUT_MS = 5000;
  private readonly COMMIT_TIMEOUT_MS = 10000;
  private readonly MAX_RETRY_ATTEMPTS = 3;
  private readonly TRANSACTION_LOG_SIZE = 1000;

  private latencyHistory: number[] = [];
  private transactionLog: Array<{
    id: string;
    state: TransactionState;
    timestamp: number;
    duration: number;
  }> = [];

  constructor(store?: AsyncMemoryStore<ContextSnapshot>) {
    super();
    this.store = store || new AsyncMemoryStore<ContextSnapshot>();
    this.metrics = this.initMetrics();
    this.startTransactionMonitor();
  }

  /**
   * CRITICAL: Atomic context preservation with 2PC
   * All-or-nothing semantics with automatic rollback
   */
  async preserveContext(
    contextId: string,
    state: Record<string, unknown>,
    participants: string[]
  ): Promise<ContextSnapshot> {
    const transactionId = this.generateTransactionId();
    const startTime = Date.now();

    // Create transaction
    const transaction: Transaction = {
      id: transactionId,
      state: TransactionState.INITIAL,
      participants: new Set(participants),
      preparedParticipants: new Set(),
      committedParticipants: new Set(),
      snapshot: this.createSnapshot(contextId, state),
      startTime,
      prepareDeadline: startTime + this.PREPARE_TIMEOUT_MS,
      commitDeadline: startTime + this.COMMIT_TIMEOUT_MS,
      rollbackData: new Map()
    };

    this.transactions.set(transactionId, transaction);
    this.metrics.totalTransactions++;

    try {
      // Phase 1: Prepare
      await this.preparePhase(transaction);

      // Phase 2: Commit
      await this.commitPhase(transaction);

      // Success
      this.recordSuccess(transaction, Date.now() - startTime);
      return transaction.snapshot;

    } catch (error) {
      // Failure: Rollback
      await this.rollbackTransaction(transaction, error);
      this.recordFailure(transaction, Date.now() - startTime);
      throw error;

    } finally {
      // Cleanup
      this.transactions.delete(transactionId);
    }
  }

  /**
   * Phase 1: Prepare all participants
   * Each participant must acknowledge readiness
   */
  private async preparePhase(transaction: Transaction): Promise<void> {
    transaction.state = TransactionState.PREPARING;
    this.emit('prepare', { transactionId: transaction.id });

    const preparePromises = Array.from(transaction.participants).map(async (participant) => {
      try {
        await this.prepareParticipant(transaction, participant);
        transaction.preparedParticipants.add(participant);
      } catch (error) {
        throw new Error(`Prepare failed for ${participant}: ${error.message}`);
      }
    });

    // Wait for all with timeout
    await this.withTimeout(
      Promise.all(preparePromises),
      this.PREPARE_TIMEOUT_MS,
      'Prepare phase timeout'
    );

    // Verify all prepared
    if (transaction.preparedParticipants.size !== transaction.participants.size) {
      const missing = Array.from(transaction.participants)
        .filter(p => !transaction.preparedParticipants.has(p));
      throw new Error(`Prepare incomplete. Missing: ${missing.join(', ')}`);
    }

    transaction.state = TransactionState.PREPARED;
  }

  /**
   * Prepare individual participant
   * Saves rollback data for potential recovery
   */
  private async prepareParticipant(
    transaction: Transaction,
    participant: string
  ): Promise<void> {
    const key = `${participant}:${transaction.snapshot.id}`;

    // Save current state for rollback
    const currentState = await this.store.get(key);
    transaction.rollbackData.set(participant, currentState);

    // Attempt to acquire lock/reservation
    const prepared = await this.tryPrepare(participant, transaction.snapshot);

    if (!prepared) {
      throw new Error(`Failed to prepare ${participant}`);
    }
  }

  /**
   * Phase 2: Commit all participants
   * Only proceeds if all participants prepared successfully
   */
  private async commitPhase(transaction: Transaction): Promise<void> {
    transaction.state = TransactionState.COMMITTING;
    this.emit('commit', { transactionId: transaction.id });

    const commitPromises = Array.from(transaction.participants).map(async (participant) => {
      try {
        await this.commitParticipant(transaction, participant);
        transaction.committedParticipants.add(participant);
      } catch (error) {
        // Partial commit failure - critical!
        console.error(`CRITICAL: Commit failed for ${participant}:`, error);
        throw error;
      }
    });

    // Wait for all with timeout
    await this.withTimeout(
      Promise.all(commitPromises),
      this.COMMIT_TIMEOUT_MS - (Date.now() - transaction.startTime),
      'Commit phase timeout'
    );

    // Verify all committed
    if (transaction.committedParticipants.size !== transaction.participants.size) {
      // This should not happen if prepare was successful
      const missing = Array.from(transaction.participants)
        .filter(p => !transaction.committedParticipants.has(p));
      throw new Error(`CRITICAL: Partial commit. Missing: ${missing.join(', ')}`);
    }

    transaction.state = TransactionState.COMMITTED;
  }

  /**
   * Commit individual participant
   */
  private async commitParticipant(
    transaction: Transaction,
    participant: string
  ): Promise<void> {
    const key = `${participant}:${transaction.snapshot.id}`;

    // Persist snapshot with retry
    let attempts = 0;
    let lastError: Error | undefined;

    while (attempts < this.MAX_RETRY_ATTEMPTS) {
      try {
        await this.store.set(
          key,
          transaction.snapshot,
          this.COMMIT_TIMEOUT_MS * 2 // Extended TTL for committed data
        );
        return;
      } catch (error) {
        lastError = error as Error;
        attempts++;

        if (attempts < this.MAX_RETRY_ATTEMPTS) {
          await this.delay(Math.pow(2, attempts) * 100); // Exponential backoff
        }
      }
    }

    throw lastError || new Error(`Failed to commit after ${attempts} attempts`);
  }

  /**
   * Rollback transaction on failure
   * Restores all participants to previous state
   */
  private async rollbackTransaction(
    transaction: Transaction,
    error: Error
  ): Promise<void> {
    transaction.state = TransactionState.ABORTING;
    this.emit('rollback', {
      transactionId: transaction.id,
      error: error.message
    });

    console.warn(`Rolling back transaction ${transaction.id}:`, error.message);

    // Rollback all prepared participants
    const rollbackPromises = Array.from(transaction.preparedParticipants).map(async (participant) => {
      try {
        await this.rollbackParticipant(transaction, participant);
      } catch (rollbackError) {
        // Log but continue rollback for others
        console.error(`Rollback failed for ${participant}:`, rollbackError);
        this.metrics.orphanedContexts++;
      }
    });

    await Promise.allSettled(rollbackPromises);

    transaction.state = TransactionState.ABORTED;
    this.metrics.rolledBack++;
  }

  /**
   * Rollback individual participant
   */
  private async rollbackParticipant(
    transaction: Transaction,
    participant: string
  ): Promise<void> {
    const key = `${participant}:${transaction.snapshot.id}`;
    const previousState = transaction.rollbackData.get(participant);

    if (previousState === undefined) {
      // No previous state, just delete
      await this.store.delete(key);
    } else {
      // Restore previous state
      await this.store.set(key, previousState as ContextSnapshot);
    }
  }

  /**
   * Try to prepare participant (simulation)
   * In production, this would involve actual resource allocation
   */
  private async tryPrepare(
    participant: string,
    snapshot: ContextSnapshot
  ): Promise<boolean> {
    // Simulate preparation logic
    // In real implementation, this would:
    // 1. Check resource availability
    // 2. Acquire locks
    // 3. Validate constraints
    // 4. Reserve resources

    // For now, simulate with success probability
    const successRate = 0.95; // 95% success rate
    const success = Math.random() < successRate;

    if (!success) {
      console.warn(`Prepare failed for ${participant}`);
    }

    return success;
  }

  /**
   * Monitor transactions for timeout/cleanup
   */
  private startTransactionMonitor(): void {
    setInterval(() => {
      const now = Date.now();

      for (const [id, transaction] of this.transactions) {
        // Check prepare timeout
        if (
          transaction.state === TransactionState.PREPARING &&
          now > transaction.prepareDeadline
        ) {
          this.handleTimeout(transaction, 'Prepare phase timeout');
        }

        // Check commit timeout
        if (
          transaction.state === TransactionState.COMMITTING &&
          now > transaction.commitDeadline
        ) {
          this.handleTimeout(transaction, 'Commit phase timeout');
        }
      }
    }, 1000);
  }

  private handleTimeout(transaction: Transaction, reason: string): void {
    console.error(`Transaction ${transaction.id} timeout: ${reason}`);

    // Force rollback
    this.rollbackTransaction(transaction, new Error(reason))
      .catch(error => {
        console.error(`Failed to rollback timed-out transaction:`, error);
      });
  }

  /**
   * Create context snapshot with metadata
   */
  private createSnapshot(
    id: string,
    state: Record<string, unknown>
  ): ContextSnapshot {
    const stateStr = JSON.stringify(state);

    return {
      id,
      state,
      metadata: {
        timestamp: Date.now(),
        version: 1,
        checksum: this.calculateChecksum(stateStr),
        size: stateStr.length
      }
    };
  }

  private calculateChecksum(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }

  private generateTransactionId(): string {
    return `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async withTimeout<T>(
    promise: Promise<T>,
    timeoutMs: number,
    message: string
  ): Promise<T> {
    return Promise.race([
      promise,
      new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error(message)), timeoutMs)
      )
    ]);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private recordSuccess(transaction: Transaction, durationMs: number): void {
    this.metrics.successfulCommits++;
    this.recordLatency(durationMs);
    this.logTransaction(transaction, durationMs);
  }

  private recordFailure(transaction: Transaction, durationMs: number): void {
    this.metrics.failedTransactions++;
    this.recordLatency(durationMs);
    this.logTransaction(transaction, durationMs);
  }

  private recordLatency(latencyMs: number): void {
    this.latencyHistory.push(latencyMs);

    if (this.latencyHistory.length > 1000) {
      this.latencyHistory.shift();
    }

    this.metrics.avgLatencyMs = this.calculateAverage(this.latencyHistory);
    this.metrics.p99LatencyMs = this.calculatePercentile(this.latencyHistory, 99);
  }

  private logTransaction(transaction: Transaction, duration: number): void {
    this.transactionLog.push({
      id: transaction.id,
      state: transaction.state,
      timestamp: Date.now(),
      duration
    });

    if (this.transactionLog.length > this.TRANSACTION_LOG_SIZE) {
      this.transactionLog.shift();
    }
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  private calculatePercentile(values: number[], percentile: number): number {
    if (values.length === 0) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }

  private initMetrics(): PreservationMetrics {
    return {
      totalTransactions: 0,
      successfulCommits: 0,
      failedTransactions: 0,
      rolledBack: 0,
      avgLatencyMs: 0,
      p99LatencyMs: 0,
      orphanedContexts: 0,
      timestamp: Date.now()
    };
  }

  /**
   * Export metrics as JSON
   */
  getMetrics(): PreservationMetrics {
    return {
      ...this.metrics,
      timestamp: Date.now()
    };
  }

  /**
   * Export transaction log
   */
  getTransactionLog(): typeof this.transactionLog {
    return [...this.transactionLog];
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    const failureRate = this.metrics.failedTransactions /
      Math.max(this.metrics.totalTransactions, 1);

    if (failureRate > 0.05) {
      issues.push(`High failure rate: ${(failureRate * 100).toFixed(1)}%`);
    }

    if (this.metrics.orphanedContexts > 0) {
      issues.push(`Orphaned contexts detected: ${this.metrics.orphanedContexts}`);
    }

    if (this.metrics.p99LatencyMs > 1000) {
      issues.push(`P99 latency above 1s: ${this.metrics.p99LatencyMs}ms`);
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }
}