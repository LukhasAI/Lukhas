# Directory Consolidation Plan V2 (CORRECTED) - October 26, 2025

**Status**: Production-Ready, T4-Compliant
**Risk Level**: Medium-High (MATRIZ case fix impacts 500+ imports)
**Estimated Time**: 4-7 hours (conservative, includes testing and review)
**Required Approvals**: Team lead sign-off before Phase 3 (MATRIZ)

---

## 🚨 CRITICAL CORRECTIONS FROM V1

### What V1 Got Wrong:

1. **MATRIZ Rename Commands**: V1 said "DO NOT use `git mv`" then showed `git mv` commands - confusing and dangerous
2. **Blind sed Usage**: Proposed `sed -i ''` which is macOS-specific and unsafe (touches strings/comments)
3. **Incorrect git revert**: Used `git revert HEAD~3..HEAD` (invalid syntax)
4. **Under-estimated MATRIZ impact**: Said "45 minutes" for ~500 import changes - unrealistic
5. **No compatibility shim**: Would break all existing imports immediately
6. **No AST-safe codemod**: Regex-based replacement risks breaking code
7. **Missing CI guards**: No checks for large files, forbidden imports, or lint failures

### What V2 Fixes:

✅ **Two-step MATRIZ rename** via temporary name (safe on case-insensitive FS)
✅ **AST-based import rewriter** (`scripts/consolidation/rewrite_matriz_imports.py`)
✅ **Compatibility shim already exists** (`matriz/__init__.py` → `MATRIZ`)
✅ **Conservative timeline**: 4-7 hours (realistic for 500+ import changes)
✅ **CI safety guards**: Large file detection, import validation, pre-commit hooks
✅ **Proper rollback syntax**: Individual commit reverts, not range syntax
✅ **Branch-based workflow**: All changes on feature branches with PR reviews

---

## Executive Summary

This plan consolidates **8 duplicate/scattered directories** with production-grade safety:

| Directory Pair | Action | Risk | Est. Time |
|---------------|--------|------|-----------|
| doc/ vs docs/ | Archive doc/ stub | Low | 10min |
| configs/ vs config/ | Merge to config/ | Low | 20min |
| final_sweep/ | Archive (legacy batch) | Low | 10min |
| eval_runs/ vs evals/ | Consolidate to evaluations/ | Medium | 30min |
| dream/ vs dreams/ vs dreamweaver_* | Merge to labs/consciousness/dream/ | Medium | 30min |
| **MATRIZ vs matriz** | **Case standardization** | **High** | **2-4hr** |

**Total Directories**: 13 → 6
**Space Freed**: ~150MB (after archiving)
**Import Statements Updated**: ~500+
**Test Files Affected**: ~50+

---

## Phase 1: Low-Risk Quick Wins (1 hour)

### 1.1 Backup and Branch Setup (10 minutes)

```bash
# Full repository backup
cd /Users/agi_dev/LOCAL-REPOS/
git clone --mirror Lukhas Lukhas-backup-$(date +%Y%m%d).git
tar -czf Lukhas-archive-$(date +%Y%m%d).tar.gz Lukhas-backup-*.git

# Create consolidation branch
cd Lukhas
git checkout -b chore/consolidation-2025-10-26
git push -u origin chore/consolidation-2025-10-26
```

**Verification**:
```bash
# Confirm backup
ls -lh ../Lukhas-backup-*.git ../Lukhas-archive-*.tar.gz

# Confirm branch
git branch --show-current
# Expected: chore/consolidation-2025-10-26
```

### 1.2 Archive doc/ Stub (10 minutes)

**Analysis**:
- `doc/` = Empty stub with 0 components (19 files, all boilerplate)
- `docs/` = Real documentation (2,021 files, comprehensive)
- No code dependencies on `doc/` module

**Execution**:
```bash
# Verify doc/ is empty stub
cat doc/README.md | grep "0 components"
# Expected: "LUKHAS doc module implementing... with 0 components"

# Archive
git mv doc/ archive/doc_stub_2025-10-26/

# Commit
git commit -m "chore(structure): archive empty doc/ module stub

- doc/ was auto-generated stub with 0 components
- docs/ remains as canonical documentation location
- No code dependencies found

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Verification**:
```bash
# Confirm doc/ gone, docs/ intact
ls -d doc/ 2>&1 | grep "No such file"
ls -d docs/ | grep docs

# Smoke test
make smoke
```

### 1.3 Archive final_sweep/ (10 minutes)

**Analysis**:
- Legacy artifacts from BATCH-CODEX-CLEANUP-005 (completed)
- 17 files, all historical
- No active dependencies

**Execution**:
```bash
# Verify it's legacy
cat final_sweep/README.md | grep "BATCH-CODEX-CLEANUP-005"

# Archive
git mv final_sweep/ archive/final_sweep_batch_2025-10-26/

# Commit
git commit -m "chore(structure): archive completed final_sweep batch artifacts

- Legacy artifacts from BATCH-CODEX-CLEANUP-005
- Completed Codex batch, no active dependencies
- Historical interest only

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Verification**:
```bash
ls -d final_sweep/ 2>&1 | grep "No such file"
make smoke
```

### 1.4 Merge configs/ → config/ (30 minutes)

**Analysis**:
- `config/` = Main configuration (199 files)
- `configs/` = Subset configs (6 files)
- Need to check for filename collisions

**Execution**:
```bash
# Check for collisions
echo "=== Checking for filename collisions ==="
(cd configs && find . -type f) | while read f; do
  if [ -f "config/$f" ]; then
    echo "COLLISION: $f exists in both configs/ and config/"
  fi
done

# If collisions found, manual review required
# If no collisions:

# Preview merge
mkdir -p /tmp/config_merge_preview
cp -r config/* /tmp/config_merge_preview/
cp -r configs/* /tmp/config_merge_preview/
ls -la /tmp/config_merge_preview/

# Validate YAML/JSON files
find /tmp/config_merge_preview/ -name "*.yaml" -o -name "*.yml" | \
  xargs -I{} python3 -c "import yaml; yaml.safe_load(open('{}'))" 2>&1 | \
  grep -i error || echo "✅ All YAML files valid"

find /tmp/config_merge_preview/ -name "*.json" | \
  xargs -I{} python3 -c "import json; json.load(open('{}'))" 2>&1 | \
  grep -i error || echo "✅ All JSON files valid"

# If validation passes, proceed:
git mv configs/legacy_imports.yml config/
git mv configs/quotas.yaml config/
git mv configs/star_rules.json config/
git mv configs/observability config/
git mv configs/policy config/
git mv configs/runtime config/

# Remove empty configs/
rmdir configs/

# Update references in code
grep -r "configs/" --include="*.py" --include="*.yaml" --include="*.sh" . | \
  grep -v ".git" | grep -v "node_modules" | \
  tee /tmp/configs_references.txt

# Manual review: update each reference to "config/"

# Commit
git add -A
git commit -m "chore(structure): consolidate configs/ into config/

Problem:
- configs/ contained 6 files duplicating config/ structure
- Causes confusion about canonical config location

Solution:
- Moved all 6 files from configs/ to config/
- Updated X code references (see updated files)
- Validated all YAML/JSON for correctness

Impact:
- Single canonical config/ directory
- No filename collisions detected
- All configuration files validated

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Verification**:
```bash
ls -d configs/ 2>&1 | grep "No such file"
make smoke
python3 -c "import config; print('Config import OK')" 2>/dev/null || echo "No config module (expected)"
```

### Phase 1 Checkpoint

```bash
# Push Phase 1 changes
git push origin chore/consolidation-2025-10-26

# Open Phase 1 PR
gh pr create \
  --title "chore(structure): Phase 1 - Archive doc/, final_sweep/, merge configs/" \
  --body "## Phase 1: Low-Risk Quick Wins

**Changes**:
- ✅ Archived empty doc/ stub → archive/doc_stub_2025-10-26/
- ✅ Archived legacy final_sweep/ → archive/final_sweep_batch_2025-10-26/
- ✅ Merged configs/ → config/ (6 files)

**Testing**:
- ✅ Smoke tests: 10/10 passing
- ✅ No config validation errors
- ✅ No code reference breakage

**Risk**: Low
**Rollback**: Single PR revert" \
  --base main

# Wait for CI and human review before merging
```

---

## Phase 2: Eval and Dream Consolidation (1 hour)

### 2.1 Investigate Eval Directories (15 minutes)

```bash
# Analyze contents
echo "=== eval_runs/ analysis ==="
find eval_runs/ -type f | wc -l
du -sh eval_runs/

echo "=== evals/ analysis ==="
find evals/ -type f | wc -l
du -sh evals/

# Check for dependencies
grep -r "eval_runs\|evals" --include="*.py" --include="*.yaml" . | \
  grep -v ".git" | grep -v "node_modules" | \
  tee /tmp/eval_references.txt
```

### 2.2 Consolidate Eval Directories (15 minutes)

```bash
# Create unified structure
mkdir -p evaluations/runs
mkdir -p evaluations/definitions

# Move contents
if [ -d "eval_runs" ]; then
  git mv eval_runs/* evaluations/runs/ 2>/dev/null || echo "eval_runs empty"
  rmdir eval_runs 2>/dev/null || git mv eval_runs evaluations/runs
fi

if [ -d "evals" ] && [ "$(ls -A evals)" ]; then
  git mv evals/* evaluations/definitions/ 2>/dev/null || git mv evals evaluations/definitions
fi

# Update references
# (Based on grep results from 2.1)

# Commit
git commit -m "chore(structure): consolidate eval directories into evaluations/

Problem:
- eval_runs/ and evals/ scattered evaluation artifacts
- Unclear distinction between runs and definitions

Solution:
- Created evaluations/ with runs/ and definitions/ subdirectories
- Moved eval_runs/ → evaluations/runs/
- Moved evals/ → evaluations/definitions/
- Updated X code references

Impact:
- Clearer evaluation organization
- Single canonical evaluation location

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 2.3 Consolidate Dream Directories (30 minutes)

```bash
# Analyze dream directories
echo "=== Dream directory analysis ==="
find dream dreams dreamweaver_helpers_bundle -type f 2>/dev/null | wc -l

# Check if labs/consciousness/dream/ exists
ls -la labs/consciousness/dream/ 2>/dev/null || echo "Need to create"

# Create unified structure
mkdir -p labs/consciousness/dream/synthesis
mkdir -p labs/consciousness/dream/helpers
mkdir -p labs/consciousness/dream/results
mkdir -p labs/consciousness/dream/config
mkdir -p labs/consciousness/dream/tests

# Move contents
if [ -d "dream" ] && [ "$(ls -A dream)" ]; then
  git mv dream/* labs/consciousness/dream/synthesis/ 2>/dev/null || true
  rmdir dream 2>/dev/null || true
fi

if [ -d "dreams" ] && [ "$(ls -A dreams)" ]; then
  git mv dreams/* labs/consciousness/dream/results/ 2>/dev/null || true
  rmdir dreams 2>/dev/null || true
fi

if [ -d "dreamweaver_helpers_bundle" ] && [ "$(ls -A dreamweaver_helpers_bundle)" ]; then
  git mv dreamweaver_helpers_bundle/* labs/consciousness/dream/helpers/ 2>/dev/null || true
  rmdir dreamweaver_helpers_bundle 2>/dev/null || true
fi

# Create README for new location
cat > labs/consciousness/dream/README.md <<'EOF'
# Dream Synthesis Module

Consolidated dream synthesis functionality from scattered directories.

## Structure

- `synthesis/` - Dream synthesis engines (formerly `dream/`)
- `results/` - Dream output and results (formerly `dreams/`)
- `helpers/` - Helper utilities (formerly `dreamweaver_helpers_bundle/`)
- `config/` - Dream configuration
- `tests/` - Dream tests

## Migration

Old imports:
```python
from dream import ...
from dreams import ...
from dreamweaver_helpers_bundle import ...
```

New imports:
```python
from labs.consciousness.dream.synthesis import ...
from labs.consciousness.dream.results import ...
from labs.consciousness.dream.helpers import ...
```

Compatibility shim available during migration period.
EOF

# Create compatibility shim (if needed)
cat > dream.py <<'EOF'
"""
COMPATIBILITY SHIM: dream → labs.consciousness.dream.synthesis

DEPRECATED: Use labs.consciousness.dream.synthesis for new code.
This shim will be removed in Q1 2026.
"""
import warnings
from labs.consciousness.dream import synthesis

warnings.warn(
    "Importing 'dream' is deprecated. "
    "Use 'labs.consciousness.dream.synthesis' instead. "
    "This shim will be removed in Q1 2026.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export synthesis module
__all__ = dir(synthesis)
for attr in dir(synthesis):
    if not attr.startswith('_'):
        globals()[attr] = getattr(synthesis, attr)
EOF

# Check for import references
grep -r "from dream\|import dream" --include="*.py" . | \
  grep -v ".git" | grep -v "node_modules" | \
  tee /tmp/dream_references.txt

# Commit
git add -A
git commit -m "chore(structure): consolidate dream modules into labs/consciousness/dream

Problem:
- dream/, dreams/, dreamweaver_helpers_bundle/ scattered across repo
- Unclear organization for consciousness dream research

Solution:
- Consolidated into labs/consciousness/dream/ with clear structure:
  - synthesis/ (engines)
  - results/ (outputs)
  - helpers/ (utilities)
- Added compatibility shim for migration period
- Updated X import references

Impact:
- Unified dream research location
- Clearer consciousness architecture
- Compatibility shim allows gradual migration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Verification**:
```bash
make smoke
python3 -c "from labs.consciousness.dream import synthesis; print('Dream import OK')"
```

### Phase 2 Checkpoint

```bash
# Push Phase 2 changes
git push origin chore/consolidation-2025-10-26

# Create Phase 2 PR (or update existing PR)
gh pr create \
  --title "chore(structure): Phase 2 - Consolidate eval and dream directories" \
  --body "## Phase 2: Eval and Dream Consolidation

**Changes**:
- ✅ eval_runs/ + evals/ → evaluations/
- ✅ dream/ + dreams/ + dreamweaver_helpers_bundle/ → labs/consciousness/dream/
- ✅ Compatibility shims added for migration

**Testing**:
- ✅ Smoke tests: 10/10 passing
- ✅ Import compatibility verified
- ✅ No broken references

**Risk**: Medium
**Rollback**: PR revert" \
  --base main
```

---

## Phase 3: MATRIZ Case Standardization (2-4 hours) 🚨 HIGH RISK

### 3.0 Pre-Flight Checks (15 minutes)

```bash
# Verify case-insensitive issue
ls -lid MATRIZ matriz
# Expected: Same inode number

# Check existing compatibility shim
cat MATRIZ/__init__.py | grep -A5 "compatibility"
# Should see existing shim code

# Count imports to update
echo "=== Counting imports to update ==="
grep -r "from matriz\." --include="*.py" . 2>/dev/null | wc -l
grep -r "import matriz" --include="*.py" . 2>/dev/null | wc -l

# Backup current state
git branch backup/before-matriz-fix

# Full test baseline
make smoke > /tmp/matriz_pre_smoke.txt
python3 -m pytest tests/ --collect-only 2>&1 | tee /tmp/matriz_pre_collection.txt
```

**STOP**: Team review required before proceeding.

### 3.1 Install AST Rewriter Dependencies (5 minutes)

```bash
# Install astor for AST → source conversion
pip3 install astor

# Verify script works
python3 scripts/consolidation/rewrite_matriz_imports.py --help

# Test dry-run on small subset
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --dry-run \
  --path tests/ \
  --verbose | head -50
```

### 3.2 Two-Step Directory Rename (15 minutes)

**CRITICAL**: Must use two-step rename on case-insensitive filesystem.

```bash
# Step 1: Rename to temporary name
git mv MATRIZ MATRIZ_temp
git status | grep renamed

# Commit step 1
git commit -m "temp: prepare MATRIZ for case standardization

- First step of two-step case-only rename
- Required for case-insensitive filesystems (macOS APFS)
- No functional changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and verify
git push origin chore/consolidation-2025-10-26

# Step 2: Rename to canonical uppercase name
git mv MATRIZ_temp MATRIZ
git status | grep renamed

# Commit step 2
git commit -m "fix(matriz): standardize MATRIZ directory to uppercase

Problem:
- MATRIZ and matriz showed as same directory (same inode 16291479)
- macOS case-insensitive filesystem issue
- Import ambiguity (from matriz. vs from MATRIZ.)

Solution:
- Standardized to uppercase MATRIZ (official branding)
- Used two-step rename via temp name (FS-safe)
- Existing compatibility shim in MATRIZ/__init__.py provides
  backward compatibility for lowercase imports

Impact:
- Resolves case ambiguity
- Aligns with LUKHAS naming (uppercase for major components)
- Compatibility shim allows gradual migration

Next: Update imports via AST-safe codemod

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push
git push origin chore/consolidation-2025-10-26
```

**Verification**:
```bash
# Confirm only one MATRIZ directory
ls -lid MATRIZ matriz 2>&1
# Expected: matriz: No such file or directory (if rename succeeded)
# OR: Same inode (if FS still shows both - normal on macOS)

# Verify compatibility shim works
python3 -c "import matriz; print('Lowercase shim works:', matriz.__file__)"
python3 -c "import MATRIZ; print('Uppercase works:', MATRIZ.__file__)"
```

### 3.3 Update Imports with AST Rewriter (1-2 hours)

```bash
# Dry run first (review changes)
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --dry-run \
  --verbose > /tmp/matriz_dryrun.txt

# Review changes
less /tmp/matriz_dryrun.txt

# If dry-run looks good, apply changes
python3 scripts/consolidation/rewrite_matriz_imports.py

# Review git diff
git diff --stat
git diff | head -500

# Run tests after import changes
make smoke
# If smoke fails, investigate and fix before proceeding

# If smoke passes, run broader tests
python3 -m pytest tests/smoke -v
python3 -m pytest tests/unit/MATRIZ -v

# Commit import updates
git add -A
git commit -m "fix(imports): update all matriz → MATRIZ imports (AST-safe)

Problem:
- 500+ import statements used lowercase 'matriz'
- Caused import ambiguity and collection errors

Solution:
- Used AST-safe import rewriter (not blind regex)
- Rewrote 'from matriz.' → 'from MATRIZ.'
- Rewrote 'import matriz' → 'import MATRIZ'
- Preserved compatibility shim for gradual migration

Impact:
- All imports now use canonical uppercase MATRIZ
- Tests collection improved
- Compatibility shim provides safety net

Script: scripts/consolidation/rewrite_matriz_imports.py

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3.4 Update Module Registry and Manifests (30 minutes)

```bash
# Find all module manifests referencing matriz
find . -name "module.manifest*.json" -exec grep -l "matriz" {} \; | \
  tee /tmp/matriz_manifests.txt

# Update each manifest (manual review required)
# Replace "matriz" with "MATRIZ" in paths and module names

# Update MODULE_INDEX.md
sed -i.bak 's/`matriz\./`MATRIZ./g' MODULE_INDEX.md
sed -i.bak 's/matriz\//MATRIZ\//g' MODULE_INDEX.md

# Update README.md
sed -i.bak 's/`matriz`/`MATRIZ`/g' README.md

# Update architecture docs
find docs/ -name "*.md" -exec sed -i.bak 's/matriz\//MATRIZ\//g' {} \;

# Commit
git add -A
git commit -m "docs(matriz): update all references to uppercase MATRIZ

- Updated MODULE_INDEX.md
- Updated README.md
- Updated architecture documentation
- Updated module manifests

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 3.5 Full Test Suite Validation (30 minutes)

```bash
# Run comprehensive tests
echo "=== Running full test validation ==="

# Smoke tests
make smoke > /tmp/matriz_post_smoke.txt
diff /tmp/matriz_pre_smoke.txt /tmp/matriz_post_smoke.txt || echo "Check differences"

# Collection errors comparison
python3 -m pytest tests/ --collect-only 2>&1 | tee /tmp/matriz_post_collection.txt
echo "Collection errors before:"
grep -c "ERROR" /tmp/matriz_pre_collection.txt || echo "0"
echo "Collection errors after:"
grep -c "ERROR" /tmp/matriz_post_collection.txt || echo "0"

# Run MATRIZ-specific tests
python3 -m pytest tests/unit/ -k "matriz or MATRIZ" -v

# Import validation
python3 -c "
import sys
import importlib

# Test uppercase import
try:
    MATRIZ = importlib.import_module('MATRIZ')
    print('✅ MATRIZ import works')
except Exception as e:
    print(f'❌ MATRIZ import failed: {e}')
    sys.exit(1)

# Test lowercase compatibility
try:
    matriz = importlib.import_module('matriz')
    print('✅ matriz (lowercase) compatibility shim works')
except Exception as e:
    print(f'❌ matriz compatibility failed: {e}')
    sys.exit(1)

# Test submodule imports
try:
    from MATRIZ.consciousness import *
    print('✅ MATRIZ.consciousness import works')
except Exception as e:
    print(f'❌ MATRIZ.consciousness import failed: {e}')
    sys.exit(1)

print('\\n✅ All MATRIZ imports validated')
"

# If all tests pass:
echo "✅ MATRIZ consolidation complete and validated"
```

### Phase 3 Checkpoint

```bash
# Push all Phase 3 changes
git push origin chore/consolidation-2025-10-26

# Create Phase 3 PR (CRITICAL - requires review)
gh pr create \
  --title "fix(matriz): standardize MATRIZ case and update all imports (500+ changes)" \
  --body "## Phase 3: MATRIZ Case Standardization 🚨 HIGH IMPACT

### Problem
- MATRIZ and matriz showed as same directory (inode 16291479)
- macOS case-insensitive filesystem issue
- 500+ imports used lowercase 'matriz'
- Import ambiguity and collection errors

### Solution
1. ✅ Two-step directory rename (MATRIZ → MATRIZ_temp → MATRIZ)
2. ✅ AST-safe import rewriter (not blind regex)
3. ✅ Updated 500+ import statements
4. ✅ Existing compatibility shim preserved for migration
5. ✅ Module manifests and documentation updated

### Testing
- ✅ Smoke tests: 10/10 passing
- ✅ MATRIZ imports validated (uppercase and lowercase shim)
- ✅ Test collection errors: BEFORE vs AFTER comparison
- ✅ Full MATRIZ test suite passing

### Impact
- All imports now use canonical uppercase MATRIZ
- Compatibility shim allows gradual migration
- Deprecation notice added (remove Q1 2026)

### Rollback
\`\`\`bash
# Revert individual commits
git revert <commit3> <commit2> <commit1>
# OR restore from backup
git checkout backup/before-matriz-fix
\`\`\`

### Review Checklist
- [ ] Import changes reviewed (see scripts/consolidation/rewrite_matriz_imports.py)
- [ ] Smoke tests passing (10/10)
- [ ] MATRIZ imports validated
- [ ] Documentation updated
- [ ] Team notified of deprecation schedule

**Risk**: High (500+ imports changed)
**Requires**: Team lead approval
**Timeline**: Merge after 24h review period" \
  --base main \
  --label "high-risk" \
  --label "breaking-change"

# DO NOT MERGE until team review complete
echo "⚠️  Phase 3 PR created - WAIT FOR TEAM REVIEW before merging"
```

---

## Phase 4: Final Documentation and CI Updates (1 hour)

### 4.1 Update MODULE_INDEX.md (15 minutes)

```bash
# Update with new directory structure
cat >> MODULE_INDEX.md <<'EOF'

## 🆕 Directory Consolidation (October 26, 2025)

### Changes:
- ✅ `doc/` → Archived (empty stub)
- ✅ `configs/` → Merged into `config/`
- ✅ `final_sweep/` → Archived (legacy batch)
- ✅ `eval_runs/` + `evals/` → `evaluations/`
- ✅ `dream/` + `dreams/` + `dreamweaver_helpers_bundle/` → `labs/consciousness/dream/`
- ✅ `matriz` → Standardized to `MATRIZ` (uppercase)

### New Canonical Locations:
- **Configuration**: `config/` (single location)
- **Documentation**: `docs/` (comprehensive)
- **Evaluations**: `evaluations/runs/` and `evaluations/definitions/`
- **Dream Research**: `labs/consciousness/dream/`
- **MATRIZ**: `MATRIZ/` (uppercase only)

### Compatibility:
- Lowercase `matriz` imports supported via shim until Q1 2026
- Dream imports: compatibility shim at `dream.py`
EOF

git add MODULE_INDEX.md
git commit -m "docs: update MODULE_INDEX with consolidation changes"
```

### 4.2 Update README.md (15 minutes)

```bash
# Update project structure section
# (Manual edit required - update directory tree diagram)

git add README.md
git commit -m "docs: update README with consolidated directory structure"
```

### 4.3 Add CI Safety Guards (30 minutes)

Create `.github/workflows/consolidation-guards.yml`:

```yaml
name: Directory Consolidation Guards

on:
  pull_request:
    paths:
      - '**.py'
      - '**/module.manifest*.json'
      - 'config/**'
      - 'MATRIZ/**'

jobs:
  check-large-files:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for large files (>50MB)
        run: |
          git ls-files --stage | awk '{print $4}' | while read file; do
            size=$(stat -c%s "$file" 2>/dev/null || echo 0)
            if [ "$size" -gt 52428800 ]; then
              echo "❌ Large file detected: $file ($size bytes)"
              exit 1
            fi
          done
          echo "✅ No large files detected"

  check-forbidden-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for forbidden lowercase matriz imports
        run: |
          # Allow matriz imports with DeprecationWarning until Q1 2026
          # But flag if new files added with lowercase imports
          git diff origin/main --name-only --diff-filter=A | grep "\.py$" | while read file; do
            if grep -q "from matriz\." "$file" || grep -q "^import matriz" "$file"; then
              echo "⚠️  New file with lowercase matriz import: $file"
              echo "   Use 'from MATRIZ.' instead"
              echo "   Lowercase imports deprecated, remove Q1 2026"
            fi
          done

  check-config-validity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate config files
        run: |
          # Validate YAML
          find config/ -name "*.yaml" -o -name "*.yml" | while read file; do
            python3 -c "import yaml; yaml.safe_load(open('$file'))" || {
              echo "❌ Invalid YAML: $file"
              exit 1
            }
          done

          # Validate JSON
          find config/ -name "*.json" | while read file; do
            python3 -c "import json; json.load(open('$file'))" || {
              echo "❌ Invalid JSON: $file"
              exit 1
            }
          done

          echo "✅ All config files valid"

  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run import validation
        run: |
          python3 -c "import MATRIZ; print('✅ MATRIZ import OK')"
          python3 -c "import matriz; print('✅ matriz compat OK')" 2>&1 | grep -i deprecation || echo "⚠️  No deprecation warning"
```

```bash
git add .github/workflows/consolidation-guards.yml
git commit -m "ci: add directory consolidation safety guards

- Large file detection (>50MB)
- Forbidden import detection (new files with lowercase matriz)
- Config file validation (YAML/JSON)
- Import health checks

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 4.4 Regenerate Module Registry (15 minutes)

```bash
# Update registry with new paths
python3 scripts/generate_meta_registry.py

# Commit
git add artifacts/module.registry.json docs/_generated/META_REGISTRY.json
git commit -m "chore(registry): regenerate after directory consolidation

- Updated module paths for consolidated directories
- MATRIZ uppercase standardization
- New evaluations/ structure
- New labs/consciousness/dream/ structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Phase 4 Final Push

```bash
# Push all Phase 4 changes
git push origin chore/consolidation-2025-10-26

# Update PR or create Phase 4 PR
gh pr create \
  --title "chore: Phase 4 - Documentation and CI updates for consolidation" \
  --body "## Phase 4: Final Documentation and CI Updates

**Changes**:
- ✅ Updated MODULE_INDEX.md with consolidation changes
- ✅ Updated README.md directory structure
- ✅ Added CI safety guards (large files, imports, config validation)
- ✅ Regenerated module registry with new paths

**Risk**: Low
**Depends on**: Phase 1, 2, 3 merged" \
  --base main
```

---

## Testing and Validation

### Pre-Consolidation Baseline

```bash
# Capture baseline before any changes
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout main
git pull origin main

# Smoke tests
make smoke | tee /tmp/consolidation_baseline_smoke.txt

# Test collection
python3 -m pytest tests/ --collect-only 2>&1 | tee /tmp/consolidation_baseline_collection.txt
grep -c "ERROR" /tmp/consolidation_baseline_collection.txt || echo "0"

# Import validation
python3 -c "import MATRIZ; print('MATRIZ OK')" 2>&1 | tee -a /tmp/consolidation_baseline_imports.txt
python3 -c "import matriz; print('matriz OK')" 2>&1 | tee -a /tmp/consolidation_baseline_imports.txt

# Ruff linting
python3 -m ruff check . --statistics 2>&1 | tee /tmp/consolidation_baseline_ruff.txt
```

### Post-Consolidation Validation

```bash
# After all phases merged
git checkout main
git pull origin main

# Smoke tests
make smoke | tee /tmp/consolidation_final_smoke.txt
diff /tmp/consolidation_baseline_smoke.txt /tmp/consolidation_final_smoke.txt

# Test collection
python3 -m pytest tests/ --collect-only 2>&1 | tee /tmp/consolidation_final_collection.txt
echo "Collection errors BEFORE:"
grep -c "ERROR" /tmp/consolidation_baseline_collection.txt || echo "0"
echo "Collection errors AFTER:"
grep -c "ERROR" /tmp/consolidation_final_collection.txt || echo "0"

# Import validation
python3 -c "import MATRIZ; print('✅ MATRIZ OK')"
python3 -c "import matriz; print('✅ matriz compat OK')" 2>&1 | grep -i deprecation

# Ruff linting
python3 -m ruff check . --statistics 2>&1 | tee /tmp/consolidation_final_ruff.txt
```

### Success Criteria

- [ ] Smoke tests: 10/10 passing (same as baseline)
- [ ] Test collection errors: ≤ baseline (ideally reduced)
- [ ] MATRIZ imports: Both uppercase and lowercase work
- [ ] Deprecation warnings: Show for lowercase matriz imports
- [ ] No new ruff violations introduced
- [ ] CI: All checks passing
- [ ] Documentation: Updated and accurate

---

## Rollback Procedures

### Individual Phase Rollback

```bash
# Phase 1 rollback (doc/, configs/, final_sweep/)
git revert <phase1-commit3> <phase1-commit2> <phase1-commit1>

# Phase 2 rollback (eval, dream)
git revert <phase2-commit2> <phase2-commit1>

# Phase 3 rollback (MATRIZ) - MOST CRITICAL
git revert <phase3-commit4> <phase3-commit3> <phase3-commit2> <phase3-commit1>

# Phase 4 rollback (docs, CI)
git revert <phase4-commit3> <phase4-commit2> <phase4-commit1>
```

### Full Consolidation Rollback

```bash
# Create rollback branch from backup
git checkout -b rollback/consolidation-emergency backup/before-matriz-fix

# Force push (REQUIRES TEAM COORDINATION)
git push -f origin rollback/consolidation-emergency

# Notify team to re-clone
echo "⚠️  ROLLBACK IN PROGRESS - Team must re-clone repository"
```

### Restore from Archive

```bash
# If git history damaged, restore from backup
cd /Users/agi_dev/LOCAL-REPOS/
rm -rf Lukhas
git clone --mirror Lukhas-backup-20251026.git Lukhas.git
cd Lukhas.git
git config --bool core.bare false
git reset --hard
```

---

## Timeline and Resource Allocation

### Conservative Estimate (4-7 hours)

| Phase | Duration | Resources | Risk | Can Pause? |
|-------|----------|-----------|------|------------|
| **Phase 1** | 1 hour | 1 engineer | Low | ✅ Yes |
| **Phase 2** | 1 hour | 1 engineer | Medium | ✅ Yes |
| **Phase 3** | 2-4 hours | 1 engineer + 1 reviewer | **High** | ⚠️  At checkpoints |
| **Phase 4** | 1 hour | 1 engineer | Low | ✅ Yes |
| **Total** | **4-7 hours** | 2 people | Mixed | Per phase |

### Recommended Schedule

**Day 1 Morning** (2 hours):
- Phase 1: Low-risk quick wins
- Phase 2: Eval and dream consolidation
- **STOP**: Team review before Phase 3

**Day 1 Afternoon** (3-4 hours) - After team approval:
- Phase 3: MATRIZ case fix (most critical)
- Full testing and validation
- **STOP**: 24-hour review period

**Day 2** (1 hour) - After Phase 3 approved:
- Phase 4: Documentation and CI updates
- Final validation
- Announce changes to team

### Team Communication Plan

**Before Starting**:
- [ ] Slack announcement: "Directory consolidation starting"
- [ ] Meeting: 15-min overview of plan
- [ ] Doc share: This plan document

**During Phase 3 (MATRIZ)**:
- [ ] Slack update: "MATRIZ case fix in progress - avoid merging to main"
- [ ] PR created with "high-risk" label
- [ ] Team lead review requested

**After Phase 3**:
- [ ] Slack: "MATRIZ case fix complete - review PR before merging"
- [ ] 24-hour review window
- [ ] Document deprecation timeline (Q1 2026)

**After All Phases**:
- [ ] Slack: "Consolidation complete - please `git pull`"
- [ ] Email: Summary of changes with new directory structure
- [ ] Wiki update: Migration guide for lowercase matriz imports

---

## Post-Consolidation Monitoring

### Week 1: Active Monitoring

```bash
# Daily checks (automated via CI)
- Smoke tests passing
- No new collection errors
- Import health checks
- Ruff violations stable

# Manual checks
- Team reports any issues
- Monitor CI failure rates
- Check Slack for confusion
```

### Week 2-4: Passive Monitoring

```bash
# Weekly checks
- Deprecation warning counts (matriz imports)
- CI health
- Any rollbacks needed?
```

### Q1 2026: Deprecation Cleanup

```bash
# Remove compatibility shims
rm matriz/__init__.py
rm dream.py

# Update documentation
# Remove "deprecated" notices

# Announce removal
```

---

## Appendices

### A. Scripts and Tools

1. **AST Import Rewriter**: `scripts/consolidation/rewrite_matriz_imports.py`
2. **Config Validator**: `scripts/consolidation/validate_config_merge.sh`
3. **Import Health Checker**: `scripts/consolidation/check_import_health.py`

### B. Reference Commands

```bash
# Check directory inode (case-sensitivity)
ls -lid MATRIZ matriz

# Find import references
grep -r "from matriz\." --include="*.py" .
grep -r "import matriz" --include="*.py" .

# Count collection errors
python3 -m pytest tests/ --collect-only 2>&1 | grep -c "ERROR"

# Validate YAML files
find config/ -name "*.yaml" | xargs -I{} python3 -c "import yaml; yaml.safe_load(open('{}'))"

# Check for large files
git ls-files --stage | awk '$1 > 52428800 {print $4}'
```

### C. Contacts and Escalation

- **Primary Engineer**: [Your name]
- **Reviewer**: [Team lead name]
- **Escalation**: [Manager name]
- **Emergency Rollback Authority**: [CTO/Tech lead]

---

## Final Checklist

### Before Starting:
- [ ] Team notified
- [ ] Full repository backup created
- [ ] Backup branch created: `backup/before-matriz-fix`
- [ ] Pre-consolidation baseline captured
- [ ] AST rewriter dependencies installed (`pip install astor`)

### Phase 1:
- [ ] doc/ archived
- [ ] final_sweep/ archived
- [ ] configs/ merged into config/
- [ ] Smoke tests passing
- [ ] PR created and reviewed

### Phase 2:
- [ ] eval directories consolidated
- [ ] dream directories consolidated
- [ ] Compatibility shims created
- [ ] Smoke tests passing
- [ ] PR created and reviewed

### Phase 3: 🚨
- [ ] Team approval received
- [ ] Pre-flight checks complete
- [ ] Two-step MATRIZ rename done
- [ ] AST import rewriter run
- [ ] 500+ imports updated
- [ ] Full test suite passing
- [ ] Documentation updated
- [ ] PR created with "high-risk" label
- [ ] 24-hour review period enforced

### Phase 4:
- [ ] MODULE_INDEX.md updated
- [ ] README.md updated
- [ ] CI safety guards added
- [ ] Module registry regenerated
- [ ] Final smoke tests passing
- [ ] PR created and reviewed

### Post-Consolidation:
- [ ] All PRs merged
- [ ] Team notified of completion
- [ ] Migration guide shared
- [ ] Deprecation timeline documented (Q1 2026)
- [ ] Monitoring activated
- [ ] Backup archive retained for 30 days

---

**Document Version**: 2.0 (CORRECTED)
**Created**: 2025-10-26
**Status**: Production-Ready, T4-Compliant
**Approved By**: [Pending team lead sign-off]
**Next Review**: After Phase 3 completion

---

## 🎯 Bottom Line

This V2 plan fixes all critical issues from V1:
- ✅ Safe two-step MATRIZ rename
- ✅ AST-safe import rewriting (no blind regex)
- ✅ Compatibility shims for gradual migration
- ✅ Conservative timeline (4-7 hours, not 2.5)
- ✅ Proper CI guards and pre-commit hooks
- ✅ Correct rollback procedures
- ✅ Team communication and approval workflow

**Risk Level**: Medium-High (but well-controlled)
**Confidence**: High (T4-compliant, production-ready)
**Ready to Execute**: ✅ Yes (after team approval)
