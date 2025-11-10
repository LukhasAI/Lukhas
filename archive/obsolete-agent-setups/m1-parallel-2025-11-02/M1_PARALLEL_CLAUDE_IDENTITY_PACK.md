# M1 Parallel Claude Code Pack - Core Identity Refactoring

**Target**: M1 Branch Laptop (Secondary Claude Work)  
**Branch**: `task/claude-lazy-load-identity-M1`  
**File**: `core/identity.py`  
**Timeline**: 30 minutes  
**Safety Level**: T4-Safe (single file, reversible)

---

## 🎯 Mission Overview

Replace import-time `labs` usage in `core/identity.py` with ProviderRegistry or lazy loader. Add import-safety test. Keep changes minimal and surgical.

## ⚡ Quick Start Commands

```bash
# Setup branch
git fetch origin
git checkout -B task/claude-lazy-load-identity-M1 origin/M1

# After Claude edits, run validations
. .venv/bin/activate
pip install ruff mypy pytest || true
python -m py_compile core/identity.py
ruff check core/identity.py --select E,F,W,C > artifacts/reports/ruff_identity.txt 2>&1 || true
mypy core/identity.py --ignore-missing-imports > artifacts/reports/mypy_identity.txt 2>&1 || true
pytest tests/core/test_identity_importsafe.py -q > artifacts/reports/pytest_identity.txt 2>&1 || true
./scripts/run_lane_guard_worktree.sh > artifacts/reports/lane_guard_identity.log 2>&1 || true

# Commit and push
git add core/identity.py tests/core/test_identity_importsafe.py
git commit -m "refactor(provider): lazy-load labs in core/identity (M1)"
git push -u origin task/claude-lazy-load-identity-M1
```

## 🤖 Claude Code Agent Prompt

````
Task: Make `core/identity.py` import-safe (M1 laptop).

Base branch: origin/M1. Create branch:
  git fetch origin
  git checkout -B task/claude-lazy-load-identity-M1 origin/M1

Goal:
- Remove any top-level `from labs... import ...` or `import labs` in core/identity.py
- Prefer ProviderRegistry pattern if the module constructs a service client
- If the file is only helper functions, use lazy `_get_labs()` helper
- Add a small import-safety unit test
- Keep changes minimal and reversible (one-file PR)

Preferred Provider pattern (if module creates a client/service):
```py
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver
from typing import Any

def _get_openai_provider() -> Any:
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()
```

Use this provider inside runtime functions only; **do not** instantiate at module import-time.

Fallback lazy helper (for small helpers):
```py
import importlib
from typing import Optional, Any

def _get_labs() -> Optional[Any]:
    try:
        return importlib.import_module("labs")
    except Exception:
        return None
```

Then inside functions:
```py
_labs = _get_labs()
if _labs is None:
    raise RuntimeError("labs integration not available")
_labs.governance.identity.some_fn(...)
```

Tests (add file `tests/core/test_identity_importsafe.py`):
```py
def test_import_safe():
    # import-only test: module import must not trigger labs import-time
    import importlib
    importlib.import_module("core.identity")

def test_stub_provider_behavior(monkeypatch):
    # if core.identity exposes a function that uses a provider, stub it
    class StubProvider:
        def do_identity(self, *a, **k):
            return {"id": "stub"}
    from core.identity import some_runtime_function  # replace with actual function name
    # monkeypatch or pass provider if API allows
    # Example: some_runtime_function(provider=StubProvider())
    # Assert correct behavior:
    # assert some_runtime_function(provider=StubProvider()) == expected
```

Stop & ask for human review if:
- The agent must change >1 file to make code compile or tests pass
- The change requires altering public APIs  
- Lane-guard shows a transitive path to `labs` (post-change)

Make the edits minimal and comment any TODOs (e.g., migrate to ProviderRegistry) in the file header.
````

## 📝 PR Template

```
Title: refactor(provider): lazy-load labs in core/identity (M1)

Summary:
- Replace import-time labs usage with ProviderRegistry / lazy-load helper
- Add tests: tests/core/test_identity_importsafe.py (import-safety + stubbed behavior)

Validation:
- ruff (file) attached: artifacts/reports/ruff_identity.txt
- mypy (file) attached: artifacts/reports/mypy_identity.txt  
- pytest attached: artifacts/reports/pytest_identity.txt
- lane-guard run attached: artifacts/reports/lane_guard_identity.log

Checklist:
- [ ] Import-safety test passes
- [ ] ruff checked for changed file
- [ ] mypy file-level OK (no hard errors)
- [ ] lane-guard: Contracts KEPT (or explanation)
```

## 🛡️ Safety Guardrails

- ✅ Single file change only
- ✅ Minimal, reversible edits
- ✅ Import-safety test required
- ✅ Validation artifacts attached
- ✅ Human review for any complications

## 🔄 Validation Requirements

1. **Syntax Check**: `python -m py_compile core/identity.py`
2. **Linting**: `ruff check` with E,F,W,C selectors
3. **Type Check**: `mypy` with ignore-missing-imports
4. **Tests**: `pytest` for import-safety test
5. **Lane Guard**: Import contract validation

## 📋 Coordination

- **File Lock**: Add `core/identity.py` to run-lock while PR open
- **PR Label**: `agent:claude-M1`
- **Conflict Avoidance**: Main laptop should avoid this file
- **Human Escalation**: If lane-guard shows labs chain, escalate immediately

---

**Status**: Ready for Claude Code execution  
**Next**: Run prompt → Validate → Create PR → Coordinate with main machine