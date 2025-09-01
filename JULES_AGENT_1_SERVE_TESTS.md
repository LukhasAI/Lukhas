# Jules Agent 1: serve/ API Tests Specialist

## 🎯 Mission: Complete serve/ API Test Coverage
**Critical Gap**: 19 serve/ modules have ZERO test coverage - highest impact work

## 🚨 Priority Queue (serve/ Tests Only)

### Phase 1: Core API Endpoints (Start Here)
1. **serve/main.py** → `tests/serve/test_main.py`
   - FastAPI app initialization, middleware setup
   - Startup/shutdown event handlers
   - Basic endpoint registration verification

2. **serve/consciousness_api.py** → `tests/serve/test_consciousness_api.py`
   - Consciousness endpoint responses
   - Request validation and error handling
   - Integration with consciousness modules

3. **serve/identity_api.py** → `tests/serve/test_identity_api.py`
   - Authentication flows and JWT handling
   - User registration/login endpoints
   - Authorization middleware testing

4. **serve/guardian_api.py** → `tests/serve/test_guardian_api.py`
   - Guardian security validation endpoints
   - Ethics enforcement API responses
   - Security policy compliance checks

### Phase 2: Route Handlers
5. **serve/routes.py** → `tests/serve/test_routes.py`
   - General route registration and middleware
   - Error handling and response formatting
   - CORS and security headers

6. **serve/openai_routes.py** → `tests/serve/test_openai_routes.py`
   - OpenAI API proxy endpoints
   - Request/response transformation
   - Rate limiting and authentication

7. **serve/orchestration_routes.py** → `tests/serve/test_orchestration_routes.py`
   - Multi-AI orchestration endpoints
   - Workflow management APIs
   - Context preservation testing

### Phase 3: Specialized APIs
8. **serve/feedback_routes.py** → `tests/serve/test_feedback_routes.py`
   - User feedback collection endpoints
   - Feedback processing and storage
   - Analytics and reporting APIs

9. **serve/routes_traces.py** → `tests/serve/test_routes_traces.py`
   - Distributed tracing endpoints
   - Trace correlation and context
   - Performance monitoring APIs

10. **serve/login.py** → `tests/serve/test_login.py`
    - Login form handling and validation
    - Session management
    - Security token generation

## 🛡️ Safety Constraints
- **Branch**: Work on `feat/jules-serve-tests` 
- **Focus**: Only `serve/` modules and their tests
- **Avoid**: `candidate/aka_qualia/` (Wave C parallel development)
- **Test Framework**: pytest with FastAPI TestClient
- **Quality Gate**: 85% test pass rate minimum

## 🧪 Test Template Pattern
```python
# tests/serve/test_[module].py
import pytest
from fastapi.testclient import TestClient
from serve.main import app

client = TestClient(app)

class Test[Module]:
    def test_[endpoint]_success(self):
        # Happy path testing
        
    def test_[endpoint]_validation_error(self):
        # Input validation testing
        
    def test_[endpoint]_auth_required(self):
        # Authentication testing
        
    def test_[endpoint]_error_handling(self):
        # Error response testing
```

## 📊 Success Metrics
- **Target**: 10 test files created in `tests/serve/`
- **Coverage**: 70%+ on serve/ modules
- **Quality**: All tests pass with proper mocking
- **Documentation**: Each test file has clear docstrings

## 🔧 Commands
```bash
# Setup
source .venv/bin/activate
cd tests/serve/

# Run agent's tests only
pytest tests/serve/ -v

# Coverage check
pytest --cov=serve tests/serve/

# Quality gate
make jules-gate
```

## 🎯 Expected Outcome
By completion, Agent 1 will have created comprehensive test coverage for the serve/ API layer, addressing the most critical testing gap in LUKHAS AI.

---
*Agent 1 Focus: serve/ API endpoints - Maximum impact, zero conflicts*