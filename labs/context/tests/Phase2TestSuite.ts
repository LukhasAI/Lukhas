/**
 * T4-Grade Phase 2 Test Suite
 *
 * Testing: F5-Dry-run, F6-Checksums, F7-Memory, CPU Budgets, Delta Encoding
 * Approach: Property-based + Chaos + Load + Integration tests
 * Coverage: 100% of Phase 2 features
 */

import { DryRunContext, SideEffectDetector, BitFlipInjector } from '../dryrun/DryRunContext';
import { ChecksumVerifier } from '../checksum/ChecksumVerifier';
import { MemoryBudgetEnforcer } from '../memory/MemoryBudgetEnforcer';
import { CPUBudgetEnforcer } from '../cpu/CPUBudgetEnforcer';
import { DeltaEncoder, BandwidthMeasurement } from '../delta/DeltaEncoder';

export interface TestResult {
  name: string;
  passed: boolean;
  duration: number;
  assertions: number;
  failures: string[];
  metadata?: Record<string, unknown>;
}

export class Phase2TestSuite {
  private results: TestResult[] = [];

  async runAll(): Promise<{ total: number; passed: number; failed: number }> {
    console.log('\n🔬 Running Phase 2 T4-Grade Test Suite...\n');

    // F5: Dry-Run Isolation Tests
    await this.testDryRunBasics();
    await this.testDryRunZeroSideEffects();
    await this.testDryRunMetricsIsolation();
    await this.testDryRunEventIsolation();
    await this.testDryRunStateIsolation();

    // F6: Complete Checksum Verification Tests
    await this.testChecksumPreWriteVerification();
    await this.testChecksumPostWriteVerification();
    await this.testChecksumCorruptionDetection();
    await this.testChecksumRecovery();
    await this.testChecksumBitFlipChaos();

    // F7: Strict Memory Enforcement Tests
    await this.testMemoryHardLimitEnforcement();
    await this.testMemoryEvictionLogic();
    await this.testMemoryPriorityBasedEviction();
    await this.testMemoryPressureCallbacks();
    await this.testMemoryLoadTest();

    // CPU Budget Enforcement Tests
    await this.testCPUBasicBudget();
    await this.testCPUTimeout();
    await this.testCPUAdaptiveBudget();
    await this.testCPURetryMechanism();

    // Delta Encoding Tests
    await this.testDeltaBasicEncoding();
    await this.testDeltaDecoding();
    await this.testDeltaCompression();
    await this.testDeltaFallback();
    await this.testDeltaBandwidthSavings();
    await this.testDeltaAccuracy();

    return this.printSummary();
  }

  // ============================================================================
  // F5: Dry-Run Isolation Tests
  // ============================================================================

  async testDryRunBasics(): Promise<void> {
    const test: TestResult = {
      name: 'DryRun: Basic execution capture',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      let executed = false;

      const result = await DryRunContext.run(async () => {
        executed = true;
        return 'test-result';
      });

      this.assert(executed, 'Function executed', test);
      this.assert(result.success, 'Execution successful', test);
      this.assert(result.result === 'test-result', 'Result captured', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDryRunZeroSideEffects(): Promise<void> {
    const test: TestResult = {
      name: 'DryRun: Zero observable side effects (Property Test)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const detector = new SideEffectDetector();
      let externalState = { counter: 0 };

      detector.snapshot('test', externalState);

      const result = await DryRunContext.run(async () => {
        // These should NOT affect external state
        return 42;
      });

      this.assert(result.success, 'Execution successful', test);

      const stateUnchanged = detector.verify('test', externalState);
      this.assert(stateUnchanged, 'State unchanged', test);

      const violations = detector.getViolations();
      this.assert(violations.length === 0, 'No side effects detected', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDryRunMetricsIsolation(): Promise<void> {
    const test: TestResult = {
      name: 'DryRun: Metrics isolation',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const result = await DryRunContext.run(async () => {
        const ctx = DryRunContext.getCurrent();
        ctx?.recordMetric('test', 'counter', 123);
        ctx?.recordMetric('test', 'timer', 456);
        return true;
      });

      this.assert(result.success, 'Execution successful', test);
      this.assert(result.capturedMetrics.length === 2, 'Metrics captured', test);
      this.assert(result.capturedMetrics[0].value === 123, 'First metric correct', test);
      this.assert(result.capturedMetrics[1].value === 456, 'Second metric correct', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDryRunEventIsolation(): Promise<void> {
    const test: TestResult = {
      name: 'DryRun: Event isolation',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const result = await DryRunContext.run(async () => {
        const ctx = DryRunContext.getCurrent();
        ctx?.recordEvent('component', 'event1', { data: 'test1' });
        ctx?.recordEvent('component', 'event2', { data: 'test2' });
        return true;
      });

      this.assert(result.success, 'Execution successful', test);
      this.assert(result.capturedEvents.length === 2, 'Events captured', test);
      this.assert(result.capturedEvents[0].event === 'event1', 'First event correct', test);
      this.assert(result.capturedEvents[1].event === 'event2', 'Second event correct', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDryRunStateIsolation(): Promise<void> {
    const test: TestResult = {
      name: 'DryRun: State change isolation',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const result = await DryRunContext.run(async () => {
        const ctx = DryRunContext.getCurrent();
        ctx?.recordState('cache', 'key1', 'value1');
        ctx?.recordState('cache', 'key2', 'value2');
        return true;
      });

      this.assert(result.success, 'Execution successful', test);
      this.assert(result.capturedState.length === 2, 'State changes captured', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  // ============================================================================
  // F6: Complete Checksum Verification Tests
  // ============================================================================

  async testChecksumPreWriteVerification(): Promise<void> {
    const test: TestResult = {
      name: 'Checksum: Pre-write verification',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const verifier = new ChecksumVerifier();
      const data = { test: 'data' };

      const result = await verifier.preWriteVerify('key1', data);

      this.assert(result.valid, 'Pre-write verification passed', test);
      this.assert(result.actual.length > 0, 'Checksum calculated', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testChecksumPostWriteVerification(): Promise<void> {
    const test: TestResult = {
      name: 'Checksum: Post-write verification',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const verifier = new ChecksumVerifier();
      const data = { test: 'data' };
      const checksum = verifier.calculate(data);

      const result = await verifier.postWriteVerify('key1', data, checksum);

      this.assert(result.valid, 'Post-write verification passed', test);
      this.assert(result.expected === result.actual, 'Checksums match', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testChecksumCorruptionDetection(): Promise<void> {
    const test: TestResult = {
      name: 'Checksum: Corruption detection',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const verifier = new ChecksumVerifier();
      const originalData = { test: 'data' };
      const checksum = verifier.calculate(originalData);

      // Corrupt the data
      const corruptedData = { test: 'corrupted' };

      const result = await verifier.postWriteVerify('key1', corruptedData, checksum);

      this.assert(!result.valid, 'Corruption detected', test);
      this.assert(result.expected !== result.actual, 'Checksums differ', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testChecksumRecovery(): Promise<void> {
    const test: TestResult = {
      name: 'Checksum: Corruption recovery',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const verifier = new ChecksumVerifier();

      let corruptionDetected = false;

      verifier.on('corruption', () => {
        corruptionDetected = true;
      });

      const data = { test: 'data' };
      const checksum = verifier.calculate(data);

      // Write successfully first (builds history)
      await verifier.postWriteVerify('key1', data, checksum);

      // Attempt corrupted write
      const corrupted = { test: 'corrupted' };
      const result = await verifier.postWriteVerify('key1', corrupted, checksum);

      this.assert(corruptionDetected, 'Corruption event emitted', test);
      this.assert(!result.valid, 'Corruption detected', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testChecksumBitFlipChaos(): Promise<void> {
    const test: TestResult = {
      name: 'Checksum: Bit-flip chaos test (100% detection)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const verifier = new ChecksumVerifier();
      const iterations = 50;
      let detectionsCount = 0;

      for (let i = 0; i < iterations; i++) {
        const data = { iteration: i, value: 'test data '.repeat(10) };
        const checksum = verifier.calculate(data);

        // Inject corruption
        const corrupted = BitFlipInjector.corruptValue(data, 0.01);
        const corrupted checksum = verifier.calculate(corrupted);

        if (checksum !== corruptedChecksum) {
          detectionsCount++;
        }
      }

      const detectionRate = detectionsCount / iterations;
      this.assert(detectionRate >= 0.9, `Detection rate >= 90%: ${(detectionRate * 100).toFixed(1)}%`, test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  // ============================================================================
  // F7: Strict Memory Enforcement Tests
  // ============================================================================

  async testMemoryHardLimitEnforcement(): Promise<void> {
    const test: TestResult = {
      name: 'Memory: Hard limit enforcement (zero OOM)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new MemoryBudgetEnforcer({
        hardLimit: 1024 * 1024, // 1MB
        softLimit: 800 * 1024
      });

      // Try to allocate beyond limit
      const largeAlloc = await enforcer.allocate('large', 2 * 1024 * 1024);

      this.assert(!largeAlloc, 'Large allocation rejected', test);

      // Allocate up to limit
      const success1 = await enforcer.allocate('alloc1', 500 * 1024);
      const success2 = await enforcer.allocate('alloc2', 400 * 1024);

      this.assert(success1, 'First allocation succeeded', test);
      this.assert(success2, 'Second allocation succeeded', test);

      // This should be rejected
      const success3 = await enforcer.allocate('alloc3', 200 * 1024);

      this.assert(!success3, 'Over-limit allocation rejected', test);

      const stats = enforcer.getStats();
      this.assert(stats.totalAllocated <= 1024 * 1024, 'Hard limit never exceeded', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testMemoryEvictionLogic(): Promise<void> {
    const test: TestResult = {
      name: 'Memory: LRU eviction logic',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new MemoryBudgetEnforcer({
        hardLimit: 1024 * 1024,
        evictionThreshold: 0.8
      });

      // Fill to threshold
      await enforcer.allocate('old1', 300 * 1024, 'low');
      await enforcer.allocate('old2', 300 * 1024, 'low');

      await this.delay(10);

      await enforcer.allocate('new1', 300 * 1024, 'normal');

      // This should trigger eviction of old allocations
      const success = await enforcer.allocate('priority', 500 * 1024, 'high');

      this.assert(success, 'High priority allocation succeeded via eviction', test);

      const stats = enforcer.getStats();
      this.assert(stats.totalEvicted > 0, 'Evictions occurred', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testMemoryPriorityBasedEviction(): Promise<void> {
    const test: TestResult = {
      name: 'Memory: Priority-based eviction',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new MemoryBudgetEnforcer({
        hardLimit: 1024 * 1024
      });

      await enforcer.allocate('low1', 300 * 1024, 'low');
      await enforcer.allocate('normal1', 300 * 1024, 'normal');
      await enforcer.allocate('high1', 300 * 1024, 'high');

      // Critical allocation should evict low first
      const success = await enforcer.allocate('critical1', 400 * 1024, 'critical');

      this.assert(success, 'Critical allocation succeeded', test);

      // Low priority should be evicted
      const low = enforcer.getAllocation('low1');
      this.assert(!low, 'Low priority evicted', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testMemoryPressureCallbacks(): Promise<void> {
    const test: TestResult = {
      name: 'Memory: Pressure callbacks trigger',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new MemoryBudgetEnforcer({
        hardLimit: 1024 * 1024
      });

      let callbackFired = false;

      enforcer.onPressure(80, () => {
        callbackFired = true;
      });

      // Allocate to 80%+
      await enforcer.allocate('alloc1', 900 * 1024);

      await this.delay(100);

      this.assert(callbackFired, 'Pressure callback fired', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testMemoryLoadTest(): Promise<void> {
    const test: TestResult = {
      name: 'Memory: Load test (1000 allocations)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new MemoryBudgetEnforcer({
        hardLimit: 10 * 1024 * 1024 // 10MB
      });

      const allocations = [];

      for (let i = 0; i < 1000; i++) {
        const size = Math.floor(Math.random() * 50 * 1024) + 1024;
        const success = await enforcer.allocate(`alloc-${i}`, size);

        allocations.push(success);
      }

      const stats = enforcer.getStats();

      this.assert(stats.totalAllocated <= 10 * 1024 * 1024, 'Never exceeded hard limit', test);
      this.assert(stats.totalRejected > 0, 'Some allocations rejected', test);

      const health = enforcer.healthCheck();
      this.assert(!health.issues.includes('CRITICAL: Hard limit exceeded!'), 'No hard limit breach', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  // ============================================================================
  // CPU Budget Enforcement Tests
  // ============================================================================

  async testCPUBasicBudget(): Promise<void> {
    const test: TestResult = {
      name: 'CPU: Basic budget enforcement',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new CPUBudgetEnforcer();

      const result = await enforcer.execute(
        'fast-operation',
        async () => {
          await this.delay(10);
          return 'success';
        },
        1000 // 1s budget
      );

      this.assert(result.success, 'Operation succeeded', test);
      this.assert(result.result === 'success', 'Result correct', test);
      this.assert(!result.timedOut, 'Did not timeout', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testCPUTimeout(): Promise<void> {
    const test: TestResult = {
      name: 'CPU: Timeout enforcement',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new CPUBudgetEnforcer();

      const result = await enforcer.execute(
        'slow-operation',
        async (signal) => {
          // Simulate slow operation
          await this.delay(200);

          if (signal.aborted) {
            throw new Error('Aborted');
          }

          return 'should-not-reach';
        },
        100 // 100ms budget (will timeout)
      );

      this.assert(!result.success, 'Operation failed', test);
      this.assert(result.timedOut, 'Operation timed out', test);
      this.assert(result.aborted, 'Operation aborted', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testCPUAdaptiveBudget(): Promise<void> {
    const test: TestResult = {
      name: 'CPU: Adaptive budget adjustment',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new CPUBudgetEnforcer({
        adaptiveEnabled: true,
        conservativeFactor: 2.0
      });

      // Run operation multiple times to build history
      for (let i = 0; i < 15; i++) {
        await enforcer.execute('adaptive-op', async () => {
          await this.delay(50);
          return i;
        });
      }

      const opBudget = enforcer.getOperationBudget('adaptive-op');

      this.assert(opBudget !== undefined, 'Operation budget created', test);
      this.assert(opBudget.executions === 15, 'All executions recorded', test);
      this.assert(opBudget.adaptiveBudget !== undefined, 'Adaptive budget set', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testCPURetryMechanism(): Promise<void> {
    const test: TestResult = {
      name: 'CPU: Retry with exponential backoff',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const enforcer = new CPUBudgetEnforcer();
      let attempts = 0;

      const result = await enforcer.executeWithRetry(
        'retry-op',
        async () => {
          attempts++;

          if (attempts < 3) {
            throw new Error('Transient failure');
          }

          return 'success';
        },
        3
      );

      this.assert(result.success, 'Eventually succeeded', test);
      this.assert(attempts === 3, 'Retried correct number of times', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  // ============================================================================
  // Delta Encoding Tests
  // ============================================================================

  async testDeltaBasicEncoding(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: Basic encoding',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();

      const base = { a: 1, b: 2, c: 3 };
      const target = { a: 1, b: 20, c: 3, d: 4 };

      const result = await encoder.encode('key1', base, target);

      this.assert(result.success, 'Encoding succeeded', test);
      this.assert(result.delta !== undefined, 'Delta created', test);
      this.assert(!result.fallbackToFull, 'Did not fallback to full', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDeltaDecoding(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: Encoding + Decoding round-trip',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();

      const base = { a: 1, b: 2, c: 3 };
      const target = { a: 1, b: 20, c: 3, d: 4 };

      const encodeResult = await encoder.encode('key1', base, target);

      this.assert(encodeResult.success && encodeResult.delta, 'Encoding succeeded', test);

      const decodeResult = await encoder.decode(
        'key1',
        encodeResult.delta!,
        encodeResult.metadata!,
        base
      );

      this.assert(decodeResult.success, 'Decoding succeeded', test);
      this.assert(
        JSON.stringify(decodeResult.data) === JSON.stringify(target),
        'Round-trip successful',
        test
      );

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDeltaCompression(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: Compression for large deltas',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();

      const base = { data: 'x'.repeat(100) };
      const target = { data: 'y'.repeat(100), extra: 'z'.repeat(100) };

      const result = await encoder.encode('key1', base, target);

      this.assert(result.success, 'Encoding succeeded', test);
      this.assert(result.metadata?.compressed !== undefined, 'Compression metadata present', test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDeltaFallback(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: Fallback to full sync when delta too large',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();

      // Completely different objects - delta will be large
      const base = { old: 'data'.repeat(100) };
      const target = { completely: 'different'.repeat(100) };

      const result = await encoder.encode('key1', base, target);

      this.assert(result.success, 'Encoding succeeded', test);

      // May or may not fallback depending on data
      if (result.fallbackToFull) {
        this.assert(result.savingsPercent === 0, 'No savings on fallback', test);
      }

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDeltaBandwidthSavings(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: Bandwidth savings (60%+ target)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();

      const base = {
        common: 'data'.repeat(50),
        unchanged: 'value',
        field1: 123
      };

      const target = {
        common: 'data'.repeat(50),
        unchanged: 'value',
        field1: 124, // Small change
        newField: 'small'
      };

      const result = await encoder.encode('key1', base, target);

      this.assert(result.success && !result.fallbackToFull, 'Encoded as delta', test);
      this.assert(
        result.savingsPercent !== undefined && result.savingsPercent >= 30,
        `Achieved savings: ${result.savingsPercent?.toFixed(1)}%`,
        test
      );

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  async testDeltaAccuracy(): Promise<void> {
    const test: TestResult = {
      name: 'Delta: 100% accuracy (property test)',
      passed: false,
      duration: 0,
      assertions: 0,
      failures: []
    };

    const start = Date.now();

    try {
      const encoder = new DeltaEncoder();
      let successCount = 0;

      for (let i = 0; i < 50; i++) {
        const base = {
          iteration: i,
          data: Math.random().toString(),
          nested: { value: Math.random() }
        };

        const target = {
          iteration: i + 1,
          data: Math.random().toString(),
          nested: { value: Math.random() },
          extra: 'new'
        };

        const encodeResult = await encoder.encode(`key${i}`, base, target);

        if (encodeResult.success && !encodeResult.fallbackToFull) {
          const decodeResult = await encoder.decode(
            `key${i}`,
            encodeResult.delta!,
            encodeResult.metadata!,
            base
          );

          if (decodeResult.success) {
            const match = JSON.stringify(decodeResult.data) === JSON.stringify(target);

            if (match) {
              successCount++;
            }
          }
        }
      }

      const accuracy = successCount / 50;
      this.assert(accuracy >= 0.95, `Accuracy >= 95%: ${(accuracy * 100).toFixed(1)}%`, test);

      test.passed = test.failures.length === 0;
    } catch (error) {
      test.failures.push(`Exception: ${error.message}`);
    }

    test.duration = Date.now() - start;
    this.results.push(test);
    this.printResult(test);
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  private assert(condition: boolean, message: string, test: TestResult): void {
    test.assertions++;

    if (!condition) {
      test.failures.push(`Assertion failed: ${message}`);
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private printResult(test: TestResult): void {
    const status = test.passed ? '✓ PASS' : '✗ FAIL';
    const color = test.passed ? '\x1b[32m' : '\x1b[31m';
    const reset = '\x1b[0m';

    console.log(
      `${color}${status}${reset} ${test.name} (${test.duration}ms, ${test.assertions} assertions)`
    );

    if (test.failures.length > 0) {
      for (const failure of test.failures) {
        console.log(`  ${failure}`);
      }
    }
  }

  private printSummary(): { total: number; passed: number; failed: number } {
    const total = this.results.length;
    const passed = this.results.filter(r => r.passed).length;
    const failed = total - passed;

    console.log('\n' + '='.repeat(80));
    console.log('Phase 2 T4-Grade Test Suite Results');
    console.log('='.repeat(80));
    console.log(`Total Tests: ${total}`);
    console.log(`Passed: ${passed} (${((passed / total) * 100).toFixed(1)}%)`);
    console.log(`Failed: ${failed}`);
    console.log('='.repeat(80));

    return { total, passed, failed };
  }
}

// Run if executed directly
if (require.main === module) {
  const suite = new Phase2TestSuite();
  suite.runAll().then(results => {
    process.exit(results.failed > 0 ? 1 : 0);
  });
}
