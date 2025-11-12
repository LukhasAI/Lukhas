# Guardian Import Guide for Developers
**Version**: 1.1.0
**Last Updated**: 2025-11-12
**Applies To**: Phase 3+ (Consolidation Complete)

## Quick Reference

### ✅ Correct Import Patterns

```python
# Core types (canonical)
from lukhas_website.lukhas.governance.guardian import (
    DriftResult,
    EthicalDecision,
    EthicalSeverity,
    GovernanceAction,
    SafetyResult,
)

# Wrapper functions (canonical)
from lukhas_website.lukhas.governance.guardian import (
    detect_drift,
    evaluate_ethics,
    check_safety,
    get_guardian_status,
)

# Implementation (canonical)
from lukhas_website.lukhas.governance.guardian import GuardianSystemImpl

# Policies and reflector (canonical - Phase 3 relocated implementations)
from lukhas_website.lukhas.governance.guardian import (
    GuardianPoliciesEngine,  # Full implementation (652 lines)
    GuardianReflector,        # Full implementation (791 lines)
)

# Via bridge modules (convenience)
from governance.guardian.core import DriftResult, EthicalDecision
from governance.guardian.guardian_wrapper import detect_drift
from governance.guardian.guardian_impl import GuardianSystemImpl
```

### ⚠️ Legacy Import Patterns (Deprecated - Will Show Warnings)

```python
# DEPRECATED: Legacy bridges (pre-Phase 2)
# Phase 3 added DeprecationWarning to these imports
# Will be removed in Phase 4 (2025-Q1)
from governance.guardian_system import GuardianSystem           # ⚠️ DeprecationWarning
from governance.guardian_sentinel import GuardianSentinel       # ⚠️ DeprecationWarning
from governance.guardian_shadow_filter import GuardianShadowFilter  # ⚠️ DeprecationWarning
from governance.guardian_policies import GuardianPolicies       # ⚠️ DeprecationWarning
from governance.guardian_reflector import GuardianReflector     # ⚠️ DeprecationWarning
```

**Note**: These imports still work but trigger `DeprecationWarning` as of Phase 3. Migrate to canonical imports before Phase 4 (2025-Q1) when these will be removed.

### ❌ Incorrect Import Patterns

```python
# WRONG: Trying to import from non-existent locations
from guardian import GuardianSystem  # No such module
from lukhas.guardian import detect_drift  # Wrong path
from governance.core import DriftResult  # Wrong bridge location
```

## Import Decision Tree

```
Need Guardian functionality?
├─ YES → What are you importing?
│   ├─ Core types (DriftResult, EthicalDecision, etc.)
│   │   └─ Use: from lukhas_website.lukhas.governance.guardian import <types>
│   │
│   ├─ Wrapper functions (detect_drift, evaluate_ethics, etc.)
│   │   └─ Use: from lukhas_website.lukhas.governance.guardian import <functions>
│   │
│   ├─ GuardianSystemImpl (full implementation)
│   │   └─ Use: from lukhas_website.lukhas.governance.guardian import GuardianSystemImpl
│   │
│   ├─ Policies or Reflector
│   │   └─ Use: from lukhas_website.lukhas.governance.guardian import GuardianPolicies|GuardianReflector
│   │
│   └─ Prefer brevity over correctness?
│       └─ Use bridge: from governance.guardian.core import <types>
│
└─ NO → Don't import anything ✅
```

## Lane-Based Import Rules

### Production Lane (`lukhas_website/lukhas/`)

**Rule**: CAN import from all lanes

```python
# ✅ ALLOWED: Import from canonical Guardian
from lukhas_website.lukhas.governance.guardian import detect_drift

# ✅ ALLOWED: Import from core components
from matriz.core import CognitiveOrchestrator

# ✅ ALLOWED: Import from bridge modules
from governance.guardian.core import DriftResult
```

### Integration Lane (`core/`)

**Rule**: CAN import from `core/`, `matriz/`, `universal_language/`

```python
# ✅ ALLOWED: Import from matriz
from matriz.core import CognitiveOrchestrator

# ✅ ALLOWED: Import from governance bridges
from governance.guardian.core import DriftResult

# ❌ FORBIDDEN: Import from lukhas production
from lukhas_website.lukhas.governance.guardian import detect_drift  # VIOLATION
```

### Development Lane (`candidate/`)

**Rule**: CAN import from `core/`, `matriz/` ONLY

```python
# ✅ ALLOWED: Import from matriz
from matriz.core import CognitiveOrchestrator

# ✅ ALLOWED: Import from bridge modules
from governance.guardian.core import DriftResult

# ❌ FORBIDDEN: Import from lukhas production
from lukhas_website.lukhas.governance.guardian import detect_drift  # VIOLATION
```

### Experimental Lane (`labs/`)

**Rule**: Similar to candidate/, experimental prototypes

```python
# ✅ ALLOWED: Import from core, matriz
from matriz.core import CognitiveOrchestrator

# ✅ ALLOWED: Import experimental Guardian components
from labs.governance.guardian import AdvancedDriftDetector
```

**Validation**: Run `make lane-guard` to check import boundaries

## Module Structure Reference

### Canonical Location

```
lukhas_website/lukhas/governance/guardian/
├── __init__.py           ← Public API, re-exports everything
├── core.py               ← Core types
├── guardian_impl.py      ← GuardianSystemImpl
├── guardian_wrapper.py   ← Wrapper functions
├── policies.py           ← ✅ GuardianPoliciesEngine (652 lines - Phase 3 relocated)
└── reflector.py          ← ✅ GuardianReflector (791 lines - Phase 3 relocated)
```

**Import from**: `lukhas_website.lukhas.governance.guardian`

**Phase 3 Consolidation Complete**: All implementations now in canonical location (~2,343 lines total).

### Bridge Modules (Convenience)

```
governance/guardian/
├── __init__.py           ← Bridge initialization
├── core.py               ← Core types bridge
├── guardian_impl.py      ← Implementation bridge
└── guardian_wrapper.py   ← Wrapper functions bridge
```

**Import from**: `governance.guardian.<module>`

### Experimental (Labs)

```
labs/governance/guardian/
├── debug_interface.py
├── drift_detector.py     ← Advanced drift algorithms
├── monitoring_dashboard.py
└── ... (13 experimental files)
```

**Import from**: `labs.governance.guardian.<module>`

## Common Import Scenarios

### Scenario 1: Basic Drift Detection

```python
from lukhas_website.lukhas.governance.guardian import detect_drift

result = detect_drift(
    baseline_behavior="Expected behavior",
    current_behavior="Current behavior",
    mode="dry_run"
)

if result["threshold_exceeded"]:
    print(f"Drift detected: {result['drift_score']}")
```

**Why this import?**
- `detect_drift` is the primary wrapper function
- Located in canonical production location
- Most direct and clear import path

### Scenario 2: Building Custom Guardian Logic

```python
from lukhas_website.lukhas.governance.guardian import (
    GuardianSystemImpl,
    DriftResult,
    EthicalDecision,
)

class CustomGuardian:
    def __init__(self):
        self.guardian = GuardianSystemImpl(drift_threshold=0.20)

    def custom_evaluation(self, data: dict) -> EthicalDecision:
        # Custom logic using Guardian primitives
        pass
```

**Why these imports?**
- Need both implementation and types
- Building custom logic on top of Guardian
- Single canonical import location keeps code clean

### Scenario 3: API Middleware Integration

```python
from lukhas_website.lukhas.governance.guardian import (
    evaluate_ethics,
    GovernanceAction,
    EthicalSeverity,
)
from fastapi import Request, Response

async def guardian_middleware(request: Request, call_next):
    action = GovernanceAction(
        action_type=request.method,
        target=str(request.url.path),
        context={"user": getattr(request.state, "user", None)}
    )

    decision = evaluate_ethics(action, mode="live")

    if not decision["allowed"]:
        return Response(status_code=403, content=decision["reason"])

    return await call_next(request)
```

**Why these imports?**
- Need both wrapper function and types
- Single import line keeps middleware clean
- Canonical location ensures stability

### Scenario 4: Testing Guardian Functionality

```python
import pytest
from lukhas_website.lukhas.governance.guardian import (
    detect_drift,
    evaluate_ethics,
    check_safety,
    GovernanceAction,
)

def test_drift_detection():
    result = detect_drift(
        baseline_behavior="baseline",
        current_behavior="current",
        mode="dry_run"
    )
    assert result["ok"] is True
    assert "drift_score" in result

def test_ethics_evaluation():
    action = GovernanceAction(
        action_type="delete",
        target="critical_data",
        context={}
    )
    decision = evaluate_ethics(action, mode="dry_run")
    assert decision["allowed"] is False  # Risky action should be blocked
```

**Why these imports?**
- All Guardian functions in one import
- Canonical location ensures test stability
- Easy to mock if needed

### Scenario 5: Using Bridge Modules (Shorthand)

```python
# When brevity matters more than explicitness
from governance.guardian.core import DriftResult, EthicalDecision
from governance.guardian.guardian_wrapper import detect_drift

# Instead of the more explicit:
from lukhas_website.lukhas.governance.guardian import (
    DriftResult,
    EthicalDecision,
    detect_drift,
)
```

**When to use bridges?**
- Quick scripts and prototypes
- When import line length is a concern
- When you know the bridge pattern

**When NOT to use bridges?**
- Production code (prefer explicit canonical imports)
- When clarity and maintainability are priorities
- When teaching others the codebase

## Migration Guide

### From Legacy Imports (Pre-Phase 2 → Phase 3)

**Before** (Legacy - triggers DeprecationWarning):
```python
from governance.guardian_policies import GuardianPolicies
from governance.guardian_reflector import GuardianReflector
from governance.guardian_system import GuardianSystem
```

**After** (Phase 3 - Canonical):
```python
from lukhas_website.lukhas.governance.guardian import (
    GuardianPoliciesEngine,  # ✅ Full implementation (652 lines)
    GuardianReflector,        # ✅ Full implementation (791 lines)
)
# Note: GuardianSystem is deprecated, use GuardianSystemImpl
from lukhas_website.lukhas.governance.guardian import GuardianSystemImpl
```

**Migration Steps**:
1. Search for old import patterns: `grep -r "from governance.guardian_" .`
2. Replace with canonical imports (see examples above)
3. Update `GuardianPolicies` → `GuardianPoliciesEngine` for clarity
4. Update `GuardianSystem` → `GuardianSystemImpl` if needed
5. Run tests: `pytest tests/guardian/`
6. Validate: `make imports-guard`
7. Verify no deprecation warnings: `python -W error::DeprecationWarning your_script.py`

**Phase 3 Migration Timeline**:
- **Now (2025-11-12)**: Legacy imports trigger `DeprecationWarning` but still work
- **Phase 4 (2025-Q1)**: Legacy imports will be removed entirely

### From Direct Implementation Imports

**Before**:
```python
# Importing from scattered locations
from governance.guardian_policies import PolicyEngine
from governance.guardian_reflector import DriftMetrics
```

**After**:
```python
# Import from canonical location
from lukhas_website.lukhas.governance.guardian.policies import PolicyEngine
from lukhas_website.lukhas.governance.guardian.reflector import DriftMetrics
```

## Import Patterns by Use Case

### Use Case: REST API Endpoint

```python
from fastapi import APIRouter
from lukhas_website.lukhas.governance.guardian import (
    detect_drift,
    evaluate_ethics,
    check_safety,
    GovernanceAction,
)

router = APIRouter(prefix="/guardian")

@router.post("/drift")
async def check_drift(baseline: str, current: str):
    return detect_drift(baseline, current, mode="live")

@router.post("/ethics")
async def check_ethics(action: GovernanceAction):
    return evaluate_ethics(action, mode="live")

@router.post("/safety")
async def validate_content(content: str):
    return check_safety(content, mode="live")
```

### Use Case: Background Task

```python
from lukhas_website.lukhas.governance.guardian import detect_drift
import asyncio

async def monitor_drift_task(baseline: str):
    while True:
        current = await get_current_behavior()
        result = detect_drift(baseline, current, mode="live")

        if result["threshold_exceeded"]:
            await alert_drift_detected(result)

        await asyncio.sleep(60)  # Check every minute
```

### Use Case: Consciousness Integration

```python
from lukhas_website.lukhas.governance.guardian import (
    evaluate_ethics,
    check_safety,
    GovernanceAction,
)
from matriz.consciousness import ConsciousnessEngine

class EthicalConsciousness(ConsciousnessEngine):
    async def process_thought(self, thought: str):
        # Safety check
        safety = check_safety(thought, constitutional_check=True)
        if not safety["safe"]:
            return None

        # Ethics check
        action = GovernanceAction(
            action_type="process_thought",
            target="consciousness",
            context={"thought": thought}
        )
        decision = evaluate_ethics(action)

        if decision["allowed"]:
            return await super().process_thought(thought)
        return None
```

## Import Anti-Patterns

### ❌ Anti-Pattern 1: Circular Imports

```python
# BAD: Causes circular dependency
from lukhas_website.lukhas.governance.guardian import detect_drift
from lukhas_website.lukhas.governance.guardian_wrapper import _simulate_drift_score

# GOOD: Import only what you need
from lukhas_website.lukhas.governance.guardian import detect_drift
```

### ❌ Anti-Pattern 2: Wildcard Imports

```python
# BAD: Pollutes namespace
from lukhas_website.lukhas.governance.guardian import *

# GOOD: Explicit imports
from lukhas_website.lukhas.governance.guardian import detect_drift, evaluate_ethics
```

### ❌ Anti-Pattern 3: Importing from `__init__.py`

```python
# BAD: Fragile, breaks if __init__ changes
from lukhas_website.lukhas.governance.guardian.__init__ import detect_drift

# GOOD: Import from module directly
from lukhas_website.lukhas.governance.guardian import detect_drift
```

### ❌ Anti-Pattern 4: Mixing Import Styles

```python
# BAD: Inconsistent, confusing
from lukhas_website.lukhas.governance.guardian import detect_drift
from governance.guardian.core import DriftResult
from guardian.guardian_impl import GuardianSystemImpl  # Wrong path!

# GOOD: Consistent imports from one location
from lukhas_website.lukhas.governance.guardian import (
    detect_drift,
    DriftResult,
    GuardianSystemImpl,
)
```

## Type Hints and Static Analysis

### Using Type Hints with Guardian

```python
from typing import Dict, Any
from lukhas_website.lukhas.governance.guardian import (
    DriftResult,
    EthicalDecision,
    GovernanceAction,
)

def process_drift(result: Dict[str, Any]) -> bool:
    """Process drift detection result."""
    return result.get("threshold_exceeded", False)

def handle_decision(decision: Dict[str, Any]) -> None:
    """Handle ethical decision."""
    if not decision["allowed"]:
        raise PermissionError(decision["reason"])

# Better: Use proper type annotations
from dataclasses import dataclass

@dataclass
class ProcessedDrift:
    exceeded: bool
    score: float
    severity: str

def process_drift_typed(result: Dict[str, Any]) -> ProcessedDrift:
    return ProcessedDrift(
        exceeded=result["threshold_exceeded"],
        score=result["drift_score"],
        severity=result["severity"]
    )
```

### MyPy Configuration

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True

[mypy-lukhas_website.lukhas.governance.guardian.*]
# Guardian modules have full type coverage
disallow_untyped_defs = True
warn_return_any = True
```

## IDE Configuration

### VS Code

```json
// .vscode/settings.json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}",
    "${workspaceFolder}/lukhas_website",
    "${workspaceFolder}/governance"
  ],
  "python.autoComplete.extraPaths": [
    "${workspaceFolder}",
    "${workspaceFolder}/lukhas_website",
    "${workspaceFolder}/governance"
  ]
}
```

### PyCharm

```
File → Settings → Project → Project Structure
→ Add Content Root: <workspace>/lukhas_website
→ Add Content Root: <workspace>/governance
```

## Troubleshooting

### Import Error: ModuleNotFoundError

**Error**:
```python
ModuleNotFoundError: No module named 'lukhas_website.lukhas.governance.guardian'
```

**Solutions**:
1. Check PYTHONPATH includes workspace root:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/Lukhas"
   ```

2. Verify file exists:
   ```bash
   ls lukhas_website/lukhas/governance/guardian/__init__.py
   ```

3. Check Python can import:
   ```python
   import sys
   print(sys.path)  # Should include workspace root
   ```

### Import Error: Circular Import

**Error**:
```python
ImportError: cannot import name 'detect_drift' from partially initialized module
```

**Solutions**:
1. Use local imports inside functions:
   ```python
   def my_function():
       from lukhas_website.lukhas.governance.guardian import detect_drift
       return detect_drift(...)
   ```

2. Reorganize imports to break cycle
3. Use TYPE_CHECKING for type-only imports:
   ```python
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from lukhas_website.lukhas.governance.guardian import DriftResult
   ```

### Import Error: Bridge Module Missing

**Error**:
```python
ModuleNotFoundError: No module named 'governance.guardian.core'
```

**Solutions**:
1. Ensure Phase 1 bridges were merged (PR #1356)
2. Check bridge files exist:
   ```bash
   ls governance/guardian/*.py
   ```

3. Use canonical import instead:
   ```python
   from lukhas_website.lukhas.governance.guardian import DriftResult
   ```

## Best Practices Summary

1. **✅ DO**: Use canonical imports from `lukhas_website.lukhas.governance.guardian`
2. **✅ DO**: Import only what you need (explicit imports)
3. **✅ DO**: Use bridge modules for convenience in prototypes
4. **✅ DO**: Follow lane-based import rules (validate with `make lane-guard`)
5. **✅ DO**: Use type hints with Guardian types

6. **❌ DON'T**: Use wildcard imports (`from guardian import *`)
7. **❌ DON'T**: Mix import styles in same file
8. **❌ DON'T**: Import from legacy locations without migration plan
9. **❌ DON'T**: Create circular dependencies
10. **❌ DON'T**: Import from `__init__.py` directly

## Related Documentation

- **Architecture**: [docs/architecture/GUARDIAN_SYSTEM.md](../architecture/GUARDIAN_SYSTEM.md)
- **Phase 2 Audit**: [docs/GUARDIAN_STRUCTURE_CONSOLIDATION_AUDIT_2025-11-12.md](../GUARDIAN_STRUCTURE_CONSOLIDATION_AUDIT_2025-11-12.md)
- **Kill-Switch**: [docs/GUARDIAN_EMERGENCY_KILLSWITCH.md](../GUARDIAN_EMERGENCY_KILLSWITCH.md)
- **Testing**: [tests/guardian/README.md](../../tests/guardian/README.md)

## Getting Help

- **Import Issues**: Check this guide's Troubleshooting section
- **Module Structure**: See [docs/GUARDIAN_STRUCTURE_CONSOLIDATION_AUDIT_2025-11-12.md](../GUARDIAN_STRUCTURE_CONSOLIDATION_AUDIT_2025-11-12.md)
- **Architecture Questions**: See [docs/architecture/GUARDIAN_SYSTEM.md](../architecture/GUARDIAN_SYSTEM.md)
- **Lane Violations**: Run `make lane-guard` for detailed report

---

**Document Status**: ✅ Complete (Phase 3 Final)
**Last Reviewed**: 2025-11-12
**Phase 3 Completion**: 2025-11-12 (All implementations relocated to canonical locations)
**Next Review**: Phase 4 planning (2025-Q1 - legacy import removal)
**Maintainer**: LUKHAS AI Governance Team
