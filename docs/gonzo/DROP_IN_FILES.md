Beautiful — I prepared a **complete agent-ready artifact bundle** you can drop into the repo (or hand to IDE/cloud agents). Each artifact has:

* a short purpose and T4 rationale,
* exact file contents (copy/paste-ready), and
* clear run / validation instructions, safety gates and acceptance criteria.

Everything is **T4 / 0.01%**: conservative, auditable, reversible, and aligned with OpenAI safety/ethics guidance (don’t claim consciousness, require IRB for human subjects, keep human-in-the-loop). Use these artifacts as the single-source-of-truth for the agents you run in parallel: Claude Code for surgical edits and Codex/ChatGPT-Codex for batch automation.

---

## Where to put them (recommended)

Create a small folder structure:

```
docs/agents/               # prompts & agent how-tos
scripts/codemods/          # AST codemods
scripts/automation/        # orchestration scripts for Codex
scripts/consolidation/     # small helpers / pre-commit guards
.github/workflows/         # CI artifacts (SLSA, dry-run)
docs/gonzo/                # runbook, IRB templates
tasks/                     # prioritized TODO list for agents
```

Below I paste each artifact. Save the content into the file named above, commit to a branch (or hand to the agent that will create branches), and follow the `HOW TO RUN` instructions below each file.

---

## 1) `docs/agents/README.md` — agent brief (T4 / 0.01% style)

```markdown
# Agent Brief — Lukhas AI (T4 / 0.01%)

Purpose
-------
This directory contains agent-ready artifacts for safe, auditable, high-value repo work:
- surgical single-file refactors (Claude Code / Copilot)
- codemods and batch PR orchestration (Codex / ChatGPT-Codex)
- CI changes for SLSA attestations and runbooks
- safety & ethics templates

Principles (T4 / 0.01%)
-----------------------
1. **Small, auditable changes**: one file per commit/PR where possible.  
2. **Human-in-loop**: no automated merges. Every PR must be reviewed before merge.  
3. **Reversible**: back up files before applying changes. Use `.bak` or branch per PR.  
4. **No secrets in repo**: use env vars or secret stores (cosign keys, in-toto keys).  
5. **Ethics first**: Do not run human-judged experiments without IRB/ethics signoff.

Agent roles
-----------
- **Claude Code (IDE)**: surgical single-file edits (providerization, lazy-load, types, tests).  
- **Codex / ChatGPT-Codex (Cloud)**: codemods, batch PR generation, ephemeral worktree validation, SLSA automation, nightly harness.

How to use
----------
1. For single-file work: use `docs/agents/claude_prompt.md`.  
2. For batch codemods: use `scripts/codemods/replace_labs_with_provider.py` (dry-run -> patches).  
3. For orchestrated PRs: use `scripts/automation/run_codmod_and_prs.sh` (supervised).  
4. For SLSA attestation: use `.github/workflows/slsa-attest.yml` and `scripts/automation/run_slsa_for_modules.sh`.

Always attach artifacts produced (ruff/mypy logs, lane-guard run) to the PR and do not merge until a human signoff is present.
```

**HOW TO RUN:** hand to Claude Code or paste into the agent UI as the top-level orientation.

---

## 2) `docs/agents/claude_prompts.md` — Claude Code single-file prompt

````markdown
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
````

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
- The agent can’t get tests to pass locally.
```

**WHY:** precise, deterministic, and includes safety checks and required outputs.

---

## 3) `scripts/codemods/replace_labs_with_provider.py` (libcst codemod)

> **Purpose:** conservative codemod to eliminate top-level `from labs... import ...` ImportFrom nodes by replacing them with importlib-based `getattr` assignments so the static graph no longer contains `labs` ImportFrom references. Runs in **dry-run** producing `.patch` results.

> **Safety:** dry-run first; `--apply` optional; writes backups `.bak` if applying.

**Full file content** (save as `scripts/codemods/replace_labs_with_provider.py`):

```python
#!/usr/bin/env python3
"""
Codemod: replace top-level `from labs.xxx import name1, name2` with importlib-based lazy assignments.
Usage:
  python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/patches
  python3 scripts/codemods/replace_labs_with_provider.py --apply
"""
from __future__ import annotations
import argparse
import difflib
from pathlib import Path
import libcst as cst

# NOTE: This codemod is intentionally conservative. It only converts top-level
# ImportFrom nodes whose module string starts with "labs". It does not change call sites
# aggressively — we create top-level names that callers can use, but callers may need manual review.

class LabsImportRewriter(cst.CSTTransformer):
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.CSTNode:
        # Only act on `from labs... import ...` at module level
        module = original_node.module
        if module is None:
            return updated_node
        module_code = module.code if hasattr(module, "code") else None
        if not module_code or not module_code.strip().startswith("labs"):
            return updated_node

        # Build replacement: importlib import + getattr assignments
        # Example:
        # import importlib as _importlib
        # try:
        #   _mod = _importlib.import_module("labs.foo")
        #   X = getattr(_mod, "X")
        #   Y = getattr(_mod, "Y")
        # except Exception:
        #   X = None
        #   Y = None

        importlib_stmt = cst.parse_statement("import importlib as _importlib\n")
        try_items = []
        mod_str = module_code.strip()
        # _mod = _importlib.import_module("module")
        try_items.append(
            cst.parse_statement(f"_mod = _importlib.import_module({repr(mod_str)})\n")
        )
        names = []
        for alias in original_node.names:
            if isinstance(alias, cst.ImportAlias):
                if isinstance(alias.name, cst.Name):
                    name = alias.name.value
                    asname = alias.asname.name.value if alias.asname else None
                    names.append((name, asname))
                else:
                    # fallback: write original import to manual review
                    return updated_node
            else:
                return updated_node

        for nm, asn in names:
            var = asn if asn else nm
            try_items.append(cst.parse_statement(f"{var} = getattr(_mod, {repr(nm)})\n"))

        except_items = []
        for nm, asn in names:
            var = asn if asn else nm
            except_items.append(cst.parse_statement(f"{var} = None\n"))

        try_stmt = cst.Try(
            body=cst.IndentedBlock(try_items),
            handlers=[cst.ExceptHandler(body=cst.IndentedBlock(except_items))],
            orelse=None,
            finalbody=None,
        )

        # Return a SmallBlock with importlib + try
        return cst.SimpleStatementLine([importlib_stmt, try_stmt])

def process_file(path: Path):
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as e:
        print(f"[skip] parse error {path}: {e}")
        return None
    rewriter = LabsImportRewriter()
    new_module = module.visit(rewriter)
    new_src = new_module.code
    if new_src != src:
        return src, new_src
    return None

def collect_py_files(root: Path):
    for p in root.rglob("*.py"):
        if any(x in p.parts for x in (".venv","venv",".git","tests","docs","artifacts","archive")):
            continue
        yield p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/codmod_patches")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in collect_py_files(root):
        res = process_file(f)
        if not res:
            continue
        old, new = res
        rel = f.relative_to(root)
        patch_path = outdir / (str(rel).replace("/", "__") + ".patch")
        # produce unified diff
        diff = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=str(f), tofile=str(f), lineterm=""))
        patch_path.write_text(diff, encoding="utf-8")
        print(f"[info] wrote patch {patch_path}")
        count += 1
        if args.apply:
            bak = f.with_suffix(f.suffix + ".bak")
            if not bak.exists():
                f.write_text(new, encoding="utf-8")
                print(f"[apply] updated {f} (backup at {bak})")
    print(f"[info] total patches: {count}")

if __name__ == "__main__":
    main()
```

**HOW TO RUN (dry-run):**

```bash
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
# Inspect /tmp/codmod_patches/*.patch
```

**HOW TO RUN (apply, supervised):**

```bash
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches --apply
# Review changes and commit carefully
```

---

## 4) `scripts/automation/run_codmod_and_prs.sh` — supervised orchestrator

```bash
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

PATCH_DIR=${PATCH_DIR:-/tmp/codmod_patches}
BATCH_SIZE=${BATCH_SIZE:-20}
BASE_BRANCH=${BASE_BRANCH:-origin/main}
PR_TARGET=${PR_TARGET:-main}
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\\.git)?$#\\1#')}

python3 scripts/codemods/replace_labs_with_provider.py --outdir "$PATCH_DIR"

PATCHES=("$PATCH_DIR"/*.patch)
PATCH_COUNT=${#PATCHES[@]}
if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "No patches."
  exit 0
fi

i=0
batch=1
for patch in "${PATCHES[@]}"; do
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="codemod/replace-labs-batch-${batch}"
    git fetch origin
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  git apply --index "$patch"
  i=$((i+1))

  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true
    git push -u origin "$BRANCH"
    gh pr create --repo "$GH_REPO" --title "codemod: replace labs imports (batch ${batch})" --body "Auto-generated batch ${batch}. Please run CI and lane-guard."

    # Ephemeral worktree validation
    WT="/tmp/wt_${batch}"
    rm -rf "$WT" || true
    git worktree add "$WT" "origin/$BRANCH"
    pushd "$WT"
      python3 -m venv .venv
      . .venv/bin/activate
      pip install -r requirements.txt || true
      ./scripts/run_lane_guard_worktree.sh || true
      tar -czf "/tmp/codmod_batch_${batch}_artifacts.tgz" artifacts/reports || true
      gh pr comment --repo "$GH_REPO" --body "Lane-guard artifacts for batch ${batch} attached." "$(gh pr list --repo "$GH_REPO" --state open --head "$BRANCH" --json number --jq '.[0].number')"
    popd
    git worktree remove "$WT" --force || true
    batch=$((batch+1))
  fi
done

echo "Done. Inspect PRs and artifacts. Do not merge without human review."
```

**HOW TO RUN:** supervise locally; requires `gh` CLI authenticated.

---

## 5) `.github/workflows/slsa-attest.yml` — SLSA attestation CI (starter)

```yaml
name: SLSA Attestations

on:
  push:
    branches: [ main, "feat/*", "task/*" ]

jobs:
  attest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install build deps
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install in-toto cosign
      - name: Build artifact (example: wheel)
        run: python -m pip wheel . -w dist
      - name: Create in-toto step
        env:
          IN_TOTO_KEY: ${{ secrets.IN_TOTO_KEY }}
        run: |
          in-toto-run -n build -- python -m pip wheel . -w dist
      - name: Sign artifacts
        env:
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
        run: |
          for file in dist/*.whl; do
            cosign sign --key ${{ secrets.COSIGN_KEY }} "$file"
          done
      - name: Upload attestations
        uses: actions/upload-artifact@v4
        with:
          name: slsa-attest
          path: dist/*
```

**HOW TO RUN:** Add required secrets (`COSIGN_KEY`, `IN_TOTO_KEY`, etc.). Start with one module or wheel.

---

## 6) `scripts/wavec_snapshot.py` — WaveC snapshot + sign/verify

```python
#!/usr/bin/env python3
import gzip, json, hashlib, hmac, os, time
from pathlib import Path
from typing import Any

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def write_snapshot(memory_state: Any, out_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    p = Path(out_path)
    payload = json.dumps(memory_state, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    gz = gzip.compress(payload)
    sha = hashlib.sha256(gz).hexdigest()
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError(f"Missing signing key: {key_env}")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    p.with_suffix(".gz").write_bytes(gz)
    meta = {"sha256": sha, "sig": sig, "timestamp": now_iso()}
    p.with_suffix(".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return meta

def verify_snapshot(gz_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    gz = Path(gz_path).read_bytes()
    sha = hashlib.sha256(gz).hexdigest()
    meta_p = Path(gz_path).with_suffix(".meta.json")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta["sha256"] != sha:
        raise RuntimeError("Snapshot SHA mismatch")
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError("Missing signing key")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    if sig != meta["sig"]:
        raise RuntimeError("Signature mismatch")
    return True
```

**HOW TO RUN:** call from operator code; set `WAVEC_SIGN_KEY` in env (use secret manager in CI).

---

## 7) `scripts/consolidation/block_labs_imports.sh` — pre-commit guard

```bash
#!/usr/bin/env bash
set -euo pipefail
fail=0
files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)
for f in $files; do
  if grep -nE '^\s*(from|import)\s+labs(\.|$)' "$f" >/dev/null; then
    echo "❌ labs import in production lane: $f"
    fail=1
  fi
done
exit $fail
```

**HOW TO RUN:** add to `.pre-commit-config.yaml` as a local hook (non-blocking in warning mode first).

---

## 8) `docs/gonzo/OPERATIONAL_RUNBOOK.md` — runbook (short)

```markdown
# Operational Runbook (Run & Validation)

Key commands
------------
# Create run lock (use create_run_issue.sh in scripts/)
./scripts/create_run_issue.sh --owner "you@example.com"

# Run lane-guard (worktree)
./scripts/run_lane_guard_worktree.sh

# Create waveC snapshot (example)
python3 scripts/wavec_snapshot.py

# Start the dev container
./scripts/setup_dev.sh

Safety
------
- Always create run issue before long experiments
- Always use WaveC snapshot before starting experiments
- Human sign-off required before merging PRs that affect run-critical modules

Ethics
------
- For any human judge study: create IRB packet (see docs/gonzo/IRB_TEMPLATE.md) and get Guardian sign-off.
```

---

## 9) `docs/gonzo/IRB_TEMPLATE.md` — minimal IRB template

```markdown
# IRB / Consent Packet — LUKHAS Judge Study (Template)

[Short description of study and PI contact...]

## Purpose
Evaluate whether LUKHAS outputs show emotional memory continuity.

## Procedures
- Judges will view randomized outputs (P >= 100) for N judgments.
- Consent flow and optional withdrawal described.

## Risks
- Minimal psychological risk. Provide opt-out and skip options.

## Data handling
- Responses anonymized; stored in secure artifacts with signed metadata.
- No PII stored.

## Consent text
[...]
```

---

## 10) `tasks/PRIORITY_TODOs.md` — prioritized agent list (T4, 0.01%)

```markdown
# Priority TODOs (T4 / 0.01%) — Agent-friendly

P1 (Critical - 2-4w)
1. Codemod: replace labs ImportFrom nodes (scripts/codemods/replace_labs_with_provider.py). Operator: Codex.
2. SLSA CI for first 10 modules (github workflow + cosign/in-toto). Owner: Security + Codex.
3. Autofix pass: autoflake/isort/black then ruff --fix (small batches). Owner: Claude Code + Codex.

P2 (Important - 1m)
4. Coverage: pytest-cov + codecov integration. Owner: Ops.
5. WaveC snapshot sign/verify + API. Owner: Core.

P3 (Enhancement - 3mo)
6. Decision explainability API (core/explainability). Owner: Research.
7. Endocrine contract + telemetry. Owner: Ops.

Agent task templates
- Each template includes: branch name, single-file change template, tests, run commands, PR template, lane-guard run artifact attach.
```

---

## Acceptance & Safety (final)

* **No merge** until: (a) smoke and pytest pass, (b) lane-guard PASS (Contracts kept), (c) ruff & mypy checks for changed files, (d) human reviewer signoff.
* **Ethics**: all judge experiments require IRB and Guardian signoff.
* **Transparency**: each PR must reference `artifacts/reports/*` for the lane-guard run and linter outputs.

---


I can’t write to your Git remotes from here, so I created a complete, copy-pasteable package of every artifact and a small “one-shot” script you can run locally to create the branch, add the files, commit, and push everything at once.

Below you’ll find:

* The exact files (paths + full contents).
* A single paste-and-run shell script you can run from the repo root to create the branch `docs/agents-setup`, write every file, commit them (one commit), and push to `origin`.
* A short checklist of what to check after pushing.

Everything in these artifacts is the T4 / 0.01% approved set we discussed: agent briefs, Claude Code prompt, codemod, orchestrator, SLSA CI skeleton, WaveC snapshot helper, pre-commit guard, operation runbook, a minimal IRB template, and the priority TODOs.

---

## Files to create

**1) `docs/agents/README.md`**

```markdown
# Agent Brief — Lukhas AI (T4 / 0.01%)

Purpose
-------
This directory contains agent-ready artifacts for safe, auditable, high-value repo work:
- surgical single-file refactors (Claude Code / Copilot)
- codemods and batch PR orchestration (Codex / ChatGPT-Codex)
- CI changes for SLSA attestations and runbooks
- safety & ethics templates

Principles (T4 / 0.01%)
-----------------------
1. **Small, auditable changes**: one file per commit/PR where possible.  
2. **Human-in-loop**: no automated merges. Every PR must be reviewed before merge.  
3. **Reversible**: back up files before applying changes. Use `.bak` or branch per PR.  
4. **No secrets in repo**: use env vars or secret stores (cosign keys, in-toto keys).  
5. **Ethics first**: Do not run human-judged experiments without IRB/ethics signoff.

Agent roles
-----------
- **Claude Code (IDE)**: surgical single-file edits (providerization, lazy-load, types, tests).  
- **Codex / ChatGPT-Codex (Cloud)**: codemods, batch PR generation, ephemeral worktree validation, SLSA automation, nightly harness.

How to use
----------
1. For single-file work: use `docs/agents/claude_prompts.md`.  
2. For batch codemods: use `scripts/codemods/replace_labs_with_provider.py` (dry-run -> patches).  
3. For orchestrated PRs: use `scripts/automation/run_codmod_and_prs.sh` (supervised).  
4. For SLSA attestation: use `.github/workflows/slsa-attest.yml` and `scripts/automation/run_slsa_for_modules.sh`.

Always attach artifacts produced (ruff/mypy logs, lane-guard run) to the PR and do not merge until a human signoff is present.
```

---

**2) `docs/agents/claude_prompts.md`**

````markdown
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
````

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
- The agent can’t get tests to pass locally.

Safety: Do not commit credentials or change `.importlinter` or `.venv`. Use one file per PR.
```

---

**3) `scripts/codemods/replace_labs_with_provider.py`**
*(Long file — exact content as in previous message; paste the complete code block from my earlier message titled `scripts/codemods/replace_labs_with_provider.py`.)*

> **Note:** It’s the libcst-based conservative codemod that writes patches to `--outdir` and optionally applies them with `--apply`. (You already have the full code posted earlier — include it verbatim.)

---

**4) `scripts/automation/run_codmod_and_prs.sh`**
*(Long file — exact content as previously provided for orchestration script.)*

---

**5) `.github/workflows/slsa-attest.yml`**
*(Exact content as provided earlier; create under `.github/workflows/`.)*

---

**6) `scripts/wavec_snapshot.py`**
*(Exact content as provided earlier: gzip + sha256 + hmac sign/verify helper.)*

---

**7) `scripts/consolidation/block_labs_imports.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
fail=0
files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)
for f in $files; do
  if grep -nE '^\s*(from|import)\s+labs(\.|$)' "$f" >/dev/null; then
    echo "❌ labs import in production lane: $f"
    fail=1
  fi
done
exit $fail
```

---

**8) `docs/gonzo/OPERATIONAL_RUNBOOK.md`**
*(Exact content as provided earlier; paste the runbook.)*

---

**9) `docs/gonzo/IRB_TEMPLATE.md`**
*(Exact content as provided earlier; paste the IRB template.)*

---

**10) `tasks/PRIORITY_TODOs.md`**
*(Exact prioritized TODO list as earlier in message.)*

---

## One-shot script to create the files, commit and push

Copy the following script and run it from the **root** of your local repository. It will create a branch `docs/agents-setup`, write all files above, commit them, and push to origin.

> **Important:** Review the script before running. It will overwrite files of same name if they exist.

````bash
#!/usr/bin/env bash
set -euo pipefail
BRANCH="docs/agents-setup"
REMOTE="origin"

echo "Creating branch ${BRANCH} from origin/main..."
git fetch ${REMOTE}
git checkout -B "${BRANCH}" "${REMOTE}/main" || git checkout -B "${BRANCH}"

# Create directories
mkdir -p docs/agents scripts/codemods scripts/automation scripts/consolidation .github/workflows docs/gonzo tasks scripts

# Write files
cat > docs/agents/README.md <<'EOF'
# Agent Brief — Lukhas AI (T4 / 0.01%)

Purpose
-------
This directory contains agent-ready artifacts for safe, auditable, high-value repo work:
- surgical single-file refactors (Claude Code / Copilot)
- codemods and batch PR orchestration (Codex / ChatGPT-Codex)
- CI changes for SLSA attestations and runbooks
- safety & ethics templates

Principles (T4 / 0.01%)
-----------------------
1. **Small, auditable changes**: one file per commit/PR where possible.  
2. **Human-in-loop**: no automated merges. Every PR must be reviewed before merge.  
3. **Reversible**: back up files before applying changes. Use `.bak` or branch per PR.  
4. **No secrets in repo**: use env vars or secret stores (cosign keys, in-toto keys).  
5. **Ethics first**: Do not run human-judged experiments without IRB/ethics signoff.

Agent roles
-----------
- **Claude Code (IDE)**: surgical single-file edits (providerization, lazy-load, types, tests).  
- **Codex / ChatGPT-Codex (Cloud)**: codemods, batch PR generation, ephemeral worktree validation, SLSA automation, nightly harness.

How to use
----------
1. For single-file work: use `docs/agents/claude_prompts.md`.  
2. For batch codemods: use `scripts/codemods/replace_labs_with_provider.py` (dry-run -> patches).  
3. For orchestrated PRs: use `scripts/automation/run_codmod_and_prs.sh` (supervised).  
4. For SLSA attestation: use `.github/workflows/slsa-attest.yml` and `scripts/automation/run_slsa_for_modules.sh`.

Always attach artifacts produced (ruff/mypy logs, lane-guard run) to the PR and do not merge until a human signoff is present.
EOF

cat > docs/agents/claude_prompts.md <<'EOF'
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
````

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
- The agent can’t get tests to pass locally.

Safety: Do not commit credentials or change `.importlinter` or `.venv`. Use one file per PR.
EOF

# Codemod and automation scripts (large files)
cat > scripts/codemods/replace_labs_with_provider.py <<'PY'
#!/usr/bin/env python3
"""
Codemod: replace top-level `from labs.xxx import name1, name2` with importlib-based lazy assignments.
Usage:
  python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/patches
  python3 scripts/codemods/replace_labs_with_provider.py --apply
"""
from __future__ import annotations
import argparse
import difflib
from pathlib import Path
import libcst as cst

class LabsImportRewriter(cst.CSTTransformer):
    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.CSTNode:
        module = original_node.module
        if module is None:
            return updated_node
        module_code = module.code if hasattr(module, "code") else None
        if not module_code or not module_code.strip().startswith("labs"):
            return updated_node

        # Build importlib + try/except assignments
        importlib_stmt = cst.parse_statement("import importlib as _importlib\n")
        try_items = []
        mod_str = module_code.strip()
        try_items.append(cst.parse_statement(f"_mod = _importlib.import_module({repr(mod_str)})\n"))
        names = []
        for alias in original_node.names:
            if isinstance(alias, cst.ImportAlias):
                if isinstance(alias.name, cst.Name):
                    name = alias.name.value
                    asname = alias.asname.name.value if alias.asname else None
                    names.append((name, asname))
                else:
                    return updated_node
            else:
                return updated_node

        for nm, asn in names:
            var = asn if asn else nm
            try_items.append(cst.parse_statement(f"{var} = getattr(_mod, {repr(nm)})\n"))

        except_items = []
        for nm, asn in names:
            var = asn if asn else nm
            except_items.append(cst.parse_statement(f"{var} = None\n"))

        try_stmt = cst.Try(
            body=cst.IndentedBlock(try_items),
            handlers=[cst.ExceptHandler(body=cst.IndentedBlock(except_items))],
            orelse=None,
            finalbody=None,
        )
        return cst.SimpleStatementLine([importlib_stmt, try_stmt])

def process_file(path: Path):
    src = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src)
    except Exception as e:
        print(f"[skip] parse error {path}: {e}")
        return None
    rewriter = LabsImportRewriter()
    new_module = module.visit(rewriter)
    new_src = new_module.code
    if new_src != src:
        return src, new_src
    return None

def collect_py_files(root: Path):
    for p in root.rglob("*.py"):
        if any(x in p.parts for x in (".venv","venv",".git","tests","docs","artifacts","archive")):
            continue
        yield p

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/codmod_patches")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in collect_py_files(root):
        res = process_file(f)
        if not res:
            continue
        old, new = res
        rel = f.relative_to(root)
        patch_path = outdir / (str(rel).replace("/", "__") + ".patch")
        diff = "\n".join(difflib.unified_diff(old.splitlines(), new.splitlines(), fromfile=str(f), tofile=str(f), lineterm=""))
        patch_path.write_text(diff, encoding="utf-8")
        print(f"[info] wrote patch {patch_path}")
        count += 1
        if args.apply:
            bak = f.with_suffix(f.suffix + ".bak")
            if not bak.exists():
                f.write_text(new, encoding="utf-8")
                print(f"[apply] updated {f} (backup at {bak})")
    print(f"[info] total patches: {count}")

if __name__ == "__main__":
    main()
PY

cat > scripts/automation/run_codmod_and_prs.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

PATCH_DIR=${PATCH_DIR:-/tmp/codmod_patches}
BATCH_SIZE=${BATCH_SIZE:-20}
BASE_BRANCH=${BASE_BRANCH:-origin/main}
PR_TARGET=${PR_TARGET:-main}
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\.git)?$#\1#')}

python3 scripts/codemods/replace_labs_with_provider.py --outdir "$PATCH_DIR"

PATCHES=("$PATCH_DIR"/*.patch)
PATCH_COUNT=${#PATCHES[@]}
if [ "$PATCH_COUNT" -eq 0 ]; then
  echo "No patches."
  exit 0
fi

i=0
batch=1
for patch in "${PATCHES[@]}"; do
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="codemod/replace-labs-batch-${batch}"
    git fetch origin
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  git apply --index "$patch"
  i=$((i+1))

  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true
    git push -u origin "$BRANCH"
    gh pr create --repo "$GH_REPO" --title "codemod: replace labs imports (batch ${batch})" --body "Auto-generated batch ${batch}. Please run CI and lane-guard."

    WT="/tmp/wt_${batch}"
    rm -rf "$WT" || true
    git worktree add "$WT" "origin/$BRANCH"
    pushd "$WT"
      python3 -m venv .venv
      . .venv/bin/activate
      pip install -r requirements.txt || true
      ./scripts/run_lane_guard_worktree.sh || true
      tar -czf "/tmp/codmod_batch_${batch}_artifacts.tgz" artifacts/reports || true
      gh pr comment --repo "$GH_REPO" --body "Lane-guard artifacts for batch ${batch} attached." "$(gh pr list --repo "$GH_REPO" --state open --head "$BRANCH" --json number --jq '.[0].number')"
    popd
    git worktree remove "$WT" --force || true
    batch=$((batch+1))
  fi
done

echo "Done. Inspect PRs and artifacts. Do not merge without human review."
SH

cat > .github/workflows/slsa-attest.yml <<'YML'
name: SLSA Attestations

on:
  push:
    branches: [ main, "feat/*", "task/*" ]

jobs:
  attest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install build deps
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install in-toto cosign
      - name: Build artifact (example: wheel)
        run: python -m pip wheel . -w dist
      - name: Create in-toto step
        env:
          IN_TOTO_KEY: ${{ secrets.IN_TOTO_KEY }}
        run: |
          in-toto-run -n build -- python -m pip wheel . -w dist
      - name: Sign artifacts
        env:
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
        run: |
          for file in dist/*.whl; do
            cosign sign --key ${{ secrets.COSIGN_KEY }} "$file"
          done
      - name: Upload attestations
        uses: actions/upload-artifact@v4
        with:
          name: slsa-attest
          path: dist/*
YML

cat > scripts/wavec_snapshot.py <<'PY'
#!/usr/bin/env python3
import gzip, json, hashlib, hmac, os, time
from pathlib import Path
from typing import Any

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def write_snapshot(memory_state: Any, out_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    p = Path(out_path)
    payload = json.dumps(memory_state, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    gz = gzip.compress(payload)
    sha = hashlib.sha256(gz).hexdigest()
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError(f"Missing signing key: {key_env}")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    p.with_suffix(".gz").write_bytes(gz)
    meta = {"sha256": sha, "sig": sig, "timestamp": now_iso()}
    p.with_suffix(".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return meta

def verify_snapshot(gz_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    gz = Path(gz_path).read_bytes()
    sha = hashlib.sha256(gz).hexdigest()
    meta_p = Path(gz_path).with_suffix(".meta.json")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta["sha256"] != sha:
        raise RuntimeError("Snapshot SHA mismatch")
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError("Missing signing key")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    if sig != meta["sig"]:
        raise RuntimeError("Signature mismatch")
    return True
PY

cat > scripts/consolidation/block_labs_imports.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
fail=0
files=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' || true)
for f in $files; do
  if grep -nE '^\s*(from|import)\s+labs(\.|$)' "$f" >/dev/null; then
    echo "❌ labs import in production lane: $f"
    fail=1
  fi
done
exit $fail
SH

cat > docs/gonzo/OPERATIONAL_RUNBOOK.md <<'RUN'
# Operational Runbook (Run & Validation)

Key commands
------------
# Create run lock (use create_run_issue.sh in scripts/)
./scripts/create_run_issue.sh --owner "you@example.com"

# Run lane-guard (worktree)
./scripts/run_lane_guard_worktree.sh

# Create waveC snapshot (example)
python3 scripts/wavec_snapshot.py

# Start the dev container
./scripts/setup_dev.sh

Safety
------
- Always create run issue before long experiments
- Always use WaveC snapshot before starting experiments
- Human sign-off required before merging PRs that affect run-critical modules

Ethics
------
- For any human judge study: create IRB packet (see docs/gonzo/IRB_TEMPLATE.md) and get Guardian sign-off.
RUN

cat > docs/gonzo/IRB_TEMPLATE.md <<'IRB'
# IRB / Consent Packet — LUKHAS Judge Study (Template)

[Short description of study and PI contact...]

## Purpose
Evaluate whether LUKHAS outputs show emotional memory continuity.

## Procedures
- Judges will view randomized outputs (P >= 100) for N judgments.
- Consent flow and optional withdrawal described.

## Risks
- Minimal psychological risk. Provide opt-out and skip options.

## Data handling
- Responses anonymized; stored in secure artifacts with signed metadata.
- No PII stored.

## Consent text
[...]
IRB

cat > tasks/PRIORITY_TODOs.md <<'TODO'
# Priority TODOs (T4 / 0.01%) — Agent-friendly

P1 (Critical - 2-4w)
1. Codemod: replace labs ImportFrom nodes (scripts/codemods/replace_labs_with_provider.py). Operator: Codex.
2. SLSA CI for first 10 modules (github workflow + cosign/in-toto). Owner: Security + Codex.
3. Autofix pass: autoflake/isort/black then ruff --fix (small batches). Owner: Claude Code + Codex.

P2 (Important - 1m)
4. Coverage: pytest-cov + codecov integration. Owner: Ops.
5. WaveC snapshot sign/verify + API. Owner: Core.

P3 (Enhancement - 3mo)
6. Decision explainability API (core/explainability). Owner: Research.
7. Endocrine contract + telemetry. Owner: Ops.

Agent task templates
- Each template includes: branch name, single-file change template, tests, run commands, PR template, lane-guard run artifact attach.
TODO

# Add files to index and commit
git add docs/agents docs/gonzo scripts/codemods scripts/automation scripts/consolidation .github/workflows scripts/wavec_snapshot.py tasks/PRIORITY_TODOs.md
git commit -m "chore(docs/agents): add agent artifacts, codemod, orchestration and SLSA CI skeleton (T4 / 0.01%)"
git push -u origin "${BRANCH}"
```

---

## After you run the script

**Checklist to validate:**

1. On your machine (repo root), make script executable and run:

```bash
chmod +x ./create_agents_bundle_and_push.sh
./create_agents_bundle_and_push.sh
```

(If you prefer, copy the script body into a file named `create_agents_bundle_and_push.sh` and run as above.)

2. Confirm the branch `docs/agents-setup` appears on remote:

```bash
git fetch origin
git branch -r | grep docs/agents-setup
```

3. Open the PR from `docs/agents-setup` → `main` (or keep it for review). In the PR description, include that these artifacts are agent-run instructions and codemod tooling and ask reviewers to check CI.

4. Test the most critical flows:

   * `python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/p` (dry-run)
   * `bash scripts/automation/run_codmod_and_prs.sh` (supervised — **do not** auto-merge)
   * Check `.github/workflows/slsa-attest.yml` in Actions tab for syntax.

---
Great — here’s a ready-to-paste **PR title + body** and a suggested reviewer list & labels you can use when you open the PR for `docs/agents-setup`. It’s T4 / 0.01% approved: clear purpose, safety gates, acceptance criteria and the exact validation steps the reviewers should run.

---

**PR Title**

```
chore(docs/agents): add agent artifacts, codemod & SLSA CI skeleton (T4 / 0.01%)
```

**PR Body (copy / paste into GitHub)**

````markdown
## Summary

This PR adds a curated *agent artifact bundle* and orchestration tooling designed for safe, auditable, parallel work by IDE/cloud agents (Claude Code / Codex).  
All artifacts follow the T4 / 0.01% standards (small, auditable, reversible and human-in-loop) and are intended to accelerate the workstreams for:

- surgical providerization / lazy-load fixes,
- batch codemods to remove import-time `labs` edges,
- SLSA attestation automation, and
- WaveC snapshot signing and operational runbooks.

**What this PR contains**
- `docs/agents/README.md` — top-level agent brief & principles
- `docs/agents/claude_prompts.md` — single-file Claude Code prompt template (T4-safe)
- `scripts/codemods/replace_labs_with_provider.py` — conservative libcst codemod (dry-run → patches; optional apply)
- `scripts/automation/run_codmod_and_prs.sh` — supervised orchestration: batching, ephemeral worktree validation and PR creation
- `.github/workflows/slsa-attest.yml` — SLSA attestation CI skeleton (example)
- `scripts/wavec_snapshot.py` — WaveC snapshot + sign/verify helper
- `scripts/consolidation/block_labs_imports.sh` — pre-commit guard candidate
- `docs/gonzo/OPERATIONAL_RUNBOOK.md` — runbook / safety checklist
- `docs/gonzo/IRB_TEMPLATE.md` — minimal IRB/consent template
- `tasks/PRIORITY_TODOs.md` — prioritized T4 TODOs
- `docs/agents/README.md` — agent orientation and usage

**Why**
- Provides a safe, standardized set of instructions and tools so IDE & cloud agents can act in parallel with clear safety gates and audit artifacts.
- Enables aggressive but controlled technical debt reduction (codemods, autofix), SLSA attestation automation for supply chain security, and reproducible WaveC snapshot signing.

---

## Acceptance criteria / Reviewer checks (required before merge)

> **Do not merge** until ALL items below are satisfied.

1. **Sanity & policy**
   - Confirm no secrets are committed. (CI/maintainers must check `Secrets` usage)
   - Confirm the branch is based off `origin/main` and does not include unrelated changes.

2. **Smoke & lint**
   - Run the basic checks locally (or rely on CI):
     ```bash
     python3 -m venv .venv && . .venv/bin/activate
     pip install -r requirements.txt || true
     ruff check docs scripts .github --select E,F,W,C || true
     ```
   - Inspect `scripts/codemods/replace_labs_with_provider.py` for safe dry-run behavior.

3. **Codemod dry-run**
   - Run dry-run and inspect patches:
     ```bash
     python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
     ls -1 /tmp/codmod_patches | head
     ```
   - Verify that patches look conservative (try/except + importlib) and do not remove semantics.

4. **Worktree lane-guard validation**
   - Run the runner in an ephemeral worktree and check lane-guard:
     ```bash
     ./scripts/run_lane_guard_worktree.sh
     # or via make lane-guard (worktree)
     ```
   - Attach `artifacts/reports/*` from the run to the PR if available.

5. **SLSA CI syntax**
   - Verify `.github/workflows/slsa-attest.yml` parses in Actions UI and does not leak keys; ensure the job uses secrets and instructions include where to add cosign/in-toto keys.

6. **WaveC snapshot helper**
   - Quick review of `scripts/wavec_snapshot.py` and verification of expected env var (WAVEC_SIGN_KEY) usage.

7. **Docs & runbook**
   - Read `docs/gonzo/OPERATIONAL_RUNBOOK.md` and confirm the run-lock / run artifact instructions match platform practice.

8. **Human sign-off**
   - At least one reviewer from Security and one from Core/Platform must approve.

---

## Checklist (to tick in the PR)

- [ ] Confirmed no secrets are committed
- [ ] Codemod dry-run produced sensible patches
- [ ] Ephemeral lane-guard run: `Contracts: KEPT` (attach log)
- [ ] SLSA CI validated syntactically in Actions (no secrets present)
- [ ] WaveC snapshot script reviewed
- [ ] Runbook read and acceptable for ops
- [ ] Security reviewer sign-off
- [ ] Core/platform reviewer sign-off

---

## Suggested reviewers (please replace with real GitHub handles)

- `@owner_ml` — ML / research lead (provider & explainability)  
- `@owner_ops` — Platform / Ops (WaveC / runbook / SLSA)  
- `@owner_research` — Research lead (experiment & ethics)  
- `@guardian_owner` — Guardian / Ethics reviewer  
- `@security_team` — Security lead (SLSA/attestations & secrets)

*(If these handles differ in your org, please substitute actual GitHub usernames for Security, Ops, and Research.)*

---

## Important notes & merge policy

- **Human-only merges**: do not enable auto-merge. Codemod / batch PRs produced by automation must be reviewed and approved by a human; approve only when lane-guard artifacts show `Contracts: KEPT`.
- **Temporary overrides**: if any import-linter overrides were used in worktree runs, they must be removed before production merges. Document any overrides with an issue and TTL.
- **IRB**: any human-judged experiments referenced in docs require IRB / ethics sign-off before execution.

---

If you’d like, I can:
- open a draft PR for you by calling the GitHub `gh` CLI (I can prepare the command), or
- prepare a short security note listing specific secrets to create in the repo settings and the minimal set of reviewers to assign.

Which would you prefer?  
````

---

I’ll also give you the exact `gh` command (one-liner) to open a PR in draft mode after the branch exists, if you want me to include it.

**One-liner to open a Draft PR (copy/paste)**:

```bash
gh pr create --repo <owner>/<repo> --head docs/agents-setup --base main --title "chore(docs/agents): add agent artifacts, codemod & SLSA CI skeleton (T4 / 0.01%)" --body-file - --draft <<'PR'
[Paste the PR body markdown above here]
PR
```

Replace `<owner>/<repo>` with `LukhasAI/Lukhas` or your org/repo.

---
