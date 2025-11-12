# Performance Benchmarks

This document outlines the performance benchmarks for the LUKHAS system, which are designed to ensure that the system meets its performance targets for key operations.

## Running the Benchmarks

The performance benchmarks are built using `pytest-benchmark` and can be run using the following command:

```bash
pytest tests/benchmarks/performance_suite.py
```

## Benchmark Suite

The benchmark suite is located in `tests/benchmarks/performance_suite.py` and includes the following benchmarks:

### Memory Recall Latency

- **Target:** < 100ms
- **Description:** Measures the time it takes for the `MemoryOrchestrator` to process a query and return a result. This benchmark is parameterized to test different query lengths.

### Pipeline P95 Latency

- **Target:** < 250ms
- **Description:** Measures the end-to-end processing time for a query through the `AsyncOrchestrator` pipeline. This benchmark tests both sequential and parallel execution modes with a varying number of stages.

### Cascade Prevention Efficiency

- **Target:** 99.7% detection rate with minimal overhead
- **Description:** Measures the latency of the oscillation detection mechanism within the `AsyncOrchestrator`'s meta controller. This ensures that this critical safety feature adds negligible overhead to the pipeline's execution time.
