# 🛡️ LUKHAS AI Security & Compliance - Phase 1 Remediation

**Target for Claude Code Web**  
**Estimated Effort**: 210 engineering days (6-7 months with team)  
**Priority**: P0 + Core P1  
**Goal**: Eliminate critical security risks and achieve foundational GDPR compliance

---

## 🎯 OBJECTIVES

### Current State (Baseline from Audit)
- **Security**: 2,425 high-risk patterns (75 CRITICAL, 722 HIGH, 1,628 MEDIUM)
- **GDPR Compliance**: 58% ready
- **Code Quality**: 51% type annotations, 71.5% docstrings
- **Overall Status**: Research & Development Phase - Not Production Ready

### Target State (Phase 1 - Manageable Goals)
- **Security**: 0 CRITICAL patterns, <150 HIGH patterns (75% reduction)
- **GDPR Compliance**: 75% ready (+17 percentage points)
- **Code Quality**: 65% type annotations in critical modules
- **Overall Status**: Beta-Ready with Core Compliance

### Success Metrics
✅ **Security**: All 75 CRITICAL patterns eliminated (eval/exec removal)  
✅ **Security**: 100 highest-risk HIGH patterns fixed (shell injection, pickle, SQL)  
✅ **Compliance**: 4 core Data Subject Rights APIs implemented  
✅ **Compliance**: Automated data retention policy deployed  
✅ **Quality**: Type annotations added to all security-critical modules  
✅ **Documentation**: Complete privacy policy and security documentation  

---

## 📋 PHASE 1 WORK BREAKDOWN

### 🚨 PRIORITY 1: CRITICAL Security Patterns (90 days)

#### Task 1.1: Eliminate All eval() Calls (47 occurrences)
**Location**: See `reports/analysis/high_risk_patterns.json` → `.patterns.eval_usage.occurrences`

**Approach**:
```bash
# Extract all eval() locations
jq '.patterns.eval_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > eval_locations.json

# For each occurrence:
# 1. Assess if truly necessary (many in test/research code)
# 2. If test code → Remove or mock
# 3. If production → Replace with safer alternative:
#    - ast.literal_eval() for literals
#    - getattr() for attribute access
#    - Custom parser for expressions
# 4. Add type annotations and validation
# 5. Write security tests
```

**Example Remediation Pattern**:
```python
# ❌ BEFORE (CRITICAL)
result = eval(user_input)

# ✅ AFTER (SAFE)
import ast
from typing import Any

def safe_evaluate_literal(expr: str) -> Any:
    """Safely evaluate Python literal expressions only."""
    try:
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Invalid literal expression: {e}")

result = safe_evaluate_literal(user_input)
```

**Deliverable**: 
- [ ] All 47 eval() calls eliminated or secured
- [ ] Security tests for each replacement
- [ ] Documentation of why each eval() was needed and how replaced

#### Task 1.2: Eliminate All exec() Calls (28 occurrences)
**Location**: See `reports/analysis/high_risk_patterns.json` → `.patterns.exec_usage.occurrences`

**Approach**:
```bash
# Extract all exec() locations
jq '.patterns.exec_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > exec_locations.json

# Remediation strategy:
# 1. Test/demo code → Remove entirely
# 2. Dynamic class creation → Use metaclasses or factory functions
# 3. Code generation → Use templates with Jinja2
# 4. Plugin system → Use importlib with controlled modules
```

**Example Remediation Pattern**:
```python
# ❌ BEFORE (CRITICAL)
exec(dynamic_code)

# ✅ AFTER (SAFE - Plugin System)
import importlib.util
from pathlib import Path
from typing import Any, Optional

def load_plugin_safely(plugin_path: Path, plugin_name: str) -> Optional[Any]:
    """Load plugin from controlled directory only."""
    # Validate plugin is in allowed directory
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

**Deliverable**:
- [ ] All 28 exec() calls eliminated or secured
- [ ] Whitelist-based plugin system if needed
- [ ] Security audit of all dynamic code execution paths

#### Task 1.3: Fix Top 50 HIGH-Risk Patterns (60 days)
**Focus Areas**:
1. **Shell Injection (27 subprocess + 39 os.system = 66 total)**
2. **Pickle Deserialization (12 occurrences)**
3. **SQL Injection (25 occurrences)**
4. **YAML Unsafe Loading (3 occurrences)**

**Shell Injection Remediation**:
```python
# ❌ BEFORE (HIGH RISK)
import subprocess
result = subprocess.run(f"ls {user_path}", shell=True)

# ✅ AFTER (SAFE)
import subprocess
from pathlib import Path
from typing import List

def safe_list_directory(user_path: str) -> List[str]:
    """Safely list directory without shell injection."""
    # Validate path
    path = Path(user_path).resolve()
    if not path.exists() or not path.is_dir():
        raise ValueError("Invalid directory")
    
    # Use array form (no shell=True)
    result = subprocess.run(
        ["ls", str(path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=5
    )
    return result.stdout.splitlines()
```

**SQL Injection Remediation**:
```python
# ❌ BEFORE (HIGH RISK)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ AFTER (SAFE)
from typing import Any, Dict, List

def safe_query_user(user_id: int) -> List[Dict[str, Any]]:
    """Safely query user with parameterized statement."""
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)  # Parameterized - prevents injection
    )
    return cursor.fetchall()
```

**Pickle Deserialization Remediation**:
```python
# ❌ BEFORE (HIGH RISK)
import pickle
data = pickle.loads(untrusted_bytes)

# ✅ AFTER (SAFE)
import json
from typing import Any, Dict

def safe_deserialize(data_bytes: bytes) -> Dict[str, Any]:
    """Use JSON instead of pickle for untrusted data."""
    try:
        return json.loads(data_bytes.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid data format: {e}")
```

**Deliverable**:
- [ ] All 66 shell injection patterns fixed (subprocess/os.system)
- [ ] All 12 pickle.loads() replaced with JSON or hmac-signed pickle
- [ ] All 25 SQL concatenations replaced with parameterized queries
- [ ] All 3 yaml.unsafe_load() replaced with yaml.safe_load()
- [ ] Security tests for each fix
- [ ] Updated security documentation

---

### 🛡️ PRIORITY 2: GDPR Core Compliance (120 days)

#### Task 2.1: Implement Data Subject Rights APIs (60 days)

**API 1: Right to Access (GDPR Art. 15)**
```python
# lukhas/api/v1/data_rights.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime

router = APIRouter(prefix="/v1/data-rights", tags=["GDPR"])

@router.get("/users/{user_id}/data")
async def get_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Right to Access - GDPR Article 15.
    
    Returns all personal data LUKHAS holds about the user:
    - Identity data (ΛID, profile)
    - Memory folds and consciousness states
    - Interaction history
    - Processing purposes
    - Data retention periods
    - Third-party sharing (if any)
    """
    # Verify user is requesting their own data or has admin rights
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only access own data")
    
    # Gather all data from all systems
    return {
        "requested_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "identity": await get_identity_data(user_id),
        "memory": await get_memory_data(user_id),
        "consciousness": await get_consciousness_data(user_id),
        "interactions": await get_interaction_history(user_id),
        "processing_purposes": get_processing_purposes(),
        "retention_periods": get_retention_periods(),
        "third_parties": get_third_party_sharing(user_id),
        "export_format": "JSON",
        "controller": "LUKHAS AI Platform"
    }
```

**API 2: Right to Erasure (GDPR Art. 17)**
```python
@router.delete("/users/{user_id}/data")
async def erase_user_data(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Right to Erasure ("Forget Me") - GDPR Article 17.
    
    Permanently deletes all user data unless legal retention required.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only erase own data")
    
    # Create audit log before deletion (required for compliance)
    await create_erasure_audit_log(user_id, current_user.id)
    
    # Delete from all systems
    results = {
        "identity": await erase_identity_data(user_id),
        "memory": await erase_memory_data(user_id),
        "consciousness": await erase_consciousness_data(user_id),
        "interactions": await erase_interaction_history(user_id),
        "audit_logs": await anonymize_audit_logs(user_id)  # Anonymize, don't delete
    }
    
    return {
        "status": "completed",
        "user_id": user_id,
        "erased_at": datetime.utcnow().isoformat(),
        "systems_processed": list(results.keys()),
        "audit_retention": "6 years (legal requirement)"
    }
```

**API 3: Right to Data Portability (GDPR Art. 20)**
```python
@router.get("/users/{user_id}/export")
async def export_user_data(
    user_id: str,
    format: str = "json",  # json, csv, xml
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    """
    Right to Data Portability - GDPR Article 20.
    
    Export all user data in machine-readable format.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only export own data")
    
    # Gather all data
    data = await get_user_data(user_id, current_user)
    
    # Convert to requested format
    if format == "json":
        content = json.dumps(data, indent=2)
        media_type = "application/json"
    elif format == "csv":
        content = convert_to_csv(data)
        media_type = "text/csv"
    elif format == "xml":
        content = convert_to_xml(data)
        media_type = "application/xml"
    else:
        raise HTTPException(400, "Format must be json, csv, or xml")
    
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename=lukhas_data_{user_id}.{format}"
        }
    )
```

**API 4: Right to Rectification (GDPR Art. 16)**
```python
@router.patch("/users/{user_id}/data")
async def rectify_user_data(
    user_id: str,
    corrections: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Right to Rectification - GDPR Article 16.
    
    Allow users to correct inaccurate personal data.
    """
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Can only rectify own data")
    
    # Validate corrections
    validated = validate_corrections(corrections)
    
    # Apply corrections with audit trail
    results = await apply_data_corrections(user_id, validated)
    
    return {
        "status": "completed",
        "corrected_fields": list(validated.keys()),
        "corrected_at": datetime.utcnow().isoformat()
    }
```

**Deliverable**:
- [ ] All 4 Data Subject Rights APIs implemented
- [ ] Integration tests for each endpoint
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User-facing dashboard for data rights
- [ ] Audit logging for all data operations

#### Task 2.2: Automated Data Retention Policy (30 days)

```python
# lukhas/compliance/data_retention.py

from datetime import datetime, timedelta
from typing import List, Dict
import asyncio

class DataRetentionPolicy:
    """
    Automated data retention and cleanup.
    
    GDPR requires:
    - Data kept no longer than necessary
    - Clear retention periods
    - Automatic deletion after period expires
    """
    
    RETENTION_PERIODS = {
        "memory_folds": timedelta(days=90),  # 90 days of inactivity
        "interaction_logs": timedelta(days=180),  # 6 months
        "audit_logs": timedelta(days=2190),  # 6 years (legal requirement)
        "consciousness_states": timedelta(days=30),  # 30 days
        "temporary_data": timedelta(days=1),  # 24 hours
    }
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Run scheduled cleanup of expired data."""
        results = {}
        
        for data_type, retention_period in self.RETENTION_PERIODS.items():
            cutoff_date = datetime.utcnow() - retention_period
            
            if data_type == "memory_folds":
                count = await self.cleanup_memory_folds(cutoff_date)
            elif data_type == "interaction_logs":
                count = await self.cleanup_interaction_logs(cutoff_date)
            elif data_type == "consciousness_states":
                count = await self.cleanup_consciousness_states(cutoff_date)
            elif data_type == "temporary_data":
                count = await self.cleanup_temporary_data(cutoff_date)
            # Note: audit_logs are never auto-deleted (legal requirement)
            
            results[data_type] = count
        
        # Log cleanup results for audit
        await self.log_cleanup_results(results)
        
        return results
    
    async def cleanup_memory_folds(self, cutoff_date: datetime) -> int:
        """Delete memory folds with no activity since cutoff_date."""
        # Implementation here
        pass
```

**Cron Job Setup**:
```yaml
# kubernetes/cronjobs/data-retention.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: lukhas-data-retention
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: retention-cleanup
            image: lukhas/compliance:latest
            command:
            - python
            - -m
            - lukhas.compliance.data_retention
            env:
            - name: DRY_RUN
              value: "false"
          restartPolicy: OnFailure
```

**Deliverable**:
- [ ] Automated retention policy implemented
- [ ] Scheduled cleanup job deployed
- [ ] User-configurable retention preferences
- [ ] Audit logging of all deletions
- [ ] Dashboard showing retention status

#### Task 2.3: Privacy Documentation (30 days)

**Privacy Policy Template**:
```markdown
# LUKHAS AI Privacy Policy

## 1. Data Controller
LUKHAS AI Platform
[Contact information]

## 2. Data We Collect
- Identity data (ΛID, authentication)
- Memory folds (consciousness interactions)
- Usage data (interaction logs)
- Technical data (IP, browser, device)

## 3. Legal Basis for Processing
- Consent (Art. 6(1)(a))
- Contract performance (Art. 6(1)(b))
- Legitimate interests (Art. 6(1)(f))

## 4. Data Retention
- Memory folds: 90 days of inactivity
- Interaction logs: 6 months
- Audit logs: 6 years (legal requirement)
- User-configurable preferences available

## 5. Your Rights
- Right to Access (get your data)
- Right to Rectification (correct errors)
- Right to Erasure (delete your data)
- Right to Data Portability (export your data)
- Right to Object (opt-out of processing)
- Right to Restrict Processing

## 6. How to Exercise Your Rights
Use our Data Rights Dashboard at /data-rights
Or contact: privacy@lukhas.ai

## 7. Data Security
[Security measures: encryption, access controls, etc.]

## 8. International Transfers
[If applicable - Standard Contractual Clauses]

## 9. Changes to This Policy
[Last updated: DATE]
```

**Deliverable**:
- [ ] Complete privacy policy published
- [ ] Privacy notices in all data collection flows
- [ ] Cookie consent banner (if applicable)
- [ ] GDPR compliance documentation
- [ ] Data Processing Agreements for third parties

---

### 🎯 PRIORITY 3: Type Annotations for Critical Modules (30 days)

**Target**: 65% type annotation coverage (up from 51%)

**Focus Areas**:
1. All security-critical modules (eval/exec replacements)
2. All GDPR API endpoints
3. All authentication/authorization code
4. All data processing pipelines

**Example**:
```python
# Before (51% coverage)
def process_user_data(user_id, data):
    result = transform(data)
    return result

# After (65% coverage target)
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
        data: Raw input data
        options: Optional processing options
        
    Returns:
        Processed and validated data
        
    Raises:
        ValueError: If data validation fails
    """
    result: ProcessedData = transform(data)
    return result
```

**Tools**:
```bash
# Run mypy strict mode on critical modules
mypy --strict lukhas/api/v1/data_rights.py
mypy --strict lukhas/compliance/
mypy --strict lukhas/security/

# Add missing annotations automatically
monkeytype run script.py
monkeytype apply module.name
```

**Deliverable**:
- [ ] 65% type annotation coverage achieved
- [ ] mypy strict mode passing on critical modules
- [ ] Type stubs for third-party libraries
- [ ] CI/CD type checking enforced

---

## 📊 PROGRESS TRACKING

### Weekly Checkpoints
```bash
# Security progress
python3 scripts/security_scan.py > current_scan.json
jq '.summary' current_scan.json
# Compare with baseline: reports/analysis/high_risk_patterns.json

# GDPR progress
curl http://localhost:8000/v1/data-rights/compliance-status
```

### Success Criteria (Phase 1 Complete)
- [ ] **Security**: 0 CRITICAL patterns (down from 75)
- [ ] **Security**: <150 HIGH patterns (down from 722)
- [ ] **GDPR**: 75% compliance (up from 58%)
- [ ] **GDPR**: 4 Data Subject Rights APIs deployed
- [ ] **Quality**: 65% type annotations (up from 51%)
- [ ] **Docs**: Complete privacy policy published

---

## 🚀 EXECUTION STRATEGY

### Week 1-4: CRITICAL Security (eval/exec)
- Inventory all 75 CRITICAL patterns
- Classify: test code vs production code
- Replace production code with safe alternatives
- Write security tests
- Deploy fixes

### Week 5-12: HIGH Security (shell, pickle, SQL)
- Fix all 66 shell injection patterns
- Replace all 12 pickle.loads() calls
- Parameterize all 25 SQL queries
- Security audit and penetration testing

### Week 13-20: GDPR APIs
- Implement 4 Data Subject Rights APIs
- Build user-facing dashboard
- Create API documentation
- Integration testing

### Week 21-24: Data Retention & Privacy
- Deploy automated retention policy
- Write and publish privacy policy
- Add privacy notices to all flows
- Compliance audit

### Week 25-30: Type Annotations & Final Testing
- Add type annotations to critical modules
- Run full security audit
- Compliance verification
- Documentation updates

---

## 📚 REFERENCE MATERIALS

### Audit Reports
- **Main summary**: `reports/analysis/audit_summary.md`
- **Security patterns**: `reports/analysis/high_risk_patterns.json`
- **GDPR compliance**: `reports/analysis/compliance_audit.md`
- **Remediation plan**: `reports/analysis/remediation_roadmap.md`

### Commands
```bash
# List all eval() locations
jq '.patterns.eval_usage.occurrences' reports/analysis/high_risk_patterns.json

# List all exec() locations
jq '.patterns.exec_usage.occurrences' reports/analysis/high_risk_patterns.json

# Check subprocess shell=True
jq '.patterns.subprocess_shell' reports/analysis/high_risk_patterns.json

# View GDPR gaps
grep -A10 "Missing Data Subject Rights" reports/analysis/compliance_audit.md
```

### Testing
```bash
# Security tests
pytest tests/security/ -v

# GDPR API tests
pytest tests/compliance/test_data_rights.py -v

# Type checking
mypy lukhas/ --strict
```

---

## ✅ ACCEPTANCE CRITERIA

This Phase 1 work is **COMPLETE** when:

1. ✅ **All 75 CRITICAL security patterns eliminated** (verified by security scan)
2. ✅ **Top 100 HIGH-risk patterns fixed** (shell, pickle, SQL, YAML)
3. ✅ **4 Data Subject Rights APIs deployed and tested**
4. ✅ **Automated data retention policy running in production**
5. ✅ **Complete privacy policy published and accessible**
6. ✅ **65% type annotation coverage achieved** (verified by coverage tool)
7. ✅ **Security penetration test passed**
8. ✅ **GDPR compliance audit shows 75% readiness**

**Timeline**: 30 weeks (210 days) with 2-3 person team  
**Budget**: ~$150K-$200K USD (assuming $100-150/hour engineering rates)

---

## 🎯 POST-PHASE 1: NEXT STEPS

After completing Phase 1 (75% GDPR, 0 CRITICAL patterns), proceed to:

**Phase 2 Targets**:
- Security: Eliminate remaining 550 HIGH patterns
- GDPR: 90% compliance (all Data Subject Rights, DPO, DPIA)
- Quality: 80% type annotations, 90% docstrings
- Timeline: Additional 240 days (8 months)

This phased approach makes the work **manageable** while delivering **measurable progress** every 4 weeks.

---

**Generated**: November 15, 2025  
**Audit Baseline**: PR #1566 Full Cognitive Audit  
**Target Completion**: Q2 2026 (210 days from start)
