# Claude Code Web Prompts for Security & GDPR Compliance Issues

**Generated**: 2025-11-15
**Purpose**: Comprehensive prompts for Claude Code Web to implement all 13 security and GDPR compliance issues
**Repository**: https://github.com/LukhasAI/Lukhas

---

## Overview

This document contains ready-to-use prompts for Claude Code Web to implement all 13 security and GDPR compliance issues identified in Phase 1 of the LUKHAS security remediation plan.

### Issue Summary

| # | Issue | Priority | Effort | GitHub Issue |
|---|-------|----------|--------|--------------|
| 1 | Eliminate All eval() Calls | P0 CRITICAL | 12 days | [#1582](https://github.com/LukhasAI/Lukhas/issues/1582) |
| 2 | Eliminate All exec() Calls | P0 CRITICAL | 10 days | [#1583](https://github.com/LukhasAI/Lukhas/issues/1583) |
| 3 | Fix Shell Injection | P1 HIGH | 20 days | [#1584](https://github.com/LukhasAI/Lukhas/issues/1584) |
| 4 | Fix Pickle Deserialization | P1 HIGH | 8 days | [#1585](https://github.com/LukhasAI/Lukhas/issues/1585) |
| 5 | Fix SQL Injection | P1 HIGH | 10 days | [#1586](https://github.com/LukhasAI/Lukhas/issues/1586) |
| 6 | Fix YAML Unsafe Loading | P1 HIGH | 2 days | [#1587](https://github.com/LukhasAI/Lukhas/issues/1587) |
| 7 | Right to Access API (GDPR Art. 15) | P0 | 15 days | [#1588](https://github.com/LukhasAI/Lukhas/issues/1588) |
| 8 | Right to Erasure API (GDPR Art. 17) | P0 | 15 days | [#1589](https://github.com/LukhasAI/Lukhas/issues/1589) |
| 9 | Right to Data Portability API (GDPR Art. 20) | P0 | 10 days | [#1590](https://github.com/LukhasAI/Lukhas/issues/1590) |
| 10 | Right to Rectification API (GDPR Art. 16) | P0 | 10 days | [#1591](https://github.com/LukhasAI/Lukhas/issues/1591) |
| 11 | Automated Data Retention Policy | P0 | 10 days | [#1592](https://github.com/LukhasAI/Lukhas/issues/1592) |
| 12 | Privacy Policy Documentation | P0 | 10 days | [#1593](https://github.com/LukhasAI/Lukhas/issues/1593) |
| 13 | Type Annotations for Critical Modules | P1 | 10 days | [#1594](https://github.com/LukhasAI/Lukhas/issues/1594) |

**Total Estimated Effort**: 142 days
**Target Outcome**: 
- Security: 0 CRITICAL patterns, <150 HIGH patterns (75% reduction)
- GDPR: 75% compliance (up from 58%)
- Quality: 65% type annotations (up from 51%)

---

## Prompt 1: Eliminate All eval() Calls (CRITICAL)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1582

**Prompt for Claude Code Web**:

```
**Task**: Eliminate All eval() Calls from LUKHAS Codebase (CRITICAL Security Issue)

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1582
**Priority**: P0 - CRITICAL
**Estimated Time**: 12 days

## Objective

Eliminate all 47 eval() calls to prevent code injection vulnerabilities. The eval() function is a CRITICAL security risk that can execute arbitrary Python code from strings.

## Current State

- **Total eval() occurrences**: 47
- **Risk Level**: CRITICAL
- **Data Source**: `reports/analysis/high_risk_patterns.json`

## Tasks

### 1. Extract All eval() Locations

```bash
jq '.patterns.eval_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > /tmp/eval_locations.json
```

### 2. Categorize Each Occurrence

For each eval() call, determine:
- Is it in test code? → Can be removed or mocked
- Is it in research/demo code? → Can be mocked or use fixtures
- Is it in production code? → Requires safe replacement

### 3. Implement Safe Replacements

**For Literal Evaluation**:
```python
# SAFE REPLACEMENT
import ast
from typing import Any

def safe_evaluate_literal(expr: str) -> Any:
    """Safely evaluate Python literal expressions only."""
    try:
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid literal expression: {e}")
```

**For Attribute Access**:
```python
# Use getattr() instead of eval()
value = getattr(obj, attribute_name, None)
```

**For Test Code**:
```python
# Remove entirely or replace with expected output
expected_result = get_expected_test_result()
```

### 4. Security Testing

For each replacement, add security tests:
```python
def test_safe_literal_eval_rejects_code_injection():
    """Ensure safe_evaluate_literal rejects code execution attempts."""
    malicious_inputs = [
        "__import__('os').system('rm -rf /')",
        "exec('malicious code')",
        "compile('bad code', '', 'exec')",
    ]
    
    for malicious in malicious_inputs:
        with pytest.raises(ValueError):
            safe_evaluate_literal(malicious)
```

### 5. Documentation

Create `docs/security/EVAL_ELIMINATION_REPORT.md` documenting:
- Complete list of all 47 occurrences
- Categorization (test/research/production)
- Remediation strategy for each
- Security test results

## Acceptance Criteria

- [ ] All 47 eval() calls eliminated or secured
- [ ] Each replacement has unit tests and security tests
- [ ] Zero eval() calls in production code paths
- [ ] Complete documentation
- [ ] Security scan shows 0 eval() patterns
- [ ] All tests pass

## Commands to Validate

```bash
# Search for remaining eval() calls
rg "eval\(" --type py

# Run security scan
python3 scripts/security_scan.py | jq '.patterns.eval_usage'

# Run tests
pytest tests/security/ -v
```

**Success**: Security scan shows 0 CRITICAL eval() patterns, all tests pass.
```

---

## Prompt 2: Eliminate All exec() Calls (CRITICAL)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1583

**Prompt for Claude Code Web**:

```
**Task**: Eliminate All exec() Calls from LUKHAS Codebase (CRITICAL Security Issue)

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1583
**Priority**: P0 - CRITICAL
**Estimated Time**: 10 days

## Objective

Eliminate all 28 exec() calls to prevent arbitrary code execution. Like eval(), exec() poses a CRITICAL security risk.

## Current State

- **Total exec() occurrences**: 28
- **Risk Level**: CRITICAL
- **Data Source**: `reports/analysis/high_risk_patterns.json`

## Safe Replacement Strategies

### For Plugin Systems

```python
import importlib.util
from pathlib import Path
from typing import Any, Optional

def load_plugin_safely(plugin_path: Path, plugin_name: str) -> Optional[Any]:
    """Load plugin from controlled directory only."""
    allowed_dir = Path("/path/to/plugins").resolve()
    if not plugin_path.resolve().is_relative_to(allowed_dir):
        raise ValueError(f"Plugin must be in {allowed_dir}")
    
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
```

### For Dynamic Class Creation

```python
def create_class(name: str, bases: tuple, attrs: dict):
    """Safe dynamic class creation using type()."""
    return type(name, bases, attrs)
```

### For Code Generation

```python
from jinja2 import Template

template = Template(code_template)
generated_code = template.render(**context)
# Save to file and import normally
```

## Acceptance Criteria

- [ ] All 28 exec() calls eliminated
- [ ] Whitelist-based plugin system if needed
- [ ] Security audit of all dynamic code paths
- [ ] Complete documentation
- [ ] All tests pass

**Success**: Security scan shows 0 CRITICAL exec() patterns.
```

---

## Prompt 3: Fix Shell Injection Vulnerabilities (HIGH)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1584

**Prompt for Claude Code Web**:

```
**Task**: Fix All Shell Injection Vulnerabilities

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1584
**Priority**: P1 - HIGH
**Estimated Time**: 20 days

## Objective

Fix all 66 shell injection vulnerabilities from subprocess and os.system calls.

## Current State

- **subprocess with shell=True**: 27 occurrences
- **os.system calls**: 39 occurrences
- **Total**: 66 shell injection risks

## Safe Replacements

### Standard Fix (subprocess without shell)

```python
# SAFE - No shell injection
import subprocess
from pathlib import Path
from typing import List

def safe_list_directory(user_path: str) -> List[str]:
    """Safely list directory without shell injection."""
    path = Path(user_path).resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid directory")
    
    # Use array form - no shell interpretation
    result = subprocess.run(
        ["ls", str(path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )
    return result.stdout.splitlines()
```

### Replace os.system

```python
# Replace os.system with subprocess.run array form
subprocess.run(
    ["rm", str(path)],
    check=True,
    timeout=5
)
```

## Security Testing

```python
def test_shell_injection_prevented():
    """Ensure shell injection is prevented."""
    malicious_inputs = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "&& whoami",
    ]
    
    for malicious in malicious_inputs:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            safe_list_directory(malicious)
```

## Acceptance Criteria

- [ ] All 66 shell injection patterns fixed
- [ ] All subprocess calls use array form (no shell=True)
- [ ] All os.system replaced with subprocess
- [ ] Security tests pass

**Success**: Security scan shows <150 HIGH patterns (66 eliminated).
```

---

## Prompt 4: Fix Pickle Deserialization Vulnerabilities (HIGH)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1585

**Prompt for Claude Code Web**:

```
**Task**: Fix All Pickle Deserialization Vulnerabilities

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1585
**Priority**: P1 - HIGH
**Estimated Time**: 8 days

## Objective

Replace all 12 insecure pickle.loads() calls with safe alternatives.

## Preferred Fix: Use JSON

```python
import json
from typing import Any, Dict

def safe_deserialize(data_bytes: bytes) -> Dict[str, Any]:
    """Use JSON instead of pickle for untrusted data."""
    try:
        return json.loads(data_bytes.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid data format: {e}")
```

## Alternative: HMAC-Signed Pickle

```python
import pickle
import hmac
import hashlib

SECRET_KEY = b'your-secret-key-from-env'

def secure_pickle_loads(data: bytes) -> Any:
    """Deserialize with HMAC verification."""
    signature = data[:32]
    pickled = data[32:]
    
    expected_sig = hmac.new(SECRET_KEY, pickled, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    
    return pickle.loads(pickled)
```

## Acceptance Criteria

- [ ] All 12 pickle.loads() replaced with JSON or HMAC-signed pickle
- [ ] No untrusted pickle deserialization
- [ ] Security tests pass

**Success**: All pickle deserialization is secure.
```

---

## Prompt 5: Fix SQL Injection Vulnerabilities (HIGH)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1586

**Prompt for Claude Code Web**:

```
**Task**: Fix All SQL Injection Vulnerabilities

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1586
**Priority**: P1 - HIGH
**Estimated Time**: 10 days

## Objective

Replace all 25 SQL query concatenations with parameterized queries.

## Safe Parameterized Queries

```python
from typing import Any, Dict, List

def safe_query_user(user_id: int) -> List[Dict[str, Any]]:
    """Safely query user with parameterized statement."""
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)  # Parameterized - prevents injection
    )
    return cursor.fetchall()
```

## Prefer ORM

```python
from sqlalchemy.orm import Session

def safe_query_user_orm(session: Session, user_id: int):
    """Query using ORM - automatically safe."""
    return session.query(User).filter(User.id == user_id).first()
```

## Acceptance Criteria

- [ ] All 25 SQL concatenations replaced
- [ ] No string formatting in SQL queries
- [ ] Prefer ORM where possible
- [ ] Security tests pass

**Success**: No SQL concatenation patterns remain.
```

---

## Prompt 6: Fix YAML Unsafe Loading (HIGH)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1587

**Prompt for Claude Code Web**:

```
**Task**: Fix YAML Unsafe Loading Vulnerabilities

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1587
**Priority**: P1 - HIGH
**Estimated Time**: 2 days

## Objective

Replace all 3 yaml.unsafe_load() calls with yaml.safe_load().

## Simple Fix

```python
import yaml
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """Safely load YAML configuration."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config
```

## Security Testing

```python
def test_yaml_code_execution_prevented():
    """Ensure YAML code execution attempts fail."""
    malicious_yaml = """
    !!python/object/apply:os.system
    args: ['rm -rf /']
    """
    
    with pytest.raises((yaml.YAMLError, AttributeError)):
        yaml.safe_load(malicious_yaml)
```

## Acceptance Criteria

- [ ] All 3 yaml.unsafe_load() replaced
- [ ] All YAML files scanned for dangerous tags
- [ ] Security tests pass

**Success**: All YAML loading is safe.
```

---

## Prompt 7: Implement Right to Access API (GDPR Art. 15)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1588

**Prompt for Claude Code Web**:

```
**Task**: Implement GDPR Right to Access API

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1588
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 15 days

## Objective

Implement API allowing users to retrieve all personal data (GDPR Article 15).

## API Endpoint

File: `lukhas/api/v1/data_rights.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/v1/data-rights", tags=["GDPR"])

@router.get("/users/{user_id}/data")
async def get_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Right to Access - GDPR Article 15."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only access own data")
    
    return {
        "requested_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "identity": await get_identity_data(user_id),
        "memory": await get_memory_data(user_id),
        "consciousness": await get_consciousness_data(user_id),
        "interactions": await get_interaction_history(user_id),
        "processing_purposes": get_processing_purposes(),
        "retention_periods": get_retention_periods(),
    }
```

## Testing

```python
@pytest.mark.asyncio
async def test_user_can_access_own_data():
    """User can access their own data."""
    response = await client.get("/v1/data-rights/users/user123/data")
    assert response.status_code == 200
    assert "identity" in response.json()
```

## Acceptance Criteria

- [ ] API endpoint implemented
- [ ] All data sources integrated
- [ ] OpenAPI documentation
- [ ] Tests with >80% coverage

**Success**: Users can retrieve all their personal data via API.
```

---

## Prompt 8: Implement Right to Erasure API (GDPR Art. 17)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1589

**Prompt for Claude Code Web**:

```
**Task**: Implement GDPR Right to Erasure API

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1589
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 15 days

## Objective

Implement "Right to be Forgotten" API (GDPR Article 17).

## API Endpoint

```python
@router.delete("/users/{user_id}/data")
async def erase_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Right to Erasure - GDPR Article 17."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only erase own data")
    
    # Create audit log before deletion
    await create_erasure_audit_log(user_id, current_user.id)
    
    # Delete from all systems
    results = {
        "identity": await erase_identity_data(user_id),
        "memory": await erase_memory_data(user_id),
        "audit_logs": await anonymize_audit_logs(user_id)  # Anonymize, don't delete
    }
    
    return {
        "status": "completed",
        "erased_at": datetime.utcnow().isoformat()
    }
```

## Acceptance Criteria

- [ ] All data deleted from all systems
- [ ] Audit logs anonymized (not deleted)
- [ ] Two-step confirmation workflow
- [ ] Tests verify complete erasure

**Success**: Users can permanently delete all their data.
```

---

## Prompt 9: Implement Right to Data Portability API (GDPR Art. 20)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1590

**Prompt for Claude Code Web**:

```
**Task**: Implement GDPR Right to Data Portability API

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1590
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 10 days

## Objective

Allow users to export data in machine-readable formats (JSON, CSV, XML).

## API Endpoint

```python
from fastapi.responses import StreamingResponse

@router.get("/users/{user_id}/export")
async def export_user_data(
    user_id: str,
    format: str = "json",
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """Right to Data Portability - GDPR Article 20."""
    data = await get_user_data(user_id, current_user)
    
    if format == "json":
        content = json.dumps(data, indent=2)
        media_type = "application/json"
    elif format == "csv":
        content = convert_to_csv(data)
        media_type = "text/csv"
    elif format == "xml":
        content = convert_to_xml(data)
        media_type = "application/xml"
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=lukhas_data_{user_id}.{format}"}
    )
```

## Acceptance Criteria

- [ ] JSON, CSV, XML formats supported
- [ ] Streaming for large datasets
- [ ] Tests for all formats

**Success**: Users can export data in multiple formats.
```

---

## Prompt 10: Implement Right to Rectification API (GDPR Art. 16)

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1591

**Prompt for Claude Code Web**:

```
**Task**: Implement GDPR Right to Rectification API

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1591
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 10 days

## Objective

Allow users to correct inaccurate personal data (GDPR Article 16).

## API Endpoint

```python
@router.patch("/users/{user_id}/data")
async def rectify_user_data(
    user_id: str,
    corrections: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Right to Rectification - GDPR Article 16."""
    validated = validate_corrections(corrections)
    results = await apply_data_corrections(user_id, validated)
    
    return {
        "status": "completed",
        "corrected_fields": list(validated.keys())
    }
```

## Acceptance Criteria

- [ ] Field validation in place
- [ ] Audit trail for corrections
- [ ] Tests prevent unauthorized modifications

**Success**: Users can correct their personal data.
```

---

## Prompt 11: Implement Automated Data Retention Policy

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1592

**Prompt for Claude Code Web**:

```
**Task**: Implement Automated Data Retention Policy

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1592
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 10 days

## Objective

Automatically delete expired data according to GDPR requirements.

## Implementation

File: `lukhas/compliance/data_retention.py`

```python
from datetime import datetime, timedelta
from typing import Dict

class DataRetentionPolicy:
    RETENTION_PERIODS = {
        "memory_folds": timedelta(days=90),
        "interaction_logs": timedelta(days=180),
        "audit_logs": timedelta(days=2190),  # 6 years
    }
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Run scheduled cleanup."""
        results = {}
        for data_type, period in self.RETENTION_PERIODS.items():
            cutoff = datetime.utcnow() - period
            count = await self.cleanup_by_type(data_type, cutoff)
            results[data_type] = count
        return results
```

## Cron Job

```yaml
# kubernetes/cronjobs/data-retention.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: lukhas-data-retention
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
```

## Acceptance Criteria

- [ ] Automated cleanup job deployed
- [ ] User-configurable preferences
- [ ] Audit logging of deletions

**Success**: Data automatically deleted after retention period.
```

---

## Prompt 12: Create Privacy Policy and GDPR Documentation

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1593

**Prompt for Claude Code Web**:

```
**Task**: Create Privacy Policy and GDPR Documentation

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1593
**Priority**: P0 - GDPR Compliance
**Estimated Time**: 10 days

## Objective

Create comprehensive privacy policy and documentation required by GDPR.

## Privacy Policy

File: `legal/PRIVACY_POLICY.md`

Must include:
1. Data Controller information
2. Data we collect
3. Legal basis for processing
4. Data retention periods
5. User rights (Access, Erasure, Portability, Rectification)
6. How to exercise rights
7. Data security measures
8. International transfers
9. Contact information

## Additional Documents

- Cookie Policy (`legal/COOKIE_POLICY.md`)
- User Guide (`docs/user/DATA_RIGHTS_GUIDE.md`)
- Privacy notices for all data collection points

## Acceptance Criteria

- [ ] Complete privacy policy published
- [ ] Cookie policy published
- [ ] Privacy notices in all flows
- [ ] Legal review completed

**Success**: Comprehensive GDPR documentation published.
```

---

## Prompt 13: Add Type Annotations to Critical Modules

**GitHub Issue**: https://github.com/LukhasAI/Lukhas/issues/1594

**Prompt for Claude Code Web**:

```
**Task**: Add Type Annotations to Critical Modules

**Repository**: https://github.com/LukhasAI/Lukhas
**Issue Reference**: https://github.com/LukhasAI/Lukhas/issues/1594
**Priority**: P1 - Code Quality
**Estimated Time**: 10 days

## Objective

Add comprehensive type annotations to security and GDPR modules (65% coverage, up from 51%).

## Focus Areas

**Critical Modules**:
- `lukhas/api/v1/data_rights.py`
- `lukhas/compliance/data_retention.py`
- All security remediation code
- Data processing pipelines

## Example

```python
from typing import Dict, Any, Optional
from lukhas.types import UserID, ProcessedData

def process_user_data(
    user_id: UserID,
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> ProcessedData:
    """Process user data with full type safety."""
    result: ProcessedData = transform(data)
    return result
```

## Custom Types

File: `lukhas/types.py`

```python
from typing import NewType, TypedDict

UserID = NewType('UserID', str)

class UserData(TypedDict):
    user_id: UserID
    email: str
    created_at: str
```

## mypy Configuration

```ini
[mypy]
python_version = 3.11
disallow_untyped_defs = True

[mypy-lukhas.api.v1.*]
strict = True
```

## Acceptance Criteria

- [ ] 65% type annotation coverage
- [ ] mypy strict mode passing on critical modules
- [ ] Custom types defined
- [ ] CI/CD type checking enforced

**Success**: Type checking passes, 65% coverage achieved.
```

---

## Execution Instructions

### For Each Prompt:

1. **Copy the entire prompt** (including the code examples)
2. **Open Claude Code Web** at https://claude.ai/code
3. **Paste the prompt**
4. **Review the generated code** and PR
5. **Test the implementation** according to acceptance criteria
6. **Merge the PR** once validated

### Recommended Order:

**Phase 1 - Critical Security (Weeks 1-4)**:
1. Prompt 1: Eliminate eval() calls
2. Prompt 2: Eliminate exec() calls

**Phase 2 - High Security (Weeks 5-12)**:
3. Prompt 3: Fix shell injection
4. Prompt 4: Fix pickle deserialization
5. Prompt 5: Fix SQL injection
6. Prompt 6: Fix YAML unsafe loading

**Phase 3 - GDPR APIs (Weeks 13-20)**:
7. Prompt 7: Right to Access API
8. Prompt 8: Right to Erasure API
9. Prompt 9: Right to Data Portability API
10. Prompt 10: Right to Rectification API

**Phase 4 - GDPR Infrastructure (Weeks 21-24)**:
11. Prompt 11: Data Retention Policy
12. Prompt 12: Privacy Documentation

**Phase 5 - Quality (Weeks 25-30)**:
13. Prompt 13: Type Annotations

### Success Metrics

After completing all 13 prompts:

- **Security**: 0 CRITICAL patterns (down from 75), <150 HIGH patterns (down from 722)
- **GDPR**: 75% compliance (up from 58%), all 4 Data Subject Rights APIs deployed
- **Quality**: 65% type annotations (up from 51%)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Total Issues**: 13
**Total Estimated Effort**: 142 days
**Status**: ✅ Ready for Claude Code Web execution - All 13 GitHub issues created (#1582-#1594)
