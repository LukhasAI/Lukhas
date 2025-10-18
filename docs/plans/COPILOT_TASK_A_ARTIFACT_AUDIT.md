# GitHub Copilot Task A: Artifact Coverage Audit (99% Target)

**Status**: Ready for Delegation
**Priority**: High
**Estimated Time**: 2-3 hours
**Complexity**: Medium
**Model Recommendation**: Claude 3.5 Sonnet or GPT-4

---

## 🎯 Objective

Achieve **99% manifest coverage** by:
1. Finding all orphan modules (directories without `module.manifest.json`)
2. Generating missing manifests with appropriate star assignments
3. Validating all new manifests comply with schema

---

## 📋 Task Breakdown

### Task 1: Scan for Orphan Modules (30 min)

**Goal**: Identify all Python modules lacking manifests

**Commands**:
```bash
# Find all Python package directories (have __init__.py)
find . -type f -name "__init__.py" \
  -not -path "./.venv/*" \
  -not -path "./node_modules/*" \
  -not -path "./.git/*" \
  -not -path "./build/*" \
  -not -path "./dist/*" \
  -exec dirname {} \; | sort -u > /tmp/all_packages.txt

# Find all directories with manifests
find manifests -name "module.manifest.json" \
  -exec dirname {} \; | \
  sed 's|^manifests/||' | sort -u > /tmp/manifested_packages.txt

# Diff to find orphans
comm -23 /tmp/all_packages.txt /tmp/manifested_packages.txt > /tmp/orphan_modules.txt

wc -l /tmp/orphan_modules.txt
```

**Output**: List of orphan module paths

---

### Task 2: Categorize Orphans (30 min)

**Goal**: Classify orphans by domain and suggest star assignments

For each orphan in `/tmp/orphan_modules.txt`:
- Determine domain (consciousness, governance, identity, etc.)
- Suggest initial star (Flow/Trail/Anchor based on code complexity)
- Determine quality tier (T1-T4)

**Heuristics**:
- **Flow (⚡)**: Simple utilities, helpers, small modules
- **Trail (🧭)**: Medium modules with some dependencies
- **Anchor (⚓)**: Core infrastructure, critical dependencies
- **T1**: <50 lines or critical infrastructure
- **T2**: 50-200 lines, moderate complexity
- **T3**: 200-500 lines, research code
- **T4**: >500 lines or experimental

**Output**: JSON categorization file

---

### Task 3: Generate Missing Manifests (1 hour)

**Goal**: Create manifests for all orphans using generator script

**Command Template**:
```bash
# For each orphan module
python scripts/generate_module_manifests.py \
  --module-path <ORPHAN_PATH> \
  --star <SUGGESTED_STAR> \
  --tier <SUGGESTED_TIER> \
  --write
```

**Example**:
```bash
python scripts/generate_module_manifests.py \
  --module-path consciousness/qualia/analyzer \
  --star Flow \
  --tier T3 \
  --write
```

---

### Task 4: Validate Generated Manifests (30 min)

**Goal**: Ensure all new manifests pass validation

**Commands**:
```bash
# Validate all manifests
python scripts/validate_module_manifests.py

# Check for schema errors
python scripts/validate_module_manifests.py --strict

# Verify 99% coverage
python -c "
import json
from pathlib import Path

total_packages = len(Path('.').rglob('__init__.py'))
total_manifests = len(list(Path('manifests').rglob('module.manifest.json')))
coverage = (total_manifests / total_packages) * 100

print(f'Coverage: {coverage:.1f}%')
print(f'Manifests: {total_manifests}')
print(f'Packages: {total_packages}')
"
```

**Success Criteria**: Coverage ≥ 99%

---

## 📁 Key Files

- **Generator**: `scripts/generate_module_manifests.py`
- **Validator**: `scripts/validate_module_manifests.py`
- **Schema**: `schemas/module.manifest.schema.json`
- **Star Rules**: `configs/star_rules.json`
- **Output**: `manifests/***/module.manifest.json`

---

## ✅ Acceptance Criteria

1. [ ] All Python packages have corresponding manifests
2. [ ] Manifest coverage ≥ 99%
3. [ ] All new manifests pass `validate_module_manifests.py`
4. [ ] Star assignments follow constellation rules
5. [ ] Tier assignments are reasonable (not all T4)
6. [ ] Commit message follows T4 standards

---

## 📝 Commit Message Template

```
feat(manifests): achieve 99% artifact coverage with orphan module manifests

**Problem**
Many Python modules lacked module.manifest.json files, reducing
discoverability and preventing constellation star tracking.

**Solution**
- Scanned repository for orphan modules (packages without manifests)
- Generated <N> missing manifests with star/tier assignments
- Validated all manifests against schema

**Impact**
- Coverage: XX% → 99%
- New manifests: <N>
- Total manifests: <TOTAL>
- All manifests validated successfully

🤖 Generated with GitHub Copilot

Co-Authored-By: Copilot <noreply@github.com>
```

---

## 🚨 Important Notes

1. **Exclude Paths**: Skip `.venv/`, `node_modules/`, `.git/`, `build/`, `dist/`, `__pycache__/`
2. **Star Assignments**: Be conservative - most should be Flow/Trail, few Anchors
3. **Quality Tiers**: Research code → T3/T4, production code → T1/T2
4. **Validation**: Run validator BEFORE committing
5. **No Overwrites**: Do NOT regenerate existing manifests

---

## 🤝 Handoff Instructions

When complete:
1. Create audit report in `docs/audits/artifact_coverage_audit_<DATE>.md`
2. Commit with message template above
3. Create summary comment with:
   - Before/after coverage %
   - Number of manifests generated
   - Any edge cases discovered
   - Validation results
