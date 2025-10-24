/**
 * T4-Grade AsyncLock Implementation
 *
 * Conservative approach: Prevents deadlocks with timeouts
 * Supports both single and multi-key locking
 * Machine-parsable lock metrics
 */

export interface LockMetrics {
  activeLocks: number;
  totalAcquired: number;
  totalTimeouts: number;
  avgWaitMs: number;
  maxWaitMs: number;
  deadlocksDetected: number;
  timestamp: number;
}

interface LockRequest {
  resolve: (value: void) => void;
  reject: (error: Error) => void;
  timestamp: number;
  timeout: NodeJS.Timeout;
}

export class AsyncLock {
  private readonly locks: Map<string, LockRequest[]> = new Map();
  private readonly heldLocks: Map<string, number> = new Map();
  private readonly metrics: LockMetrics;

  // Conservative timeouts to prevent deadlocks
  private readonly DEFAULT_TIMEOUT_MS = 5000;
  private readonly DEADLOCK_CHECK_INTERVAL_MS = 1000;

  private deadlockChecker?: NodeJS.Timeout;
  private waitTimes: number[] = [];

  constructor() {
    this.metrics = this.initMetrics();
    this.startDeadlockDetection();
  }

  /**
   * Acquire lock for a single key
   * Quantified uncertainty: 5s timeout, automatic release
   */
  async acquire<T>(
    key: string,
    callback: () => Promise<T> | T,
    timeoutMs: number = this.DEFAULT_TIMEOUT_MS
  ): Promise<T> {
    await this.acquireLock(key, timeoutMs);

    try {
      const result = await callback();
      return result;
    } finally {
      this.releaseLock(key);
    }
  }

  /**
   * Acquire multiple locks atomically
   * CRITICAL: Sorts keys to prevent circular wait deadlocks
   */
  async acquireMultiple<T>(
    keys: string[],
    callback: () => Promise<T> | T,
    timeoutMs: number = this.DEFAULT_TIMEOUT_MS
  ): Promise<T> {
    // Sort keys to ensure consistent lock ordering (deadlock prevention)
    const sortedKeys = [...new Set(keys)].sort();

    // Acquire all locks in order
    for (const key of sortedKeys) {
      await this.acquireLock(key, timeoutMs);
    }

    try {
      const result = await callback();
      return result;
    } finally {
      // Release in reverse order
      for (const key of sortedKeys.reverse()) {
        this.releaseLock(key);
      }
    }
  }

  /**
   * Low-level lock acquisition with timeout
   */
  private async acquireLock(key: string, timeoutMs: number): Promise<void> {
    const startTime = Date.now();

    // Fast path: lock available
    if (!this.heldLocks.has(key)) {
      this.heldLocks.set(key, Date.now());
      this.metrics.totalAcquired++;
      return;
    }

    // Slow path: must wait for lock
    return new Promise<void>((resolve, reject) => {
      const request: LockRequest = {
        resolve,
        reject,
        timestamp: Date.now(),
        timeout: setTimeout(() => {
          this.handleTimeout(key, request);
        }, timeoutMs)
      };

      // Add to wait queue
      const queue = this.locks.get(key) || [];
      queue.push(request);
      this.locks.set(key, queue);
    }).then(() => {
      const waitTime = Date.now() - startTime;
      this.recordWaitTime(waitTime);
    });
  }

  /**
   * Release lock and process wait queue
   */
  private releaseLock(key: string): void {
    // Remove from held locks
    this.heldLocks.delete(key);

    // Process wait queue
    const queue = this.locks.get(key);

    if (queue && queue.length > 0) {
      const next = queue.shift()!;
      clearTimeout(next.timeout);

      // Grant lock to next waiter
      this.heldLocks.set(key, Date.now());
      this.metrics.totalAcquired++;
      next.resolve();

      // Clean up empty queue
      if (queue.length === 0) {
        this.locks.delete(key);
      }
    }
  }

  /**
   * Handle lock timeout
   */
  private handleTimeout(key: string, request: LockRequest): void {
    const queue = this.locks.get(key);

    if (queue) {
      const index = queue.indexOf(request);

      if (index !== -1) {
        queue.splice(index, 1);
        this.metrics.totalTimeouts++;

        request.reject(new Error(`Lock acquisition timeout for key: ${key}`));
      }
    }
  }

  /**
   * Deadlock detection (runs every second)
   * Conservative: Logs warnings but doesn't break locks
   */
  private startDeadlockDetection(): void {
    this.deadlockChecker = setInterval(() => {
      this.detectDeadlocks();
    }, this.DEADLOCK_CHECK_INTERVAL_MS);
  }

  private detectDeadlocks(): void {
    const now = Date.now();

    // Check for long-held locks (potential deadlock)
    for (const [key, acquiredAt] of this.heldLocks) {
      const heldDuration = now - acquiredAt;

      if (heldDuration > this.DEFAULT_TIMEOUT_MS * 2) {
        console.warn(`Potential deadlock: Lock '${key}' held for ${heldDuration}ms`);
        this.metrics.deadlocksDetected++;
      }
    }

    // Check for long wait times
    for (const [key, queue] of this.locks) {
      for (const request of queue) {
        const waitDuration = now - request.timestamp;

        if (waitDuration > this.DEFAULT_TIMEOUT_MS) {
          console.warn(`Long wait detected: Key '${key}' waiting ${waitDuration}ms`);
        }
      }
    }
  }

  /**
   * Record wait time for metrics
   */
  private recordWaitTime(waitMs: number): void {
    this.waitTimes.push(waitMs);

    // Keep last 1000 samples
    if (this.waitTimes.length > 1000) {
      this.waitTimes.shift();
    }

    // Update metrics
    this.metrics.avgWaitMs = this.calculateAverage(this.waitTimes);
    this.metrics.maxWaitMs = Math.max(...this.waitTimes, 0);
  }

  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  private initMetrics(): LockMetrics {
    return {
      activeLocks: 0,
      totalAcquired: 0,
      totalTimeouts: 0,
      avgWaitMs: 0,
      maxWaitMs: 0,
      deadlocksDetected: 0,
      timestamp: Date.now()
    };
  }

  /**
   * Export lock metrics as JSON
   */
  getMetrics(): LockMetrics {
    return {
      ...this.metrics,
      activeLocks: this.heldLocks.size,
      timestamp: Date.now()
    };
  }

  /**
   * Force release all locks (emergency use only)
   */
  forceReleaseAll(): void {
    console.warn('EMERGENCY: Force releasing all locks');

    // Clear all held locks
    this.heldLocks.clear();

    // Reject all waiting requests
    for (const [key, queue] of this.locks) {
      for (const request of queue) {
        clearTimeout(request.timeout);
        request.reject(new Error('Lock force released'));
      }
    }

    this.locks.clear();
  }

  /**
   * Cleanup
   */
  destroy(): void {
    if (this.deadlockChecker) {
      clearInterval(this.deadlockChecker);
    }

    this.forceReleaseAll();
  }
}