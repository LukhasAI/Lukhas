# Missing Modules Analysis for LUKHAS AI Test Suite

**Date**: 2025-10-06
**Context**: Reducing pytest collection errors from 111 to <102 (50% of original 204)
**Task**: Create bridge modules for all missing imports using real implementations

---

## Instructions for GPT-5

You are tasked with creating bridge modules for the LUKHAS AI codebase. Follow these requirements:

### Bridge Pattern (Explicit-API with `_CANDIDATES`)

Use the `bridge_from_candidates()` utility from `lukhas._bridgeutils`:

```python
"""Bridge: module_name -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.MODULE.PATH",  # Try lukhas_website first
    "candidate.MODULE.PATH",               # Then candidate
    "MODULE.PATH",                         # Then root package
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
```

### Search Strategy for Real Implementations

For each missing module, search in this order:
1. `lukhas_website/lukhas/MODULE/PATH/` (most common location)
2. `candidate/MODULE/PATH/`
3. Root package `MODULE/PATH/`

Use these commands to find real implementations:
```bash
# Find the module file
find . -path "*/MODULE/PATH.py" | grep -v ".venv" | grep -v __pycache__

# Find the class/symbol
grep -r "class SYMBOL" --include="*.py" . | grep -v ".venv"

# Find the directory
find . -type d -name "MODULE_NAME" | grep -v ".venv"
```

### Rules

1. **Never create mocks** - Always find and use real implementations
2. **Use explicit `_CANDIDATES` tuples** - No star imports without bridge_from_candidates
3. **Create `__init__.py` for packages** - If creating a directory bridge
4. **Export missing symbols** - If import errors show specific symbols missing
5. **Document what you found** - Note which canonical location you used

---

## Missing Modules (39 Total)

### Bridge API Modules (1)
- `bridge.api.identity` → Need: `AuthUser`, `get_current_user`

### Candidate Modules (6)
- `candidate.core.matriz`
- `candidate.core.symbolic.symbolic_glyph_hash`
- `candidate.ledger`
- `candidate.matriz`
- `candidate.rl`
- `candidate.trace`

### Consciousness Modules (4)
- `consciousness.systems` → Need: `ConsciousnessState`
- `lukhas.consciousness.enhanced_thought_engine` → Need: `EnhancedThoughtEngine`, `ThoughtComplexity`
- `lukhas.consciousness.matriz_thought_loop` → *Already exists, but not importing correctly*
- `lukhas.consciousness.types` → Need: `DEFAULT_CREATIVITY_CONFIG`, `ConsciousnessState`, `CreativeTask`, `CreativitySnapshot`, `AwarenessSnapshot`, `ReflectionReport`

### Core Modules (7)
- `core.breakthrough`
- `core.business`
- `core.clock`
- `core.collective.clusters`
- `core.consciousness`
- `core.ethics.logic` → Need: DSL evaluation components
- `core.common` → Need to export: `GLYPHToken`

### Governance Modules (3)
- `governance.audit_trail`
- `governance.guardian` → Need: `core` submodule with `EthicalSeverity`, `GovernanceAction`
- `governance.guardian_system` → Need: `GuardianSystem`

### LUKHAS Submodules (7)
- `lukhas.bio.utils`
- `lukhas.memory.backends`
- `lukhas.observability.compliance_dashboard`
- `lukhas.observability.evidence_collection`
- `lukhas.observability.opentelemetry_tracing`
- `lukhas.observability.performance_regression`
- `lukhas.observability.prometheus_metrics`
- `lukhas.observability.service_metrics`

### Memory Modules (6)
- `memory.backends`
- `memory.folds`
- `memory.indexer`
- `memory.lifecycle`
- `memory.memory_event`
- `memory.observability`

### Tools Modules (5)
- `tools.acceptance_gate_ast`
- `tools.analysis`
- `tools.commands`
- `tools.scripts` → Need: `generate_final_research_report`
- `tools.security`

**Note**: `tools/` directory exists but `lukhas/tools.py` file is shadowing it. May need to be converted to package.

---

## Import Errors - Missing Symbols (41 Total)

These modules exist but don't export specific symbols. Update their `__all__` or create proper bridges.

### High Priority Symbols

#### `GLYPHToken` (appears 3 times)
- Needed by: `core.common`, `lukhas.core.common`
- **Action**: Find GLYPHToken class and ensure it's exported

#### `ConsciousnessState` (appears 3 times)
- Needed by: `lukhas.consciousness.types`, `consciousness.systems`
- **Action**: Find in lukhas_website or candidate

#### `ConsciousnessStream`, `ConsciousnessTicker`, `ConsciousnessTaskManager`
- Related to consciousness streaming/async management
- **Action**: Find in async_manager, core.consciousness_stream, core.consciousness_ticker

### Symbol-to-Module Mapping

| Symbol | Expected Module | Action |
|--------|----------------|--------|
| `AIModel`, `AIProvider` | `orchestration.multi_ai_router` | Export from module |
| `AdaptiveCircuitBreaker` | `core.reliability` | Export from module |
| `AutoConsciousness` | `consciousness` | Export from consciousness/__init__.py |
| `AwarenessLevel` | `consciousness` | Export from consciousness/__init__.py |
| `CompressionLevel` | `candidate.memory.compression`, `memory.scheduled_folding`, `orchestration.context_preservation` | Export from module |
| `ConsciousnessStream` | `core.consciousness_stream` | Create bridge |
| `ConsciousnessTaskManager` | `async_manager` | Export from async_manager/__init__.py |
| `ConsciousnessTicker` | `core.consciousness_ticker` | Create bridge |
| `DecimatingRing` | `core.ring` | Export from module |
| `GLYPHToken` | `core.common` | Create bridge to candidate.core.common |
| `GLYPHTokenError` | `candidate.core.common.exceptions` | Export from exceptions |
| `GuardianSerializer` | `governance.guardian_serializers` | Export from module |
| `InferenceRequest` | `cognitive_core.reasoning.deep_inference_engine` | Already has bridge, needs to export symbol |
| `LANE_CFG` | `core.drift` | Export from module |
| `LanePolicyConfig` | `core.policy_guard` | Export from module |
| `ZSTD_AVAILABLE` | `candidate.memory.compression` | Export from module |
| `collapse_simulator_main` | `tools` | Need `tools.collapse_simulator_main` module |
| `get_constellation_context` | `branding_bridge` | Export from branding |
| `resolve` | `core.registry` | Export from module |

---

## Special Cases

### 1. `aka_qualia` Package Error
```
AttributeError: module 'aka_qualia' has no attribute '__path__'
```
**Issue**: `aka_qualia/__init__.py` is not properly structured as a package
**Action**: Ensure `aka_qualia/__init__.py` has proper structure and exports `AkaQualia` from `aka_qualia.core`

### 2. `tools` is Not a Package
```
ModuleNotFoundError: No module named 'tools.scripts'; 'tools' is not a package
```
**Issue**: `lukhas/tools.py` file exists, shadowing `tools/` directory
**Action**:
- Option A: Delete `lukhas/tools.py`, create `tools/__init__.py`
- Option B: Create `lukhas/tools/` package and move `tools.py` → `tools/__init__.py`

### 3. SyntaxError in `openai_modulated_service.py`
```
candidate/consciousness/reflection/openai_modulated_service.py:22
    from datetime import timezone
    ^
SyntaxError: invalid syntax
```
**Issue**: File has syntax error (likely encoding or actual Python syntax issue)
**Action**: Fix the syntax error in the file

### 4. Marker Errors (not module issues)
- `'chaos_resilience' not found in markers configuration option`
- `'deployment' not found in markers configuration option`
**Action**: Add these to `pytest.ini` `[pytest] markers` section

---

## Verification Commands

After creating bridges, verify with:

```bash
# Check collection error count
python3 -m pytest --collect-only -q 2>&1 | tail -1

# Test specific bridge
python3 -c "from lukhas.consciousness.types import ConsciousnessState; print(ConsciousnessState)"

# Run bridge contract tests
python3 -m pytest tests/bridges/test_chatgpt_bridges.py -v

# Check for remaining collisions
python3 - <<'PY'
from pathlib import Path
for py in Path(".").rglob("*.py"):
    if ".venv" in py.parts or "__pycache__" in py.parts:
        continue
    pkg = py.with_suffix("")
    if pkg.is_dir() and (pkg / "__init__.py").exists():
        print(f"COLLISION: {py} <-> {pkg}/")
PY
```

---

## Expected Outcomes

**Target**: Reduce collection errors from 111 to <102 (50% reduction milestone)

**Success Criteria**:
1. All 39 missing modules have bridges created
2. All 41 import errors resolved with proper exports
3. No new module-package collisions introduced
4. Bridge contract tests pass
5. Collection errors ≤ 102

---

## Implementation Order (Recommended)

### Phase 1: Core Infrastructure (15 modules)
High-impact modules that unblock many tests:
1. `lukhas.consciousness.types` (used by 5+ test files)
2. `core.common` → `GLYPHToken` export
3. `consciousness.systems` → `ConsciousnessState`
4. `lukhas.consciousness.enhanced_thought_engine`
5. `core.consciousness_stream`, `core.consciousness_ticker`
6. `async_manager` → `ConsciousnessTaskManager` export
7. Fix `aka_qualia/__init__.py` structure
8. `governance.guardian_system`
9. `governance.guardian` + `governance.guardian.core`
10. `bridge.api.identity`

### Phase 2: Memory & Observability (13 modules)
Medium-impact modules:
1. `memory.backends`, `memory.folds`, `memory.indexer`
2. `memory.lifecycle`, `memory.memory_event`, `memory.observability`
3. `lukhas.memory.backends`
4. `lukhas.observability.*` (6 modules)

### Phase 3: Tools & Candidate (11 modules)
Lower-impact but required:
1. Convert `tools/` to proper package (remove `lukhas/tools.py`)
2. Create `tools.scripts`, `tools.commands`, `tools.analysis`, `tools.security`, `tools.acceptance_gate_ast`
3. `candidate.rl`, `candidate.trace`, `candidate.ledger`, `candidate.matriz`
4. `candidate.core.matriz`, `candidate.core.symbolic.symbolic_glyph_hash`

### Phase 4: Remaining Core (6 modules)
Final cleanup:
1. `core.business`, `core.breakthrough`, `core.clock`
2. `core.collective.clusters`, `core.consciousness`
3. `core.ethics.logic`

---

## Notes for GPT-5

- **Codebase root**: `/Users/agi_dev/LOCAL-REPOS/Lukhas`
- **Bridge utilities**: `lukhas/_bridgeutils.py` (already exists)
- **Real implementations**: Primarily in `lukhas_website/lukhas/*`
- **Fallback**: `candidate/*` packages
- **Testing**: All bridges must be testable via pytest import

**Do NOT**:
- Create mock implementations
- Use `from X import *` without `bridge_from_candidates()`
- Create placeholder classes
- Guess at symbol names

**DO**:
- Search filesystem for real implementations
- Use `grep -r "class SymbolName"` to find definitions
- Create proper `__init__.py` package files
- Export all symbols via `__all__`
- Document which canonical path you used in each bridge

---

## Output Format Expected

For each module created, provide:
```
### Module: lukhas.consciousness.types

**Location**: lukhas/consciousness/types.py
**Real implementation found**: lukhas_website/lukhas/consciousness/types.py
**Symbols exported**: ConsciousnessState, CreativeTask, CreativitySnapshot, DEFAULT_CREATIVITY_CONFIG

**Bridge code**:
```python
"""Bridge: consciousness.types -> canonical implementations."""
from __future__ import annotations

from lukhas._bridgeutils import bridge_from_candidates

_CANDIDATES = (
    "lukhas_website.lukhas.consciousness.types",
    "candidate.consciousness.types",
)

__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)
```

**Tests affected**: 5 test files now passing collection
```

---

## Ready for GPT-5 Processing

This document contains all information needed to:
1. Identify the 39 missing modules
2. Resolve the 41 import errors
3. Fix special cases (aka_qualia, tools package, syntax errors)
4. Create proper bridges using the explicit-API pattern
5. Verify success with provided commands

**Current state**: 111 collection errors
**Target state**: <102 collection errors (50% reduction achieved)
**Remaining work**: 9 more errors to fix after these modules are created
