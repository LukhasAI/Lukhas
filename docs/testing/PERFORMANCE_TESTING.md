# Performance Testing Guide

## Overview

Performance tests ensure LUKHAS core wiring components meet latency and throughput requirements. We use pytest-benchmark for detailed performance analysis and smoke tests for CI validation.

## Performance Budgets

| Component | Operation | Target (p95) | Budget |
|-----------|-----------|--------------|---------|
| **Dreams** | simulate_dream | < 250ms | Critical |
| **Dreams** | parallel_mesh | < 500ms | High |
| **GLYPHs** | encode_concept | < 100ms | Critical |
| **GLYPHs** | bind_glyph | < 150ms | High |
| **GLYPHs** | validate_glyph | < 10ms | Critical |
| **Drift** | update | < 50ms | Critical |
| **Drift** | EMA calculation | < 10ms | High |
| **API** | Routing overhead | < 10ms | Critical |

## Running Performance Tests

### Full Benchmark Suite

```bash
# Install pytest-benchmark if needed
pip install pytest-benchmark

# Run all benchmarks with detailed stats
pytest tests/performance/test_core_wiring_benchmarks.py -v --benchmark-only

# Run with autosave (creates .benchmarks/ directory)
pytest tests/performance/test_core_wiring_benchmarks.py --benchmark-autosave

# Compare with previous run
pytest tests/performance/test_core_wiring_benchmarks.py --benchmark-compare=0001

# Generate histogram
pytest tests/performance/test_core_wiring_benchmarks.py --benchmark-histogram
```

### Smoke Tests (Fast CI)

```bash
# Run smoke tests (< 10 seconds)
pytest tests/smoke/test_core_wiring_smoke.py -v

# Run with coverage
pytest tests/smoke/test_core_wiring_smoke.py --cov=lukhas --cov=lukhas_website
```

### Specific Component Tests

```bash
# Dreams only
pytest tests/performance/test_core_wiring_benchmarks.py::TestDreamsPerformance -v

# GLYPHs only
pytest tests/performance/test_core_wiring_benchmarks.py::TestGlyphsPerformance -v

# Drift only
pytest tests/performance/test_core_wiring_benchmarks.py::TestDriftPerformance -v
```

## Performance Test Structure

### Benchmark Tests (`tests/performance/`)

Detailed performance measurements with pytest-benchmark:

```python
def test_operation_latency(benchmark):
    """Operation should meet performance budget"""
    result = benchmark(
        function_to_test,
        arg1="value",
        arg2="value"
    )
    assert result["success"]
```

**Features**:
- Statistical analysis (mean, median, stddev)
- Outlier detection
- Historical comparison
- Histogram generation
- JSON export for CI

### Smoke Tests (`tests/smoke/`)

Fast validation tests for CI:

```python
def test_endpoint_reachable(client):
    """Endpoint is reachable and returns correct status"""
    response = client.get("/api/v1/dreams/")
    assert response.status_code == 200
```

**Features**:
- < 10 second total runtime
- Feature flag validation
- Import verification
- Basic request/response cycles

## CI Integration

### GitHub Actions Workflow

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/smoke/test_core_wiring_smoke.py -v

  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt pytest-benchmark
      - run: pytest tests/performance/ --benchmark-only --benchmark-json=output.json
      - uses: benchmark-action/github-action-benchmark@v1
        with:
          tool: 'pytest'
          output-file-path: output.json
```

## Performance Regression Detection

### Automated Checks

```bash
# Fail if performance degrades > 20%
pytest tests/performance/ --benchmark-compare=baseline --benchmark-compare-fail=mean:20%

# Fail if any test exceeds budget
pytest tests/performance/ --benchmark-max-time=0.250
```

### Manual Analysis

```bash
# Generate detailed report
pytest tests/performance/ --benchmark-only --benchmark-verbose

# Export to JSON for analysis
pytest tests/performance/ --benchmark-json=results.json

# Histogram visualization
pytest tests/performance/ --benchmark-histogram=histogram
```

## Load Testing (Optional)

For high-traffic scenarios, use load testing tools:

### Locust Example

```python
# locustfile.py
from locust import HttpUser, task, between

class CoreWiringUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def simulate_dream(self):
        self.client.post("/api/v1/dreams/simulate", json={
            "seed": "load_test",
            "context": {"load": "test"}
        })

    @task
    def encode_glyph(self):
        self.client.post("/api/v1/glyphs/encode", json={
            "concept": "load_test"
        })
```

Run with:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### K6 Example

```javascript
// k6-script.js
import http from 'k6/http';

export let options = {
  stages: [
    { duration: '30s', target: 20 },  // Ramp up
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down
  ],
};

export default function() {
  http.post('http://localhost:8000/api/v1/dreams/simulate', JSON.stringify({
    seed: 'k6_test',
    context: {}
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

Run with:
```bash
k6 run k6-script.js
```

## Chaos Engineering (Advanced)

Test resilience under adverse conditions:

```python
import pytest
from chaos import inject_latency, inject_failure

def test_dream_with_latency_injection():
    """Dream simulation handles injected latency gracefully"""
    with inject_latency(mean=100, stddev=20):
        result = simulate_dream("chaos_test")
        # Should still succeed, but slower
        assert result["success"]

def test_glyph_with_failure_injection():
    """GLYPH encoding handles transient failures"""
    with inject_failure(rate=0.1):  # 10% failure rate
        successes = 0
        for i in range(100):
            try:
                encode_concept(f"test_{i}")
                successes += 1
            except Exception:
                pass

        # Should have reasonable success rate
        assert successes >= 85  # Allow 15% failure
```

## Memory Profiling

### Check for Memory Leaks

```bash
# Install memory_profiler
pip install memory_profiler

# Run with memory profiling
python -m memory_profiler tests/performance/test_core_wiring_benchmarks.py

# Use memray for detailed analysis
pip install memray
memray run tests/performance/test_core_wiring_benchmarks.py
memray tree memray-results.bin
```

### Memory Bounds

```python
def test_drift_monitor_memory_bounded():
    """Drift monitor has bounded memory usage"""
    import tracemalloc
    tracemalloc.start()

    monitor = DriftMonitor()
    for i in range(10000):
        monitor.update([1.0, 0.0], [0.9, 0.1])

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Should not exceed 10MB
    assert peak < 10 * 1024 * 1024
```

## Troubleshooting

### Slow Tests

1. **Check mock setup**: Ensure external dependencies are mocked
2. **Reduce iterations**: Lower benchmark iterations for development
3. **Isolate tests**: Run specific test classes instead of full suite

### Flaky Tests

1. **Add warm-up rounds**: `benchmark.pedantic(func, rounds=10, warmup_rounds=2)`
2. **Increase tolerance**: Allow wider stddev for inherently variable operations
3. **Control environment**: Disable CPU throttling, close background apps

### CI Failures

1. **Check runner specs**: Ensure consistent CI runner performance
2. **Use relative thresholds**: Compare against baseline, not absolute values
3. **Skip on slow runners**: Use `@pytest.mark.skipif` for resource-constrained CI

## Best Practices

1. ✅ **Separate benchmarks from unit tests**: Use `--benchmark-only` flag
2. ✅ **Use consistent test data**: Deterministic seeds and inputs
3. ✅ **Mock external services**: Don't measure network/DB latency
4. ✅ **Warm up before measuring**: Use warm-up rounds
5. ✅ **Run on dedicated hardware**: Consistent results require consistent environment
6. ✅ **Track trends over time**: Store benchmark results for regression detection
7. ✅ **Document performance budgets**: Make targets explicit and visible

## Related Documentation

- [Testing Strategy](./TESTING_STRATEGY.md)
- [Core Wiring API](../api/CORE_WIRING_API.md)
- [Wrapper Modules](../wrappers/WRAPPER_MODULES.md)

## Support

For performance issues or questions:
- GitHub Issues: https://github.com/LukhasAI/Lukhas/issues
- Performance Dashboard: (link TBD)
