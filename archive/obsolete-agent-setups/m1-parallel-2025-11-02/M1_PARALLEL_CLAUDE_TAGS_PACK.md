# M1 Parallel Claude Code Pack - Core Tags Init

**Target**: M1 Branch Laptop (Secondary Claude Work)  
**Branch**: `task/claude-lazy-init-tags-M1`  
**File**: `core/tags/__init__.py`  
**Timeline**: 30 minutes  
**Safety Level**: T4-Safe (single file, interim pattern)

---

## 🎯 Mission Overview

Replace `from labs... import *` re-exports in `core/tags/__init__.py` with lazy `__getattr__`/`__dir__` proxy. Ensure package import doesn't trigger labs import-time. This is an interim safety pattern.

## ⚡ Quick Start Commands

```bash
# Setup branch
git fetch origin
git checkout -B task/claude-lazy-init-tags-M1 origin/M1

# After Claude edits, run validations
. .venv/bin/activate
pip install ruff mypy pytest || true
python -m py_compile core/tags/__init__.py
ruff check core/tags/__init__.py --select E,F,W,C > artifacts/reports/ruff_tags_init.txt 2>&1 || true
mypy core/tags/__init__.py --ignore-missing-imports > artifacts/reports/mypy_tags_init.txt 2>&1 || true
pytest tests/core/test_tags_init_importsafe.py -q > artifacts/reports/pytest_tags_init.txt 2>&1 || true
./scripts/run_lane_guard_worktree.sh > artifacts/reports/lane_guard_tags_init.log 2>&1 || true

# Commit and push
git add core/tags/__init__.py tests/core/test_tags_init_importsafe.py
git commit -m "chore(tags): lazy-proxy re-exports in core/tags/__init__.py (M1)"
git push -u origin task/claude-lazy-init-tags-M1
```

## 🤖 Claude Code Agent Prompt

```
Task: Make `core/tags/__init__.py` import-safe (M1 laptop).

Base branch: origin/M1. Create branch:
git fetch origin
git checkout -B task/claude-lazy-init-tags-M1 origin/M1

Goal:
- If `core/tags/__init__.py` re-exports `labs.*` (e.g., `from labs.foo import *`), remove the re-export and implement a lazy proxy using `__getattr__` and `__dir__` that imports labs symbols on attribute access
- This is an **interim** safety change; add a TODO to migrate to ProviderRegistry as future improvement
- Ensure package import (`import core.tags`) does not import `labs` at module import time

Recommended implementation (safe, minimal):
```py
# core/tags/__init__.py
import importlib
from typing import Any, List

def __getattr__(name: str) -> Any:
    # lazy-load the implementation module on demand
    try:
        _mod = importlib.import_module("labs.some_tags_module")
    except Exception:
        raise AttributeError(f"module 'core.tags' has no attribute {name}")
    return getattr(_mod, name)

def __dir__() -> List[str]:
    try:
        _mod = importlib.import_module("labs.some_tags_module")
        mod_names = [n for n in dir(_mod) if not n.startswith("_")]
    except Exception:
        mod_names = []
    return list(globals().keys()) + mod_names
```

- Replace `labs.some_tags_module` with the specific module(s) that were being re-exported (e.g., `labs.tags.registry` or `labs.core.tag_helpers`)
- If multiple labs modules were re-exported, fold them into `__getattr__` lookup logic or load them lazily on first access

Tests (add `tests/core/test_tags_init_importsafe.py`):
```py
def test_tags_import_safe():
    import importlib
    importlib.import_module("core.tags")

def test_tags_dir_proxy_has_expected_names(monkeypatch):
    # If you want, simulate labs module with monkeypatch
    import types
    fake = types.SimpleNamespace(TEST_TAG="example")
    import sys
    sys.modules['labs.some_tags_module'] = fake
    import core.tags
    assert 'TEST_TAG' in dir(core.tags)
    del sys.modules['labs.some_tags_module']
```

Stop & ask human review if:
- The change needs multiple re-export modules to be brought in (more than 1 labs module)
- The package API cannot be preserved by lazy proxy (manual rework needed)
- Lane-guard still shows a transitive path

Notes:
- This is an **interim** safe pattern. Add `# TODO: migrate to ProviderRegistry` at the top of the file
- Keep changes minimal and add documentation comment
```

## 📝 PR Template

```
Title: chore(tags): lazy-proxy re-exports in core/tags/__init__.py (M1)

Summary:
- Replace re-exports from labs in core/tags/__init__.py with a lazy __getattr__/__dir__ proxy
- Add tests ensuring package import is safe and proxy exposes expected names when labs module available

Validation:
- ruff: artifacts/reports/ruff_tags_init.txt
- mypy: artifacts/reports/mypy_tags_init.txt
- pytest: artifacts/reports/pytest_tags_init.txt
- lane-guard: artifacts/reports/lane_guard_tags_init.log

Checklist:
- [ ] Import-safety tests pass
- [ ] No top-level labs import-time edges introduced
- [ ] Lane-guard: Contracts KEPT
```

## 🛡️ Safety Guardrails

- ✅ Single file change only
- ✅ Interim pattern (TODO for ProviderRegistry migration)
- ✅ Lazy proxy preserves API compatibility
- ✅ Import-safety test required
- ✅ Documentation comments added

## 🔄 Implementation Pattern

**Lazy Proxy Pattern**:
```py
# Before: from labs.tags.registry import *
# After: __getattr__ + __dir__ proxy that loads on demand
```

**Benefits**:
- ✅ Preserves existing API
- ✅ No import-time labs loading
- ✅ Graceful fallback on missing labs
- ✅ Compatible with existing consumers

## 📋 Coordination

- **File Lock**: Add `core/tags/__init__.py` to run-lock while PR open
- **PR Label**: `agent:claude-M1`  
- **Conflict Avoidance**: Main laptop should avoid this file
- **Future Migration**: TODO added for ProviderRegistry transition

---

**Status**: Ready for Claude Code execution  
**Next**: Run prompt → Validate → Create PR → Plan ProviderRegistry migration