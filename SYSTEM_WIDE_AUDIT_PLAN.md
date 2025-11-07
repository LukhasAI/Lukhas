# 🔍 LUKHAS System-Wide Module Audit Plan

**Mission:** Identify and consolidate ALL fragmented modules across the entire LUKHAS codebase  
**Standard:** 0.01% (Zero-Tolerance Excellence)  
**Scope:** matriz/ + lukhas/ + core/ + candidate/ + labs/ (~7,000 Python files)  
**Timeline:** 4-8 weeks comprehensive analysis + consolidation

---

## 🎯 Audit Objectives

**Primary Goals:**
1. **Identify ALL fragmented modules** - Find every module with multiple versions
2. **Rank implementations** - 1-10 quality scoring for each version
3. **Extract unique logic** - Preserve all valuable code from every version
4. **Define canonical versions** - Declare single source of truth for each module
5. **Create migration paths** - Systematic consolidation with zero regression
6. **Fix import crisis** - Eliminate all 138 test import errors at root

**Success Criteria:**
- ✅ 70%+ reduction in module fragmentation (Guardian: 7→1 achieved)
- ✅ 100% import errors resolved (currently 138)
- ✅ <100ms system initialization (Constellation Framework operational)
- ✅ Comprehensive MODULE_REGISTRY.md documenting all decisions
- ✅ Zero regression - all existing functionality preserved

---

## 📊 Phase 1: Discovery & Assessment (Week 1)

### A. Automated Module Discovery

**Script: `/tmp/discover_duplicates.py`**

```python
#!/usr/bin/env python3
"""Discover all duplicated/fragmented modules across LUKHAS."""

import os
from pathlib import Path
from collections import defaultdict
import ast

def find_all_python_modules(root: Path) -> dict[str, list[Path]]:
    """Find all Python modules and their locations."""
    
    modules = defaultdict(list)
    
    for py_file in root.rglob("*.py"):
        # Skip cache, test files, archive
        if any(skip in str(py_file) for skip in [
            "__pycache__", ".pytest_cache", ".git",
            "archive", "backup", ".venv", "venv"
        ]):
            continue
        
        module_name = py_file.stem
        modules[module_name].append(py_file)
    
    return modules

def analyze_module_versions(module_name: str, paths: list[Path]) -> dict:
    """Analyze all versions of a module."""
    
    versions = []
    
    for path in paths:
        try:
            with open(path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Extract structure
            classes = [node.name for node in ast.walk(tree) 
                      if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) 
                        if isinstance(node, ast.FunctionDef)]
            
            versions.append({
                "path": str(path),
                "lines": len(content.split('\n')),
                "classes": len(classes),
                "functions": len(functions),
                "class_names": classes,
                "function_names": functions,
            })
        except:
            versions.append({
                "path": str(path),
                "error": "Parse failed",
            })
    
    return {
        "module_name": module_name,
        "count": len(paths),
        "versions": versions,
    }

def main():
    root = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")
    
    # Find all modules
    all_modules = find_all_python_modules(root)
    
    # Filter to duplicates only (2+ versions)
    duplicates = {k: v for k, v in all_modules.items() if len(v) >= 2}
    
    print(f"📊 Found {len(all_modules)} unique module names")
    print(f"⚠️  Found {len(duplicates)} fragmented modules (2+ versions)\n")
    
    # Sort by count (most fragmented first)
    sorted_duplicates = sorted(
        duplicates.items(), 
        key=lambda x: len(x[1]), 
        reverse=True
    )
    
    # Analyze top 20 most fragmented
    print("🔥 Top 20 Most Fragmented Modules:\n")
    
    for module_name, paths in sorted_duplicates[:20]:
        analysis = analyze_module_versions(module_name, paths)
        
        print(f"**{module_name}** - {len(paths)} versions")
        for i, version in enumerate(analysis["versions"], 1):
            if "error" in version:
                print(f"  v{i}: {version['path']} - ERROR: {version['error']}")
            else:
                print(f"  v{i}: {version['path']}")
                print(f"      {version['lines']} lines, "
                      f"{version['classes']} classes, "
                      f"{version['functions']} functions")
        print()
    
    # Write full report
    report_path = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas-test-integration/MODULE_FRAGMENTATION_REPORT.md")
    with open(report_path, 'w') as f:
        f.write("# LUKHAS Module Fragmentation Report\n\n")
        f.write(f"**Total modules:** {len(all_modules)}\n")
        f.write(f"**Fragmented modules:** {len(duplicates)}\n\n")
        f.write("## All Fragmented Modules\n\n")
        
        for module_name, paths in sorted_duplicates:
            f.write(f"### {module_name} ({len(paths)} versions)\n\n")
            analysis = analyze_module_versions(module_name, paths)
            for i, version in enumerate(analysis["versions"], 1):
                f.write(f"**v{i}:** `{version['path']}`\n")
                if "error" not in version:
                    f.write(f"- Lines: {version['lines']}\n")
                    f.write(f"- Classes: {version['classes']}\n")
                    f.write(f"- Functions: {version['functions']}\n")
                f.write("\n")
    
    print(f"\n✅ Full report written to: {report_path}")

if __name__ == "__main__":
    main()
```

**Run discovery:**
```bash
python3 /tmp/discover_duplicates.py
```

**Expected output:**
- List of ALL fragmented modules (estimated 50-100)
- Ranked by fragmentation level (most versions first)
- Full report in MODULE_FRAGMENTATION_REPORT.md

---

### B. Priority Categorization

**Category 1: CRITICAL (Fix immediately - blocking tests)**
- Modules causing import errors in Jules tests
- Infrastructure modules (_bridgeutils, async_orchestrator)
- Core system modules (identity, consciousness, memory)

**Category 2: HIGH (Fix this sprint - production impact)**
- Guardian system (IN PROGRESS)
- Governance modules (drift_manager, schema_registry)
- API/bridge modules

**Category 3: MEDIUM (Next sprint - code health)**
- Labs experimental modules
- Demo/example fragmentation
- Documentation modules

**Category 4: LOW (Future - nice to have)**
- Archived code with live references
- Legacy compatibility stubs

---

## 🔬 Phase 2: Deep Analysis (Week 2)

### For Each Fragmented Module:

**Step 1: Extract Structure**
```bash
# Use guardian_system analysis script as template
python3 /tmp/analyze_module.py <module_name>
```

**Step 2: Rank Versions (1-10)**

**Criteria:**
- **Completeness (30%)** - All features implemented vs stubs
- **Quality (25%)** - Code quality, type hints, documentation
- **Testing (20%)** - Test coverage, test quality
- **Production (15%)** - Used in production vs experimental
- **Constellation (10%)** - Alignment with 8-star framework

**Scoring:**
- **10/10** - Production, complete, tested, documented, Constellation-aligned
- **8-9/10** - Production-ready, minor gaps
- **6-7/10** - Functional, needs polish
- **4-5/10** - Incomplete, stubs, or broken dependencies
- **1-3/10** - Broken, syntax errors, or empty

**Step 3: Method/Class Overlap Analysis**
```python
# For each module, compare all versions
def analyze_overlap(versions: list) -> dict:
    """Find overlapping vs unique logic."""
    
    all_methods = {}
    for v in versions:
        for method in v.methods:
            if method not in all_methods:
                all_methods[method] = []
            all_methods[method].append(v.version_id)
    
    shared = {k: v for k, v in all_methods.items() if len(v) > 1}
    unique = {k: v for k, v in all_methods.items() if len(v) == 1}
    
    return {
        "shared_methods": len(shared),
        "unique_methods": len(unique),
        "total_methods": len(all_methods),
        "overlap_percentage": len(shared) / len(all_methods) * 100,
    }
```

**Guardian system finding:**
- 33 total methods across 3 key versions
- 0 shared methods (0% overlap!)
- 100% unique logic - complementary components, not duplicates

**Step 4: Consolidation Strategy**

**Pattern A: High Overlap (>50%) - Merge**
```python
# Example: Two implementations with mostly duplicate logic
# Strategy: Keep best version, extract unique features, archive others
```

**Pattern B: Low Overlap (<10%) - Modular Architecture**
```python
# Example: Guardian (0% overlap)
# Strategy: Unified API delegating to specialized components
# DON'T merge - preserve all unique logic
```

**Pattern C: Bridge/Forwarding - Document & Simplify**
```python
# Example: schema_registry (2 lines → 618 lines)
# Strategy: Keep forwarding pattern, ensure correctness
```

---

## 📋 Phase 3: Documentation (Week 3)

### Create MODULE_REGISTRY.md

**Template:**

```markdown
# LUKHAS Module Registry

**Purpose:** Canonical source of truth for all module locations  
**Status:** Living document, updated with every consolidation  
**Owner:** Architecture team

---

## Registry Format

### module_name

**Canonical Location:** `core/governance/module_name/`  
**Status:** ✅ Consolidated (v3.0)  
**Last Updated:** 2025-11-07

**Deprecated Locations:**
- `labs/governance/module_name.py` → ARCHIVED (2025-11-07)
- `candidate/module_name.py` → FORWARDING STUB

**Import Path:**
```python
# Correct (v3.0+)
from core.governance.module_name import ModuleClass

# Deprecated but supported (compatibility)
from labs.governance.module_name import ModuleClass  # Auto-forwards
```

**Version History:**
- v3.0 (2025-11-07): Unified architecture, AGI-ready
- v2.0 (2024-XX-XX): Security features, decision envelope
- v1.0 (2023-XX-XX): Initial implementation

**Consolidation Details:**
- 7 versions analyzed
- Best logic extracted: v7 (monitoring), v6 (security), v1 (explainability)
- Expected impact: Fix 12-15 test import errors

---

## Example Entries

### guardian_system ✅

**Canonical:** `core/governance/guardian/v3/`  
**Status:** ✅ Consolidated (v3.0) - IN PROGRESS  
**Import:** `from core.governance.guardian import GuardianV3`

**Deprecated:**
- `lukhas_website/lukhas/governance/guardian_system.py` → v3/decision_envelope.py
- `core/governance/guardian_system_integration.py` → v3/monitoring.py
- `labs/core/governance/guardian_system_2.py` → v3/explainability.py
- 4 others → ARCHIVED

### _bridgeutils ⏳

**Status:** ⏳ ANALYSIS PENDING  
**Known Locations:**
- `bridge/_bridgeutils.py` (3.3KB)
- `scripts/utils/_bridgeutils.py` (4.1KB)

**Issue:** Different APIs, need to determine canonical
```

---

## 🚀 Phase 4: Implementation (Weeks 4-8)

### Week 4: Infrastructure Modules

**Target:** _bridgeutils, async_orchestrator, async_manager

**Strategy:**
1. Analyze both/all versions
2. Rank by quality + usage
3. Declare canonical version
4. Extract unique features from non-canonical
5. Create forwarding stubs
6. Update all imports in tests
7. Run test suite, verify 0 regressions

**Expected impact:** Fix 20-30 import errors

---

### Week 5: Governance Modules

**Target:** drift_manager, schema_registry, ethics components

**Strategy:** Same as Week 4

**Expected impact:** Fix 15-20 import errors

---

### Week 6: Core Systems

**Target:** consciousness fragments, identity duplicates, memory versions

**Strategy:**
1. EXTRA CAUTION - core systems are complex
2. Comprehensive testing before/after
3. Phased rollout (one module at a time)
4. Rollback plan for each consolidation

**Expected impact:** Fix 30-40 import errors

---

### Week 7: Candidate/Labs Migration

**Target:** Promote valuable candidate/ modules, archive dead labs/ code

**Strategy:**
1. Review all candidate/ modules for production readiness
2. Promote ready modules to core/lukhas/
3. Archive experimental labs/ code
4. Add labs/ to PYTHONPATH for legacy compatibility

**Expected impact:** Fix remaining 40-50 import errors

---

### Week 8: Integration & Validation

**Activities:**
1. Run complete test suite (all 775+ tests)
2. Performance benchmarks
3. Security audit
4. Documentation review
5. Create migration guide
6. Rollout plan

**Success Criteria:**
- ✅ 0 import errors (from 138)
- ✅ 100% tests pass or have tracked failures
- ✅ <100ms system initialization
- ✅ MODULE_REGISTRY.md complete
- ✅ All consolidations documented

---

## 🎯 Consolidation Patterns

### Pattern 1: Simple Merge (High Overlap)

**When:** 50%+ method overlap, similar purpose

**Steps:**
1. Identify best version (highest rank)
2. Extract unique methods from other versions
3. Merge unique methods into best version
4. Add comprehensive tests for all methods
5. Archive non-canonical versions
6. Create forwarding stubs
7. Update all imports

**Example:**
```python
# Before: 2 versions with 80% overlap
version_a.py:  method1, method2, method3, method4
version_b.py:  method1, method2, method3, method5

# After: 1 canonical version
canonical.py:  method1, method2, method3, method4, method5
```

---

### Pattern 2: Modular Architecture (Low Overlap)

**When:** <10% method overlap, complementary functionality

**Steps:**
1. Create unified API class
2. Extract each version to specialized component
3. API delegates to appropriate component
4. Preserve ALL unique logic
5. Add integration tests
6. Update documentation

**Example (Guardian):**
```python
# Before: 7 versions, 0% overlap, 33 unique methods
v7: 2 methods (monitoring)
v6: 9 methods (security)
v1: 22 methods (explainability)

# After: Unified API + specialized components
core/governance/guardian/
├── __init__.py              # GuardianV3 unified API
├── v3/
│   ├── monitoring.py        # v7 logic
│   ├── decision_envelope.py # v6 logic
│   └── explainability.py    # v1 logic

# Usage:
guardian = GuardianV3()
guardian.get_system_status()     # Delegates to monitoring
guardian.verify_integrity(...)   # Delegates to decision_envelope
guardian.explain_decision(...)   # Delegates to explainability
```

---

### Pattern 3: Bridge/Forwarding

**When:** Intentional redirection pattern

**Steps:**
1. Verify forwarding logic is correct
2. Document the forwarding relationship
3. Add tests to ensure forwarding works
4. Consider simplifying if too complex

**Example:**
```python
# Small forwarding stub
# governance/schema_registry.py (2 lines)
from lukhas_website.lukhas.governance.schema_registry import *

# Keep this pattern if working correctly
```

---

## 📊 Tracking & Metrics

### Weekly Progress Report

**Template:**
```markdown
## Week X Progress Report

**Modules Analyzed:** X
**Modules Consolidated:** X
**Import Errors Fixed:** X (remaining: Y)
**Tests Passing:** X% (was: Y%)

**This Week:**
- ✅ Consolidated: module1, module2, module3
- 🔧 In Progress: module4, module5
- ⏳ Blocked: module6 (dependency on module7)

**Next Week:**
- Target: module7, module8, module9
- Risk: High complexity in module7
- Mitigation: Extra testing, phased rollout

**Blockers:**
- None / [describe blockers]
```

---

## 🛡️ Risk Mitigation

### Risk 1: Breaking Production Code

**Mitigation:**
- Comprehensive test suite before ANY consolidation
- Feature flags for new consolidated modules
- Parallel operation (old + new) during migration
- Immediate rollback plan
- Canary deployments (10% → 50% → 100%)

### Risk 2: Losing Valuable Logic

**Mitigation:**
- NEVER delete code without analysis
- Archive all non-canonical versions to .archive/
- Document what was extracted vs archived
- Keep git history (don't force-push)
- 30-day grace period before permanent deletion

### Risk 3: Import Chaos During Migration

**Mitigation:**
- Create forwarding stubs immediately
- Update imports in phases (tests first, then code)
- Use automated refactoring tools
- Add temporary PYTHONPATH fixes
- Comprehensive import testing

---

## 🎯 Success Definition

**System-Wide Consolidation is complete when:**

1. ✅ **Zero Import Errors**
   - All 138 test import errors resolved
   - All tests collectable with pytest
   - No ModuleNotFoundError in any test

2. ✅ **MODULE_REGISTRY.md Complete**
   - Every fragmented module documented
   - Canonical location declared for each
   - Deprecation paths documented
   - Import guidance provided

3. ✅ **70%+ Fragmentation Reduction**
   - Example: Guardian 7→1 (86% reduction) ✅
   - Target: 50-100 fragmented modules → 15-30

4. ✅ **Zero Regression**
   - All existing tests still pass
   - No functionality lost
   - Performance maintained or improved

5. ✅ **Professional Documentation**
   - Every consolidation documented
   - Migration guides created
   - Architecture decisions recorded

6. ✅ **<100ms System Init**
   - Constellation Framework operational
   - All 8 stars initialized
   - No import bottlenecks

---

## 🚀 Immediate Next Steps (This Session)

1. **Run discovery script** - Identify all fragmented modules
2. **Prioritize top 20** - Focus on highest-impact consolidations
3. **Begin _bridgeutils analysis** - Next module after Guardian
4. **Create MODULE_REGISTRY.md skeleton** - Start documentation
5. **Quick win: PYTHONPATH fix** - Fix 60% of import errors in 15 minutes

**Ready to execute? Let's rebuild like pros! 🏗️**

---

**Status:** 📋 AUDIT PLAN DOCUMENTED  
**Scope:** System-wide (matriz + lukhas + core + candidate + labs)  
**Timeline:** 4-8 weeks  
**Confidence:** HIGH - Methodology proven with Guardian analysis

