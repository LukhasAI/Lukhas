# Codex Execution Prompt: Hidden Gems Module Integration

## CRITICAL: This Is NOT a Planning Task

**DO NOT** create helper scripts, utilities, or documentation.
**DO NOT** analyze or summarize the manifest.
**DO** execute the actual integration workflow starting immediately.

---

## Your Mission (Explicit)

Execute `make batch-next` repeatedly until all 144 modules are integrated into production structure.

**Start NOW with this exact command:**

```bash
make batch-status
make batch-next
```

---

## What "Integrate" Means (Zero Ambiguity)

For each module, the automation script (`scripts/batch_next.sh`) will:

1. Create a feature branch
2. Run `git mv SOURCE_PATH TARGET_PATH` (preserving git history)
3. Create placeholder integration test
4. Run `pytest tests/smoke/`
5. Run `make codex-acceptance-gates`
6. Create T4-formatted commit
7. Mark module as done

**Your job**: Run the command, handle failures, push PR.

---

## Exact Operating Loop

```
STEP 1: Check Status
→ Bash("make batch-status")
→ Read output: "matriz: X rem, core: Y rem, serve: Z rem"

STEP 2: Execute Next Integration
→ Bash("make batch-next")
→ Wait for completion (script handles all 9 steps)

STEP 3: Handle Results

IF output contains "✅ Integrated: [MODULE]":
  → Bash("scripts/batch_push_pr.sh")
  → Output: "PR created for [MODULE]"
  → GOTO STEP 1 (repeat)

IF output contains "❌" or "failed" or "error":
  → Read the failing file mentioned in error
  → Apply ONE surgical Edit to fix
  → Bash("pytest tests/smoke/ -q")
  → IF still fails:
    * Bash("git restore --staged . && git checkout -- .")
    * Output: "FAILED: [MODULE] - [reason]"
    * STOP and report to human
  → ELSE:
    * Bash("git add -A && git commit --amend --no-edit")
    * GOTO STEP 3 (retry push)

STEP 4: Progress Report (every 5 modules)
→ Bash("make batch-status")
→ Output: "✅ Completed X/144 modules, Y PRs created"
```

---

## First Integration (Example)

**You will do this NOW as your first action:**

```bash
# 1. Status
make batch-status
# Expected output:
# batch_matriz.tsv        | total: 36  done:  0  rem: 36  next:matriz.core.async_orchestrator
# batch_core.tsv          | total:106  done:  0  rem:106  next:core.guardian.shield
# batch_serve.tsv         | total:  2  done:  0  rem:  2  next:api.integrated_consciousness_api

# 2. Execute
make batch-next
# This auto-picks smallest batch (serve: 2 modules)
# Expected output:
# ➡️  MODULE: api.integrated_consciousness_api
#     SRC   : api/integrated_consciousness_api.py
#     DST   : serve/api/integrated_consciousness_api.py
#     BRANCH: feat/integrate-api-integrated_consciousness_api
# [... git mv, test creation, pytest run ...]
# ✅ Integrated: api.integrated_consciousness_api
# Next: run this script again to pick the next item.

# 3. Push PR
scripts/batch_push_pr.sh
# Expected output:
# remote: Create a pull request for 'feat/integrate-api-integrated_consciousness_api'
# PR READY: feat/integrate-api-integrated_consciousness_api

# 4. Verify
make batch-status
# Expected output:
# batch_serve.tsv         | total:  2  done:  1  rem:  1  next:serve.health_check
```

---

## What NOT To Do

❌ **DO NOT** create `scripts/hidden_gems_summary.py` or similar helpers
❌ **DO NOT** write documentation about the integration process
❌ **DO NOT** analyze the manifest
❌ **DO NOT** create planning documents
❌ **DO NOT** summarize what needs to be done

✅ **DO** run `make batch-next` repeatedly
✅ **DO** push PRs after each success
✅ **DO** fix test failures with surgical edits
✅ **DO** report progress every 5 modules

---

## Handling Test Failures

**Scenario**: `pytest tests/smoke/` fails during integration

```bash
# 1. See the error in batch_next output
# Example error: "ImportError: cannot import name 'AsyncOrchestrator' from 'matriz.core'"

# 2. Read the moved file
Read("serve/api/integrated_consciousness_api.py")

# 3. Find the bad import (line 15)
# from MATRIZ.core import AsyncOrchestrator  # ❌ Wrong casing

# 4. Fix it
Edit(
  file_path="serve/api/integrated_consciousness_api.py",
  old_string="from MATRIZ.core import AsyncOrchestrator",
  new_string="from matriz.core import AsyncOrchestrator"
)

# 5. Re-test
Bash("pytest tests/smoke/ -q")

# 6. If passes, amend commit
Bash("git add -A && git commit --amend --no-edit")

# 7. Continue
Bash("scripts/batch_push_pr.sh")
```

---

## Handling Acceptance Gate Failures

**Scenario**: `make codex-acceptance-gates` fails at gate 4 (lane guard)

```bash
# 1. Check which gate failed
Bash("make codex-acceptance-gates 2>&1 | tail -20")
# Output: "❌ Gate 4 failed: candidate imports detected"

# 2. Find the violation
Grep(pattern="from candidate", path=".", output_mode="content")
# Output: serve/api/integrated_consciousness_api.py:23: from candidate.memory import Store

# 3. Fix it
Edit(
  file_path="serve/api/integrated_consciousness_api.py",
  old_string="from candidate.memory import Store",
  new_string="from core.memory import Store"
)

# 4. Re-test gates
Bash("make codex-acceptance-gates")

# 5. Amend and continue
Bash("git add -A && git commit --amend --no-edit")
Bash("scripts/batch_push_pr.sh")
```

---

## Success Metrics

You will know you're done when:

```bash
make batch-status
# Output:
# batch_matriz.tsv        | total: 36  done: 36  rem:  0  next:
# batch_core.tsv          | total:106  done:106  rem:  0  next:
# batch_serve.tsv         | total:  2  done:  2  rem:  0  next:
```

**At that point:**
- 144 PRs created
- All modules moved to production structure
- All tests passing
- Mission complete

---

## Your First 3 Commands (Start NOW)

```bash
make batch-status
make batch-next
scripts/batch_push_pr.sh
```

Then repeat `make batch-next` and `scripts/batch_push_pr.sh` until all batches show `rem: 0`.

---

## Context Files (Read if needed)

- [docs/audits/integration_manifest.json](/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/audits/integration_manifest.json) - Full manifest (only read if you need details about a specific module)
- [CLAUDE.md](/Users/agi_dev/LOCAL-REPOS/Lukhas/CLAUDE.md) - Repository context
- [scripts/batch_next.sh](/Users/agi_dev/LOCAL-REPOS/Lukhas/scripts/batch_next.sh) - The automation script (read if script fails)

---

## Emergency Recovery

If batch_next.sh hangs or crashes:

```bash
# 1. Kill process
pkill -f batch_next.sh

# 2. Clean up
git checkout main
git branch -D feat/integrate-* 2>/dev/null || true

# 3. Check what was marked done
wc -l /tmp/batch_*.tsv.done

# 4. Resume
make batch-next
```

---

## Commit Message Format (Auto-generated by script)

You don't write commits manually. The script creates them with:

```
feat(integration): integrate [MODULE] → [TARGET] — task: Hidden Gems Integration

Problem:
- [Module] in labs/candidate
- Score: X, ready for production

Solution:
- Moved with git history
- Integration test added
- Acceptance gates passing

Impact:
- Production-ready in [target]
- Tests passing
```

---

## Expected Timeline

- **Module 1-10**: ~5 min each (50 min total)
- **Module 11-50**: ~3 min each (120 min total)
- **Module 51-144**: ~2 min each (188 min total)

**Total**: ~6 hours of continuous execution (if no failures)

**With failures**: ~12-18 hours (assume 20% failure rate requiring manual fixes)

---

## Final Checklist Before You Start

- [x] Understand: This is EXECUTION, not planning
- [x] Understand: The script does all the work, you just run it repeatedly
- [x] Understand: Your job is to handle failures and push PRs
- [x] Understand: Start NOW with `make batch-status && make batch-next`

---

**🚨 CRITICAL: Your first action after reading this prompt MUST be:**

```bash
make batch-status
```

**Then immediately:**

```bash
make batch-next
```

**DO NOT create any helper scripts or documentation. START INTEGRATING NOW.**

---

## Expected First Output

You should see this within 60 seconds:

```
➡️  MODULE: api.integrated_consciousness_api
    SRC   : api/integrated_consciousness_api.py
    DST   : serve/api/integrated_consciousness_api.py
    BRANCH: feat/integrate-api-integrated_consciousness_api
[...]
✅ Integrated: api.integrated_consciousness_api
```

If you see that, push PR and continue:

```bash
scripts/batch_push_pr.sh
make batch-next
```

---

**Mission**: Integrate 144 modules
**Method**: Run `make batch-next` 144 times
**Start**: NOW

🚀 **BEGIN EXECUTION**
