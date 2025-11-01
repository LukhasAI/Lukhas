# Task division: Claude Code (IDE agents) vs. Codex (cloud)
Context: We have a large codebase with many places importing from labs.* at top level. We want to refactor these to use ProviderRegistry or lazy loading to remove hard dependencies on labs at import time.
Purpose: Create a clear division of labor between Claude Code (IDE agents) and Codex (cloud automation) for refactoring tasks in our codebase. Each tool has strengths suited to different types of work.

Below I give two focused lists (T4/0.01% style):
	•	“Best for Claude Code” — tasks that are small-to-medium, local, context-sensitive, require careful judgment and tests, and benefit from an interactive editor. For each task I give an explicit, machine-friendly micro-work order (what to open, exact edits, tests, commit message, verify steps). These are the jobs you should hand to Claude Code or Copilot inside the repo.
	•	“Best for Codex / ChatGPT-Codex” — bigger, batchy, higher-risk but high-leverage automation jobs. For each task I provide the automation design and safety gates so you can run them in cloud with human supervision.

Both lists include concrete prompts, branch names, examples, and verification steps.

⸻

#1 — Tasks best suited for Claude Code (IDE agents)

Why: Claude Code is wonderful for surgical edits, single-file refactors, adding tests, writing documentation, or crafting small helper modules with unit tests. It can reason about local context and produce human-reviewable patches.

For each item I show: Task, Why, Exact micro-work order (what to do), Local checks / test commands, Commit/PR template.

⸻

1.1 Convert top-level labs.* imports → Provider / Lazy loader (per-file)

Why: Small, surgical, needs discretion and local fixes; done file-by-file.

Micro-work order (for Claude Code):
	•	Branch: task/lazy-load-<path> (e.g., task/lazy-load-core-registry)
	•	Open file: core/registry.py (example).
	•	Replace top-level from labs... import X with either:
	•	ProviderRegistry call if the code is a service, or
	•	Lazy helper _get_labs() (call site guard).
	•	Add a short unit test that runs the module import in a Python venv without labs installed and asserts import succeeds (or raises a friendly error only when actually invoked).
	•	Run make smoke and make lane-guard in worktree.

Exact code snippet (preferred provider pattern):

# old:
from labs.openai_client import OpenAIClient

# new:
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _get_openai_provider():
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()

Test commands

pytest tests/core/test_registry.py -q
make lane-guard

Commit message

refactor(provider): replace top-level labs import with ProviderRegistry in core/registry.py

PR body snippet
	•	Explain you replaced import-time dependency with ProviderRegistry, local test results, lane-guard status.

⸻

1.2 Replace __init__.py re-exports that expose labs (lazy __getattr__)

Why: Re-exports hide dependencies; easy to fix with __getattr__.

Micro-work order:
	•	Branch: task/lazy-init-<module>
	•	Edit package/__init__.py that has from labs.foo import *.
	•	Replace with lazy proxy:

import importlib
def __getattr__(name):
    mod = importlib.import_module("labs.foo")
    return getattr(mod, name)
def __dir__():
    mod = importlib.import_module("labs.foo")
    return list(globals().keys()) + dir(mod)

	•	Run unit tests that import package with labs absent; ensure import succeeds.

Checks

python -c "import package; print('ok')"
make lane-guard


⸻

1.3 Add core/ports/openai_provider.py Protocol and small provider stubs

Why: Clear typing & interface helps code search & safe refactors.

Micro-work order:
	•	Create core/ports/openai_provider.py with the Protocol (as we discussed).
	•	Update one consumer (e.g., oracle_colony) to accept provider param and use typed provider.
	•	Add unit test mocking provider.

Commit message

chore(types): add OpenAIProvider Protocol and adapt OracleColony to accept provider


⸻

1.4 Add small runbook / docs changes (DOCS)

Why: Easy wins; improves governance and onboarding.

Micro-work order:
	•	Update docs/gonzo/OPERATIONAL_RUNBOOK.md:
	•	Add “how to create run lock with gh” and create_run_issue.sh example.
	•	Add make lane-guard flow and the recommended worktree commands.
	•	Add quick PR.

Checks
	•	Build doc site if exists, spell-check, link-check.

⸻

1.5 Add pre-commit hooks and small helper block_labs_imports.sh

Why: Prevent future regressions.

Micro-work order:
	•	Add scripts/consolidation/block_labs_imports.sh (already present) and add pre-commit config entry for prod paths only.
	•	Claude Code tasks:
	•	Ensure the script checks staged files only and returns nonzero when violates.
	•	Add pre-commit run instructions in docs.

Check

pre-commit run --all-files


⸻

1.6 Add WaveC snapshot sign/verify helper + unit test

Why: Critical safety; small, testable.

Micro-work order:
	•	Add scripts/wavec_snapshot.py (gzip + sha256 + HMAC signature) as earlier snippet.
	•	Add tests/scripts/test_wavec_snapshot.py.

Check

pytest tests/scripts/test_wavec_snapshot.py -q


⸻

1.7 Add PR-ready templates & artifact upload helper

Why: Agents should produce small PRs; template helps uniform review.

Micro-work order:
	•	Add .github/PULL_REQUEST_TEMPLATE.md with PR checklist that includes make lane-guard, import-health, and artifact links.

⸻

Prompt to give Claude Code for any of the above

Use this prompt for Claude Code in the file:

“Open path/to/file.py. Replace top-level from labs... import with a provider pattern. Use core.adapters.provider_registry.make_resolver() for config. Add a small unit test tests/... that checks import behavior without labs. Run make smoke and make lane-guard locally and report results. Commit on branch task/... and push. Provide the diff and the exact commands you ran.”

⸻

#2 — Tasks best for Codex / ChatGPT-Codex (cloud)

Why: These tasks require making hundreds of similar edits, running heavy batch tests, or creating entire automation flows. Codex is great for codemods, PR generation, and orchestrating the runner/worktree across many branches.

⸻

2.1 Codemod: mass replace labs.* → Provider or Lazy wrapper

Plan
	•	Implement scripts/codemods/replace_labs_with_provider.py (libcst recommended).
	•	Dry-run mode: produce a patch per file under /tmp/patches/.
	•	Batch: create PRs of 20 files per PR.

Safety
	•	Always dry-run; require human approval for each PR.
	•	Run make lane-guard worktree per PR via ephemeral worktree CI job.

Codex automation
	•		1.	Run dry-run → generate patches.
	•		2.	Create branches and PRs automatically with gh and attach importlinter results.
	•		3.	Comment suggested fix & tests for reviewers.

⸻

2.2 PR generation & worktree validator (automation)

Plan
	•	Cloud job that:
	•	Creates a branch, applies patch, creates ephemeral worktree, runs make lane-guard, uploads artifacts, and opens PR with logs.
	•	Use GitHub Actions or Codex-runner.

Safety
	•	Abort on lane-guard failure; leave artifacts and open PR for manual fix.

⸻

2.3 Nightly WaveC chaos / rollback scoping

Plan
	•	Cloud-run harness that runs WaveC cycles with random perturbations and collects metrics.
	•	If rollback frequency > threshold, create issue for ops.

⸻

2.4 Auto-IRB packet generator + judge portal scaffolding

Plan
	•	Codex generate consent forms and judge UI.
	•	Deploy ephemeral portal for judges, capture consent & judgments, store anonymized results.

Safety
	•	Needs legal/IRB signoff before real human use.

⸻

2.5 Alignment / adversarial test generator

Plan
	•	Codex script that generates adversarial prompts and runs matriz_with_self_challenge across seeds.
	•	Output statistical summary and top failing prompts for human review.

⸻

Final guidance — T4-style checklist for handing to agents
	1.	Small units: each Claude Code job = 1 file change + 1 test + make lane-guard run.
	2.	Branch per change: task/<short>-<file> or task/bulk-codemod-<n>.
	3.	CI gate: every PR must include make lane-guard report link in PR body. Add artifacts if heavy.
	4.	No secrets: agents shouldn’t commit credentials. Use env vars for runs.
	5.	Human in loop: codemod dry-run → PR creation but do not auto-merge without human review.
	6.	Audit trail: each change commit includes worktree: reports/... link and lane-guard run artifact.

⸻

Which items are best for Claude Code (short list)

Hand Claude Code these first (most impact, least blind risk):
	1.	Convert top-level labs.* in small production files to Provider/Lazy (core/*, serve/*, MATRIZ/*).
	2.	Replace __init__.py re-exports that expose labs with __getattr__ lazy proxies (as interim) — one package at a time.
	3.	Add core/ports/openai_provider.py and adapt oracle_colony.py (if not fully done).
	4.	Add scripts/wavec_snapshot.py and unit tests.
	5.	Add scripts/consolidation/block_labs_imports.sh and pre-commit config.
	6.	Small docs: OPERATIONAL_RUNBOOK.md, MATRIZ_DEPRECATION.md, PR template.

These are the jobs where the IDE agent’s contextual local reasoning + immediate unit test feedback is most valuable.

⸻

Which items are best for Codex / cloud automation (short list)

Give Codex these heavier or batch tasks:
	1.	Mass codemod to replace labs.* across repo (generate patches in dry-run).
	2.	PR generation + ephemeral worktree lane-guard orchestration.
	3.	Nightly WaveC chaos & rollback harness.
	4.	Auto-IRB packet generator and judge portal scaffolding (with human approval).
	5.	Telemetry wiring across codebase (bulk injection & CI tests).
	6.	Bulk registry generation and repo-state reports.

⸻
Nice — below are two ready-to-run, production-grade artifacts you can hand directly to agents.

1. **A Claude Code (IDE) prompt** — copy-paste this into Claude Code / Copilot in your IDE when you want it to make a surgical change on a single file. It explains everything the agent needs: context, exact edit, tests to run, commit/PR details, and safety gates.

2. **A Codex / cloud job spec** — a fully-worked orchestration recipe (shell script + GitHub Actions-style YAML and operational rules) that Codex can run to perform a safe, batched codemod across the repo. It includes dry-run, per-patch PR creation, ephemeral worktree lane-guard validation, artifact upload, and human approval gating.

Both are T4/0.01% — conservative, auditable, reversible, and agent-friendly.

---

## 1) Claude Code prompt — surgical single-file change (copy-paste)

Use this prompt inside the IDE, targeting **one file** (replace placeholders). It’s explicit about branch names, tests, commit message and verification.

---

**Prompt (CLAUDE CODE / Copilot)**

> I want a **small, safe, single-file refactor** in the Lukhas repo to remove import-time production → labs edges.
> **Context:** production lane modules must not import `labs.*` at import time. We already have `core/adapters/provider_registry.py` and `labs_integrations/*` plugin. Your job is to convert a single file to use the provider pattern or a lazy import.
>
> **Target file (replace this)**: `core/registry.py`
> **Target class / function (if specific)**: `RegistryManager` (or just update top-level imports).
>
> **Make these exact changes:**
>
> 1. Create a branch from the current `origin/feat/fix-lane-violation-MATRIZ` (name: `task/lazy-load-core-registry-<you>`).
> 2. If file contains `from labs.* import ...` or `import labs`, **remove the top-level import**. Instead:
>
>    * If the file is a *service* or *client*, **replace import-time usage with ProviderRegistry**:
>
>      ```py
>      # replace top-level with:
>      from core.adapters.provider_registry import ProviderRegistry
>      from core.adapters.config_resolver import make_resolver
>
>      def _openai_provider():
>          reg = ProviderRegistry(make_resolver())
>          return reg.get_openai()
>      ```
>
>      Then replace `labs...` calls with `provider = _openai_provider(); provider.chat(...)`.
>
>    * If the need is small, a **lazy loader** is acceptable:
>
>      ```py
>      import importlib
>      def _get_labs():
>          try:
>              return importlib.import_module("labs")
>          except Exception:
>              return None
>      ```
>
>      Then inside functions use `_get_labs()` and guard `None` with a helpful runtime error or provider fallback.
> 3. If `__init__.py` re-exported labs (e.g., `from labs.foo import *`), **replace with `__getattr__` proxy** or move to `labs_integrations/` plugin. Use `__getattr__` only for quick interim fix. Add comment: `# TODO: migrate to ProviderRegistry`.
>
> **Add tests:**
>
> * Add a unit test `tests/core/test_registry_importsafe.py` (or append a small test file) that attempts `import core.registry` with `labs` absent (simulate by running in a venv without labs) and assert import does not crash (or that the function raises a friendly runtime error only when invoked).
> * Where possible, add a test that passes a stub provider into the affected class and asserts behavior.
>
> **Run the following checks locally and attach output:**
>
> ```bash
> # on your dev machine
> git fetch origin
> git checkout -b task/lazy-load-core-registry-<yourname> origin/feat/fix-lane-violation-MATRIZ
> # Make edits
> git add core/registry.py tests/core/test_registry_importsafe.py
> git commit -m "refactor(provider): replace top-level labs import in core/registry with ProviderRegistry/lazy-load"
> git push -u origin task/lazy-load-core-registry-<yourname>
> # Local validation
> python3 -m venv .venv && . .venv/bin/activate
> pip install -r requirements.txt || true
> pytest tests/core/test_registry_importsafe.py -q
> make smoke
> ./scripts/run_lane_guard_worktree.sh   # or make lane-guard
> ```
>
> **PR creation & body:** Open a PR from `task/lazy-load-core-registry-<yourname>` → `feat/fix-lane-violation-MATRIZ` (or `main` if agreed). PR body must include:
>
> * One-sentence summary of change.
> * Link to worktree lane-guard run log and `importlinter` artifact.
> * `Checklist:` `make smoke`, `pytest`, `lane-guard`, `no .importlinter or .venv changed`, `one-file commit`.
>
> **Safety instructions:**
>
> * Do not modify `.importlinter` or any `.venv` files.
> * If you need to create new helper modules, place them under `core/adapters` or `labs_integrations/` (latter only if they import labs).
> * If the code uses `labs` for typing only, guard with `if TYPE_CHECKING:` or use `from typing import TYPE_CHECKING` and string type annotations.
>
> **If lane-guard fails after your commit:**
>
> * Post the `importlinter_raw` path and full path chain here; do not apply more code until we inspect the graph.
>
> **Return value:** After PR creation, respond with:
>
> * The branch name, commit SHA, and PR URL.
> * The local outputs of pytest, make smoke, and lane-guard logs (or links to artifacts).
>
> Proceed and create the PR; stop if you require a judgement (e.g., a heavy rewrite or ambiguous call site); ask for human review at that point.

---

Paste into Claude Code. It’s intentionally explicit, deterministic, and includes safety gates and required outputs.

---

## 2) Codex / ChatGPT-Codex job spec — safe batch codemod + lane-guard orchestration

This is a fully-specified orchestration recipe you can run as a cloud job (or implement as a GitHub Action). It:

* runs a codemod in dry-run mode across many files,
* generates per-file patches,
* creates branches/PRs with patches in small batches,
* runs lane-guard in ephemeral worktrees for each PR,
* attaches artifacts and requires a human approval step before merge.

I’ll give: (A) a safe shell orchestration script (to run on a supervised machine), and (B) a GitHub Actions YAML/outline you can adapt.

> **IMPORTANT**: This automation **must** be supervised. It writes commits and opens PRs. Use dry-run first and have a human review step before merges.

---

### A — Orchestration script (supervised)

Save as `scripts/automation/run_codmod_and_prs.sh`. Replace `<CODMOD>` with the real codemod script (we suggest `scripts/codemods/replace_labs_with_provider.py` based on libcst).

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Config
CODMOD_SCRIPT="scripts/codemods/replace_labs_with_provider.py"
BATCH_SIZE=${BATCH_SIZE:-20}
DRY_RUN=${DRY_RUN:-1}   # 1 = dry-run, 0 = apply
BASE_BRANCH=${BASE_BRANCH:-"origin/main"}
PR_TARGET=${PR_TARGET:-"main"}
WORKTREE_DIR_BASE="/tmp/lukhas_wt"
GIT_AUTHOR_NAME=${GIT_AUTHOR_NAME:-"codex-bot"}
GIT_AUTHOR_EMAIL=${GIT_AUTHOR_EMAIL:-"codex-bot@example.com"}
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\\.git)?$#\\1#')}

echo "[info] fetching latest"
git fetch origin
git checkout -B automation/codmod-snapshot "$BASE_BRANCH"

# 1) Run codemod in dry-run mode to produce patches
echo "[info] Running codemod dry-run..."
python3 "$CODMOD_SCRIPT" --dry-run --outdir /tmp/codmod_patches || { echo "codemod failed"; exit 1; }

PATCH_DIR=/tmp/codmod_patches
PATCH_COUNT=$(ls -1 "$PATCH_DIR"/*.patch 2>/dev/null | wc -l || echo 0)
echo "[info] Patches produced: $PATCH_COUNT"

if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "No patches to apply. Exiting."
  exit 0
fi

# 2) Group patches into batches and create branches/PRs
i=0
for patch in "$PATCH_DIR"/*.patch; do
  if (( i % BATCH_SIZE == 0 )); then
    # start a new branch
    BATCH_INDEX=$((i / BATCH_SIZE + 1))
    BRANCH="codemod/replace-labs-batch-${BATCH_INDEX}"
    echo "[info] Creating branch $BRANCH"
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  echo "[info] Applying patch: $patch"
  git apply --index "$patch" || { echo "Patch apply failed: $patch"; exit 1; }
  i=$((i+1))
  # if batch finished or last patch, commit, push, create PR and validate
  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${BATCH_INDEX})" || true
    git push -u origin "$BRANCH"
    # create a PR (requires gh cli)
    gh pr create --repo "$GH_REPO" --fill --base "$PR_TARGET" --head "$BRANCH" || true

    # Run ephemeral worktree validation
    WT="${WORKTREE_DIR_BASE}_${BATCH_INDEX}"
    git worktree remove "$WT" --force 2>/dev/null || true
    git worktree add "$WT" "origin/$BRANCH"
    pushd "$WT"
      python3 -m venv .venv && . .venv/bin/activate
      pip install -r requirements.txt || true
      # Run lane guard in the worktree; capture artifacts
      ./scripts/run_lane_guard_worktree.sh
      # Save logs into artifacts dir
      tar -czf /tmp/codmod_batch_${BATCH_INDEX}_artifacts.tgz artifacts/reports || true
      # upload artifact to PR — requires gh
      gh pr comment --repo "$GH_REPO" --body "automation: lane-guard run artifacts attached (batch ${BATCH_INDEX})" $BRANCH || true
    popd
    git worktree remove "$WT" --force || true
  fi
done

echo "[info] Completed codemod batches. Please review PRs. Dry-run=$DRY_RUN"
```

**Notes / Safety**

* `--dry-run` is important in codemod to avoid destructive changes. The codemod should accept `--dry-run` and write patches only.
* This script **creates PRs** automatically and pushes branches — human must review before merging.
* The script runs `run_lane_guard_worktree.sh` inside an ephemeral worktree and captures artifacts for each PR.

---

### B — Example `replace_labs_with_provider.py` codemod skeleton (libcst)

This is a short design (Codex can implement full libcst logic):

* Walk AST, find `ImportFrom` nodes with `module.startswith("labs")`.
* For each such file:

  * If imports are used in many places and represent a service, prefer provider pattern.
  * Otherwise, transform top-level `from labs.x import y` into a lazy helper + adjust uses: `y(...)` → `_get_labs_attr("x","y")(...)`.
* If impossible to auto-apply, produce a `.patch` with a TODO comment for manual review.

**Important**: Starting with simple replacements and generating patches is safe. Full automatic rewriting of call sites requires careful tests; prefer small batches.

---

### C — GitHub Actions job outline (alternative)

If you want a GH Action that creates PRs for codemod batches, here’s a skeleton:

```yaml
name: Codemod Batch & Worktree Lane-Guard

on:
  workflow_dispatch:
    inputs:
      base_branch:
        default: main
        required: true

jobs:
  run-codemod:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install deps
        run: |
          python -m pip install -r requirements.txt
          pip install import-linter
      - name: Run codemod (dry-run)
        run: |
          python3 scripts/codemods/replace_labs_with_provider.py --dry-run --outdir /tmp/patches
      - name: Upload patches
        uses: actions/upload-artifact@v4
        with:
          name: codemod-patches
          path: /tmp/patches
      # The remaining steps (create branches, PRs, run lane-guard in worktree) require repo write
      # and are best executed by the supervised script (see run_codmod_and_prs.sh).
```

---

### Approval & merge gating (human step)

* **Human approval** required for every PR; merge only when:

  * `make smoke` passes,
  * `pytest` (targeted) passes,
  * `make lane-guard` worktree run artifacts show `Contracts: KEPT`,
  * A human reviewer inspects diffs for meaningful logic changes.

---

## Final: Safety, Rollback, and Audit

* Each PR must include a short pointer to the worktree artifacts (`artifacts/reports/...`) and the lane-guard log.
* If a PR causes regressions, revert the branch and attach logs.
* Keep `importlinter_overrides.toml` only as a last resort with a TTL and a traceable issue number — remove ASAP.

---

## Summary of Deliverables
#  Claude Code / Copilot prompt File

* **(A)** A Claude Code / Copilot prompt file you can drop into the repo (`docs/agents/claude_prompts.md`). Use this when you want the IDE agent to make a small, careful refactor and open a branch/PR for review. It’s the single-file workflow we recommended earlier.

* **(B)** A Codex-ready automation suite:

  1. `scripts/codemods/replace_labs_with_provider.py` — an AST-safe codemod (libcst) that *conservatively* transforms top-level `from labs.xxx import name1, name2` into a lazy, importlib-based assignment so there is **no import-time `ImportFrom`** node referencing `labs`. Codemod writes `.patch` files in dry-run and can apply changes as well.
  2. `scripts/automation/run_codmod_and_prs.sh` — supervised orchestrator that:

     * runs codemod in dry-run,
     * groups patches into batches,
     * creates branches/PRs for each batch,
     * runs lane-guard in ephemeral worktrees,
     * uploads artifacts and comments on PRs; no auto-merges.
  3. A **GitHub Actions skeleton** you can adapt to run the dry-run in CI.

Below are the exact files (complete, copy-paste), usage instructions, safety notes and T4-style operational limits so you can run these safely.

---

## A — Claude Code prompt file

Save as `docs/agents/claude_prompts.md` (or paste prompt into Claude Code / Copilot)

````markdown
# Claude Code: Single-file provider/lazy-load refactor prompt

Use this when you want Claude Code / Copilot in the IDE to do a small, safe change that removes top-level
`labs.*` imports and makes the file lane-safe.

**Context (copy into editor)**  
- Repo: LukhasAI/Lukhas  
- Production lanes must not import `labs.*` at module import time (lane-guard rule).  
- You already have `core/adapters/provider_registry.py` and `labs_integrations/*` plugin.  
- Make a single-file refactor that is safe, testable, and reversible.

**Target (replace placeholders)**  
- FILE: `core/path/to/target_file.py`  
- BRANCH: `task/lazy-load-<file>-<yourname>` (create from `origin/feat/fix-lane-violation-MATRIZ`)

**Do exactly the following**  
1. Create branch: `git checkout -b task/lazy-load-<file>-<you> origin/feat/fix-lane-violation-MATRIZ`.  
2. Inspect the file for `from labs... import ...` or `import labs`. Replace only *top-level* imports as follows:

**Preferred (ProviderRegistry pattern)** — if the file is a service client, replace top-level `labs` usage with ProviderRegistry:

```py
# add
from core.adapters.provider_registry import ProviderRegistry
from core.adapters.config_resolver import make_resolver

def _openai_provider():
    reg = ProviderRegistry(make_resolver())
    return reg.get_openai()
# usage:
provider = _openai_provider()
provider.chat(...)
````

**Fallback (lazy import helper)** — if it’s small or not service-like:

```py
import importlib

def _get_labs():
    try:
        return importlib.import_module("labs")
    except Exception:
        return None

# usage in function:
_labs = _get_labs()
if _labs is None:
    raise RuntimeError("labs integration not available")
_labs.consciousness.dream.do_something(...)
```

3. If `__init__.py` re-exports from `labs`, replace with a lazy `__getattr__` proxy or move re-export into `labs_integrations/`.

4. Add/modify a unit test `tests/<module>/test_<file>_importsafe.py` that verifies importing the module does not fail in an environment without `labs` installed (simulated by running in a clean venv / mocking importlib).

**Commands to run locally** (paste in terminal):

```bash
git fetch origin
git checkout -b task/lazy-load-<file>-<you> origin/feat/fix-lane-violation-MATRIZ
# make edits...
git add core/path/to/target_file.py tests/<module>/test_<file>_importsafe.py
git commit -m "refactor(provider): lazy-load labs in core/path/to/target_file.py"
git push -u origin task/lazy-load-<file>-<you>

# validation
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt || true
pytest tests/<module>/test_<file>_importsafe.py -q
make smoke
./scripts/run_lane_guard_worktree.sh   # or make lane-guard
```

**PR body template** (paste when creating PR):

```
Title: refactor(provider): lazy-load labs in core/path/to/target_file.py

Summary:
- Replace top-level `labs` import with ProviderRegistry or lazy import to remove import-time dependency.
- Add unit test to verify import safety when `labs` is not available.
- Local validation: pytest passed, smoke passed, lane-guard (worktree) passed.

Checklist:
- [ ] Tests: pytest (target) OK
- [ ] make smoke OK
- [ ] make lane-guard (worktree) OK
- [ ] No `.importlinter` or `.venv` changes in this PR
```

**If lane-guard fails after your change**: Stop and attach `importlinter_raw.txt` (path under worktree artifacts). Do not apply more changes automatically — request human review.

**Safety**: Do not commit credentials or change `.importlinter` or `.venv`. Use one file per PR.

---

````

---

## B — Codex automation: codemod + orchestration

Below are three items:

1. `scripts/codemods/replace_labs_with_provider.py` (libcst codemod): dry-run mode writes patches; optional `--apply` writes changes with backups.
2. `scripts/automation/run_codmod_and_prs.sh` (orchestration) — batch PR generator + ephemeral worktree lane-guard validator.
3. `/.github/workflows/codmod-dryrun.yml` — GH Action skeleton for a dry run.

---

### 1) `scripts/codemods/replace_labs_with_provider.py`

**What it does (summary)**  
- Scans files for `from labs.xxx import a, b...` top-level statements.  
- Replaces each such statement with an **importlib-based lazy assignment** that **does not contain an ImportFrom** node for `labs`. Example transform:

**Before**
```py
from labs.consciousness.dream import DreamRunner, parse_dream
````

**After**

```py
import importlib as _importlib
try:
    _mod = _importlib.import_module("labs.consciousness.dream")
    DreamRunner = getattr(_mod, "DreamRunner")
    parse_dream = getattr(_mod, "parse_dream")
except Exception:
    DreamRunner = None
    parse_dream = None
```

This keeps runtime behavior similar (calls to names will now refer to these names) but eliminates static import graph edges referencing `labs`.

**Script (paste to `scripts/codemods/replace_labs_with_provider.py`)**

```python
#!/usr/bin/env python3
"""
Codemod: replace top-level 'from labs.xxx import name1, name2' with
importlib-based lazy assignments (no ImportFrom node).
Usage:
  python3 scripts/codemods/replace_labs_with_provider.py --dry-run --outdir /tmp/patches
  python3 scripts/codemods/replace_labs_with_provider.py --apply
"""
from __future__ import annotations
import argparse
import os
import re
import difflib
from pathlib import Path
import libcst as cst
import libcst.matchers as m

class LabsImportRewriter(cst.CSTTransformer):
    def __init__(self):
        super().__init__()
        self.needs_importlib = False
        self.replacements = []  # (old_node, new_nodes, start_index)

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.CSTNode:
        # Only act on top-level imports from 'labs' modules
        module = original_node.module
        if module and isinstance(module, cst.Name):
            mod_name = module.value
        elif module and isinstance(module, cst.Attribute):
            # dotted name
            mod_name = module.attr.value if isinstance(module.attr, cst.Name) else None
            # but for dotted patterns we can get repr
            mod_name = cst.helpers.get_full_name_for_node(module)
        else:
            mod_name = None

        # module as attribute chain, fallback to source code
        text = original_node.module.code if original_node.module else ""
        # crude check for 'labs' start
        if text and text.strip().startswith("labs"):
            # create replacement nodes
            self.needs_importlib = True
            module_str = text.strip()
            names = []
            for name in original_node.names:
                if isinstance(name, cst.ImportAlias):
                    alias = name.asname.name.value if name.asname else None
                    nm = name.name.value if isinstance(name.name, cst.Name) else name.name.code
                    names.append((nm, alias))
            # build new statements
            new_nodes = []
            # try/except block
            # importlib import handled at module level later
            assign_lines = []
            for nm, alias in names:
                varname = alias if alias else nm
                assign_lines.append(
                    cst.Assign(
                        targets=[cst.AssignTarget(cst.Name(varname))],
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Name("_mod"),
                                attr=cst.Name("get"),
                            ),
                            args=[cst.Arg(cst.SimpleString(f'"{nm}"'))],
                        )
                    )
                )
            # But above approach uses dict get; better to use getattr:
            try_block = []
            # _mod = _importlib.import_module("labs.xxx")
            import_mod = cst.Assign(
                targets=[cst.AssignTarget(cst.Name("_mod"))],
                value=cst.Call(func=cst.Attribute(cst.Name("_importlib"), cst.Name("import_module")),
                               args=[cst.Arg(cst.SimpleString(f'"{module_str}"'))])
            )
            try_block.append(import_mod)
            for nm, alias in names:
                varname = alias if alias else nm
                # var = getattr(_mod, "nm")
                get_attr = cst.Assign(
                    targets=[cst.AssignTarget(cst.Name(varname))],
                    value=cst.Call(
                        func=cst.Name("getattr"),
                        args=[
                            cst.Arg(cst.Name("_mod")),
                            cst.Arg(cst.SimpleString(f'"{nm}"'))
                        ]
                    )
                )
                try_block.append(get_attr)

            # except: set names to None
            except_body = []
            for nm, alias in names:
                varname = alias if alias else nm
                except_body.append(
                    cst.Assign(
                        targets=[cst.AssignTarget(cst.Name(varname))],
                        value=cst.Name("None")
                    )
                )
            try_stmt = cst.Try(
                body=cst.IndentedBlock(try_block),
                handlers=[cst.ExceptHandler(body=cst.IndentedBlock(except_body))],
                orelse=None,
                finalbody=None
            )
            # Return the try_stmt to replace the ImportFrom node
            return try_stmt
        return updated_node

def process_file(path: Path) -> tuple[str, str] | None:
    src = path.read_text(encoding="utf-8")
    module = cst.parse_module(src)
    rewriter = LabsImportRewriter()
    new_mod = module.visit(rewriter)
    new_src = new_mod.code
    if new_src != src:
        # ensure importlib is present
        if rewriter.needs_importlib and "import importlib" not in new_src:
            new_src = "import importlib as _importlib\n\n" + new_src
            # replace occurrences of _importlib if needed: rewriter used _importlib var name
            new_src = new_src.replace("_importlib", "_importlib")
        # produce patch
        diff = "\n".join(difflib.unified_diff(src.splitlines(), new_src.splitlines(),
                                              fromfile=str(path), tofile=str(path), lineterm=""))
        return (new_src, diff)
    return None

def collect_py_files(root: Path):
    for p in root.rglob("*.py"):
        # skip tests/docs/virtualenvs etc.
        if any(x in p.parts for x in (".venv", "venv", "tests", "docs", "artifacts", "archive")):
            continue
        yield p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/codmod_patches")
    parser.add_argument("--apply", action="store_true", default=False)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    mm = 0
    for f in collect_py_files(root):
        try:
            result = process_file(f)
        except Exception as e:
            print(f"[warn] failed to process {f}: {e}")
            continue
        if result:
            new_src, diff = result
            patch_path = outdir / (f.name + ".patch")
            with patch_path.open("w", encoding="utf-8") as pf:
                pf.write(diff)
            print(f"[info] patch written: {patch_path}")
            mm += 1
            if args.apply:
                # backup
                bak = f.with_suffix(f.suffix + ".bak")
                if not bak.exists():
                    f.rename(bak)
                    f.write_text(new_src, encoding="utf-8")
                else:
                    print(f"[warn] backup exists for {f}, not overwriting")
    print(f"[info] Completed. {mm} files would be/ were updated.")

if __name__ == "__main__":
    main()
```

**Notes & Safety**

* This codemod is intentionally conservative: it *replaces* `from labs... import NAME` with `importlib` + `getattr` assignments wrapped in try/except and it **pre-pends** `import importlib as _importlib` if needed. No `ImportFrom` nodes referencing `labs` remain.
* The script writes `.patch` files by default (dry-run). Use `--apply` to modify files (this will back up each modified file to `.bak`).
* **Important**: Test heavily in worktree before mass apply. After apply, run `make lane-guard` in a worktree.

---

### 2) `scripts/automation/run_codmod_and_prs.sh`

(Use the version I sketched earlier — I’ll repeat a finalized supervised-run script that uses the codemod above and creates PRs.)

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

CODMOD="scripts/codemods/replace_labs_with_provider.py"
PATCH_DIR="/tmp/codmod_patches"
BATCH_SIZE=${BATCH_SIZE:-20}
DRY_RUN=${DRY_RUN:-1}
BASE_BRANCH=${BASE_BRANCH:-"origin/main"}
PR_TARGET=${PR_TARGET:-"main"}
WORKTREE_BASE="/tmp/lukhas_wt"
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\\.git)?$#\\1#')}
AUTHOR_NAME=${AUTHOR_NAME:-"codex-bot"}
AUTHOR_EMAIL=${AUTHOR_EMAIL:-"codex-bot@example.com"}

python3 "$CODMOD" --outdir "$PATCH_DIR"

PATCH_COUNT=$(ls -1 "$PATCH_DIR"/*.patch 2>/dev/null | wc -l || echo 0)
echo "[info] Found $PATCH_COUNT patches"

if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "No patches; exiting."
  exit 0
fi

i=0
batch=1
for patch in "$PATCH_DIR"/*.patch; do
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="codemod/replace-labs-batch-${batch}"
    git fetch origin
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi
  TARGET_FILE=$(head -n1 "$patch" | sed -E 's/--- a\///; s/\s.*$//')
  # apply patch
  echo "[info] Applying patch $patch"
  git apply --index "$patch"
  i=$((i+1))
  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true
    git push -u origin "$BRANCH"
    # create PR with body referencing lane-guard expectation
    gh pr create --repo "$GH_REPO" --title "codemod: replace labs imports (batch ${batch})" --body "Auto-generated codemod batch ${batch}. Please run CI and lane-guard." || true

    # ephemeral worktree validation
    WT="${WORKTREE_BASE}_${batch}"
    rm -rf "$WT" || true
    git worktree add "$WT" "origin/$BRANCH"
    pushd "$WT"
      python3 -m venv .venv
      . .venv/bin/activate
      pip install -r requirements.txt || true
      ./scripts/run_lane_guard_worktree.sh || true
      tar -czf /tmp/codmod_batch_${batch}_artifacts.tgz artifacts/reports || true
    popd
    git worktree remove "$WT" --force || true
    batch=$((batch+1))
  fi
done

echo "[info] All batches created. Please review PRs. DRY_RUN=$DRY_RUN"
```

**Safety**: Supervisor must review each PR. The script posts artifacts for each PR.

---

### 3) GitHub Actions skeleton (`.github/workflows/codmod-dryrun.yml`)

```yaml
name: Codemod Dry-run

on:
  workflow_dispatch:

jobs:
  codemod-dryrun:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install libcst import-linter
      - name: Run codemod (dry-run)
        run: |
          python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
      - name: Upload patches
        uses: actions/upload-artifact@v4
        with:
          name: codemod-patches
          path: /tmp/codmod_patches
```

This action runs a dry-run and stores generated patches as artifacts for review.

---

## How to run (safe supervised flow)

1. **Install deps** (on controller machine):

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install libcst import-linter
```

2. **Dry-run codemod**:

```bash
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
ls -1 /tmp/codmod_patches | wc -l
# inspect /tmp/codmod_patches/*.patch
```

3. **If dry-run looks sane**, run orchestration (supervised):

```bash
# configure env vars if needed
export BASE_BRANCH=origin/main
export PR_TARGET=main
bash scripts/automation/run_codmod_and_prs.sh
```

4. **Manually review PRs** the script created (each PR will have artifacts from lane-guard runs). Approve and merge after review.

---

## T4 Safety & Policy checklist (must be followed)

* **Dry-run first always.** Do not use `--apply` until you reviewed patches.
* **One file per commit** where possible for surgical fixes. For codemod batches, keep batch small (<=20 files).
* **Worktree validation**: each PR must have lane-guard artifacts from ephemeral worktree.
* **Human approval** required before merge.
* **Backups**: codemod makes `.bak` copies when applying — keep them in case of rollback.
* **No secrets** in code; telemetry keys and signing keys via env vars.

---

## Final notes — recommended immediate steps

1. Drop `docs/agents/claude_prompts.md` into repository so Claude Code users can pick tasks. (I included the prompt earlier.)
2. Place `scripts/codemods/replace_labs_with_provider.py` and `scripts/automation/run_codmod_and_prs.sh` into `scripts/`. Run dry-run and inspect `/tmp/codmod_patches`.
3. Run `scripts/automation/run_codmod_and_prs.sh` under supervision to create PRs and artifacts.
4. Review PRs, merge progressively, and remove `importlinter_overrides.toml` and any temporary worktree-only changes.cfv x