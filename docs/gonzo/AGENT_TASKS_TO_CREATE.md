Nice — I’ll do **both**. Below you’ll get:

* A **ready-to-use 10-file worklist** for **Claude Code** with a precise per-file prompt, branch name, tests to add, and local validation commands (one file → one PR). These are the highest-impact, surgical edits we want human-context agents to do first.
* A **Codex (batch) dry-run plan** to run the codemod over the repo, inspect patches, and produce a safe first batch (20 files) for review. I give exact commands, what to inspect, and the orchestrator commands you already have so Codex can make the PRs safely.

Everything is T4 / 0.01% — conservative, auditable, reversible, and aligned with the safety rules we agreed.

---

## Part A — Claude Code: 10-file priority list (one-file PRs)

**How to use each item**

1. Copy the per-file prompt into Claude Code / Copilot session.
2. Create the branch name shown.
3. Make the conservative provider / lazy-load change. Prefer **ProviderRegistry** when the file acts as a service; otherwise use `_get_labs()` lazy import.
4. Add an import-safety unit test.
5. Run targeted checks (ruff/mypy/pytest) and `./scripts/run_lane_guard_worktree.sh` in the worktree.
6. Commit, push, open PR into `feat/fix-lane-violation-MATRIZ` or into `main` per your flow. Attach `artifacts/reports/*`.

Below are the ten files, each with a one-shot prompt:

---

### 1) `core/colony/gpt_colony_orchestrator.py`

**Branch:** `task/claude-lazy-load-gpt_colony-<you>`
**Why:** High-impact orchestrator that likely instantiates OpenAI/`labs` clients at import-time.

**Prompt (copy/paste)**

```
Open core/colony/gpt_colony_orchestrator.py on branch task/claude-lazy-load-gpt_colony-<you> (from origin/feat/fix-lane-violation-MATRIZ). Remove any top-level 'from labs...' or 'import labs' usage. Prefer ProviderRegistry:

from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _get_openai_provider():
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

Use provider at runtime (not at module import). Add tests:
- tests/gpt/test_gpt_colony_importsafe.py: assert import succeeds without labs and stub provider injection test.

Run:
. .venv/bin/activate
pytest tests/gpt/test_gpt_colony_importsafe.py -q
ruff check core/colony/gpt_colony_orchestrator.py --select E,F,W,C
mypy core/colony/gpt_colony_orchestrator.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit message:
refactor(provider): lazy-load/providerize labs usage in gpt_colony_orchestrator

If lane-guard shows a path, paste the import-linter path here and stop for review.
```

---

### 2) `core/identity.py`

**Branch:** `task/claude-lazy-load-identity-<you>`
**Why:** Mentioned earlier as importing `labs.governance.identity`. Often re-exported or used in governance flows.

**Prompt (copy/paste)**

```
Edit core/identity.py. Remove 'from labs.governance.identity import ...' at module import time. Replace with:
- ProviderRegistry if identity is a service, OR
- _get_labs() lazy loader for small helpers.

Add tests: tests/core/test_identity_importsafe.py to assert import safety and to mock provider for the main functions.

Validation: pytest, ruff, mypy on the file, and run worktree lane-guard.

Commit:
refactor(provider): lazy-load labs in core/identity.py
```

---

### 3) `core/observability/evidence_collection.py`

**Branch:** `task/claude-lazy-load-evidence-<you>`
**Why:** Observability code often imports `labs.observability.*` (side effects/logging) — import-time edges are common.

**Prompt (copy/paste)**

```
Open core/observability/evidence_collection.py. Replace top-level imports from labs.observability.* with lazy import or provider adapter. Keep the external API same. Add tests: tests/observability/test_evidence_importsafe.py (import-only) and a small behavioral test with stubbed module.

Validation: run pytest + ruff + mypy + lane-guard.
Commit: refactor(provider): lazy-load labs in observability/evidence_collection.py
```

---

### 4) `core/dream/hyperspace_dream_simulator.py`

**Branch:** `task/claude-lazy-load-dreamsim-<you>`
**Why:** Dreams frequently import heavy `labs.consciousness.dream.*`; move to plugin or lazy.

**Prompt (copy/paste)**

```
Edit core/dream/hyperspace_dream_simulator.py. Remove import-time calls to labs.*. If the file uses Labs dream engines, move lab-dependent code into labs_integrations/openai_adapter or add _get_labs() and guard runtime functions. Add tests for import safety and a simple behavior test with a stubbed dream engine.

Validation: pytest, ruff, mypy, lane-guard.
Commit msg: refactor(provider): lazy-load labs in hyperspace_dream_simulator.py
```

---

### 5) `core/tags/registry.py`

**Branch:** `task/claude-lazy-load-tags-<you>`
**Why:** Tag registry may import labs for semantics/explanations. Prevent transitive edges.

**Prompt (copy/paste)**

```
Edit core/tags/registry.py: ensure no top-level labs imports. Replace with lazy `__getattr__` of lab helpers or ProviderRegistry calls. Add unit tests: tests/core/test_tag_registry_importsafe.py and ensure registry API unchanged.

Validation: pytest, ruff, mypy, lane-guard.
Commit: refactor(provider): lazy-load labs in core/tags/registry.py
```

---

### 6) `core/tags/__init__.py`

**Branch:** `task/claude-lazy-init-tags-<you>`
**Why:** Re-exports here can hide libs and create transitive edges.

**Prompt (copy/paste)**

```
Open core/tags/__init__.py. If it re-exports labs (e.g., 'from labs... import *'), replace with lazy __getattr__/__dir__ proxy or move re-exports into labs_integrations. Add a small test ensuring `import core.tags` does not import labs.

Validation: ruff, mypy, pytest, lane-guard.
Commit: chore(tags): lazy-proxy re-exports in core/tags/__init__.py
```

---

### 7) `core/adapters/__init__.py`

**Branch:** `task/claude-adapters-init-<you>`
**Why:** Adapters should not re-export labs; this file can expose labs through shims.

**Prompt (copy/paste)**

```
Edit core/adapters/__init__.py to avoid re-exporting labs. Ensure adapters export only lane-safe interfaces, and move any labs-based code to labs_integrations adapters. Add tests for import-safety.

Validation: pytest, ruff, mypy, and lane-guard.
Commit: chore(adapters): remove import-time labs re-exports
```

---

### 8) `core/governance/__init__.py`

**Branch:** `task/claude-gov-init-<you>`
**Why:** Governance shims often import labs.governance.* for identity/ethics.

**Prompt (copy/paste)**

```
Edit core/governance/__init__.py: remove top-level labs imports; replace with lazy proxies or explicit provider facades. Add import-safety test and run validations.

Commit: chore(governance): lazy-load labs re-exports
```

---

### 9) `serve/api/openai_proxy.py` (or similar endpoint)

**Branch:** `task/claude-lazy-load-serve-openai-<you>`
**Why:** Serve layer endpoints can create import-time edges by instantiating clients at module level.

**Prompt (copy/paste)**

```
Edit serve/api/openai_proxy.py: ensure no top-level instantiation of labs/OpenAI clients. Use ProviderRegistry or DI pattern to instantiate provider in request handlers only. Add test for import safety and for endpoint behavior via stub provider.

Validation: pytest, ruff, mypy, lane-guard.
Commit: refactor(provider): lazy-load labs in serve/api/openai_proxy.py
```

---

### 10) `lukhas_website/api.py` (or `lukhas_website/*`)

**Branch:** `task/claude-lazy-load-website-<you>`
**Why:** Website or integration layers sometimes pull in labs for demos/logs.

**Prompt (copy/paste)**

```
Edit lukhas_website/api.py to replace any top-level labs imports with lazy provider or adapter. Add tests to ensure import-safe and that demo routes use stub providers.

Validation: pytest, ruff, mypy, lane-guard.
Commit: refactor(provider): lazy-load labs in lukhas_website/api.py
```

---

**Notes and small checklist for Claude Code PRs**

* Keep each PR single-file where possible.
* Attach `artifacts/reports/*` for ruff/mypy/lane-guard.
* If tests fail because of missing network keys, mock provider or use stub.
* Stop if any change forces API break — escalate to human reviewer.

---

## Part B — Codex dry-run: run codemod and create first 20-file batch

**Goal:** run `replace_labs_with_provider.py` in dry-run, inspect patches, pick a first batch of 20 patches to convert into a PR batch for human review.

**Exact commands to run (one-time)**

1. **Dry-run to produce patches**

```bash
# from repo root
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
ls -1 /tmp/codmod_patches | wc -l    # see how many patches
head -n 1 /tmp/codmod_patches/*.patch  # inspect one example
```

2. **Inspect patches**
   Open several patches (`/tmp/codmod_patches/*.patch`) and verify they are conservative: they should add `import importlib as _importlib` and a `try: _mod = _importlib.import_module("labs.xxx"); NAME = getattr(_mod, "NAME"); ... except: NAME = None`.

If you see anything that *removes functionality* or changes logic, **do not apply** for that file — mark it for manual review.

3. **Select first 20 patches**
   Create a file with the first 20 patches:

```bash
mkdir -p /tmp/codmod_batches
ls -1 /tmp/codmod_patches | head -n 20 > /tmp/codmod_batches/batch1.list
```

4. **Create a branch locally and apply the 20 patches** (supervised)

```bash
git fetch origin
git checkout -B codemod/replace-labs-batch-1 origin/main

# apply each patch from the list
while read -r p; do
  git apply --index "/tmp/codmod_patches/$p" || { echo "patch apply failed: $p"; exit 1; }
done < /tmp/codmod_batches/batch1.list

git commit -m "chore(codemod): replace labs imports (batch 1)"
git push -u origin codemod/replace-labs-batch-1
```

5. **Run ephemeral worktree lane-guard** (validate)

```bash
WT="/tmp/wt_batch1"
git worktree add "$WT" origin/codemod/replace-labs-batch-1
pushd "$WT"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt || true
./scripts/run_lane_guard_worktree.sh || true
# collect artifacts
tar -czf /tmp/codmod_batch1_artifacts.tgz artifacts/reports || true
popd
git worktree remove "$WT" --force
```

6. **Create a PR for batch 1**
   Use `gh` or UI:

```bash
gh pr create --title "codemod: replace labs imports (batch 1)" --body "Batch 1 codemod, attached lane-guard artifacts." --base main --head codemod/replace-labs-batch-1
```

**Safety & manual review**

* Human reviewers must inspect the diff before merging.
* If lane-guard fails, run the parser on the lane-guard artifacts to find the transitive path and fix leaf modules next.
* For patches that touched tests or complex functions, require manual review and unit test runs.

---

## Part C — Reporting & progress

Have Codex produce a small JSON `progress.json` after each batch with:

```json
{
  "batch": 1,
  "patch_count": 20,
  "lane_guard_status": "PASS",
  "artifacts": "/tmp/codmod_batch1_artifacts.tgz",
  "files": ["core__identity.py.patch", "..."]
}
```

Attach to PR. This makes tracking programmatic and easy.

---

## Final notes (operational)

* **Run order I recommend:** Start Claude Code surgical work on the 10 files *in parallel* (each one-file PR). Meanwhile, run the Codex dry-run and prepare batch-1. This gives short-term wins (critical files) while Codex reduces bulk debt.
* **Stop conditions:** Any lane-guard failure, or a patch that removes semantics, or a test failing that indicates API change — stop and escalate.
* **Daily synchronization:** Agents post a daily summary listing PRs created, lane-guard outcomes, and next 10 files. Keep the human reviewers informed.

---
 I prepared two main deliverables for you:

1. **Ten ready-to-use Claude Code prompt files** (one per target file). Put them under `docs/agents/tasks/` and each one is a complete single-file task: branch name, exact edit pattern (ProviderRegistry or lazy `_get_labs()`), test to add, exact local validation commands, commit message, and PR checklist. These are short, deterministic and T4-approved.

2. **A Codex dry-run + batch script** you can run to produce the first **20** codemod patches and assemble them into batch-1 (supervised). It includes the dry-run command, the quick inspection step, a safe apply flow into a branch, ephemeral worktree lane-guard validation, and the `gh pr create` command.

Below are the files / scripts and the exact commands to create/use them. You can either copy/paste the prompt files into the repo, or run the small `create_tasks.sh` script I included to write them for you. After that, run the codemod dry-run steps to create batch-1.

---

## A — Ten Claude Code prompt files (place under `docs/agents/tasks/`)

Create directory `docs/agents/tasks/` and save each of the following as its own `.md` file. Each file is self-contained and ready to paste into Claude Code/Copilot.

---

### 1) `docs/agents/tasks/01_gpt_colony_orchestrator.md`

```
# Task 01 — gpt_colony_orchestrator.py
Branch: task/claude-lazy-load-gpt_colony-<yourname>
Target: core/colony/gpt_colony_orchestrator.py

Goal
Remove import-time dependency on `labs.*` from this orchestrator. Ensure providerization/lazy-load pattern applied and add import-safety tests.

Edit pattern
- Prefer ProviderRegistry when the module instantiates an LLM or other service:
    from core.adapters.provider_registry import ProviderRegistry
    from core.adapters.config_resolver import make_resolver

    def _get_openai_provider():
        reg = ProviderRegistry(make_resolver())
        return reg.get_openai()

- Otherwise add lazy loader:
    import importlib
    from typing import Optional, Any
    def _get_labs() -> Optional[Any]:
        try:
            return importlib.import_module("labs")
        except Exception:
            return None

Changes
- Replace top-level `from labs... import ...` or `import labs` with above patterns.
- Use provider only inside runtime functions, not at module import-time.

Tests (add)
- tests/gpt/test_gpt_colony_importsafe.py
  - test_import_safe: `import core.colony.gpt_colony_orchestrator` must not raise.
  - test_with_stub_provider: instantiate orchestrator with a stub provider and assert behavior.

Local validation commands
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/gpt/test_gpt_colony_importsafe.py -q
ruff check core/colony/gpt_colony_orchestrator.py --select E,F,W,C
mypy core/colony/gpt_colony_orchestrator.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit message
refactor(provider): lazy-load/providerize labs usage in gpt_colony_orchestrator

PR checklist
- [ ] pytest (target) PASS
- [ ] ruff check PASS
- [ ] mypy (file) PASS
- [ ] lane-guard `Contracts: KEPT`
- Attach artifacts: ruff/mypy/lane-guard logs

Stop & escalate if
- More than 1 file must be changed to get behavior to pass
- Tests fail due to API change
- lane-guard shows a new transitive path
```

---

### 2) `docs/agents/tasks/02_core_identity.md`

```
# Task 02 — core/identity.py
Branch: task/claude-lazy-load-identity-<yourname>
Target: core/identity.py

Goal
Remove top-level imports from labs.governance.identity or other labs identity helpers. Replace with ProviderRegistry or lazy import.

Edit pattern
- If identity is a service: use ProviderRegistry
- If small helper functions, use _get_labs() lazy loader

Tests
- tests/core/test_identity_importsafe.py:
  - test_import_safe: `import core.identity` should not import labs at module import.
  - test_stub_provider: verify main functions with a stub provider.

Validation
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/core/test_identity_importsafe.py -q
ruff check core/identity.py --select E,F,W,C
mypy core/identity.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit message
refactor(provider): lazy-load labs in core/identity

PR checklist
- pytest / ruff / mypy / lane-guard artifacts attached
```

---

### 3) `docs/agents/tasks/03_evidence_collection.md`

```
# Task 03 — core/observability/evidence_collection.py
Branch: task/claude-lazy-load-evidence-<yourname>
Target: core/observability/evidence_collection.py

Goal
Remove import-time `labs.observability.*`. Add lazy import/provider facade.

Edit pattern
- Use ProviderRegistry if this module registers or creates observability clients.
- Otherwise use _get_labs() and guard.

Tests
- tests/observability/test_evidence_importsafe.py: import-only safe test and a stubbed behavior test.

Validation
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/observability/test_evidence_importsafe.py -q
ruff check core/observability/evidence_collection.py --select E,F,W,C
mypy core/observability/evidence_collection.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit
refactor(provider): lazy-load labs in observability/evidence_collection.py
```

---

### 4) `docs/agents/tasks/04_hyperspace_dream_simulator.md`

```
# Task 04 — core/dream/hyperspace_dream_simulator.py
Branch: task/claude-lazy-load-dreamsim-<yourname>
Target: core/dream/hyperspace_dream_simulator.py

Goal
Eliminate import-time `labs.consciousness.dream` usage. Move heavy labs-bound code into labs_integrations or make runtime lazily loaded.

Edit pattern
- Move adapters into labs_integrations/openai_adapter or similar.
- Use provider or _get_labs().

Tests
- tests/dream/test_hyperspace_importsafe.py
  - import-only safe test
  - stubbed dream engine behavior test

Validation
Same test/lint/lane-guard commands as others.

Commit
refactor(provider): lazy-load labs in hyperspace_dream_simulator.py
```

---

### 5) `docs/agents/tasks/05_tags_registry.md`

```
# Task 05 — core/tags/registry.py
Branch: task/claude-lazy-load-tags-<yourname>
Target: core/tags/registry.py

Goal
Remove top-level labs imports for explainability/hormone tags. Provide ProviderRegistry or lazy proxy.

Edit pattern
- Avoid importing labs at module import time
- If tags depend on labs for explanations, push those functions into labs_integrations or wrap as runtime calls

Tests
- tests/core/test_tag_registry_importsafe.py - import-safe and a stub-provider explain test

Validation
pytest, ruff, mypy, lane-guard

Commit
refactor(provider): lazy-load labs in core/tags/registry.py
```

---

### 6) `docs/agents/tasks/06_tags_init.md`

```
# Task 06 — core/tags/__init__.py
Branch: task/claude-lazy-init-tags-<yourname>
Target: core/tags/__init__.py

Goal
If __init__ re-exports labs symbols, replace re-export with lazy __getattr__ proxy or move re-export to labs_integrations.

Edit pattern
- Use __getattr__ and __dir__ to lazy-proxy attributes (interim)
- Add comment TODO: migrate to ProviderRegistry

Tests
- tests/core/test_tags_init_importsafe.py - import-only safe test

Validation
ruff, mypy, pytest, lane-guard

Commit
chore(tags): lazy-proxy re-exports in core/tags/__init__.py
```

---

### 7) `docs/agents/tasks/07_adapters_init.md`

```
# Task 07 — core/adapters/__init__.py
Branch: task/claude-adapters-init-<yourname>
Target: core/adapters/__init__.py

Goal
Avoid re-exporting labs in adapters __init__. Keep adapter interface lane-safe.

Edit pattern
- Move labs-based code to labs_integrations adapters.
- Keep core/adapters exposing only Protocols/Interfaces or provider accessors.

Tests
- tests/core/test_adapters_importsafe.py

Validation
ruff, mypy, pytest, lane-guard

Commit
chore(adapters): remove import-time labs re-exports
```

---

### 8) `docs/agents/tasks/08_governance_init.md`

```
# Task 08 — core/governance/__init__.py
Branch: task/claude-gov-init-<yourname>
Target: core/governance/__init__.py

Goal
Move any top-level labs imports into lazy proxies or labs_integrations plugin; ensure governance API unchanged.

Tests
- tests/core/test_governance_importsafe.py

Validation and commit format as before.

Commit
chore(governance): lazy-load labs re-exports
```

---

### 9) `docs/agents/tasks/09_serve_openai_proxy.md`

```
# Task 09 — serve/api/openai_proxy.py
Branch: task/claude-lazy-load-serve-openai-<yourname>
Target: serve/api/openai_proxy.py

Goal
Ensure endpoint does not instantiate labs/OpenAI client at module import. Use ProviderRegistry or DI inside handlers.

Tests
- tests/serve/test_openai_proxy_importsafe.py
- test endpoint behavior with stub provider

Validation + commit as earlier.

Commit
refactor(provider): lazy-load labs in serve/api/openai_proxy.py
```

---

### 10) `docs/agents/tasks/10_website_api.md`

```
# Task 10 — lukhas_website/api.py
Branch: task/claude-lazy-load-website-<yourname>
Target: lukhas_website/api.py

Goal
Replace any module-level labs imports with provider or lazy loader so the website import is lane-safe.

Tests
- tests/website/test_api_importsafe.py
- add stubbed behavior tests for demo endpoints

Validation, commit and PR checklist as above.

Commit
refactor(provider): lazy-load labs in lukhas_website/api.py
```

---

## Quick helper to write these 10 files automatically

If you want, run this (safe) local script to write the ten prompt files into `docs/agents/tasks/`:

```bash
mkdir -p docs/agents/tasks
# Save each of the above blocks as files; example for first file:
cat > docs/agents/tasks/01_gpt_colony_orchestrator.md <<'EOF'
# Task 01 — gpt_colony_orchestrator.py
Branch: task/claude-lazy-load-gpt_colony-<yourname>
Target: core/colony/gpt_colony_orchestrator.py

... [paste entire content of file 1 here] ...
EOF

# Repeat for each file accordingly or copy the block contents above into files.
```

(You can copy-paste each block I gave into its respective file.)

---

## B — Codex dry-run + batch-1 workflow (exact commands)

Run these on the controller machine (supervised):

1. **Dry-run codemod to create patches**

```bash
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
ls -1 /tmp/codmod_patches | wc -l   # how many patches
# Inspect first few patches
for p in /tmp/codmod_patches/*.patch; do sed -n '1,120p' "$p"; break; done
```

2. **Pick first 20 conservative patches**
   If patches look conservative (importlib + try/except + getattr assignments), assemble batch list:

```bash
mkdir -p /tmp/codmod_batches
ls -1 /tmp/codmod_patches | head -n 20 > /tmp/codmod_batches/batch1.list
```

3. **Apply the 20 patches into a fresh branch** (supervised)

```bash
git fetch origin
git checkout -B codemod/replace-labs-batch-1 origin/main

while read -r patchname; do
  patchfile="/tmp/codmod_patches/${patchname}"
  echo "Applying $patchfile"
  git apply --index "$patchfile" || { echo "apply failed: $patchfile"; exit 1; }
done < /tmp/codmod_batches/batch1.list

git commit -m "chore(codemod): replace labs imports (batch 1)"
git push -u origin codemod/replace-labs-batch-1
```

4. **Run ephemeral worktree lane-guard validation**

```bash
WT="/tmp/wt_batch1"
git worktree add "$WT" origin/codemod/replace-labs-batch-1
pushd "$WT"
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt || true
  ./scripts/run_lane_guard_worktree.sh || true
  tar -czf /tmp/codmod_batch1_artifacts.tgz artifacts/reports || true
popd
git worktree remove "$WT" --force
```

5. **Create PR**

```bash
gh pr create --title "codemod: replace labs imports (batch 1)" --body "Batch 1 codemod. Lane-guard artifacts: /tmp/codmod_batch1_artifacts.tgz" --base main --head codemod/replace-labs-batch-1
```

**Inspection & safety**

* **Inspect diffs** in PR. If any change modifies logic (not just rearranging imports), mark for manual review.
* **If lane-guard fails**, parse the import-linter raw graph to find the exact chain and fix the leaf file(s) first.

**Repeat** for subsequent batches.

---

## Final validation & next steps

**When Claude Code PRs are open** (10 files), and **Codex batch-1 PR is open**, do this:

* Wait for lane-guard artifacts for each PR.
* Have Security and Core reviewers confirm PRs (for Codex PRs, review diffs carefully).
* Merge small Claude PRs early to reduce conflicts for Codex batches.
* Run the SLSA pipeline on a small module to validate the attestation process end-to-end.

---
## Optional: Automation script to prepare codemod Batch
To streamline the Codex dry-run and batch preparation, here’s a bash script that automates the process of:

* runs the codemod **in dry-run mode** to produce `.patch` files,
* collects the **first N** patches (default 20),
* writes those patches into a batch folder, and
* creates a single archive `/tmp/codmod_batch1_patches.tgz` you can download and inspect.

The script also does quick sanity checks (ensures each patch is conservative: contains `importlib.import_module` and `getattr(_mod, ...)` patterns) and prints a short review checklist you should follow before applying.

Save as `scripts/automation/prepare_codmod_batch.sh`, make it executable, and run it from the repo root.

---

### Script: `scripts/automation/prepare_codmod_batch.sh`

```bash
#!/usr/bin/env bash
# prepare_codmod_batch.sh
# Run codemod dry-run and assemble first batch of patches into an archive for human review.
#
# Usage:
#   bash scripts/automation/prepare_codmod_batch.sh         # default /tmp/codmod_patches, batch size 20
#   BATCH_SIZE=30 OUTDIR=/tmp/my_patches bash scripts/automation/prepare_codmod_batch.sh
set -euo pipefail

# Configuration (override with env vars)
CODMOD_SCRIPT="${CODMOD_SCRIPT:-scripts/codemods/replace_labs_with_provider.py}"
OUTDIR="${OUTDIR:-/tmp/codmod_patches}"
BATCH_DIR="${BATCH_DIR:-/tmp/codmod_batches}"
BATCH_NAME="${BATCH_NAME:-batch1}"
BATCH_SIZE="${BATCH_SIZE:-20}"
ARCHIVE_PATH="${ARCHIVE_PATH:-/tmp/codemod_${BATCH_NAME}_patches.tgz}"

# Basic preconditions
if [ ! -f "$CODMOD_SCRIPT" ]; then
  echo "ERROR: codemod script not found at $CODMOD_SCRIPT"
  exit 2
fi

echo "[info] Running codemod dry-run -> patches at $OUTDIR"
rm -rf "$OUTDIR"
python3 "$CODMOD_SCRIPT" --outdir "$OUTDIR"

PATCH_COUNT=$(ls -1 "$OUTDIR"/*.patch 2>/dev/null | wc -l || echo 0)
echo "[info] Total patches generated: $PATCH_COUNT"

if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "[warn] No patches produced. Inspect codemod output and try again."
  exit 0
fi

mkdir -p "$BATCH_DIR"
rm -rf "$BATCH_DIR/${BATCH_NAME}" || true
mkdir -p "$BATCH_DIR/${BATCH_NAME}"

echo "[info] Selecting first $BATCH_SIZE patches into $BATCH_DIR/${BATCH_NAME}"
i=0
for p in "$OUTDIR"/*.patch; do
  i=$((i+1))
  if [ "$i" -le "$BATCH_SIZE" ]; then
    cp "$p" "$BATCH_DIR/${BATCH_NAME}/"
  fi
done

SELECTED_COUNT=$(ls -1 "$BATCH_DIR/${BATCH_NAME}"/*.patch 2>/dev/null | wc -l || echo 0)
echo "[info] Selected patches: $SELECTED_COUNT (saved to $BATCH_DIR/${BATCH_NAME})"

# Quick sanity scan: ensure each patch contains importlib & getattr pattern
echo "[info] Performing conservative sanity checks on selected patches..."
bad=0
for p in "$BATCH_DIR/${BATCH_NAME}"/*.patch; do
  has_importlib=$(grep -E "importlib|_importlib" -n "$p" || true)
  has_getattr=$(grep -E "getattr\\(|getattr\\(_mod" -n "$p" || true)
  if [ -z "$has_importlib" ] || [ -z "$has_getattr" ]; then
    echo "[warn] Patch may not be conservative: $p"
    echo "  contains importlib? -> ${has_importlib:-NO}"
    echo "  contains getattr? -> ${has_getattr:-NO}"
    bad=$((bad+1))
  fi
done

if [ "$bad" -gt 0 ]; then
  echo "[warn] $bad patch(es) failed the conservative pattern check. Please review them manually before applying."
else
  echo "[info] All selected patches pass the conservative pattern check."
fi

# Create archive of the batch
echo "[info] Creating archive $ARCHIVE_PATH"
rm -f "$ARCHIVE_PATH" || true
tar -czf "$ARCHIVE_PATH" -C "$BATCH_DIR" "$BATCH_NAME"

echo "[info] Batch archive created: $ARCHIVE_PATH"
echo
echo "=== NEXT STEPS (REVIEW CHECKLIST) ==="
echo "1) Inspect patches in the archive or in directory: $BATCH_DIR/${BATCH_NAME}"
echo "   - For each patch, ensure it:"
echo "      a) Replaces top-level 'from labs...' imports with importlib try/getattr assignments,"
echo "      b) Does not remove non-labs code or change logic other than import reshaping,"
echo "      c) Preserves symbol names (caller code should not break)."
echo
echo "2) Run a quick apply-check on a temp branch before applying:"
echo "   git fetch origin; git checkout -b codemod/preview-batch-1 origin/main"
echo "   cd $(pwd)"  # repo root
echo "   for p in $BATCH_DIR/${BATCH_NAME}/*.patch; do git apply --check \"\$p\" || { echo 'apply-check failed for' \$p; exit 1; }; done"
echo "   echo 'apply-check OK. To actually apply patches:'"
echo "   for p in $BATCH_DIR/${BATCH_NAME}/*.patch; do git apply --index \"\$p\" || { echo 'apply failed for' \$p; exit 1; }; done"
echo "   git commit -m 'chore(codemod): replace labs imports (preview batch1)'; git push -u origin codemod/preview-batch-1"
echo
echo "3) Validate in ephemeral worktree (example):"
echo "   WT=/tmp/wt_preview_batch1; git worktree add \$WT origin/codemod/preview-batch-1; pushd \$WT; python3 -m venv .venv; . .venv/bin/activate; pip install -r requirements.txt || true; ./scripts/run_lane_guard_worktree.sh; popd; git worktree remove \$WT --force"
echo
echo "4) If lane-guard PASS and tests pass, create PR and attach artifacts. If lane-guard fails, run the import-linter path parser to find the exact transitive chain and fix the leaf module(s) first."
echo
echo "[done]"
```

---

### How to run the helper

1. Save the script:

```bash
mkdir -p scripts/automation
# copy the script content above into scripts/automation/prepare_codmod_batch.sh
chmod +x scripts/automation/prepare_codmod_batch.sh
```

2. Run from repo root:

```bash
# default: picks first 20 patches and creates archive at /tmp/codemod_batch1_patches.tgz
bash scripts/automation/prepare_codmod_batch.sh
```

3. To adjust batch size or outdir:

```bash
BATCH_SIZE=30 OUTDIR=/tmp/my_patches bash scripts/automation/prepare_codmod_batch.sh
```

---

### What to inspect in the archive

Open `/tmp/codemod_batch1_patches.tgz` or inspect patches in `/tmp/codmod_batches/batch1/` and check:

* **Conservative pattern**: patch should not contain `from labs` lines; instead it should introduce `importlib` and a `try: _mod = _importlib.import_module("labs...."); VAR = getattr(_mod, "Name") ... except: VAR = None`.
* **No logic removal**: search patch for lines that remove calls to functions or change logic (look for `-    ` lines that delete more than just the import).
* **Naming**: ensure the same exported names are created (preserve API).
* **Tests**: identify files that will need a small import-safety test or provider injection test (Claude Code will do this).

---

### Safety notes (T4 / 0.01%)

* **Dry-run only**: The helper runs the codemod **dry-run**; do not apply patches automatically without review.
* **One branch per batch**: apply your batch into a dedicated branch (e.g., `codemod/replace-labs-batch-1`) and run ephemeral worktree validation before PR.
* **Human review mandatory**: do not merge codemod PRs without human inspection of diffs and lane-guard artifacts.
* **If you see a patch that changes semantics, stop** and mark for manual fix (this patch should not be auto-applied).
* **If lane-guard fails**, do the import-linter path parse to see which module still creates the transitive `labs` edge and fix that module (leaf-first).

---

# Conservative Filter for Codemod Patches

When running large-scale codemods, especially those that modify imports and module dependencies, it's crucial to ensure that the generated patches are safe to apply. This script provides a conservative heuristic filter to identify patches that are likely safe to apply automatically, while flagging potentially risky ones for manual review.

---
## Overview

Below you’ll find:

1. `scripts/automation/filter_safe_patches.sh` — the script (copy/paste).
2. How it works (heuristics).
3. Example runs and next steps.
4. Safety notes and limitations.

---

## 1) Script — `scripts/automation/filter_safe_patches.sh`

Save this file, make it executable (`chmod +x scripts/automation/filter_safe_patches.sh`) and run from the repo root.

```bash
#!/usr/bin/env bash
# scripts/automation/filter_safe_patches.sh
# Conservative filter for codemod patches (heuristic).
# Usage:
#   scripts/automation/filter_safe_patches.sh \
#       --patch-dir /tmp/codmod_patches \
#       --out-dir /tmp/codmod_batches/batch1.safe \
#       --max-non-import-deletions 2 \
#       [--move]
#
# If --move is provided, selected safe patches are copied (or moved) into out-dir.
set -euo pipefail

# defaults
PATCH_DIR="/tmp/codmod_patches"
OUT_DIR="/tmp/codmod_batches/batch1.safe"
MAX_NON_IMPORT_DELETIONS=2
MOVE=false

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --patch-dir) PATCH_DIR="$2"; shift 2 ;;
    --out-dir) OUT_DIR="$2"; shift 2 ;;
    --max-non-import-deletions) MAX_NON_IMPORT_DELETIONS="$2"; shift 2 ;;
    --move) MOVE=true; shift ;;
    --help) echo "Usage: $0 [--patch-dir DIR] [--out-dir DIR] [--max-non-import-deletions N] [--move]"; exit 0 ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

mkdir -p "$OUT_DIR"
TMP_OK_LIST="$(mktemp)"
TMP_BAD_LIST="$(mktemp)"

echo "[info] Filtering patches in: $PATCH_DIR"
echo "[info] Output dir for safe patches: $OUT_DIR"
echo "[info] Threshold non-import deletions: $MAX_NON_IMPORT_DELETIONS"
echo

count_total=0
count_safe=0
count_bad=0

for p in "$PATCH_DIR"/*.patch; do
  [ -e "$p" ] || continue
  count_total=$((count_total+1))
  reason=""
  safe=1

  # 1) must include importlib usage OR _importlib OR getattr(_mod,...)
  if ! grep -E "importlib|_importlib" -n "$p" >/dev/null 2>&1 && ! grep -E "getattr\\(_mod|getattr\\(" -n "$p" >/dev/null 2>&1 ; then
    safe=0; reason="${reason}missing importlib/getattr; "
  fi

  # 2) must NOT still contain a 'from labs' or 'import labs' line (codemod should remove)
  if grep -E "^[+-].*(from|import)\\s+labs(\\.|$)" -n "$p" >/dev/null 2>&1 ; then
    safe=0; reason="${reason}contains leftover labs import; "
  fi

  # 3) check deletions: if there are significant deletions beyond imports, flag
  del_total=$(grep -E '^[+-]' "$p" | wc -l || echo 0)
  del_imports=$(grep -E '^[+-]\s*(from|import)\s+' "$p" | wc -l || echo 0)
  del_non_import=$((del_total - del_imports))

  # If many deletions not related to imports, fail
  if [ "$del_non_import" -gt "$MAX_NON_IMPORT_DELETIONS" ]; then
    safe=0
    reason="${reason}too many non-import deletions (${del_non_import}); "
  fi

  # 4) if deletes a def/class header, flag (deleting function/class definitions is risky)
  if grep -E '^-.*def\s+[A-Za-z0-9_]+' "$p" >/dev/null 2>&1 || grep -E '^-.*class\s+[A-Za-z0-9_]+' "$p" >/dev/null 2>&1; then
    safe=0; reason="${reason}deletes def/class; "
  fi

  # 5) guard against wholesale removals: if patch deletes >10 lines overall, flag
  del_only_count=$(grep -E '^-.*' "$p" | wc -l || echo 0)
  if [ "$del_only_count" -gt 10 ]; then
    safe=0; reason="${reason}large deletion count (${del_only_count}); "
  fi

  if [ "$safe" -eq 1 ]; then
    echo "$p" >> "$TMP_OK_LIST"
    count_safe=$((count_safe+1))
    if [ "$MOVE" = true ]; then
      mv "$p" "$OUT_DIR/"
    else
      cp "$p" "$OUT_DIR/"
    fi
  else
    echo "$p : $reason" >> "$TMP_BAD_LIST"
    count_bad=$((count_bad+1))
  fi
done

echo
echo "=== FILTER SUMMARY ==="
echo "Total patches scanned: $count_total"
echo "Safe patches: $count_safe (copied to $OUT_DIR)"
echo "Flagged patches: $count_bad"
echo

if [ "$count_safe" -gt 0 ]; then
  echo "Safe patch list:"
  nl -ba "$TMP_OK_LIST" || true
  echo
fi

if [ "$count_bad" -gt 0 ]; then
  echo "Flagged patch list (reasons):"
  nl -ba "$TMP_BAD_LIST" || true
  echo
  echo "Recommendation: Inspect flagged patches manually. They may change more than imports (logic removal or significant deletions)."
fi

rm -f "$TMP_OK_LIST" "$TMP_BAD_LIST"
echo "[done]"
```

---

## 2) How the script works (heuristics)

The script is intentionally conservative. For each `.patch` it:

* **Requires** presence of either `importlib` (or `_importlib`) or `getattr` usage — this indicates the codemod produced the conservative lazy-import form.
* **Rejects** patches that still contain `from labs`/`import labs` as deletion or addition lines — this indicates the patch didn't fully remove the static import.
* **Counts deletions**: if there are **more than `MAX_NON_IMPORT_DELETIONS`** (default 2) deletion lines that are not import-related, the patch is flagged as *unsafe* (likely it removes more than just an import).
* **Rejects** patches that delete function or class headers (lines like `-    def foo` or `-class Foo`) — that is a red flag that the patch removes code bodies.
* **Rejects** patches that delete >10 lines total — a simple guard to avoid huge deletions.

If a patch passes all these checks, the script copies it to the safe outdir (or moves it if `--move` specified). The script prints safe & flagged lists and a recommendation to inspect flagged patches manually.

These heuristics aim to prefer **smaller, safer** patches that only reshape imports; they intentionally exclude patches that change logic or remove definitions.

---

## 3) Example run & integration into your flow

1. Produce patches with the codemod dry-run (as earlier):

```bash
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
```

2. Filter safe patches (default 20 later selected by previous helper or all):

```bash
# Filter and copy safe patches into batch folder
scripts/automation/filter_safe_patches.sh --patch-dir /tmp/codmod_patches --out-dir /tmp/codmod_batches/batch1.safe
```

3. Inspect `/tmp/codmod_batches/batch1.safe` or `/tmp/codemod_batch1_patches.tgz` (if you used previous helper) and follow the safe apply workflow:

```bash
# Example quick apply-check
git fetch origin
git checkout -B codemod/preview-batch-1 origin/main
for p in /tmp/codmod_batches/batch1.safe/*.patch; do git apply --check "$p" || { echo "apply-check failed: $p"; exit 1; }; done
# apply
for p in /tmp/codmod_batches/batch1.safe/*.patch; do git apply --index "$p" || { echo "apply failed: $p"; exit 1; }; done
git commit -m "chore(codemod): replace labs imports (preview batch1 safe)"
git push -u origin codemod/preview-batch-1
```

4. Run ephemeral worktree lane-guard:

```bash
WT=/tmp/wt_preview_batch1
git worktree add "$WT" origin/codemod/preview-batch-1
pushd "$WT"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt || true
./scripts/run_lane_guard_worktree.sh
popd
git worktree remove "$WT" --force
```

5. If lane-guard passes, create PR for `codemod/preview-batch-1` → `main` (or to your codemod branch). Attach artifacts and the safe/flagged lists from the filter script.

---

## 4) Safety notes & limitations

* **Heuristic, not perfect**: the script reduces manual review burden but doesn’t guarantee semantic equivalence. Always human-review flagged and safe patches before applying.
* **False negatives**: some safe patches might be flagged (e.g., if the codemod removed a small helper that was unused — deletion > threshold). That’s OK — flagged patches require manual review and are safer.
* **False positives**: unlikely given checks, but still inspect safe patches.
* **No auto-merge**: do not merge batch PRs without human security/core review and lane-guard PASS.

---

### summary


this is a *complement* to the previous workflow I gave. The `prepare_codmod_batch.sh` script creates the batch archive; the new `filter_safe_patches.sh` script is an extra, conservative gate to extract only patches that meet strict heuristics for safety. Both scripts together give you a safe path: **dry-run -> prepare batch -> filter safe patches -> manual review/apply -> lane-guard -> PR**.

---

# Gemini's Infra Tasks for SLSA, Coverage, and Dashboards

---   
Prepared for Gemini, the infra/system/CI designer.


Below I’ve laid out a **T4 / 0.01%** set of *actionable, agent-ready tasks for Gemini* (the system/infra/CI designer). Each task is fully specified: **why**, **what**, **exact files/commands**, **branch/PR names**, **validation**, **secrets**, and **acceptance criteria**. Gemini’s remit here is high-impact infra: **SLSA attestation**, **attestations matrix**, **attestation verification**, **coverage & benchmark pipelines**, and **operational dashboards/telemetry**. These tasks assume the repo already has the agent artifacts you and I prepared.

Work plan: do these tasks in parallel where safe. Start with the SLSA minimal PoC (10 modules) and the coverage pipeline. Both are high ROI: security posture and measurable test coverage.

---

## High-level priority (Gemini)

1. **P1 (immediate):** SLSA attestation pipeline — PoC for 10 modules, automated verification script, CI workflow, secrets runbook.
2. **P1 (parallel):** Coverage pipeline — pytest-cov + Codecov, enforce coverage gates.
3. **P1:** Attestation verification & dashboard: collect attestations, show SLSA coverage metric.
4. **P2:** Performance harness & nightly baselines (pytest-benchmark or asv).
5. **P2:** Datadog/NewRelic dashboards & alerts (WaveC, endocrine, guard).
6. **P3:** Automation to rotate keys, handle attestations long-term and integrate with release process.

Each task below is self-contained for Gemini to run or to hand to Codex for code generation.

---

# Task A — SLSA Attestation Pipeline (PoC for 10 modules)

**Goal:** Produce signed attestations for builds of modules and wire them into CI. Provide a verification script and integrate into the security posture report.

**Deliverables**

* `.github/workflows/slsa-attest-matrix.yml` — GitHub Actions workflow that builds artifacts for a matrix of modules and produces attestations (in-toto/cosign).
* `scripts/automation/run_slsa_for_module.sh` — local helper to produce attestation (in-toto + cosign) for a module.
* `scripts/verify_attestation.py` — verify signature + provenance.
* `docs/gonzo/SLSA_RUNBOOK.md` — how to create keys, rotate, and validate attestations.
* PR: `task/gemini-slsa-poc` with the above files.

**Detailed plan & files**

1. **Module selection**

   * Create `config/slsa_modules.yml` listing the first 10 modules (explicit names). Example:

     ```yaml
     modules:
       - core
       - serve
       - governance
       - core/tags
       - core/colony
       - core/endocrine
       - core/memory
       - core/dream
       - lukhas_website
       - MATRIZ
     ```
   * Branch: `task/gemini-slsa-poc`.

2. **GH Action: `.github/workflows/slsa-attest-matrix.yml`**

   * Matrix job over modules in `config/slsa_modules.yml`.
   * Steps:

     * Checkout
     * Setup Python & environment
     * Run `python3 scripts/automation/run_slsa_for_module.sh --module $MODULE` which:

       * Builds module artifact (wheel or a small tar for the module)
       * Runs `in-toto-run` to capture `build` step
       * Uses `cosign` to sign the artifact and upload the signature
       * Uploads the attestation artifact to job artifacts
   * Use secrets: `COSIGN_KEY` (private key), `IN_TOTO_KEY` (private key). Use minimal-permission secrets.
   * Keep artifacts for 90 days.

   Example snippet (in Action):

   ```yaml
   strategy:
     matrix:
       module: [core, serve, governance, core/tags, ...]
   steps:
     - uses: actions/checkout@v4
     - name: Setup Python
       uses: actions/setup-python@v4
       with: {python-version: '3.11'}
     - name: Run SLSA attestation
       env:
         COSIGN_KEY: ${{ secrets.COSIGN_KEY }}
         IN_TOTO_KEY: ${{ secrets.IN_TOTO_KEY }}
       run: |
         bash scripts/automation/run_slsa_for_module.sh --module "${{ matrix.module }}"
   ```

3. **`scripts/automation/run_slsa_for_module.sh`**

   * Inputs: `--module` (path), `--outdir`

   * Steps:

     * Create isolated venv, install deps
     * Build artifact (example for Python: `python -m pip wheel . -w dist/<module>`; for module-only, package minimal tar)
     * Use `in-toto-run -n build` to capture build step (in-toto identifies step owner). Command:

       ```bash
       in-toto-run -n build -- python -m pip wheel . -w dist
       ```
     * Sign artifacts with `cosign sign --key $COSIGN_KEY dist/*.whl`
     * Produce a small JSON attestation record: module, git_sha, artifact_name, cosign signature, in-toto step layout/artifacts.
     * Upload attestation as artifact.

   * Implementation note: ensure build is deterministic and that the job records `git rev-parse HEAD` and runtime env.

4. **`scripts/verify_attestation.py`**

   * Inputs: attestation JSON or artifact path + public cosign key / in-toto layout.
   * Validates:

     * cosign signature verifies with public key
     * in-toto provenance is intact
     * git SHA in attestation matches expected artifact
   * Return non-zero if verification fails.

5. **`docs/gonzo/SLSA_RUNBOOK.md`**

   * Steps for operators to add `COSIGN_KEY`/`IN_TOTO_KEY` into GitHub secrets (use ephemeral key files and separate keys for CI).
   * How to verify artifacts locally: `python scripts/verify_attestation.py --artifact path`.
   * Rotation: commands to generate new cosign keys and rotate them (`cosign generate-key-pair`), then re-sign or re-attest.

**Validation**

* The workflow must run for the matrix on a test branch and generate artifacts.
* `scripts/verify_attestation.py` must verify an attestation created by the PoC.
* Add a small `security_posture_report.json` entry showing SLSA coverage percent (modules attested / total modules planned).

**Acceptance**

* Attestations for first 10 modules produced and verified. CI job output attached.

---

# Task B — Attestation verification & Security dashboard

**Goal:** Aggregate attestations, compute coverage, and expose SLSA percent as a metric in the security posture report and a GitHub Actions check.

**Deliverables**

* `scripts/automation/collect_attestations.py` — ingest GitHub artifacts or S3 location and aggregate attestations into `security_posture_report.json`.
* A lightweight dashboard JSON for your monitoring (example Datadog dashboard spec) and a GH Action `slsa-coverage.yml` that fails if coverage < threshold.

**What to build**

1. `collect_attestations.py`:

   * Scans artifacts for attestations (CI artifacts or a known S3/Blob path),
   * Verifies signatures via `verify_attestation.py`,
   * Computes coverage = attested_modules / target_modules,
   * Writes `security_posture_report.json`.

2. `slsa-coverage.yml`

   * Trigger: push to main or cron daily,
   * Steps: `collect_attestations.py` and fail if coverage < 80%.

**Validation**

* Run against PoC artifacts; expect coverage >= 10/82 (for PoC first 10). For real acceptance, target 80% eventually.

---

# Task C — Coverage pipeline + Codecov gate

**Goal:** Add test coverage reporting and hard gating so PRs must maintain minimum coverage on critical modules.

**Deliverables**

* `.github/workflows/coverage.yml` — collects coverage via `pytest --cov`, uploads coverage.xml to Codecov.
* `scripts/ci/check_coverage.py` — reads coverage XML, ensures per-module coverage above thresholds (e.g., 80% for core modules). Return non-zero if failed.
* Update PR template to require a coverage badge.

**Example GH Action snippet**

```yaml
- name: Run tests and coverage
  run: |
    pip install pytest pytest-cov codecov
    pytest --cov=MATRIZ --cov-report=xml
- name: Upload coverage
  uses: codecov/codecov-action@v4
```

**Local validation**

```bash
pytest --cov=MATRIZ --cov-report=xml
python scripts/ci/check_coverage.py --report coverage.xml --threshold 0.80
```

**Acceptance**

* `check_coverage.py` returns success for baseline tests on main.

---

# Task D — Performance harness & nightly baselines

**Goal:** Create a benchmark suite for key subsystems (MATRIZ hot paths, endocrine update, WaveC checkpointing) and a nightly CI job to record baselines.

**Deliverables**

* `benchmarks/` folder with `benchmark_endocrine.py`, `benchmark_matriz_cycle.py` using `pytest-benchmark` or `asv`.
* `.github/workflows/benchmarks-nightly.yml` — nightly run saves `benchmarks/baseline-YYYYMMDD.json` artifacts and posts a summary.

**Example test** (pytest-benchmark)

```py
def test_matriz_cycle_benchmark(benchmark):
    def run_cycle():
        # call into MATRIZ minimal synthetic cycle
        from MATRIZ.orchestration import cycle_once
        cycle_once(seed=42)
    benchmark(run_cycle)
```

**Acceptance**

* Nightly job runs and stores artifacts; performance regressions trigger an alert (e.g., >10% slowdown).

---

# Task E — Datadog/NewRelic dashboards & alerts (WaveC & Endocrine)

**Goal:** Wire key metrics and provide a dashboard with SLOs and alerts.

**Deliverables**

* Dashboard JSON for Datadog with widgets for:

  * `lukhas.wavec.snapshot.count` (per-run),
  * `lukhas.wavec.rollback.rate`,
  * `lukhas.endocrine.hormone.cortisol.level`,
  * `lukhas.decision.explain.time`,
  * lane-guard daily failures (converted to metric).
* Alerts:

  * `wavec.rollback.rate > 0.1%` last 24h → PagerDuty/Slack,
  * `endocrine.cortisol > saturation` → Ops page,
  * `slsa.coverage < 0.8` → Security channel.

**Exact steps**

1. Produce a `scripts/telemetry/datadog_dashboard.json` skeleton with widgets and pre-populated queries. Put under `docs/gonzo/monitoring/`.
2. Provide `docs/gonzo/DATADOG_RUNBOOK.md` with steps to import the dashboard and configure alerts.

**Acceptance**

* Dashboard imported and shows test metrics when you run a local test that posts sample metrics.

---

# Task F — Key management & rotation runbook

**Goal:** Provide short, exact steps for operators to generate cosign and in-toto keys, store them in GitHub secrets or vault, and rotate them.

**Deliverables**

* `docs/gonzo/SLSA_KEY_RUNBOOK.md` with commands:

  * `cosign generate-key-pair` instructions,
  * `in-toto-key generation` and `in-toto-run` notes,
  * `cosign verify` steps,
  * Key rotation steps and how to re-attest old artifacts if necessary.

**Acceptance**

* Operator can create keys locally and verify a PoC artifact.

---

# Implementation details, secrets & safety

**Secrets needed (minimum)**

* `COSIGN_KEY` (private key for cosign) stored in GitHub Secrets — rotated regularly.
* `COSIGN_PUB` (public key) available publicly for verification.
* `IN_TOTO_KEY` (private key for signing in-toto steps).
* Optional: artifact storage credentials (S3 / Azure Blob) if attestation artifacts need to be centralized.

**Safety**

* Keys must be created in secure environment and limited to CI user. Use Key Vault / Secret Manager.
* Use short TTL for temporary CI keys if possible; rotate and publish new public key to `docs/gonzo` runbook.

---

# Branches & PR names (Gemini standard)

* `task/gemini-slsa-poc` — SLSA PoC for 10 modules
* `task/gemini-slsa-verify` — verification scripts + collect attestations
* `task/gemini-coverage-pipeline` — coverage CI + check_coverage.py
* `task/gemini-benchmarking` — benchmarks & nightly workflow
* `task/gemini-monitoring` — datadog dashboard & runbook
* `task/gemini-key-runbook` — key generation + rotation docs

**Commit message format**: `chore(slsa): add attestation pipeline (10-module PoC)` etc.

---

# Precise PR templates (what to include)

For SLSA PRs include:

* Short summary, security rationale, list of modules in matrix, secrets required and notes about who to add as secret owner, runbook link, sample verification output.
* Attach attestation artifacts from PoC run in Check stage.

For Coverage pipeline include: coverage badge example and `scripts/ci/check_coverage.py` usage.

---

# Time estimates & parallelism

* SLSA PoC (10 modules): ~1–2 days (dev + initial CI runs), depending on available secrets and CI speed.
* Verify & collect: 0.5–1 day.
* Coverage pipeline: 1–2 days to integrate and validate per-module thresholds.
* Benchmarks & dashboards: 1–2 weeks for good baselines and alert tuning.

---

# Agent prompts for Gemini

Use these short prompts for Gemini (copy/paste into Gemini):

**SLSA PoC prompt**:

> Create a SLSA attestation PoC in `task/gemini-slsa-poc`. Add a GitHub Actions workflow `.github/workflows/slsa-attest-matrix.yml` that runs a matrix for the modules listed in `config/slsa_modules.yml` and uses `in-toto` and `cosign` to build and sign artifacts. Add `scripts/automation/run_slsa_for_module.sh` to perform local attestation and `scripts/verify_attestation.py` to verify signatures. Add `docs/gonzo/SLSA_RUNBOOK.md` describing secrets and rotation. Show sample verification output for one module.

**Coverage pipeline prompt**:

> Add a coverage workflow `.github/workflows/coverage.yml` that runs pytest with `--cov` and uploads to Codecov. Add `scripts/ci/check_coverage.py` to enforce module-level thresholds. Document how to configure Codecov and thresholds.

**Benchmark prompt**:

> Add `benchmarks/` with a pytest-benchmark test for MATRIZ cycle and endocrine updates. Add `.github/workflows/benchmarks-nightly.yml` to run nightly and upload artifacts. Provide example baseline files and instructions.

**Monitoring prompt**:

> Produce a Datadog dashboard JSON `docs/gonzo/monitoring/datadog_wavec_endocrine.json` with specific widgets for `lukhas.wavec.snapshot.count`, `lukhas.wavec.rollback.rate`, `lukhas.endocrine.*`, and `lukhas.lane_guard.failures`. Add `docs/gonzo/DATADOG_RUNBOOK.md` that explains import and alert rules.

---

## Final acceptance: what Gemini must hand over

For each task Gemini completes, the PR must include:

1. Code & config files (workflow scripts and helpers), committed to `task/gemini-*` branch.
2. Example run (CI or local) with artifacts and `tar.gz` of attestations/coverage/benchmarks.
3. `docs/gonzo/*` runbook pages for operators (secrets + verify + rotate).
4. A verification run where `scripts/verify_attestation.py` successfully verifies at least one artifact.
5. A final comment mapping how this improves the audit metrics (SLSA coverage, coverage percent, benchmarks baseline).

---

If you’d like I can:

* Produce the **exact** template files (`run_slsa_for_module.sh`, `verify_attestation.py`, `collect_attestations.py`, `check_coverage.py`, `benchmarks/*`) ready to commit (I can paste them next).
* Or you can ask Gemini to implement the PRs with the prompts above and I’ll review.

Which do you prefer: **(1)** I paste the exact helper scripts and workflow files now, or **(2)** you want to hand the Gemini prompts directly and have Gemini author the files?

Nice — I’ve prepared two things you asked for:

1. **Exact `gh` CLI secrets commands + operator guidance** so you (or an operator) can safely add the CI secrets needed for SLSA/`cosign`/`in-toto`. This includes recommended key generation commands and how to store and rotate keys safely.

2. **A PR body + metadata** ready to paste when you open `task/gemini-slsa-poc`. It includes reviewers, labels, acceptance checklist, and the `gh pr create` command you can run.

After that I’ll give you **small, concrete task packs** for **Claude Code** and **GitHub Copilot** so you can start the surgical edits in parallel (one-file PRs), with branch names, commit messages and validation steps. Let’s go.

---

## 1) Secrets & key management — exact `gh` commands + runbook (operator-friendly)

> **Important safety notes**
>
> * **Never** commit private keys into the git repo. Use GitHub Secrets (or your secret manager).
> * Keep private keys limited to CI use and rotate them frequently (e.g., 90 days).
> * Store the **public** cosign key in a public doc or repository file (`docs/gonzo/cosign_pub.pem`) so verification is easy and auditable.

### Step A — Generate keys locally (example)

**cosign (recommended local key pair)**

```bash
# Install cosign (follow instructions); then:
cosign generate-key-pair
# This creates cosign.key (private) and cosign.pub (public) in cwd.
# Keep cosign.key secret.
```

**in-toto (private key)**

We’ll use an RSA key for in-toto step signing:

```bash
# generate 2048-bit RSA private key:
openssl genpkey -algorithm RSA -out in_toto_key.pem -pkeyopt rsa_keygen_bits:2048
# You can extract public key:
openssl rsa -in in_toto_key.pem -pubout -out in_toto_pub.pem
```

(Or use in-toto keygen tooling if you prefer; above is simple and portable.)

---

### Step B — Add secrets to GitHub (exact `gh` commands)

Replace `LukhasAI/Lukhas` with your repo owner/name if different.

**Upload cosign private key (as secret):**

```bash
# From the repo root, where cosign.key exists
gh secret set COSIGN_KEY --repo LukhasAI/Lukhas --body "$(cat cosign.key)"
```

**Upload cosign public key (optional - not secret):**

You **can** store the public key as a secret, but it’s better to commit `docs/gonzo/cosign_pub.pem` (public) into the repo to ease verification. If you prefer it as a secret:

```bash
gh secret set COSIGN_PUB --repo LukhasAI/Lukhas --body "$(cat cosign.pub)"
```

**Upload in-toto private key:**

```bash
gh secret set IN_TOTO_KEY --repo LukhasAI/Lukhas --body "$(cat in_toto_key.pem)"
```

**(Optional) Cosign passphrase** — if your cosign key is passphrase-protected:

```bash
gh secret set COSIGN_PASSPHRASE --repo LukhasAI/Lukhas --body "your-passphrase-here"
```

> **Operator tip:** For larger orgs prefer a dedicated secrets vault and give the CI runner scoped access to the key only during the job.

---

### Step C — How CI will use the secrets (example snippet)

Inside the GitHub Action job:

```yaml
- name: Write keys to disk
  run: |
    echo "${{ secrets.COSIGN_KEY }}" > cosign.key
    chmod 600 cosign.key
    echo "${{ secrets.IN_TOTO_KEY }}" > in_toto_key.pem
    chmod 600 in_toto_key.pem
```

Then use `cosign` / `in-toto-run` referencing the files written above.

**After the job** make sure to `shred` or delete local copies if you explicitly write them in a runner, but GitHub Actions ephemeral runners are ephemeral — still, be explicit:

```bash
rm -f cosign.key in_toto_key.pem
```

---

### Step D — Key rotation (quick runbook)

1. Generate new key pair on secure host.
2. Put new public key into `docs/gonzo/cosign_pub.pem` (a PR) or update your secrets/registry.
3. Update `COSIGN_KEY` secret with new private key via `gh secret set ...`.
4. Re-run attestation pipeline for newly-created artifacts (rebuild + re-attest if you need historical artifacts re-signed).
5. Revoke old keys if using a key service (KMS) and record rotation in the runbook.

---

## 2) PR body & metadata for `task/gemini-slsa-poc`

**Branch:** `task/gemini-slsa-poc`
**Title:**

```
chore(slsa): add SLSA attestation PoC for 10 modules + verify/collect helpers
```

**PR Body (copy / paste)**

````markdown
## Summary

This PR adds a SLSA attestation Proof-of-Concept (PoC) and verification helpers for an initial set of modules (10).  
It provides CI workflow, local helper scripts, and verification tooling to produce and verify provenance + signed artifacts.

### What’s included
- `config/slsa_modules.yml` — list of the 10 PoC modules
- `scripts/automation/run_slsa_for_module.sh` — build + in-toto link + cosign sign, emits attestation JSON
- `scripts/verify_attestation.py` — verify SHA256 and cosign signature (and report in-toto link presence)
- `scripts/automation/collect_attestations.py` — scan and verify attestations, writes `security_posture_report.json`
- `.github/workflows/slsa-attest-matrix.yml` — GH Action matrix for PoC
- `docs/gonzo/SLSA_RUNBOOK.md` — operator runbook: keys, rotate, verify
- `scripts/ci/check_coverage.py` — helper for coverage gating (included for cross-reference)
- Benchmarks & runbook skeletons (for downstream tasks)

### Why
- Improves supply-chain security by generating attestations for early critical modules.
- Provides operators a repeatable workflow and a verification tool.
- Lays the groundwork to reach SLSA coverage targets (target: 80% modules attested).

### Secrets required
(Configure via GitHub repository secrets)
- `COSIGN_KEY` — cosign private key (content)
- `IN_TOTO_KEY` — in-toto private key (content)
- Optionally: `COSIGN_PASSPHRASE` if cosign key is encrypted

**Important:** Never commit private keys into the repository. Use GitHub Secrets.

---

## How to run locally

1. Generate keys (local PoC):
   ```bash
   cosign generate-key-pair
   openssl genpkey -algorithm RSA -out in_toto_key.pem -pkeyopt rsa_keygen_bits:2048
   export COSIGN_KEY=$(pwd)/cosign.key
   export IN_TOTO_KEY=$(pwd)/in_toto_key.pem
````

2. Attest a module:

   ```bash
   bash scripts/automation/run_slsa_for_module.sh --module core --outdir ./slsa_out
   python3 scripts/verify_attestation.py --att ./slsa_out/core-attestation.json --cosign-pub ./cosign.pub
   ```

3. Collect attestations:

   ```bash
   python3 scripts/automation/collect_attestations.py --att-dir ./slsa_out --cosign-pub ./cosign.pub --out security_posture_report.json
   ```

### Acceptance Criteria

* PoC workflow runs and creates attestations for the listed 10 modules.
* `verify_attestation.py` successfully verifies an attestation created by the PoC.
* `collect_attestations.py` produces a `security_posture_report.json` with verified count and percentage.
* Runbook `docs/gonzo/SLSA_RUNBOOK.md` is reviewed by Security and Ops and contains secret handling & rotation steps.

### Reviewers (suggested)

* `@owner_ops` — Platform & ops
* `@security_team` — Security lead
* `@owner_ml` — Research/ML owner
* `@guardian_owner` — Ethics/Guardian

### Labels

* `security`, `infrastructure`, `T4`, `audit`

---

Please run the PoC workflow in GitHub Actions or run local commands above and attach the generated attestation artifact(s) and `security_posture_report.json` to the PR for review.

````

**One-liner to open the PR (fill repo owner/name):**

```bash
gh pr create --repo LukhasAI/Lukhas --head task/gemini-slsa-poc --base main \
  --title "chore(slsa): add SLSA attestation PoC for 10 modules + verify/collect helpers" \
  --body-file - <<'PRBODY'
(paste the PR body YAML/content above here)
PRBODY
````

---

## 3) Next: Task packs for Claude Code & GitHub Copilot

You asked to focus on those next — here’s a short plan to run right after the PR is open and secrets added.

### Claude Code: immediate 3-file sprint (highest ROI)

1. `core/colony/gpt_colony_orchestrator.py` — providerize (branch `task/claude-lazy-load-gpt_colony-<you>`).
2. `core/registry.py` — lazy-load registry / move re-export (branch `task/claude-lazy-load-registry-<you>`).
3. `core/tags/registry.py` — make import-safe (branch `task/claude-lazy-load-tags-<you>`).

**Prompt**: use the Exact prompts we saved under `docs/agents/tasks/01_gpt_colony_orchestrator.md` etc. Each job should run `ruff`, `mypy` (file), and `./scripts/run_lane_guard_worktree.sh` and attach artifacts to PR.

### GitHub Copilot: real-time in-editor helper

* Use Copilot while editing to generate small helper functions, docstrings, and tests.
* Always require Claude Code to review Copilot's suggestions before commit. Copilot should not be given permission to auto-commit.

**Copilot guidance snippet (for the developer in VS Code):**

```
Prompt to Copilot: "Rewrite this top-level labs import into an in-module provider accessor using ProviderRegistry. Provide two options: (A) ProviderRegistry use inside runtime functions, (B) lazy _get_labs helper. Also show a short unit test showing how to inject a stub provider."
```

---

## Final steps I recommend you do now

1. **Create the secrets** using the `gh secret set` commands above (or your secret manager).
2. **Create the PR `task/gemini-slsa-poc`** using the PR body above and request the reviewers.
3. **Kick off Claude Code**: hand the `docs/agents/tasks/*` files to Claude Code agents (or run the `create_tasks.sh` helper if you prefer). Start with the 3-file sprint.
4. **Run the codemod dry-run + filter** to prepare batch-1 for Codex using the helper scripts (we built earlier). Inspect `batch1.safe` patches, then allow Codex to create `codemod/replace-labs-batch-1` and run ephemeral lane-guard.

--

Sweet — I prepared a single, safe script that when run from your repo root will:

* create the directory `docs/agents/tasks/`,
* write the **10 Claude Code task files** (one per file, exactly as we specified),
* create a branch `task/claude-tasks-setup` based on `origin/feat/fix-lane-violation-MATRIZ` (so it’s aligned with your ongoing work),
* commit the files in a single commit, and
* push the branch to `origin`.

Run it locally, inspect the branch/PR yourself, and then hand the files to your Claude Code agents. I kept the script conservative and it will **not** overwrite other files outside that folder.

---

### Script: create_claude_tasks.sh

Copy the script below into a file (e.g., `scripts/create_claude_tasks.sh`), review it, then run:

```bash
chmod +x scripts/create_claude_tasks.sh
./scripts/create_claude_tasks.sh
```

If you prefer, run it in a dry-run shell first or paste it here and I can adjust it.

```bash
#!/usr/bin/env bash
# scripts/create_claude_tasks.sh
# Creates 10 Claude Code task files under docs/agents/tasks and pushes a branch
set -euo pipefail

BRANCH="task/claude-tasks-setup"
REMOTE="${REMOTE:-origin}"
BASE="${BASE:-origin/feat/fix-lane-violation-MATRIZ}"

echo "[info] Creating Claude Code task files under docs/agents/tasks/"
mkdir -p docs/agents/tasks

cat > docs/agents/tasks/01_gpt_colony_orchestrator.md <<'EOF'
# Task 01 — gpt_colony_orchestrator.py
Branch: task/claude-lazy-load-gpt_colony-<yourname>
Target: core/colony/gpt_colony_orchestrator.py

Goal
Remove import-time dependency on `labs.*` from this orchestrator. Ensure providerization/lazy-load pattern applied and add import-safety tests.

Edit pattern
- Prefer ProviderRegistry when the module instantiates an LLM or other service:
    from core.adapters.provider_registry import ProviderRegistry
    from core.adapters.config_resolver import make_resolver

    def _get_openai_provider():
        reg = ProviderRegistry(make_resolver())
        return reg.get_openai()

- Otherwise add lazy loader:
    import importlib
    from typing import Optional, Any
    def _get_labs() -> Optional[Any]:
        try:
            return importlib.import_module("labs")
        except Exception:
            return None

Changes
- Replace top-level `from labs... import ...` or `import labs` with above patterns.
- Use provider only inside runtime functions, not at module import-time.

Tests (add)
- tests/gpt/test_gpt_colony_importsafe.py
  - test_import_safe: `import core.colony.gpt_colony_orchestrator` must not raise.
  - test_with_stub_provider: instantiate orchestrator with a stub provider and assert behavior.

Local validation commands
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/gpt/test_gpt_colony_importsafe.py -q
ruff check core/colony/gpt_colony_orchestrator.py --select E,F,W,C
mypy core/colony/gpt_colony_orchestrator.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit message
refactor(provider): lazy-load/providerize labs usage in gpt_colony_orchestrator

PR checklist
- [ ] pytest (target) PASS
- [ ] ruff check PASS
- [ ] mypy (file) PASS
- [ ] lane-guard `Contracts: KEPT`
- Attach artifacts: ruff/mypy/lane-guard logs

Stop & escalate if
- More than 1 file must be changed to get behavior to pass
- Tests fail due to API change
- lane-guard shows a new transitive path
EOF

cat > docs/agents/tasks/02_core_identity.md <<'EOF'
# Task 02 — core/identity.py
Branch: task/claude-lazy-load-identity-<yourname>
Target: core/identity.py

Goal
Remove top-level imports from labs.governance.identity or other labs identity helpers. Replace with ProviderRegistry or lazy import.

Edit pattern
- If identity is a service: use ProviderRegistry
- If small helper functions, use _get_labs() lazy loader

Tests
- tests/core/test_identity_importsafe.py:
  - test_import_safe: `import core.identity` should not import labs at module import.
  - test_stub_provider: verify main functions with a stub provider.

Validation
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/core/test_identity_importsafe.py -q
ruff check core/identity.py --select E,F,W,C
mypy core/identity.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit message
refactor(provider): lazy-load labs in core/identity

PR checklist
- pytest / ruff / mypy / lane-guard artifacts attached
EOF

cat > docs/agents/tasks/03_evidence_collection.md <<'EOF'
# Task 03 — core/observability/evidence_collection.py
Branch: task/claude-lazy-load-evidence-<yourname>
Target: core/observability/evidence_collection.py

Goal
Remove import-time `labs.observability.*`. Add lazy import/provider facade.

Edit pattern
- Use ProviderRegistry if this module registers or creates observability clients.
- Otherwise use _get_labs() and guard.

Tests
- tests/observability/test_evidence_importsafe.py: import-only safe test and a stubbed behavior test.

Validation
. .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/observability/test_evidence_importsafe.py -q
ruff check core/observability/evidence_collection.py --select E,F,W,C
mypy core/observability/evidence_collection.py --ignore-missing-imports
./scripts/run_lane_guard_worktree.sh

Commit
refactor(provider): lazy-load labs in observability/evidence_collection.py
EOF

cat > docs/agents/tasks/04_hyperspace_dream_simulator.md <<'EOF'
# Task 04 — core/dream/hyperspace_dream_simulator.py
Branch: task/claude-lazy-load-dreamsim-<yourname>
Target: core/dream/hyperspace_dream_simulator.py

Goal
Eliminate import-time `labs.consciousness.dream` usage. Move heavy labs-bound code into labs_integrations or make runtime lazily loaded.

Edit pattern
- Move adapters into labs_integrations/openai_adapter or similar.
- Use provider or _get_labs().

Tests
- tests/dream/test_hyperspace_importsafe.py
  - import-only safe test
  - stubbed dream engine behavior test

Validation
Same test/lint/lane-guard commands as others.

Commit
refactor(provider): lazy-load labs in hyperspace_dream_simulator.py
EOF

cat > docs/agents/tasks/05_tags_registry.md <<'EOF'
# Task 05 — core/tags/registry.py
Branch: task/claude-lazy-load-tags-<yourname>
Target: core/tags/registry.py

Goal
Remove top-level labs imports for explainability/hormone tags. Provide ProviderRegistry or lazy proxy.

Edit pattern
- Avoid importing labs at module import time
- If tags depend on labs for explanations, push those functions into labs_integrations or wrap as runtime calls

Tests
- tests/core/test_tag_registry_importsafe.py - import-safe and a stub-provider explain test

Validation
pytest, ruff, mypy, lane-guard

Commit
refactor(provider): lazy-load labs in core/tags/registry.py
EOF

cat > docs/agents/tasks/06_tags_init.md <<'EOF'
# Task 06 — core/tags/__init__.py
Branch: task/claude-lazy-init-tags-<yourname>
Target: core/tags/__init__.py

Goal
If __init__ re-exports labs symbols, replace re-export with lazy __getattr__ proxy or move re-export to labs_integrations.

Edit pattern
- Use __getattr__ and __dir__ to lazy-proxy attributes (interim)
- Add comment TODO: migrate to ProviderRegistry

Tests
- tests/core/test_tags_init_importsafe.py - import-only safe test

Validation
ruff, mypy, pytest, lane-guard

Commit
chore(tags): lazy-proxy re-exports in core/tags/__init__.py
EOF

cat > docs/agents/tasks/07_adapters_init.md <<'EOF'
# Task 07 — core/adapters/__init__.py
Branch: task/claude-adapters-init-<yourname>
Target: core/adapters/__init__.py

Goal
Avoid re-exporting labs in adapters __init__. Keep adapter interface lane-safe.

Edit pattern
- Move labs-based code to labs_integrations adapters.
- Keep core/adapters exposing only Protocols/Interfaces or provider accessors.

Tests
- tests/core/test_adapters_importsafe.py

Validation
ruff, mypy, pytest, lane-guard

Commit
chore(adapters): remove import-time labs re-exports
EOF

cat > docs/agents/tasks/08_governance_init.md <<'EOF'
# Task 08 — core/governance/__init__.py
Branch: task/claude-gov-init-<yourname>
Target: core/governance/__init__.py

Goal
Move any top-level labs imports into lazy proxies or labs_integrations plugin; ensure governance API unchanged.

Tests
- tests/core/test_governance_importsafe.py

Validation and commit format as before.

Commit
chore(governance): lazy-load labs re-exports
EOF

cat > docs/agents/tasks/09_serve_openai_proxy.md <<'EOF'
# Task 09 — serve/api/openai_proxy.py
Branch: task/claude-lazy-load-serve-openai-<yourname>
Target: serve/api/openai_proxy.py

Goal
Ensure endpoint does not instantiate labs/OpenAI client at module import. Use ProviderRegistry or DI inside handlers.

Tests
- tests/serve/test_openai_proxy_importsafe.py
- test endpoint behavior with stub provider

Validation + commit as earlier.

Commit
refactor(provider): lazy-load labs in serve/api/openai_proxy.py
EOF

cat > docs/agents/tasks/10_website_api.md <<'EOF'
# Task 10 — lukhas_website/api.py
Branch: task/claude-lazy-load-website-<yourname>
Target: lukhas_website/api.py

Goal
Replace any module-level labs imports with provider or lazy loader so the website import is lane-safe.

Tests
- tests/website/test_api_importsafe.py
- add stubbed behavior tests for demo endpoints

Validation, commit and PR checklist as above.

Commit
refactor(provider): lazy-load labs in lukhas_website/api.py
EOF

echo "[info] Files created. Now creating branch '$BRANCH' and committing..."

# Create branch based off BASE
git fetch "${REMOTE}"
if git rev-parse --verify "${BASE}" >/dev/null 2>&1; then
  git checkout -B "${BRANCH}" "${BASE}"
else
  git checkout -B "${BRANCH}"
fi

git add docs/agents/tasks
git commit -m "chore(docs/agents): add 10 Claude Code task templates (lazy-load/provider tasks)"
git push -u "${REMOTE}" "${BRANCH}"

echo "[done] Branch '${BRANCH}' pushed to ${REMOTE}. Review the files under docs/agents/tasks/"
```

---

### After you run the script

1. Confirm the branch exists remotely:

```bash
git fetch origin
git branch -r | grep task/claude-tasks-setup
```

2. Open a PR from `task/claude-tasks-setup` → `origin/feat/fix-lane-violation-MATRIZ` or `main` (your choice), and add the reviewers we listed earlier.

3. Hand the task files to your Claude Code instances (or have them open the PR and act on each file, creating the per-file branches for surgical edits).

---
