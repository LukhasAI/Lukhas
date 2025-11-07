# MATRIZ Readiness — Executive Summary (T4 / 0.01%)

**Chosen strategy (recommended):** **Virtual Flattening (Shim-first, then physical)** — create flattened top-level modules for deeply nested MATRIZ and candidate/core matrix nodes, implement lightweight backward-compatibility shims at the original locations, and then run targeted PRs to remove shims after a short deprecation period.
**Why:** discovery shows heavy cross-subsystem imports (high import centrality) and many critical entry points defined under `candidate.core.matrix.nodes` and `MATRIZ` (see `pyproject.toml` entry points). A shim-first approach minimizes runtime risk and gives us audit evidence for each change. It enables the Matriz Cognitive Mesh with minimal immediate behavioral risk.

**What we produced** (all under `release_artifacts/matriz_readiness_v1/`):
- `flatten_map.csv` — initial top-50 candidate migration map (shim/move choices + risk)
- `todo_list.md` — precise, surgical TODOs (agent-ready) for implementation
- `restoration_audit.csv` — template + sample rows (empty originals where unknown)
- `scripts/rewrite_imports_libcst.py` — AST-based import-rewrite tool
- `patches/` — example patch (shim + move) for canonical MATRIZ node
- `pr_templates/` — ready PR bodies and checklists for top subsystems
- `verification/` — scripts + commands to run verification; placeholders for log outputs (to be produced by running the scripts)
- `manifest.txt` — list of files and locations

**Assumptions & runtime decision:** repo advertises `requires-python = ">=3.9"` and `tool.ruff.target-version = "py39"` in `pyproject.toml` (we fetched it). Default runtime target: **Python 3.9**. If you plan to target py310+ for some refactors, change the `target-version` in `pyproject.toml` and re-run `ruff`/`pyupgrade` passes after upgrading CI.

**Risk summary:** highest risk is public API and test fixtures breakage. Mitigations: shim-first, per-PR smoke and compile checks, per-PR `restoration_audit.csv` entries, CI gating, small PRs per subsystem.

**Acceptance criteria (per PR and overall):**
- `python3 -m compileall .` passes (no SyntaxError)
- `ruff check --select E,F --statistics` shows no new E/F errors attributable to the moved files
- `ruff check --select E741` for moved modules either passes or E741 fixes are included in PRs
- Smoke tests for MATRIZ lane (`pytest -m "matriz or tier1"`) pass locally and in CI

**Next action:** run `scripts/generate_flatten_map.py` (below) with the discovery outputs (I included an initial top-50 map). Then implement TODOs in `todo_list.md` in order: TODO-02 (VIVOX shim example) → TODO-03 (BENCHMARKS physical small move) → TODO-04 (TESTS E741) → etc.
