# F821 Bulk Remediation Ready for Application

**Status**: ✅ Both dry-runs completed successfully  
**Date**: 2025-11-08  
**Campaign**: F821 undefined names  
**Branch**: t4/f821-scan-20251108  

---

## Executive Summary

Successfully built and tested **2 bulk remediation codemods** targeting **69 F821 issues** across 2 high-impact files. Both dry-runs generated clean diffs with zero errors. Ready for application.

### Impact Forecast
- **Before**: 436 F821 issues (post-Quick Win)
- **After**: 367 F821 issues (-69, -15.8% reduction)
- **Files Fixed**: 2 of 88 remaining files
- **Estimated Runtime**: <5 seconds per codemod

---

## ✅ Ready-to-Apply Fixes

### 1. oidc.py Prometheus Metrics Fix (19 issues → 0)

**File**: `lukhas_website/lukhas/api/oidc.py`  
**Tool**: `tools/ci/codemods/add_metrics_counters.py`  
**Status**: ✅ Dry-run passed  
**Diff**: `/tmp/oidc_metrics_diff.txt`

#### Proposed Changes
```python
# Add at top of file
from prometheus_client import Counter

# Add after imports
# F821: Prometheus metrics fix - undefined counter
oidc_api_requests_total = Counter(
    "oidc_api_requests_total",
    "Oidc Api Requests Total"
)
```

#### Application Command
```bash
cd /Users/agi_dev/LOCAL-REPOS/lukhas-f821-scan
python3 tools/ci/codemods/add_metrics_counters.py --apply
```

#### Verification
```bash
# Lint check
ruff check lukhas_website/lukhas/api/oidc.py | grep F821

# Syntax check
python3 -m py_compile lukhas_website/lukhas/api/oidc.py

# Test suite
pytest tests/ -k oidc -v
```

---

### 2. creative_q_expression.py Bulk Import Fix (50 issues → 0)

**File**: `qi/engines/creativity/creative_q_expression.py`  
**Tool**: `tools/ci/codemods/add_bulk_imports.py`  
**Status**: ✅ Dry-run passed  
**Diff**: `/tmp/creative_bulk_imports_diff.txt`

#### Proposed Changes
Adds 47 class imports from 2 modules:
- **46 classes** from `labs.consciousness.creativity.qi_creative_types`
- **1 class** from `products.content.poetica.creativity_engines.qi_creative_types`

```python
# F821: Bulk import fix - resolved undefined names
from labs.consciousness.creativity.qi_creative_types import (
    AcetylcholineLearningBridge,
    CollaborativeSessionRequest,
    CreativeBlockchain,
    CreativeConflictHarmonizer,
    CreativeEvolutionEngine,
    CreativeRequest,
    CreativityMeshNetwork,
    CreativityMonitor,
    CreativityStyleEvolver,
    CrossCulturalSynthesizer,
    CulturalQIMemory,
    CulturalResonanceTuner,
    CulturalScaleQuantumLibrary,
    DopamineCreativityModulator,
    DopamineRewardSystem,
    EmergenceDetector,
    EmotionImageryQuantumMapper,
    EmotionalMelodyWeaver,
    EmotionalPreferenceLearner,
    HarmonicQuantumInspiredProcessor,
    KirejiQuantumSelector,
    NeuralCreativityNetwork,
    NeuralOscillator,
    NorepinephrineFocusEnhancer,
    PersonalizedCreation,
    PhoneticHarmonyAnalyzer,
    QIAestheticProfiler,
    QIChoreographer,
    QICodePoet,
    QIEmotionEncoder,
    QIIdeaSynthesizer,
    QIImaginationProcessor,
    QIStoryWeaver,
    QISyllableCounter,
    QIVisualArtist,
    QIWatermarkEmbedder,
    REMDreamSynthesizer,
    RhythmPatternSuperposer,
    SeasonalReferenceEncoder,
    SemanticEntangler,
    SerotoninMoodHarmonizer,
    SwarmCreativityOrchestrator,
    SynapticInspirationPool,
    SynapticPlasticityEngine,
    UserSession,
    ZeroKnowledgeCreativityValidator
)
from products.content.poetica.creativity_engines.qi_creative_types import Quantum3DSculptor
```

#### Application Command
```bash
cd /Users/agi_dev/LOCAL-REPOS/lukhas-f821-scan
python3 tools/ci/codemods/add_bulk_imports.py \
    --file qi/engines/creativity/creative_q_expression.py \
    --map /tmp/creative_import_map_resolved.json \
    --apply
```

#### Verification
```bash
# Lint check
ruff check qi/engines/creativity/creative_q_expression.py | grep F821

# Syntax check
python3 -m py_compile qi/engines/creativity/creative_q_expression.py

# Test suite
pytest tests/ -k creative -v
```

---

## 🛠️ Technical Implementation Details

### Import Resolution Strategy

**Disambiguation Heuristic** for 45 ambiguous classes:
```python
# Pattern: Most classes exist in both modules
# - labs.consciousness.creativity.qi_creative_types
# - products.content.poetica.creativity_engines.qi_creative_types

# Rule: Prefer labs.consciousness for qi/ target files
# Rationale: qi/ is core quantum infrastructure, closer to labs/ than products/
```

**Results**:
- ✅ 47/47 classes found in repo
- ✅ 45/47 ambiguous → resolved via heuristic
- ✅ 2/47 unambiguous → direct mapping

### Repository Search Methodology

```bash
# Search for class definitions
grep -R "class {name}\b" --include="*.py" --exclude-dir=.git

# Extract module paths
./path/to/file.py:linenum:class {name}:
→ path.to.file

# Disambiguation priorities:
1. labs.consciousness.creativity.qi_creative_types (preferred for qi/ files)
2. labs.core.telemetry.monitoring (for EmergenceDetector)
3. labs.core.orchestration.brain.core.types (for UserSession)
4. products.content.poetica.creativity_engines.qi_creative_types (fallback)
```

### LibCST Codemod Architecture

**Key Features**:
- AST-based transformations (no regex)
- Preserves code structure and formatting
- Automatic backup creation (`.bak` files)
- Unified diff generation for review
- Multi-line import formatting (Black-style)

**Safety Mechanisms**:
1. Dry-run mandatory before apply
2. File-level backups before changes
3. Syntax validation via `py_compile`
4. Lint verification via `ruff check`

---

## 📊 Campaign Progress Tracking

### F821 Reduction Timeline

| Stage | Issues | Reduction | % Change |
|-------|--------|-----------|----------|
| Baseline | 461 | - | - |
| Quick Win | 436 | -25 | -5.4% |
| **oidc.py (pending)** | **417** | **-19** | **-4.4%** |
| **creative (pending)** | **367** | **-50** | **-12.0%** |
| **Total Reduction** | **367** | **-94** | **-20.4%** |

### Files Eliminated from Top 10

| Rank | File | Issues | Status |
|------|------|--------|--------|
| 1 | tools/module_schema_validator.py | 40 | ✅ Fixed (Quick Win) |
| 2 | qi/engines/creativity/creative_q_expression.py | 50 | 🔄 Ready to apply |
| 3 | lukhas_website/lukhas/api/oidc.py | 19 | 🔄 Ready to apply |

---

## 🎯 Recommended Application Order

### Option A: Sequential (Conservative)
```bash
# 1. Apply oidc.py fix
python3 tools/ci/codemods/add_metrics_counters.py --apply
ruff check lukhas_website/lukhas/api/oidc.py
git add lukhas_website/lukhas/api/oidc.py
git commit -m "fix(F821): add Prometheus Counter imports (19 issues)"

# 2. Apply creative fix
python3 tools/ci/codemods/add_bulk_imports.py --file qi/engines/creativity/creative_q_expression.py --map /tmp/creative_import_map_resolved.json --apply
ruff check qi/engines/creativity/creative_q_expression.py
git add qi/engines/creativity/creative_q_expression.py
git commit -m "fix(F821): bulk import 47 consciousness classes (50 issues)"
```

### Option B: Batch (Aggressive)
```bash
# Apply both fixes
python3 tools/ci/codemods/add_metrics_counters.py --apply
python3 tools/ci/codemods/add_bulk_imports.py --file qi/engines/creativity/creative_q_expression.py --map /tmp/creative_import_map_resolved.json --apply

# Verify all changes
ruff check lukhas_website/lukhas/api/oidc.py qi/engines/creativity/creative_q_expression.py
python3 -m py_compile lukhas_website/lukhas/api/oidc.py qi/engines/creativity/creative_q_expression.py

# Single commit
git add lukhas_website/lukhas/api/oidc.py qi/engines/creativity/creative_q_expression.py tools/ci/codemods/
git commit -m "fix(F821): bulk remediation - metrics + consciousness imports (69 issues)"
```

---

## 🚀 Next Steps (Post-Application)

### 1. Update F821 Baseline
```bash
# Re-run scan
ruff check --select F821 --output-format json . 2>/dev/null | tail -n +2 > /tmp/ruff_f821_post_bulk.json

# Update scanner summary
python3 tools/ci/f821_scan.py /tmp/ruff_f821_post_bulk.json

# Expected: 367 issues (down from 436)
```

### 2. Create PR for Review
```bash
git push origin t4/f821-scan-20251108 --force-with-lease

gh pr create \
    --title "fix(F821): Bulk remediation campaign - 94 issues resolved" \
    --body "$(cat F821_BULK_REMEDIATION_READY.md)" \
    --draft
```

### 3. Continue Campaign
Next targets from top 10:
- `qi/creativity/dream_evolution.py` (15 issues)
- `qi/creativity/creativity_blockchain.py` (13 issues)
- `qi/creativity/cultural_resonance_tuner.py` (11 issues)

---

## 📝 Artifacts

All intermediate files preserved for audit trail:

### Input Data
- `/tmp/ruff_f821.json` - Original F821 scan (461 issues)
- `/tmp/ruff_f821_clean.json` - Cleaned JSON array
- `/tmp/ruff_f821_updated.json` - Post-Quick Win scan (436 issues)

### Analysis Outputs
- `/tmp/f821_first_shard.txt` - Heuristic shard (1 file)
- `/tmp/ruff_f821_summary.json` - Structured analysis

### oidc.py Metrics Fix
- `/tmp/oidc_metrics_diff.txt` - Unified diff preview

### creative_q_expression.py Bulk Fix
- `/tmp/creative_f821.json` - F821 issues for creative file
- `/tmp/creative_undef_names.json` - 47 extracted class names
- `/tmp/creative_name_matches.json` - Grep search results
- `/tmp/creative_import_map_resolved.json` - Final import mappings
- `/tmp/creative_bulk_imports_diff.txt` - Unified diff preview

### Codemods
- `tools/ci/codemods/add_metrics_counters.py` - Prometheus Counter automation
- `tools/ci/codemods/add_bulk_imports.py` - Bulk import insertion

---

## ✅ Quality Gates Passed

- [x] All undefined names found in repository (47/47)
- [x] Import ambiguity resolved via heuristic (45/45)
- [x] LibCST codemods generate syntactically valid code
- [x] Dry-runs produce clean diffs with zero errors
- [x] Backup mechanism tested (`.bak` files created)
- [x] Unified diffs generated for human review
- [x] No cross-file dependencies identified

---

**Ready for Application**: Yes ✅  
**Risk Level**: Low (dry-runs passed, backups created)  
**Estimated Time**: <2 minutes total  
**Reviewer**: Human approval recommended before `--apply`
