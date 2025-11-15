# 🎯 Claude Code Web - Enumerated Prompt List

**Phase 1 Security & Compliance Remediation**  
**Full Plan**: [CLAUDE_WEB_SECURITY_COMPLIANCE_PHASE1.md](./CLAUDE_WEB_SECURITY_COMPLIANCE_PHASE1.md)  
**Summary**: [CLAUDE_WEB_EXEC_SUMMARY.md](./CLAUDE_WEB_EXEC_SUMMARY.md)

---

## 📖 How to Use These Prompts

### Workflow Options Based on Claude Code Web's Recommendations:

#### **Option 1: Direct Sharing (Simplest)**
Copy any prompt below and paste directly into Claude Code Web with:
```
"Work on Prompt #[number] from CLAUDE_WEB_PROMPTS_ENUMERATED.md"
```

#### **Option 2: Label-Based Workflow (Recommended)**
Create GitHub issues for each prompt with labels:
- `claude-ready` - Ready for Claude to work on
- `phase-1-security` - Security remediation tasks (Prompts 1-6)
- `phase-1-gdpr` - GDPR compliance tasks (Prompts 7-11)
- `phase-1-quality` - Code quality tasks (Prompts 12-13)
- `critical` - CRITICAL pattern elimination (Prompts 1-2)

Then tell Claude Code Web:
```
"Work on issues labeled 'claude-ready' and 'critical'"
```

#### **Option 3: Queue File Workflow**
Create `.claude/issues-queue.md` in your repo:
```markdown
## Current Queue for Claude Code Web
- [ ] Prompt #1: Eliminate eval() calls (47 occurrences)
- [ ] Prompt #2: Eliminate exec() calls (28 occurrences)
- [ ] Prompt #3: Fix shell injection patterns
```

Then: `"Work through the issues in .claude/issues-queue.md"`

#### **Option 4: Session-Based (This Session)**
For immediate work, just say:
```
"Start with Prompt #1" or "Work on Prompt #5"
```

---

## 🚨 PHASE A: CRITICAL Security Elimination (Prompts 1-6)

### **Prompt #1: Eliminate All eval() Calls (47 occurrences)**

**Priority**: CRITICAL  
**Effort**: 30 days  
**Label**: `critical`, `security`, `code-execution`

**Task**:
Eliminate all 47 `eval()` calls from the LUKHAS codebase. These represent immediate code execution risks.

**Context**:
```bash
# Get list of all eval() locations
jq '.patterns.eval_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > eval_locations.json
```

**Approach**:
1. **Classify each eval() call**:
   - Test/demo code → Remove entirely
   - Literal evaluation → Replace with `ast.literal_eval()`
   - Attribute access → Replace with `getattr()`
   - Complex expressions → Build custom safe parser

2. **Remediation pattern**:
```python
# ❌ BEFORE (CRITICAL RISK)
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

3. **For each file modified**:
   - Add comprehensive type annotations
   - Write security tests proving no code execution possible
   - Update docstrings explaining the safe replacement
   - Add to audit trail: `docs/security/eval_removal_log.md`

**Acceptance Criteria**:
- [ ] All 47 eval() calls eliminated (verify with: `rg "\beval\(" --type py`)
- [ ] Security tests pass for each replacement
- [ ] No new security vulnerabilities introduced
- [ ] Documentation updated with remediation details

**Files to Create**:
- `docs/security/eval_removal_log.md` - Audit trail of each eval() removal
- `tests/security/test_no_eval.py` - Test to prevent future eval() usage

---

### **Prompt #2: Eliminate All exec() Calls (28 occurrences)**

**Priority**: CRITICAL  
**Effort**: 20 days  
**Label**: `critical`, `security`, `code-execution`

**Task**:
Eliminate all 28 `exec()` calls from the LUKHAS codebase.

**Context**:
```bash
# Get list of all exec() locations
jq '.patterns.exec_usage.occurrences[] | {file: .file, line: .line, context: .context}' \
  reports/analysis/high_risk_patterns.json > exec_locations.json
```

**Approach**:
1. **Classify each exec() call**:
   - Test/demo code → Remove entirely
   - Dynamic class creation → Use metaclasses or factory functions
   - Code generation → Use Jinja2 templates
   - Plugin loading → Use importlib with path validation

2. **Safe plugin loading pattern**:
```python
# ❌ BEFORE (CRITICAL RISK)
exec(dynamic_code)

# ✅ AFTER (SAFE)
import importlib.util
from pathlib import Path
from typing import Any, Optional

def load_plugin_safely(plugin_path: Path, plugin_name: str) -> Optional[Any]:
    """Load plugin from controlled directory only."""
    # Validate plugin is in allowed directory
    allowed_dir = Path("/opt/lukhas/plugins").resolve()
    resolved_path = plugin_path.resolve()
    
    if not resolved_path.is_relative_to(allowed_dir):
        raise ValueError(f"Plugin must be in {allowed_dir}")
    
    if not resolved_path.suffix == ".py":
        raise ValueError("Plugin must be a .py file")
    
    spec = importlib.util.spec_from_file_location(plugin_name, resolved_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None
```

**Acceptance Criteria**:
- [ ] All 28 exec() calls eliminated (verify with: `rg "\bexec\(" --type py`)
- [ ] Plugin system uses whitelist-based importlib if needed
- [ ] Security audit confirms no dynamic code execution
- [ ] Documentation updated

**Files to Create**:
- `docs/security/exec_removal_log.md`
- `lukhas/plugins/safe_loader.py` - If plugin system needed
- `tests/security/test_no_exec.py`

---

### **Prompt #3: Fix Shell Injection Patterns (66 occurrences)**

**Priority**: HIGH  
**Effort**: 25 days  
**Label**: `high-priority`, `security`, `shell-injection`

**Task**:
Fix all shell injection vulnerabilities:
- 27 `subprocess.run(shell=True)` calls
- 39 `os.system()` calls

**Context**:
```bash
# Get locations
jq '.patterns.subprocess_shell.occurrences' reports/analysis/high_risk_patterns.json
jq '.patterns.os_system.occurrences' reports/analysis/high_risk_patterns.json
```

**Approach**:
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
    
    # Use array form (NO shell=True)
    result = subprocess.run(
        ["ls", "-la", str(path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=5  # Prevent hanging
    )
    return result.stdout.splitlines()
```

**Acceptance Criteria**:
- [ ] All `shell=True` removed (verify: `rg "shell\s*=\s*True" --type py`)
- [ ] All `os.system()` replaced (verify: `rg "os\.system\(" --type py`)
- [ ] Input validation on all file paths
- [ ] Timeout protection on all subprocess calls

---

### **Prompt #4: Fix Pickle Deserialization (12 occurrences)**

**Priority**: HIGH  
**Effort**: 10 days  
**Label**: `high-priority`, `security`, `deserialization`

**Task**:
Replace all `pickle.loads()` calls on untrusted data.

**Approach**:
```python
# ❌ BEFORE (HIGH RISK)
import pickle
data = pickle.loads(untrusted_bytes)

# ✅ AFTER (SAFE - Option 1: Use JSON)
import json
from typing import Dict, Any

def safe_deserialize(data_bytes: bytes) -> Dict[str, Any]:
    """Use JSON instead of pickle for untrusted data."""
    try:
        return json.loads(data_bytes.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Invalid data format: {e}")

# ✅ AFTER (SAFE - Option 2: HMAC-signed pickle)
import pickle
import hmac
import hashlib
from typing import Any

SECRET_KEY = b"your-secret-key-from-env"

def safe_pickle_loads(signed_data: bytes) -> Any:
    """Load pickle only if HMAC signature valid."""
    if len(signed_data) < 32:
        raise ValueError("Invalid signed data")
    
    signature = signed_data[:32]
    data = signed_data[32:]
    
    # Verify signature
    expected_sig = hmac.new(SECRET_KEY, data, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    
    return pickle.loads(data)
```

**Acceptance Criteria**:
- [ ] All 12 pickle.loads() on untrusted data replaced
- [ ] Use JSON for external data
- [ ] Use HMAC-signed pickle only for internal trusted data
- [ ] Security tests verify no arbitrary code execution

---

### **Prompt #5: Fix SQL Injection Patterns (25 occurrences)**

**Priority**: HIGH  
**Effort**: 15 days  
**Label**: `high-priority`, `security`, `sql-injection`

**Task**:
Replace all SQL string concatenation with parameterized queries.

**Approach**:
```python
# ❌ BEFORE (HIGH RISK)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ AFTER (SAFE)
from typing import Any, Dict, List

def safe_query_user(user_id: int) -> List[Dict[str, Any]]:
    """Safely query user with parameterized statement."""
    # Parameterized query - prevents injection
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )
    return cursor.fetchall()

# For complex queries
def safe_query_users_filtered(
    status: str,
    role: str,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Complex parameterized query."""
    cursor.execute(
        """
        SELECT * FROM users 
        WHERE status = ? AND role = ?
        LIMIT ?
        """,
        (status, role, limit)
    )
    return cursor.fetchall()
```

**Acceptance Criteria**:
- [ ] All 25 SQL concatenations replaced with parameterized queries
- [ ] Verify with: `rg "execute.*f['\"]" --type py` (should be empty)
- [ ] ORM usage reviewed (SQLAlchemy/Django already safe)
- [ ] SQL injection penetration test passed

---

### **Prompt #6: Fix YAML Unsafe Loading (3 occurrences)**

**Priority**: HIGH  
**Effort**: 2 days  
**Label**: `high-priority`, `security`, `yaml`

**Task**:
Replace `yaml.unsafe_load()` and `yaml.load()` with `yaml.safe_load()`.

**Approach**:
```python
# ❌ BEFORE (HIGH RISK)
import yaml
data = yaml.load(config_file)  # or yaml.unsafe_load()

# ✅ AFTER (SAFE)
import yaml
from typing import Any

def load_yaml_safely(file_path: str) -> Any:
    """Load YAML with safe loader only."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)
```

**Acceptance Criteria**:
- [ ] All 3 unsafe YAML loads fixed
- [ ] Verify: `rg "yaml\.(load|unsafe_load)\(" --type py` (should be empty)
- [ ] All YAML loading uses `yaml.safe_load()`

---

## 🛡️ PHASE B: GDPR Core Compliance (Prompts 7-11)

### **Prompt #7: Implement Right to Access API (GDPR Art. 15)**

**Priority**: HIGH  
**Effort**: 15 days  
**Label**: `gdpr`, `data-rights`, `api`

**Task**:
Create API endpoint for users to retrieve all their personal data.

**Implementation**:
Create file: `lukhas/api/v1/data_rights.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
from lukhas.auth import get_current_user, User

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
        "controller": "LUKHAS AI Platform",
        "contact": "privacy@lukhas.ai"
    }
```

**Helper functions to implement**:
- `get_identity_data(user_id)` - Query identity database
- `get_memory_data(user_id)` - Query memory system
- `get_consciousness_data(user_id)` - Query consciousness states
- `get_interaction_history(user_id)` - Query all interactions

**Acceptance Criteria**:
- [ ] API endpoint deployed and accessible
- [ ] Returns complete user data from all systems
- [ ] Authentication/authorization working
- [ ] API documentation generated (Swagger/OpenAPI)
- [ ] Integration tests passing

**Files to Create**:
- `lukhas/api/v1/data_rights.py`
- `tests/api/test_data_rights.py`
- `docs/api/data_rights.md`

---

### **Prompt #8: Implement Right to Erasure API (GDPR Art. 17)**

**Priority**: HIGH  
**Effort**: 20 days  
**Label**: `gdpr`, `data-rights`, `api`

**Task**:
Create "Forget Me" functionality to permanently delete user data.

**Implementation**:
Add to `lukhas/api/v1/data_rights.py`:

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
    
    # Create audit log BEFORE deletion (required for compliance)
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
        "audit_retention": "6 years (legal requirement)",
        "reversible": False
    }
```

**Important**:
- Audit logs must be anonymized, NOT deleted (legal requirement)
- Confirm deletion with user before executing
- Make deletion irreversible
- Comply with legal retention periods

**Acceptance Criteria**:
- [ ] API endpoint deployed
- [ ] Deletes data from all systems
- [ ] Audit logs preserved (anonymized)
- [ ] Confirmation workflow implemented
- [ ] Integration tests for complete deletion

---

### **Prompt #9: Implement Data Portability API (GDPR Art. 20)**

**Priority**: HIGH  
**Effort**: 15 days  
**Label**: `gdpr`, `data-rights`, `api`

**Task**:
Allow users to export all their data in machine-readable format (JSON, CSV, XML).

**Implementation**:
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

**Acceptance Criteria**:
- [ ] Supports JSON, CSV, XML export formats
- [ ] Complete data included in export
- [ ] Proper streaming for large datasets
- [ ] Download works in browser
- [ ] Tests for all formats

---

### **Prompt #10: Implement Automated Data Retention Policy**

**Priority**: HIGH  
**Effort**: 20 days  
**Label**: `gdpr`, `data-retention`, `automation`

**Task**:
Implement automated cleanup of old data per GDPR requirement.

**Implementation**:
Create file: `lukhas/compliance/data_retention.py`

```python
from datetime import datetime, timedelta
from typing import Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

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
            
            logger.info(f"Cleaning {data_type} older than {cutoff_date}")
            
            if data_type == "memory_folds":
                count = await self.cleanup_memory_folds(cutoff_date)
            elif data_type == "interaction_logs":
                count = await self.cleanup_interaction_logs(cutoff_date)
            elif data_type == "consciousness_states":
                count = await self.cleanup_consciousness_states(cutoff_date)
            elif data_type == "temporary_data":
                count = await self.cleanup_temporary_data(cutoff_date)
            # Note: audit_logs are never auto-deleted (legal requirement)
            else:
                count = 0
            
            results[data_type] = count
            logger.info(f"Cleaned {count} {data_type} records")
        
        # Log cleanup results for audit
        await self.log_cleanup_results(results)
        
        return results
```

**Kubernetes CronJob**:
Create file: `kubernetes/cronjobs/data-retention.yaml`

```yaml
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

**Acceptance Criteria**:
- [ ] Retention policy implemented for all data types
- [ ] Scheduled cleanup running daily
- [ ] User-configurable preferences (opt for longer retention)
- [ ] Audit logging of all deletions
- [ ] Dashboard showing retention status

---

### **Prompt #11: Create Privacy Policy & Documentation**

**Priority**: HIGH  
**Effort**: 10 days  
**Label**: `gdpr`, `documentation`, `legal`

**Task**:
Write comprehensive privacy policy and add privacy notices to all data collection points.

**Implementation**:
Create file: `docs/legal/PRIVACY_POLICY.md`

```markdown
# LUKHAS AI Privacy Policy

**Last Updated**: [DATE]  
**Effective Date**: [DATE]

## 1. Data Controller
**LUKHAS AI Platform**  
[Contact Information]  
Data Protection Officer: privacy@lukhas.ai

## 2. What Data We Collect

### Personal Data
- **Identity Data**: ΛID (Lambda ID), username, email
- **Authentication Data**: Password hash, 2FA secrets
- **Profile Data**: Display name, preferences

### Usage Data
- **Memory Folds**: Your interactions with the consciousness system
- **Conversation History**: Your chats and queries
- **System Logs**: Interaction timestamps, feature usage

### Technical Data
- **Device Information**: IP address, browser type, device ID
- **Performance Data**: Response times, error logs

## 3. Legal Basis for Processing

We process your data under:
- **Consent** (GDPR Art. 6(1)(a)) - You explicitly agreed
- **Contract Performance** (GDPR Art. 6(1)(b)) - Necessary for service
- **Legitimate Interests** (GDPR Art. 6(1)(f)) - Security, fraud prevention

## 4. How We Use Your Data

- Provide consciousness-aware AI services
- Maintain memory across sessions
- Improve system performance
- Ensure security and prevent abuse
- Comply with legal obligations

## 5. Data Retention Periods

| Data Type | Retention Period | Reason |
|-----------|-----------------|--------|
| Memory Folds | 90 days of inactivity | Service quality |
| Interaction Logs | 6 months | Debugging, analytics |
| Audit Logs | 6 years | Legal requirement |
| Consciousness States | 30 days | Performance optimization |
| Temporary Data | 24 hours | Processing only |

**User Control**: You can configure longer retention in your settings.

## 6. Your GDPR Rights

### Right to Access (Art. 15)
Get a copy of all your data: `/data-rights/users/{your-id}/data`

### Right to Rectification (Art. 16)
Correct errors in your data: `/data-rights/users/{your-id}/data` (PATCH)

### Right to Erasure (Art. 17)
Delete all your data: `/data-rights/users/{your-id}/data` (DELETE)

### Right to Data Portability (Art. 20)
Export your data (JSON/CSV/XML): `/data-rights/users/{your-id}/export`

### Right to Object (Art. 21)
Object to processing: Contact privacy@lukhas.ai

### Right to Restrict Processing (Art. 18)
Limit how we use your data: Contact privacy@lukhas.ai

### How to Exercise Your Rights
- **API**: Use our Data Rights endpoints
- **Dashboard**: Visit `/settings/privacy`
- **Email**: privacy@lukhas.ai
- **Response Time**: Within 30 days

## 7. Data Security

We protect your data with:
- **Encryption**: AES-256 at rest, TLS 1.3 in transit
- **Access Control**: Role-based access, ΛID authentication
- **Audit Trails**: All data access logged
- **Regular Audits**: Quarterly security reviews

## 8. Data Sharing

We **DO NOT** sell your data.

We may share data with:
- **Service Providers**: Cloud hosting (AWS/GCP) - DPA in place
- **Legal Requirements**: If required by law
- **Security**: With law enforcement if necessary

All third parties sign Data Processing Agreements (DPAs).

## 9. International Transfers

If data leaves the EU/EEA, we use:
- **Standard Contractual Clauses** (EU Commission approved)
- **Adequacy Decisions** (for approved countries)

## 10. Cookies & Tracking

We use:
- **Essential Cookies**: Authentication, security (required)
- **Analytics Cookies**: Usage statistics (optional - you can opt-out)

Manage cookies: `/settings/cookies`

## 11. Children's Privacy

LUKHAS is not intended for children under 16. We do not knowingly collect data from children.

## 12. Changes to This Policy

We'll notify you of material changes:
- Email notification
- Dashboard banner
- 30 days notice before changes take effect

## 13. Contact Us

**Data Protection Officer**: privacy@lukhas.ai  
**General Inquiries**: support@lukhas.ai  
**Supervisory Authority**: [Your local data protection authority]

## 14. Your Right to Complain

If you're unhappy with how we handle your data, you can complain to:
- **Our DPO**: privacy@lukhas.ai
- **Your local supervisory authority**: [Link]
```

**Privacy Notices** (add to UI):
```html
<!-- At signup -->
<p class="privacy-notice">
  By creating an account, you agree to our 
  <a href="/privacy">Privacy Policy</a> and 
  <a href="/terms">Terms of Service</a>.
  We will process your data as described in our privacy policy.
</p>

<!-- At data collection points -->
<p class="privacy-notice">
  We collect this data to [PURPOSE]. 
  See our <a href="/privacy#data-collection">Privacy Policy</a> for details.
</p>
```

**Acceptance Criteria**:
- [ ] Complete privacy policy published
- [ ] Privacy notices on all data collection forms
- [ ] Cookie consent banner (if applicable)
- [ ] Privacy settings dashboard
- [ ] Legal review completed

---

## 🎯 PHASE C: Quality & Final Audit (Prompts 12-13)

### **Prompt #12: Add Type Annotations to Security-Critical Modules**

**Priority**: MEDIUM  
**Effort**: 20 days  
**Label**: `code-quality`, `type-safety`

**Task**:
Increase type annotation coverage from 51% to 65% in security-critical modules.

**Target Modules**:
- All files with eval/exec replacements (from Prompts 1-2)
- All GDPR API endpoints (from Prompts 7-9)
- All authentication/authorization code
- All data processing pipelines

**Approach**:
```bash
# Run mypy strict mode
mypy --strict lukhas/api/v1/data_rights.py
mypy --strict lukhas/compliance/
mypy --strict lukhas/security/

# Auto-generate annotations with monkeytype
monkeytype run -m pytest tests/
monkeytype apply lukhas.api.v1.data_rights

# Check coverage
mypy --html-report coverage/ lukhas/
```

**Example**:
```python
# Before (51% coverage)
def process_data(user_id, data, options=None):
    result = transform(data)
    if options:
        result = apply_options(result, options)
    return result

# After (65% coverage target)
from typing import Dict, Any, Optional
from lukhas.types import UserID, ProcessedData

def process_data(
    user_id: UserID,
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> ProcessedData:
    """
    Process user data with full type safety.
    
    Args:
        user_id: Unique user identifier (ΛID)
        data: Raw input data to process
        options: Optional processing configuration
        
    Returns:
        Processed and validated data
        
    Raises:
        ValueError: If data validation fails
        TypeError: If data types are incorrect
    """
    result: ProcessedData = transform(data)
    if options is not None:
        result = apply_options(result, options)
    return result
```

**Acceptance Criteria**:
- [ ] 65% type annotation coverage achieved
- [ ] mypy strict mode passing on critical modules
- [ ] CI/CD enforces type checking
- [ ] No type errors in production code

---

### **Prompt #13: Security Audit & Compliance Verification**

**Priority**: HIGH  
**Effort**: 10 days  
**Label**: `audit`, `security`, `compliance`

**Task**:
Run comprehensive security and compliance audit to verify Phase 1 completion.

**Security Audit**:
```bash
# Re-run security scan
python3 scripts/security_scan.py > final_scan.json

# Compare with baseline
jq '.summary' reports/analysis/high_risk_patterns.json > baseline.json
jq '.summary' final_scan.json > final.json
diff baseline.json final.json

# Should show:
# - critical_count: 75 → 0
# - high_count: 722 → <150
```

**GDPR Compliance Check**:
```bash
# Test all Data Subject Rights APIs
curl http://localhost:8000/v1/data-rights/users/test-user/data
curl -X DELETE http://localhost:8000/v1/data-rights/users/test-user/data
curl http://localhost:8000/v1/data-rights/users/test-user/export?format=json

# Verify data retention
python3 -m lukhas.compliance.data_retention --dry-run

# Check privacy policy
curl http://localhost:8000/privacy
```

**Penetration Testing**:
- Attempt code injection (should fail)
- Attempt SQL injection (should fail)
- Attempt unauthorized data access (should fail)
- Test GDPR workflows (should succeed)

**Acceptance Criteria**:
- [ ] 0 CRITICAL security patterns
- [ ] <150 HIGH security patterns
- [ ] 75% GDPR compliance verified
- [ ] All Data Subject Rights APIs working
- [ ] Privacy policy published
- [ ] Penetration test passed
- [ ] Type annotation coverage ≥65%
- [ ] All Phase 1 acceptance criteria met

**Final Deliverable**:
Create file: `docs/compliance/PHASE1_COMPLETION_REPORT.md`

```markdown
# Phase 1 Completion Report

**Date**: [DATE]  
**Audit Period**: [START] - [END]

## Security Improvements

| Metric | Baseline | Target | Achieved | Status |
|--------|----------|--------|----------|--------|
| CRITICAL patterns | 75 | 0 | 0 | ✅ |
| HIGH patterns | 722 | <150 | [ACTUAL] | ✅/❌ |
| eval() calls | 47 | 0 | 0 | ✅ |
| exec() calls | 28 | 0 | 0 | ✅ |
| Shell injection | 66 | 0 | 0 | ✅ |
| SQL injection | 25 | 0 | 0 | ✅ |

## GDPR Compliance

| Feature | Status |
|---------|--------|
| Right to Access API | ✅ Deployed |
| Right to Erasure API | ✅ Deployed |
| Data Portability API | ✅ Deployed |
| Data Retention Policy | ✅ Automated |
| Privacy Policy | ✅ Published |
| Privacy Notices | ✅ Added |
| Overall Compliance | 75% ✅ |

## Code Quality

| Metric | Baseline | Target | Achieved |
|--------|----------|--------|----------|
| Type annotations | 51% | 65% | [ACTUAL]% |
| Docstring coverage | 71.5% | 75% | [ACTUAL]% |

## Conclusion

Phase 1 **[COMPLETE/INCOMPLETE]**

LUKHAS AI is now **[Beta-Ready/Needs Additional Work]** for production deployment with core security and compliance features in place.

## Next Steps

Proceed to Phase 2:
- Eliminate remaining HIGH patterns (550+)
- Achieve 90% GDPR compliance
- Implement full DPO and DPIA processes
```

---

## 📊 Progress Tracking

### Weekly Checkpoint Commands
```bash
# Security progress
python3 scripts/security_scan.py > scan_week_$(date +%U).json
jq '.summary' scan_week_$(date +%U).json

# Compare with baseline
diff <(jq '.summary' reports/analysis/high_risk_patterns.json) \
     <(jq '.summary' scan_week_$(date +%U).json)

# GDPR API health
curl http://localhost:8000/v1/data-rights/health

# Type annotation coverage
mypy --html-report coverage/ lukhas/
open coverage/index.html
```

### GitHub Issues Creation Script
```bash
#!/bin/bash
# create_phase1_issues.sh

# Prompt #1
gh issue create \
  --title "🚨 CRITICAL: Eliminate all eval() calls (47 occurrences)" \
  --body "See docs/prompts/CLAUDE_WEB_PROMPTS_ENUMERATED.md - Prompt #1" \
  --label "claude-ready,critical,security,code-execution,phase-1-security"

# Prompt #2
gh issue create \
  --title "🚨 CRITICAL: Eliminate all exec() calls (28 occurrences)" \
  --body "See docs/prompts/CLAUDE_WEB_PROMPTS_ENUMERATED.md - Prompt #2" \
  --label "claude-ready,critical,security,code-execution,phase-1-security"

# ... (continue for all prompts)
```

---

## 🎯 How to Execute

### For Claude Code Web - Choose Your Workflow:

#### **Immediate Start** (Session-Based)
```
"Start with Prompt #1: Eliminate eval() calls"
```

#### **Label-Based** (Create issues first)
```bash
# 1. Create GitHub issues for all 13 prompts
./scripts/create_phase1_issues.sh

# 2. Tell Claude Code Web:
"Work on issues labeled 'claude-ready' and 'critical'"
```

#### **Queue File** (Organized approach)
```bash
# 1. Create queue file
cat > .claude/issues-queue.md << 'EOF'
## Phase 1 Security & Compliance Queue

### Week 1-4: CRITICAL Security
- [ ] Prompt #1: Eliminate eval() calls (47 occurrences)
- [ ] Prompt #2: Eliminate exec() calls (28 occurrences)

### Week 5-8: HIGH Security
- [ ] Prompt #3: Fix shell injection (66 occurrences)
- [ ] Prompt #4: Fix pickle deserialization (12 occurrences)
- [ ] Prompt #5: Fix SQL injection (25 occurrences)
- [ ] Prompt #6: Fix YAML unsafe loading (3 occurrences)

### Week 9-20: GDPR APIs
- [ ] Prompt #7: Right to Access API
- [ ] Prompt #8: Right to Erasure API
- [ ] Prompt #9: Data Portability API
- [ ] Prompt #10: Data Retention Policy
- [ ] Prompt #11: Privacy Documentation

### Week 21-30: Quality & Audit
- [ ] Prompt #12: Type Annotations
- [ ] Prompt #13: Final Security Audit
EOF

# 2. Tell Claude Code Web:
"Work through .claude/issues-queue.md starting with CRITICAL tasks"
```

#### **Direct Sharing** (One at a time)
```
"Work on Prompt #[NUMBER]"
# Copy-paste the specific prompt from this document
```

---

## ✅ Phase 1 Complete When:

- [ ] All 13 prompts completed
- [ ] 0 CRITICAL security patterns
- [ ] <150 HIGH security patterns  
- [ ] 75% GDPR compliance
- [ ] 4 Data Subject Rights APIs deployed
- [ ] Privacy policy published
- [ ] 65% type annotation coverage
- [ ] Security penetration test passed

**Timeline**: 30 weeks (210 days)  
**Budget**: $150K-$200K USD  
**Status**: Ready for Beta Launch

---

**Generated**: November 15, 2025  
**Full Plan**: [CLAUDE_WEB_SECURITY_COMPLIANCE_PHASE1.md](./CLAUDE_WEB_SECURITY_COMPLIANCE_PHASE1.md)  
**Summary**: [CLAUDE_WEB_EXEC_SUMMARY.md](./CLAUDE_WEB_EXEC_SUMMARY.md)
