# Phase 2 — Automation: Bulk Bridge Generator

**Goal:** Automate bridge generation for remaining ~766 gaps with simulation-first flow.

**Why:** Manual creation of 766 bridges is error-prone and time-consuming.

**Deliverables:**
- `tools/bridge_generator.py` that:
  - Reads gap analysis from `scripts/find_bridge_gaps.py`
  - Generates bridge exports using safe pattern
  - Creates dry-run patches via `simulate_change.sh`
  - Produces report with created/skipped/conflicts
- Unit tests for generator
- Documentation with deprecation policy
- Draft PR with sample 100-bridge patchset

**Pattern to Generate:**
```python
try:
    from labs.module.path import name
except ImportError:
    def name(*args, **kwargs): return None
try:
    __all__
except NameError:
    __all__ = []
if "name" not in __all__:
    __all__.append("name")
```

**Safety:**
- Default to `--simulate` mode
- Respect pyproject.toml excludes
- Generate `# DEPRECATED shim` comments
- No public package renames

**Acceptance:**
- Process 100 gaps in <5 minutes
- All generated code compiles
- Report shows conflicts/manual review cases

**References:**
- `scripts/find_bridge_gaps.py`
- `BRIDGE_GAP_ANALYSIS.md`
- Example: `consciousness/dream/expand/__init__.py`
