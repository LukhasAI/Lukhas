---
status: active
type: linting-campaign
rule: F821-undefined-names
date: 2025-11-08
branch: t4/f821-scan-20251108
---

# F821 Undefined Names - Scan Results

## Executive Summary

**Total F821 violations:** 461 across 89 unique files
**Most common undefined names:** `oidc_api_requests_total` (17), `false` (17), `lukhasQuantumValidator` (10)
**Heuristic import candidates:** 1 file only (`scripts/generate_complete_inventory.py`)

## Top 10 Files by Issue Count

| Count | File | Category |
|-------|------|----------|
| 50 | `qi/engines/creativity/creative_q_expression.py` | Production - QI |
| 20 | `tools/module_schema_validator.py` | Tooling |
| 19 | `lukhas_website/lukhas/api/oidc.py` | Production - API |
| 16 | `qi/distributed_qi_architecture.py` | Production - QI |
| 14 | `matriz/consciousness/reflection/visionary_orchestrator.py` | Production - MATRIZ |
| 12 | `mcp-lukhas-sse/tests/test_mcp-lukhas-sse_unit.py` | Test |
| 12 | `qi/states/system_orchestrator.py` | Production - QI |
| 11 | `qi/post_quantum_crypto.py` | Production - QI |
| 11 | `tests/smoke/test_auth.py` | Test |
| 10 | `qi/systems/qi_entanglement.py` | Production - QI |

## Top Undefined Names Analysis

### Critical Issues (17 occurrences)
- **`oidc_api_requests_total`** - Prometheus metrics undefined (likely missing import)
- **`false`** - Literal typo (should be `False` in Python)

### Architectural Issues (10 occurrences)
- **`lukhasQuantumValidator`** - Class/module naming inconsistency
- **`app`** - Flask/FastAPI app instance undefined

### MCP-Related (9 occurrences)
- **`mcp`** - Model Context Protocol module undefined

### Common Typos/Errors
- **`SyntaxError: unindent does not`** (7) - Indentation syntax errors
- **`SyntaxError: Expected a statem`** (4) - Statement syntax errors

## Issue Categories

### 1. Missing Imports (Est. 150 issues)
Files referencing undefined classes/modules that need imports:
- `ΛQuantumEntanglement`, `ΛQuantumValidator`
- `QILikeState`, `QISecureSession`
- `MATRIZThoughtLoop`, `MATRIZProcessingContext`
- `VIVOXMemoryExpansion`

### 2. Typos & Literal Errors (Est. 50 issues)
- `false` → `False`
- `true` → `True`

### 3. Syntax Errors (Est. 20 issues)
- Indentation errors
- Statement syntax errors

### 4. Configuration/Metrics Issues (Est. 30 issues)
- Prometheus metrics undefined
- Settings/config objects undefined

### 5. Namespace/Naming Issues (Est. 211 issues)
- Inconsistent class naming (lukhasQuantumValidator vs ΛQuantumValidator)
- Missing module prefixes

## Strategic Approach

### Option A: Start with Heuristic Shard (LOW YIELD)
Only 1 file identified with simple import fixes:
- `scripts/generate_complete_inventory.py` (needs `from typing import Any`)

**Verdict:** Not worth separate campaign; fold into broader fix

### Option B: Target Top Files (HIGH IMPACT)
Focus on top 10 files (171 issues = 37% of total):

**Shard 1 (Production - High Impact):**
1. `qi/engines/creativity/creative_q_expression.py` (50) - Missing QI imports
2. `tools/module_schema_validator.py` (20) - Validation tooling
3. `lukhas_website/lukhas/api/oidc.py` (19) - API metrics/imports
4. `qi/distributed_qi_architecture.py` (16) - QI architecture
5. `matriz/consciousness/reflection/visionary_orchestrator.py` (14) - MATRIZ

**Shard 2 (Tests - Medium Impact):**
6. `mcp-lukhas-sse/tests/test_mcp-lukhas-sse_unit.py` (12) - MCP tests
7. `tests/smoke/test_auth.py` (11) - Auth smoke tests

**Shard 3 (Production - QI Systems):**
8. `qi/states/system_orchestrator.py` (12) - State management
9. `qi/post_quantum_crypto.py` (11) - Crypto
10. `qi/systems/qi_entanglement.py` (10) - Entanglement

### Option C: Category-Based Approach (SYSTEMATIC)

**Phase 1: Quick Wins (Est. 50 issues, 1-2 hrs)**
- Fix all `false` → `False` typos (17 issues)
- Fix all `true` → `True` typos (3 issues)
- Add simple typing imports where heuristic applies (30 issues)

**Phase 2: Prometheus Metrics (Est. 30 issues, 2-3 hrs)**
- Fix `oidc_api_requests_total` and similar metrics (17 issues)
- Add metrics imports to API modules (13 issues)

**Phase 3: Architecture Imports (Est. 200 issues, 5-8 hrs)**
- Fix QI module imports (80 issues)
- Fix MATRIZ module imports (50 issues)
- Fix VIVOX module imports (30 issues)
- Fix consciousness module imports (40 issues)

**Phase 4: Syntax Errors (Est. 20 issues, 3-5 hrs)**
- Fix indentation errors (11 issues)
- Fix statement syntax errors (9 issues)

## Recommended Execution Plan

### Immediate Actions (Today)
1. **Quick Win Batch:** Fix `false`/`true` typos globally (20 issues)
   ```bash
   # Automated find/replace with validation
   find . -name "*.py" -not -path "./.*" -exec sed -i '' 's/\bfalse\b/False/g' {} \;
   ruff check --select F821 --diff
   ```

2. **Metrics Import Batch:** Fix OIDC API metrics (19 issues in 1 file)
   - Review `lukhas_website/lukhas/api/oidc.py`
   - Add missing Prometheus imports
   - Test with `make smoke`

### This Week
3. **Top File Campaign:** Process top 5 production files (119 issues)
   - Use LibCST for safe import additions
   - Create dry-run patches per file
   - Manual review + commit

### Next Week
4. **Test File Sweep:** Fix test undefined names (50 issues)
   - MCP test imports
   - Auth test fixtures
   - Integration test dependencies

## Artifacts Generated

- **Raw scan:** `/tmp/ruff_f821.json` (7,841 lines)
- **Clean JSON:** `/tmp/ruff_f821_clean.json`
- **Summary:** `/tmp/ruff_f821_summary.json` (structured analysis)
- **Heuristic shard:** `/tmp/f821_first_shard.txt` (1 file only)
- **Scanner script:** `tools/ci/f821_scan.py` (prioritization tool)

## Success Criteria

- **Phase 1 Complete:** F821 < 400 (61 issues fixed)
- **Phase 2 Complete:** F821 < 350 (111 issues fixed)
- **Phase 3 Complete:** F821 < 150 (311 issues fixed)
- **Campaign Complete:** F821 < 50 (411 issues fixed, 89% reduction)

## Next Steps

**User Decision Required:**
1. Execute Quick Win Batch (false/true typos) now?
2. Start with Top File Campaign (creative_q_expression.py)?
3. Generate dry-run import inserter for heuristic cases?

---

**Generated:** 2025-11-08
**Branch:** t4/f821-scan-20251108
**Tools:** ruff 0.8.4, Python 3.9
