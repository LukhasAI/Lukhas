---
status: wip
type: documentation
---
# LUKHAS Dream — Phase NEXT (Ops-Ready Evaluation)

**Status**: Phase NEXT (T4 · 0.01%)
**Focus**: Production-ready evaluation science with stability, calibration, and safe rollout

## Overview

Phase NEXT upgrades the Dream System evaluation to production-grade science with:

- 🔬 **Multi-seed stability testing** - Deterministic behavior verification across randomness
- 📊 **Calibration & threshold sweeps** - Data-driven configuration optimization
- 🏷️ **Error taxonomy** - Systematic failure classification and diagnosis
- 🎲 **Synthetic case generation** - Adversarial testing and edge case coverage
- ⚙️ **Smart config chooser** - Environment-aware configuration recommendations
- 🚀 **Safe rollout system** - Canary/A-B testing with automatic safety monitoring

## Components

### 1. Stability Testing (`stability.py`)

Multi-seed testing to verify deterministic behavior:

```bash
# Run stability test with 6 seeds
python -m benchmarks.dream.stability

# Results show variance across seeds
# - Accuracy consistency
# - Selection determinism
# - Performance stability
```

**Key Features:**
- Fixed seed set: `[1, 7, 13, 42, 123, 999]`
- Measures accuracy variance, selection consistency
- Identifies non-deterministic behavior
- Generates stability metrics report

### 2. Calibration System (`calibration.py`)

Threshold optimization through grid search:

```bash
# Run comprehensive threshold sweep (729 configs)
python -m benchmarks.dream.calibration --sweep

# Generates optimal thresholds for:
# - alignment_threshold: 0.1-0.9
# - drift_threshold: 0.1-0.9
# - confidence_threshold: 0.1-0.9
```

**Output:**
- Production-recommended configuration
- Conservative fallback settings
- Performance predictions per metric
- Environment-specific optimization

### 3. Error Taxonomy (`taxonomy.py`)

Systematic error classification and diagnosis:

```bash
# Analyze benchmark results for error patterns
python -m benchmarks.dream.taxonomy results.jsonl taxonomy_report.json
```

**Error Categories:**
- `NO_SNAPSHOTS` - Empty snapshot lists (Critical)
- `ALL_FILTERED` - Staleness filtering removes all candidates (High)
- `LOW_ALIGNMENT` - Poor emotional matching (Medium)
- `HIGH_DRIFT` - Temporal instability (Medium)
- `TIMEOUT` - Processing time exceeded (High)
- `DETERMINISM_VIOLATION` - Non-reproducible results (Critical)

### 4. Synthetic Case Generator (`synthetic.py`)

Adversarial test case generation:

```bash
# Generate 50 synthetic test cases
python -m benchmarks.dream.synthetic 50 42 synthetic_corpus.json
```

**Case Types:**
- **Easy** (40%) - Clear winner scenarios
- **Medium** (30%) - Close competitor decisions
- **Hard** (20%) - Temporal complexity tradeoffs
- **Adversarial** (10%) - Edge cases and stress tests

**Adversarial Scenarios:**
- Extreme values (0.0/1.0 only)
- All-zero emotions
- All-max emotions
- Identical emotions (tiebreaking)
- Sparse emotion vectors

### 5. Config Chooser (`chooser.py`)

Intelligent configuration selection:

```bash
# Get recommendation for production environment
python -m benchmarks.dream.chooser benchmark_results.json production accuracy

# Available environments: development, staging, production, high_load, low_latency
# Available priorities: accuracy, latency, coverage, stability, balanced
```

**Predefined Profiles:**
- `dev_fast` - Development optimized for iteration speed
- `staging_balanced` - Staging with balanced performance
- `prod_accuracy` - Production optimized for accuracy
- `prod_latency` - Production optimized for low latency
- `high_load` - High-load environment with aggressive optimization

### 6. Rollout System (`rollout.py`)

Safe deployment with monitoring:

```bash
# Create canary rollout plan
python -m benchmarks.dream.rollout create config.json canary

# Execute rollout with safety monitoring
python -m benchmarks.dream.rollout execute plan_12345

# Monitor rollout status
python -m benchmarks.dream.rollout status plan_12345

# Emergency rollback
python -m benchmarks.dream.rollout rollback plan_12345
```

**Rollout Strategies:**
- `immediate` - Direct 100% deployment
- `canary` - 5% → 100% with monitoring
- `gradual` - 10% → 25% → 50% → 100%
- `a_b_test` - 50/50 split testing
- `blue_green` - Environment switching

**Safety Features:**
- Automatic threshold monitoring
- Configurable rollback triggers
- Violation count tracking
- Emergency rollback capability

### 7. CI Integration (`ci.py`)

Automated testing pipeline:

```bash
# Run complete CI suite
python -m benchmarks.dream.ci
```

**CI Tests:**
- Benchmark validation (accuracy ≥ 0.7)
- Configuration validation
- Synthetic generation test
- Taxonomy analysis test
- Determinism verification

## Environment Variables

**Phase NEXT specific:**
```bash
LUKHAS_CI_MODE=1                    # Enable CI optimizations
LUKHAS_ALIGNMENT_THRESHOLD=0.5      # Override alignment threshold
LUKHAS_DRIFT_THRESHOLD=0.3          # Override drift threshold
LUKHAS_CONFIDENCE_THRESHOLD=0.7     # Override confidence threshold
```

**Inherited from previous phases:**
```bash
LUKHAS_BENCH_SEED=42               # Deterministic randomness
LUKHAS_MAX_SNAPSHOT_AGE_SEC=0      # Staleness filtering (0=disabled)
LUKHAS_SNAPSHOT_HALF_LIFE_SEC=0    # Temporal weighting (0=disabled)
LUKHAS_HYBRID_ALPHA=0.5            # Blend strategy weight
```

## Performance Targets

**CI Thresholds:**
- Accuracy ≥ 0.70
- P95 Latency ≤ 0.10ms
- Determinism = 1.0 (exact reproducibility)
- Coverage ≥ 0.70

**Production Targets:**
- Accuracy ≥ 0.85
- P95 Latency ≤ 0.05ms
- Coverage ≥ 0.90
- Stability = 1.0

## Integration Example

Complete evaluation workflow:

```bash
# 1. Generate synthetic test cases
python -m benchmarks.dream.synthetic 100 42 adversarial_corpus.json

# 2. Run stability analysis
python -m benchmarks.dream.stability

# 3. Calibrate thresholds
python -m benchmarks.dream.calibration --sweep

# 4. Get configuration recommendation
python -m benchmarks.dream.chooser calibration_results/threshold_sweep.json production accuracy

# 5. Create rollout plan
echo '{"strategy": "overlap", "use_objective": "1", "alignment_threshold": 0.5}' > optimal_config.json
python -m benchmarks.dream.rollout create optimal_config.json canary

# 6. Execute safe rollout
python -m benchmarks.dream.rollout execute rollout_1234567890_abc12345
```

## Files Structure

```
benchmarks/dream/
├── stability.py          # Multi-seed stability testing
├── calibration.py        # Threshold optimization
├── taxonomy.py           # Error classification
├── synthetic.py          # Adversarial case generation
├── chooser.py            # Smart configuration selection
├── rollout.py            # Safe deployment system
├── ci.py                 # CI integration
├── README_PHASE_NEXT.md  # This documentation
└── [results directories]
    ├── stability_results/
    ├── calibration_results/
    ├── ci_results/
    └── rollout_state.json
```

## Safety & Compliance

**T4 Compliance:**
- ✅ Deterministic across machines and time
- ✅ Privacy-preserving (no sensitive data exposure)
- ✅ Reproducible results with fixed seeds
- ✅ Graceful degradation under failures

**0.01% Engineering:**
- ✅ Minimal assumptions about environment
- ✅ Robust error handling and recovery
- ✅ Safe defaults for all configurations
- ✅ Comprehensive monitoring and alerting

## Next Steps

Phase NEXT provides production-ready evaluation infrastructure. Future enhancements:

1. **Real-time monitoring** - Live production metrics integration
2. **Adaptive thresholds** - Dynamic threshold adjustment based on traffic
3. **ML-driven optimization** - Automatic configuration tuning
4. **Multi-region rollouts** - Geographic deployment strategies
5. **Performance profiling** - Detailed latency/memory analysis

---

**Generated by**: LUKHAS Dream Phase NEXT
**Version**: T4 · 0.01%
**Compliance**: Deterministic, Privacy-Preserving, Production-Ready