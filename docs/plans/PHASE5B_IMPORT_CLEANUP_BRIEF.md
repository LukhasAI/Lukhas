---
title: Phase 5B Import Path Cleanup Brief
date: 2025-10-18
status: ready-for-parallel-agent
priority: high
branch: chore/phase5b-migrate-real-code
---

# Phase 5B Import Path Cleanup Brief

## Mission
Fix remaining import path issues after complete `lukhas/` namespace removal. The directory flattening is complete, but ~35 import references need cleanup and import errors need resolution.

## Context

### What Was Done (Phase 5B Complete)
- ✅ Removed entire `lukhas/` directory via `git rm -rf lukhas/`
- ✅ Merged 63 Python files from `lukhas/` to root directories
- ✅ Rewrote 1,097 Python files to remove `lukhas.*` imports (3,296 → 35 remaining)
- ✅ Updated 17 manifest paths (removed `lukhas/` prefix)
- ✅ Contract validation passed (0 errors)
- ✅ Committed in `23e5c17aa` on branch `chore/phase5b-migrate-real-code`

### Current Branch Status
```bash
Branch: chore/phase5b-migrate-real-code
Last commit: 23e5c17aa "refactor(phase5b): complete lukhas/ namespace removal"
Files changed: 2,200+
Status: All changes committed
```

## Problems to Solve

### 1. Remaining `lukhas.*` Import References (35 occurrences in 20 files)

Located primarily in:
- Test files: `tests/lint/test_lane_imports.py`, `tests/telemetry/conftest.py`, `tests/test_telemetry_authz_smoke.py`
- Scripts: `scripts/normalize_inventory.py`, `scripts/dependency_scanner.py`, `scripts/normalize_imports.py`, etc.
- Root files: `__init__.py` (5 refs), `conftest.py` (4 refs)
- Quarantine: Various phase2_syntax files

**Find them with:**
```bash
rg '\blukhas\.' --type py | head -20
```

### 2. Import Errors in Test Suite

**Error seen:**
```
ImportError while loading conftest '/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/conftest.py'
AttributeError: '_SixMetaPathImporter' object has no attribute 'find_spec'
```

This indicates broken imports in the test infrastructure.

### 3. Verify All Modules Load Correctly

Need to validate that the flattened structure doesn't have circular imports or missing dependencies.

## Tasks

### Task 1: Fix Remaining 35 `lukhas.*` References
- [ ] Update test files to use root-level imports
- [ ] Update scripts that reference `lukhas.*` namespace
- [ ] Update `__init__.py` and `conftest.py` root files
- [ ] Clean up quarantine files if still relevant

**Pattern to apply:**
```python
# Before
from lukhas.memory import MemorySystem
import lukhas.core.governance

# After
from memory import MemorySystem
import core.governance
```

### Task 2: Fix conftest.py Import Issues
- [ ] Read `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/conftest.py`
- [ ] Read `/Users/agi_dev/LOCAL-REPOS/Lukhas/conftest.py`
- [ ] Fix the `_SixMetaPathImporter` attribute error
- [ ] Ensure pytest can load conftest without errors

### Task 3: Validate Import Health
- [ ] Run basic import test for critical modules:
  ```bash
  python3 -c "import memory; import core; import governance; print('✅ Core imports work')"
  ```
- [ ] Check for circular import issues
- [ ] Run smoke tests: `make smoke` or `pytest tests/smoke/ -v`

### Task 4: Update Remaining Manifests (if needed)
- [ ] Check if any manifests still reference `lukhas/` paths:
  ```bash
  rg '"path":\s*"lukhas/' manifests/ --type json
  ```
- [ ] Update any remaining manifest paths

### Task 5: Final Validation
- [ ] Run contract validation: `python3 scripts/validate_contract_refs.py`
- [ ] Run linting: `make lint` or `ruff check .`
- [ ] Attempt smoke test suite: `make smoke`
- [ ] Document any modules that legitimately can't import yet

## Success Criteria

1. ✅ Zero `lukhas.*` import references in codebase (except archived/quarantine if intentional)
2. ✅ Smoke tests pass or show expected failures only
3. ✅ conftest.py loads without AttributeError
4. ✅ Core modules importable: `memory`, `core`, `governance`, `observability`
5. ✅ Contract validation passes
6. ✅ All changes committed with T4 standard commit message

## Key Files to Review

### Import Issues
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/conftest.py` - 4 lukhas refs
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/__init__.py` - 5 lukhas refs
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/conftest.py` - AttributeError source

### Scripts to Update
- `scripts/normalize_inventory.py`
- `scripts/dependency_scanner.py`
- `scripts/normalize_imports.py`
- `scripts/plan_colony_renames.py`
- `scripts/gen_lukhas_pkg_shims.py`
- `scripts/codemod_imports.py`

### Test Files
- `tests/lint/test_lane_imports.py`
- `tests/telemetry/conftest.py`
- `tests/test_telemetry_authz_smoke.py`

## Migration Artifacts (Reference)

Created during Phase 5B:
- `docs/audits/phase5b_migration_plan.json` - Original migration strategy
- `docs/audits/lukhas_shim_audit.json` - Phase 5A shim analysis (reference)

## Notes

- **DO NOT** recreate `lukhas/` directory
- **DO NOT** revert any of the 2,200 files changed in Phase 5B
- **Focus on** fixing imports, not restructuring
- Some quarantine files may intentionally reference old structure - use judgment
- If a module truly can't import, document why rather than forcing it

## Commit Message Template

When complete, use this format:

```
fix(imports): resolve remaining lukhas.* references after Phase 5B flattening

**Problem**
- 35 lukhas.* import references remaining after namespace removal
- conftest.py AttributeError preventing test suite from loading
- Import paths need update in test files and scripts

**Solution**
- Updated [N] test files to use root-level imports
- Fixed conftest.py [specific fix]
- Updated scripts: [list key scripts]
- Validated core module imports work correctly

**Impact**
- ✅ Zero lukhas.* references in active code
- ✅ Smoke tests [pass/show expected failures]
- ✅ Test infrastructure loads without errors
- ✅ Core modules importable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Questions/Blockers

If you encounter issues:
1. Some imports may legitimately fail if modules have unresolved dependencies - document these
2. Quarantine files may be intentionally broken - check git history before "fixing"
3. If circular imports emerge, consider using TYPE_CHECKING guards or lazy imports

## Original User Request

> "then lets run a parallel Claude fixing all the merges / paths"

This brief addresses that request. Good luck! 🚀
