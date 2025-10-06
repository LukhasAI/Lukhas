---
status: wip
type: documentation
---
# Temporary Stubs and Bridges Audit

This document tracks all temporary stubs, bridges, and compatibility shims in the LUKHAS  system.

## Status Overview

| Component | Type | Status | Real Implementation | Notes |
|-----------|------|---------|-------------------|--------|
| Feature Flags | New Module | ✅ Complete | `/lukhas/flags.py` | Production ready |
| Identity Bridge | Bridge | ✅ Sophisticated | `/governance/identity/__init__.py` | Full compatibility system |
| Signal Pattern | Missing Class | ✅ Added | `/orchestration/signals/signal_bus.py` | Now exported properly |
| Ethics Components | Mixed | ⚠️ Partial | Multiple locations | Mix of real and stubs |
| Colony Demo Code | Side Effects | ✅ Isolated | `/core/colonies/demo/` | Moved to prevent imports |

## Ethics Module Analysis

### What Exists (Real Implementations)
- ✅ **EthicsEngine**: `governance/ethics/ethics_engine.py` - Full featured ethics evaluation
- ✅ **Decision**: `governance/policy/base.py` - Complete decision dataclass with validation
- ✅ **RiskLevel**: `governance/policy/base.py` - Proper enum with LOW/MEDIUM/HIGH/CRITICAL
- ✅ **SafetyChecker**: Likely exists but needs mapping

### What's Missing (Using Stubs)
- ❌ **MEGPolicyBridge**: Not found in governance, using stub
- ❌ **create_meg_bridge**: Factory function, using stub

### Import Paths Working
```python
# These now work via ethics/__init__.py
from ethics.meg_bridge import MEGPolicyBridge, create_meg_bridge  # Stub
from ethics.policy_engines.base import Decision, RiskLevel       # Real (from governance)
from ethics.ethics_engine import EthicsEngine                    # Real (from governance)
from ethics.safety_checks import SafetyChecker                   # Real/Stub (needs verification)
```

## Bridge Components

### 1. Identity Bridge (`governance/identity/__init__.py`)
**Type**: Sophisticated compatibility system
**Status**: ✅ Production ready
**Features**:
- Import path mapping with deprecation warnings
- Dynamic module loading with caching
- Virtual module creation for backward compatibility
- Submodule bridging system
- Hook installation for sys.modules

**Usage**:
```python
# All these work thanks to the bridge
from governance.identity import IdentityClient, TierValidator
from identity.core.tier import TierValidator  # Deprecated but works
```

### 2. Feature Flags (`lukhas/flags.py`)
**Type**: New utility module
**Status**: ✅ Complete implementation
**Features**:
- Environment variable support (LUKHAS_FLAG_*)
- YAML configuration file support
- Context managers for testing
- Decorator for conditional execution
- Singleton pattern for global state

**Usage**:
```python
from lukhas.flags import get_flags, require_feature, when_enabled
```

### 3. Signal System (`orchestration/signals/`)
**Type**: Core system with missing exports
**Status**: ✅ Fixed
**Added**:
- `SignalPattern` class with matching logic
- Proper exports in `__init__.py`
- Convenience functions like `emit_stress`

## Temporary Files Created

### Files We Added
1. `/lukhas/flags.py` - Feature flag system (KEEP - production ready)
2. `/governance/identity/__init__.py` - Already existed, sophisticated bridge (KEEP)
3. `/orchestration/signals/signal_bus.py` - Added SignalPattern class (KEEP)
4. `/ethics/stubs.py` - Temporary stubs (REVIEW - some may be replaceable)
5. `/core/colonies/demo/__init__.py` - Demo isolation (KEEP)

### Files We Modified
1. `/ethics/__init__.py` - Updated to use real implementations where possible
2. `/orchestration/signals/__init__.py` - Added proper exports

## Recommendations

### High Priority
1. **Find real MEGPolicyBridge** - Search for existing implementation or create proper one
2. **Verify SafetyChecker location** - Find real implementation in governance
3. **Test ethics integrations** - Ensure colonies work with real components

### Medium Priority
1. **Colony syntax errors** - Fix syntax error in `oracle_colony.py`
2. **ActorRef missing** - Resolve ActorRef import issues in colonies
3. **Validate all bridges** - Comprehensive testing of bridge functionality

### Low Priority
1. **Clean up empty directories** - Ethics subdirectories are empty shells
2. **Documentation** - Document bridge patterns for future use
3. **Migration paths** - Plan removal of deprecated import paths

## Testing Status

### Working Components ✅
- Feature flags (all functions)
- Signal bus and patterns
- Ethics stubs integration
- Basic identity operations

### Needs Attention ⚠️
- Colony imports (syntax/ActorRef issues)
- Real ethics component mapping
- Complete end-to-end flows

### Test Command
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
python3 tests/test_integration_fixes.py
```

## Next Steps

1. **Immediate**: Fix syntax errors blocking colony imports
2. **Short-term**: Map real ethics components to replace remaining stubs
3. **Long-term**: Plan migration away from bridges to direct imports where possible

This audit shows we have good bridge infrastructure in place, with most components working. The remaining issues are primarily about mapping existing implementations rather than creating new stubs.
