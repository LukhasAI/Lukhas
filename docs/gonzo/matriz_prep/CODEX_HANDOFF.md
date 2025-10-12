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
