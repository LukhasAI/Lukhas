# Benchmarks

This directory contains performance benchmarks for the LUKHAS project.

## Running Benchmarks

To run the benchmarks, you will need to install `pytest-benchmark`:

```bash
pip install pytest-benchmark
```

Then, run the benchmarks using `pytest`:

```bash
pytest benchmarks/
```

## Baselines

The `baselines/` directory contains the baseline performance data for the benchmarks. These are used to detect performance regressions.