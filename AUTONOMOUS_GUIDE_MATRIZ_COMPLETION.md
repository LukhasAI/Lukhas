# Autonomous Guide: Complete MATRIZ Migration (Remaining 35 Imports)

**Goal:** Migrate remaining ~35 legacy `matriz` imports to canonical `MATRIZ` in non-critical code paths
**Priority:** Medium (Q1 2026)
**Estimated Time:** 2-3 hours
**Compatible With:** Claude Code, Codex, GitHub Copilot, Manual Execution

---

## 📋 Prerequisites

### Check Current Status
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout main && git pull origin main

# Verify smoke tests passing
make smoke

# Count remaining legacy imports
grep -R --exclude-dir={.git,artifacts,manifests,third_party,archive,dist,build,.pytest_cache,__pycache__} \
  -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" . | \
  grep -E "\.py:" | wc -l

# Expected: ~35 imports
```

### Verify Tools Available
```bash
python3 scripts/consolidation/rewrite_matriz_imports.py --help
make smoke  # Should pass 10/10
```

---

## 🎯 Phase 1: Identify Remaining Imports (5 minutes)

### Step 1.1: Generate Full Inventory
```bash
grep -R --exclude-dir={.git,artifacts,manifests,third_party,archive,dist,build,.pytest_cache,__pycache__} \
  -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" . | \
  grep -E "\.py:" > /tmp/matriz_remaining_inventory.txt

cat /tmp/matriz_remaining_inventory.txt
```

**Expected Output:** ~35 lines showing file:line:import

### Step 1.2: Group by Directory
```bash
cat /tmp/matriz_remaining_inventory.txt | \
  awk -F: '{print $1}' | \
  xargs dirname | \
  sort | uniq -c | sort -rn

# Expected groups:
# - tests/benchmarks/
# - lukhas_website/
# - tests/performance/
# - tests/e2e/
# - examples/
# - tools/
```

### Step 1.3: Prioritize Migration Order
**Priority Order:**
1. `tests/benchmarks/` - Performance validation (~8 imports)
2. `tests/performance/` - Load testing (~5 imports)
3. `tests/e2e/` - End-to-end tests (~4 imports)
4. `lukhas_website/` - Website code (~6 imports)
5. `examples/` - Example code (~5 imports)
6. `tools/` - Developer tools (~7 imports)

---

## 🚀 Phase 2: Execute Migrations by Group (30-45 minutes per group)

### For Each Group (Repeat Pattern)

#### Example: tests/benchmarks/

**Step 2.1: Create Branch**
```bash
git checkout main && git pull origin main
git checkout -b migration/matriz-benchmarks-$(date +%Y-%m-%d)
```

**Step 2.2: Dry Run**
```bash
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --dry-run \
  --verbose \
  --path tests/benchmarks \
  > /tmp/matriz_benchmarks_dryrun.txt

cat /tmp/matriz_benchmarks_dryrun.txt
# Review changes carefully
```

**Step 2.3: Validate Dry Run**
- ✅ Only imports changed (no other code)
- ✅ Import statements are syntactically correct
- ✅ No unexpected file modifications

**If validation fails:** STOP and investigate

**Step 2.4: Apply Migration**
```bash
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path tests/benchmarks \
  --verbose

# Verify changes
git diff
```

**Step 2.5: Run Validation**
```bash
# CRITICAL: Smoke tests must pass
make smoke
# Expected: 10/10 PASS

# Run affected benchmarks (if applicable)
pytest tests/benchmarks -v --tb=short || echo "Benchmarks may have other issues"

# Check module registry
python3 scripts/generate_meta_registry.py
```

**Step 2.6: Commit Changes**
```bash
# Count imports migrated
IMPORT_COUNT=$(git diff --cached | grep -E "^\+.*from MATRIZ\.|^\+.*import MATRIZ" | wc -l)

git add tests/benchmarks/
git commit -m "$(cat <<EOF
chore(imports): migrate matriz -> MATRIZ in tests/benchmarks (AST codemod)

Problem: tests/benchmarks/ still used legacy lowercase 'matriz' imports
Solution: Migrated ${IMPORT_COUNT} imports using AST-safe rewriter
Impact: Benchmarks now use canonical MATRIZ imports, maintaining test validity

- Files: $(git diff --cached --name-only | wc -l)
- Imports: ${IMPORT_COUNT}
- Validation: smoke tests 10/10 PASS

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Step 2.7: Push and Create PR**
```bash
git push origin migration/matriz-benchmarks-$(date +%Y-%m-%d)

gh pr create \
  --title "chore(imports): migrate matriz -> MATRIZ in tests/benchmarks" \
  --body "$(cat <<EOF
## Summary
- Migrated ${IMPORT_COUNT} legacy \\\`matriz\\\` imports to canonical \\\`MATRIZ\\\` in tests/benchmarks/
- Used AST-safe rewriter for guaranteed correctness
- Part of ongoing MATRIZ case standardization effort

## Testing
- Smoke tests: 10/10 PASS
- Module registry: regenerated successfully

## Progress
- Previous: 58% complete (49/84 imports)
- This PR: +${IMPORT_COUNT} imports
- After merge: $(echo "scale=0; (49 + ${IMPORT_COUNT}) * 100 / 84" | bc)% complete

## References
- Migration Guide: MATRIZ_MIGRATION_GUIDE.md
- Session Summary: MATRIZ_MIGRATION_SESSION_2025-10-26.md
EOF
)"
```

**Step 2.8: Return to Main**
```bash
git checkout main
```

---

## 📊 Phase 3: Repeat for Each Group

### Group 2: tests/performance/
```bash
git checkout -b migration/matriz-performance-$(date +%Y-%m-%d)
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path tests/performance
# ... follow same pattern as Phase 2 ...
```

### Group 3: tests/e2e/
```bash
git checkout -b migration/matriz-e2e-$(date +%Y-%m-%d)
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path tests/e2e
# ... follow same pattern as Phase 2 ...
```

### Group 4: lukhas_website/
```bash
git checkout -b migration/matriz-website-$(date +%Y-%m-%d)
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path lukhas_website
# ... follow same pattern as Phase 2 ...
```

### Group 5: examples/
```bash
git checkout -b migration/matriz-examples-$(date +%Y-%m-%d)
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path examples
# ... follow same pattern as Phase 2 ...
```

### Group 6: tools/
```bash
git checkout -b migration/matriz-tools-$(date +%Y-%m-%d)
python3 scripts/consolidation/rewrite_matriz_imports.py --dry-run --path tools
# ... follow same pattern as Phase 2 ...
```

---

## ✅ Phase 4: Final Verification (15 minutes)

### Step 4.1: Verify All Migrations Complete
```bash
git checkout main && git pull origin main

# Should return 0 or very low count (only artifacts/legacy)
grep -R --exclude-dir={.git,artifacts,manifests,third_party,archive,dist,build,.pytest_cache,__pycache__} \
  -nE "(^|[^\w])from\s+matriz\.|(^|[^\w])import\s+matriz\b" . | \
  grep -E "\.py:" | wc -l
```

**Expected:** 0-5 remaining (only in archived/legacy directories)

### Step 4.2: Run Full Validation
```bash
make smoke  # Must be 10/10 PASS
python3 scripts/generate_meta_registry.py
python3 scripts/consolidation/check_import_health.py --verbose
```

### Step 4.3: Update Documentation
```bash
# Update MATRIZ_MIGRATION_SESSION_2025-10-26.md
# - Mark all groups as complete
# - Update progress to 100%
# - Document final statistics

git add MATRIZ_MIGRATION_SESSION_2025-10-26.md
git commit -m "docs(matriz): mark migration as 100% complete"
git push origin main
```

---

## 🔄 Phase 5: Enable CI Enforcement (48 hours after completion)

### Step 5.1: Monitor Stability
Wait 48 hours after all PRs merged to ensure no issues.

### Step 5.2: Flip CI to Blocking Mode
```bash
# Edit .github/workflows/matriz-import-check.yml
# Change:
#   BLOCK_LEGACY: "0"
# To:
#   BLOCK_LEGACY: "1"

git checkout -b feature/matriz-ci-enforcement
# Edit file
git add .github/workflows/matriz-import-check.yml
git commit -m "ci(matriz): enable blocking mode for legacy import enforcement

All MATRIZ migrations complete (100%), enabling CI enforcement to prevent
regressions. Any new code with lowercase 'matriz' imports will now fail CI.

Compatibility shim remains active until Q2 2026."
git push origin feature/matriz-ci-enforcement

gh pr create --title "ci(matriz): enable CI enforcement" --body "..."
```

---

## 🎯 Success Criteria

### Must Pass
- ✅ All 6 migration groups completed
- ✅ 0 legacy imports in production/test code
- ✅ Smoke tests: 10/10 PASS
- ✅ No production incidents
- ✅ All PRs merged successfully

### Should Achieve
- ✅ 100% MATRIZ migration complete
- ✅ CI enforcement enabled
- ✅ Documentation updated
- ✅ Nightly audit showing 0 legacy imports

---

## ⚠️ Rollback Procedure (If Issues Arise)

### For Single Group
```bash
git checkout main
git revert <commit-sha>
git push origin main
```

### For Multiple Groups
```bash
# Disable CI enforcement immediately
git checkout -b hotfix/disable-matriz-enforcement
# Edit .github/workflows/matriz-import-check.yml
# Set BLOCK_LEGACY: "0"
git add .github/workflows/matriz-import-check.yml
git commit -m "hotfix(ci): disable MATRIZ enforcement due to issues"
git push origin hotfix/disable-matriz-enforcement
gh pr create --title "HOTFIX: Disable MATRIZ CI enforcement" --body "..."

# Investigate and fix issues before re-enabling
```

---

## 📋 Execution Checklist

```
Phase 1: Identify Remaining
[ ] Generate inventory (/tmp/matriz_remaining_inventory.txt)
[ ] Group by directory
[ ] Prioritize migration order

Phase 2-3: Execute Migrations (for each group)
[ ] tests/benchmarks/ (8 imports)
[ ] tests/performance/ (5 imports)
[ ] tests/e2e/ (4 imports)
[ ] lukhas_website/ (6 imports)
[ ] examples/ (5 imports)
[ ] tools/ (7 imports)

Phase 4: Final Verification
[ ] Verify 0 remaining imports
[ ] Smoke tests 10/10 PASS
[ ] Update documentation

Phase 5: Enable Enforcement
[ ] Wait 48 hours for stability
[ ] Flip BLOCK_LEGACY to "1"
[ ] Monitor for regressions
```

---

## 🎓 Lessons from Previous Migrations

### What Worked
1. AST-safe rewriter (zero manual edits)
2. Small, focused PRs (1 directory at a time)
3. Smoke test validation before commit
4. Clear commit messages with statistics

### What to Avoid
1. ❌ Manual search-and-replace
2. ❌ Large PRs with multiple directories
3. ❌ Skipping validation steps
4. ❌ Committing without smoke tests passing

---

## 📊 Expected Timeline

- **Phase 1:** 5 minutes
- **Phase 2-3:** 3-4 hours (6 groups × 30-45 min each)
- **Phase 4:** 15 minutes
- **Phase 5:** 2 days wait + 30 minutes

**Total:** ~1 week end-to-end (4 hours active work)

---

## 🤖 Autonomous Execution Notes

**For AI Agents (Claude Code, Codex, Copilot):**

1. **Follow phases sequentially** - Don't skip validation steps
2. **Stop on smoke test failure** - Immediate rollback required
3. **Create one PR per group** - Don't combine directories
4. **Report progress** - Update user after each phase
5. **Error handling** - Use rollback procedure if any step fails

**Success Signal:** When grep count reaches 0 and smoke tests pass 10/10

---

**Last Updated:** 2025-10-28
**Status:** Ready for Autonomous Execution
**Difficulty:** Medium
**Risk:** Low (non-critical code paths)
