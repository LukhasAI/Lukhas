# Quality Issue 13: Type Annotations for Critical Modules

## Priority: P1 - Code Quality
## Estimated Effort: 10 days
## Target: 65% type annotation coverage (up from 51%)

---

## 🎯 Objective

Add comprehensive type annotations to critical security and GDPR modules to improve code safety, maintainability, and enable static type checking.

## 📊 Current State

- **Type Annotation Coverage**: 51%
- **Target Coverage**: 65%
- **Docstring Coverage**: 71.5%
- **Gap**: +14 percentage points needed

## 🔍 Background

Type annotations improve:
- **Code Safety**: Catch bugs at development time
- **IDE Support**: Better autocomplete and refactoring
- **Documentation**: Self-documenting code
- **Maintainability**: Easier to understand and modify

Critical for security-sensitive code where type errors can lead to vulnerabilities.

## 📋 Deliverables

### 1. Focus Areas

Priority modules for type annotations:

**Security-Critical Modules**:
- All eval/exec replacement code
- Shell command execution wrappers
- SQL query builders
- Data serialization/deserialization
- Authentication and authorization

**GDPR API Modules**:
- `lukhas/api/v1/data_rights.py`
- `lukhas/compliance/data_retention.py`
- All data access/erasure/export functions

**Data Processing Pipelines**:
- Memory fold processing
- Consciousness state management
- User data aggregation

### 2. Type Annotation Standards

**Function Signatures**:
```python
# ❌ BEFORE (No types - 51% coverage)
def process_user_data(user_id, data, options=None):
    result = transform(data)
    return result

# ✅ AFTER (Full types - 65% target)
from typing import Dict, Any, Optional
from lukhas.types import UserID, ProcessedData

def process_user_data(
    user_id: UserID,
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> ProcessedData:
    """
    Process user data with full type safety.
    
    Args:
        user_id: Unique user identifier (ΛID)
        data: Raw input data dictionary
        options: Optional processing configuration
        
    Returns:
        Processed and validated data object
        
    Raises:
        ValueError: If data validation fails
        TypeError: If data types are incompatible
    """
    result: ProcessedData = transform(data)
    return result
```

**Class Attributes**:
```python
from typing import ClassVar, List
from dataclasses import dataclass

@dataclass
class DataRetentionPolicy:
    """Automated data retention configuration."""
    
    RETENTION_PERIODS: ClassVar[Dict[str, timedelta]] = {
        "memory_folds": timedelta(days=90),
        "interaction_logs": timedelta(days=180),
    }
    
    dry_run: bool = False
    log_results: bool = True
    cleanup_counts: Dict[str, int] = field(default_factory=dict)
```

### 3. Custom Types

**File**: `lukhas/types.py`

```python
from typing import NewType, TypedDict, Literal

# Semantic types for better type safety
UserID = NewType('UserID', str)
SessionID = NewType('SessionID', str)
MemoryFoldID = NewType('MemoryFoldID', str)

# Typed dictionaries for structured data
class UserData(TypedDict):
    user_id: UserID
    email: str
    created_at: str
    preferences: Dict[str, Any]

class ProcessedData(TypedDict):
    status: Literal["success", "partial", "failed"]
    data: Dict[str, Any]
    timestamp: str

# Union types for flexibility
DataFormat = Literal["json", "csv", "xml"]
RetentionPeriod = Literal["short", "medium", "long"]
```

### 4. Tools and Validation

**mypy Configuration** (`mypy.ini`):
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True

[mypy-lukhas.api.v1.*]
# Strict mode for API modules
strict = True

[mypy-lukhas.compliance.*]
# Strict mode for compliance modules
strict = True

[mypy-tests.*]
# Relaxed for tests
disallow_untyped_defs = False
```

**Run Type Checking**:
```bash
# Check critical modules with strict mode
mypy --strict lukhas/api/v1/data_rights.py
mypy --strict lukhas/compliance/
mypy --strict lukhas/security/

# Check overall coverage
mypy lukhas/ --html-report mypy_report/
```

**Auto-generate Annotations** (MonkeyType):
```bash
# Run code with MonkeyType to infer types
monkeytype run script.py

# Apply inferred types
monkeytype apply lukhas.module_name
```

### 5. CI/CD Integration

**Add to `.github/workflows/type-check.yml`**:
```yaml
name: Type Checking

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install mypy
          pip install -r requirements.txt
      
      - name: Run mypy strict on critical modules
        run: |
          mypy --strict lukhas/api/v1/
          mypy --strict lukhas/compliance/
          mypy --strict lukhas/security/
      
      - name: Run mypy on all code
        run: mypy lukhas/ --html-report mypy_report/
      
      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: mypy-report
          path: mypy_report/
```

### 6. Documentation

- [ ] Create `docs/development/TYPE_ANNOTATIONS_GUIDE.md`
- [ ] Document custom types
- [ ] Type annotation best practices
- [ ] mypy configuration guide

### 7. Testing

```python
def test_type_annotations_present():
    """Verify critical functions have type annotations."""
    import inspect
    from lukhas.api.v1.data_rights import get_user_data
    
    sig = inspect.signature(get_user_data)
    
    # Check all parameters have annotations
    for param in sig.parameters.values():
        assert param.annotation != inspect.Parameter.empty
    
    # Check return type annotated
    assert sig.return_annotation != inspect.Signature.empty
```

## ✅ Acceptance Criteria

- [ ] 65% type annotation coverage achieved (up from 51%)
- [ ] mypy strict mode passing on critical modules:
  - `lukhas/api/v1/data_rights.py`
  - `lukhas/compliance/`
  - `lukhas/security/`
- [ ] Custom types defined in `lukhas/types.py`
- [ ] Type stubs for third-party libraries
- [ ] CI/CD type checking enforced
- [ ] Documentation complete
- [ ] All security-critical code fully annotated

## 🏷️ Labels: `code-quality`, `type-safety`, `p1`, `technical-debt`

---

**Estimated Days**: 10 days | **Phase**: Security Phase 1 - Quality
