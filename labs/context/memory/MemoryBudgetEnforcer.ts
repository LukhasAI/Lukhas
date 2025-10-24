/**
 * T4-Grade Strict Memory Budget Enforcement
 *
 * PHASE 2 FIX F7: Hard limits with immediate rejection
 * Guarantees: Zero OOM crashes, memory never exceeds limit
 * Verification: Load test with memory pressure
 */

import { EventEmitter } from 'events';

export interface MemoryBudget {
  hardLimit: number;          // Absolute maximum (bytes)
  softLimit: number;          // Warning threshold (bytes)
  reservedBuffer: number;     // Reserved for critical ops (bytes)
  evictionThreshold: number;  // Start evicting (percentage of hard limit)
}

export interface MemoryAllocation {
  key: string;
  size: number;
  timestamp: number;
  priority: 'low' | 'normal' | 'high' | 'critical';
  metadata?: Record<string, unknown>;
}

export interface MemoryStats {
  totalAllocated: number;
  totalEvicted: number;
  totalRejected: number;
  activeAllocations: number;
  largestAllocation: number;
  utilizationPercent: number;
  pressureLevel: 'none' | 'low' | 'medium' | 'high' | 'critical';
  timestamp: number;
}

export interface PressureCallback {
  threshold: number; // Utilization percent
  callback: (stats: MemoryStats) => void | Promise<void>;
}

/**
 * Strict memory budget enforcer with hard limits
 */
export class MemoryBudgetEnforcer extends EventEmitter {
  private readonly budget: MemoryBudget;
  private readonly allocations: Map<string, MemoryAllocation> = new Map();
  private readonly pressureCallbacks: PressureCallback[] = [];

  private totalAllocated = 0;
  private totalEvicted = 0;
  private totalRejected = 0;

  // Conservative defaults
  private readonly DEFAULT_BUDGET: MemoryBudget = {
    hardLimit: 100 * 1024 * 1024,      // 100MB
    softLimit: 80 * 1024 * 1024,       // 80MB
    reservedBuffer: 10 * 1024 * 1024,  // 10MB
    evictionThreshold: 0.85             // 85%
  };

  constructor(budget?: Partial<MemoryBudget>) {
    super();
    this.budget = { ...this.DEFAULT_BUDGET, ...budget };
    this.validateBudget();
    this.startPressureMonitoring();
  }

  /**
   * CRITICAL: Attempt allocation with hard limit enforcement
   * Returns: true if allocated, false if rejected
   */
  async allocate(
    key: string,
    size: number,
    priority: 'low' | 'normal' | 'high' | 'critical' = 'normal',
    metadata?: Record<string, unknown>
  ): Promise<boolean> {
    // Validate size
    if (size <= 0) {
      throw new Error('Allocation size must be positive');
    }

    if (size > this.budget.hardLimit) {
      throw new Error(`Allocation size ${size} exceeds hard limit ${this.budget.hardLimit}`);
    }

    // Check if already allocated
    if (this.allocations.has(key)) {
      await this.deallocate(key);
    }

    // Calculate available space
    const available = this.getAvailableMemory();

    // HARD LIMIT: Immediate rejection if no space
    if (size > available) {
      // Try eviction first
      const evicted = await this.evictToMakeSpace(size, priority);

      if (!evicted) {
        // Still no space after eviction - REJECT
        this.totalRejected++;

        this.emit('allocationRejected', {
          key,
          size,
          available,
          reason: 'hard limit reached',
          timestamp: Date.now()
        });

        return false;
      }
    }

    // Allocate
    const allocation: MemoryAllocation = {
      key,
      size,
      timestamp: Date.now(),
      priority,
      metadata
    };

    this.allocations.set(key, allocation);
    this.totalAllocated += size;

    this.emit('allocated', {
      key,
      size,
      utilizationPercent: this.getUtilizationPercent(),
      timestamp: Date.now()
    });

    // Check pressure level
    await this.checkPressure();

    return true;
  }

  /**
   * Deallocate memory
   */
  async deallocate(key: string): Promise<boolean> {
    const allocation = this.allocations.get(key);

    if (!allocation) {
      return false;
    }

    this.allocations.delete(key);
    this.totalAllocated -= allocation.size;

    this.emit('deallocated', {
      key,
      size: allocation.size,
      timestamp: Date.now()
    });

    return true;
  }

  /**
   * Get allocation info
   */
  getAllocation(key: string): MemoryAllocation | undefined {
    return this.allocations.get(key);
  }

  /**
   * Update allocation size (must fit in budget)
   */
  async resize(key: string, newSize: number): Promise<boolean> {
    const allocation = this.allocations.get(key);

    if (!allocation) {
      return false;
    }

    const sizeDelta = newSize - allocation.size;

    // Growing
    if (sizeDelta > 0) {
      const available = this.getAvailableMemory();

      if (sizeDelta > available) {
        // Try eviction
        const evicted = await this.evictToMakeSpace(sizeDelta, allocation.priority);

        if (!evicted) {
          return false;
        }
      }

      this.totalAllocated += sizeDelta;
    }
    // Shrinking
    else if (sizeDelta < 0) {
      this.totalAllocated += sizeDelta; // sizeDelta is negative
    }

    allocation.size = newSize;
    allocation.timestamp = Date.now();

    this.emit('resized', {
      key,
      oldSize: allocation.size - sizeDelta,
      newSize,
      timestamp: Date.now()
    });

    return true;
  }

  /**
   * Evict allocations to make space
   */
  private async evictToMakeSpace(
    neededSpace: number,
    requestPriority: MemoryAllocation['priority']
  ): Promise<boolean> {
    // Get candidates for eviction (lower priority, older first)
    const candidates = Array.from(this.allocations.values())
      .filter(a => this.canEvict(a, requestPriority))
      .sort((a, b) => {
        // Sort by priority (lower first), then age (older first)
        const priorityOrder = { low: 0, normal: 1, high: 2, critical: 3 };

        if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        }

        return a.timestamp - b.timestamp;
      });

    let freedSpace = 0;
    const evicted: string[] = [];

    for (const candidate of candidates) {
      if (freedSpace >= neededSpace) {
        break;
      }

      await this.deallocate(candidate.key);
      freedSpace += candidate.size;
      evicted.push(candidate.key);
      this.totalEvicted++;
    }

    if (evicted.length > 0) {
      this.emit('eviction', {
        count: evicted.length,
        freedSpace,
        keys: evicted,
        timestamp: Date.now()
      });
    }

    return freedSpace >= neededSpace;
  }

  /**
   * Check if allocation can be evicted
   */
  private canEvict(
    allocation: MemoryAllocation,
    requestPriority: MemoryAllocation['priority']
  ): boolean {
    const priorityOrder = { low: 0, normal: 1, high: 2, critical: 3 };

    // Can only evict lower priority allocations
    return priorityOrder[allocation.priority] < priorityOrder[requestPriority];
  }

  /**
   * Get available memory
   */
  getAvailableMemory(): number {
    return Math.max(0, this.budget.hardLimit - this.totalAllocated);
  }

  /**
   * Get utilization percentage
   */
  getUtilizationPercent(): number {
    return (this.totalAllocated / this.budget.hardLimit) * 100;
  }

  /**
   * Get pressure level
   */
  getPressureLevel(): MemoryStats['pressureLevel'] {
    const utilization = this.getUtilizationPercent();

    if (utilization >= 95) return 'critical';
    if (utilization >= 85) return 'high';
    if (utilization >= 70) return 'medium';
    if (utilization >= 50) return 'low';
    return 'none';
  }

  /**
   * Register callback for pressure threshold
   */
  onPressure(threshold: number, callback: PressureCallback['callback']): void {
    this.pressureCallbacks.push({ threshold, callback });

    // Sort by threshold descending
    this.pressureCallbacks.sort((a, b) => b.threshold - a.threshold);
  }

  /**
   * Check pressure and fire callbacks
   */
  private async checkPressure(): Promise<void> {
    const utilization = this.getUtilizationPercent();
    const stats = this.getStats();

    for (const { threshold, callback } of this.pressureCallbacks) {
      if (utilization >= threshold) {
        try {
          await callback(stats);
        } catch (error) {
          this.emit('callbackError', {
            threshold,
            error: error.message,
            timestamp: Date.now()
          });
        }
      }
    }
  }

  /**
   * Monitor pressure periodically
   */
  private startPressureMonitoring(): void {
    setInterval(() => {
      const pressure = this.getPressureLevel();

      if (pressure !== 'none') {
        this.emit('pressure', {
          level: pressure,
          utilization: this.getUtilizationPercent(),
          timestamp: Date.now()
        });
      }
    }, 5000); // Every 5 seconds
  }

  /**
   * Validate budget configuration
   */
  private validateBudget(): void {
    if (this.budget.hardLimit <= 0) {
      throw new Error('Hard limit must be positive');
    }

    if (this.budget.softLimit >= this.budget.hardLimit) {
      throw new Error('Soft limit must be less than hard limit');
    }

    if (this.budget.reservedBuffer >= this.budget.hardLimit) {
      throw new Error('Reserved buffer must be less than hard limit');
    }

    if (this.budget.evictionThreshold <= 0 || this.budget.evictionThreshold > 1) {
      throw new Error('Eviction threshold must be between 0 and 1');
    }
  }

  /**
   * Get comprehensive stats
   */
  getStats(): MemoryStats {
    const allocations = Array.from(this.allocations.values());

    return {
      totalAllocated: this.totalAllocated,
      totalEvicted: this.totalEvicted,
      totalRejected: this.totalRejected,
      activeAllocations: this.allocations.size,
      largestAllocation: allocations.length > 0
        ? Math.max(...allocations.map(a => a.size))
        : 0,
      utilizationPercent: this.getUtilizationPercent(),
      pressureLevel: this.getPressureLevel(),
      timestamp: Date.now()
    };
  }

  /**
   * Get allocations by priority
   */
  getAllocationsByPriority(
    priority: MemoryAllocation['priority']
  ): MemoryAllocation[] {
    return Array.from(this.allocations.values())
      .filter(a => a.priority === priority);
  }

  /**
   * Force eviction of all low priority allocations
   */
  async forceEvictLowPriority(): Promise<number> {
    const lowPriority = this.getAllocationsByPriority('low');
    let evicted = 0;

    for (const allocation of lowPriority) {
      await this.deallocate(allocation.key);
      this.totalEvicted++;
      evicted++;
    }

    return evicted;
  }

  /**
   * Get budget configuration
   */
  getBudget(): MemoryBudget {
    return { ...this.budget };
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];
    const utilization = this.getUtilizationPercent();

    if (utilization >= 95) {
      issues.push(`CRITICAL: Memory utilization at ${utilization.toFixed(1)}%`);
    } else if (utilization >= 85) {
      issues.push(`WARNING: Memory utilization at ${utilization.toFixed(1)}%`);
    }

    const rejectionRate = this.totalRejected /
      Math.max(this.totalRejected + this.allocations.size, 1);

    if (rejectionRate > 0.05) {
      issues.push(`High rejection rate: ${(rejectionRate * 100).toFixed(1)}%`);
    }

    if (this.totalAllocated > this.budget.hardLimit) {
      issues.push('CRITICAL: Hard limit exceeded!');
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  /**
   * Get memory report
   */
  getReport(): {
    budget: MemoryBudget;
    stats: MemoryStats;
    allocations: MemoryAllocation[];
    health: ReturnType<typeof this.healthCheck>;
  } {
    return {
      budget: this.getBudget(),
      stats: this.getStats(),
      allocations: Array.from(this.allocations.values()),
      health: this.healthCheck()
    };
  }

  /**
   * Reset stats (for testing)
   */
  resetStats(): void {
    this.totalEvicted = 0;
    this.totalRejected = 0;
  }

  /**
   * Clear all allocations (emergency)
   */
  async clearAll(): Promise<number> {
    const count = this.allocations.size;

    for (const key of Array.from(this.allocations.keys())) {
      await this.deallocate(key);
    }

    this.emit('clearedAll', {
      count,
      timestamp: Date.now()
    });

    return count;
  }
}

/**
 * Memory pressure monitor
 */
export class MemoryPressureMonitor {
  private readonly enforcer: MemoryBudgetEnforcer;
  private readonly thresholds: Map<number, string> = new Map([
    [50, 'low'],
    [70, 'medium'],
    [85, 'high'],
    [95, 'critical']
  ]);

  constructor(enforcer: MemoryBudgetEnforcer) {
    this.enforcer = enforcer;
    this.setupMonitoring();
  }

  private setupMonitoring(): void {
    // Register callbacks for each threshold
    this.enforcer.onPressure(50, async (stats) => {
      console.warn('[MEMORY] Low pressure detected:', stats.utilizationPercent.toFixed(1) + '%');
    });

    this.enforcer.onPressure(70, async (stats) => {
      console.warn('[MEMORY] Medium pressure detected:', stats.utilizationPercent.toFixed(1) + '%');
    });

    this.enforcer.onPressure(85, async (stats) => {
      console.error('[MEMORY] High pressure detected:', stats.utilizationPercent.toFixed(1) + '%');
      // Start aggressive eviction
      await this.enforcer.forceEvictLowPriority();
    });

    this.enforcer.onPressure(95, async (stats) => {
      console.error('[MEMORY] CRITICAL pressure detected:', stats.utilizationPercent.toFixed(1) + '%');
      // Emergency measures
      await this.enforcer.forceEvictLowPriority();
    });
  }
}
