# M1 branch / Laptop — Parallel Codemod & Claude Code Work Instructions

- **Codex / automation work (primary)** — run the codemod _dry-run_, run the conservative filter, and prepare `batch-1` archive of safe patches. This is CPU/light IO, non-destructive, and produces an artifact the main machine or reviewers can apply.
- **Claude Code (secondary)** — do 2–3 small surgical edits (different files than the main laptop will touch), add import-safety tests and run local checks. Claude Code will produce small PRs off your `M1` branch.

Both tasks are T4-safe: small, auditable, reversible, and keep humans in the loop. I’ll give exact commands, branch names, agent prompts, and safety checks. Follow them step-by-step on the M1 laptop.

---

## Rules for working in parallel (absolute musts)

1. **Base everything on `M1` branch on the M1 laptop.** Don’t rebase or force-push `feat/*` branches that the main laptop is working on. Use dedicated `task/*` branches.
2. **Never change `.importlinter` or `.venv` in committed form.** Worktree edits for discovery are fine locally, but do not commit them.
3. **One file / one PR for Claude tasks.** Keep PRs tiny.
4. **Codex batches are dry-run → filtered → archive only.** Do not apply safe patches automatically. Main laptop (or reviewer) will apply them after review.
5. **Upload artifacts** (`/tmp/codmod_batch1_patches.tgz`, `artifacts/reports/`) into PR comments or to a shared location for review.

---

## Part A — Codex / automation work on M1 laptop (primary job)

**Goal:** run the codemod `scripts/codemods/replace_labs_with_provider.py` in dry-run mode, filter for conservative patches using the filter script, and build `batch-1` archive `/tmp/codemod_batch1_patches.tgz`. This gives reviewers a guaranteed safe-first batch.

### Step 0 — Checkout the M1 branch

```bash
git fetch origin
git checkout --track -B M1 origin/M1   # or your local name for the M1 branch
git pull --ff origin M1
```

### Step 1 — Prepare work environment

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip setuptools wheel
# install required libs for the codemod and runner
pip install libcst
# (if you plan to run lane-guard or run the runner, install dev deps)
# pip install -r requirements.txt  # optional; do this only if required
```

### Step 2 — Dry-run codemod (produce patches)

```bash
mkdir -p /tmp/codmod_patches
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
ls -1 /tmp/codmod_patches | wc -l
# Inspect a patch
sed -n '1,160p' /tmp/codmod_patches/$(ls /tmp/codmod_patches | head -n1)
```

### Step 3 — Run conservative filter

```bash
# copy filter script to scripts/automation if not present
chmod +x scripts/automation/filter_safe_patches.sh
# run the filter
scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe
```

**What the filter does (quick recap)**

- Keeps only patches that: include `importlib` or `_importlib` AND `getattr(_mod,...)`, don’t delete function/class headers, and have few non-import deletions.
- Writes safe patches into `/tmp/codmod_batches/batch1.safe` and prints flagged patches.

### Step 4 — Create the batch archive

```bash
tar -czf /tmp/codemod_batch1_patches.tgz -C /tmp/codmod_batches batch1.safe
# quick listing:
ls -1 /tmp/codmod_batches/batch1.safe | wc -l
```

### Step 5 — Quick sanity-check (optional)

Open a few of the safe patches and confirm they follow the conservative pattern (importlib + try/getattr + fallback `None`). Example:

```bash
for p in /tmp/codmod_batches/batch1.safe/*.patch; do
  echo "---- $p ----"
  sed -n '1,120p' "$p"
  echo
done | head -n 200
```

### Step 6 — Upload artifact / share

- Upload `/tmp/codemod_batch1_patches.tgz` to the PR or to a shared S3/drive, or create a GitHub Gist with listing for reviewers.
- Add a short comment in your main coordination doc: “Batch-1 ready: `/tmp/codemod_batch1_patches.tgz` — conservative filtered patches. Please review and apply on main machine or via codex orchestrator.”

---

## Part B — Claude Code tasks on M1 laptop (secondary job)

**Goal:** pick 2 small surgical tasks from the ten we prepared — fast wins. I recommend `core/identity.py` and `core/tags/__init__.py` because they’re low-risk and unlikely to conflict if main laptop is doing gpt_colony + registry.

### Branch naming (base `M1`)

- `task/claude-lazy-load-identity-M1`
- `task/claude-lazy-init-tags-M1`

### Per-task commands (do for each)

1. **Create branch**

```bash
git fetch origin
git checkout -B task/claude-lazy-load-identity-M1 origin/M1
```

2. **Start Claude Code in your IDE** and paste the exact prompt from `docs/agents/tasks/02_core_identity.md` (or open that file). Ask Claude Code to:

   - Replace top-level `from labs...` imports with `ProviderRegistry` or `_get_labs()`.
   - Add `tests/core/test_identity_importsafe.py`.
   - Run the local checks noted.

3. **Run local checks** (after Claude finishes edits)

```bash
. .venv/bin/activate
pip install -r requirements.txt || true
python -m py_compile core/identity.py  # quick syntax check
ruff check core/identity.py --select E,F,W,C || true
mypy core/identity.py --ignore-missing-imports || true
pytest tests/core/test_identity_importsafe.py -q || true
./scripts/run_lane_guard_worktree.sh > artifacts/reports/lane_guard_identity.log 2>&1 || true
```

4. **If all good, commit and push**

```bash
git add core/identity.py tests/core/test_identity_importsafe.py
git commit -m "refactor(provider): lazy-load labs in core/identity (M1)"
git push -u origin task/claude-lazy-load-identity-M1
```

5. **Open a PR**

- PR title: `refactor(provider): lazy-load labs in core/identity (M1)`
- PR body: paste the content of the task file (it contains the checklist).
- Attach `artifacts/reports/lane_guard_identity.log` and ruff/mypy outputs.

Repeat analogous steps for `core/tags/__init__.py` with branch `task/claude-lazy-init-tags-M1`.

---

## Agent prompts for this laptop

### Codex prompt (for the dry-run/filter work)

Use this prompt in Codex:

```
Task: Run the lukhas codemod dry-run and produce safe first batch.
Steps:
1) Run: python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
2) Filter conservative patches: scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe
3) Archive the safe batch: tar -czf /tmp/codemod_batch1_patches.tgz -C /tmp/codmod_batches batch1.safe
4) Upload or print the archive path and produce a JSON report with counts (total patches, safe patches, flagged patches).
Constraints: do NOT apply any patches. Provide the archive for human review.
```

### Claude Code prompt (for identity)

Use the exact file `docs/agents/tasks/02_core_identity.md` (it’s already prepared). Instruct Claude to run the local checks and to stop if lane-guard shows a `labs` chain.

If you want, include a short note to Claude: “Keep edits minimal and add one import-safety unit test. If uncertain about provider usage, create a `core/adapters/openai_provider.py` protocol and use that.”

---

## Coordination & conflict avoidance

- **Files chosen**: M1 laptop will do `core/identity.py` and `core/tags/__init__.py`. Main laptop should avoid these files while M1 PRs are in flight. Add them to a daily run-lock (create a run issue with the file list).
- **Codex batch**: Codex patches are only packaged — **do not apply** until main team has reviewed and merged any Claude PRs that would conflict.
- **PR labels**: tag PRs with `agent:claude-M1` or `agent:codex-M1` so reviewers can quickly see origin and machine.

---

## Minimal timeline for M1 laptop

- **Hour 0**: Setup venv, run codemod dry-run, run filter, produce `/tmp/codemod_batch1_patches.tgz`. Upload artifact or share path.
- **Hour 0.5**: Create branch for `identity`, run Claude Code to edit, add test, run validations. Push PR.
- **Hour 1**: Create branch for `tags` and do same.
- **Hour 1.5**: If all PRs pass local checks, open PRs and link codemod archive for main laptop review.
- **Daily**: Update the shared coordination doc with PR links + codemod batch status.

---

## Final small checklist to run on M1 laptop before you start

1. `git fetch origin` and ensure `M1` is up to date.
2. `python3 -m venv .venv && . .venv/bin/activate` and `pip install libcst` (plus ruff/mypy if needed).
3. Run the codemod dry-run + filter script:

   ```bash
   python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
   scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe
   tar -czf /tmp/codemod_batch1_patches.tgz -C /tmp/codmod_batches batch1.safe
   ```

4. Start the Claude edits (identity, tags) as described.
5. Push branches and open PRs with artifacts attached.

---

Next: the exact Copilot/Claude prompt text for the two specific files (identity & tags init) pre-filled with your `M1` branch and ready to paste into the agents
Nice — below are **two ready-to-paste Claude Code prompts** (one per file) **pre-filled for your M1 laptop**.
Each prompt is: deterministic, T4-safe, and includes:

- exact branch name to create (based on `M1`),
- the minimal code change pattern (ProviderRegistry preferred or lazy `_get_labs()`),
- a short import-safe unit test you should add (copy/paste code included),
- the exact commands to run locally (venv, ruff, mypy, pytest, lane-guard),
- commit message, PR body template, and required artifacts to attach,
- stop/escape rules (when the agent must ask a human).

Copy each prompt into Claude Code (or paste into Copilot as guidance), let the agent make the edits, and then run the validations. I kept tests small and non-flaky and used the same validations we agreed earlier.

---

## PROMPT A — `core/identity.py`

**Branch:** `task/claude-lazy-load-identity-M1`
**File:** `core/identity.py`
**Purpose:** Replace import-time `labs` usage with ProviderRegistry or lazy loader and add an import-safety test.

**Prompt (paste into Claude Code)**

````
Task: Make `core/identity.py` import-safe (M1 laptop).

Base branch: origin/M1. Create branch:
  git fetch origin
  git checkout -B task/claude-lazy-load-identity-M1 origin/M1

Goal:
- Remove any top-level `from labs... import ...` or `import labs` in core/identity.py.
- Prefer ProviderRegistry pattern if the module constructs a service client. If the file is only a few helper functions, use a lazy `_get_labs()` helper.
- Add a small import-safety unit test.
- Keep changes minimal and reversible (one-file PR).

Preferred Provider pattern (if the module creates a client/service):
```py
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver
from typing import Any

def _get_openai_provider() -> Any:
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()
````

Use this provider inside runtime functions only; **do not** instantiate at module import-time.

Fallback lazy helper (for small helpers):

```py
import importlib
from typing import Optional, Any

def _get_labs() -> Optional[Any]:
    try:
        return importlib.import_module("labs")
    except Exception:
        return None
```

Then inside functions:

```py
_labs = _get_labs()
if _labs is None:
    raise RuntimeError("labs integration not available")
_labs.governance.identity.some_fn(...)
```

Tests (add file `tests/core/test_identity_importsafe.py`):

```py
def test_import_safe():
    # import-only test: module import must not trigger labs import-time
    import importlib
    importlib.import_module("core.identity")

def test_stub_provider_behavior(monkeypatch):
    # if core.identity exposes a function that uses a provider, stub it
    class StubProvider:
        def do_identity(self, *a, **k):
            return {"id": "stub"}
    from core.identity import some_runtime_function  # replace with actual function name
    # monkeypatch or pass provider if API allows
    # Example: some_runtime_function(provider=StubProvider())
    # Assert correct behavior:
    # assert some_runtime_function(provider=StubProvider()) == expected
```

(If `core.identity` API does not accept a provider injection, create a small wrapper function that accepts a provider for test purposes and leave a TODO to remove later.)

Local validations to run in worktree `.venv`:

```bash
# create & activate venv (if not already)
python3 -m venv .venv && . .venv/bin/activate

# install minimal dev tools (no secrets)
pip install ruff mypy pytest || true

# syntax check
python -m py_compile core/identity.py

# ruff
ruff check core/identity.py --select E,F,W,C > artifacts/reports/ruff_identity.txt 2>&1 || true

# mypy (targeted)
mypy core/identity.py --ignore-missing-imports > artifacts/reports/mypy_identity.txt 2>&1 || true

# run tests (target)
pytest tests/core/test_identity_importsafe.py -q > artifacts/reports/pytest_identity.txt 2>&1 || true

# run lane-guard in worktree (captures import-linter)
./scripts/run_lane_guard_worktree.sh > artifacts/reports/lane_guard_identity.log 2>&1 || true
```

If all checks look OK (ruff warnings acceptable or none, mypy does not show new hard errors, pytest pass or show only stubs), commit and push:

```bash
git add core/identity.py tests/core/test_identity_importsafe.py
git commit -m "refactor(provider): lazy-load labs in core/identity (M1)"
git push -u origin task/claude-lazy-load-identity-M1
```

PR Body (paste into PR):

```
Title: refactor(provider): lazy-load labs in core/identity (M1)

Summary:
- Replace import-time labs usage with ProviderRegistry / lazy-load helper.
- Add tests: tests/core/test_identity_importsafe.py (import-safety + stubbed behavior).
Validation:
- ruff (file) attached: artifacts/reports/ruff_identity.txt
- mypy (file) attached: artifacts/reports/mypy_identity.txt
- pytest attached: artifacts/reports/pytest_identity.txt
- lane-guard run attached: artifacts/reports/lane_guard_identity.log
Checklist:
- [ ] Import-safety test passes
- [ ] ruff checked for changed file
- [ ] mypy file-level OK (no hard errors)
- [ ] lane-guard: Contracts KEPT (or explanation)
```

Stop & ask for human review if:

- The agent must change >1 file to make code compile or tests pass,
- The change requires altering public APIs,
- Lane-guard shows a transitive path to `labs` (post-change).

Make the edits minimal and comment any TODOs (e.g., migrate to ProviderRegistry) in the file header.

```

---

## PROMPT B — `core/tags/__init__.py`
**Branch:** `task/claude-lazy-init-tags-M1`
**File:** `core/tags/__init__.py`
**Purpose:** Replace any `from labs... import *` re-exports with a lazy `__getattr__`/`__dir__` proxy (interim) and add import-safety test.

**Prompt (paste into Claude Code)**

```

Task: Make `core/tags/__init__.py` import-safe (M1 laptop).

Base branch: origin/M1. Create branch:
git fetch origin
git checkout -B task/claude-lazy-init-tags-M1 origin/M1

Goal:

- If `core/tags/__init__.py` re-exports `labs.*` (e.g., `from labs.foo import *`), remove the re-export and implement a lazy proxy using `__getattr__` and `__dir__` that imports labs symbols on attribute access. This is an **interim** safety change; add a TODO to migrate to ProviderRegistry as future improvement.
- Ensure package import (`import core.tags`) does not import `labs` at module import time.

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

- Replace `labs.some_tags_module` with the specific module(s) that were being re-exported (e.g., `labs.tags.registry` or `labs.core.tag_helpers`). If multiple labs modules were re-exported, fold them into `__getattr__` lookup logic or load them lazily on first access.

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

Local validation commands:

```bash
. .venv/bin/activate
pip install ruff mypy pytest || true
python -m py_compile core/tags/__init__.py
ruff check core/tags/__init__.py --select E,F,W,C > artifacts/reports/ruff_tags_init.txt 2>&1 || true
mypy core/tags/__init__.py --ignore-missing-imports > artifacts/reports/mypy_tags_init.txt 2>&1 || true
pytest tests/core/test_tags_init_importsafe.py -q > artifacts/reports/pytest_tags_init.txt 2>&1 || true
./scripts/run_lane_guard_worktree.sh > artifacts/reports/lane_guard_tags_init.log 2>&1 || true
```

Commit and push:

```bash
git add core/tags/__init__.py tests/core/test_tags_init_importsafe.py
git commit -m "chore(tags): lazy-proxy re-exports in core/tags/__init__.py (M1)"
git push -u origin task/claude-lazy-init-tags-M1
```

PR Body:

```
Title: chore(tags): lazy-proxy re-exports in core/tags/__init__.py (M1)

Summary:
- Replace re-exports from labs in core/tags/__init__.py with a lazy __getattr__/__dir__ proxy.
- Add tests ensuring package import is safe and proxy exposes expected names when labs module available.

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

Stop & ask human review if:

- The change needs multiple re-export modules to be brought in (more than 1 labs module),
- The package API cannot be preserved by lazy proxy (manual rework needed),
- Lane-guard still shows a transitive path.

Notes:

- This is an **interim** safe pattern. Add `# TODO: migrate to ProviderRegistry` at the top of the file.
- Keep changes minimal and add documentation comment.

```

---

## Final small operational notes for the M1 laptop

- After the agent edits, **run the validations** exactly as provided and attach `artifacts/reports/*` to the PR.
- If the lane-guard run shows a transitive path to `labs`, copy the `lane_guard` log and paste the direct import-linter chain here — I’ll parse it and tell you the exact minimal file(s) to fix next (leaf-first).
- Use the run-lock: add the two files (`core/identity.py`, `core/tags/__init__.py`) to the daily run issue so the main laptop avoids them while PRs are open.

---

When you paste these prompts into Claude Code (or run the edits), I’ll stand by to review the resulting diffs, help interpret the lane-guard logs, and prepare the next small tasks for GitHub Copilot (inline help) or Codex (batch continuation).
```
