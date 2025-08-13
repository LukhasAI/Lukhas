# LUKHAS Comprehensive Testing Guide

## Overview

This guide describes the comprehensive testing framework for the LUKHAS  system, covering unit tests, integration tests, end-to-end workflows, performance benchmarks, and security validation.

## 🧪 Test Architecture

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual components in isolation
   - Mock external dependencies
   - Fast execution
   - High code coverage

2. **Integration Tests** (`tests/integration/`)
   - Test interactions between components
   - Verify system integration points
   - Use real or stub services
   - Medium execution time

3. **End-to-End Tests** (`tests/e2e/`)
   - Test complete user workflows
   - Validate full system behavior
   - Realistic scenarios
   - Slower execution

4. **Security Tests** (`tests/security/`)
   - Validate encryption and authentication
   - Test security boundaries
   - Penetration testing scenarios
   - Critical for production

5. **API Tests** (`tests/api/`)
   - Test REST API endpoints
   - Validate request/response formats
   - Authentication flows
   - Client SDK testing

6. **Performance Tests**
   - Benchmark system performance
   - Load testing
   - Scalability validation
   - Resource usage monitoring

## 🚀 Quick Start

### Running All Tests

```bash
# Run all tests with coverage
python tests/run_tests.py all --coverage --report

# Run all tests excluding slow ones
python tests/run_tests.py all --exclude e2e performance

# Verbose output
python tests/run_tests.py all --verbose
```

### Running Specific Test Suites

```bash
# Run only unit tests
python tests/run_tests.py suite --suite unit

# Run integration tests with coverage
python tests/run_tests.py suite --suite integration --coverage

# Run security tests
python tests/run_tests.py suite --suite security --verbose
```

### Quick Validation

```bash
# Run smoke tests (quick validation)
python tests/run_tests.py smoke

# Run performance benchmarks
python tests/run_tests.py performance
```

## 📁 Test Structure

```
tests/
├── __init__.py
├── test_framework.py          # Base test classes and utilities
├── run_tests.py              # Test runner script
├── pytest.ini                # Pytest configuration
│
├── unit/                     # Unit tests
│   ├── test_consciousness.py
│   ├── test_memory.py
│   ├── test_guardian.py
│   └── test_symbolic.py
│
├── integration/              # Integration tests
│   └── test_core_integration.py
│
├── e2e/                      # End-to-end tests
│   └── test_e2e_workflows.py
│
├── security/                 # Security tests
│   └── test_enhanced_security.py
│
├── api/                      # API tests
│   └── test_enhanced_api.py
│
├── governance/               # Governance tests
│   ├── test_governance.py
│   ├── test_enhanced_governance.py
│   └── test_comprehensive_governance.py
│
└── results/                  # Test results and reports
    ├── coverage/            # Coverage reports
    └── *.json              # Test result files
```

## 🧪 Writing Tests

### Using the Test Framework

The test framework provides base classes for different test types:

```python
from tests.test_framework import LUKHASTestCase, IntegrationTestCase

class TestMyComponent(LUKHASTestCase):
    """Unit tests for my component"""
    
    @pytest.fixture
    async def my_component(self):
        """Create component instance"""
        component = MyComponent()
        await component.initialize()
        yield component
        await component.shutdown()
        
    @pytest.mark.asyncio
    async def test_basic_functionality(self, my_component):
        """Test basic component functionality"""
        result = await my_component.do_something()
        assert result is not None
```

### Test Utilities

```python
# Mock data generation
from tests.test_framework import MockDataGenerator

consciousness_state = MockDataGenerator.create_consciousness_state()
memory_entry = MockDataGenerator.create_memory_entry()
action_proposal = MockDataGenerator.create_action_proposal()

# Response validation
from tests.test_framework import TestValidator

TestValidator.validate_api_response(response)
TestValidator.validate_consciousness_response(response)
TestValidator.validate_memory_response(response)
TestValidator.validate_governance_response(response)
```

### Performance Testing

```python
from tests.test_framework import PerformanceTestCase

class TestPerformance(PerformanceTestCase):
    @pytest.mark.asyncio
    async def test_operation_speed(self, my_component, performance_metrics):
        """Test operation performance"""
        result = await self.measure_operation(
            lambda: my_component.expensive_operation(),
            performance_metrics
        )
        
        self.assert_performance(
            performance_metrics,
            max_response_time=0.5,  # 500ms
            max_memory_mb=100
        )
```

## 🎯 Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
async def test_unit_functionality():
    """Quick unit test"""
    pass

@pytest.mark.integration
@pytest.mark.slow
async def test_complex_integration():
    """Slower integration test"""
    pass

@pytest.mark.security
async def test_security_boundary():
    """Security-critical test"""
    pass
```

Run tests by marker:

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run security and unit tests
pytest -m "security or unit"
```

## 📊 Coverage Reports

### Generate Coverage

```bash
# Run with coverage
pytest --cov=core --cov=consciousness --cov-report=html

# View HTML report
open tests/results/coverage/index.html
```

### Coverage Goals

- **Unit Tests**: Aim for >90% coverage
- **Integration Tests**: Cover all integration points
- **Critical Paths**: 100% coverage for security, Guardian, and consciousness

## 🔍 Test Fixtures

### Common Fixtures

The framework provides common fixtures:

```python
@pytest.fixture
async def symbolic_engine():
    """Symbolic/GLYPH engine"""
    
@pytest.fixture
async def consciousness_system():
    """Consciousness system"""
    
@pytest.fixture
async def memory_system():
    """Memory system"""
    
@pytest.fixture
async def guardian_system():
    """Guardian/governance system"""
```

### Custom Fixtures

Create module-specific fixtures:

```python
@pytest.fixture
def mock_security(self):
    """Mock security system"""
    from core.security.security_integration import SecurityIntegration
    security = Mock(spec=SecurityIntegration)
    security.validate_request = AsyncMock(return_value=(True, None))
    return security
```

## 🐛 Debugging Tests

### Verbose Output

```bash
# Show print statements and full error traces
pytest -v -s tests/unit/test_consciousness.py

# Show local variables in errors
pytest -l tests/unit/test_memory.py
```

### Run Specific Tests

```bash
# Run single test
pytest tests/unit/test_guardian.py::TestGuardianCore::test_initialization

# Run tests matching pattern
pytest -k "test_memory" 

# Run failed tests from last run
pytest --lf
```

### Debug with PDB

```python
@pytest.mark.asyncio
async def test_debugging():
    """Test with debugger"""
    import pdb; pdb.set_trace()  # Breakpoint
    result = await complex_operation()
    assert result is not None
```

## 📈 Performance Benchmarks

### Built-in Benchmarks

The framework includes performance benchmarks:

```python
PERFORMANCE_BENCHMARKS = {
    'consciousness_query': {
        'max_response_time': 0.5,  # 500ms
        'max_memory_mb': 100
    },
    'memory_store': {
        'max_response_time': 0.1,  # 100ms
        'max_memory_mb': 50
    },
    # ... more benchmarks
}
```

### Custom Benchmarks

```python
@pytest.mark.benchmark
async def test_custom_performance(benchmark):
    """Custom performance test"""
    result = await benchmark(my_async_function, arg1, arg2)
    assert result is not None
```

## 🔐 Security Testing

### Security Test Scenarios

1. **Encryption Validation**
   - Verify no XOR usage
   - Test AES-256-GCM implementation
   - Key rotation testing

2. **Authentication Testing**
   - JWT validation
   - MFA flows
   - Session management

3. **Authorization Boundaries**
   - Role-based access
   - API key scopes
   - Resource isolation

4. **Attack Prevention**
   - Injection attacks
   - XSS prevention
   - Rate limiting

## 🤖 Continuous Integration

### GitHub Actions Configuration

```yaml
name: LUKHAS Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
          
      - name: Run tests
        run: |
          python tests/run_tests.py all --coverage --report
          
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📋 Test Data Sets

The framework includes test datasets:

```python
TEST_DATASETS = {
    'consciousness_queries': [
        "What is the nature of consciousness?",
        "How do you perceive reality?",
        # ... more queries
    ],
    'memory_content': [
        {"event": "System initialization", "importance": "high"},
        # ... more memories
    ],
    'action_proposals': [
        {"action": "respond_to_user", "content": "Hello"},
        # ... more actions
    ]
}
```

## 🏆 Best Practices

1. **Test Independence**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mock External Services**: Don't depend on external APIs
5. **Test Edge Cases**: Include boundary conditions
6. **Performance Awareness**: Mark slow tests
7. **Security First**: Always test security boundaries
8. **Documentation**: Document complex test scenarios

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Add project root to PYTHONPATH
   export PYTHONPATH=$PYTHONPATH:/path/to/lukhas
   ```

2. **Async Test Issues**
   ```python
   # Ensure proper async handling
   @pytest.mark.asyncio
   async def test_async():
       pass
   ```

3. **Fixture Scope Issues**
   ```python
   # Use appropriate scope
   @pytest.fixture(scope="module")
   async def expensive_fixture():
       pass
   ```

4. **Test Isolation**
   ```python
   # Reset state between tests
   @pytest.fixture(autouse=True)
   def reset_state():
       yield
       # Cleanup code
   ```

## 📞 Support

For testing issues:
- Check test logs in `tests/results/`
- Review coverage reports
- Use verbose mode for debugging
- Contact the LUKHAS development team