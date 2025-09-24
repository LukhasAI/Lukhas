# Memory Safety, Interleavings & Slow Tests

This document describes the combined test suite for memory safety, interleavings, and slow tests in LUKHAS.

## Overview

The combined test suite runs three categories of tests together:

- **`memory_safety`**: Property-based invariants for memory systems
- **`memory_interleavings`**: Concurrency and race condition testing
- **`slow`**: Long-running validation and stress tests

## Usage

### Command Line

Run all tests in these categories:

```bash
pytest -m "memory_safety or memory_interleavings or slow"
```

### Using the Script

For convenience, use the provided script:

```bash
./scripts/run_memory_slow_tests.sh
```

### CI Integration

The tests are automatically run in CI via the **Advanced Testing Suite** workflow:

- **Workflow**: `.github/workflows/advanced-testing.yml`
- **Job**: `memory-safety-interleavings`
- **Timeout**: 45 minutes
- **Environment**: `LUKHAS_LANE=candidate`, `LUKHAS_PERF=1`

## Test Categories

### Memory Safety (`memory_safety`)

Property-based tests that verify memory system invariants:

- Memory recall integrity under load (1K, 5K, 10K operations)
- Memory consistency invariants
- TopK correctness properties
- Memory safeguard edge cases

### Memory Interleavings (`memory_interleavings`)

Concurrency tests for memory systems:

- Concurrent recall fidelity
- Race condition detection
- Interleaving invariants under concurrent access

### Slow Tests (`slow`)

Long-running validation tests:

- Performance regression tests
- Stress testing under sustained load
- End-to-end system validation
- Production load simulation

## Configuration

### pytest.ini

The markers are defined in `pytest.ini`:

```ini
markers =
    memory_safety: property-based invariants for memory
    memory_interleavings: concurrency/interleavings invariants
    slow: long-running tests
```

### Environment Variables

For optimal testing, set:

```bash
export LUKHAS_LANE=candidate
export LUKHAS_PERF=1
export PYTHONPATH=.
```

## Expected Results

The test suite typically:

- Collects 25-30 tests from various modules
- Runs property-based tests with multiple parameter combinations
- Validates memory system behavior under various load conditions
- Takes 10-45 minutes depending on system performance

Tests may be skipped if optional dependencies are not available, which is expected behavior.