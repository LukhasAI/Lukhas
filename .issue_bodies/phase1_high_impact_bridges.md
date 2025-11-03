# Phase 1 — Fix High-Impact Bridges (Top 5 modules)

**Goal (short):** Create/extend bridge modules to export high-impact labs modules so test collection succeeds for the top 5 failure hotspots.

**Why:** The root cause is bridge files that exist but do not export the underlying modules (e.g., `consciousness/dream/expand/__init__.py` doesn't export `mesh`), exposing ~786 gaps and causing ~50% of collection errors.

**Scope (this issue):**
- Target the *Top 5* high-impact bridges:
  1. `lukhas.identity` (7 failures)
  2. `governance.ethics` (7 failures)
  3. `memory.backends` (6 failures)
  4. `labs.governance.guardian_system_integration` (5 failures)
  5. `aka_qualia.core` (5 failures)

**Deliverables:**
- For each module above:
  - Create branch `refactor/bridge-<short>-v1` (example: `refactor/bridge-identity-v1`).
  - Add exports in the bridge `__init__.py` so `from bridge.path import X` works.
  - Create a minimal unit smoke-check or `python -m py_compile` target to verify syntax.
  - Create a draft PR per bridge with `simulate_change.sh` patch attached (or include patch in `patches/`).

**Exact steps (per-bridge):**
1. `git checkout -b refactor/bridge-<short>-v1`
2. Identify bridge and implementation. Example:
   - Implementation: `labs/lukhas/identity/__init__.py`
   - Bridge: `lukhas/__init__.py`
3. Edit `__init__.py` to export module(s), e.g.:
   ```python
   # Bridge export for lukhas.identity
   try:
       from labs.lukhas import identity
   except ImportError:
       identity = None  # fallback
   
   if identity:
       __all__.append("identity")
   ```
4. Run syntax check:
   ```bash
   python3 -m py_compile lukhas/__init__.py labs/lukhas/identity/__init__.py
   ```
5. Run collection-only to verify reduced errors:
   ```bash
   pytest --collect-only -m "smoke" 2>&1 | grep "ERROR collecting" | wc -l
   ```
6. Commit changes, run `simulate_change.sh --simulate shim <old> <new> <symbols>` to produce a patch for review, and open a draft PR.

**Verification / Acceptance Criteria:**
- Each bridge PR compiles (`python -m py_compile`) and preserves public symbols via `__all__`.
- Combined impact after merging all 5 bridges: expect reduction of **~28 collection errors** (target: ~180 remaining).
- PR includes `restoration_audit.csv` entry and the `simulate_change.sh` patch.

**Files to review for guidance:**
- `BRIDGE_GAP_ANALYSIS.md`
- `scripts/find_bridge_gaps.py`
- Example: `consciousness/dream/expand/__init__.py` (lines 90-144)

**Current Status:**
- Collection errors: 211
- Tests collecting: 14 of 42 smoke test files
- Root cause: Identified as missing bridge exports

**Labels:** `area:bridges priority:high task`
