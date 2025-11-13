# MATRIZ Flattening - Getting Started Guide

## Overview

This directory contains a complete, ready-to-execute plan for flattening deeply nested MATRIZ and candidate modules to improve import paths and maintainability.

**Strategy**: Shim-first virtual flattening → gradual physical migration

## Quick Start

### 1. Review the Plan (5 minutes)

```bash
# Read the executive summary
cat matriz_readiness_report.md

# Review the 7-step TODO list
cat todo_list.md

# Check the migration plan (48 files)
head -20 flatten_map.csv
```

### 2. Verify Tools Work (2 minutes)

```bash
# Test the import rewriter
python3 scripts/rewrite_imports_libcst.py --help

# Test the verification script
bash scripts/verify_and_collect.sh
```

### 3. Start Implementation

**Begin with TODO-02** - Canonical VIVOX Example (shim pattern)

```bash
# Create branch
git checkout -b refactor/flatten-vivox-v1

# Follow detailed steps in todo_list.md (TODO-02)
# Use PR template: pr_templates/refactor_flatten_vivox.md
```

## File Guide

### Core Documents
- **matriz_readiness_report.md** - Executive summary and strategy
- **flatten_map.csv** - 48 files migration plan with risk levels
- **todo_list.md** - 7 surgical TODOs with exact commands
- **restoration_audit.csv** - Template for tracking changes

### Tools
- **scripts/rewrite_imports_libcst.py** - AST-based import rewriter
  - Safely rewrites `from old.module import X` → `from new_module import X`
- **scripts/verify_and_collect.sh** - Verification suite
  - Runs: compile, ruff, black, smoke tests

### PR Templates (5 ready templates)
- **refactor_flatten_vivox.md** - MATRIZ shim example
- **refactor_flatten_benchmarks.md** - Physical move example
- **refactor_e741_tests.md** - E741 cleanup
- **chore_ci_flatten.md** - CI updates
- **refactor_flatten_scripts_tools.md** - Scripts/tools

### Discovery Data
- **discovery/pyproject.toml** - Current project config
- **discovery/top_python_files.txt** - Candidate files

## Implementation Sequence

### Phase 1: Shim Pattern (High-Risk Files)
**TODO-02**: VIVOX canonical example
- Target: `candidate/core/matrix/nodes/memory_node.py`
- Strategy: Create shim at original location, move implementation to `MATRIZ/matriz_memory_node.py`
- PR template ready

### Phase 2: Physical Moves (Low-Risk Files)
**TODO-03**: Benchmarks subset
- 3 files with low import centrality
- Use AST rewriter for import updates
- PR template ready

### Phase 3: Cleanup
**TODO-04**: E741 ambiguous identifiers in tests
- Fix single-letter variables exposed by moves
- PR template ready

### Phase 4: Infrastructure
**TODO-05**: CI and pre-commit updates
- Update `pyproject.toml`
- Add/update `.pre-commit-config.yaml`
- PR template ready

### Phase 5: Release
**TODO-06**: Verification and packaging
**TODO-07**: Tag v0.9.2-flatten-preview

## Example: Shim Pattern

**Original file**: `candidate/core/matrix/nodes/memory_node.py`
```python
class MemoryNode:
    def __init__(self):
        # ... implementation ...
```

**After flattening**:

**New location**: `MATRIZ/matriz_memory_node.py`
```python
# Full implementation moved here
class MemoryNode:
    def __init__(self):
        # ... implementation ...
```

**Shim** (replaces original): `candidate/core/matrix/nodes/memory_node.py`
```python
# DEPRECATED shim: moved to MATRIZ/matriz_memory_node.py
from MATRIZ.matriz_memory_node import MemoryNode  # noqa: TID001
__all__ = ["MemoryNode"]
```

## Verification (Per PR)

```bash
# 1. Compilation check
python3 -m compileall .

# 2. Ruff syntax check
ruff check --select E,F --statistics

# 3. E741 check (if applicable)
ruff check --select E741

# 4. Smoke tests
pytest -m "matriz or tier1"
```

## Risk Mitigation

- ✅ Small PRs (< 15 files per PR)
- ✅ Shim-first for high-risk files
- ✅ Per-PR verification suite
- ✅ restoration_audit.csv tracking
- ✅ CI gating on all checks
- ✅ Rollback procedures documented

## Success Criteria

Per PR:
- [ ] `python3 -m compileall .` passes
- [ ] `ruff check --select E,F` shows no new errors
- [ ] Smoke tests pass
- [ ] restoration_audit.csv updated

Overall:
- [ ] All 48 files migrated or shimmed
- [ ] Zero syntax errors
- [ ] All tests passing
- [ ] v0.9.2-flatten-preview tag created

## Support

- **Detailed commands**: See `todo_list.md` for exact step-by-step instructions
- **PR guidance**: Use templates in `pr_templates/`
- **Rollback**: Each TODO includes rollback commands
- **Questions**: Review `matriz_readiness_report.md` for strategy details

---

**Ready to start?** Begin with TODO-02 in `todo_list.md`
