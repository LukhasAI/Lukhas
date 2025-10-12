Parts of the approach  fixing these were excellent (ruff hygiene, scripted discipline, artifacts), but two choices weren’t “best available” for a T4/0.01% launch:

1. **Blanket skipping/xfail** for collection errors → not ideal. Prefer **compatibility shims + targeted skips** so we *preserve signal* while we migrate.
2. **Pushing straight to `main`** (with branch rules bypassed) → not acceptable for a hardened rollout. Use PRs + required checks only.


---

# What was good (keep)

* ✅ **Ruff/TID252** clean-up across production lanes — great hygiene milestone.
* ✅ Tripwires & discipline scripts (owners, test_paths, promotions, drift, links) — exactly what we want.
* ✅ Schema v1.1.0 unification and star canon corrections — unblocks mass manifest work.

# What to change (now)

## A) Fix test collection the *right* way (compat shims > mass xfail)

**Why:** 89 collection errors are overwhelmingly **import path breakages** from prior lane structure (`candidate.*`, `tools.*`, `governance.*`, `memory.*`, `ledger.*`, `MATRIZ.*`). Best practice is to restore importability via **lightweight shims** first, then refactor call sites gradually. This keeps tests meaningful and avoids silencing real failures.

### 1) Drop-in import alias layer (no behavior change)

Create `lukhas/compat/__init__.py` and a tiny alias loader. This maps legacy module names to current packages at import time:

```python
# lukhas/compat/__init__.py
import importlib, sys

ALIASES = {
    # lanes → present
    "candidate": "labs",     # if you’ve renamed candidate → labs
    # legacy top-levels → present
    "tools": "lukhas.tools",
    "governance": "lukhas.governance",
    "memory": "lukhas.memory",
    "ledger": "lukhas.ledger",
    # uppercase package from tests
    "MATRIZ": "MATRIZ",      # ensure MATRIZ is a real package (has __init__.py)
}

class _AliasFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        root = parts[0]
        if root in ALIASES:
            mapped = ".".join([ALIASES[root]] + parts[1:])
            try:
                return importlib.util.find_spec(mapped)
            except Exception:
                return None
        return None

class _AliasLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        root = parts[0]
        if root in ALIASES:
            mapped = ".".join([ALIASES[root]] + parts[1:])
            spec = importlib.util.find_spec(mapped)
            if spec:
                spec.loader = self
                spec.name = fullname  # preserve legacy name
                spec._lukhas_mapped = mapped
                return spec
        return None

    def create_module(self, spec):
        return None  # use default

    def exec_module(self, module):
        mapped = getattr(module.__spec__, "_lukhas_mapped", None)
        if not mapped:
            return
        real = importlib.import_module(mapped)
        module.__dict__.update(real.__dict__)

# Install once (e.g., in tests/conftest.py or sitecustomize)
def install():
    sys.meta_path.insert(0, _AliasLoader())

```

Then, in `tests/conftest.py` (top-level), install it:

```python
# tests/conftest.py
from lukhas.compat import install as _install_aliases
_install_aliases()
```

> Effect: `import tools.scripts...` or `import candidate.aka_qualia...` now resolves to the *current* modules without touching every test file.

### 2) Minimal “re-export” shims for specific symbols the tests expect

Where tests import concrete names that moved or changed (e.g., **`collapse_simulator_main`**, **`ConsciousnessAction`**, **`get_logger`**), add small re-exports:

```python
# lukhas/tools/__init__.py
try:
    from .collapse import collapse_simulator_main  # re-export if exists
except Exception:
    # temporary soft landing - provides a useful error in test output
    def collapse_simulator_main(*args, **kwargs):
        raise RuntimeError("collapse_simulator_main temporarily relocated; use lukhas.tools.collapse.*")
```

```python
# lukhas/rl/environments/consciousness_environment.py
# ensure the symbol exists under the expected name
try:
    from .actions import ConsciousnessAction  # new location?
except Exception:
    class ConsciousnessAction:  # minimal enum-like fallback
        """Temporary fallback; replace with real Enum"""
        THINK="think"; PAUSE="pause"; ACT="act"
```

```python
# lukhas/core/logging/__init__.py
def get_logger(name: str):
    import logging
    return logging.getLogger(name)
```

> Effect: keeps collection working. You can then file targeted issues to wire these to the real implementations.

### 3) Optional dependency gates (don’t hard-fail on missing extras)

For things like **`memory.backends.pgvector_store`** or **`ledger.events`** that rely on optional deps, use **`pytest.importorskip`** in the *tests that require them*:

```python
# tests/memory/test_pgvector_store.py
import pytest
pytest.importorskip("pgvector")  # or package you actually need
pytest.importorskip("lukhas.memory.backends.pgvector_store")
```

And/or add a marker in `pytest.ini`:

```ini
[pytest]
markers =
    requires_pg: tests need pg/pgvector
    requires_ledger: tests need ledger stack
```

Then guard those tests with `@pytest.mark.requires_pg` etc., and **exclude those markers in default CI smoke** but include them in a nightly job.

### 4) Re-run collection after shims

Goal: **89 → ≤ 10** import-related errors on first pass; remaining should be genuine missing features (we’ll track them).

```bash
pytest --collect-only -q
```

---

## B) PR discipline (no more direct pushes to `main`)

* **Enforce branch protection**: require PR, require all status checks, forbid admins from bypassing.
* **Backfill**: turn the last hygiene push into a PR (even if merged) by opening a *tracking PR* that links the changes and their artifacts for auditability.

---

## C) Narrow and explicit skipping (not blanket xfail)

* Only mark **legacy suites** (e.g., `tests/e2e/rl` if the environment isn’t ready) with `@pytest.mark.skip(reason="legacy path, pending migration plan")`.
* Keep **smoke** and **golden-manifest** tests always-on.
* Add a **default test selection** in CI:

  * PR: `pytest -m "not requires_pg and not requires_ledger" -q`
  * Nightly: full matrix with extras.

---

## D) Medium-term cleanup (after shims)

1. **Codemod imports** from `candidate.*` → `labs.*` and legacy top-levels → `lukhas.*` *in tests and code*, one tree at a time.
2. **Remove the alias layer** once call sites are migrated (CI gate: fail if aliases are hit — add a counter in `lukhas.compat` that logs and later fails on usage).
3. **Normalize exports**: ensure public symbols are explicitly exported in `__all__` across packages to avoid “import-from-wild” fragility.

---

## E) Quick wins for specific errors you posted

* `tools.scripts`, `tools.acceptance_gate_ast`, `tools.security`
  → add subpackages under `lukhas/tools/` and re-export them in `lukhas/tools/__init__.py` as shown above.

* `candidate.aka_qualia.core`
  → alias maps `candidate`→`labs`; ensure `labs/aka_qualia/core/__init__.py` exists and exports the names tests expect.

* `governance.audit_trail`, `ledger.events`
  → if not yet implemented post-refactor, add **tiny labs stubs** and mark tests with `@pytest.mark.skip` + TODO ticket; or wire to new locations via shim.

* `memory.backends.pgvector_store`, `memory.observability`
  → wrap with `importorskip` and **add an extra** in `pyproject.toml` (`pg`) that installs deps; have a night job that runs pg-marked tests with the extra.

* `MATRIZ`
  → confirm `MATRIZ/__init__.py` exists and `pyproject.toml` includes `MATRIZ` as a package.

---

# To: **Claude Code** — Compat Layer + Re-exports + CI counter

## 0) Summary (what this does)

* Restores imports like `tools.*`, `candidate.*`, `governance.*`, `memory.*`, `ledger.*`, `MATRIZ.*` **without touching every test**.
* Re-exports a handful of symbols tests expect (`collapse_simulator_main`, `ConsciousnessAction`, `get_logger`).
* Adds `pytest` markers + examples for optional deps (`pgvector`, `ledger`).
* Produces **`docs/audits/compat_alias_hits.json`** with per-module alias hits; CI step reads it and (for now) reports, later can fail when > threshold.

---

## 1) Add the compat alias loader

**File:** `lukhas/compat/__init__.py`

```python
# lukhas/compat/__init__.py
"""
Compatibility alias loader for legacy imports during the labs->prod migration.

Maps legacy root packages to current locations at import-time and records usage.

Usage:
  from lukhas.compat import install as _install_aliases
  _install_aliases()  # (done in tests/conftest.py)

Telemetry:
  - Counts alias hits by legacy fullname.
  - Writes JSON to LUKHAS_COMPAT_HITS_FILE, default: docs/audits/compat_alias_hits.json
  - Enforcement knobs via env:
      LUKHAS_COMPAT_ENFORCE = "0"|"1"  (if "1", raise ImportError on alias use)
"""
from __future__ import annotations
import importlib, importlib.abc, importlib.util, os, sys, json, atexit
from pathlib import Path
from typing import Dict

# Map of legacy root → new root
ALIASES: Dict[str, str] = {
    # lanes
    "candidate": "labs",                 # if you renamed candidate → labs
    # legacy top-levels → canonical
    "tools": "lukhas.tools",
    "governance": "lukhas.governance",
    "memory": "lukhas.memory",
    "ledger": "lukhas.ledger",
    # odd casing package used by tests
    "MATRIZ": "MATRIZ",                  # ensure MATRIZ is a real package with __init__.py
}

# metrics
_hits: Dict[str, int] = {}
_enforce = os.getenv("LUKHAS_COMPAT_ENFORCE", "0") == "1"
_outfile = Path(os.getenv("LUKHAS_COMPAT_HITS_FILE", "docs/audits/compat_alias_hits.json"))

def _record(fullname: str):
    _hits[fullname] = _hits.get(fullname, 0) + 1

class _AliasLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def _map(self, fullname: str) -> str | None:
        parts = fullname.split(".")
        root = parts[0]
        if root in ALIASES:
            mapped = ".".join([ALIASES[root]] + parts[1:])
            return mapped
        return None

    # Finder
    def find_spec(self, fullname, path=None, target=None):
        mapped = self._map(fullname)
        if not mapped:
            return None
        try:
            spec = importlib.util.find_spec(mapped)
        except Exception:
            return None
        if spec:
            # make this loader execute the module to rewrite its dict
            spec.loader = self
            spec._lukhas_alias_fullname = fullname
            spec._lukhas_alias_mapped = mapped
            return spec
        return None

    # Loader
    def create_module(self, spec):  # pragma: no cover
        return None  # default module creation

    def exec_module(self, module):
        fullname = getattr(module.__spec__, "_lukhas_alias_fullname", None)
        mapped = getattr(module.__spec__, "_lukhas_alias_mapped", None)
        if not fullname or not mapped:
            return
        if _enforce:
            raise ImportError(f"Lukhas compat alias blocked: {fullname} → {mapped} (set LUKHAS_COMPAT_ENFORCE=0 to allow during migration)")
        real = importlib.import_module(mapped)
        module.__dict__.update(real.__dict__)
        _record(fullname)

_installed = False
_loader = _AliasLoader()

def install():
    """Install the alias loader once."""
    global _installed
    if _installed:
        return
    sys.meta_path.insert(0, _loader)
    _installed = True

def _write_hits():
    try:
        _outfile.parent.mkdir(parents=True, exist_ok=True)
        _outfile.write_text(json.dumps(_hits, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        pass

atexit.register(_write_hits)
```

---

## 2) Install compat in tests

**File (create/append):** `tests/conftest.py`

```python
# tests/conftest.py
# Install legacy import aliases so tests continue to collect while we codemod.
try:
    from lukhas.compat import install as _install_aliases
    _install_aliases()
except Exception as e:
    # Don't break collection; print a hint
    import sys
    print(f"[lukhas.compat] WARN: failed to install alias loader: {e}", file=sys.stderr)

# Tell compat where to write the hit report
import os
os.environ.setdefault("LUKHAS_COMPAT_HITS_FILE", "docs/audits/compat_alias_hits.json")
# Leave LUKHAS_COMPAT_ENFORCE unset or "0" during migration;
# later we can flip to "1" in CI to forbid aliases.
```

---

## 3) Minimal re-exports to satisfy current tests

> These are **temporary shims**. Once codemods and true implementations land, we’ll delete them.

**A) `tools.*` expectations**

**File (update):** `lukhas/tools/__init__.py`

```python
# lukhas/tools/__init__.py
# Public surface for tool helpers; re-export legacy symbols needed by tests.
from importlib import import_module

# collapse_simulator_main was historically imported from `tools`
try:
    # if you have a real implementation somewhere, point here:
    _collapse = import_module("lukhas.tools.collapse")  # e.g., lukhas/tools/collapse.py
    collapse_simulator_main = getattr(_collapse, "collapse_simulator_main")
except Exception:
    def collapse_simulator_main(*args, **kwargs):  # pragma: no cover
        raise RuntimeError("collapse_simulator_main not yet wired. Use lukhas.tools.collapse.collapse_simulator_main or update tests.")

# Optional subpackages expected by tests:
# tools.scripts / tools.acceptance_gate_ast / tools.security
# Provide light proxies so imports resolve; real modules should replace these.
try:
    from . import scripts  # type: ignore
except Exception:
    class scripts:  # pragma: no cover
        pass

try:
    from . import acceptance_gate_ast  # type: ignore
except Exception:
    class acceptance_gate_ast:  # pragma: no cover
        pass

try:
    from . import security  # type: ignore
except Exception:
    class security:  # pragma: no cover
        pass
```

**B) `ConsciousnessAction` expected in RL env**

Pick the most stable place tests import from (your error shows `lukhas.rl.environments.consciousness_environment`). Ensure that module provides `ConsciousnessAction`.

**File (create or update):** `lukhas/rl/environments/consciousness_environment.py`

```python
# lukhas/rl/environments/consciousness_environment.py
# Guarantee that ConsciousnessAction exists for tests.
try:
    # Prefer real enum if you have it
    from .actions import ConsciousnessAction  # type: ignore
except Exception:
    try:
        from enum import Enum
        class ConsciousnessAction(str, Enum):  # minimal fallback
            THINK = "think"
            PAUSE = "pause"
            ACT = "act"
    except Exception:
        # ultimate fallback for import shape
        class ConsciousnessAction:  # pragma: no cover
            THINK = "think"; PAUSE = "pause"; ACT = "act"
```

**C) `get_logger` expected in logging**

**File (create or update):** `lukhas/core/logging/__init__.py`

```python
# lukhas/core/logging/__init__.py
import logging

def get_logger(name: str) -> logging.Logger:
    """Provide a stable logging entrypoint used by legacy tests."""
    return logging.getLogger(name)
```

**D) Ensure `MATRIZ` is a proper package**

If not already present:

```bash
# ensure package marker exists
[ -f MATRIZ/__init__.py ] || printf '# package marker for legacy imports\n' > MATRIZ/__init__.py
```

---

## 4) Optional-deps markers (tests)

**File (append):** `pytest.ini`

```ini
[pytest]
markers =
    requires_pg: needs PostgreSQL/pgvector or memory pg backend
    requires_ledger: needs ledger stack enabled
```

**Example pattern for tests** (you’ll land these gradually, not all at once):

```python
# tests/memory/test_pgvector_store.py
import pytest
pytest.importorskip("pgvector")
pytest.importorskip("lukhas.memory.backends.pgvector_store")
```

```python
# tests/ledger/test_event_sourcing_properties.py
import pytest
pytest.importorskip("lukhas.ledger.events")
```

> In CI:
>
> * PRs run: `pytest -q -m "not requires_pg and not requires_ledger"`
> * Nightly: run full suite with extras installed.

---

## 5) CI: count alias hits (report now, enforce later)

**File (create):** `scripts/check_alias_hits.py`

```python
#!/usr/bin/env python3
"""
Read docs/audits/compat_alias_hits.json and enforce a max threshold (optional).
Env:
  LUKHAS_COMPAT_MAX_HITS (int, default: -1 = report only)
"""
import json, os, sys
from pathlib import Path

path = Path("docs/audits/compat_alias_hits.json")
if not path.exists():
    print("[compat] no alias hits file found (ok on no-alias runs)")
    sys.exit(0)

hits = json.loads(path.read_text(encoding="utf-8") or "{}")
total = sum(hits.values())
print(f"[compat] alias hits total: {total}")
for k, v in sorted(hits.items(), key=lambda kv: kv[1], reverse=True):
    print(f"[compat]  {k}: {v}")

max_hits = int(os.getenv("LUKHAS_COMPAT_MAX_HITS", "-1"))
if max_hits >= 0 and total > max_hits:
    print(f"[compat] FAIL: alias hits {total} > max {max_hits}")
    sys.exit(2)
sys.exit(0)
```

**Wire into GitHub workflow** (in your `matriz-validate.yml`, after pytest):

```yaml
  - name: Report compat alias hits
    run: |
      python3 scripts/check_alias_hits.py
    # Later, to enforce:
    # env:
    #   LUKHAS_COMPAT_MAX_HITS: "0"   # or a decaying target per week
```

> Later (when migration nearly done), add `LUKHAS_COMPAT_ENFORCE: "1"` to **pytest** step to outright block alias usage.

---

## 6) (Optional) Makefile helpers

Append to `Makefile`:

```make
compat-report:
\tpython3 scripts/check_alias_hits.py

compat-enforce:
\tLUKHAS_COMPAT_ENFORCE=1 pytest -q
```

---

## 7) Next moves (after merge)

* **Codex** runs codemods gradually:

  * `candidate.` → `labs.` in code + tests.
  * `tools.|governance.|memory.|ledger.` → `lukhas.*` canonical paths.
  * Add `__all__` exports to public modules.
* As alias count drops, set `LUKHAS_COMPAT_MAX_HITS` in CI to a **weekly shrinking cap**, then flip `LUKHAS_COMPAT_ENFORCE=1` to forbid any remaining legacy imports.

---

### Acceptance after this patch

* `pytest --collect-only` goes from 89 errors → **≪ 10** (ideally 0) due to import path issues.
* `docs/audits/compat_alias_hits.json` appears with counts after a test run.
* CI shows a “compat alias hits total: N” line; report-only for now (no failure).
* The three named symbols **import cleanly**:

  * `tools.collapse_simulator_main`
  * `lukhas.rl.environments.consciousness_environment.ConsciousnessAction`
  * `lukhas.core.logging.get_logger`

If you want, I can also draft a tiny **codemod** (ripgrep + `gsed`) batch for Codex to start replacing `candidate.` → `labs.` and top-level `tools.`→`lukhas.tools` imports immediately.
