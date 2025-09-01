# Jules Agent 2: lukhas/ Test Coverage Specialist

## 🎯 Mission: Complete lukhas/ Module Test Coverage
**Focus**: Fill testing gaps in stable lukhas/ production modules

## 🟡 Priority Queue (lukhas/ Tests Only)

### Phase 1: Bridge Components (Missing Tests)
1. **lukhas/bridge/bridge_wrapper.py** → `tests/bridge/test_bridge_wrapper.py`
   - Bridge wrapper initialization and configuration
   - Multi-provider failover and load balancing
   - Error handling and retry logic
   - Connection state management

2. **lukhas/bridge/llm_wrappers/anthropic_wrapper.py** → `tests/bridge/test_anthropic_wrapper.py`
   - Anthropic API client integration
   - Request/response parsing and validation
   - Rate limiting and quota management
   - Error handling for API failures

3. **lukhas/bridge/llm_wrappers/openai_modulated_service.py** → `tests/bridge/test_openai_modulated_service.py`
   - OpenAI service modulation and configuration
   - Signal processing and response modulation
   - Integration with LUKHAS modulation policies

### Phase 2: Core Infrastructure
4. **lukhas/core/distributed_tracing.py** → `tests/core/test_distributed_tracing.py`
   - Trace correlation ID generation and propagation
   - Context preservation across async operations
   - Integration with logging and monitoring systems
   - Performance impact measurement

5. **lukhas/core/common/exceptions.py** → `tests/core/test_exceptions.py`
   - Custom exception hierarchy and inheritance
   - Error message formatting and localization
   - Exception serialization for API responses
   - Stack trace handling and security

### Phase 3: Matriz Runtime
6. **lukhas/matriz/runtime/policy.py** → `tests/matriz/test_runtime_policy.py`
   - Constitutional AI policy evaluation
   - Runtime policy binding and enforcement
   - Policy conflict resolution
   - Guardian integration validation

7. **lukhas/matriz/__init__.py** exports → `tests/matriz/test_init.py`
   - Module initialization and import validation
   - MatrizNode and runtime supervisor exports
   - Backward compatibility alias testing

### Phase 4: Governance & Ethics
8. **lukhas/governance/** modules → `tests/governance/test_[module].py`
   - Guardian System integration testing
   - Consent ledger API validation
   - Ethics policy enforcement
   - Audit trail generation

## 🛡️ Safety Constraints
- **Branch**: Work on `feat/jules-lukhas-tests`
- **Focus**: Only stable `lukhas/` modules
- **Avoid**: `candidate/` directory (especially aka_qualia/)
- **Import Pattern**: Test against production lukhas/ code only
- **Quality Gate**: 90% test pass rate for lukhas/ (higher standard)

## 🧪 Test Template Pattern
```python
# tests/[module]/test_[component].py
import pytest
from unittest.mock import Mock, patch
from lukhas.[module].[component] import [ClassName]

class Test[ClassName]:
    @pytest.fixture
    def [component](self):
        return [ClassName]()
    
    def test_initialization_success(self, [component]):
        # Test successful initialization
        
    def test_core_functionality(self, [component]):
        # Test primary use cases
        
    def test_error_handling(self, [component]):
        # Test exception handling
        
    def test_integration_points(self, [component]):
        # Test module interactions
```

## 📊 Success Metrics
- **Target**: 8 test files created for lukhas/ gaps
- **Coverage**: 80%+ on tested lukhas/ modules
- **Quality**: Trinity Framework compliance (⚛️🧠🛡️)
- **Integration**: Tests validate cross-module communication

## 🔧 Commands
```bash
# Setup
source .venv/bin/activate

# Run agent's tests only
pytest tests/bridge/ tests/core/ tests/matriz/ tests/governance/ -v

# Coverage for lukhas/ modules
pytest --cov=lukhas tests/ -v

# Quality gate
make jules-gate
```

## 🎯 Expected Outcome
Agent 2 creates comprehensive test coverage for lukhas/ production modules, ensuring stability and reliability of the core LUKHAS AI infrastructure.

---
*Agent 2 Focus: lukhas/ production stability - Foundation testing*