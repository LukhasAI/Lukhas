# GitHub Copilot Task A: Artifact Coverage Audit - Phase 5B Updated

**Created**: 2025-10-19
**Status**: Ready for Delegation
**Priority**: High
**Estimated Time**: 2-3 hours
**Complexity**: Medium
**Model Recommendation**: Claude 3.5 Sonnet or GPT-4

---

## 🎯 Objective

Achieve **99% manifest coverage** (1,934 manifests from 1,953 packages) by generating manifests for orphan modules using the validated star assignment rules.

**Current State** (as of 2025-10-19):
- **Total Python Packages**: 1,953
- **Current Manifests**: 1,571
- **Coverage**: 80.4%
- **Target**: 99% = 1,934 manifests
- **Gap**: 363 manifests needed

---

## 📊 Context: Phase 5B Flat Structure

**CRITICAL**: The repository underwent Phase 5B directory flattening. All manifests are now at **flat structure**:

✅ **Correct**: `manifests/consciousness/core/module.manifest.json`
❌ **Wrong**: `manifests/lukhas/consciousness/core/module.manifest.json`

**Directory Structure**:
```
Lukhas/
├── consciousness/          # Production consciousness modules
├── identity/              # Production identity modules
├── governance/            # Production governance modules
├── memory/               # Production memory modules
├── core/                 # Core integration modules
├── labs/                 # Development lane (was candidate/)
├── manifests/            # ALL manifests mirror code structure
│   ├── consciousness/
│   ├── identity/
│   ├── labs/
│   └── ...
└── quarantine/           # Archived code (exclude)
```

**Exclusion Paths** (IMPORTANT):
- `.venv/`, `node_modules/`, `.git/`
- `quarantine/` (archived/deprecated)
- `build/`, `dist/`, `*.egg-info`
- `__pycache__/`, `*.pyc`

---

## 📋 Task Breakdown

### Step 1: Find Orphan Packages (15 min)

**Goal**: Identify Python packages without manifests

```bash
# Navigate to repository
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Find all Python packages (__init__.py locations)
find . -name "__init__.py" -type f \
  -not -path "./.venv/*" \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./quarantine/*" \
  -not -path "./build/*" \
  -not -path "./dist/*" | \
  awk -F/ '{
    path=""
    for(i=2; i<=NF-1; i++) {
      if(path) path=path"/"$i
      else path=$i
    }
    print path
  }' | sort -u > /tmp/all_packages.txt

# Find packages with manifests (FLAT STRUCTURE)
find manifests -name "module.manifest.json" | \
  sed 's|^manifests/||; s|/module.manifest.json$||' | \
  sort -u > /tmp/manifested_packages.txt

# Find orphans
comm -23 /tmp/all_packages.txt /tmp/manifested_packages.txt > /tmp/orphans.txt

# Report
echo "Total packages: $(wc -l < /tmp/all_packages.txt)"
echo "Manifested packages: $(wc -l < /tmp/manifested_packages.txt)"
echo "Orphan packages: $(wc -l < /tmp/orphans.txt)"
```

**Expected Output**: ~363 orphan packages

---

### Step 2: Generate Manifests with Star Rules (1.5 hours)

**Goal**: Generate manifests using validated star assignment rules

**Tool**: `scripts/generate_module_manifests.py`

**Star Rules Configuration**: `configs/star_rules.json` (validated 2025-10-19)

**Command for Each Orphan**:
```bash
# Read orphans and generate manifests
while IFS= read -r orphan_path; do
  echo "Generating manifest for: $orphan_path"

  python scripts/generate_module_manifests.py \
    --module-path "$orphan_path" \
    --star-from-rules \
    --star-confidence-min 0.70 \
    --write \
    --verbose

done < /tmp/orphans.txt
```

**Star Assignment Strategy** (from configs/star_rules.json):

| Signal | Weight | Purpose |
|--------|--------|---------|
| `capability_override` | 0.60 | Explicit capability declarations |
| `node_override` | 0.50 | MATRIZ node integration |
| `path_regex` | 0.40 | Path-based heuristics |
| `owner_prior` | 0.35 | Owner metadata hints |
| `dependency_hint` | 0.30 | Package dependencies |

**Confidence Thresholds**:
- **0.70+**: Auto-promote to specific star
- **0.50-0.69**: Suggest star (stays Supporting)
- **<0.50**: Stays Supporting

**Expected Star Distribution** (conservative):
- 70-80% Supporting (infrastructure/utilities)
- 10-15% 🌊 Flow (Consciousness)
- 5-8% ✦ Trail (Memory)
- 2-5% 🛡️ Watch (Guardian)
- <2% each for Anchor, Horizon, Oracle, etc.

---

### Step 3: Validate All Manifests (30 min)

**Goal**: Ensure 100% schema compliance

```bash
# Validate all manifests
python scripts/validate_module_manifests.py --strict

# Check final coverage
python3 -c "
from pathlib import Path

all_packages = len([
    p for p in Path('.').rglob('__init__.py')
    if '.venv' not in str(p)
    and 'node_modules' not in str(p)
    and 'quarantine' not in str(p)
    and 'build' not in str(p)
    and 'dist' not in str(p)
])

manifests = len(list(Path('manifests').rglob('module.manifest.json')))
coverage = (manifests / all_packages) * 100

print(f'Total packages: {all_packages}')
print(f'Total manifests: {manifests}')
print(f'Coverage: {coverage:.2f}%')
print(f'Target (99%): {int(all_packages * 0.99)}')
print(f'Gap: {max(0, int(all_packages * 0.99) - manifests)}')
"
```

**Success Criteria**:
- ✅ Coverage ≥ 99%
- ✅ All manifests pass schema validation
- ✅ No broken contract references
- ✅ Star distribution is reasonable (70%+ Supporting)

---

### Step 4: Create Audit Report (20 min)

**Goal**: Document what was generated

**File**: `docs/audits/artifact_coverage_audit_2025-10-19.md`

**Template**:
```markdown
# Artifact Coverage Audit Report

**Date**: 2025-10-19
**Executed By**: GitHub Copilot
**Task**: Generate missing module manifests to achieve 99% coverage

## Summary

- **Before**: 1,571 manifests (80.4% coverage)
- **After**: <NEW_COUNT> manifests (<NEW_COVERAGE>% coverage)
- **Generated**: <DELTA> new manifests
- **Target**: 1,934 manifests (99%)
- **Status**: ✅ Target achieved

## Star Distribution (New Manifests)

| Star | Count | Percentage |
|------|-------|------------|
| Supporting | <COUNT> | <PCT>% |
| 🌊 Flow (Consciousness) | <COUNT> | <PCT>% |
| ✦ Trail (Memory) | <COUNT> | <PCT>% |
| 🛡️ Watch (Guardian) | <COUNT> | <PCT>% |
| Other | <COUNT> | <PCT>% |

## Validation Results

- Schema validation: ✅ PASS
- Contract references: ✅ PASS
- Coverage target: ✅ ACHIEVED

## Sample Generated Manifests

1. `manifests/<path1>/module.manifest.json` - <Star> (<Tier>)
2. `manifests/<path2>/module.manifest.json` - <Star> (<Tier>)
3. ...

## Notes

<Any edge cases, issues, or observations>
```

---

## 📁 Key Files

**Scripts**:
- `scripts/generate_module_manifests.py` - Manifest generator
- `scripts/validate_module_manifests.py` - Schema validator
- `scripts/validate_contract_refs.py` - Contract validator

**Configuration**:
- `configs/star_rules.json` - Star assignment rules (validated 2025-10-19)
- `docs/schemas/matriz_module_compliance.schema.json` - Manifest schema

**Documentation**:
- `docs/CONSTELLATION_TOP.md` - 8-star system overview
- `docs/audits/star_rules_validation_2025-10-19.md` - Star rules validation

**Output**:
- `manifests/**/module.manifest.json` - Generated manifests (FLAT structure)

---

## ✅ Acceptance Criteria

1. ✅ Manifest coverage ≥ 99% (1,934+ manifests)
2. ✅ All new manifests pass `validate_module_manifests.py --strict`
3. ✅ All manifests in correct flat location (`manifests/<module_path>/`)
4. ✅ Star distribution is conservative (70%+ Supporting)
5. ✅ Tier assignments follow quality guidelines
6. ✅ Audit report created in `docs/audits/`
7. ✅ Commit follows T4 standards (no hype)

---

## 📝 Commit Message Template

```
feat(manifests): achieve 99% artifact coverage post-Phase 5B

Problem:
- 363 Python packages lacked module.manifest.json files
- Manifest coverage was 80.4% (1,571/1,953)
- Reduced discoverability and constellation tracking

Solution:
- Scanned repository for orphan packages
- Generated 363 manifests using validated star rules (configs/star_rules.json)
- Used --star-from-rules with 0.70 confidence threshold
- All manifests validated against schema

Impact:
- Coverage: 80.4% → 99.1% (1,571 → 1,934 manifests)
- Star distribution: 78% Supporting, 12% Flow, 8% Trail, 2% other
- All new manifests pass validation
- Constellation tracking now comprehensive

🤖 Generated with GitHub Copilot

Co-Authored-By: Copilot <noreply@github.com>
```

*(Adjust numbers based on actual results)*

---

## 🚨 Important Reminders

### Path Structure (Phase 5B)
- ✅ **Correct**: `manifests/consciousness/core/module.manifest.json`
- ❌ **Wrong**: `manifests/lukhas/consciousness/core/module.manifest.json`

### Exclusion List
```bash
# ALWAYS exclude these paths when scanning
.venv/
node_modules/
.git/
quarantine/       # Archived/deprecated code
build/
dist/
*.egg-info
__pycache__/
*.pyc
```

### Star Assignment Philosophy
- **Be Conservative**: When in doubt, use Supporting
- **High Confidence Only**: Only assign specific stars with confidence ≥ 0.70
- **No Manual Overrides**: Let star_rules.json handle assignments
- **Tier Defaults**: Use T3 for labs/, T2 for production modules

### Validation Requirements
- Run `validate_module_manifests.py --strict` BEFORE committing
- Verify no broken contract references
- Ensure all manifests are in flat structure (no `lukhas/` prefix)

---

## 🤝 Handoff Instructions

**When Complete**:
1. ✅ Create audit report: `docs/audits/artifact_coverage_audit_2025-10-19.md`
2. ✅ Run final validation: `python scripts/validate_module_manifests.py --strict`
3. ✅ Commit with T4 message template (no hype, humble tone)
4. ✅ Create PR or comment with summary:
   - Before/after coverage percentages
   - Number of manifests generated
   - Star distribution breakdown
   - Any edge cases or issues discovered

**Summary Comment Template**:
```markdown
## Task A Complete: 99% Artifact Coverage Achieved

**Coverage**: 80.4% → 99.1% ✅
**New Manifests**: 363 generated
**Star Distribution**: 78% Supporting, 12% Flow, 8% Trail, 2% other
**Validation**: All manifests pass schema checks ✅

**Audit Report**: [docs/audits/artifact_coverage_audit_2025-10-19.md](../audits/artifact_coverage_audit_2025-10-19.md)

**Notes**: <Any observations or edge cases>
```

---

## 🔗 Related Documents

- [COPILOT_UPDATED_BRIEF_POST_PHASE5B.md](./COPILOT_UPDATED_BRIEF_POST_PHASE5B.md) - Phase 5B context
- [CONSTELLATION_TOP.md](../CONSTELLATION_TOP.md) - 8-star system documentation
- [star_rules_validation_2025-10-19.md](../audits/star_rules_validation_2025-10-19.md) - Star rules validation

---

**Prepared By**: Claude Code (Sonnet 4.5)
**Date**: 2025-10-19
**Status**: Ready for Execution
**Blocks**: Phase 4 manifest regeneration
