# 🚀 Guardian Consolidation Execution Plan - With Professional Toolkit

**Integration:** Combining Gonzo's T4-aligned Guardian_Upgrade.py toolkit with our architectural vision  
**Status:** Ready for immediate execution  
**Confidence:** VERY HIGH - Proven methodology + comprehensive vision

---

## 🎯 What Changed: From Vision to Executable Plan

**Before (our vision):**
- Comprehensive architectural design
- AGI-ready patterns
- 8-week timeline
- Success metrics defined

**NOW (with toolkit):**
- ✅ **Automated discovery script** - finds exact + near duplicates
- ✅ **PYTHONPATH helper** - safe, non-destructive quick win
- ✅ **PR template** - enforces T4 guardrails (snapshots, tests, registry)
- ✅ **Copilot brief** - keeps AI agents aligned with safety rules
- ✅ **Data-driven decisions** - evidence, not opinions

---

## 📋 Phase 0: Setup Toolkit (15 minutes)

### Step 1: Copy Guardian Discovery Script

```bash
# Create scripts directory if needed
mkdir -p scripts

# Copy discovery script from Gonzo docs
cp docs/gonzo/Guardian_Upgrade.py scripts/guardian_discovery.py

# Make executable
chmod +x scripts/guardian_discovery.py
```

### Step 2: Create PYTHONPATH Helper

```bash
cat > scripts/fix_pythonpath.sh << 'SCRIPT'
#!/usr/bin/env bash
# fix_pythonpath.sh - Suggest PYTHONPATH additions for local dev

REPO_ROOT="${1:-.}"
echo "Scanning for Python packages under ${REPO_ROOT} ..."

# Find all __init__.py files and extract package directories
PKGS=()
while IFS= read -r dir; do
  PKGS+=("$dir")
done < <(find "$REPO_ROOT" -type f -name "__init__.py" -exec dirname {} \; | sort -u)

if [ ${#PKGS[@]} -eq 0 ]; then
  echo "No packages found. Add repo root to PYTHONPATH:"
  echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
  exit 0
fi

# Extract unique top-level directories
declare -A TOPS
for p in "${PKGS[@]}"; do
  rel=$(realpath --relative-to="$REPO_ROOT" "$p" 2>/dev/null || echo "$p")
  top=$(echo "$rel" | cut -d'/' -f1)
  TOPS["$top"]=1
done

echo ""
echo "Suggested PYTHONPATH entries (paste into shell or .env):"
for t in "${!TOPS[@]}"; do
  echo "export PYTHONPATH=\"\$(pwd)/$t:\$PYTHONPATH\""
done

echo ""
echo "Or add repository root:"
echo "export PYTHONPATH=\"\$(pwd):\$PYTHONPATH\""
SCRIPT

chmod +x scripts/fix_pythonpath.sh
```

### Step 3: Create PR Template with T4 Guardrails

```bash
mkdir -p .github

cat > .github/PULL_REQUEST_TEMPLATE.md << 'TEMPLATE'
## What/Why
Describe the change in one sentence. Why is this change necessary?

## Checklist (T4 guardrails)
- [ ] **Snapshot**: Recorded state snapshot for audit trail (attach ledger id or file)
- [ ] **Tests**: Unit/integration tests added/updated. All tests pass: `pytest -q`
- [ ] **Module Registry**: New/modified modules registered in `lukhas/core/module_registry.py`
- [ ] **Observability**: Metrics intact (`lukhas_guardian_decision_total` etc.)
- [ ] **Documentation**: Updated README, docs/guardian-enhancements.md
- [ ] **Zero-regression**: No behavior changes (explain test coverage)
- [ ] **Canary**: Rollback plan provided for risky changes
- [ ] **Audit**: Dual approval captured for governance/flag changes

## Implementation notes
Short implementation notes and reasoning. Link to discovery report if relevant.

## Testing instructions
How to run tests locally and manual verification steps.

## Snapshot metadata
Attach snapshot output or ledger transaction id:
```

---

## 🔍 Phase 1: Automated Discovery (30 minutes)

### Run Guardian Discovery Script

```bash
# From repo root (main Lukhas, not worktree)
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Run discovery with recommended threshold
python3 scripts/guardian_discovery.py \
  --repo-root . \
  --output reports/guardian_discovery.json \
  --similarity 0.85

# Review results
less reports/guardian_discovery.txt
cat reports/guardian_discovery.json | jq '.summary'
```

**What it finds:**
- ✅ Exact duplicate functions (hash-based)
- ✅ Near-duplicate functions (similarity ≥ 0.85)
- ✅ Import/dependency graph
- ✅ Guardian modules not in module_registry.py
- ✅ Evidence-based prioritization

**Expected output:**
```json
{
  "py_files": 7000,
  "functions_found": ~15000,
  "exact_duplicate_groups": 50-100,
  "near_duplicate_pairs": 100-200,
  "guardian_files": 12-20,
  "guardian_modules_detected": ["guardian", "labs/governance/guardian", ...],
  "guardian_not_registered_in_module_registry": ["guardian_system", ...]
}
```

---

## ⚡ Phase 2: Quick Win - PYTHONPATH Fix (20 minutes)

### Step 1: Run PYTHONPATH Helper

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas-test-integration

# Get suggestions
bash ../Lukhas/scripts/fix_pythonpath.sh ../Lukhas
```

**Expected output:**
```bash
Suggested PYTHONPATH entries:
export PYTHONPATH="$(pwd)/labs:$PYTHONPATH"
export PYTHONPATH="$(pwd)/bridge:$PYTHONPATH"
export PYTHONPATH="$(pwd)/candidate:$PYTHONPATH"
export PYTHONPATH="$(pwd)/core:$PYTHONPATH"
```

### Step 2: Apply to conftest.py (Surgical Edit)

```python
# Add to tests/conftest.py (or create if missing)
import sys
from pathlib import Path

# Add discovered package paths
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "labs"))
sys.path.insert(0, str(repo_root / "bridge"))
sys.path.insert(0, str(repo_root / "candidate"))
sys.path.insert(0, str(repo_root / "core"))
```

### Step 3: Verify Import Fix

```bash
# Count import errors before
pytest --collect-only 2>&1 | grep -c "ModuleNotFoundError"  # Should be 138

# Apply conftest.py change
# (use replace_string_in_file in next step)

# Count import errors after
pytest --collect-only 2>&1 | grep -c "ModuleNotFoundError"  # Should be ~55 (60% reduction)
```

**Expected Impact:** Fix 83/138 import errors (60%) in 20 minutes!

---

## 📊 Phase 3: Triage Discovery Report (1-2 hours)

### Analyze Top Duplicates

**From guardian_discovery.json:**

1. **Exact duplicates** - highest priority
   - Same hash = identical code
   - Safe to consolidate immediately
   - Example: `guardian_system.get_system_status()` in 3 locations

2. **Near duplicates (>0.90 similarity)** - high priority
   - Minor variations (docstrings, comments, formatting)
   - Merge after review
   - Example: `verify_integrity()` with different error messages

3. **Medium similarity (0.85-0.90)** - review carefully
   - May have intentional differences
   - Extract common logic, keep variations
   - Example: Different `InterpretabilityEngine` implementations

4. **Guardian modules not registered** - critical governance gap
   - Add to `lukhas/core/module_registry.py`
   - Document tier requirements
   - Example: `guardian_system` missing from registry

### Create Consolidation Matrix

```markdown
| Module | Versions | Overlap % | Strategy | Priority | Effort |
|--------|----------|-----------|----------|----------|--------|
| guardian_system | 7 | 0% | Modular API | P0 | 2 weeks |
| _bridgeutils | 2 | 40% | Merge + extract | P0 | 3 days |
| drift_manager | 2 | 75% | Simple merge | P1 | 2 days |
| schema_registry | 2 | 5% | Forwarding | P1 | 1 day |
```

---

## 🏗️ Phase 4: Systematic Consolidation (Weeks 1-8)

### Week 1: Guardian System (Following Our V3 Vision)

**Using discovery report + our architectural design:**

1. **Run discovery on guardian_system specifically:**
   ```bash
   python3 scripts/guardian_discovery.py --repo-root . --output reports/guardian_system_discovery.json
   ```

2. **Extract best logic (data-driven):**
   - Discovery report shows 0% overlap → confirms modular architecture
   - v7: 2 methods (monitoring) → `v3/monitoring.py`
   - v6: 9 methods (security) → `v3/decision_envelope.py`
   - v1: 22 methods (explainability) → `v3/explainability.py`

3. **Create unified API:**
   ```python
   # core/governance/guardian/v3/__init__.py
   from .core import GuardianV3
   from .monitoring import get_system_status, register_alert_handler
   from .decision_envelope import serialize_decision, verify_integrity
   from .explainability import InterpretabilityEngine
   
   __all__ = ['GuardianV3', ...]
   ```

4. **Add to module registry:**
   ```python
   # lukhas/core/module_registry.py
   MODULE_TIER_REQUIREMENTS = {
       ...
       "guardian": {
           "tier": 1,
           "canonical": "core/governance/guardian/v3/",
           "deprecated": [
               "lukhas_website/lukhas/governance/guardian_system.py",
               "core/governance/guardian_system_integration.py",
               ...
           ],
           "version": "3.0.0",
           "consolidated": "2025-11-07"
       }
   }
   ```

5. **Create forwarding stubs:**
   ```python
   # lukhas_website/lukhas/governance/guardian_system.py
   """DEPRECATED: Use core.governance.guardian.GuardianV3 instead."""
   import warnings
   from core.governance.guardian.v3 import GuardianV3
   
   warnings.warn(
       "guardian_system is deprecated. Use core.governance.guardian.GuardianV3",
       DeprecationWarning,
       stacklevel=2
   )
   
   # Forward all public API
   __all__ = GuardianV3.__all__
   ```

6. **100% test coverage:**
   ```bash
   pytest core/governance/guardian/v3/tests/ -v --cov=core/governance/guardian/v3 --cov-report=term-missing
   # Must show 100% coverage
   ```

7. **PR with T4 guardrails:**
   - Snapshot: Record state before changes
   - Tests: All guardian tests pass
   - Registry: Updated module_registry.py
   - Docs: Update docs/guardian-enhancements.md
   - Zero-regression: Forwarding stubs ensure old imports work

### Week 2-8: Systematic Module Consolidation

**For each fragmented module from discovery report:**

1. Run discovery script filtered to module
2. Analyze overlap percentage
3. Choose strategy:
   - **High overlap (>50%):** Simple merge
   - **Low overlap (<10%):** Modular architecture (Guardian pattern)
   - **Forwarding pattern:** Document and verify
4. Create PR following template
5. Merge with dual approval

---

## 🛡️ T4 Safety Guardrails (ENFORCED)

### Every PR Must Have:

1. **Discovery evidence** - attach relevant section from discovery report
2. **Snapshot** - record state before changes (audit trail)
3. **Tests** - 100% coverage for consolidated code
4. **Registry** - module registered in module_registry.py
5. **Forwarding stubs** - old imports keep working
6. **Documentation** - architecture decisions recorded
7. **Rollback plan** - how to undo if issues arise

### Copilot Brief (Paste Before Any AI Refactoring)

```
T4 BRIEF FOR COPILOT:
- Consolidating guardian code with strict safety guardrails
- Discovery script shows exact duplicates and similarity scores
- Do NOT merge until discovery report reviewed by human
- Quick wins: PYTHONPATH/import fixes only, must pass pytest
- Any functional consolidation requires:
  * Module registration in module_registry.py
  * Unit tests covering preserved behavior
  * Audit snapshot with ledger id
  * Updated docs in guardian/ and docs/
  * Forwarding shims for old APIs (deprecate, don't break)
  * Canary/rollback plan
- Strategy driven by overlap %:
  * >50% overlap: merge
  * <10% overlap: modular API (Guardian pattern)
  * Forwarding: document and verify
```

---

## 📈 Success Metrics (Aligned with Vision)

### Guardian V3 Consolidation:
- ✅ 7 versions → 1 canonical (86% reduction)
- ✅ All 33 unique methods preserved
- ✅ 100% test coverage
- ✅ <1ms latency maintained
- ✅ Zero security vulnerabilities
- ✅ Forwarding stubs for all deprecated paths
- ✅ Module registry updated
- ✅ Fix 12-15 test import errors

### System-Wide Consolidation:
- ✅ 50-100 fragmented modules → 15-30 canonical
- ✅ 138 import errors → 0
- ✅ <100ms system initialization
- ✅ MODULE_REGISTRY.md complete
- ✅ Zero regression (all tests pass)
- ✅ Professional documentation

---

## 🚀 Immediate Next Steps (THIS SESSION)

### Option A: Execute Discovery + Quick Win (1 hour)

1. **Setup toolkit** (15 min)
   ```bash
   # Copy scripts
   cp docs/gonzo/Guardian_Upgrade.py scripts/guardian_discovery.py
   bash scripts/create_pythonpath_helper.sh
   mkdir -p .github && touch .github/PULL_REQUEST_TEMPLATE.md
   ```

2. **Run discovery** (15 min)
   ```bash
   python3 scripts/guardian_discovery.py --repo-root . --output reports/guardian_discovery.json --similarity 0.85
   less reports/guardian_discovery.txt
   ```

3. **PYTHONPATH quick win** (20 min)
   ```bash
   # Get suggestions
   bash scripts/fix_pythonpath.sh .
   
   # Apply to conftest.py
   # (I'll use replace_string_in_file)
   
   # Verify: pytest --collect-only
   ```

4. **Commit results** (10 min)
   ```bash
   git add scripts/ .github/ reports/
   git commit -m "🔧 Setup Guardian consolidation toolkit with T4 guardrails"
   ```

### Option B: Review Vision First

- Take time to review all 2,000+ lines of vision documents
- Review Guardian_Upgrade.py toolkit approach
- Come back with questions or adjustments

### Option C: Custom Scope

- Tell me which specific module to consolidate first
- Or which part of the toolkit to implement

---

## 💡 Why This Integration is Powerful

**Gonzo's Toolkit provides:**
- ✅ Automated discovery (evidence-based decisions)
- ✅ Safety guardrails (T4-aligned PR process)
- ✅ Non-destructive helpers (PYTHONPATH fix)
- ✅ Proven methodology

**Our Architectural Vision provides:**
- ✅ 0.01% quality standard
- ✅ AGI-ready patterns
- ✅ Future-proof design
- ✅ Comprehensive success metrics

**Together:**
- ✅ Data-driven + vision-driven
- ✅ Safety + innovation
- ✅ Quick wins + long-term excellence
- ✅ Proven process + ambitious goals

---

**Status:** 🎯 EXECUTION-READY  
**Risk:** VERY LOW - Proven toolkit + comprehensive vision  
**Confidence:** VERY HIGH - Data-driven, safe, professionally architected

**Your decision: A, B, or C?** 🚀

