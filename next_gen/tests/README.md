# Next_Gen Tests

This directory contains the test suite for the next_gen module.

## Test Structure

### Test Files

- **`conftest.py`** - Test configuration and shared fixtures
- **`test_next_gen_unit.py`** - Unit tests for individual components
- **`test_next_gen_integration.py`** - Integration tests for module interactions

### Test Categories

- **Unit Tests** - Test individual functions and classes
- **Integration Tests** - Test module interactions and workflows
- **Performance Tests** - Benchmark performance characteristics

## Running Tests

### All Tests
```bash
pytest tests/
```

### Unit Tests Only
```bash
pytest tests/ -m unit
```

### Integration Tests Only
```bash
pytest tests/ -m integration
```

### With Coverage
```bash
pytest tests/ --cov=next_gen --cov-report=html
```

## Test Configuration

Test configuration is managed in `conftest.py`:
- Test fixtures and mocks
- Environment setup/teardown
- Shared test utilities

## Writing Tests

Follow LUKHAS testing standards:
1. Clear test names describing what is tested
2. Proper setup and teardown
3. Mock external dependencies
4. Test both success and failure cases

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Main branch commits
- Release builds

Target coverage: 85%+

---

*Part of LUKHAS T4/0.01% testing standards*
