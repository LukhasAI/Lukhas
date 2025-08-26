# 🧹 LUKHAS Codebase Hygiene - Rename Plan

## 🎯 Naming Convention Standards
- **Modules/Files**: `snake_case.py` (lowercase, underscores)
- **Directories**: `snake_case` for packages, `PascalCase` for high-level components
- **Classes**: `PascalCase`
- **Remove**: All `lukhas_`, `legacy_`, `_` prefixes
- **Consolidate**: Single-purpose scattered files into cohesive modules

## 📋 Rename Mappings (15 Critical Changes)

### 1. Directory Renames (Remove lukhas_ prefix)
```
BEFORE                          → AFTER                      LOGIC
lukhas_dreams/                  → dreams/                    Remove redundant prefix, already in lukhas repo
lukhas_governance/              → governance_extended/       Merge with existing governance/
lukhas_personality/             → personality/               Clean module name
lukhas_ethics_guard/            → ethics/                    Merge with existing ethics/
lukhas_awareness_protocol/      → awareness/                 Protocol is implied
lukhas_brain/                   → brain_core/                Distinguish from orchestration/brain/
lukhas_id/                      → identity_legacy/           Mark as legacy, merge later
lukhas_id_enhanced/             → identity_enhanced/         Cleaner naming
lukhas_lambda_id/               → lambda_identity/           Standard ordering
lukhas_next_gen/                → next_gen/                  Remove prefix
```

### 2. Analysis Tool Renames (Remove _ prefix)
```
BEFORE                                      → AFTER                          LOGIC
tools/analysis/_OPERATIONAL_SUMMARY.py  → operational_summary.py         Tool purpose is clear
tools/analysis/_FUNCTIONAL_ANALYSIS.py  → functional_analysis.py         Standard naming
tools/analysis/_WORKSPACE_STATUS.py     → workspace_status.py            Concise and clear
tools/analysis/_SECURITY_GAP.py         → security_gap_analysis.py      Full clarity
tools/analysis/_IMPORT_FIXER.py         → import_fixer.py                Action-oriented name
```

### 3. Core Module Consolidation
```
BEFORE (Multiple Files)                    → AFTER (Single Module)          LOGIC
lukhas_governance/audit_logger/__init__.py
lukhas_governance/compliance_hooks/__init__.py
lukhas_governance/policy_manager/__init__.py    → governance_extended.py       Consolidate sparse modules

lukhas_personality/creative_core/__init__.py
lukhas_personality/narrative_engine/__init__.py → personality_engine.py        Single cohesive module
```

### 4. Legacy Module Updates
```
BEFORE                                      → AFTER                          LOGIC
tools/legacy_analysis/                     → tools/deprecated/              Clear deprecation status
core/orchestration/legacy_adapter.py       → core/orchestration/v1_adapter.py  Version-based naming
```

### 5. Symbolic Module Cleanup
```
BEFORE                                      → AFTER                          LOGIC
core/symbolic/lukhas_symbolic_core.py      → core/symbolic/kernel.py        OpenAI-style naming
core/glyph/glyph_engine.py                → core/glyph/engine.py           Remove redundancy
```

## 🔧 Implementation Script

```python
#!/usr/bin/env python3
"""
Codebase Hygiene - Automated Rename Execution
"""

import os
import shutil
from pathlib import Path

RENAME_MAPPINGS = {
    # Directory renames
    'lukhas_dreams': 'dreams',
    'lukhas_governance': 'governance_extended',
    'lukhas_personality': 'personality',
    'lukhas_ethics_guard': 'ethics_guard',
    'lukhas_awareness_protocol': 'awareness_protocol',
    'lukhas_brain': 'brain_core',
    'lukhas_id': 'identity_legacy',
    'lukhas_id_enhanced': 'identity_enhanced',
    'lukhas_lambda_id': 'lambda_identity',
    'lukhas_next_gen': 'next_gen',

    # File renames (tools/analysis/)
    'tools/analysis/_OPERATIONAL_SUMMARY.py': 'tools/analysis/operational_summary.py',
    'tools/analysis/_FUNCTIONAL_ANALYSIS.py': 'tools/analysis/functional_analysis.py',
    'tools/analysis/_WORKSPACE_STATUS_ANALYSIS.py': 'tools/analysis/workspace_status.py',
    'tools/analysis/_SECURITY_COMPLIANCE_GAP_ANALYSIS.py': 'tools/analysis/security_gap_analysis.py',
    'tools/analysis/_TARGETED_IMPORT_FIXER.py': 'tools/analysis/import_fixer.py',
}

def execute_renames():
    """Execute the rename plan"""
    workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas")

    for old_path, new_path in RENAME_MAPPINGS.items():
        old_full = workspace / old_path
        new_full = workspace / new_path

        if old_full.exists():
            print(f"Renaming: {old_path} → {new_path}")
            shutil.move(str(old_full), str(new_full))
        else:
            print(f"Skip (not found): {old_path}")
```

## 📊 Impact Analysis

### Benefits
1. **Consistency**: All modules follow snake_case convention
2. **Clarity**: No redundant prefixes (repo name already provides context)
3. **Simplicity**: Consolidated single-purpose files into cohesive modules
4. **OpenAI-style**: Clean, professional naming matching industry standards
5. **Discoverability**: Easier to find and understand module purposes

### Files Affected by Import Changes
- Approximately 150-200 files will need import updates
- Use automated script to update all `from lukhas_*` imports
- Update configuration files referencing old paths

## 🚀 Execution Order
1. Create backup of current structure
2. Execute directory renames
3. Execute file renames
4. Run import update script
5. Test all modules for import errors
6. Update documentation references

## ✅ Validation Checklist
- [ ] All `lukhas_` prefixes removed from directories
- [ ] All `_` prefixes removed from analysis tools
- [ ] Sparse modules consolidated into single files
- [ ] All imports updated across codebase
- [ ] Tests pass with new structure
- [ ] Documentation updated with new paths

---

This plan transforms the codebase into a clean, professional structure following OpenAI-inspired conventions while maintaining full functionality.
