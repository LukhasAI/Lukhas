# Benchmarking Runbook

This document provides instructions for managing performance benchmarks in the LUKHAS project.

## Running Benchmarks Locally

To run the benchmarks locally, you will need to install `pytest-benchmark`:

```bash
pip install pytest-benchmark
```

Then, run the benchmarks using `pytest`:

```bash
pytest benchmarks/ --benchmark-json=benchmark_results.json
```

This will create a `benchmark_results.json` file with the results of the benchmark run.

## Updating Baselines

To update a baseline, first run the benchmarks locally to generate a new `benchmark_results.json` file. Then, copy the relevant parts of the results to the appropriate baseline file in `benchmarks/baselines/`.

For example, to update the MATRIZ baseline, you would copy the MATRIZ-related results from `benchmark_results.json` to `benchmarks/baselines/matriz_baseline.json`.

## Interpreting Regression Reports

The nightly benchmark workflow will automatically create a GitHub issue if a performance regression of more than 10% is detected.

The issue body will contain a report detailing the regression. This report should be used to identify the commit that introduced the regression and to guide the debugging process.

## Performance Targets

### MATRIZ
-   **Cognitive Cycle Latency**: <250ms p95
-   **Throughput**: 50+ ops/sec
-   **Memory Usage**: <100MB

### Endocrine
-   **Update Latency**: <100ms p95
-   **WaveC Snapshot Creation Time**: <50ms
