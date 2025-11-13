# Benchmark Results Directory

This directory stores pytest-benchmark results for historical comparison and regression detection.

## Structure

```
.benchmarks/
├── README.md (this file)
├── Linux-CPython-3.11-64bit/  # Per-platform results
│   ├── 0001_*.json            # Benchmark run 1
│   ├── 0002_*.json            # Benchmark run 2
│   └── ...
└── ...
```

## Usage

### Save Benchmark Results

```bash
# Auto-save with timestamp
pytest tests/performance/ --benchmark-autosave

# Save with custom name
pytest tests/performance/ --benchmark-save=baseline
```

### Compare Against Baseline

```bash
# Compare with most recent
pytest tests/performance/ --benchmark-compare

# Compare with specific run
pytest tests/performance/ --benchmark-compare=0001

# Compare with named baseline
pytest tests/performance/ --benchmark-compare=baseline

# Fail if regression > 20%
pytest tests/performance/ --benchmark-compare-fail=mean:20%
```

### Visualize Results

```bash
# Generate histogram
pytest tests/performance/ --benchmark-histogram

# List all saved benchmarks
pytest-benchmark list

# Compare multiple runs
pytest-benchmark compare 0001 0002 0003
```

## CI Integration

In CI, benchmark results can be:
1. Stored as artifacts
2. Published to GitHub Pages
3. Tracked in monitoring dashboard
4. Used for automated regression alerts

## Cleaning Up

```bash
# Remove old benchmarks (keep last 10)
ls -t .benchmarks/Linux-*/0*.json | tail -n +11 | xargs rm

# Remove all benchmarks
rm -rf .benchmarks/Linux-*/
```

## Gitignore

Benchmark results are gitignored by default to avoid repository bloat. Store important baselines separately or in CI artifacts.
