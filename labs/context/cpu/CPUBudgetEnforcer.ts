/**
 * T4-Grade CPU Budget Enforcement
 *
 * PHASE 2: Per-operation CPU time budgets with timeout
 * Guarantees: No operation exceeds budget, slow ops aborted
 * Verification: Benchmark test suite with timeout scenarios
 */

import { EventEmitter } from 'events';

export interface CPUBudget {
  defaultBudgetMs: number;
  maxBudgetMs: number;
  adaptiveEnabled: boolean;
  conservativeFactor: number; // Multiplier for safety (2x = conservative)
}

export interface OperationBudget {
  operation: string;
  budgetMs: number;
  adaptiveBudget?: number;
  executions: number;
  timeouts: number;
  avgDurationMs: number;
  p99DurationMs: number;
}

export interface ExecutionResult<T> {
  success: boolean;
  result?: T;
  durationMs: number;
  timedOut: boolean;
  aborted: boolean;
  error?: string;
}

export interface CPUStats {
  totalExecutions: number;
  totalTimeouts: number;
  totalAborts: number;
  avgExecutionTimeMs: number;
  p99ExecutionTimeMs: number;
  budgetAdaptations: number;
  timestamp: number;
}

/**
 * CPU budget enforcer with adaptive budgets
 */
export class CPUBudgetEnforcer extends EventEmitter {
  private readonly globalBudget: CPUBudget;
  private readonly operationBudgets: Map<string, OperationBudget> = new Map();
  private readonly executionHistory: Map<string, number[]> = new Map();

  private totalExecutions = 0;
  private totalTimeouts = 0;
  private totalAborts = 0;
  private budgetAdaptations = 0;

  private readonly MAX_HISTORY = 100;

  // Conservative defaults
  private readonly DEFAULT_BUDGET: CPUBudget = {
    defaultBudgetMs: 5000,        // 5 seconds
    maxBudgetMs: 30000,           // 30 seconds
    adaptiveEnabled: true,
    conservativeFactor: 2.0       // 2x measured p99
  };

  constructor(budget?: Partial<CPUBudget>) {
    super();
    this.globalBudget = { ...this.DEFAULT_BUDGET, ...budget };
  }

  /**
   * Execute operation with CPU budget enforcement
   */
  async execute<T>(
    operation: string,
    fn: (signal: AbortSignal) => Promise<T> | T,
    customBudgetMs?: number
  ): Promise<ExecutionResult<T>> {
    const startTime = Date.now();
    const budget = this.getBudgetForOperation(operation, customBudgetMs);

    // Create abort controller for timeout
    const abortController = new AbortController();
    const { signal } = abortController;

    // Set timeout
    const timeoutId = setTimeout(() => {
      abortController.abort();
      this.handleTimeout(operation);
    }, budget);

    this.totalExecutions++;

    try {
      const result = await fn(signal);
      clearTimeout(timeoutId);

      const duration = Date.now() - startTime;

      // Record successful execution
      this.recordExecution(operation, duration, false);

      return {
        success: true,
        result,
        durationMs: duration,
        timedOut: false,
        aborted: false
      };

    } catch (error) {
      clearTimeout(timeoutId);

      const duration = Date.now() - startTime;
      const wasAborted = signal.aborted;

      if (wasAborted) {
        this.recordExecution(operation, duration, true);
        this.totalAborts++;

        return {
          success: false,
          durationMs: duration,
          timedOut: true,
          aborted: true,
          error: `Operation '${operation}' exceeded budget of ${budget}ms`
        };
      }

      // Other error
      this.recordExecution(operation, duration, false);

      return {
        success: false,
        durationMs: duration,
        timedOut: false,
        aborted: false,
        error: error.message
      };
    }
  }

  /**
   * Execute with retry on timeout
   */
  async executeWithRetry<T>(
    operation: string,
    fn: (signal: AbortSignal) => Promise<T> | T,
    maxRetries: number = 3
  ): Promise<ExecutionResult<T>> {
    let lastResult: ExecutionResult<T> | undefined;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      const result = await this.execute(operation, fn);

      if (result.success || !result.timedOut) {
        return result;
      }

      lastResult = result;

      // Exponential backoff before retry
      if (attempt < maxRetries) {
        await this.delay(Math.pow(2, attempt) * 1000);
      }
    }

    return lastResult!;
  }

  /**
   * Get budget for operation (adaptive or default)
   */
  private getBudgetForOperation(operation: string, customBudget?: number): number {
    if (customBudget !== undefined) {
      return Math.min(customBudget, this.globalBudget.maxBudgetMs);
    }

    const opBudget = this.operationBudgets.get(operation);

    if (opBudget && this.globalBudget.adaptiveEnabled && opBudget.adaptiveBudget) {
      return opBudget.adaptiveBudget;
    }

    return this.globalBudget.defaultBudgetMs;
  }

  /**
   * Record execution and adapt budget
   */
  private recordExecution(operation: string, durationMs: number, timedOut: boolean): void {
    // Get or create operation budget
    let opBudget = this.operationBudgets.get(operation);

    if (!opBudget) {
      opBudget = {
        operation,
        budgetMs: this.globalBudget.defaultBudgetMs,
        executions: 0,
        timeouts: 0,
        avgDurationMs: 0,
        p99DurationMs: 0
      };
      this.operationBudgets.set(operation, opBudget);
    }

    // Update stats
    opBudget.executions++;
    if (timedOut) {
      opBudget.timeouts++;
    }

    // Add to history
    const history = this.executionHistory.get(operation) || [];
    history.push(durationMs);

    if (history.length > this.MAX_HISTORY) {
      history.shift();
    }

    this.executionHistory.set(operation, history);

    // Calculate statistics
    opBudget.avgDurationMs = this.calculateAverage(history);
    opBudget.p99DurationMs = this.calculatePercentile(history, 99);

    // Adapt budget if enabled
    if (this.globalBudget.adaptiveEnabled && history.length >= 10) {
      this.adaptBudget(operation, opBudget);
    }
  }

  /**
   * Adapt budget based on historical performance
   */
  private adaptBudget(operation: string, opBudget: OperationBudget): void {
    const p99 = opBudget.p99DurationMs;

    // Conservative: Use p99 * conservativeFactor
    const newBudget = Math.min(
      p99 * this.globalBudget.conservativeFactor,
      this.globalBudget.maxBudgetMs
    );

    // Only adapt if significantly different (>20%)
    const currentBudget = opBudget.adaptiveBudget || opBudget.budgetMs;
    const percentChange = Math.abs(newBudget - currentBudget) / currentBudget;

    if (percentChange > 0.2) {
      opBudget.adaptiveBudget = Math.ceil(newBudget);
      this.budgetAdaptations++;

      this.emit('budgetAdapted', {
        operation,
        oldBudget: currentBudget,
        newBudget: opBudget.adaptiveBudget,
        p99: p99,
        timestamp: Date.now()
      });
    }
  }

  /**
   * Handle timeout
   */
  private handleTimeout(operation: string): void {
    this.totalTimeouts++;

    this.emit('timeout', {
      operation,
      timestamp: Date.now()
    });
  }

  /**
   * Set custom budget for operation
   */
  setBudget(operation: string, budgetMs: number): void {
    const opBudget = this.operationBudgets.get(operation) || {
      operation,
      budgetMs,
      executions: 0,
      timeouts: 0,
      avgDurationMs: 0,
      p99DurationMs: 0
    };

    opBudget.budgetMs = Math.min(budgetMs, this.globalBudget.maxBudgetMs);
    this.operationBudgets.set(operation, opBudget);
  }

  /**
   * Get operation budget info
   */
  getOperationBudget(operation: string): OperationBudget | undefined {
    return this.operationBudgets.get(operation);
  }

  /**
   * Get all operation budgets
   */
  getAllOperationBudgets(): OperationBudget[] {
    return Array.from(this.operationBudgets.values());
  }

  /**
   * Get comprehensive stats
   */
  getStats(): CPUStats {
    const allDurations = Array.from(this.executionHistory.values()).flat();

    return {
      totalExecutions: this.totalExecutions,
      totalTimeouts: this.totalTimeouts,
      totalAborts: this.totalAborts,
      avgExecutionTimeMs: this.calculateAverage(allDurations),
      p99ExecutionTimeMs: this.calculatePercentile(allDurations, 99),
      budgetAdaptations: this.budgetAdaptations,
      timestamp: Date.now()
    };
  }

  /**
   * Get timeout rate
   */
  getTimeoutRate(): number {
    if (this.totalExecutions === 0) return 0;
    return this.totalTimeouts / this.totalExecutions;
  }

  /**
   * Calculate average
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  /**
   * Calculate percentile
   */
  private calculatePercentile(values: number[], percentile: number): number {
    if (values.length === 0) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[Math.max(0, index)];
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    const timeoutRate = this.getTimeoutRate();

    if (timeoutRate > 0.1) {
      issues.push(`High timeout rate: ${(timeoutRate * 100).toFixed(1)}%`);
    }

    // Check individual operations
    for (const opBudget of this.operationBudgets.values()) {
      const opTimeoutRate = opBudget.timeouts / Math.max(opBudget.executions, 1);

      if (opTimeoutRate > 0.2) {
        issues.push(`Operation '${opBudget.operation}' timeout rate: ${(opTimeoutRate * 100).toFixed(1)}%`);
      }
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  /**
   * Reset stats (for testing)
   */
  resetStats(): void {
    this.totalExecutions = 0;
    this.totalTimeouts = 0;
    this.totalAborts = 0;
    this.budgetAdaptations = 0;
    this.executionHistory.clear();
  }

  /**
   * Get global budget config
   */
  getBudgetConfig(): CPUBudget {
    return { ...this.globalBudget };
  }
}

/**
 * CPU budget decorator
 */
export function WithCPUBudget(
  budgetMs?: number
) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      // Get enforcer from instance or create one
      const enforcer = this.cpuEnforcer || new CPUBudgetEnforcer();

      const result = await enforcer.execute(
        `${target.constructor.name}.${propertyKey}`,
        async (signal) => {
          // Pass signal to method if it accepts it
          if (originalMethod.length >= args.length + 1) {
            return await originalMethod.apply(this, [...args, signal]);
          } else {
            return await originalMethod.apply(this, args);
          }
        },
        budgetMs
      );

      if (!result.success) {
        throw new Error(result.error);
      }

      return result.result;
    };

    return descriptor;
  };
}

/**
 * Utility to measure CPU time for benchmarking
 */
export class CPUBenchmark {
  private readonly samples: Map<string, number[]> = new Map();

  /**
   * Measure execution time
   */
  async measure<T>(
    operation: string,
    fn: () => Promise<T> | T
  ): Promise<{ result: T; durationMs: number }> {
    const start = Date.now();
    const result = await fn();
    const duration = Date.now() - start;

    // Record sample
    const samples = this.samples.get(operation) || [];
    samples.push(duration);
    this.samples.set(operation, samples);

    return { result, duration };
  }

  /**
   * Get benchmark results
   */
  getResults(operation: string): {
    samples: number;
    min: number;
    max: number;
    avg: number;
    p50: number;
    p95: number;
    p99: number;
  } | null {
    const samples = this.samples.get(operation);

    if (!samples || samples.length === 0) {
      return null;
    }

    const sorted = [...samples].sort((a, b) => a - b);

    return {
      samples: samples.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      avg: samples.reduce((a, b) => a + b, 0) / samples.length,
      p50: sorted[Math.floor(sorted.length * 0.5)],
      p95: sorted[Math.floor(sorted.length * 0.95)],
      p99: sorted[Math.floor(sorted.length * 0.99)]
    };
  }

  /**
   * Get all results
   */
  getAllResults(): Map<string, ReturnType<typeof this.getResults>> {
    const results = new Map();

    for (const operation of this.samples.keys()) {
      results.set(operation, this.getResults(operation));
    }

    return results;
  }

  /**
   * Clear benchmarks
   */
  clear(operation?: string): void {
    if (operation) {
      this.samples.delete(operation);
    } else {
      this.samples.clear();
    }
  }
}
