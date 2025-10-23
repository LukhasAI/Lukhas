/**
 * LUKHAS AI ΛiD Authentication System - Performance Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Setup file for performance tests - includes latency and load testing utilities
 */

// Performance testing configuration
const PERFORMANCE_TARGETS = {
  AUTH_P95_LATENCY_MS: 100,
  CONTEXT_P95_LATENCY_MS: 250,
  SCIM_DEPROVISIONING_SLO_MS: 15 * 60 * 1000, // 15 minutes
  API_THROUGHPUT_RPS: 1000,
  DATABASE_QUERY_MAX_MS: 50,
  JWT_GENERATION_MAX_MS: 10,
  PASSWORD_HASH_MAX_MS: 1000,
  SESSION_LOOKUP_MAX_MS: 25,
} as const;

// Performance measurement utilities
globalThis.performanceUtils = {
  // Measure function performance with statistics
  async measureFunction<T>(
    fn: () => Promise<T> | T,
    iterations: number = 100
  ): Promise<{
    results: T[];
    stats: {
      mean: number;
      median: number;
      p95: number;
      p99: number;
      min: number;
      max: number;
      stdDev: number;
    };
    durations: number[];
  }> {
    const results: T[] = [];
    const durations: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const start = process.hrtime.bigint();
      const result = await fn();
      const end = process.hrtime.bigint();
      
      results.push(result);
      durations.push(Number(end - start) / 1000000); // Convert to milliseconds
    }

    // Calculate statistics
    const sorted = [...durations].sort((a, b) => a - b);
    const mean = durations.reduce((sum, d) => sum + d, 0) / durations.length;
    const median = sorted[Math.floor(sorted.length / 2)];
    const p95 = sorted[Math.floor(sorted.length * 0.95)];
    const p99 = sorted[Math.floor(sorted.length * 0.99)];
    const min = Math.min(...durations);
    const max = Math.max(...durations);
    
    const variance = durations.reduce((sum, d) => sum + Math.pow(d - mean, 2), 0) / durations.length;
    const stdDev = Math.sqrt(variance);

    return {
      results,
      stats: { mean, median, p95, p99, min, max, stdDev },
      durations,
    };
  },

  // Simulate concurrent load
  async simulateLoad<T>(
    fn: () => Promise<T>,
    concurrency: number,
    duration: number
  ): Promise<{
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    rps: number;
    latencies: number[];
    errors: any[];
  }> {
    const startTime = Date.now();
    const endTime = startTime + duration;
    const latencies: number[] = [];
    const errors: any[] = [];
    let totalRequests = 0;
    let successfulRequests = 0;

    const workers = Array.from({ length: concurrency }, async () => {
      while (Date.now() < endTime) {
        const requestStart = process.hrtime.bigint();
        totalRequests++;
        
        try {
          await fn();
          successfulRequests++;
        } catch (error) {
          errors.push(error);
        }
        
        const requestEnd = process.hrtime.bigint();
        latencies.push(Number(requestEnd - requestStart) / 1000000);
      }
    });

    await Promise.all(workers);

    const actualDuration = Date.now() - startTime;
    const rps = (totalRequests / actualDuration) * 1000;

    return {
      totalRequests,
      successfulRequests,
      failedRequests: totalRequests - successfulRequests,
      rps,
      latencies,
      errors,
    };
  },

  // Memory usage measurement
  measureMemoryUsage(): { heapUsed: number; heapTotal: number; external: number; rss: number } {
    const usage = process.memoryUsage();
    return {
      heapUsed: usage.heapUsed / 1024 / 1024, // MB
      heapTotal: usage.heapTotal / 1024 / 1024, // MB
      external: usage.external / 1024 / 1024, // MB
      rss: usage.rss / 1024 / 1024, // MB
    };
  },

  // CPU usage measurement (approximate)
  async measureCPUUsage(duration: number = 1000): Promise<number> {
    const startUsage = process.cpuUsage();
    await new Promise(resolve => setTimeout(resolve, duration));
    const endUsage = process.cpuUsage(startUsage);
    
    // Calculate CPU percentage (rough approximation)
    const totalTime = endUsage.user + endUsage.system;
    const cpuPercent = (totalTime / (duration * 1000)) * 100;
    
    return cpuPercent;
  },

  // Database connection pool simulation
  createMockConnectionPool(maxConnections: number = 10) {
    let activeConnections = 0;
    const waitQueue: Array<(conn: any) => void> = [];

    return {
      async getConnection(): Promise<any> {
        return new Promise((resolve) => {
          if (activeConnections < maxConnections) {
            activeConnections++;
            resolve({ id: activeConnections, close: () => { activeConnections--; } });
          } else {
            waitQueue.push(resolve);
          }
        });
      },

      releaseConnection(conn: any) {
        conn.close();
        if (waitQueue.length > 0) {
          const nextResolve = waitQueue.shift()!;
          activeConnections++;
          nextResolve({ id: activeConnections, close: () => { activeConnections--; } });
        }
      },

      getStats() {
        return {
          activeConnections,
          queueLength: waitQueue.length,
          utilization: activeConnections / maxConnections,
        };
      },
    };
  },

  // Rate limiting simulation for performance testing
  createPerformanceRateLimiter(requestsPerSecond: number) {
    let lastRequestTime = 0;
    const interval = 1000 / requestsPerSecond;

    return {
      async waitForNext(): Promise<void> {
        const now = Date.now();
        const timeSinceLastRequest = now - lastRequestTime;
        
        if (timeSinceLastRequest < interval) {
          const delay = interval - timeSinceLastRequest;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
        
        lastRequestTime = Date.now();
      },
    };
  },

  // Generate performance test report
  generatePerformanceReport(testName: string, measurements: any) {
    const report = {
      testName,
      timestamp: new Date().toISOString(),
      measurements,
      targets: PERFORMANCE_TARGETS,
      summary: {
        passed: 0,
        failed: 0,
        warnings: 0,
      },
    };

    // Analyze against targets
    if (measurements.stats?.p95) {
      if (testName.includes('auth') && measurements.stats.p95 > PERFORMANCE_TARGETS.AUTH_P95_LATENCY_MS) {
        report.summary.failed++;
      } else if (testName.includes('context') && measurements.stats.p95 > PERFORMANCE_TARGETS.CONTEXT_P95_LATENCY_MS) {
        report.summary.failed++;
      } else {
        report.summary.passed++;
      }
    }

    return report;
  },

  // Validate performance against SLA
  validateSLA(metrics: any, slaConfig: any) {
    const violations = [];

    for (const [metric, target] of Object.entries(slaConfig)) {
      const actual = metrics[metric];
      if (actual && actual > target) {
        violations.push({
          metric,
          actual,
          target,
          violation: actual - target,
        });
      }
    }

    return {
      passed: violations.length === 0,
      violations,
    };
  },
};

// Mock external services for performance testing
globalThis.mockExternalServices = {
  // Mock slow database
  createSlowDatabase(latencyMs: number = 50) {
    return {
      async query(sql: string) {
        await new Promise(resolve => setTimeout(resolve, latencyMs));
        return { rows: [{ id: 1, name: 'test' }] };
      },
    };
  },

  // Mock slow external API
  createSlowAPI(latencyMs: number = 100) {
    return {
      async request(url: string) {
        await new Promise(resolve => setTimeout(resolve, latencyMs));
        return { status: 200, data: { success: true } };
      },
    };
  },

  // Mock email service with latency
  createSlowEmailService(latencyMs: number = 200) {
    return {
      async sendEmail(to: string, subject: string, body: string) {
        await new Promise(resolve => setTimeout(resolve, latencyMs));
        return { messageId: 'test-message-id' };
      },
    };
  },
};

// Performance test configuration
export const PERFORMANCE_CONFIG = {
  targets: PERFORMANCE_TARGETS,
  testDuration: {
    short: 10000,  // 10 seconds
    medium: 30000, // 30 seconds
    long: 60000,   // 1 minute
  },
  concurrencyLevels: [1, 5, 10, 25, 50, 100],
  loadPatterns: {
    constant: (rps: number) => rps,
    rampUp: (baseRPS: number, time: number, duration: number) => 
      baseRPS + (baseRPS * 2 * time / duration),
    spike: (baseRPS: number, time: number) => 
      time > 5000 && time < 7000 ? baseRPS * 5 : baseRPS,
  },
};

// Set longer timeout for performance tests
jest.setTimeout(120000);

// Memory leak detection
let initialMemory: any;

beforeEach(() => {
  // Force garbage collection if available
  if (global.gc) {
    global.gc();
  }
  initialMemory = globalThis.performanceUtils.measureMemoryUsage();
});

afterEach(() => {
  // Force garbage collection if available
  if (global.gc) {
    global.gc();
  }
  
  const finalMemory = globalThis.performanceUtils.measureMemoryUsage();
  const memoryLeak = finalMemory.heapUsed - initialMemory.heapUsed;
  
  // Warn about potential memory leaks (>10MB increase)
  if (memoryLeak > 10) {
    console.warn(`Potential memory leak detected: ${memoryLeak.toFixed(2)}MB increase`);
  }
});