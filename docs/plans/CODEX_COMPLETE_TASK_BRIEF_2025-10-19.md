---
title: Codex Agent - Complete Task Brief (Post-Phase 5B)
date: 2025-10-19
status: ready-for-execution
priority: high
assigned: Codex Agent / GitHub Copilot
estimated_time: 4-6 hours
complexity: high
---

# Codex Agent - Complete Task Brief

**Created**: 2025-10-19
**Status**: Ready for Execution
**Priority**: HIGH
**Estimated Time**: 4-6 hours
**Complexity**: High (2,262 files, multi-phase regeneration)
**Context**: Post-Phase 5B directory flattening

---

## 🎯 Mission

Execute Phase 4 manifest regeneration with validated star assignment rules across 1,571+ existing manifests, ensuring architectural alignment and contract compliance.

---

## 📊 Current State

### Repository Structure (Post-Phase 5B)
```
Lukhas/
├── consciousness/          # Production consciousness modules
├── identity/              # Production identity modules
├── governance/            # Production governance modules
├── memory/               # Production memory modules
├── core/                 # Core integration modules (253 files)
├── labs/                 # Development lane (was candidate/, 2,877 files)
├── manifests/            # ALL manifests mirror code structure (FLAT)
│   ├── consciousness/
│   ├── identity/
│   ├── labs/
│   └── ...
├── matriz/               # MATRIZ cognitive engine
└── api/                  # Public API layer
```

**CRITICAL**: NO MORE `lukhas/` directory. All paths are FLAT.
- ✅ Correct: `manifests/consciousness/core/module.manifest.json`
- ❌ Wrong: `manifests/lukhas/consciousness/core/module.manifest.json`

### Current Metrics
```
Total Python Packages:  1,953
Current Manifests:      1,571
Coverage:              80.4%
Target (99%):          1,934
Gap:                     363 manifests
```

### Completed Prerequisites
- ✅ **Phase 5B**: Directory flattening complete (PRs #433, #434)
- ✅ **Star Rules**: Validated and approved (configs/star_rules.json)
- ✅ **Context Files**: YAML front matter added (91 files)
- ✅ **Constellation Docs**: Updated with accurate module counts

---

## 📋 Task Overview

You will execute **THREE MAJOR TASKS** in sequence:

1. **Task 4.1**: Regenerate 1,571 Existing Manifests (with star promotions)
2. **Task 4.2**: Generate 363 Missing Manifests (achieve 99% coverage)
3. **Task 4.3**: Update Constellation Dashboard & Metrics

**Total Expected Output**: 1,934 manifests, comprehensive audit reports, updated dashboards

---

## 📋 Task 4.1: Regenerate Existing Manifests with Star Promotions

**Priority**: HIGH
**Time**: 2-3 hours
**Files**: 1,571 existing manifests
**Objective**: Apply validated star assignment rules to promote manifests from Supporting to specific stars

### Background

Many manifests currently have `constellation.stars: ["Supporting"]` as a placeholder. The validated star rules in `configs/star_rules.json` can now promote these to specific constellation stars based on:

- **Capability overrides**: Explicit capabilities in manifest
- **Node overrides**: MATRIZ node integration
- **Path regex**: Module path heuristics
- **Owner priors**: Module owner metadata
- **Dependency hints**: Import dependencies

### Star Assignment Rules

**Configuration**: `configs/star_rules.json` (validated 2025-10-19)

**Weighting System**:
```json
{
  "weights": {
    "capability_override": 0.60,  // Highest priority
    "node_override": 0.50,
    "path_regex": 0.40,
    "owner_prior": 0.35,
    "dependency_hint": 0.30
  },
  "confidence": {
    "min_suggest": 0.50,      // Suggest but keep Supporting
    "min_autopromote": 0.70   // Auto-promote to specific star
  }
}
```

**Nine Canonical Stars**:
```json
{
  "stars": [
    {"id": "Anchor", "emoji": "⚓", "domain": "Core Infrastructure"},
    {"id": "Flow", "emoji": "🌊", "domain": "Consciousness"},
    {"id": "Trail", "emoji": "✦", "domain": "Memory"},
    {"id": "Watch", "emoji": "🛡️", "domain": "Guardian/Governance"},
    {"id": "Horizon", "emoji": "🔭", "domain": "Vision/Perception"},
    {"id": "Oracle", "emoji": "🔮", "domain": "Prediction/Foresight"},
    {"id": "Living", "emoji": "🌱", "domain": "Bio-inspired"},
    {"id": "Drift", "emoji": "🌙", "domain": "Dream/Creativity"},
    {"id": "Supporting", "emoji": "🔧", "domain": "Infrastructure/Utilities"}
  ]
}
```

### Execution Process

#### Step 1: Backup Existing Manifests
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Create backup
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p .backups/manifests_${timestamp}
cp -r manifests/ .backups/manifests_${timestamp}/

echo "✅ Backed up 1,571 manifests to .backups/manifests_${timestamp}/"
```

#### Step 2: Regenerate with Star Rules
```bash
# Find all existing manifests
find manifests -name "module.manifest.json" -type f > /tmp/existing_manifests.txt

echo "Found $(wc -l < /tmp/existing_manifests.txt) existing manifests"

# Regenerate each manifest with star promotion
while IFS= read -r manifest_path; do
  # Extract module path from manifest path
  # manifests/consciousness/core/module.manifest.json -> consciousness/core
  module_path=$(echo "$manifest_path" | sed 's|^manifests/||; s|/module.manifest.json$||')

  echo "Regenerating: $module_path"

  python scripts/generate_module_manifests.py \
    --module-path "$module_path" \
    --star-from-rules \
    --star-confidence-min 0.70 \
    --preserve-tier \
    --preserve-owner \
    --preserve-contracts \
    --write \
    --verbose

done < /tmp/existing_manifests.txt
```

**Key Flags Explained**:
- `--star-from-rules`: Use validated star rules from configs/star_rules.json
- `--star-confidence-min 0.70`: Only promote if confidence ≥70%
- `--preserve-tier`: Keep existing tier assignment (T1/T2/T3/T4)
- `--preserve-owner`: Keep existing module.owner value
- `--preserve-contracts`: Keep existing contracts array
- `--write`: Write changes to disk
- `--verbose`: Show detailed star scoring

#### Step 3: Validate Regenerated Manifests
```bash
# Validate all manifests pass schema
python scripts/validate_module_manifests.py --strict

# Check for any broken contract references
python scripts/validate_contract_refs.py

# Verify constellation star distribution is reasonable
python -c "
import json
from pathlib import Path
from collections import Counter

manifests = list(Path('manifests').rglob('module.manifest.json'))
star_counts = Counter()

for m in manifests:
    data = json.loads(m.read_text())
    stars = data.get('constellation', {}).get('stars', [])
    for star in stars:
        star_counts[star] += 1

print('Star Distribution After Regeneration:')
for star, count in star_counts.most_common():
    pct = (count / len(manifests)) * 100
    print(f'  {star}: {count} ({pct:.1f}%)')
"
```

### Expected Outcomes

**Star Distribution** (estimated):
- Supporting: ~60-70% (down from ~85% before)
- Flow (Consciousness): ~12-15%
- Trail (Memory): ~8-12%
- Watch (Guardian): ~5-8%
- Anchor (Core): ~3-5%
- Other stars: ~2-5% combined

**Quality Checks**:
- All manifests pass schema validation
- No broken contract references
- Star promotions are architecturally sound
- Tier/owner/contract preservation successful

---

## 📋 Task 4.2: Generate Missing Manifests (99% Coverage)

**Priority**: HIGH
**Time**: 1-2 hours
**Files**: 363 new manifests
**Objective**: Achieve 99% artifact coverage by generating manifests for orphan packages

### Background

After regenerating existing manifests, 363 Python packages still lack manifests. We need to generate these to achieve 99% coverage.

### Execution Process

#### Step 1: Find Orphan Packages
```bash
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

# Find packages with manifests
find manifests -name "module.manifest.json" | \
  sed 's|^manifests/||; s|/module.manifest.json$||' | \
  sort -u > /tmp/manifested_packages.txt

# Find orphans
comm -23 /tmp/all_packages.txt /tmp/manifested_packages.txt > /tmp/orphans.txt

echo "Orphan packages: $(wc -l < /tmp/orphans.txt)"
```

#### Step 2: Generate Manifests for Orphans
```bash
# Generate manifests using star rules
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

**Tier Assignment Strategy** (auto-determined by generator):
- `labs/` modules → T3 or T4 (research/experimental)
- Production modules → T2 (default)
- Core/MATRIZ modules → T1 or T2 (critical)

#### Step 3: Validate Final Coverage
```bash
# Final validation
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
print(f'Status: {'✅ ACHIEVED' if coverage >= 99 else '❌ INCOMPLETE'}')
"
```

---

## 📋 Task 4.3: Update Constellation Dashboard & Metrics

**Priority**: MEDIUM
**Time**: 1 hour
**Files**: Dashboard files, audit reports
**Objective**: Update all constellation documentation with new star distribution

### Files to Update

#### 1. Update CONSTELLATION_TOP.md
```bash
vim docs/CONSTELLATION_TOP.md
```

**Update These Sections**:
- Current Distribution table (1,934 total modules)
- Star-by-star breakdown with new percentages
- Orphan packages count (should be ~19 after 99% coverage)
- Last updated timestamp

**New Distribution** (calculate actual values):
```markdown
## 📊 Current Distribution (1,934 Total Modules)

| Star | Count | Percentage | Tier Breakdown |
|------|-------|------------|----------------|
| Supporting | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🌊 Flow (Consciousness) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| ✦ Trail (Memory) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🛡️ Watch (Guardian) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| ⚓ Anchor (Core) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🔭 Horizon (Vision) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🔮 Oracle (Foresight) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🌱 Living (Bio) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |
| 🌙 Drift (Dream) | XXX | XX.X% | T1: XX, T2: XXX, T3: XXX, T4: XX |

**Manifest Coverage**: 99.X% (1,934 manifests / 1,953 Python packages)
**Orphan Packages**: XX packages without manifests
**Last Updated**: 2025-10-19
```

#### 2. Create Audit Report
```bash
vim docs/audits/phase4_manifest_regeneration_2025-10-19.md
```

**Template**:
```markdown
# Phase 4 Manifest Regeneration Audit Report

**Date**: 2025-10-19
**Executed By**: Codex Agent
**Duration**: X hours
**Status**: ✅ Complete

## Summary

### Task 4.1: Regenerate Existing Manifests
- **Before**: 1,571 manifests (85% Supporting star)
- **After**: 1,571 manifests (XX% Supporting, XX% promoted)
- **Star Promotions**: XXX manifests promoted to specific stars
- **Confidence Threshold**: 0.70 minimum
- **Validation**: ✅ All manifests pass schema

### Task 4.2: Generate Missing Manifests
- **Before Coverage**: 80.4% (1,571/1,953)
- **After Coverage**: 99.X% (1,934/1,953)
- **New Manifests**: 363 generated
- **Validation**: ✅ All manifests pass schema

### Task 4.3: Update Documentation
- ✅ CONSTELLATION_TOP.md updated
- ✅ Audit report created
- ✅ Metrics dashboards refreshed

## Star Distribution Changes

### Before Regeneration
| Star | Count | Percentage |
|------|-------|------------|
| Supporting | ~1,335 | ~85% |
| Flow | ~100 | ~6% |
| Trail | ~80 | ~5% |
| Other | ~56 | ~4% |

### After Regeneration + New Manifests
| Star | Count | Percentage |
|------|-------|------------|
| Supporting | XXX | XX% |
| Flow | XXX | XX% |
| Trail | XXX | XX% |
| Watch | XXX | XX% |
| Anchor | XXX | XX% |
| Other | XXX | XX% |

## Validation Results

### Schema Validation
```bash
$ python scripts/validate_module_manifests.py --strict
✅ 1,934 manifests validated
✅ 0 schema errors
✅ 0 warnings
```

### Contract Validation
```bash
$ python scripts/validate_contract_refs.py
✅ All contract references valid
✅ All T1 manifests have contracts
```

### Coverage Verification
```bash
$ # Coverage calculation
Total packages: 1,953
Total manifests: 1,934
Coverage: 99.0%
Target achieved: ✅
```

## Notable Promotions

### Top Promoted Modules (Supporting → Specific Star)
1. `consciousness/qualia/processor` → Flow (confidence: 0.85)
2. `memory/fold/integration` → Trail (confidence: 0.82)
3. `governance/guardian/core` → Watch (confidence: 0.91)
4. ... (list top 20)

### New T1 Modules Manifested
1. `core/matriz/orchestrator` → Anchor + T1
2. `identity/lambda_id/auth` → Anchor + T1
3. ... (list all new T1)

## Issues & Resolutions

### Issue 1: [Description if any]
- **Problem**: [What happened]
- **Resolution**: [How fixed]
- **Impact**: [Scope]

### Issue 2: ...

## Recommendations

1. **Star Rule Refinement**: Consider adjusting weights for [specific case]
2. **Tier Review**: XX modules may be mis-tiered, manual review recommended
3. **Contract Coverage**: XX T1 modules still lack contracts (follow-up task)

## Files Modified

- 1,571 manifests regenerated (star promotions)
- 363 manifests created (new coverage)
- 1 configuration file used (configs/star_rules.json)
- 2 documentation files updated

**Total Changes**: 1,937 files
```

#### 3. Create Metrics Dashboard Script
```bash
vim scripts/constellation_metrics.py
```

Create a script that generates constellation metrics on demand:

```python
#!/usr/bin/env python3
"""
Generate Constellation Framework metrics and visualizations.

Usage:
    python scripts/constellation_metrics.py --output docs/metrics/

Outputs:
    - constellation_distribution.json
    - tier_breakdown.json
    - star_promotion_report.md
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def analyze_constellation():
    manifests = list(Path('manifests').rglob('module.manifest.json'))

    star_counts = Counter()
    tier_counts = Counter()
    star_tier_breakdown = defaultdict(lambda: defaultdict(int))

    for manifest_path in manifests:
        data = json.loads(manifest_path.read_text())

        # Count stars
        stars = data.get('constellation', {}).get('stars', [])
        for star in stars:
            star_counts[star] += 1

        # Count tiers
        tier = data.get('module', {}).get('tier', 'Unknown')
        tier_counts[tier] += 1

        # Star-tier breakdown
        for star in stars:
            star_tier_breakdown[star][tier] += 1

    return {
        'total_manifests': len(manifests),
        'star_distribution': dict(star_counts),
        'tier_distribution': dict(tier_counts),
        'star_tier_breakdown': {k: dict(v) for k, v in star_tier_breakdown.items()}
    }

if __name__ == '__main__':
    metrics = analyze_constellation()
    print(json.dumps(metrics, indent=2))
```

---

## ✅ Acceptance Criteria

### Task 4.1: Manifest Regeneration
- [ ] All 1,571 existing manifests regenerated
- [ ] Star promotions applied (confidence ≥0.70)
- [ ] All manifests pass schema validation
- [ ] Tier/owner/contract values preserved
- [ ] Backup created before regeneration

### Task 4.2: Missing Manifests
- [ ] Coverage ≥ 99% (1,934+ manifests)
- [ ] All orphan packages manifested
- [ ] All new manifests pass validation
- [ ] Star distribution is reasonable (60-70% Supporting)

### Task 4.3: Documentation
- [ ] CONSTELLATION_TOP.md updated with accurate stats
- [ ] Audit report created with full details
- [ ] Metrics dashboard script created
- [ ] All documentation timestamps updated

---

## 📝 Commit Message Template

```
feat(manifests): Phase 4 complete - 1,934 manifests with star promotions at 99% coverage

Problem:
- 1,571 manifests had placeholder "Supporting" stars
- 363 Python packages lacked manifests (80.4% coverage)
- Star assignment rules validated but not applied

Solution:
- Regenerated 1,571 manifests with star promotion (0.70 confidence)
- Generated 363 new manifests for orphan packages
- Applied validated star rules from configs/star_rules.json
- Updated constellation documentation and metrics

Impact:
- Coverage: 80.4% → 99.0% (1,571 → 1,934 manifests)
- Star promotions: XXX modules promoted from Supporting
- Distribution: XX% Supporting, XX% Flow, XX% Trail, XX% other
- All manifests validated against schema
- Constellation framework fully mapped

Phase 4 complete. Ready for API integration (Phase 2 tasks).

🤖 Generated with Codex Agent

Co-Authored-By: Codex <noreply@github.com>
```

---

## 🚨 Critical Reminders

### Path Structure (Post-Phase 5B)
```
✅ CORRECT:
manifests/consciousness/core/module.manifest.json
manifests/identity/lambda_id/module.manifest.json
manifests/labs/bio/adapters/module.manifest.json

❌ WRONG (pre-Phase 5B):
manifests/lukhas/consciousness/core/module.manifest.json
manifests/candidate/bio/adapters/module.manifest.json
```

### Exclusion Paths
ALWAYS exclude:
```
.venv/
node_modules/
.git/
quarantine/        # Archived/deprecated code
build/
dist/
*.egg-info
__pycache__/
*.pyc
```

### Star Assignment Confidence
- **0.70+**: Auto-promote to specific star
- **0.50-0.69**: Suggest star but keep Supporting
- **<0.50**: Keep as Supporting

### Preservation Flags
When regenerating existing manifests, ALWAYS use:
- `--preserve-tier`: Keep T1/T2/T3/T4
- `--preserve-owner`: Keep module owner
- `--preserve-contracts`: Keep contract references

---

## 🔗 Reference Documents

**Essential Reading**:
1. [AGENTS.md](../../AGENTS.md) - Agent coordination system
2. [EXECUTION_PLAN.md](../EXECUTION_PLAN.md) - Overall project roadmap
3. [configs/star_rules.json](../../configs/star_rules.json) - Star assignment rules
4. [docs/audits/star_rules_validation_2025-10-19.md](../audits/star_rules_validation_2025-10-19.md) - Rules validation

**Tools & Scripts**:
- `scripts/generate_module_manifests.py` - Manifest generator
- `scripts/validate_module_manifests.py` - Schema validator
- `scripts/validate_contract_refs.py` - Contract validator

**Previous Work**:
- PR #433: Phase 5B manifest relocation (Copilot)
- PR #434: Context file enhancements (Jules)
- Issue #436: 99% coverage task (Copilot - may overlap with Task 4.2)

---

## 🚀 Getting Started

1. **Read All Reference Docs** (30 min):
   - AGENTS.md for repository structure
   - Star rules validation report
   - Previous PR #433 to understand flat structure

2. **Verify Environment** (5 min):
   ```bash
   cd /Users/agi_dev/LOCAL-REPOS/Lukhas
   git pull origin main
   python --version  # Verify 3.9+
   python scripts/validate_module_manifests.py  # Ensure tooling works
   ```

3. **Execute Task 4.1** (2-3 hours):
   - Backup manifests
   - Regenerate with star promotions
   - Validate results

4. **Execute Task 4.2** (1-2 hours):
   - Find orphans
   - Generate missing manifests
   - Validate coverage

5. **Execute Task 4.3** (1 hour):
   - Update CONSTELLATION_TOP.md
   - Create audit report
   - Create metrics script

6. **Final Validation & Commit** (30 min):
   ```bash
   # Validate everything
   python scripts/validate_module_manifests.py --strict
   python scripts/validate_contract_refs.py

   # Commit with T4 standards
   git add -A
   git commit -m "..." # Use template above
   git push origin main  # Or create PR
   ```

---

**Status**: Ready for execution
**Blocks**: API integration (Phase 2), OpenAPI specs
**Estimated Completion**: 4-6 hours
**Complexity**: HIGH (2,262 files total)

Good luck, Codex! This is a critical milestone for LUKHAS. 🚀

— Claude Code (LUKHAS Core Team)
