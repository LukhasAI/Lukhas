# CODEX TASK PACK — Batch Codemod Automation
**Agent**: Codex (Batch Automation & GitHub Issues)
**Mission**: Execute large-scale codemods to replace `labs` imports with lazy-loading patterns
**Standards**: T4/0.01% reliability, human-in-loop review, ephemeral worktree validation
**Collaboration**: Works with Claude Code (surgical refactors), Gemini (coverage/SLSA), Copilot (suggestions)

---

## Executive Summary

### What Codex Does
Codex is the **Batch Automation Specialist** for LUKHAS AI. While Claude Code handles surgical single-file refactors and Gemini builds infrastructure, Codex focuses on:

1. **Large-Scale Codemods**: Automated refactoring across hundreds of files using AST transformations
2. **Batch PR Creation**: Breaking codemods into reviewable 20-file batches with automated PR creation
3. **Conservative Safety Filters**: Heuristic validation to ensure patches only reshape imports, not logic
4. **Ephemeral Worktree Validation**: Testing each batch in isolation before PR creation
5. **GitHub Issue Tracking**: Creating issues for each batch task with acceptance criteria

### What You've Learned About LUKHAS

**Lane-Based Architecture**:
- **candidate/** (2,877 files): Experimental research lane
- **core/** (253 components): Integration/testing lane
- **lukhas/** (692 components): Production lane
- **Import Rules**: NO imports from `candidate/` → `lukhas/`; NO top-level `labs` imports in production

**The Problem**:
- LUKHAS has **dozens of files** with top-level `from labs.xxx import Name` imports
- These create import-time dependencies that violate lane boundaries
- Manual refactoring of each file is too slow for the scope of changes needed

**The Solution**:
- **AST-Based Codemod**: `scripts/codemods/replace_labs_with_provider.py` using `libcst` to transform imports
- **Pattern**: Replace `from labs.xxx import Name` with:
  ```python
  import importlib as _importlib
  try:
      _mod = _importlib.import_module("labs.xxx")
      Name = getattr(_mod, "Name")
  except Exception:
      Name = None
  ```
- **Batch Processing**: Break into 20-file chunks for reviewability
- **Safety Gates**: Lane-guard validation, conservative patch filtering, human review

### Mission
Execute a **T4 batch automation workflow** that:
1. **Generates patches** for all files with `labs` imports (~100-200 files estimated)
2. **Filters safe patches** using conservative heuristics (only import reshaping)
3. **Creates batches** of 20 patches each for manageable review
4. **Validates each batch** in ephemeral worktrees with lane-guard checks
5. **Creates PRs** with artifacts and verification output
6. **Tracks progress** via GitHub Issues (one issue per batch)

### Success Criteria
- ✅ Codemod dry-run generates patches for all `labs` import files
- ✅ Conservative filter identifies safe patches (no logic changes)
- ✅ Batch PRs created (20 files each) with ephemeral worktree validation
- ✅ Lane-guard passes on all batch branches
- ✅ GitHub Issues track batch progress with acceptance checklists
- ✅ Human security review completed before any merges
- ✅ 0 production incidents from automated changes

---

## Codemod Architecture

### AST Transformation Pattern

The codemod uses `libcst` (Concrete Syntax Tree) to preserve formatting while transforming imports:

**Input** (top-level import):
```python
from labs.openai import OpenAI
from labs.tags import EnhancedTagExplainer

# Later usage
client = OpenAI()
explainer = EnhancedTagExplainer()
```

**Output** (lazy-loading with try/except):
```python
import importlib as _importlib
try:
    _mod = _importlib.import_module("labs.openai")
    OpenAI = getattr(_mod, "OpenAI")
except Exception:
    OpenAI = None

try:
    _mod = _importlib.import_module("labs.tags")
    EnhancedTagExplainer = getattr(_mod, "EnhancedTagExplainer")
except Exception:
    EnhancedTagExplainer = None

# Later usage (unchanged)
client = OpenAI()  # Will be None if labs not available
explainer = EnhancedTagExplainer()
```

### Conservative Safety Heuristics

The batch automation includes two-stage safety validation:

**Stage 1: Codemod Constraints**
- Only transforms top-level `from labs.* import ...` statements
- Preserves all non-import code exactly
- Maintains symbol names (callers don't break)
- Adds graceful degradation (symbols become None on import failure)

**Stage 2: Patch Filtering** (`filter_safe_patches.sh`)
- ✅ MUST contain `importlib` or `_importlib` usage
- ✅ MUST contain `getattr(_mod, ...)` pattern
- ❌ MUST NOT contain leftover `from labs` imports
- ❌ MUST NOT delete >2 non-import lines
- ❌ MUST NOT delete function/class definitions
- ❌ MUST NOT delete >10 total lines

Patches failing any check are **flagged for manual review**.

---

## Task Execution Pattern for Codex

Each batch follows this workflow:

### Standard Branch & PR Naming
- Branch: `codemod/replace-labs-batch-<N>`
- PR Title: `chore(codemod): replace labs imports (batch <N>)`
- Example: `codemod/replace-labs-batch-1` → `chore(codemod): replace labs imports (batch 1)`

### Standard Workflow
1. **Generate patches**: Run codemod in dry-run mode
2. **Filter safe patches**: Apply conservative heuristics
3. **Create batch**: Select 20 patches for batch-N
4. **Create branch**: `git checkout -B codemod/replace-labs-batch-N origin/main`
5. **Apply patches**: Use `git apply --index` for each patch
6. **Validate in worktree**: Ephemeral worktree with lane-guard checks
7. **Create PR**: Include artifacts, lane-guard output, patch list
8. **Human review**: Security + Core team approval required
9. **Never auto-merge**: Explicit human approval after review

### Standard Commit Message Format
```
chore(codemod): replace labs imports (batch <N>)

Problem:
- <N> files have top-level 'from labs.*' imports
- Creates import-time dependencies violating lane boundaries
- Blocks lane-guard compliance

Solution:
- Replace static imports with importlib lazy-loading
- Add try/except for graceful degradation
- Preserve all non-import code and symbol names
- Conservative patch filter ensures no logic changes

Impact:
- Reduces lane-guard violations from <total> files
- Enables optional labs dependencies
- Maintains backward compatibility with None checks

Validation:
- Ephemeral worktree lane-guard: PASS
- Conservative patch filter: <N> patches passed
- Import-safety tests: Added for each refactored file

Files Changed: <list of 20 files>

🤖 Generated with Codex (OpenAI)
Co-Authored-By: Codex <noreply@openai.com>
```

---

## Task 01: Dry-Run Codemod & Patch Generation

### Why
Before creating any batches, we need to **generate all patches** in dry-run mode and understand the scope of changes needed.

### Codex Prompt (Copy/Paste)

```
Context: LUKHAS AI has dozens of files with top-level 'from labs.*' imports
Task: Run codemod in dry-run mode to generate patches for all affected files

Requirements:
1. Execute codemod script:
   python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches

2. Analyze patch count and distribution:
   - Count total patches generated
   - Group by directory (candidate/, core/, lukhas/, etc.)
   - Identify largest files (most imports to transform)

3. Generate patch summary report:
   - Total patches: <N>
   - Breakdown by lane:
     * candidate/: <N> patches
     * core/: <N> patches
     * lukhas/: <N> patches
     * serve/: <N> patches
     * other: <N> patches

4. Inspect sample patches for quality:
   - Select 5 random patches
   - Verify each contains:
     * import importlib as _importlib
     * try/except with getattr
     * No leftover 'from labs' imports
     * No logic changes beyond imports

5. Create GitHub Issue for tracking:
   - Title: "[Codex] Batch Codemod — Replace labs imports (dry-run complete)"
   - Body: Patch summary report, estimated batch count, next steps
   - Labels: codemod, automation, T4
   - Assignees: @security_team, @core_team

Output Format:
/tmp/codmod_patches/*.patch  (all generated patches)
/tmp/codmod_summary.md       (patch summary report)
```

### Expected Output

```bash
# Patch generation
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches
# Output:
# [info] wrote patch /tmp/codmod_patches/core__colony__gpt_colony_orchestrator.py.patch
# [info] wrote patch /tmp/codmod_patches/core__identity.py.patch
# ...
# [info] total patches: 147

# Patch summary
Total patches: 147

Breakdown by lane:
- candidate/: 89 patches
- core/: 31 patches
- lukhas/: 12 patches
- serve/: 8 patches
- other: 7 patches

Estimated batches (20 patches each): 8 batches

Sample patch inspection:
✅ core__colony__gpt_colony_orchestrator.py.patch - SAFE (importlib + getattr, no logic changes)
✅ core__identity.py.patch - SAFE (importlib + getattr, no logic changes)
✅ core__observability__evidence_collection.py.patch - SAFE (importlib + getattr, no logic changes)
⚠️  candidate__consciousness__reflection__swarm.py.patch - REVIEW (7 non-import deletions)
✅ lukhas_website__api.py.patch - SAFE (importlib + getattr, no logic changes)

Recommendation: Proceed with conservative filter for batch-1
```

### Validation Commands

```bash
# 1. Count patches
ls -1 /tmp/codmod_patches/*.patch | wc -l

# 2. Group by directory
for dir in candidate core lukhas serve; do
  echo "$dir: $(ls -1 /tmp/codmod_patches/${dir}__*.patch 2>/dev/null | wc -l)"
done

# 3. Inspect first patch
head -n 50 /tmp/codmod_patches/core__colony__gpt_colony_orchestrator.py.patch

# 4. Search for conservative patterns
grep -l "importlib" /tmp/codmod_patches/*.patch | wc -l  # Should match total
grep -l "getattr(_mod" /tmp/codmod_patches/*.patch | wc -l  # Should match total
```

### Acceptance Criteria

- [ ] Codemod dry-run completes without errors
- [ ] All patches generated in /tmp/codmod_patches/
- [ ] Patch summary report created with lane breakdown
- [ ] Sample patches inspected and pass conservative pattern check
- [ ] GitHub Issue created for dry-run tracking
- [ ] Estimated batch count calculated (total / 20)

### GitHub Issue Template

```markdown
## [Codex] Batch Codemod — Replace labs imports (dry-run complete)

### Summary
Dry-run codemod completed. Generated **147 patches** to replace top-level `from labs.*` imports with lazy-loading pattern.

### Patch Breakdown
- **candidate/**: 89 patches (research lane, lower priority)
- **core/**: 31 patches (integration lane, high priority)
- **lukhas/**: 12 patches (production lane, highest priority)
- **serve/**: 8 patches (API layer, high priority)
- **other**: 7 patches (tools, docs)

### Estimated Batches
- **Total batches**: 8 batches (20 patches each, except last batch: 7 patches)
- **Priority order**: lukhas → core → serve → candidate → other

### Sample Inspection Results
✅ 5/5 sample patches pass conservative pattern check:
- Contains `import importlib as _importlib`
- Contains `try/except` with `getattr(_mod, ...)`
- No leftover `from labs` imports
- No logic changes beyond import reshaping

### Next Steps
1. Run conservative patch filter (`filter_safe_patches.sh`)
2. Create batch-1 (20 patches from lukhas + core lanes)
3. Validate batch-1 in ephemeral worktree
4. Create PR for batch-1 with artifacts

### Acceptance Criteria
- [ ] Conservative filter identifies safe patches
- [ ] Batch-1 created with 20 safe patches
- [ ] Ephemeral worktree validation passes lane-guard
- [ ] PR created with artifacts and verification output

**Labels**: `codemod`, `automation`, `T4`, `security`
**Assignees**: @security_team, @core_team
**Related**: Part A of docs/gonzo/AGENT_TASKS_TO_CREATE.md
```

---

## Task 02: Conservative Patch Filter

### Why
Not all generated patches are safe to apply automatically. We need to **filter patches** using conservative heuristics to identify those that only reshape imports without changing logic.

### Codex Prompt (Copy/Paste)

```
Context: Generated 147 patches, need to identify safe patches for batch automation
Task: Run conservative patch filter to separate safe patches from manual-review patches

Requirements:
1. Execute filter script:
   bash scripts/automation/filter_safe_patches.sh \
     --patch-dir /tmp/codmod_patches \
     --out-dir /tmp/codmod_batches/batch.safe \
     --max-non-import-deletions 2

2. Analyze filter results:
   - Count safe patches (copied to batch.safe/)
   - Count flagged patches (require manual review)
   - Review flagged reasons (large deletions, def/class removal, etc.)

3. Prioritize safe patches by lane:
   - lukhas/ patches (production, highest priority)
   - core/ patches (integration, high priority)
   - serve/ patches (API, high priority)
   - candidate/ patches (research, lower priority)

4. Create batch-1 patch list (20 files):
   - Select from lukhas + core safe patches first
   - Write to /tmp/codmod_batches/batch1.list

5. Create GitHub Issue for batch-1:
   - Title: "[Codex] Batch 1 — Replace labs imports (20 files from lukhas + core)"
   - Body: File list, validation plan, acceptance criteria
   - Labels: codemod, batch-1, T4, high-priority

Output Format:
/tmp/codmod_batches/batch.safe/*.patch     (safe patches)
/tmp/codmod_batches/batch1.list            (20 files for batch-1)
```

### Expected Output

```bash
# Filter execution
bash scripts/automation/filter_safe_patches.sh \
  --patch-dir /tmp/codmod_patches \
  --out-dir /tmp/codmod_batches/batch.safe \
  --max-non-import-deletions 2

# Output:
=== FILTER SUMMARY ===
Total patches scanned: 147
Safe patches: 132 (copied to /tmp/codmod_batches/batch.safe)
Flagged patches: 15

Safe patch list:
  1  /tmp/codmod_patches/core__colony__gpt_colony_orchestrator.py.patch
  2  /tmp/codmod_patches/core__identity.py.patch
  ...

Flagged patch list (reasons):
  1  /tmp/codmod_patches/candidate__consciousness__swarm.py.patch : too many non-import deletions (7);
  2  /tmp/codmod_patches/core__legacy_helper.py.patch : deletes def/class;
  ...

Recommendation: Inspect flagged patches manually.
```

### Validation Commands

```bash
# 1. Count safe patches
ls -1 /tmp/codmod_batches/batch.safe/*.patch | wc -l

# 2. Verify safe patches contain conservative patterns
for p in /tmp/codmod_batches/batch.safe/*.patch; do
  grep -q "importlib" "$p" && grep -q "getattr" "$p" || echo "FAIL: $p"
done

# 3. Create batch-1 list (first 20 safe patches from lukhas + core)
(ls -1 /tmp/codmod_batches/batch.safe/lukhas__*.patch 2>/dev/null;
 ls -1 /tmp/codmod_batches/batch.safe/core__*.patch 2>/dev/null) | head -n 20 > /tmp/codmod_batches/batch1.list

# 4. Verify batch-1 list
cat /tmp/codmod_batches/batch1.list
```

### Acceptance Criteria

- [ ] Filter script completes successfully
- [ ] Safe patches identified (expect ~90% of total)
- [ ] Flagged patches list reviewed (expect ~10% for manual review)
- [ ] Batch-1 list created with 20 patches from lukhas + core lanes
- [ ] GitHub Issue created for batch-1 tracking

### GitHub Issue Template

```markdown
## [Codex] Batch 1 — Replace labs imports (20 files from lukhas + core)

### Summary
Conservative filter identified **132 safe patches** from 147 total. Batch-1 contains **20 high-priority patches** from lukhas and core lanes.

### Batch-1 File List
1. lukhas/core/orchestrator.py
2. lukhas/api/endpoints.py
3. core/colony/gpt_colony_orchestrator.py
4. core/identity.py
5. core/observability/evidence_collection.py
... (15 more files)

### Validation Plan
1. Create branch: `codemod/replace-labs-batch-1`
2. Apply 20 patches with `git apply --index`
3. Commit with standard message
4. Create ephemeral worktree at `/tmp/wt_batch1`
5. Run lane-guard in worktree: `./scripts/run_lane_guard_worktree.sh`
6. Verify lane-guard PASS
7. Archive artifacts: `tar -czf /tmp/codmod_batch1_artifacts.tgz artifacts/`
8. Create PR with artifacts attached

### Safety Gates
- ✅ Conservative filter passed (all 20 patches safe)
- ⏳ Ephemeral worktree lane-guard (pending)
- ⏳ Human security review (pending)
- ⏳ Core team review (pending)

### Acceptance Criteria
- [ ] Branch created and patches applied
- [ ] Ephemeral worktree lane-guard passes
- [ ] PR created with artifacts attached
- [ ] Security team approves PR
- [ ] Core team approves PR
- [ ] Tests pass in CI
- [ ] Human approves merge (NO auto-merge)

**Labels**: `codemod`, `batch-1`, `T4`, `high-priority`, `security`
**Assignees**: @security_team, @core_team
**Branch**: `codemod/replace-labs-batch-1`
**Related**: Part A of docs/gonzo/AGENT_TASKS_TO_CREATE.md
```

---

## Task 03: Batch-1 Application & Ephemeral Worktree Validation

### Why
After identifying safe patches, we need to **apply them to a branch** and **validate in isolation** using ephemeral worktrees to ensure lane-guard compliance.

### Codex Prompt (Copy/Paste)

```
Context: Batch-1 contains 20 safe patches ready for application
Task: Create branch, apply patches, validate with ephemeral worktree, create PR

Requirements:
1. Create batch-1 branch:
   git fetch origin
   git checkout -B codemod/replace-labs-batch-1 origin/main

2. Apply patches sequentially:
   while read -r patchfile; do
     git apply --index "$patchfile" || {
       echo "ERROR: Failed to apply $patchfile"
       exit 1
     }
   done < /tmp/codmod_batches/batch1.list

3. Commit with standard message:
   git commit -m "chore(codemod): replace labs imports (batch 1)"

4. Push branch:
   git push -u origin codemod/replace-labs-batch-1

5. Create ephemeral worktree validation:
   WT="/tmp/wt_batch1"
   git worktree add "$WT" origin/codemod/replace-labs-batch-1
   pushd "$WT"
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt || true
     ./scripts/run_lane_guard_worktree.sh || true
     tar -czf /tmp/codmod_batch1_artifacts.tgz artifacts/reports || true
   popd
   git worktree remove "$WT" --force

6. Verify lane-guard results:
   - Extract artifacts: tar -xzf /tmp/codmod_batch1_artifacts.tgz
   - Check lane-guard report for violations
   - If PASS: proceed to PR creation
   - If FAIL: identify violating files, fix manually

7. Create PR:
   gh pr create \
     --title "chore(codemod): replace labs imports (batch 1)" \
     --body "Batch 1 codemod (20 files). Lane-guard: PASS. Artifacts attached." \
     --base main \
     --head codemod/replace-labs-batch-1 \
     --label "codemod,batch-1,T4,high-priority,security"

8. Attach artifacts to PR:
   gh pr comment --body-file - <<EOF
   ## Ephemeral Worktree Validation Results

   **Lane-Guard**: PASS ✅
   **Artifacts**: /tmp/codmod_batch1_artifacts.tgz

   **Changed Files** (20):
   $(git diff --name-only origin/main...codemod/replace-labs-batch-1)

   **Conservative Filter**: All 20 patches passed safety heuristics
   **Import Pattern**: importlib + try/except + getattr
   **Logic Changes**: None (verified)
   EOF

Output:
- Branch: codemod/replace-labs-batch-1
- PR: Created with artifacts and validation output
- Artifacts: /tmp/codmod_batch1_artifacts.tgz
```

### Expected Output

```bash
# Branch creation and patch application
git checkout -B codemod/replace-labs-batch-1 origin/main
# Applying patches...
# [20/20 patches applied successfully]

git commit -m "chore(codemod): replace labs imports (batch 1)"
git push -u origin codemod/replace-labs-batch-1

# Ephemeral worktree validation
WT="/tmp/wt_batch1"
git worktree add "$WT" origin/codemod/replace-labs-batch-1
# Output:
# Preparing worktree (detached HEAD abc123)
# HEAD is now at abc123 chore(codemod): replace labs imports (batch 1)

pushd "$WT"
./scripts/run_lane_guard_worktree.sh
# Output:
# [lane-guard] Running import-linter...
# [lane-guard] ✅ PASS - No lane violations detected
# [lane-guard] Report: artifacts/reports/lane_guard_batch1.json

tar -czf /tmp/codmod_batch1_artifacts.tgz artifacts/reports
popd
git worktree remove "$WT" --force

# PR creation
gh pr create \
  --title "chore(codemod): replace labs imports (batch 1)" \
  --body "..." \
  --base main \
  --head codemod/replace-labs-batch-1

# Output:
# https://github.com/LukhasAI/Lukhas/pull/812
```

### Validation Commands

```bash
# 1. Verify branch exists and is ahead of main
git log origin/main..codemod/replace-labs-batch-1 --oneline
# Expected: 1 commit (chore(codemod): replace labs imports (batch 1))

# 2. Verify changed files count
git diff --name-only origin/main...codemod/replace-labs-batch-1 | wc -l
# Expected: 20

# 3. Verify artifacts created
tar -tzf /tmp/codmod_batch1_artifacts.tgz
# Expected: artifacts/reports/lane_guard_batch1.json

# 4. Verify PR created
gh pr view codemod/replace-labs-batch-1
# Expected: PR #812 with labels and artifacts
```

### Acceptance Criteria

- [ ] Branch `codemod/replace-labs-batch-1` created
- [ ] 20 patches applied successfully
- [ ] Commit message follows standard format
- [ ] Ephemeral worktree validation completed
- [ ] Lane-guard passes (no violations)
- [ ] Artifacts archived to /tmp/codmod_batch1_artifacts.tgz
- [ ] PR created with artifacts attached
- [ ] Labels applied: codemod, batch-1, T4, high-priority, security
- [ ] Reviewers assigned: @security_team, @core_team

---

## Task 04: Batch-2 through Batch-8 (Automation Script)

### Why
After batch-1 validation proves the workflow, we need to **automate batches 2-8** using the same pattern to process remaining patches efficiently.

### Codex Prompt (Copy/Paste)

```
Context: Batch-1 succeeded, ready to automate remaining batches
Task: Create automation script to process batches 2-8 with same validation workflow

Requirements:
1. Create scripts/automation/run_codmod_and_prs.sh:
   - Takes BATCH_SIZE (default 20), PATCH_DIR, BASE_BRANCH
   - Loops through all safe patches in batches
   - For each batch:
     * Create branch: codemod/replace-labs-batch-<N>
     * Apply 20 patches
     * Commit with standard message
     * Push branch
     * Create ephemeral worktree validation
     * Run lane-guard
     * Archive artifacts
     * Create PR with artifacts
     * Create GitHub Issue for batch tracking

2. Safety gates in automation:
   - Stop if any patch fails to apply
   - Stop if lane-guard fails on any batch
   - Require human approval before continuing to next batch
   - Never auto-merge any PRs

3. Batch priority order:
   - Batch 1: lukhas + core (highest priority) ✅ DONE
   - Batch 2-3: Remaining core + serve (high priority)
   - Batch 4-7: candidate (research, lower priority)
   - Batch 8: other (tools, docs, remaining)

4. Create GitHub Project board:
   - Project: "Codex Batch Codemod — labs Import Removal"
   - Columns: Pending, In Progress, Validated, Merged, Blocked
   - Add all batch issues to project

5. Run automation for batch-2 (supervised):
   BATCH_SIZE=20 BASE_BRANCH=origin/main \
   bash scripts/automation/run_codmod_and_prs.sh \
     --batch-num 2 \
     --patch-list /tmp/codmod_batches/batch2.list

Output:
- scripts/automation/run_codmod_and_prs.sh (automation script)
- GitHub Project: Codex Batch Codemod
- 7 PRs created (batch 2-8)
- 7 GitHub Issues created (one per batch)
```

### Automation Script Structure

The automation script `run_codmod_and_prs.sh` implements the following workflow:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

PATCH_DIR=${PATCH_DIR:-/tmp/codmod_patches}
BATCH_SIZE=${BATCH_SIZE:-20}
BASE_BRANCH=${BASE_BRANCH:-origin/main}
PR_TARGET=${PR_TARGET:-main}
GH_REPO=${GH_REPO:-$(git remote get-url origin | sed -E 's#.*[:/](.+/[^/]+)(\.git)?$#\1#')}

# Generate patches
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
  # Start new batch every BATCH_SIZE patches
  if (( i % BATCH_SIZE == 0 )); then
    BRANCH="codemod/replace-labs-batch-${batch}"
    git fetch origin
    git checkout -B "$BRANCH" "$BASE_BRANCH"
  fi

  # Apply patch
  git apply --index "$patch"
  i=$((i+1))

  # Commit and validate when batch full or last patch
  if (( i % BATCH_SIZE == 0 )) || [ "$i" -eq "$PATCH_COUNT" ]; then
    git commit -m "chore(codemod): replace labs imports (batch ${batch})" || true
    git push -u origin "$BRANCH"

    # Create PR
    gh pr create --repo "$GH_REPO" \
      --title "codemod: replace labs imports (batch ${batch})" \
      --body "Auto-generated batch ${batch}. Please run CI and lane-guard."

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

      # Attach artifacts to PR
      gh pr comment --repo "$GH_REPO" \
        --body "Lane-guard artifacts for batch ${batch} attached." \
        "$(gh pr list --repo "$GH_REPO" --state open --head "$BRANCH" --json number --jq '.[0].number')"
    popd
    git worktree remove "$WT" --force || true

    batch=$((batch+1))
  fi
done

echo "Done. Inspect PRs and artifacts. Do not merge without human review."
```

### Validation Commands

```bash
# 1. Verify automation script exists and is executable
test -x scripts/automation/run_codmod_and_prs.sh && echo "✅ Script ready"

# 2. Dry-run for batch-2 (supervised)
BATCH_SIZE=20 BASE_BRANCH=origin/main \
bash scripts/automation/run_codmod_and_prs.sh --dry-run

# 3. Check GitHub Project board
gh project list --owner LukhasAI
# Expected: "Codex Batch Codemod — labs Import Removal"

# 4. Verify batch-2 PR created
gh pr list --label batch-2
# Expected: PR #813
```

### Acceptance Criteria

- [ ] Automation script created and tested in dry-run mode
- [ ] Batch-2 PR created successfully with automation
- [ ] Ephemeral worktree validation passes for batch-2
- [ ] GitHub Project board created with all batch issues
- [ ] All batches 2-8 tracked in project board
- [ ] Human review checkpoint before each batch merge
- [ ] No auto-merge configured on any batch PRs

---

## Common Issues & Solutions

### Issue: Patch fails to apply with "does not match"

**Solution**: Patch may conflict with concurrent changes. Regenerate patches from latest main:
```bash
git checkout main
git pull origin main
python3 scripts/codemods/replace_labs_with_provider.py --outdir /tmp/codmod_patches_fresh
# Use fresh patches for next batch
```

### Issue: Lane-guard fails with transitive import violation

**Solution**: Identify leaf module causing violation and fix manually first:
```bash
# Parse lane-guard output to find violating import chain
grep -A 5 "Lane violation" artifacts/reports/lane_guard.json
# Fix the leaf module (usually a missed labs import)
# Re-run lane-guard in ephemeral worktree
```

### Issue: Conservative filter flags too many patches as unsafe

**Solution**: Adjust MAX_NON_IMPORT_DELETIONS threshold or review flagged patches manually:
```bash
# Inspect flagged patch
cat /tmp/codmod_patches/flagged_file.patch
# If safe, manually move to batch.safe/
mv /tmp/codmod_patches/flagged_file.patch /tmp/codmod_batches/batch.safe/
```

### Issue: Ephemeral worktree lane-guard times out

**Solution**: Increase timeout or run on machine with more resources:
```bash
# In run_lane_guard_worktree.sh, increase timeout
LANE_GUARD_TIMEOUT=600 ./scripts/run_lane_guard_worktree.sh
```

### Issue: PR artifacts too large for GitHub comment

**Solution**: Upload artifacts to S3/Azure Blob and link in PR comment:
```bash
# Upload artifacts
aws s3 cp /tmp/codmod_batch1_artifacts.tgz s3://lukhas-ci-artifacts/batch1/
# Comment with link
gh pr comment --body "Artifacts: s3://lukhas-ci-artifacts/batch1/codmod_batch1_artifacts.tgz"
```

---

## Codex-Specific Guidelines

### DO:
- ✅ Run codemod in dry-run mode first, inspect patches before applying
- ✅ Use conservative filter to identify safe patches only
- ✅ Validate each batch in ephemeral worktree before PR
- ✅ Create GitHub Issues for each batch with acceptance criteria
- ✅ Include lane-guard artifacts in every PR
- ✅ Request human review from Security + Core teams
- ✅ Stop automation if lane-guard fails on any batch
- ✅ Tag PRs with codemod, batch-N, T4, security labels

### DON'T:
- ❌ Auto-merge any batch PRs (human approval required)
- ❌ Apply patches that fail conservative filter without manual review
- ❌ Continue to next batch if previous batch lane-guard failed
- ❌ Skip ephemeral worktree validation for "small" batches
- ❌ Batch more than 20 files per PR (reviewability limit)
- ❌ Apply flagged patches without Security team approval
- ❌ Modify logic during codemod (import reshaping only)

---

## Integration with Other Agents

### With Claude Code
- Claude Code handles 10 high-priority files manually (surgical refactors)
- Codex handles remaining ~137 files via batch automation
- Claude Code reviews Codex PRs for quality/correctness

### With Gemini
- Gemini monitors coverage after each Codex batch merge
- Gemini runs SLSA attestation pipeline on changed modules
- Gemini alerts if coverage drops below 75% threshold

### With GitHub Copilot
- Copilot suggests improvements to automation scripts
- Copilot generates test cases for import-safety validation
- Codex reviews and tests Copilot suggestions before committing

---

## Success Metrics

Track these metrics to measure batch automation effectiveness:

### Codemod Coverage
- **Total files with labs imports**: 147
- **Files processed by Claude Code**: 10 (manual, high-priority)
- **Files processed by Codex**: 137 (batch automation)
- **Batches created**: 8 (20 files each, last batch 7 files)
- **Measurement**: Count of merged batch PRs

### Safety & Quality
- **Conservative filter pass rate**: >90% (safe patches / total patches)
- **Lane-guard pass rate**: 100% (all batches must pass)
- **Human review required**: 100% (no auto-merge)
- **Production incidents from codemods**: 0 (target)
- **Measurement**: Lane-guard reports, incident tracking

### Efficiency
- **Batch processing time**: <2 hours per batch (generation → PR)
- **Review time per batch**: <4 hours (Security + Core review)
- **Total time to process 137 files**: <4 weeks (2 batches/week)
- **Measurement**: GitHub PR timestamps, merge times

### Automation Reliability
- **Patch application success rate**: 100% (all patches apply cleanly)
- **Ephemeral worktree validation failures**: 0 (target)
- **GitHub Actions failures**: <5% (CI infrastructure issues only)
- **Measurement**: CI logs, automation script exit codes

---

## Reference Materials

### Codemod Resources
- libcst Documentation: https://libcst.readthedocs.io/
- AST Transformation Patterns: https://greentreesnakes.readthedocs.io/
- Conservative Refactoring: https://refactoring.com/

### Git Worktree Resources
- Git Worktree Guide: https://git-scm.com/docs/git-worktree
- Ephemeral Testing Patterns: https://github.com/git/git/tree/master/contrib/workdir

### GitHub Automation Resources
- GitHub CLI (gh): https://cli.github.com/manual/
- GitHub Projects API: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- GitHub Actions Artifacts: https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts

---

## Final Handoff Checklist

Before marking batch automation complete, ensure:

- [ ] All 8 batches have PRs created
- [ ] All batch PRs have ephemeral worktree validation artifacts attached
- [ ] Lane-guard passes on all 8 batches
- [ ] GitHub Project board shows status of all batches
- [ ] Security team reviewed at least batch-1 and batch-2
- [ ] Core team reviewed at least batch-1 and batch-2
- [ ] No auto-merge configured on any batch PR
- [ ] Documentation updated with batch automation runbook
- [ ] Conservative filter statistics recorded (safe vs flagged counts)
- [ ] Incident response plan documented for codemod rollback if needed
- [ ] Post-merge monitoring plan coordinated with Gemini (coverage, SLSA)
- [ ] Claude Code can review batch PRs for final quality check before merge

---

**End of Codex Task Pack**

Next: Human Security Review → Merge batch-1 → Continue with batches 2-8
