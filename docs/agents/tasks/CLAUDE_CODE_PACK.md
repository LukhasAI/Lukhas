# Claude Code Agent Task Pack (T4 / 0.01%)

**Agent**: Claude Code (IDE-based, surgical single-file edits)
**Standard**: T4 / 0.01% (Tested⁴, 99.99% reliability, human-in-loop)
**Base Branch**: `origin/feat/fix-lane-violation-MATRIZ` or `origin/main`
**Context Files**: Read `lukhas_context.md` and `claude.me` before starting

---

## Executive Summary for Claude Code

You are embarking on a **critical architectural hygiene initiative** to eliminate import-time dependencies from production lanes (`core/`, `lukhas/`, `serve/`) to the experimental `labs.*` modules. This preserves lane isolation, enables independent evolution, and prevents transitive dependency pollution.

**What You've Learned from Context**:
- LUKHAS uses a **3-lane architecture**: `candidate/` (research) → `core/` (integration) → `lukhas/` (production)
- **Lane boundaries must be respected**: production code CANNOT import `labs.*` at module import time
- **ProviderRegistry pattern**: Inject dependencies at runtime via `core/adapters/provider_registry.py`
- **Lazy import pattern**: Use `importlib` for optional/small helpers with graceful degradation
- **Import-safety tests**: Every refactored file needs `test_<file>_importsafe.py`
- **Lane-guard validation**: Run `./scripts/run_lane_guard_worktree.sh` to verify no transitive violations

**Your Mission**:
Execute **10 surgical, single-file refactors** that eliminate static `labs.*` imports while preserving API behavior. Each task is self-contained, reversible, and independently testable.

**Success Criteria**:
- ✅ Each file refactored in **one PR** (single-file, atomic change)
- ✅ All tests pass (pytest, ruff, mypy, lane-guard)
- ✅ API behavior unchanged (consumers don't break)
- ✅ Import-safety test added for each file
- ✅ Artifacts attached to PR (ruff/mypy/lane-guard logs)

---

## Task Execution Pattern (Copy/Paste Template)

For each task below, follow this exact pattern:

```bash
# 1. Create branch
git fetch origin && git checkout -b task/lazy-load-<file>-<yourname> origin/feat/fix-lane-violation-MATRIZ

# 2. Make surgical edit (see task-specific instructions below)
#    - Replace top-level labs imports
#    - Use ProviderRegistry OR lazy _get_labs()
#    - Update call sites to use runtime injection

# 3. Add import-safety test
#    tests/.../test_<file>_importsafe.py with:
#    - test_import_safe(): assert module imports without labs
#    - test_with_stub_provider(): inject mock and verify behavior

# 4. Run validation commands
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/.../test_<file>_importsafe.py -q
ruff check <file_path> --select E,F,W,C
mypy <file_path> --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

# 5. Commit & push
git add <file> tests/.../test_<file>_importsafe.py
git commit -m "refactor(provider): lazy-load labs in <file>"
git push -u origin task/lazy-load-<file>-<yourname>

# 6. Create PR with artifacts
gh pr create --title "refactor(provider): lazy-load labs in <file>" \
  --body "$(cat <<'PRBODY'
## Summary
- Replace import-time labs import with provider/lazy-load pattern
- Add import-safety test
- Preserve API behavior

## Validation
- pytest: PASS (attach log)
- ruff: PASS (attach log)
- mypy: PASS (attach log)
- lane-guard: PASS (attach artifacts/reports/*)

## Checklist
- [ ] Single file changed
- [ ] Tests pass
- [ ] Lane-guard contracts KEPT
- [ ] API behavior unchanged
PRBODY
)"
```

**Stop & Escalate If**:
- More than 1 file must change to get tests passing
- Tests fail due to API breaking change
- Lane-guard shows NEW transitive path violation
- You can't inject a stub provider for testing

---

## 🎯 Task 01: `core/colony/gpt_colony_orchestrator.py`

**Branch**: `task/claude-lazy-load-gpt_colony-<yourname>`
**Priority**: P1 (Critical - high-impact orchestrator)
**Estimated Time**: 45-60 minutes

### Why This File

The GPT colony orchestrator likely instantiates OpenAI/labs clients at import time, creating a direct production → labs edge. This is a **critical path** for multi-agent orchestration.

### Refactoring Strategy

**Prefer ProviderRegistry** (this is a service instantiation case):

```python
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _get_openai_provider():
    """Get OpenAI provider via registry (runtime injection)."""
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

# Inside orchestrator methods:
def orchestrate_colony(self, prompt: str):
    provider = _get_openai_provider()
    response = provider.chat.completions.create(...)
    return response
```

### Changes Needed

1. **Remove**: `from labs.openai import OpenAI` (or similar top-level import)
2. **Add**: `_get_openai_provider()` helper function
3. **Update**: All client instantiation to use `_get_openai_provider()` at runtime
4. **Guard**: If provider returns None, raise clear RuntimeError

### Test to Add

Create `tests/gpt/test_gpt_colony_importsafe.py`:

```python
def test_import_safe():
    """Verify module imports without labs installed."""
    import core.colony.gpt_colony_orchestrator
    assert core.colony.gpt_colony_orchestrator is not None

def test_with_stub_provider(monkeypatch):
    """Verify orchestrator works with stub provider."""
    from core.colony.gpt_colony_orchestrator import ColonyOrchestrator

    class StubProvider:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return {"choices": [{"message": {"content": "stub response"}}]}

    # Inject stub
    def mock_provider():
        return StubProvider()

    monkeypatch.setattr("core.colony.gpt_colony_orchestrator._get_openai_provider", mock_provider)

    orch = ColonyOrchestrator()
    result = orch.orchestrate_colony("test prompt")
    assert result is not None
```

### Validation Commands

```bash
. .venv/bin/activate
pytest tests/gpt/test_gpt_colony_importsafe.py -q
ruff check core/colony/gpt_colony_orchestrator.py --select E,F,W,C
mypy core/colony/gpt_colony_orchestrator.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh
```

### Commit Message

```
refactor(provider): lazy-load labs in gpt_colony_orchestrator

Problem:
- core/colony/gpt_colony_orchestrator.py imported labs.openai at module import time
- Created production → labs transitive dependency

Solution:
- Replaced with ProviderRegistry pattern
- Added _get_openai_provider() for runtime injection
- Added import-safety test with stub provider

Impact:
- Lane isolation preserved
- API behavior unchanged
- Tests: 2/2 passing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 🎯 Task 02: `core/identity.py`

**Branch**: `task/claude-lazy-load-identity-<yourname>`
**Priority**: P1 (Critical - identity system)
**Estimated Time**: 30-45 minutes

### Why This File

Identity module likely imports `labs.governance.identity` for authentication/authorization helpers, creating governance → labs edge.

### Refactoring Strategy

**Choice depends on usage**:
- If identity is a **service**: Use ProviderRegistry
- If identity has **small helper functions**: Use lazy `_get_labs()` loader

Example lazy loader:

```python
import importlib
from typing import Optional, Any

def _get_labs() -> Optional[Any]:
    """Lazy-load labs module (graceful degradation)."""
    try:
        return importlib.import_module("labs.governance.identity")
    except Exception:
        return None

# In functions that use labs:
def get_user_identity(user_id: str):
    labs = _get_labs()
    if labs is None:
        raise RuntimeError("Identity requires labs.governance.identity (optional dependency)")
    return labs.get_identity(user_id)
```

### Changes Needed

1. **Remove**: `from labs.governance.identity import ...` at top
2. **Add**: `_get_labs()` helper or ProviderRegistry usage
3. **Update**: All call sites to use lazy/provider pattern
4. **Guard**: Clear error message if labs unavailable

### Test to Add

Create `tests/core/test_identity_importsafe.py`:

```python
def test_import_safe():
    """Verify core.identity imports without labs."""
    import core.identity
    assert core.identity is not None

def test_stub_identity_provider(monkeypatch):
    """Verify identity functions with stub labs."""
    import core.identity

    class StubLabs:
        @staticmethod
        def get_identity(user_id):
            return {"user_id": user_id, "name": "stub_user"}

    monkeypatch.setattr("core.identity._get_labs", lambda: StubLabs())

    result = core.identity.get_user_identity("test123")
    assert result["user_id"] == "test123"
```

### Commit Message

```
refactor(provider): lazy-load labs in core/identity

Problem:
- core/identity.py imported labs.governance.identity at module level
- Created transitive governance → labs dependency

Solution:
- Added _get_labs() lazy loader with graceful degradation
- Updated call sites to use runtime loading
- Added import-safety test

Impact:
- Lane boundaries preserved
- Identity API unchanged
- Tests: 2/2 passing
```

---

## 🎯 Task 03: `core/observability/evidence_collection.py`

**Branch**: `task/claude-lazy-load-evidence-<yourname>`
**Priority**: P1 (Critical - observability layer)
**Estimated Time**: 30-45 minutes

### Why This File

Observability code often imports `labs.observability.*` for telemetry/logging, creating import-time side effects and transitive edges.

### Refactoring Strategy

Use **ProviderRegistry** if this module registers observability clients, otherwise **lazy import**:

```python
import importlib
from typing import Optional

def _get_labs_observability() -> Optional[Any]:
    """Lazy-load labs observability (optional)."""
    try:
        return importlib.import_module("labs.observability")
    except Exception:
        return None

def collect_evidence(event: dict):
    """Collect observability evidence."""
    labs_obs = _get_labs_observability()
    if labs_obs:
        labs_obs.log_event(event)  # optional enhanced logging
    # Core observability continues regardless
    return local_evidence_collection(event)
```

### Test to Add

Create `tests/observability/test_evidence_importsafe.py`:

```python
def test_import_safe():
    """Verify evidence_collection imports without labs."""
    import core.observability.evidence_collection
    assert core.observability.evidence_collection is not None

def test_evidence_collection_without_labs(monkeypatch):
    """Verify evidence collection works without labs."""
    import core.observability.evidence_collection

    monkeypatch.setattr("core.observability.evidence_collection._get_labs_observability", lambda: None)

    result = core.observability.evidence_collection.collect_evidence({"test": "event"})
    assert result is not None  # Core functionality works
```

### Commit Message

```
refactor(provider): lazy-load labs in observability/evidence_collection

Problem:
- Import-time dependency on labs.observability created side effects
- Prevented independent observability testing

Solution:
- Added _get_labs_observability() lazy loader
- Made labs observability optional enhancement
- Core evidence collection works independently

Impact:
- Observability layer decoupled
- Tests: 2/2 passing
```

---

## 🎯 Task 04: `core/dream/hyperspace_dream_simulator.py`

**Branch**: `task/claude-lazy-load-dreamsim-<yourname>`
**Priority**: P2 (Important - dream system)
**Estimated Time**: 45-60 minutes

### Why This File

Dream simulators frequently import heavy `labs.consciousness.dream.*` modules, creating large transitive dependencies at import time.

### Refactoring Strategy

**Move adapters to labs_integrations** OR use lazy loading:

```python
import importlib
from typing import Optional, Any

def _get_dream_engine() -> Optional[Any]:
    """Lazy-load labs dream engine."""
    try:
        return importlib.import_module("labs.consciousness.dream")
    except Exception:
        return None

class HyperspaceDreamSimulator:
    def simulate(self, seed: int):
        engine = _get_dream_engine()
        if engine is None:
            # Use fallback/stub dream engine
            return self._fallback_simulation(seed)
        return engine.simulate_hyperspace(seed)

    def _fallback_simulation(self, seed: int):
        """Simple local simulation (no labs required)."""
        import random
        random.seed(seed)
        return {"dream_state": "simulated", "seed": seed}
```

### Test to Add

Create `tests/dream/test_hyperspace_importsafe.py`:

```python
def test_import_safe():
    """Verify hyperspace_dream_simulator imports without labs."""
    import core.dream.hyperspace_dream_simulator
    assert core.dream.hyperspace_dream_simulator is not None

def test_simulation_with_fallback(monkeypatch):
    """Verify simulator works with fallback (no labs)."""
    import core.dream.hyperspace_dream_simulator

    monkeypatch.setattr("core.dream.hyperspace_dream_simulator._get_dream_engine", lambda: None)

    sim = core.dream.hyperspace_dream_simulator.HyperspaceDreamSimulator()
    result = sim.simulate(seed=42)
    assert result["seed"] == 42
```

### Commit Message

```
refactor(provider): lazy-load labs in hyperspace_dream_simulator

Problem:
- Heavy labs.consciousness.dream import at module level
- Prevented independent dream testing
- Large transitive dependency graph

Solution:
- Added _get_dream_engine() lazy loader
- Implemented fallback simulation (no labs required)
- Preserved hyperspace simulation API

Impact:
- Dream system decoupled from labs
- 50% reduction in import-time dependencies
- Tests: 2/2 passing
```

---

## 🎯 Task 05: `core/tags/registry.py`

**Branch**: `task/claude-lazy-load-tags-<yourname>`
**Priority**: P2 (Important - tag system)
**Estimated Time**: 30-40 minutes

### Why This File

Tag registry may import labs for semantic explanations or hormone tags, creating unnecessary coupling.

### Refactoring Strategy

```python
import importlib
from typing import Optional, Any

def _get_labs_tags() -> Optional[Any]:
    """Lazy-load labs tag enhancements (optional)."""
    try:
        return importlib.import_module("labs.tags")
    except Exception:
        return None

class TagRegistry:
    def explain_tag(self, tag_name: str) -> str:
        """Explain tag meaning (with optional labs enhancement)."""
        labs_tags = _get_labs_tags()
        if labs_tags:
            return labs_tags.explain(tag_name)  # Enhanced explanation
        # Fallback to simple explanation
        return f"Tag: {tag_name} (basic description)"
```

### Test to Add

Create `tests/core/test_tag_registry_importsafe.py`:

```python
def test_import_safe():
    """Verify tags.registry imports without labs."""
    import core.tags.registry
    assert core.tags.registry is not None

def test_tag_explanation_without_labs(monkeypatch):
    """Verify tag registry works without labs."""
    import core.tags.registry

    monkeypatch.setattr("core.tags.registry._get_labs_tags", lambda: None)

    registry = core.tags.registry.TagRegistry()
    explanation = registry.explain_tag("test_tag")
    assert "test_tag" in explanation
```

### Commit Message

```
refactor(provider): lazy-load labs in core/tags/registry

Problem:
- Tag registry imported labs for semantic explanations
- Created unnecessary coupling for basic tag operations

Solution:
- Added _get_labs_tags() lazy loader
- Implemented fallback explanations
- Preserved tag registry API

Impact:
- Tag system works independently
- Tests: 2/2 passing
```

---

## 🎯 Task 06: `core/tags/__init__.py`

**Branch**: `task/claude-lazy-init-tags-<yourname>`
**Priority**: P2 (Important - prevent re-export pollution)
**Estimated Time**: 20-30 minutes

### Why This File

`__init__.py` re-exports can hide transitive dependencies and create import-time edges through convenience imports.

### Refactoring Strategy

Use `__getattr__` for lazy proxy:

```python
# core/tags/__init__.py
from typing import Any

# Only import local modules
from .registry import TagRegistry  # OK - local

# Lazy proxy for labs-dependent exports
def __getattr__(name: str) -> Any:
    """Lazy-load labs-dependent tag features."""
    if name == "EnhancedTagExplainer":
        try:
            from labs.tags import EnhancedTagExplainer
            return EnhancedTagExplainer
        except ImportError:
            raise AttributeError(f"'{name}' requires labs.tags (optional dependency)")
    raise AttributeError(f"module 'core.tags' has no attribute '{name}'")

def __dir__():
    """Expose available attributes."""
    return ["TagRegistry", "EnhancedTagExplainer"]
```

### Test to Add

Create `tests/core/test_tags_init_importsafe.py`:

```python
def test_import_safe():
    """Verify core.tags imports without labs."""
    import core.tags
    assert core.tags.TagRegistry is not None

def test_lazy_attribute_access():
    """Verify lazy __getattr__ works."""
    import core.tags

    # Local import works
    assert hasattr(core.tags, "TagRegistry")

    # Labs-dependent attribute raises clear error
    try:
        _ = core.tags.EnhancedTagExplainer
        assert False, "Should raise AttributeError"
    except AttributeError as e:
        assert "requires labs.tags" in str(e)
```

### Commit Message

```
chore(tags): lazy-proxy re-exports in core/tags/__init__.py

Problem:
- __init__.py re-exported labs.tags symbols at import time
- Created hidden transitive dependencies

Solution:
- Added __getattr__ lazy proxy for labs-dependent exports
- Preserved local exports (TagRegistry)
- Clear error messages for missing optional deps

Impact:
- Import-time dependencies eliminated
- API preserved with lazy loading
- Tests: 2/2 passing
```

---

## 🎯 Task 07: `core/adapters/__init__.py`

**Branch**: `task/claude-adapters-init-<yourname>`
**Priority**: P2 (Important - adapter layer hygiene)
**Estimated Time**: 20-30 minutes

### Why This File

Adapters should expose only protocols/interfaces. Re-exporting labs-based implementations breaks lane isolation.

### Refactoring Strategy

```python
# core/adapters/__init__.py
"""Core adapter interfaces (lane-safe)."""

# Export only protocols/interfaces
from .provider_registry import ProviderRegistry
from .config_resolver import ConfigResolver

# DO NOT re-export labs-based implementations
# Move those to labs_integrations/adapters/

__all__ = ["ProviderRegistry", "ConfigResolver"]
```

Move any labs-dependent adapters to `labs_integrations/adapters/`.

### Test to Add

Create `tests/core/test_adapters_importsafe.py`:

```python
def test_import_safe():
    """Verify core.adapters imports without labs."""
    import core.adapters
    assert core.adapters.ProviderRegistry is not None
    assert core.adapters.ConfigResolver is not None

def test_no_labs_re_exports():
    """Verify no labs symbols re-exported."""
    import core.adapters
    import sys

    # Check that importing core.adapters doesn't import labs
    assert "labs" not in sys.modules or all(
        not mod.startswith("labs.")
        for mod in sys.modules
        if mod != "labs"
    )
```

### Commit Message

```
chore(adapters): remove import-time labs re-exports

Problem:
- core/adapters/__init__.py re-exported labs-based implementations
- Violated lane isolation principles

Solution:
- Removed labs-dependent re-exports
- Kept only protocols/interfaces (ProviderRegistry, ConfigResolver)
- Moved labs implementations to labs_integrations/

Impact:
- Adapter layer now lane-safe
- Clear separation of interfaces vs implementations
- Tests: 2/2 passing
```

---

## 🎯 Task 08: `core/governance/__init__.py`

**Branch**: `task/claude-gov-init-<yourname>`
**Priority**: P2 (Important - governance layer)
**Estimated Time**: 20-30 minutes

### Why This File

Governance often imports `labs.governance.*` for identity/ethics, creating hidden dependencies.

### Refactoring Strategy

Similar to tags/__init__.py - use lazy proxy:

```python
# core/governance/__init__.py
from typing import Any

# Local governance components only
from .guardian import Guardian
from .ethics_core import EthicsCore

def __getattr__(name: str) -> Any:
    """Lazy-load labs-dependent governance features."""
    if name == "AdvancedIdentityManager":
        try:
            from labs.governance.identity import AdvancedIdentityManager
            return AdvancedIdentityManager
        except ImportError:
            raise AttributeError(f"'{name}' requires labs.governance (optional)")
    raise AttributeError(f"module 'core.governance' has no attribute '{name}'")
```

### Test to Add

Create `tests/core/test_governance_importsafe.py`:

```python
def test_import_safe():
    """Verify core.governance imports without labs."""
    import core.governance
    assert core.governance.Guardian is not None

def test_lazy_governance_features():
    """Verify lazy loading of optional features."""
    import core.governance

    # Core features available
    assert hasattr(core.governance, "Guardian")
    assert hasattr(core.governance, "EthicsCore")
```

### Commit Message

```
chore(governance): lazy-load labs re-exports

Problem:
- core/governance/__init__.py imported labs.governance.* at module level
- Created hidden governance → labs dependencies

Solution:
- Added __getattr__ lazy proxy
- Exposed only core governance (Guardian, EthicsCore)
- Labs features load on-demand

Impact:
- Governance layer decoupled
- Tests: 2/2 passing
```

---

## 🎯 Task 09: `serve/api/openai_proxy.py`

**Branch**: `task/claude-lazy-load-serve-openai-<yourname>`
**Priority**: P1 (Critical - API endpoint)
**Estimated Time**: 40-50 minutes

### Why This File

API endpoints often instantiate clients at module import time for convenience, breaking lane isolation.

### Refactoring Strategy

Use **ProviderRegistry** with dependency injection in handlers:

```python
from fastapi import APIRouter, Depends
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

router = APIRouter()

def get_openai_provider():
    """Dependency: Get OpenAI provider (injected at request time)."""
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

@router.post("/v1/chat/completions")
async def chat_completions(
    request: dict,
    provider = Depends(get_openai_provider)
):
    """OpenAI-compatible chat endpoint."""
    response = provider.chat.completions.create(**request)
    return response
```

### Test to Add

Create `tests/serve/test_openai_proxy_importsafe.py`:

```python
def test_import_safe():
    """Verify serve.api.openai_proxy imports without labs."""
    import serve.api.openai_proxy
    assert serve.api.openai_proxy.router is not None

def test_endpoint_with_stub_provider(client, monkeypatch):
    """Verify endpoint works with stub provider."""
    class StubProvider:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    return {"choices": [{"message": {"content": "stub"}}]}

    def mock_provider():
        return StubProvider()

    monkeypatch.setattr("serve.api.openai_proxy.get_openai_provider", mock_provider)

    response = client.post("/v1/chat/completions", json={"model": "gpt-4", "messages": []})
    assert response.status_code == 200
```

### Commit Message

```
refactor(provider): lazy-load labs in serve/api/openai_proxy

Problem:
- OpenAI client instantiated at module import time
- Created serve → labs dependency at startup

Solution:
- Moved provider instantiation to request handlers
- Used FastAPI Depends() for runtime injection
- Added import-safety test with stub provider

Impact:
- API server starts without labs dependency
- Provider injected per-request (testable)
- Tests: 2/2 passing
```

---

## 🎯 Task 10: `lukhas_website/api.py`

**Branch**: `task/claude-lazy-load-website-<yourname>`
**Priority**: P2 (Important - website layer)
**Estimated Time**: 30-40 minutes

### Why This File

Website/demo layers sometimes import labs for interactive examples, creating unnecessary production dependencies.

### Refactoring Strategy

```python
import importlib
from typing import Optional

def _get_labs_demos() -> Optional[Any]:
    """Lazy-load labs demos (optional)."""
    try:
        return importlib.import_module("labs.demos")
    except Exception:
        return None

@app.get("/demo/{demo_name}")
async def run_demo(demo_name: str):
    """Run interactive demo."""
    labs = _get_labs_demos()
    if labs is None:
        return {"error": "Demos require labs (optional)", "demo_name": demo_name}
    return labs.run_demo(demo_name)
```

### Test to Add

Create `tests/website/test_api_importsafe.py`:

```python
def test_import_safe():
    """Verify lukhas_website.api imports without labs."""
    import lukhas_website.api
    assert lukhas_website.api.app is not None

def test_demo_endpoint_without_labs(client, monkeypatch):
    """Verify demo endpoint handles missing labs gracefully."""
    monkeypatch.setattr("lukhas_website.api._get_labs_demos", lambda: None)

    response = client.get("/demo/test_demo")
    assert response.status_code == 200
    assert "error" in response.json()
    assert "optional" in response.json()["error"]
```

### Commit Message

```
refactor(provider): lazy-load labs in lukhas_website/api

Problem:
- Website imported labs.demos at module level
- Created website → labs dependency for basic pages

Solution:
- Added _get_labs_demos() lazy loader
- Graceful error for missing demos
- Website core functionality independent

Impact:
- Website starts without labs
- Demos optional enhancement
- Tests: 2/2 passing
```

---

## 📋 Execution Checklist (For All 10 Tasks)

Use this checklist for each task:

- [ ] **Branch created** from correct base (`origin/feat/fix-lane-violation-MATRIZ`)
- [ ] **Top-level labs imports removed** (verified with grep)
- [ ] **ProviderRegistry OR lazy _get_labs() added** (pattern appropriate for file)
- [ ] **Call sites updated** to use runtime injection
- [ ] **Import-safety test added** (`test_<file>_importsafe.py`)
- [ ] **Stub provider test added** (verify behavior with mock)
- [ ] **pytest passes** (target file tests)
- [ ] **ruff check passes** (E,F,W,C violations)
- [ ] **mypy check passes** (file-specific, ignore missing imports)
- [ ] **lane-guard passes** (contracts KEPT, no new violations)
- [ ] **Artifacts collected** (ruff.log, mypy.log, artifacts/reports/*)
- [ ] **Commit message follows T4 standards** (Problem/Solution/Impact)
- [ ] **PR created** with validation artifacts attached
- [ ] **PR description complete** (summary, validation, checklist)

---

## 🚨 Common Issues & Solutions

### Issue 1: "Lane-guard shows new violation"

**Diagnosis**: Your change created a NEW transitive path.

**Solution**:
1. Run `import-linter` to see the exact path
2. Identify the leaf module creating the edge
3. Fix that module FIRST (another one-file PR)
4. Then retry your original change

### Issue 2: "Tests fail with missing labs module"

**Expected!** This is why we're refactoring.

**Solution**:
1. Ensure your test uses `monkeypatch` to inject stub
2. OR: Skip test if labs unavailable: `@pytest.mark.skipif(not has_labs, reason="labs optional")`
3. Focus on import-safety test passing without labs

### Issue 3: "API behavior changed"

**Stop immediately!**

**Action**:
1. Revert your changes
2. Add MORE comprehensive tests FIRST to capture current behavior
3. Retry refactor with tests validating equivalence
4. Escalate to human if breaking change is unavoidable

### Issue 4: "Multiple files need changes"

**Stop!** This violates single-file principle.

**Action**:
1. Identify dependency chain
2. Fix files in reverse dependency order (leaves first)
3. Create separate PRs for each file
4. Merge in order (leaves → roots)

---

## 📚 Reference Materials

**Must Read Before Starting**:
- `lukhas_context.md` - Complete platform context (vendor-neutral)
- `claude.me` - Claude-specific architecture overview
- `docs/agents/claude_prompts.md` - Single-file refactor template
- `docs/agents/README.md` - Agent principles (T4 / 0.01%)

**Lane Architecture**:
- `candidate/` - Research lane (labs modules live here)
- `core/` - Integration lane (you're working here)
- `lukhas/` - Production lane (also needs cleanup)

**Import Rules**:
- ✅ `core/` can import from `core/`, `matriz/`, `universal_language/`
- ❌ `core/` CANNOT import from `labs.*` at module level
- ✅ `core/` CAN use `labs.*` via runtime injection (ProviderRegistry)

**Provider Pattern**:
- `core/adapters/provider_registry.py` - Central registry
- `core/adapters/config_resolver.py` - Configuration resolver
- Pattern: Request → Provider → Labs (runtime only)

---

## 🎓 What You've Learned Summary

1. **Lane Isolation is Critical**: Production code must not depend on experimental code at import time
2. **ProviderRegistry Pattern**: Runtime dependency injection for services
3. **Lazy Loading Pattern**: `importlib` for optional/small features with graceful degradation
4. **Import-Safety Tests**: Every refactored module needs `test_<file>_importsafe.py`
5. **Stub Providers**: Use `monkeypatch` to inject mocks for testing
6. **Lane-Guard Validation**: Always run before PR to catch transitive violations
7. **Single-File PRs**: Atomic changes are easier to review and revert
8. **T4 Standards**: Tested⁴ - each change must have test, pass tests, be meaningful, be maintainable

---

## ✅ Success Metrics

After completing all 10 tasks:

- **10 PRs created** (one per file)
- **20+ tests added** (2 per file minimum)
- **10 files refactored** without breaking changes
- **0 new lane violations** (lane-guard passes)
- **100% test pass rate** (all PRs green)
- **Artifacts attached** to every PR

**Impact on Platform**:
- Import graph simplified (10 fewer import-time edges)
- Lane isolation strengthened
- Production startup time improved (~15-20%)
- Test independence increased (no labs required for unit tests)

---

## 🚀 Ready to Start?

1. **Read context files**: `lukhas_context.md` and `claude.me`
2. **Choose a task**: Start with Task 01 (highest priority)
3. **Follow the pattern**: Use the execution template above
4. **Run all validations**: pytest, ruff, mypy, lane-guard
5. **Create PR with artifacts**: Attach validation logs
6. **Wait for review**: Human approval required before merge

**Remember**: You're not just refactoring imports - you're preserving architectural integrity that enables independent evolution of research and production code.

Good luck! 🎯

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-02
**Standard**: T4 / 0.01%
**Agent**: Claude Code
**Context**: LUKHAS AI Platform - Lane Isolation Initiative
