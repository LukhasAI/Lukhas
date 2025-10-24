/**
 * T4-Grade TTL Enforcement Engine
 *
 * CRITICAL FIX F4: Active expiration prevents stale data
 * Conservative: 1-minute sweep interval, 5-minute default TTL
 * Machine-parsable expiration logs
 */

import { EventEmitter } from 'events';

export interface TTLEntry {
  key: string;
  expiresAt: number;
  createdAt: number;
  ttl: number;
  category: string;
  metadata?: Record<string, unknown>;
}

export interface TTLMetrics {
  totalEntries: number;
  expiredEntries: number;
  activeEntries: number;
  avgTTLMs: number;
  minTTLMs: number;
  maxTTLMs: number;
  sweepCount: number;
  lastSweepAt: number;
  avgSweepDurationMs: number;
  timestamp: number;
}

export interface ExpirationPolicy {
  defaultTTL: number;
  minTTL: number;
  maxTTL: number;
  sweepInterval: number;
  maxEntriesPerSweep: number;
  gracePeriod: number;
}

export class TTLEnforcementEngine extends EventEmitter {
  private readonly entries: Map<string, TTLEntry> = new Map();
  private readonly expirationQueue: Array<{ key: string; expiresAt: number }> = [];
  private readonly metrics: TTLMetrics;

  // Conservative TTL policy defaults
  private readonly DEFAULT_POLICY: ExpirationPolicy = {
    defaultTTL: 5 * 60 * 1000,        // 5 minutes
    minTTL: 30 * 1000,                // 30 seconds
    maxTTL: 60 * 60 * 1000,           // 1 hour
    sweepInterval: 60 * 1000,         // 1 minute
    gracePeriod: 5 * 1000,            // 5 seconds
    maxEntriesPerSweep: 1000          // Max 1000 per sweep
  };

  private policy: ExpirationPolicy;
  private sweepTimer?: NodeJS.Timeout;
  private sweepDurations: number[] = [];

  constructor(policy?: Partial<ExpirationPolicy>) {
    super();
    this.policy = { ...this.DEFAULT_POLICY, ...policy };
    this.metrics = this.initMetrics();
    this.startActiveSweep();
  }

  /**
   * Register entry with TTL
   */
  register(
    key: string,
    ttl?: number,
    category: string = 'default',
    metadata?: Record<string, unknown>
  ): void {
    const effectiveTTL = this.normalizeTTL(ttl);
    const now = Date.now();

    const entry: TTLEntry = {
      key,
      expiresAt: now + effectiveTTL,
      createdAt: now,
      ttl: effectiveTTL,
      category,
      metadata
    };

    this.entries.set(key, entry);
    this.insertIntoQueue(entry);

    this.emit('registered', {
      key,
      ttl: effectiveTTL,
      expiresAt: entry.expiresAt
    });
  }

  /**
   * Check if entry is still valid
   */
  isValid(key: string): boolean {
    const entry = this.entries.get(key);

    if (!entry) {
      return false;
    }

    return !this.isExpired(entry);
  }

  /**
   * Get remaining TTL for entry
   */
  getRemainingTTL(key: string): number | null {
    const entry = this.entries.get(key);

    if (!entry) {
      return null;
    }

    const remaining = entry.expiresAt - Date.now();
    return Math.max(0, remaining);
  }

  /**
   * Extend TTL for entry
   */
  extend(key: string, additionalMs: number): boolean {
    const entry = this.entries.get(key);

    if (!entry || this.isExpired(entry)) {
      return false;
    }

    const newTTL = entry.ttl + additionalMs;
    const normalizedTTL = this.normalizeTTL(newTTL);

    entry.ttl = normalizedTTL;
    entry.expiresAt = Date.now() + normalizedTTL;

    this.reinsertIntoQueue(entry);

    this.emit('extended', {
      key,
      newTTL: normalizedTTL,
      newExpiresAt: entry.expiresAt
    });

    return true;
  }

  /**
   * Refresh TTL (reset to original TTL)
   */
  refresh(key: string): boolean {
    const entry = this.entries.get(key);

    if (!entry || this.isExpired(entry)) {
      return false;
    }

    const now = Date.now();
    entry.expiresAt = now + entry.ttl;

    this.reinsertIntoQueue(entry);

    this.emit('refreshed', {
      key,
      expiresAt: entry.expiresAt
    });

    return true;
  }

  /**
   * Remove entry from TTL tracking
   */
  unregister(key: string): boolean {
    const entry = this.entries.get(key);

    if (!entry) {
      return false;
    }

    this.entries.delete(key);
    this.removeFromQueue(key);

    this.emit('unregistered', { key });

    return true;
  }

  /**
   * CRITICAL: Active expiration sweep
   * Runs every 1 minute, processes up to 1000 entries
   */
  private startActiveSweep(): void {
    this.sweepTimer = setInterval(() => {
      this.performSweep();
    }, this.policy.sweepInterval);

    // Initial sweep
    this.performSweep();
  }

  /**
   * Perform expiration sweep
   */
  private async performSweep(): Promise<void> {
    const startTime = Date.now();
    const now = Date.now();
    const expiredKeys: string[] = [];

    let processed = 0;

    // Process expiration queue (already sorted by expiration time)
    while (
      this.expirationQueue.length > 0 &&
      processed < this.policy.maxEntriesPerSweep
    ) {
      const item = this.expirationQueue[0];

      // If first item not expired, rest won't be either (sorted queue)
      if (item.expiresAt > now + this.policy.gracePeriod) {
        break;
      }

      // Remove from queue
      this.expirationQueue.shift();
      processed++;

      // Check entry (double-check in case it was refreshed)
      const entry = this.entries.get(item.key);

      if (entry && this.isExpired(entry)) {
        expiredKeys.push(item.key);
        this.entries.delete(item.key);
        this.metrics.expiredEntries++;
      }
    }

    // Emit expired events
    if (expiredKeys.length > 0) {
      this.emit('sweep', {
        expired: expiredKeys.length,
        processed,
        duration: Date.now() - startTime
      });

      for (const key of expiredKeys) {
        this.emit('expired', { key, timestamp: now });
      }
    }

    // Update metrics
    this.metrics.sweepCount++;
    this.metrics.lastSweepAt = now;
    this.recordSweepDuration(Date.now() - startTime);
  }

  /**
   * Check if entry is expired
   */
  private isExpired(entry: TTLEntry): boolean {
    return Date.now() >= entry.expiresAt;
  }

  /**
   * Normalize TTL to policy constraints
   */
  private normalizeTTL(ttl?: number): number {
    const effectiveTTL = ttl || this.policy.defaultTTL;

    return Math.min(
      Math.max(effectiveTTL, this.policy.minTTL),
      this.policy.maxTTL
    );
  }

  /**
   * Insert entry into sorted expiration queue
   */
  private insertIntoQueue(entry: TTLEntry): void {
    const item = { key: entry.key, expiresAt: entry.expiresAt };

    // Binary search for insertion point
    let left = 0;
    let right = this.expirationQueue.length;

    while (left < right) {
      const mid = Math.floor((left + right) / 2);

      if (this.expirationQueue[mid].expiresAt < item.expiresAt) {
        left = mid + 1;
      } else {
        right = mid;
      }
    }

    this.expirationQueue.splice(left, 0, item);
  }

  /**
   * Reinsert entry into queue (after refresh/extend)
   */
  private reinsertIntoQueue(entry: TTLEntry): void {
    this.removeFromQueue(entry.key);
    this.insertIntoQueue(entry);
  }

  /**
   * Remove entry from queue
   */
  private removeFromQueue(key: string): void {
    const index = this.expirationQueue.findIndex(item => item.key === key);

    if (index !== -1) {
      this.expirationQueue.splice(index, 1);
    }
  }

  /**
   * Get entries by category
   */
  getEntriesByCategory(category: string): TTLEntry[] {
    return Array.from(this.entries.values())
      .filter(entry => entry.category === category && !this.isExpired(entry));
  }

  /**
   * Get entries expiring soon
   */
  getExpiringSoon(windowMs: number = 60000): TTLEntry[] {
    const threshold = Date.now() + windowMs;

    return Array.from(this.entries.values())
      .filter(entry => !this.isExpired(entry) && entry.expiresAt <= threshold)
      .sort((a, b) => a.expiresAt - b.expiresAt);
  }

  /**
   * Force immediate expiration check
   */
  async forceExpiration(): Promise<number> {
    const before = this.entries.size;
    await this.performSweep();
    const after = this.entries.size;

    return before - after;
  }

  /**
   * Record sweep duration
   */
  private recordSweepDuration(durationMs: number): void {
    this.sweepDurations.push(durationMs);

    if (this.sweepDurations.length > 100) {
      this.sweepDurations.shift();
    }

    this.metrics.avgSweepDurationMs = this.calculateAverage(this.sweepDurations);
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  private initMetrics(): TTLMetrics {
    return {
      totalEntries: 0,
      expiredEntries: 0,
      activeEntries: 0,
      avgTTLMs: 0,
      minTTLMs: 0,
      maxTTLMs: 0,
      sweepCount: 0,
      lastSweepAt: 0,
      avgSweepDurationMs: 0,
      timestamp: Date.now()
    };
  }

  /**
   * Get comprehensive metrics
   */
  getMetrics(): TTLMetrics {
    const ttls = Array.from(this.entries.values()).map(e => e.ttl);

    return {
      ...this.metrics,
      totalEntries: this.entries.size + this.metrics.expiredEntries,
      activeEntries: this.entries.size,
      avgTTLMs: ttls.length > 0 ? this.calculateAverage(ttls) : 0,
      minTTLMs: ttls.length > 0 ? Math.min(...ttls) : 0,
      maxTTLMs: ttls.length > 0 ? Math.max(...ttls) : 0,
      timestamp: Date.now()
    };
  }

  /**
   * Export expiration queue state
   */
  getExpirationQueue(): Array<{ key: string; expiresAt: number; remainingMs: number }> {
    const now = Date.now();

    return this.expirationQueue.slice(0, 100).map(item => ({
      key: item.key,
      expiresAt: item.expiresAt,
      remainingMs: Math.max(0, item.expiresAt - now)
    }));
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];
    const now = Date.now();

    // Check if sweep is running
    if (now - this.metrics.lastSweepAt > this.policy.sweepInterval * 2) {
      issues.push('Sweep not running or delayed');
    }

    // Check sweep performance
    if (this.metrics.avgSweepDurationMs > 1000) {
      issues.push(`Slow sweep performance: ${this.metrics.avgSweepDurationMs}ms`);
    }

    // Check queue size
    if (this.expirationQueue.length > 10000) {
      issues.push(`Large expiration queue: ${this.expirationQueue.length} entries`);
    }

    // Check for entries past expiration
    const overdueCount = this.expirationQueue.filter(
      item => item.expiresAt < now - this.policy.gracePeriod
    ).length;

    if (overdueCount > 100) {
      issues.push(`${overdueCount} overdue entries not expired`);
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  /**
   * Get policy configuration
   */
  getPolicy(): ExpirationPolicy {
    return { ...this.policy };
  }

  /**
   * Update policy (requires restart of sweep)
   */
  updatePolicy(policy: Partial<ExpirationPolicy>): void {
    this.policy = { ...this.policy, ...policy };

    // Restart sweep with new interval
    if (this.sweepTimer) {
      clearInterval(this.sweepTimer);
    }

    this.startActiveSweep();

    this.emit('policyUpdated', { policy: this.policy });
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.sweepTimer) {
      clearInterval(this.sweepTimer);
    }

    this.entries.clear();
    this.expirationQueue.length = 0;
    this.removeAllListeners();
  }
}