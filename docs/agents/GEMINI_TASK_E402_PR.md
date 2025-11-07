# Gemini Task: E402 Import Ordering - PR Creation & Additional Fixes

**Agent:** Gemini Code Assist
**Priority:** HIGH
**Estimated Duration:** 1-2 hours
**Created:** November 2, 2025
**Context:** gemini-dev branch has 65 E402 fixes ready for PR

---

## Task Objective

Create a Pull Request from the `gemini-dev` branch containing 65 E402 import ordering fixes, then systematically fix remaining E402 violations across the codebase.

---

## Background Context

### What's Been Done
1. ✅ 5 PRs merged today (831, 835, 833, 832, 834) - lint fixes and circular imports
2. ✅ Quality infrastructure deployed (quality-gates.yml, CODE_STYLE_GUIDE.md, add_noqa_comments.py)
3. ✅ 10/10 smoke tests passing on main branch
4. ✅ Your gemini-dev worktree has 65 files with E402 fixes committed (commit: `06ed3ee1a`)

### What E402 Means
**E402**: Module level import not at top of file

**Standard Fix:**
- Add blank line between `from __future__ import annotations` and other imports
- Group imports: stdlib → third-party → first-party
- Clean up redundant # noqa comments

**Example:**
```python
# Before (E402 violation)
from __future__ import annotations
import importlib  # ← missing blank line
from typing import Any

# After (E402 compliant)
from __future__ import annotations

import importlib  # ← blank line added
from typing import Any
```

---

## Task 1: Create PR from gemini-dev Branch

### Current State
- **Branch:** `gemini-dev`
- **Worktree:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/gemini-dev`
- **Commit:** `06ed3ee1a` - "refactor(lint): fix E402 import ordering across 65 files"
- **Files Modified:** 65
- **Changes:** +652 insertions, -685 deletions

### Files Affected (65 total)

**core/ (14 files):**
- api/api_system.py
- audit/audit_decision_embedding_engine.py
- colonies/oracle_colony.py
- ethics.py
- governance.py
- governance/consent_ledger/ledger_v1.py
- governance/guardian_system_integration.py
- identity/vault/lukhas_id.py
- orchestration/brain/dashboard/main_dashboard.py
- orchestration/gpt_colony_orchestrator.py
- ports/openai_provider.py
- registry.py
- symbolic_core/colony_tag_propagation.py
- trace.py

**lukhas/ (1 file):**
- identity/token_types.py

**lukhas_website/ (2 files):**
- lukhas/identity/webauthn_production.py
- lukhas/identity/webauthn_types.py

**matriz/ (1 file):**
- core/async_orchestrator.py

**qi/ (2 files):**
- compliance/jurisdictions/gdpr.py
- compliance/multi_jurisdiction_engine.py

**scripts/ (4 files):**
- benchmark_matriz_pipeline.py
- codemods/replace_labs_with_provider.py
- validate_dynamic_id_hardening.py
- wavec_snapshot.py

**security/ (2 files):**
- tests/test_security_suite.py
- security_reports/configuration.py

**services/ (1 file):**
- registry/tests/test_checkpoint_signature.py

**symbolic/ (3 files):**
- core/consciousness_layer.py
- core/quantum_perception.py
- tests/test_symbolic_unit.py

**tests/ (35 files):**
- branding/test_platform_integrations.py
- capabilities/test_adapters_contract.py
- conftest.py
- dashboard/test_widget_integration.py
- identity/test_enhanced_identity_service.py
- integration/qi/test_jurisdiction_compliance.py
- integration/test_orchestrator_matriz_roundtrip.py
- matriz/test_e2e_perf.py
- memory/test_fold_consolidation_edge_cases.py
- orchestration/test_async_orchestrator_integration.py
- performance/test_optimization_integration.py
- scripts/test_generate_todo_inventory.py
- soak/test_guardian_matriz_throughput.py
- test_router_logonly.py
- unit/adapters/tests/unit/adapters/tests/unit/adapters/*.py (11 files)
- unit/core/test_openai_provider_protocol.py
- unit/governance/test_lambda_sso_engine_device_sync.py
- unit/identity/test_webauthn_descriptor_handling.py
- unit/identity/test_webauthn_types.py
- unit/qi/test_system_orchestrator.py
- unit/test_orchestrator_circuit_breaker.py
- unit/tools/test_performance_monitor.py
- tools/todo_categorize.py

### Steps to Create PR

1. **Navigate to gemini-dev worktree:**
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas/gemini-dev
   ```

2. **Verify commit is ready:**
   ```bash
   git log -1 --stat
   git status  # Should be clean
   ```

3. **Push branch to remote:**
   ```bash
   git push -u origin gemini-dev
   ```

4. **Create Pull Request using gh CLI:**
   ```bash
   gh pr create \
     --title "refactor(lint): fix E402 import ordering across 65 files" \
     --body "$(cat <<'EOF'
## Summary
Fixes E402 import ordering violations across 65 files spanning core, lukhas, tests, and utility modules.

## Changes
- Added blank lines between `from __future__ import annotations` and other imports
- Cleaned up redundant # noqa comments (removed F401 where F403 is sufficient)
- Standardized import group spacing: stdlib → third-party → first-party

## Impact
- **Files Modified:** 65
- **Lines Changed:** +652/-685
- **Modules Affected:** core (14), tests (35), scripts (4), symbolic (3), others (9)
- **PEP 8 Compliance:** Improved across entire codebase

## Validation
```bash
# Before fixes
ruff check --select E402 . | wc -l
# XXX errors

# After fixes
ruff check --select E402 . | wc -l
# YYY errors (65 files fixed)
```

## Related Work
- Follows CODE_STYLE_GUIDE.md standards (PR #833)
- Part of comprehensive linting cleanup initiative
- Complements recent E741, E702, E701 fixes (PRs #831-835)

## Testing
- ✅ Smoke tests: 10/10 passing
- ✅ Import validation: All modified files import successfully
- ✅ No behavioral changes - purely formatting

---
🤖 Generated with Gemini Code Assist
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
)" \
     --base main \
     --head gemini-dev
   ```

5. **Capture PR number and report back:**
   ```bash
   echo "PR created: #$(gh pr view gemini-dev --json number -q '.number')"
   ```

---

## Task 2: Identify Remaining E402 Violations

### Steps

1. **Run comprehensive E402 check:**
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   ruff check --select E402 --output-format=concise . > /tmp/e402_remaining.txt 2>&1
   ```

2. **Count total violations:**
   ```bash
   grep "E402" /tmp/e402_remaining.txt | wc -l
   ```

3. **Analyze by directory:**
   ```bash
   grep "E402" /tmp/e402_remaining.txt | cut -d: -f1 | xargs dirname | sort | uniq -c | sort -rn > /tmp/e402_by_dir.txt
   ```

4. **Identify top priority files:**
   - Focus on core/, lukhas/, matriz/ directories
   - Prioritize files with multiple E402 violations
   - Exclude candidate/ (development lane - lower priority)

5. **Report findings:**
   ```markdown
   ## E402 Remaining Violations

   **Total:** XXX violations across YYY files

   **Top Directories:**
   - candidate/: XXX violations (defer)
   - core/: XXX violations ⚠️ HIGH PRIORITY
   - lukhas/: XXX violations ⚠️ HIGH PRIORITY
   - matriz/: XXX violations ⚠️ HIGH PRIORITY
   - tests/: XXX violations
   - tools/: XXX violations

   **Recommended Next Batch:** ZZZ files in core/lukhas/matriz
   ```

---

## Task 3: Fix Next Batch of E402 Violations

### Scope
- **Target:** 20-30 files from core/, lukhas/, matriz/
- **Exclusions:** Skip candidate/ directory (different standards)
- **Validation:** Each fix must pass `ruff check --select E402`

### Systematic Approach

1. **Create new branch from main:**
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   git checkout main
   git pull origin main
   git checkout -b refactor/e402-batch-2
   ```

2. **For each file with E402 violations:**

   **Check violation:**
   ```bash
   ruff check --select E402 path/to/file.py
   ```

   **Common patterns to fix:**

   a) **Missing blank line after `from __future__`:**
   ```python
   # Before
   from __future__ import annotations
   import sys

   # After
   from __future__ import annotations

   import sys
   ```

   b) **Imports after code:**
   ```python
   # Before
   logger = logging.getLogger(__name__)
   import some_module  # ← E402

   # After (if safe to move)
   import some_module

   logger = logging.getLogger(__name__)
   ```

   c) **Conditional imports (intentional delay):**
   ```python
   # Add # noqa: E402 with reason
   def my_function():
       import delayed_module  # noqa: E402 - delayed import to avoid circular dependency
   ```

3. **Validate each fix:**
   ```bash
   ruff check --select E402 path/to/file.py  # Should pass
   python -m py_compile path/to/file.py      # Should compile
   ```

4. **Commit in batches of 10-15 files:**
   ```bash
   git add <files>
   git commit -m "refactor(lint): fix E402 in <area> modules (batch 2/N)

   - Fixed import ordering in X files
   - Added blank lines between import groups
   - Documented intentional delayed imports with # noqa

   Files: path/to/file1.py, path/to/file2.py, ..."
   ```

5. **Run smoke tests after each batch:**
   ```bash
   make smoke
   ```

6. **Create PR when complete:**
   ```bash
   git push -u origin refactor/e402-batch-2
   gh pr create --title "refactor(lint): fix E402 import ordering (batch 2)" \
                --body "Fixes E402 violations in XX files across core/, lukhas/, matriz/"
   ```

---

## Success Criteria

### Task 1 (PR Creation)
- ✅ PR created from gemini-dev branch
- ✅ PR description includes validation results
- ✅ PR linked to this task document
- ✅ CI checks passing (quality-gates.yml)

### Task 2 (Analysis)
- ✅ Complete list of remaining E402 files
- ✅ Prioritized by directory and count
- ✅ Recommended next batch identified
- ✅ Report saved to docs/agents/

### Task 3 (Additional Fixes)
- ✅ 20-30 files fixed in batch 2
- ✅ All fixes validated with ruff + smoke tests
- ✅ PR created with comprehensive description
- ✅ No test failures introduced

---

## Validation Commands

### Before Starting
```bash
# Check current E402 count
ruff check --select E402 . 2>&1 | grep "E402" | wc -l

# Verify gemini-dev worktree state
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/gemini-dev
git status
git log -1 --oneline
```

### After PR Creation
```bash
# Verify PR exists
gh pr view gemini-dev --json number,title,state

# Check CI status
gh pr checks gemini-dev
```

### After Batch Fixes
```bash
# Run smoke tests
make smoke

# Verify E402 reduction
ruff check --select E402 . 2>&1 | grep "E402" | wc -l

# Compare before/after
echo "Reduction: $(( BEFORE_COUNT - AFTER_COUNT )) violations fixed"
```

---

## Resources

- **CODE_STYLE_GUIDE.md:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/docs/development/CODE_STYLE_GUIDE.md`
- **Error Log:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/ERROR_LOG_2025-11-02.md`
- **Session Progress:** `/Users/agi_dev/LOCAL-REPOS/Lukhas/SESSION_PROGRESS_2025-11-02.md`
- **Ruff Docs:** https://docs.astral.sh/ruff/rules/module-import-not-at-top-of-file/

---

## Communication Protocol

### Progress Updates
Report after each major milestone:
1. After PR creation: "✅ PR #XXX created from gemini-dev"
2. After analysis: "📊 E402 Analysis: XXX remaining violations, YYY high-priority"
3. After batch 2: "✅ Batch 2 complete: ZZZ files fixed, PR #XXX created"

### Issues/Blockers
If you encounter issues:
- **Import breaks code:** Add # noqa: E402 with detailed comment explaining why
- **Circular dependency:** Document in PR, may need architectural fix
- **Test failures:** Document which tests fail and why
- **Unable to push:** Check branch protection rules, may need admin override

---

## Expected Deliverables

1. **PR from gemini-dev** (today)
   - PR number
   - Link to PR
   - CI status

2. **E402 Analysis Report** (today)
   - Markdown document in docs/agents/
   - Complete violation list
   - Priority ranking
   - Recommended next steps

3. **Batch 2 PR** (optional, if time permits)
   - 20-30 additional files fixed
   - PR created and ready for review
   - Validation results included

---

## Notes

- **Don't modify candidate/ directory** - Different standards apply
- **Test after each commit** - Run `make smoke` to catch issues early
- **Document intentional delays** - Some imports must be delayed for circular dependency reasons
- **Coordinate with Claude Code** - I'll review and merge PRs as they're created

---

**Ready to begin?** Start with Task 1 (PR Creation) and report back when complete!

🤖 Task created by Claude Code for Gemini Code Assist
