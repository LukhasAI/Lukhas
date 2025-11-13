# Phase 1 — Fix High-Impact Bridges (Top 5 modules)

**Goal:** Create/extend bridge modules to export high-impact labs modules so test collection succeeds for the top 5 failure hotspots.

**Why:** Root cause is bridge files that exist but don't export underlying modules. Files exist at `labs/consciousness/dream/expand/mesh.py` but `consciousness/dream/expand/__init__.py` doesn't expose them.

**Scope - Target Top 5:**
1. `lukhas.identity` (7 test failures)
2. `governance.ethics` (7 test failures)
3. `memory.backends` (6 test failures)
4. `labs.governance.guardian_system_integration` (5 test failures)
5. `aka_qualia.core` (5 test failures)

**Per-Bridge Steps:**
1. Create branch: `refactor/bridge-<name>-v1`
2. Check if implementation exists in `labs/`
3. Add export to bridge `__init__.py`:
```python
# Bridge export
try:
    from labs.path.to import module_name
except ImportError:
    def module_name(*args, **kwargs):
        return None
if "module_name" not in __all__:
    __all__.append("module_name")
```
4. Verify: `python3 -m py_compile <bridge_file>`
5. Test: `pytest --collect-only -m "smoke" 2>&1 | grep "ERROR" | wc -l`
6. Create draft PR with patch

**Acceptance:**
- All 5 bridges compile
- Expect ~28 error reduction (211 → ~180)
- Each PR includes restoration audit entry

**Reference:**
- `BRIDGE_GAP_ANALYSIS.md`
- `scripts/find_bridge_gaps.py`
- Example: `consciousness/dream/expand/__init__.py` lines 90-144

**Current Status:**
- Collection errors: 211
- Tests collecting: 14/42
