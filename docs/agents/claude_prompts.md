# Claude Code: Single-file task prompt (T4 / 0.01%)

Use when you want the IDE agent to make a small, safe refactor.

Context:
- Repo: LukhasAI/Lukhas
- Production modules must not have import-time edges to `labs.*`.
- Provider Registry exists under `core/adapters/provider_registry.py`.
- The goal is to remove static `labs.*` imports from a single file and add safe, testable changes.

Template (copy & paste into Claude Code):
-----------------------------------------
FILE:  (set file path, e.g. `core/registry.py`)
BRANCH: `task/lazy-load-<file>-<you>`

1) Create branch:
   `git fetch origin && git checkout -b task/lazy-load-<file>-<you> origin/feat/fix-lane-violation-MATRIZ`

2) Replace import-time `labs` usage:
   - If file is a service or client, use ProviderRegistry:
     ```py
     from core.adapters.provider_registry import ProviderRegistry
     from core.adapters.config_resolver import make_resolver

     def _get_openai_provider():
         reg = ProviderRegistry(make_resolver())
         return reg.get_openai()
     ```
   - Otherwise use a lazy helper:
     ```py
     import importlib
     from typing import Optional, Any
     def _get_labs() -> Optional[Any]:
         try:
             return importlib.import_module("labs")
         except Exception:
             return None
     ```

3) Update call sites to use provider or `_get_labs()` and guard `None` with a clear runtime error message.

4) Add unit test `tests/.../test_<file>_importsafe.py` that asserts `import module` does not crash without `labs` installed. For provider pattern, test by injecting a stub provider.

5) Local checks:
   - `python3 -m venv .venv && . .venv/bin/activate`
   - `pip install -r requirements.txt || true`
   - `pytest tests/... -q`
   - `ruff check core/path/to/file.py --select E,F,W,C`
   - `./scripts/run_lane_guard_worktree.sh` (worktree lane-guard)

6) Commit & push:
   `git add ... && git commit -m "refactor(provider): lazy-load labs in <file>" && git push -u origin task/lazy-load-<file>-<you>`

PR body template:
```

Title: refactor(provider): lazy-load labs in <file>

Summary:

* Replace import-time labs import with provider/lazy-load.
* Unit test added.
  Validation:
* pytest: PASS
* ruff: PASS (targeted)
* Lane-guard: PASS (attached artifact)

```

Stop & ask human if:
- More than 1 file requires changes to make the code work,
- The refactor requires breaking API behavior,
- The agent can't get tests to pass locally.

Safety: Do not commit credentials or change `.importlinter` or `.venv`. Use one file per PR.