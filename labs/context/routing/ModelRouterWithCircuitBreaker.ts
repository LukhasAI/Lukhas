/**
 * T4-Grade Model Router with Circuit Breaker
 *
 * CRITICAL FIX F3: Circuit breaker prevents cascade failures
 * Conservative: 30s timeout, automatic retry with backoff
 * Machine-parsable routing metrics
 */

import { EventEmitter } from 'events';

// Circuit breaker states
export enum CircuitState {
  CLOSED = 'CLOSED',     // Normal operation
  OPEN = 'OPEN',         // Failing, rejecting requests
  HALF_OPEN = 'HALF_OPEN' // Testing recovery
}

export interface ModelEndpoint {
  id: string;
  url: string;
  priority: number;
  capabilities: string[];
  maxConcurrent: number;
  timeout: number;
}

export interface RoutingRequest {
  id: string;
  context: Record<string, unknown>;
  model?: string;
  requirements?: string[];
  priority?: number;
}

export interface RoutingResponse {
  requestId: string;
  modelId: string;
  result: unknown;
  latencyMs: number;
  attempts: number;
}

export interface CircuitBreakerConfig {
  failureThreshold: number;      // Failures before opening
  successThreshold: number;       // Successes to close from half-open
  timeout: number;               // Request timeout
  resetTimeout: number;          // Time before half-open
  volumeThreshold: number;       // Min requests before opening
}

export interface RouterMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  timeoutRequests: number;
  circuitOpens: number;
  avgLatencyMs: number;
  p99LatencyMs: number;
  activeRequests: number;
  modelFailures: Map<string, number>;
  timestamp: number;
}

interface CircuitBreaker {
  state: CircuitState;
  failures: number;
  successes: number;
  lastFailureTime: number;
  nextAttemptTime: number;
  requestCount: number;
}

export class ModelRouterWithCircuitBreaker extends EventEmitter {
  private readonly models: Map<string, ModelEndpoint> = new Map();
  private readonly circuits: Map<string, CircuitBreaker> = new Map();
  private readonly activeRequests: Map<string, AbortController> = new Map();
  private readonly metrics: RouterMetrics;

  // Conservative defaults
  private readonly DEFAULT_CONFIG: CircuitBreakerConfig = {
    failureThreshold: 5,           // Open after 5 failures
    successThreshold: 3,            // Close after 3 successes
    timeout: 30000,                // 30s timeout
    resetTimeout: 60000,           // 1 minute before retry
    volumeThreshold: 10            // Min 10 requests
  };

  private config: CircuitBreakerConfig;
  private latencyHistory: number[] = [];

  constructor(config?: Partial<CircuitBreakerConfig>) {
    super();
    this.config = { ...this.DEFAULT_CONFIG, ...config };
    this.metrics = this.initMetrics();
    this.startHealthMonitor();
  }

  /**
   * Register model endpoint
   */
  registerModel(model: ModelEndpoint): void {
    this.models.set(model.id, model);
    this.circuits.set(model.id, this.createCircuitBreaker());

    this.emit('modelRegistered', { modelId: model.id });
  }

  /**
   * CRITICAL: Route request with circuit breaker protection
   * Automatic retry with exponential backoff
   */
  async route(request: RoutingRequest): Promise<RoutingResponse> {
    const startTime = Date.now();
    this.metrics.totalRequests++;

    const abortController = new AbortController();
    this.activeRequests.set(request.id, abortController);

    try {
      // Select model based on requirements and circuit state
      const modelId = this.selectModel(request);

      if (!modelId) {
        throw new Error('No available models match requirements');
      }

      // Check circuit breaker
      const circuit = this.circuits.get(modelId)!;

      if (!this.canRoute(circuit)) {
        throw new Error(`Circuit breaker OPEN for model ${modelId}`);
      }

      // Route with timeout and retry
      const response = await this.routeWithRetry(
        request,
        modelId,
        abortController.signal
      );

      // Success: update circuit breaker
      this.recordSuccess(circuit, modelId);
      this.metrics.successfulRequests++;

      const latency = Date.now() - startTime;
      this.recordLatency(latency);

      return {
        ...response,
        latencyMs: latency
      };

    } catch (error) {
      this.metrics.failedRequests++;

      // Record failure for circuit breaker
      if (error.message.includes('timeout')) {
        this.metrics.timeoutRequests++;
      }

      throw error;

    } finally {
      this.activeRequests.delete(request.id);
    }
  }

  /**
   * Route with automatic retry and exponential backoff
   */
  private async routeWithRetry(
    request: RoutingRequest,
    modelId: string,
    signal: AbortSignal
  ): Promise<RoutingResponse> {
    const model = this.models.get(modelId)!;
    const circuit = this.circuits.get(modelId)!;

    let lastError: Error | undefined;
    let attempts = 0;
    const maxAttempts = 3;

    while (attempts < maxAttempts && !signal.aborted) {
      attempts++;

      try {
        // Attempt routing
        const result = await this.executeRoute(
          request,
          model,
          signal
        );

        return {
          requestId: request.id,
          modelId,
          result,
          latencyMs: 0, // Will be set by caller
          attempts
        };

      } catch (error) {
        lastError = error as Error;

        // Record failure
        this.recordFailure(circuit, modelId, error as Error);

        // Check if we should retry
        if (this.shouldRetry(error as Error, attempts, maxAttempts)) {
          // Exponential backoff
          const delay = Math.min(1000 * Math.pow(2, attempts - 1), 10000);
          await this.delay(delay);
        } else {
          break;
        }
      }
    }

    throw lastError || new Error('Route failed after max attempts');
  }

  /**
   * Execute actual routing to model
   */
  private async executeRoute(
    request: RoutingRequest,
    model: ModelEndpoint,
    signal: AbortSignal
  ): Promise<unknown> {
    return new Promise((resolve, reject) => {
      // Set timeout
      const timeout = setTimeout(() => {
        reject(new Error(`Request timeout after ${model.timeout}ms`));
      }, model.timeout);

      // Handle abort
      signal.addEventListener('abort', () => {
        clearTimeout(timeout);
        reject(new Error('Request aborted'));
      });

      // Simulate model execution
      // In production, this would make actual API call
      setTimeout(() => {
        clearTimeout(timeout);

        // Simulate success/failure
        if (Math.random() > 0.1) { // 90% success rate
          resolve({
            response: 'Model response',
            modelId: model.id,
            timestamp: Date.now()
          });
        } else {
          reject(new Error('Model execution failed'));
        }
      }, Math.random() * 1000 + 500); // 500-1500ms latency
    });
  }

  /**
   * Select best available model based on requirements and circuit state
   */
  private selectModel(request: RoutingRequest): string | null {
    const availableModels = Array.from(this.models.entries())
      .filter(([id, model]) => {
        // Check requirements
        if (request.requirements) {
          const hasAllCapabilities = request.requirements.every(
            req => model.capabilities.includes(req)
          );
          if (!hasAllCapabilities) return false;
        }

        // Check circuit breaker
        const circuit = this.circuits.get(id)!;
        return this.canRoute(circuit);
      })
      .sort((a, b) => {
        // Sort by priority
        return b[1].priority - a[1].priority;
      });

    if (availableModels.length === 0) {
      return null;
    }

    // Return highest priority available model
    return availableModels[0][0];
  }

  /**
   * Check if circuit breaker allows routing
   */
  private canRoute(circuit: CircuitBreaker): boolean {
    const now = Date.now();

    switch (circuit.state) {
      case CircuitState.CLOSED:
        return true;

      case CircuitState.OPEN:
        // Check if we should transition to half-open
        if (now >= circuit.nextAttemptTime) {
          circuit.state = CircuitState.HALF_OPEN;
          circuit.successes = 0;
          this.emit('circuitHalfOpen', { timestamp: now });
          return true;
        }
        return false;

      case CircuitState.HALF_OPEN:
        // Allow limited traffic
        return true;

      default:
        return false;
    }
  }

  /**
   * Record successful request
   */
  private recordSuccess(circuit: CircuitBreaker, modelId: string): void {
    circuit.requestCount++;

    switch (circuit.state) {
      case CircuitState.CLOSED:
        // Reset failure count on success
        circuit.failures = 0;
        break;

      case CircuitState.HALF_OPEN:
        circuit.successes++;

        // Check if we can close the circuit
        if (circuit.successes >= this.config.successThreshold) {
          circuit.state = CircuitState.CLOSED;
          circuit.failures = 0;
          circuit.successes = 0;

          this.emit('circuitClosed', {
            modelId,
            timestamp: Date.now()
          });
        }
        break;
    }
  }

  /**
   * Record failed request
   */
  private recordFailure(
    circuit: CircuitBreaker,
    modelId: string,
    error: Error
  ): void {
    circuit.requestCount++;
    circuit.lastFailureTime = Date.now();

    // Track model-specific failures
    const currentFailures = this.metrics.modelFailures.get(modelId) || 0;
    this.metrics.modelFailures.set(modelId, currentFailures + 1);

    switch (circuit.state) {
      case CircuitState.CLOSED:
        circuit.failures++;

        // Check if we should open the circuit
        if (
          circuit.failures >= this.config.failureThreshold &&
          circuit.requestCount >= this.config.volumeThreshold
        ) {
          circuit.state = CircuitState.OPEN;
          circuit.nextAttemptTime = Date.now() + this.config.resetTimeout;
          this.metrics.circuitOpens++;

          this.emit('circuitOpen', {
            modelId,
            failures: circuit.failures,
            timestamp: Date.now()
          });
        }
        break;

      case CircuitState.HALF_OPEN:
        // Single failure in half-open reopens the circuit
        circuit.state = CircuitState.OPEN;
        circuit.failures++;
        circuit.nextAttemptTime = Date.now() + this.config.resetTimeout;
        this.metrics.circuitOpens++;

        this.emit('circuitOpen', {
          modelId,
          reason: 'Failed in half-open state',
          timestamp: Date.now()
        });
        break;
    }
  }

  /**
   * Determine if request should be retried
   */
  private shouldRetry(error: Error, attempt: number, maxAttempts: number): boolean {
    // Don't retry if max attempts reached
    if (attempt >= maxAttempts) {
      return false;
    }

    // Don't retry client errors (4xx equivalent)
    if (error.message.includes('Invalid') || error.message.includes('Unauthorized')) {
      return false;
    }

    // Retry timeouts and server errors
    return error.message.includes('timeout') ||
           error.message.includes('failed') ||
           error.message.includes('unavailable');
  }

  /**
   * Health monitoring
   */
  private startHealthMonitor(): void {
    setInterval(() => {
      // Check for stuck requests
      const now = Date.now();

      for (const [requestId, controller] of this.activeRequests) {
        // Abort requests older than 2x timeout
        if (now - parseInt(requestId.split('_')[1]) > this.config.timeout * 2) {
          console.warn(`Aborting stuck request: ${requestId}`);
          controller.abort();
          this.activeRequests.delete(requestId);
        }
      }

      // Reset circuit breakers that have been open too long
      for (const [modelId, circuit] of this.circuits) {
        if (
          circuit.state === CircuitState.OPEN &&
          now - circuit.lastFailureTime > this.config.resetTimeout * 5
        ) {
          console.info(`Force resetting circuit for model ${modelId}`);
          circuit.state = CircuitState.HALF_OPEN;
          circuit.successes = 0;
        }
      }
    }, 10000); // Every 10 seconds
  }

  /**
   * Create new circuit breaker
   */
  private createCircuitBreaker(): CircuitBreaker {
    return {
      state: CircuitState.CLOSED,
      failures: 0,
      successes: 0,
      lastFailureTime: 0,
      nextAttemptTime: 0,
      requestCount: 0
    };
  }

  private recordLatency(latencyMs: number): void {
    this.latencyHistory.push(latencyMs);

    if (this.latencyHistory.length > 1000) {
      this.latencyHistory.shift();
    }

    this.metrics.avgLatencyMs = this.calculateAverage(this.latencyHistory);
    this.metrics.p99LatencyMs = this.calculatePercentile(this.latencyHistory, 99);
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

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private initMetrics(): RouterMetrics {
    return {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      timeoutRequests: 0,
      circuitOpens: 0,
      avgLatencyMs: 0,
      p99LatencyMs: 0,
      activeRequests: 0,
      modelFailures: new Map(),
      timestamp: Date.now()
    };
  }

  /**
   * Export metrics as JSON
   */
  getMetrics(): RouterMetrics & { circuits: Record<string, CircuitState> } {
    const circuits: Record<string, CircuitState> = {};

    for (const [modelId, circuit] of this.circuits) {
      circuits[modelId] = circuit.state;
    }

    return {
      ...this.metrics,
      activeRequests: this.activeRequests.size,
      timestamp: Date.now(),
      circuits
    };
  }

  /**
   * Get circuit breaker status
   */
  getCircuitStatus(): Map<string, {
    state: CircuitState;
    failures: number;
    requestCount: number;
  }> {
    const status = new Map();

    for (const [modelId, circuit] of this.circuits) {
      status.set(modelId, {
        state: circuit.state,
        failures: circuit.failures,
        requestCount: circuit.requestCount
      });
    }

    return status;
  }

  /**
   * Force circuit state (emergency use)
   */
  forceCircuitState(modelId: string, state: CircuitState): void {
    const circuit = this.circuits.get(modelId);

    if (circuit) {
      console.warn(`FORCE: Setting circuit ${modelId} to ${state}`);
      circuit.state = state;
      circuit.failures = 0;
      circuit.successes = 0;

      this.emit('circuitForced', {
        modelId,
        state,
        timestamp: Date.now()
      });
    }
  }

  /**
   * Health check
   */
  healthCheck(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    // Check failure rate
    const failureRate = this.metrics.failedRequests /
      Math.max(this.metrics.totalRequests, 1);

    if (failureRate > 0.1) {
      issues.push(`High failure rate: ${(failureRate * 100).toFixed(1)}%`);
    }

    // Check timeout rate
    const timeoutRate = this.metrics.timeoutRequests /
      Math.max(this.metrics.totalRequests, 1);

    if (timeoutRate > 0.05) {
      issues.push(`High timeout rate: ${(timeoutRate * 100).toFixed(1)}%`);
    }

    // Check open circuits
    const openCircuits = Array.from(this.circuits.entries())
      .filter(([_, circuit]) => circuit.state === CircuitState.OPEN)
      .map(([modelId]) => modelId);

    if (openCircuits.length > 0) {
      issues.push(`Open circuits: ${openCircuits.join(', ')}`);
    }

    // Check P99 latency
    if (this.metrics.p99LatencyMs > 5000) {
      issues.push(`P99 latency above 5s: ${this.metrics.p99LatencyMs}ms`);
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }
}