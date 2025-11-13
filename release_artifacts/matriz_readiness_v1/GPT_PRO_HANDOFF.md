# GPT-Pro Handoff Document - MATRIZ Flattening Audit

**Date:** 2025-11-03T13:50:00Z
**Status:** ✅ READY FOR GPT-PRO AUDIT (dry-run mode)
**Commit:** `f012a72cd` (matrix→matriz rename complete)

---

## ✅ Pre-Audit Verification Complete

All 21 required artifacts verified and present:
- ✅ Core planning documents (4 files)
- ✅ Configuration files (4 files)
- ✅ Scripts & tools (3 files)
- ✅ PR templates (5 files)
- ✅ Discovery artifacts (2 files)
- ✅ Reports & guides (7 files)
- ✅ Verification outputs (1 directory)

---

## 📋 Current State

### What's Been Completed

1. **✅ Preflight Checklist (11 steps)** - All passed with advisories
2. **✅ TODO-01** - Flatten map generated (49 candidates)
3. **✅ Matrix→MATRIZ Rename** - Cognitive nodes moved to correct directory
4. **✅ Import Analysis** - Dependencies identified and documented
5. **✅ Backup Created** - `backup/pre-flatten-2025-11-03-1316`
6. **✅ Git Committed** - All work saved (`f012a72cd`)

### Configuration Confirmed

```json
{
  "artifacts_dir": "release_artifacts/matriz_readiness_v1",
  "flatten_strategy": "shim-first",
  "dry_run": true,
  "max_pr_files": 25,
  "author": "Gonzalo Roberto Dominguez Marchan"
}
```

**Strategy:** `shim-first` (virtual flattening)

**Policy:**
- Reviewers: @gonzalordm
- Required checks: verify-syntax-zero, pytest-matriz, ruff
- Shim deprecation: 30 days

---

## ⚠️ Known Advisories (RESOLVED)

### 1. Black/Ruff Not in PATH ✅ RESOLVED
**Status:** ✅ Installed in venv
**Versions:**
- Black: 25.9.0
- Ruff: 0.14.2
- LibCST: Installed

**Verification:**
```bash
source .venv/bin/activate
which black  # /Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/bin/black
which ruff   # /Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/bin/ruff
```

### 2. No GPG Signing Key
**Impact:** Cannot create signed tags yet (optional)
**Fix:** Configure if needed: `git config user.signingkey <KEY_ID>`
**Status:** Non-blocking for dry-run and apply mode

### 3. Archive/Quarantine Compile Errors
**Impact:** None - these directories excluded from milestone
**Status:** Expected and documented

### 4. Archive Recovery Assessment ✅ NEW
**Status:** ✅ Audit completed
**Document:** `ARCHIVE_RECOVERY_PRIORITY.md`
**Key Finding:** 8 valuable modules in `archive/lanes_experiment/` for memory systems research
**Action Required:** GPT-Pro should audit Priority 1 modules for restoration

---

## 🎯 What GPT-Pro Should Do (Dry-Run Audit)

### Phase 1: Full Audit

**Read these files first:**
1. `matriz_readiness_report.md` - Executive summary
2. `flatten_map.csv` - 49 candidates (NOTE: includes phantom files)
3. `CRITICAL_FINDING_RESOLUTION.md` - Known issues
4. `MATRIX_MATRIZ_RENAME_ANALYSIS.md` - Rename details
5. `MISSING_FILES_RECOVERY_PLAN.md` - File mapping
6. **`ARCHIVE_RECOVERY_PRIORITY.md`** - Archive audit (NEW)

**Critical Issues to Address:**
- flatten_map.csv contains paths to non-existent files
- 15 out of 49 files are phantoms (renamed or deleted)
- See `FILE_VALIDATION_REPORT.txt` for details
- **NEW:** 8 valuable modules in `archive/lanes_experiment/` need assessment

**Tasks:**
1. Run file existence validation on flatten_map.csv
2. Generate corrected flatten_map with actual file paths
3. **Audit archive/lanes_experiment/ for restoration** (Priority 1 modules)
4. Identify top 5-10 candidates for flattening (files that exist)
5. Assess import dependencies for real files
6. Create risk assessment for each candidate
7. **Recommend which archive modules should be restored before flattening**

### Phase 2: Generate Dry-Run Artifacts

**Produce these files (DO NOT APPLY):**

1. **`flatten_map_corrected.csv`**
   - Only files that exist
   - Corrected paths (labs/core/matriz/ not matrix/)
   - Validated import counts

2. **`full_audit.md`**
   - Executive summary
   - Top 5 risks identified
   - Top 5 recommendations
   - Candidate prioritization

3. **`patches/` directory**
   - Dry-run patches for top 3-5 candidates
   - Show both shim and physical move approaches
   - Include exact `rewrite_imports_libcst.py` commands

4. **`verification/verification_summary.json`**
   ```json
   {
     "compile_ok": true/false,
     "smoke_tests_ok": true/false,
     "ruff_errors_count": N,
     "candidates_analyzed": N,
     "candidates_with_issues": [...]
   }
   ```

5. **`todo_list_full.md`**
   - Updated TODO list with corrected candidates
   - Exact commands for each step
   - Expected outputs

6. **`ARCHIVE_RECOVERY_RECOMMENDATIONS.md`** (NEW)
   - Assessment of Priority 1 archive modules
   - Restoration recommendations (RESTORE / DOCUMENT / ARCHIVE)
   - Decision matrix for each module
   - Updated flatten_map.csv if modules restored

### Phase 3: Return Executive Summary

**Before making any patches, return:**

1. Top 5 risks discovered
2. Top 5 recommendations for safe flattening
3. Suggested candidate order (safest → riskiest)
4. Any blockers or manual review items
5. Estimated timeline per candidate

---

## 🚀 How to Run GPT-Pro Audit

### Step 1: Confirm Dry-Run Mode

```bash
jq .dry_run release_artifacts/matriz_readiness_v1/gptpro_config.json
# Expected output: true
```

### Step 2: (Optional) Activate Venv for Better Verification

```bash
# If .venv exists
source .venv/bin/activate

# Install dev dependencies
python3 -m pip install black ruff libcst pytest
```

### Step 3: Copy GPT-Pro Prompt to ChatGPT Desktop

**Open:** `release_artifacts/matriz_readiness_v1/GPT_PRO_PROMPT.md`

**Paste the entire prompt into ChatGPT Desktop** (GPT-Pro session)

**Wait for:** GPT-Pro to produce all dry-run artifacts and executive summary

### Step 4: Review GPT-Pro Output

**Check these files:**
- `full_audit.md` - Executive summary and recommendations
- `flatten_map_corrected.csv` - Validated candidate list
- `patches/` - Example patches (dry-run only)
- `verification/verification_summary.json` - Health check results

**Validate:**
- [ ] All recommended files actually exist
- [ ] Import counts are realistic (not all zeros)
- [ ] Risk assessment makes sense
- [ ] No high-risk items flagged as low-risk

---

## 🔄 After Dry-Run Review

### If Dry-Run Looks Good (Recommended Path)

1. **Review the audit report personally**
2. **Decide which candidates to proceed with**
3. **Update gptpro_config.json:**
   ```bash
   jq '.dry_run=false' release_artifacts/matriz_readiness_v1/gptpro_config.json > /tmp/cfg
   mv /tmp/cfg release_artifacts/matriz_readiness_v1/gptpro_config.json
   ```
4. **Commit the change:**
   ```bash
   git add release_artifacts/matriz_readiness_v1/gptpro_config.json
   git commit -m "chore(gpt): enable apply mode after dry-run audit approval"
   ```
5. **Re-run GPT-Pro with apply mode** (creates actual PRs)

### If Issues Found (Alternative Path)

1. **Document the issues** in a new file
2. **Update flatten_map.csv** based on GPT-Pro findings
3. **Re-run preflight** if major changes needed
4. **Try dry-run again**

---

## 🎓 T4 Checklist Before Apply Mode

Before flipping `dry_run=false`, confirm:

- [ ] `full_audit.md` reviewed for high-risk items
- [ ] Top 5 patches examined with exact import rewrite mappings
- [ ] `verification/compile_log.txt` shows active code compiles
- [ ] `verification/smoke_test_logs.txt` acceptable (or failures documented)
- [ ] Venv activated OR black/ruff installed globally
- [ ] (Optional) GPG signing configured if you want signed tags
- [ ] flatten_map.csv updated with corrected paths (no phantoms)

---

## 🔍 Known Issues GPT-Pro Must Address

### Issue 1: Phantom Files in flatten_map.csv

**15 out of 49 files don't exist:**
- 7 MATRIZ nodes deleted (attention, risk, intent, action, vision)
- Several files renamed from candidate/ → labs/
- Some utilities consolidated

**GPT-Pro action:** Regenerate flatten_map with only existing files

### Issue 2: Import Count Heuristic Failed

**All candidates show import_count=0:**
- Discovery heuristic missed actual dependencies
- Manual verification found 9+ active files for some nodes

**GPT-Pro action:** Run proper import analysis per file

### Issue 3: Matrix → MATRIZ Naming

**Status:** ✅ FIXED in commit `f012a72cd`
- All MATRIZ cognitive nodes now in `labs/core/matriz/nodes/`
- All imports updated
- No action needed from GPT-Pro (already done)

---

## 📁 Artifact Locations

**All artifacts:** `release_artifacts/matriz_readiness_v1/`

**Key files for GPT-Pro:**
- `GPT_PRO_PROMPT.md` - Full prompt (paste this)
- `CRITICAL_FINDING_RESOLUTION.md` - Known issues
- `flatten_map.csv` - Current candidates (needs correction)
- `FILE_VALIDATION_REPORT.txt` - Which files are phantom
- `MISSING_FILES_RECOVERY_PLAN.md` - Path mapping
- **`ARCHIVE_RECOVERY_PRIORITY.md`** - Archive audit (NEW)

---

## 🔒 Rollback Capability

**Backup branch:** `backup/pre-flatten-2025-11-03-1316`

**Rollback commands:**
```bash
git reset --hard backup/pre-flatten-2025-11-03-1316
git push -f origin main
```

**Verification:**
```bash
git log -1 backup/pre-flatten-2025-11-03-1316
git diff main backup/pre-flatten-2025-11-03-1316
```

---

## ✅ Final Verification Before Handoff

```bash
# Run the comprehensive checklist
bash /tmp/gptpro_pre_audit_checklist.sh

# Expected output: "✅ ALL CHECKS PASSED - Ready for GPT-Pro audit"
```

**Result:** ✅ ALL CHECKS PASSED (21/21)

---

## 🎯 Success Criteria for GPT-Pro Audit

GPT-Pro audit succeeds if it produces:

1. ✅ Corrected flatten_map.csv with only existing files
2. ✅ Realistic import dependency counts
3. ✅ Risk assessment that identifies actual high-risk items
4. ✅ Top 3-5 patches that demonstrate approach
5. ✅ Executive summary with actionable recommendations
6. ✅ Verification summary showing compile/test status

---

## 📞 Next Steps After GPT-Pro Completes

1. **You review** the `full_audit.md`
2. **We discuss** the top 5 risks and recommendations
3. **You decide** which candidates to flatten first
4. **We flip** to apply mode (`dry_run=false`)
5. **GPT-Pro creates** actual PRs with patches
6. **You review and merge** each PR after verification

---

**Status:** 🟢 READY - All systems GO for GPT-Pro dry-run audit

**Last Updated:** 2025-11-03T13:51:00Z
**Author:** Claude Code (T4 / 0.01% Agent)
**Backup:** `backup/pre-flatten-2025-11-03-1316`
