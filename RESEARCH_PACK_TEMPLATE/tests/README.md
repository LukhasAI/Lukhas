# Test Suite Documentation

## Overview
This directory contains test suites for validating the LUKHAS Innovation System's functionality, safety alignment, and performance characteristics.

## Test Categories

### Integration Tests
- `test_innovation_integration.py` - End-to-end pipeline validation
- Tests the flow: opportunity → hypothesis → exploration → synthesis → safety

### Alignment Tests  
- `test_alignment_stress.py` - Safety boundary testing
- Probes: bias resistance, injection attempts, value conflicts, ambiguity handling
- **Note**: Uses synthetic prompts only; no unsafe content generation

### Quick Baseline
- `test_innovation_quick_baseline.py` - Rapid validation (7 scenarios)
- Runtime: ~1 minute
- Use for: CI/CD, quick validation

### Full Research Suite
- `test_innovation_research_baseline.py` - Comprehensive testing (60 scenarios)
- Runtime: ~15 minutes
- Use for: thorough validation, benchmarking

## Running Tests

```bash
# Quick test
pytest test_innovation_quick_baseline.py

# Full suite
pytest . -v

# With coverage
pytest . --cov=../src --cov-report=html

# Specific category
pytest -m alignment
```

## Test Data
All test data is **synthetic** and located in `../data/`. No real-world sensitive data is used.

## Safety Protocol
1. All boundary tests use behavioral probing only
2. No generation of disallowed content
3. Focus on refusal/deferral/clarification behaviors
4. Response hashes logged for drift monitoring

## Output
Test results are written to `../test_results/` with timestamps and metadata for reproducibility.

## Adding New Tests
New tests must include:
- Safety tags (`@pytest.mark.safety`)
- Expected behavior documentation
- Synthetic data only
- Response hash capture