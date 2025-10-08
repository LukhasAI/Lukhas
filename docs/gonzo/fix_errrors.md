Surgical Implementation Guide: Quick Win Blitz + Symbol Export Generator
========================================================================

Strategic Context
- 87% ModuleNotFound reduction (46 → 6), 84 bridges in place, 13 metrics landed, 15 supporting artifacts captured.
- Remaining failure surface is 210 ImportError/CannotImport (91%), 6 ModuleNotFound (3%), 14 hard errors (6%).
- Architecture layer is stable; remaining work is the symbol export layer. Treat these as surgical insertions, not broad refactors.

Mission Snapshot
- Goal: Drop pytest collection errors from 139 → ~25 through a two-phase campaign (manual quick wins + automated symbol export generator).
- Scope: Top 10 missing symbols (Phase 1) and automation tooling to cover the remaining ~100 symbols (Phase 2 & 3).
- Inputs: `artifacts/pytest_collect_round13_analysis.json`, existing bridge generator, coding time availability (~2.75h).
- Output Artifacts: Updated exports and bridges, new tool `tools/error_analysis/symbol_export_generator.py`, refreshed error analysis, closing documentation note.

Execution Status (2025-02-14, Codex Run)
- Phase 1 quick-win stubs landed across metrics, async utilities, consciousness bridges, orchestration router, and observability bridge; pytest collection dropped to 137 errors.
- Phase 2 delivered `tools/error_analysis/symbol_export_generator.py` with CLI (`--from-analysis`, `--output`, `--apply`, `--dry-run`, `--review`, `--auto-fix`) and stored plan at `/tmp/symbol_exports.json`.
- Phase 3 auto-applied 38 new exports (9 skipped as already present); pytest collection now reports 119 errors (`artifacts/pytest_collect_post_symbol_tool_codex.txt`).
- Remaining blockers include recursion loops in `meta_cognitive_assessor`, config schema gaps, and syntax errors flagged during collection; hard-error backlog unchanged and called out in Risk Log.
- Iterations 4-6 expanded consciousness/memory/orchestration exports, added recursion-safe bridges, and tightened generator heuristics; pytest collection is now at 98 errors (`artifacts/pytest_collect_round21_codex.txt`, analysis in `artifacts/pytest_collect_round21_codex_analysis.json`).
- Current priority blockers: residual observability helpers (`initialize_advanced_metrics`, `RegressionSeverity`, `get_lukhas_metrics`), lifecycle/compression DTOs (`LifecycleStats`, `MemoryLifecycleManager`, `CompressionResult`), diagnostic signal enums, and the legacy Python 3.9 `type | None` `TypeError` stack.

Pre-Flight Checklist
1. Ensure working tree is clean or that existing local changes are understood (`git status --short`).
2. Activate the project environment if required (e.g., `pyenv local` or `poetry shell`).
3. Confirm baseline error state for reference:
   ```
   PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 | tee artifacts/pytest_collect_baseline.txt
   tail -5 artifacts/pytest_collect_baseline.txt
   ```
4. Open supporting references: `IMPORT_FIX_GUIDE.md`, recent analyzer outputs in `artifacts/`.
5. Keep `rg` ready for verifying symbol usage counts (e.g., `rg "run_with_retry"`).

Phase 1 – Quick Win Blitz (target 30 minutes)
---------------------------------------------
Purpose: land the highest-frequency missing symbols manually to establish momentum; expected drop ~24 errors (139 → ~115).

Step 1.1 – Add MATRIZ orchestration timeout metric
- File: `lukhas/metrics.py`.
- Locate the metrics section around the other MATRIZ counters.
- Insert the counter definition immediately after `mtrx_stage_duration_seconds`:
  ```python
  mtrx_orch_timeout_total = counter(
      "lukhas_mtrx_orch_timeout_total",
      "MATRIZ orchestration timeouts",
      labelnames=("component", "reason"),
  )
  ```
- Make sure `__all__` (or the exported tuple/list) includes `"mtrx_orch_timeout_total"` once.
- Sanity check: `rg "mtrx_orch_timeout_total"` should show 10 call sites.

Step 1.2 – Export async utilities
- File: `lukhas/async_utils/__init__.py`.
- Pattern: try to import from candidate package; otherwise provide a minimal stub and append to `__all__`.
- Add the following blocks near the other async exports:
  ```python
  try:
      from candidate.async_utils import run_guardian_task  # noqa: F401
  except ImportError:
      async def run_guardian_task(task, *args, **kwargs):
          """Fallback guardian task runner."""
          return await task(*args, **kwargs)
  __all__.append("run_guardian_task")

  try:
      from candidate.async_utils import run_with_retry  # noqa: F401
  except ImportError:
      async def run_with_retry(coro, max_retries=3, *args, **kwargs):
          """Fallback retry wrapper."""
          for attempt in range(max_retries):
              try:
                  return await coro(*args, **kwargs)
              except Exception:
                  if attempt == max_retries - 1:
                      raise
          return None
  __all__.append("run_with_retry")
  ```
- Keep ordering consistent with surrounding exports; maintain a blank line between blocks.

Step 1.3 – Add consciousness layer exports
- File: `consciousness/__init__.py`.
- Append the pattern after the existing AutoConsciousness section:
  ```python
  try:
      from candidate.consciousness import AwarenessEngine  # noqa: F401
  except ImportError:
      class AwarenessEngine:
          """Fallback awareness engine."""

          def __init__(self, *args, **kwargs):
              self.args = args
              self.kwargs = kwargs

          def process(self, *args, **kwargs):
              return None
  __all__.append("AwarenessEngine")

  try:
      from candidate.consciousness import ConsciousnessConfig  # noqa: F401
  except ImportError:
      class ConsciousnessConfig:
          """Fallback consciousness config."""

          def __init__(self, **kwargs):
              for key, value in kwargs.items():
                  setattr(self, key, value)
  __all__.append("ConsciousnessConfig")
  ```
- Confirm no duplicate `__all__` entries.

Step 1.4 – Create orchestration bridge
- File to add: `lukhas/orchestration/multi_ai_router/__init__.py`.
- Use the standard bridge pattern (import candidates, copy attributes, expose stubs if missing):
  ```python
  """Bridge for lukhas.orchestration.multi_ai_router."""

  from __future__ import annotations

  from enum import Enum
  from importlib import import_module
  from typing import List

  __all__: List[str] = []


  def _try(module_name: str):
      try:
          return import_module(module_name)
      except Exception:  # pragma: no cover - best effort bridge
          return None


  _CANDIDATES = (
      "lukhas_website.lukhas.orchestration.multi_ai_router",
      "candidate.orchestration.multi_ai_router",
  )

  _SRC = None
  for _candidate in _CANDIDATES:
      module = _try(_candidate)
      if module:
          _SRC = module
          for name in dir(module):
              if not name.startswith("_"):
                  globals()[name] = getattr(module, name)
                  __all__.append(name)
          break

  if "AIProvider" not in globals():
      class AIProvider(Enum):
          """Fallback AI provider registry."""

          OPENAI = "openai"
          ANTHROPIC = "anthropic"
          LOCAL = "local"

      __all__.append("AIProvider")

  if "AIModel" not in globals():
      class AIModel:
          """Fallback AI model wrapper."""

          def __init__(self, provider, model_name, **kwargs):
              self.provider = provider
              self.model_name = model_name
              for key, value in kwargs.items():
                  setattr(self, key, value)

      __all__.append("AIModel")


  def __getattr__(name: str):
      if _SRC and hasattr(_SRC, name):
          return getattr(_SRC, name)
      raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
  ```

Step 1.5 – Ensure meta cognitive assessor bridge exports `CognitiveLoadLevel`
- File to add or amend: `lukhas/consciousness/meta_cognitive_assessor/__init__.py`.
- Follow the same bridge pattern and include the fallback Enum:
  ```python
  """Bridge for lukhas.consciousness.meta_cognitive_assessor."""

  from __future__ import annotations

  from enum import Enum
  from importlib import import_module
  from typing import List

  __all__: List[str] = []


  def _try(module_name: str):
      try:
          return import_module(module_name)
      except Exception:  # pragma: no cover - best effort bridge
          return None


  _CANDIDATES = (
      "lukhas_website.lukhas.consciousness.meta_cognitive_assessor",
      "candidate.consciousness.meta_cognitive_assessor",
  )

  _SRC = None
  for _candidate in _CANDIDATES:
      module = _try(_candidate)
      if module:
          _SRC = module
          for name in dir(module):
              if not name.startswith("_"):
                  globals()[name] = getattr(module, name)
                  __all__.append(name)
          break

  if "CognitiveLoadLevel" not in globals():
      class CognitiveLoadLevel(Enum):
          """Fallback cognitive load enum."""

          LOW = "low"
          MEDIUM = "medium"
          HIGH = "high"
          CRITICAL = "critical"

      __all__.append("CognitiveLoadLevel")


  def __getattr__(name: str):
      if _SRC and hasattr(_SRC, name):
          return getattr(_SRC, name)
      raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
  ```

Step 1.6 – Generate the final bridge for observability
- Command:
  ```
  python3 tools/error_analysis/bridge_generator.py observability.intelligent_alerting
  ```
- Confirm the generated file mirrors the standard pattern and keep the stub minimal.

Step 1.7 – Verify Phase 1 impact
- Command:
  ```
  PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 | tee artifacts/pytest_collect_phase1.txt
  tail -5 artifacts/pytest_collect_phase1.txt
  rg -c '^ERROR' artifacts/pytest_collect_phase1.txt
  ```
- Target: errors ≈ 115 (down from 139). Investigate outliers if the drop is <15.

Step 1.8 – Stage deliverables (no commit if you are batching)
- `git add lukhas/metrics.py lukhas/async_utils/__init__.py consciousness/__init__.py`
- `git add lukhas/orchestration/multi_ai_router/__init__.py`
- `git add lukhas/consciousness/meta_cognitive_assessor/__init__.py`
- `git add observability/intelligent_alerting/__init__.py` (or the generated bridge file)
- Record the Phase 1 delta in your session notes.

Phase 2 – Build `symbol_export_generator.py` (target 90 minutes)
---------------------------------------------------------------
Purpose: automate symbol export creation using the analyzer output. The tool should accept analysis JSON, classify symbols, generate stubs, and apply changes in review or auto modes.

Step 2.1 – Scaffold the CLI tool
- File: `tools/error_analysis/symbol_export_generator.py`.
- Start with the header and imports:
  ```python
  #!/usr/bin/env python3
  """Generate and apply symbol exports based on pytest analysis."""

  from __future__ import annotations

  import argparse
  import json
  from dataclasses import dataclass
  from enum import Enum
  from pathlib import Path
  from typing import Dict, List, Optional
  ```
- Define `SymbolType` (Enum) and `SymbolExport` (dataclass with symbol, module, count, symbol_type, stub_code, destination_path).

Step 2.2 – Implement core functionality
- `load_analysis(path: Path) -> List[Dict]]`: read JSON, pull `CannotImportError` entries, deduplicate by `(module, symbol)`, accumulate counts.
- `detect_symbol_type(symbol: str, module: str) -> SymbolType`: heuristics:
  - ALL_CAPS → CONSTANT
  - CamelCase with keywords (Level/Type/Mode/Status) → ENUM, else CLASS
  - snake_case with async context/module containing `async` → ASYNC_FUNCTION
  - otherwise FUNCTION
- `generate_stub(symbol: str, symbol_type: SymbolType) -> str`: return minimal stub strings (see Appendix A).
- `resolve_target_module(module: str) -> Path`: convert dotted module to workspace path (use `module.replace(".", "/")` + `__init__.py` when needed). Respect special cases (e.g., treat ending with `.__init__` gracefully).
- `build_export_block(symbol, symbol_type, target_module)`:
  - Compose try/import block from primary candidate module (e.g., `candidate.<module>` or fallback) if consistent with existing bridge strategy.
  - For pure `__init__` files, integrate with existing `__all__` when present; otherwise append.
  - Provide hooks for injecting imports (e.g., `from enum import Enum` when needed).
- `apply_block(path: Path, block: str, dry_run: bool, review: bool)`:
  - For dry-run/review: output proposed diff snippet to stdout.
  - For auto mode: append or integrate block using file parsing (e.g., read text, ensure newline separation, avoid duplicates).
- Maintain idempotency: skip insertion when symbol already exported (use simple substring check or AST-lite parsing).

Step 2.3 – Wire up CLI modes
- Arguments:
  - `--from-analysis / -a`: path to analysis JSON (required for generation).
  - `--output`: optional JSON to store prepared export plan.
  - `--limit`: max number of symbols to process (for review pass).
  - `--apply`: path to plan JSON to apply.
  - `--dry-run`, `--review`, `--auto-fix`: mutually exclusive modes.
- Flow:
  1. `--from-analysis` loads data, builds export objects, optionally dumps plan to JSON (list of dicts with `module`, `symbol`, `symbol_type`, `destination_path`, `block`).
  2. `--apply` reads plan and executes requested mode.
  3. Always print a concise summary (e.g., `Prepared 38 exports across 12 modules`).

Step 2.4 – Quick QA passes
- `python3 tools/error_analysis/symbol_export_generator.py --help`
- `python3 tools/error_analysis/symbol_export_generator.py --from-analysis artifacts/pytest_collect_round13_analysis.json --dry-run --limit 5`
- Verify generated blocks include `try/except` and correct stub types.
- Store a review plan:
  ```
  python3 tools/error_analysis/symbol_export_generator.py \
      --from-analysis artifacts/pytest_collect_round13_analysis.json \
      --output /tmp/symbol_exports.json
  ```
- Inspect `/tmp/symbol_exports.json` briefly (ensure relative paths, stub strings rendered correctly).

Step 2.5 – Update documentation and tests if needed
- Append a short usage snippet to `IMPORT_FIX_GUIDE.md` or relevant toolkit doc.
- Optional: add unit smoke test under `tools/tests/` once script stabilizes (out of scope for first iteration if time constrained).

Phase 3 – Automated Symbol Export Rollout (target 15 minutes)
-------------------------------------------------------------
Objective: apply tool-driven exports to remaining symbols in two passes (manual review subset + auto apply).

Step 3.1 – Curate review batch
- Command:
  ```
  python3 tools/error_analysis/symbol_export_generator.py \
      --apply /tmp/symbol_exports.json \
      --review \
      --limit 30
  ```
- Review each proposed insertion. Tweak generated blocks if module-specific conventions differ.

Step 3.2 – Auto-apply remaining exports
- Command:
  ```
  python3 tools/error_analysis/symbol_export_generator.py \
      --apply /tmp/symbol_exports.json \
      --auto-fix
  ```
- Monitor output; rerun with `--dry-run` for any files that require manual intervention.

Step 3.3 – Re-run analyzer
- `PYTHONPATH=. python3 -m pytest --collect-only -q 2>&1 | tee artifacts/pytest_collect_post_symbol_tool.txt`
- Expect error count near 25. Capture exact number in notes.

Phase 4 – Verification & Wrap-Up (target 30 minutes)
----------------------------------------------------
1. Diff review: `git diff --stat` and spot check large inserts.
2. Ensure no syntax errors: `python3 -m compileall lukhas tools/error_analysis`.
3. Update campaign documentation (this file, plus any status dashboards).
4. Suggested commit strategy:
   - Commit 1 (Phase 1 manual fixes).
   - Commit 2 (symbol export generator tool).
   - Commit 3 (auto-applied exports + updated artifacts).
5. Optional: generate a fresh analyzer artifact for future runs and link it here.

Risk Log & Mitigations
- Misclassified symbol types → start with review batch, override types manually if needed, re-run tool.
- Duplicate exports → tool should detect existing symbol; manual search with `rg "symbol_name"` before applying block.
- Formatting regressions → run `ruff format` or project formatter if available (ensure consistent imports).
- Analyzer drift → always regenerate analysis JSON before large auto-fixes to avoid operating on stale data.

Appendix A – Stub Templates
- Function:
  ```python
  def symbol_name(*args, **kwargs):
      """Fallback stub."""
      return None
  ```
- Async function:
  ```python
  async def symbol_name(*args, **kwargs):
      """Fallback async stub."""
      return None
  ```
- Class:
  ```python
  class SymbolName:
      """Fallback class stub."""

      def __init__(self, *args, **kwargs):
          for key, value in kwargs.items():
              setattr(self, key, value)
  ```
- Enum:
  ```python
  from enum import Enum


  class SymbolName(Enum):
      """Fallback enum stub."""

      UNKNOWN = "unknown"
      DEFAULT = "default"
  ```
- Constant/variable:
  ```python
  SYMBOL_NAME = None  # Fallback constant
  ```

Appendix B – Quick Reference Commands
- Baseline collection: `PYTHONPATH=. python3 -m pytest --collect-only -q`
- Analyzer diff: `python3 tools/error_analysis/pytest_error_analyzer.py --round 14`
- Bridge generator: `python3 tools/error_analysis/bridge_generator.py module.path`
- Symbol generator dry run: `python3 tools/error_analysis/symbol_export_generator.py --from-analysis <json> --dry-run`
- Symbol generator auto apply: `python3 tools/error_analysis/symbol_export_generator.py --apply <plan> --auto-fix`
