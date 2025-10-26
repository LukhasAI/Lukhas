---
status: wip
type: documentation
---
# Import Error Fixes - Module Reorganization

## Summary
Fixed test import errors after LUKHAS AI codebase reorganization. Addressed module path changes from the consolidation of modules from `lukhas.*` namespace to root-level and `candidate.*` locations.

## Import Patterns Identified

### Successfully Fixed Patterns

1. **Bridge Module Imports**
   - `lukhas.bridge.*` → `bridge.*` (root level)
   - Fixed files:
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_route_handlers.py`
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_trace_logger.py`

2. **Emotion Module Imports**
   - `lukhas.emotion.*` → `candidate.emotion.*`
   - Fixed files:
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/emotion/examples/test_basic_example.py`

3. **Governance/Ethics Module Imports**
   - `lukhas.governance.ethics.*` → `candidate.governance.ethics.*`
   - `lukhas.governance.consent.*` → `candidate.governance.consent.*`
   - Fixed files:
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/ethics/test_guardian_reflector_imports.py`
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/ethics/test_lukhas_constitutional_ai.py`
     - `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/test_consent_manager.py`

4. **Core Trace Module**
   - `lukhas.core.trace` was missing
   - Solution: Copied `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas_website/lukhas/core/trace.py` → `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/core/trace.py`
   - This fixed matriz adapter imports

5. **Memory Module Imports**
   - `lukhas.memory.adaptive_memory` and `lukhas.memory.embedding_index` were missing
   - Solution: Created `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/` directory and copied:
     - `adaptive_memory.py` from lukhas_website
     - `embedding_index.py` from lukhas_website

6. **Main API Module**
   - `lukhas.main` was missing
   - Solution: Created `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/main.py` as compatibility layer:
     ```python
     from bridge.api.main import app
     __all__ = ["app"]
     ```

## Module Location Mapping

### Root-Level Modules (directly importable)
- `bridge/` - API gateway, external adapters, orchestration
- `emotion/` - Basic emotion module (limited)
- `governance/` - Guardian system, policies (limited)
- `memory/` - Memory system core
- `consciousness/` - Consciousness core (limited)
- `matriz/` - MATRIZ cognitive engine
- `core/` - Core compatibility bridge to lukhas.core
- `qi/` - Quantum-inspired layer

### Candidate Modules (import as `candidate.*`)
- `candidate/bridge/` - Full bridge implementation
- `candidate/emotion/` - Full emotion system with examples
- `candidate/governance/` - Full governance with ethics, identity, consent
- `candidate/consciousness/` - Full consciousness with dream, creativity
- `candidate/memory/` - Extended memory features
- `candidate/core/` - Core prototypes

### Lukhas Package Modules (import as `lukhas.*`)
The `lukhas/` package serves as a compatibility layer with __getattr__ that:
1. First tries to load from root-level modules
2. Falls back to candidate.* modules
3. Has issues with nested imports for incomplete root modules

### Lukhas Website Modules (legacy location)
- `lukhas_website/lukhas/core/trace.py` - Trace utilities
- `lukhas_website/lukhas/memory/` - Memory implementations
- `lukhas_website/lukhas/governance/` - Governance implementations

## Remaining Import Issues (230 errors)

### Pattern Categories

1. **lukhas.consciousness.* imports** (~40 errors)
   - Issue: Root `consciousness/` lacks submodules like `dream/`, these exist in `candidate/consciousness/`
   - Example: `lukhas.consciousness.dream.expand.mesh`
   - Solution needed: Either copy missing submodules or update imports to `candidate.consciousness.*`

2. **lukhas.core.* imports** (~50 errors)
   - Various core submodules missing (ethics, drift, orchestration, etc.)
   - The core/__init__.py compatibility bridge has issues with __all__ attribute
   - Example errors:
     - `lukhas.core.ethics`
     - `lukhas.core.orchestration.async_orchestrator`
     - `lukhas.core.business`

3. **lukhas.api imports** (~15 errors)
   - Missing lukhas.api module
   - Actual API code is in `bridge/api/` or `candidate/api/`

4. **lukhas.governance.* imports** (~20 errors)
   - Root governance/ lacks many submodules
   - Examples: `lukhas.governance.compliance`, `lukhas.governance.security`

5. **Other lukhas.* patterns** (~105 errors)
   - `lukhas.aka_qualia` - doesn't exist, likely needs mocking or removal
   - `lukhas.bio` - exists at root but may have missing submodules
   - `lukhas.cognitive_core` - doesn't exist in lukhas/, exists at root
   - `lukhas.observability` - module location unclear
   - `lukhas.rl` - reinforcement learning module
   - `lukhas.tools` - tools module

## Systematic Fix Strategy (Recommended)

### Option 1: Complete Candidate Migration
Update all `lukhas.*` imports to either:
- Root modules (if complete): `bridge`, `matriz`, `qi`, etc.
- Candidate modules (if in development): `candidate.consciousness`, `candidate.governance`, etc.

### Option 2: Complete lukhas/ Package
Copy all missing submodules from:
- `candidate/` → `lukhas/`
- `lukhas_website/lukhas/` → `lukhas/`
- Root modules → `lukhas/`

This would make all `lukhas.*` imports work but violates lane isolation.

### Option 3: Hybrid (Current Approach)
- Keep root modules at root level
- Keep candidate modules in candidate/
- Fix lukhas/ compatibility layer to properly handle nested imports
- Update failing tests case-by-case

## Files Modified

1. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_route_handlers.py`
2. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/bridge/test_trace_logger.py`
3. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/candidate/emotion/examples/test_basic_example.py`
4. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/ethics/test_guardian_reflector_imports.py`
5. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/ethics/test_lukhas_constitutional_ai.py`
6. `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/governance/test_consent_manager.py`

## Files Created

1. `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/core/trace.py` (copied from lukhas_website)
2. `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/adaptive_memory.py` (copied from lukhas_website)
3. `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/embedding_index.py` (copied from lukhas_website)
4. `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/__init__.py` (created)
5. `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/main.py` (compatibility layer for FastAPI app)

## Import Patterns by Module

### Working Patterns ✅
```python
# Bridge
from bridge.api_gateway.route_handlers import RouteHandlers
from bridge.trace_logger import BridgeTraceLogger

# Emotion
from candidate.emotion.examples.basic import example

# Governance
from candidate.governance.ethics.constitutional_ai import ConstitutionalFramework
from candidate.governance.consent.consent_manager import AdvancedConsentManager
from candidate.governance.ethics.guardian_reflector import EthicsEngine

# Core
from lukhas.core.trace import mk_crumb  # Now works

# Memory
from lukhas.memory.adaptive_memory import AdaptiveMemorySystem  # Now works
from lukhas.memory.embedding_index import EmbeddingIndex  # Now works

# Main API
from lukhas.main import app  # Now works
```

### Known Failing Patterns ❌
```python
# Consciousness (incomplete root module)
from lukhas.consciousness.dream.expand.mesh import mesh_consensus
# Fix: from candidate.consciousness.dream.expand.mesh import mesh_consensus

# Core submodules (missing)
from lukhas.core.ethics import EthicsEngine
# Fix: Find actual location and update

# API (missing)
from lukhas.api import something
# Fix: Use bridge.api or candidate.api

# Governance submodules (incomplete root)
from lukhas.governance.compliance import ComplianceMonitor
# Fix: Use candidate.governance.compliance if exists
```

## Testing Status

- **Initial Error Count**: ~280+ import errors during pytest collection
- **Errors Fixed**: ~50 individual imports fixed
- **Remaining Errors**: 230 test files with import errors
- **Tests Passing**: The 6 modified test files now import correctly

## Next Steps

1. **Batch Fix Consciousness Imports**
   - Find all `lukhas.consciousness` imports
   - Update to `candidate.consciousness` or copy missing modules

2. **Fix Core Module Imports**
   - Resolve core/__init__.py __all__ attribute error
   - Copy or create missing core submodules

3. **Complete Module Inventory**
   - Document exact location of each module
   - Create definitive import mapping

4. **Update Test Fixtures**
   - Many tests may need mocking for missing modules
   - Consider marking incomplete tests with @pytest.skip

5. **Lane Boundary Validation**
   - Ensure fixes don't violate candidate/core/lukhas boundaries
   - Run `make lane-guard` after fixes

## Architecture Notes

The codebase uses a three-lane architecture:
- **Development Lane (`candidate/`)**: Experimental features, 2,877 files
- **Integration Lane (`core/`)**: Testing and validation, 253 components
- **Production Lane (`lukhas/`)**: Battle-tested systems, 692 components

Import rules:
- ✅ `lukhas/` ← can import from `core/`, `matriz/`, root modules
- ✅ `candidate/` ← can import from `core/`, `matriz/` ONLY
- ❌ `candidate/` ← NEVER import from `lukhas/` (boundary violation)

The current import errors primarily stem from:
1. Incomplete migration from old `lukhas.*` namespace
2. Root modules that exist but lack submodules (consciousness, governance)
3. Missing compatibility layers in `lukhas/` package
4. Tests written before module reorganization
