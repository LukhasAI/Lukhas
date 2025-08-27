# LUKHAS AGI Enterprise Test Suite

## Overview

This test suite validates the enterprise-ready LUKHAS AGI system, focusing on:
- Core functionality
- Audit trail compliance
- Security validation
- Integration testing
- Performance benchmarks

## Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for system interactions
├── audit/            # Audit trail specific tests
├── test_audit_trail.py     # Core audit system tests
├── test_main_server.py     # Main orchestrator tests
├── requirements-test.txt   # Testing dependencies
└── README.md         # This file
```

## Running Tests

### Install Test Dependencies
```bash
pip install -r tests/requirements-test.txt
```

### Run All Tests (Professional Artifacts)
```bash
# From project root (timestamped artifacts under reports/test-runs/<ts>/)
python tests/run_tests.py all -v -c -r

# Artifacts generated per run:
# - reports/test-runs/<ts>/junit/junit-*.xml (CI-friendly)
# - reports/test-runs/<ts>/html/*.html (human-readable)
# - reports/test-runs/<ts>/json/*.json (machine-readable)
# - reports/test-runs/<ts>/coverage/ (HTML coverage)
# - reports/test-runs/<ts>/logs/*.log (test logs)
```

### Run Specific Test Categories
```bash
# Audit trail tests only
python -m pytest tests/test_audit_trail.py -v

# Main server tests
python -m pytest tests/test_main_server.py -v

# Integration tests
python -m pytest tests/integration/ -v
```

### Smoke and Performance
```bash
# Smoke
python tests/run_tests.py smoke -v

# Performance (benchmarks)
python tests/run_tests.py performance
```

## Test Categories

### 1. Audit Trail Tests (`test_audit_trail.py`)
- Event logging
- Consciousness transitions
- Decision chains
- Security events
- Compliance reporting
- Query functionality
- Analytics

### 2. Main Server Tests (`test_main_server.py`)
- Server initialization
- Consciousness processing
- Emergence detection
- Health checks
- Shutdown procedures
- Configuration loading

### 3. Integration Tests (Coming Soon)
- End-to-end workflows
- System interactions
- API testing
- Performance benchmarks

## Writing New Tests

### Test Template
```python
import pytest
from core.audit import get_audit_trail

@pytest.mark.asyncio
async def test_new_feature():
    """Test description"""
    # Arrange
    audit = get_audit_trail()

    # Act
    result = await audit.some_method()

    # Assert
    assert result is not None
```

### Best Practices
1. Use descriptive test names
2. Include docstrings
3. Follow Arrange-Act-Assert pattern
4. Mock external dependencies
5. Test both success and failure cases
6. Use fixtures for common setup

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pip install -r tests/requirements-test.txt
      - run: python tests/run_tests.py all -c -v -r
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-reports
          path: reports/test-runs/**
```

## Performance Testing

### Benchmark Example
```python
@pytest.mark.benchmark
def test_audit_performance(benchmark):
    """Benchmark audit event logging"""
    audit = get_audit_trail()

    def log_event():
        audit.log_event(
            AuditEventType.SYSTEM_START,
            "test",
            {"data": "test"}
        )

    benchmark(log_event)
```

## Security Testing

### Security Scan
```bash
# Run bandit security scan
bandit -r core/ main.py

# Check dependencies
safety check
```

## Test Data

### Using Test Fixtures
Test fixtures provide consistent test data:
- Mock consciousness states
- Sample memory data
- Test user profiles
- Simulated emergence events

### Test Database
Tests use temporary SQLite databases that are cleaned up automatically.

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure project root is in PYTHONPATH
   - Check import paths after directory reorganization

2. **Async Test Failures**
   - Use `pytest.mark.asyncio` decorator
   - Ensure proper async/await usage

3. **Mock Issues**
   - Patch at the correct import location
   - Use `asyncio.coroutine` for async mocks

## Coverage Goals

- Overall: 80%+
- Core systems: 90%+
- Audit trail: 95%+
- Security: 100%

## Next Steps

1. Restore more tests from archive
2. Add integration test suite
3. Create performance benchmarks
4. Set up CI/CD pipeline
5. Add mutation testing
