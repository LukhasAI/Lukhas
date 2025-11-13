# Archive Recovery Priority List
## MATRIZ Flattening Pre-Audit - Valuable Modules in archive/

**Date:** 2025-11-03T14:01:00Z
**Purpose:** Identify high-value modules in archive/ that should be restored before flattening
**Total Archive Size:** 188 Python files, 245 directories

---

## Priority 1: CRITICAL - Must Review Before Flattening

### 1. lanes_experiment (Memory Systems Research)
**Location:** `archive/lanes_experiment/lukhas_acceptance_scaffold/`
**Python Files:** 8 files
**Status:** 🔴 HIGH VALUE - Memory system variants and research

**Key Modules:**
- `memory/core/colony_memory_validator.py` - Colony-based memory validation
- `memory/causal/fold_lineage_tracker.py` - Causal fold tracking
- `memory/proteome/symbolic_proteome.py` - Symbolic proteome system
- `memory/hippocampal/pattern_separator.py` - Hippocampal-inspired pattern separation
- `memory/fold_system/fold_lineage_tracker.py` - Fold lineage management
- `memory/systems/hierarchical_data_store.py` - Hierarchical storage
- `memory/systems/tier_system.py` - Tiered memory architecture
- `memory/systems/dream_trace_linker.py` - Dream-memory integration

**Recovery Action:**
- **Option A:** Restore to `candidate/memory/` for evaluation
- **Option B:** Document as research artifacts (if superseded by current implementation)
- **Decision Point:** Compare with current `memoria/` and `candidate/memory/` systems

**GPT-Pro Task:** Audit these files for unique functionality not present in active codebase

---

### 2. scattered_root_files (Infrastructure Utilities)
**Location:** `archive/scattered_root_files/`
**Python Files:** 5 files
**Status:** 🟡 MEDIUM VALUE - Infrastructure and validation

**Key Modules:**
- `lukhas_paths.py` - Path resolution utilities
- `non_core_module_analysis.py` - Module analysis tools
- `public_api.py` - Public API definitions
- `test_non_core_modules.py` - Non-core module tests
- `validate_auth_implementation.py` - Auth validation

**Recovery Action:**
- Move to `tools/` or integrate into existing infrastructure
- Check if functionality exists in current `core/` modules

**GPT-Pro Task:** Check for duplicate functionality in active codebase

---

### 3. lukhas_website_original_working (Production Website Archive)
**Location:** `archive/lukhas_website_original_working/`
**Type:** Next.js/React application
**Status:** 🟢 PRESERVED - Working production website backup

**Contains:**
- `app/`, `components/`, `hooks/` - React components
- `lib/`, `locales/`, `prisma/` - Backend and i18n
- `public/`, `scripts/`, `styles/` - Static assets
- `templates/`, `tests/`, `tools/` - Development infrastructure

**Recovery Action:**
- Keep as-is (production backup)
- Do NOT flatten or modify
- Reference for website rebuilds

**GPT-Pro Task:** Exclude from flattening scope (not Python modules)

---

## Priority 2: REVIEW - Potential Value

### 4. quarantine_2025-10-26 (Syntax Error Files)
**Python Files:** 135 files (largest archive)
**Status:** ⚠️ LOW PRIORITY - Known syntax errors

**Action:** Excluded from v0.9.1-syntax-zero milestone
**Recovery:** Manual review required for each file (out of scope for MATRIZ flattening)

---

### 5. root_files_2025_10_03 (Old Root Cleanup)
**Python Files:** 9 files
**Status:** 🟡 MEDIUM VALUE - Historical utilities

**Key Files:**
- `metrics.py`, `branding_bridge.py`, `smart_syntax_fixer.py`
- `flags.py`, `client.py`, `ai_client.py`, `main.py`

**Action:** Check if superseded by current implementations

---

### 6. delegation_reports (Ruff Report Generator)
**Python Files:** 1 file
**Status:** 🟢 UTILITY - Report generation tool

**File:** `generate_ruff_delegation_reports.py`

**Action:** Keep as development utility (may be useful for GPT-Pro audit)

---

## Priority 3: ARCHIVED - Keep for History

- **dream_2025-10-26** (7 files) - Old dream system version
- **dreams_2025-10-26** (4 files) - Dreams variant
- **dreamweaver_helpers_bundle_2025-10-26** (3 files) - Helper utilities
- **final_sweep_batch_2025-10-26** (3 files) - Cleanup batch
- **transmission_bundle** (2 files) - Transmission utilities
- **website_v1** (3 files) - Old website version
- **tests_legacy** (2 files) - Legacy tests

**Action:** Keep archived unless specific functionality needed

---

## GPT-Pro Audit Instructions

### Phase 1: Archive Module Analysis (30 minutes)

For each Priority 1 module, determine:

1. **Uniqueness Check:**
   ```bash
   # Compare archived module with active codebase
   rg "<module_function_name>" --type py -g "!archive/*"
   ```

2. **Import Analysis:**
   ```bash
   # Check if any active code imports from archive/
   rg "from archive\." --type py
   rg "import archive\." --type py
   ```

3. **Functionality Gap Analysis:**
   - Does archived module provide unique functionality?
   - Is it superseded by current implementation?
   - Should it be restored to `candidate/` lane?

### Phase 2: Recovery Recommendations

Create `ARCHIVE_RECOVERY_RECOMMENDATIONS.md` with:

**For each Priority 1 module:**
- ✅ **RESTORE** - Unique functionality, should return to active development
- 📋 **DOCUMENT** - Superseded but valuable reference implementation
- ❌ **ARCHIVE** - No unique value, keep archived

**Decision Matrix:**
```
IF unique_functionality AND compiles_without_errors:
    → Restore to candidate/ lane
ELIF unique_functionality AND has_syntax_errors:
    → Flag for manual restoration (out of scope)
ELIF superseded_by_active_code:
    → Document in ARCHIVE_RECOVERY_RECOMMENDATIONS.md
ELSE:
    → Keep archived
```

### Phase 3: Update flatten_map.csv

If modules are restored from archive/:
- Regenerate discovery with new file paths
- Add restored modules to flatten_map.csv
- Prioritize newly restored modules in flattening sequence

---

## Statistics Summary

| Archive Section | Python Files | Priority | Action |
|-----------------|--------------|----------|--------|
| **lanes_experiment** | 8 | 🔴 CRITICAL | Audit for recovery |
| **scattered_root_files** | 5 | 🟡 MEDIUM | Check for duplicates |
| **lukhas_website_original_working** | 0 (React) | 🟢 PRESERVE | Exclude from flattening |
| **quarantine_2025-10-26** | 135 | ⚠️ LOW | Out of scope |
| **root_files_2025_10_03** | 9 | 🟡 MEDIUM | Check if superseded |
| **Other archives** | 31 | 🟢 ARCHIVED | Keep for history |
| **TOTAL** | **188** | - | - |

---

## Immediate Actions Before GPT-Pro Audit

### Required:
1. ✅ Document archive recovery priorities (this file)
2. ⏳ Install Black/Ruff/LibCST in venv (Advisory #1)
3. ⏳ Update GPT_PRO_HANDOFF.md with archive audit instructions

### Optional (GPT-Pro will handle):
- Detailed module-by-module comparison
- Restore decisions for Priority 1 modules
- Updated flatten_map.csv if restorations occur

---

**Report Generated:** 2025-11-03T14:01:00Z
**Author:** Claude Code (T4 Agent)
**Next Action:** Resolve Known Advisories, then run GPT-Pro audit with archive context
