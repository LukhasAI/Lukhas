# CODEX TODO Cleanup - Handoff Instructions

## Mission: Clean the TODO Noise Before MATRIZ Promotion

**Agent**: Codex (mechanical cleanup specialist)
**Phase**: 1 (Cleanup) - preparing for MATRIZ R2 completion
**Context**: See [TODO_brief.md](./TODO_brief.md) for full plan

---

## ⚠️ CRITICAL: The 2104 "TODOs" Are NOT All Real

The harvest script found **2,104 items** but **~90% are FAKE/NOISE**:

### Real TODOs (~200-250):
- Production stub modules (10 in `lukhas/`)
- MATRIZ-R2 integration points (~20 with `TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ`)
- Specialist delegation markers (~15 with `TODO[QUANTUM-BIO:specialist]`, etc.)
- Legitimate implementation TODOs (~5-10)

### Fake TODOs (~1,850-1,900):
1. **Auto-generated linter noise**: `# noqa: invalid-syntax  # TODO: Expected...`
2. **F821 undefined name annotations**: `# noqa: F821  # TODO: VariableName`
3. **Legacy REALITY_TODO references**
4. **TODO utility modules** (`lukhas/tools/todo/__init__.py` - not a task!)

---

## Your Tasks (Codex)

### ✅ Phase 1: Mechanical Cleanup (Safe, Fast - 1-2 hours)

**DO THIS FIRST**:

```bash
# 1. Remove auto-generated syntax error "TODOs" (these add no value)
grep -rl "# noqa: invalid-syntax  # TODO:" candidate/ | \
  xargs sed -i '' 's/# noqa: invalid-syntax  # TODO:.*$/# noqa: invalid-syntax/'

# 2. Remove F821 undefined name "TODOs" (these are just error markers)
grep -rl "# noqa: F821  # TODO:" candidate/ | \
  xargs sed -i '' 's/# noqa: F821  # TODO:.*$/# noqa: F821/'

# 3. Verify reduction
python3 scripts/harvest_todos.py --roots lukhas candidate --out docs/audits/todos_clean.csv
wc -l docs/audits/todos_clean.csv  # Should be ~200-250 now
```

**Expected Result**: Reduce from 2,104 → ~250 real TODOs

---

### 🔍 Phase 2: Categorize Real TODOs (30 min)

Run the harvest again and review `docs/audits/todos_clean.csv`:

```bash
# Check what's left
head -50 docs/audits/todos_clean.csv

# Count by category
cut -d',' -f3 docs/audits/todos_clean.csv | sort | uniq -c
# Expected:
#   ~10 general (production stubs)
#   ~15 specialist (delegation markers)
#   ~20 general (MATRIZ-R2 integration)
#   ~5-10 fixme (actual bugs/issues)
```

**Decision Tree**:
- **Production stubs** (`lukhas/*/TODO: Implement or remove`) → Flag for review, don't auto-remove
- **Specialist markers** (`TODO[AREA:specialist]`) → Keep, these are delegation points
- **MATRIZ-R2** (`TODO[T4-UNUSED-IMPORT]: kept pending MATRIZ`) → Keep, waiting for R2
- **Legacy REALITY_TODO** → Safe to remove (old tracking system)

---

### 🧹 Phase 3: Safe Removals Only (30 min)

**ONLY remove these**:

```bash
# Remove legacy REALITY_TODO references
grep -rl "REALITY_TODO" candidate/ | \
  xargs sed -i '' 's/.*REALITY_TODO.*//g'

# Clean up empty comment lines created by removals
find candidate/ -name "*.py" -type f -exec sed -i '' '/^[[:space:]]*#[[:space:]]*$/d' {} \;
```

**DO NOT REMOVE**:
- ✅ Production stubs (needs human review)
- ✅ Specialist markers (intentional delegation)
- ✅ MATRIZ-R2 TODOs (awaiting integration)
- ✅ Legitimate implementation TODOs

---

## 📊 Success Metrics

**Before (Raw)**:
- 2,104 "TODOs" harvested
- ~90% noise

**After Phase 1**:
- ~250 real TODOs
- All noise removed

**After Phase 3**:
- ~240 actionable TODOs
- Clear categorization in CSV

---

## 🎯 Deliverables

When done, provide:

1. **Updated CSV**: `docs/audits/todos_clean.csv` (~240 real items)
2. **Summary Report**: How many removed per category
3. **Git commit**: Using T4 format:
   ```
   chore(cleanup): remove 1,850+ fake TODO/FIXME noise from candidate lane

   Problem:
   - Auto-generated linter comments created ~1,850 fake "TODOs"
   - Made it impossible to track real technical debt
   - Harvest script found 2,104 items (90% noise)

   Solution:
   - Remove syntax error TODO scaffolds (F821, invalid-syntax)
   - Remove legacy REALITY_TODO references
   - Keep real TODOs: stubs (10), specialists (15), MATRIZ-R2 (20)

   Impact:
   - Real TODOs: 2,104 → 240 (88% noise reduction)
   - Production lane: Ready for MATRIZ promotion
   - Clean audit trail for issue tracker migration
   ```

---

## ⚠️ What NOT to Do

**DON'T**:
- ❌ Remove production stub TODOs (need human review first)
- ❌ Remove specialist delegation markers (by design)
- ❌ Remove MATRIZ-R2 integration TODOs (awaiting completion)
- ❌ Touch files outside `candidate/` lane (production code frozen)
- ❌ Create any new TODOs or refactor code
- ❌ Run tests or modify functionality

**DO**:
- ✅ Only remove proven noise (syntax errors, F821 markers, legacy refs)
- ✅ Verify counts at each step
- ✅ Commit with clear before/after metrics
- ✅ Flag anything uncertain for Claude Code review

---

## 🤝 Handoff Back to Claude Code

After your cleanup, Claude Code will:
1. Review the clean CSV
2. Audit the 10 production stubs (implement or remove)
3. Complete MATRIZ-R2 integration (20 TODOs)
4. Generate GitHub issues for specialist TODOs
5. Final commit and MATRIZ promotion

---

## Tools Provided

```bash
# Harvest TODOs
make todos

# Generate issue script (after cleanup)
make todos-issues

# Check what was removed
git diff --stat candidate/
```

---

**Start Time**: 2025-10-12
**Expected Duration**: 2-3 hours
**Questions**: Tag @claude-code in commit message

---

## Quick Start Commands

```bash
# 1. Baseline check
python3 scripts/harvest_todos.py --roots lukhas candidate --out /tmp/before.csv
wc -l /tmp/before.csv  # Should show ~2,104

# 2. Run cleanup (Phase 1)
grep -rl "# noqa: invalid-syntax  # TODO:" candidate/ | xargs sed -i '' 's/# noqa: invalid-syntax  # TODO:.*$/# noqa: invalid-syntax/'
grep -rl "# noqa: F821  # TODO:" candidate/ | xargs sed -i '' 's/# noqa: F821  # TODO:.*$/# noqa: F821/'

# 3. Verify reduction
python3 scripts/harvest_todos.py --roots lukhas candidate --out docs/audits/todos_clean.csv
wc -l docs/audits/todos_clean.csv  # Should show ~250

# 4. Remove legacy (Phase 3)
grep -rl "REALITY_TODO" candidate/ | xargs sed -i '' 's/.*REALITY_TODO.*//g'
find candidate/ -name "*.py" -type f -exec sed -i '' '/^[[:space:]]*#[[:space:]]*$/d' {} \;

# 5. Final count
python3 scripts/harvest_todos.py --roots lukhas candidate --out docs/audits/todos_final.csv
wc -l docs/audits/todos_final.csv  # Should show ~240

# 6. Commit
git add -A
git commit -m "chore(cleanup): remove 1,850+ fake TODO/FIXME noise from candidate lane"
```

**Ready to execute! Good luck, Codex! 🚀**

---

## 🆕 Phase 2: Legacy Import Codemod (LibCST - 2-3 hours)

**AFTER Phase 1 is complete**, execute the import codemod to migrate:
- `candidate.*` → `labs.*`
- `tools.*` → `lukhas.tools.*`
- `governance.*` → `lukhas.governance.*`
- `memory.*` → `lukhas.memory.*`
- `lucas.*` → `lukhas.*`

### Stage A: Preview (Dry-Run)

```bash
# 1. Generate preview of all import rewrites
make codemod-dry

# 2. Review the preview
wc -l docs/audits/codemod_preview.csv
head -30 docs/audits/codemod_preview.csv

# 3. Verify tests still collect (thanks to compat layer)
pytest --collect-only -q
```

**Expected**: CSV shows all proposed `from → to` import rewrites.

---

### Stage B: Apply in Batches (Safest Approach)

**Apply by subtree** to minimize risk:

```bash
# Batch 1: tests/ (highest signal, easiest to verify)
python3 scripts/codemod_imports.py --apply --roots tests
pytest --collect-only -q  # Should pass
git add tests/
git commit -m "refactor(imports): migrate tests/ from legacy to canonical imports (LibCST)"

# Batch 2: lukhas/ (production lane)
python3 scripts/codemod_imports.py --apply --roots lukhas
make check-legacy-imports  # Verify no legacy imports remain
pytest tests/smoke/ -v     # Smoke tests should pass
git add lukhas/
git commit -m "refactor(imports): migrate lukhas/ production lane to canonical imports"

# Batch 3: labs/ (formerly candidate/)
python3 scripts/codemod_imports.py --apply --roots labs
pytest --collect-only -q
git add labs/
git commit -m "refactor(imports): migrate labs/ (candidate) to canonical imports"

# Batch 4: Remaining (core, MATRIZ, packages, tools)
python3 scripts/codemod_imports.py --apply --roots core MATRIZ packages tools
make check-legacy-imports
pytest tests/smoke/ -v
git add -A
git commit -m "refactor(imports): complete import migration for core, MATRIZ, packages, tools"
```

---

### Stage C: Verification

After all batches are applied:

```bash
# 1. Check no legacy imports remain outside allowlist
make check-legacy-imports  # Should exit 0 ✅

# 2. Verify test collection
pytest --collect-only -q   # Should succeed

# 3. Run smoke tests
make smoke-matriz          # Should pass 15/15

# 4. Check import health
make lane-guard            # Should pass

# 5. Generate final codemod report
make codemod-dry
wc -l docs/audits/codemod_preview.csv  # Should show 0 or near-0 changes
```

---

### Stage D: PR Creation

**Create a PR** (don't push directly to main):

```bash
# If you applied in batches (multiple commits), create PR with all commits
gh pr create \
  --title "refactor(imports): migrate legacy imports to canonical lukhas/* paths" \
  --body "$(cat <<'BODY'
## Summary
Migrates all legacy import paths to canonical `lukhas.*` namespaces using LibCST codemod.

## Migrations Applied
- `candidate.*` → `labs.*`
- `tools.*` → `lukhas.tools.*`
- `governance.*` → `lukhas.governance.*`
- `memory.*` → `lukhas.memory.*`
- `lucas.*|Lucas.*|LUCAS.*` → `lukhas.*`

## Safety
- Applied in batches (tests → lukhas → labs → core/MATRIZ/packages/tools)
- Verified test collection after each batch
- Smoke tests passing (15/15)
- Import boundary checks passing
- Compat layer remains for transition period

## Verification
✅ `make check-legacy-imports` passes
✅ `pytest --collect-only -q` succeeds
✅ `make smoke-matriz` passes (15/15)
✅ `make lane-guard` passes

## Metrics
- Files changed: ~XXX (see commit history)
- Import rewrites: ~XXX (see docs/audits/codemod_preview.csv)
- Test collection: 0 errors
- Smoke tests: 100% pass rate

## Follow-up
- Monitor compat layer alias hits in CI
- Remove compat layer when hits reach 0
- Add pre-commit hook to prevent new legacy imports

🤖 Generated with ChatGPT CODEX
BODY
)"
```

**Alternative** (if you squashed to single commit):

```bash
git add -A
git commit -m "refactor(imports): migrate all legacy imports to canonical lukhas/* paths

Problem:
- Legacy import roots (candidate, tools, governance, etc.) scattered across codebase
- Multiple import paths for same modules causing confusion
- Import boundary enforcement difficult with mixed namespaces

Solution:
- LibCST codemod to systematically rewrite imports
- candidate.* → labs.*
- tools.* → lukhas.tools.*
- governance.* → lukhas.governance.*
- memory.* → lukhas.memory.*
- lucas.* → lukhas.*

Impact:
- All imports now use canonical lukhas.* namespace
- Import boundaries enforceable via configs/legacy_imports.yml
- Compat layer provides safe transition period
- Pre-commit hook prevents new legacy imports

Safety:
- Applied in batches with verification between each
- All tests collect successfully
- Smoke tests: 15/15 passing
- Lane guard checks passing

Metrics:
- Files changed: ~XXX
- Import rewrites: ~XXX
- Test collection: 0 errors

🤖 Generated with ChatGPT CODEX
"

gh pr create -f
```

---

## 🛠️ Tools Provided

### Config:
- `configs/legacy_imports.yml` - Mapping and allowlist

### Scripts:
- `scripts/codemod_imports.py` - LibCST import rewriter
- `scripts/check_legacy_imports.py` - CI checker (blocks legacy imports)

### Make Targets:
```bash
make codemod-dry             # Preview import rewrites (safe)
make codemod-apply           # Apply all rewrites (DESTRUCTIVE)
make check-legacy-imports    # Verify no legacy imports (CI blocker)
```

---

## ⚠️ Important Notes

1. **Phase 1 must complete first** - TODO cleanup before import migration
2. **Batch application is safest** - Apply by subtree, not all at once
3. **Verify after each batch** - Run tests and checks between batches
4. **Don't push to main** - Use PR workflow for review
5. **Compat layer stays** - Will be removed later when alias hits = 0

---

## Success Criteria (Phase 2)

**Phase 2 Complete When**:
✅ `make check-legacy-imports` passes (0 violations)
✅ All tests collect successfully
✅ Smoke tests: 15/15 passing (100%)
✅ PR created with clear before/after metrics
✅ Committed with T4 format (Problem/Solution/Impact)

---

