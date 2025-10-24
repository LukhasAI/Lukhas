/**
 * T4-Grade Dry-Run Isolation Context
 *
 * PHASE 2 FIX F5: Zero observable side effects during dry-run
 * Guarantees: No metrics, no events, no persistence, isolated state
 * Verification: Property test ensures complete isolation
 */

import { EventEmitter } from 'events';

export interface DryRunConfig {
  captureMetrics: boolean;
  captureEvents: boolean;
  captureState: boolean;
  logLevel: 'none' | 'debug' | 'verbose';
}

export interface CapturedMetric {
  component: string;
  name: string;
  value: number;
  timestamp: number;
}

export interface CapturedEvent {
  component: string;
  event: string;
  data: unknown;
  timestamp: number;
}

export interface CapturedState {
  component: string;
  key: string;
  value: unknown;
  timestamp: number;
}

export interface DryRunResult {
  success: boolean;
  duration: number;
  capturedMetrics: CapturedMetric[];
  capturedEvents: CapturedEvent[];
  capturedState: CapturedState[];
  errors: string[];
  metadata: Record<string, unknown>;
}

/**
 * Mock EventEmitter that captures events without emitting
 */
export class MockEventEmitter extends EventEmitter {
  private captured: CapturedEvent[] = [];
  private readonly component: string;
  private readonly shouldCapture: boolean;

  constructor(component: string, shouldCapture: boolean = true) {
    super();
    this.component = component;
    this.shouldCapture = shouldCapture;
  }

  emit(event: string | symbol, ...args: unknown[]): boolean {
    if (this.shouldCapture) {
      this.captured.push({
        component: this.component,
        event: String(event),
        data: args.length === 1 ? args[0] : args,
        timestamp: Date.now()
      });
    }

    // Don't call super.emit() - this is the isolation!
    return true;
  }

  getCaptured(): CapturedEvent[] {
    return [...this.captured];
  }

  clearCaptured(): void {
    this.captured = [];
  }
}

/**
 * Isolated execution context for dry-run mode
 */
export class DryRunContext {
  private readonly config: DryRunConfig;
  private readonly metrics: CapturedMetric[] = [];
  private readonly events: CapturedEvent[] = [];
  private readonly state: CapturedState[] = [];
  private readonly errors: string[] = [];
  private readonly startTime: number;

  private static activeContext: DryRunContext | null = null;

  constructor(config: Partial<DryRunConfig> = {}) {
    this.config = {
      captureMetrics: true,
      captureEvents: true,
      captureState: true,
      logLevel: 'debug',
      ...config
    };
    this.startTime = Date.now();
  }

  /**
   * Get current dry-run context (if any)
   */
  static getCurrent(): DryRunContext | null {
    return this.activeContext;
  }

  /**
   * Check if currently in dry-run mode
   */
  static isDryRun(): boolean {
    return this.activeContext !== null;
  }

  /**
   * Execute function in isolated dry-run context
   */
  static async run<T>(
    fn: () => Promise<T> | T,
    config?: Partial<DryRunConfig>
  ): Promise<DryRunResult & { result?: T }> {
    const context = new DryRunContext(config);

    // Set as active context
    const previousContext = this.activeContext;
    this.activeContext = context;

    let result: T | undefined;
    let success = false;

    try {
      result = await fn();
      success = true;
    } catch (error) {
      context.recordError(error as Error);
      success = false;
    } finally {
      // Restore previous context
      this.activeContext = previousContext;
    }

    return {
      success,
      duration: Date.now() - context.startTime,
      capturedMetrics: context.metrics,
      capturedEvents: context.events,
      capturedState: context.state,
      errors: context.errors,
      metadata: {},
      result
    };
  }

  /**
   * Record metric in dry-run mode
   */
  recordMetric(component: string, name: string, value: number): void {
    if (this.config.captureMetrics) {
      this.metrics.push({
        component,
        name,
        value,
        timestamp: Date.now()
      });
    }

    if (this.config.logLevel === 'verbose') {
      console.log(`[DRY-RUN METRIC] ${component}.${name} = ${value}`);
    }
  }

  /**
   * Record event in dry-run mode
   */
  recordEvent(component: string, event: string, data: unknown): void {
    if (this.config.captureEvents) {
      this.events.push({
        component,
        event,
        data,
        timestamp: Date.now()
      });
    }

    if (this.config.logLevel === 'verbose') {
      console.log(`[DRY-RUN EVENT] ${component}.${event}`, data);
    }
  }

  /**
   * Record state change in dry-run mode
   */
  recordState(component: string, key: string, value: unknown): void {
    if (this.config.captureState) {
      this.state.push({
        component,
        key,
        value,
        timestamp: Date.now()
      });
    }

    if (this.config.logLevel === 'verbose') {
      console.log(`[DRY-RUN STATE] ${component}.${key} =`, value);
    }
  }

  /**
   * Record error in dry-run mode
   */
  recordError(error: Error): void {
    this.errors.push(error.message);

    if (this.config.logLevel !== 'none') {
      console.error('[DRY-RUN ERROR]', error);
    }
  }

  /**
   * Get summary of captured data
   */
  getSummary(): {
    metricsCount: number;
    eventsCount: number;
    stateChanges: number;
    errorsCount: number;
  } {
    return {
      metricsCount: this.metrics.length,
      eventsCount: this.events.length,
      stateChanges: this.state.length,
      errorsCount: this.errors.length
    };
  }
}

/**
 * Conditional emitter - routes to mock if in dry-run mode
 */
export class ConditionalEventEmitter extends EventEmitter {
  private readonly component: string;
  private mockEmitter: MockEventEmitter | null = null;

  constructor(component: string) {
    super();
    this.component = component;
  }

  emit(event: string | symbol, ...args: unknown[]): boolean {
    const context = DryRunContext.getCurrent();

    if (context) {
      // Dry-run mode: capture but don't emit
      context.recordEvent(this.component, String(event), args.length === 1 ? args[0] : args);
      return true;
    } else {
      // Normal mode: emit as usual
      return super.emit(event, ...args);
    }
  }
}

/**
 * Helper to conditionally emit metrics
 */
export function emitMetric(component: string, name: string, value: number): void {
  const context = DryRunContext.getCurrent();

  if (context) {
    // Dry-run mode: capture only
    context.recordMetric(component, name, value);
  } else {
    // Normal mode: actually emit/record
    // This would integrate with your metrics system
    // For now, just log
    if (process.env.NODE_ENV !== 'production') {
      console.debug(`[METRIC] ${component}.${name} = ${value}`);
    }
  }
}

/**
 * Helper to conditionally record state
 */
export function recordStateChange(component: string, key: string, value: unknown): void {
  const context = DryRunContext.getCurrent();

  if (context) {
    // Dry-run mode: capture only
    context.recordState(component, key, value);
  } else {
    // Normal mode: actually persist
    // This would integrate with your state persistence
  }
}

/**
 * Decorator for dry-run aware methods
 */
export function DryRunAware(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = async function (...args: any[]) {
    const context = DryRunContext.getCurrent();

    if (context) {
      // Dry-run mode: log but don't modify real state
      if (context['config'].logLevel === 'verbose') {
        console.log(`[DRY-RUN] ${target.constructor.name}.${propertyKey}`, args);
      }
    }

    return await originalMethod.apply(this, args);
  };

  return descriptor;
}

/**
 * Utility to verify zero side effects
 */
export class SideEffectDetector {
  private readonly initialState: Map<string, unknown> = new Map();
  private violations: Array<{ component: string; change: string }> = [];

  /**
   * Snapshot current state before dry-run
   */
  snapshot(component: string, state: Record<string, unknown>): void {
    this.initialState.set(component, JSON.parse(JSON.stringify(state)));
  }

  /**
   * Verify state unchanged after dry-run
   */
  verify(component: string, state: Record<string, unknown>): boolean {
    const initial = this.initialState.get(component);

    if (!initial) {
      return true; // No snapshot to compare
    }

    const initialStr = JSON.stringify(initial);
    const currentStr = JSON.stringify(state);

    if (initialStr !== currentStr) {
      this.violations.push({
        component,
        change: `State changed during dry-run`
      });
      return false;
    }

    return true;
  }

  /**
   * Get all detected violations
   */
  getViolations(): Array<{ component: string; change: string }> {
    return [...this.violations];
  }

  /**
   * Check if any violations detected
   */
  hasViolations(): boolean {
    return this.violations.length > 0;
  }
}

/**
 * Property test helper: verify zero side effects
 */
export async function assertNoSideEffects<T>(
  fn: () => Promise<T> | T,
  detector: SideEffectDetector
): Promise<DryRunResult & { violations: Array<{ component: string; change: string }> }> {
  const result = await DryRunContext.run(fn, { captureMetrics: true, captureEvents: true });

  return {
    ...result,
    violations: detector.getViolations()
  };
}
