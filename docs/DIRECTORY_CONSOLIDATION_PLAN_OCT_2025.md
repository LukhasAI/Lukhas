# Directory Consolidation Plan - October 26, 2025

**Status**: Analysis Complete, Ready for Execution
**Impact**: High (will affect imports, configs, and test paths)
**Estimated Time**: 2-3 hours
**Risk Level**: Medium (requires careful reference updates)

---

## Executive Summary

Analysis identified **8 directory consolidation opportunities** that will:
- Eliminate duplicate/redundant directory structures
- Fix macOS case-sensitivity issues (MATRIZ/matriz)
- Consolidate scattered MCP server implementations
- Clean up legacy "final_sweep" batch directory
- Standardize config and documentation locations

**Total Space to Reclaim**: ~150MB (after consolidation and archive)
**Directories to Consolidate**: 13 → 6
**Files Affected**: ~400 files to move/update
**References to Update**: ~204+ code references

---

## 1. MATRIZ / matriz Case-Sensitivity Issue

### Problem:
```bash
$ ls -lid MATRIZ matriz
16291479 drwxr-x---@ 56 agi_dev  staff  1792 Oct 26 08:29 MATRIZ
16291479 drwxr-x---@ 56 agi_dev  staff  1792 Oct 26 08:29 matriz
```

**Same inode!** macOS case-insensitive filesystem shows both names for the SAME directory.

### Analysis:
- **32,934 files** appear in both `MATRIZ/` and `matriz/`
- They are literally the SAME directory viewed through different case names
- This creates confusion and import ambiguity
- Python imports use `from MATRIZ.` and `from matriz.` interchangeably

### Root Cause:
Git on macOS case-insensitive filesystem (APFS) allows both names to exist in repository metadata, but filesystem sees them as identical.

### Decision: **Keep MATRIZ (uppercase)**
**Rationale**:
- Official branding uses "MATRIZ" (uppercase)
- More references in codebase use uppercase
- Aligns with LUKHAS naming convention (all caps for major components)

### Consolidation Strategy:
1. **DO NOT use `git mv`** (will fail - same inode)
2. Use filesystem-level fix:
   ```bash
   # Create temp directory
   git mv MATRIZ MATRIZ_temp
   git commit -m "temp: prepare for case fix"

   # Rename to final name
   git mv MATRIZ_temp MATRIZ
   git commit -m "fix(matriz): standardize to uppercase MATRIZ"
   ```

### References to Update:
Search for: `from matriz.`, `import matriz`, `matriz/`
Replace with: `from MATRIZ.`, `import MATRIZ`, `MATRIZ/`

**Estimated References**: ~500+ import statements

### Test Impact:
- All imports in tests using `matriz.` need update
- Test collection errors may include matriz/MATRIZ confusion
- Module registry paths need standardization

---

## 2. Governance Directories

### Current State:
```
governance/          - 115 files, 1.2KB directory size
governance_extended/ - 16 files, 512B directory size
```

### Analysis:

#### governance/ (Main module):
- **Purpose**: Core governance, ethics, guardian system
- **Key files**:
  - `audit_trail.py` (37KB)
  - `guardian_reflector.py` (29KB)
  - `colony_memory_validator.py` (26KB)
  - `guardian_policies.py` (22KB)
- **Subdirs**: ethics/, guardian/, consent/, identity/, tests/
- **Lane**: L2 (Integration)
- **Status**: Production-ready ✅

#### governance_extended/ (Extension module):
- **Purpose**: Extended governance features (audit logger, policy manager, compliance hooks)
- **Key files**:
  - `audit_logger/` - Audit logging extensions
  - `policy_manager/` - Policy management
  - `compliance_hooks/` - Compliance integration
- **Lane**: L2 (Integration)
- **Status**: Active development 🔧

### Decision: **KEEP BOTH (they serve different purposes)**

**Rationale**:
- `governance/` = Core guardian/ethics system
- `governance_extended/` = Extended audit/compliance features
- 204 references to `governance_extended` in codebase
- Separate module manifests and test suites

### Alternative: Merge as Subdirectory
```
governance/
├── core/          (current governance/ content)
├── extended/      (current governance_extended/ content)
└── ...
```

**Recommendation**: **Keep separate for now** - they have distinct responsibilities and module boundaries.

---

## 3. Doc / Docs Directories

### Current State:
```
doc/   - 19 files, 416B directory size - "LUKHAS doc module"
docs/  - 2,021 files, 7.7KB directory size - Main documentation
```

### Analysis:

#### doc/ (Minimal stub module):
- **Purpose**: Appears to be auto-generated module stub
- **Content**:
  - README.md: "LUKHAS doc module implementing specialized doc functionality with **0 components**"
  - claude.me, lukhas_context.md, module.manifest.lock.json
  - Empty tests/, config/, schema/ directories
- **Lane**: Unknown (stub)
- **Status**: WIP stub (no actual implementation)

#### docs/ (Real documentation):
- **Purpose**: Comprehensive LUKHAS documentation
- **Content**:
  - Architecture docs
  - API references
  - Development guides
  - GA deployment runbooks
  - Dependency audits
  - RC soak test results
  - MATRIZ guides
  - Module documentation
- **Status**: Active, production-ready ✅

### Decision: **ARCHIVE doc/, KEEP docs/**

**Rationale**:
- `doc/` is an empty stub with 0 components
- `docs/` is the real, comprehensive documentation
- No code references to `doc/` module (only venv references)
- `doc/` serves no purpose

### Consolidation Strategy:
```bash
git mv doc/ archive/doc_stub_2025-10-26/
# Update any references (unlikely to exist)
```

---

## 4. Config / Configs Directories

### Current State:
```
config/  - 199 files, 2.9KB directory size - Main configuration
configs/ - 6 files, 256B directory size - Minimal configs
```

### Analysis:

#### config/ (Main configuration):
- **Purpose**: Primary system configuration
- **Content**:
  - Agent orchestration configs
  - AGI consciousness configs
  - Bio/QI radar configs
  - Brain integration configs
  - CI configs
  - Alert rules
  - Claude Desktop config
  - Cognitive architecture
  - And ~180 more files
- **Lane**: Core system config
- **Status**: Production ✅

#### configs/ (Minimal subset):
- **Purpose**: Appears to be subset of runtime configs
- **Content**:
  - `legacy_imports.yml`
  - `quotas.yaml`
  - `star_rules.json`
  - `observability/` subdir
  - `policy/` subdir
  - `runtime/` subdir
- **Lane**: Unknown
- **Status**: Unclear purpose

### Decision: **MERGE configs/ → config/**

**Rationale**:
- All 6 files in `configs/` logically belong in `config/`
- `config/` is the standard location for all configurations
- No reason to have separate `configs/` directory

### Consolidation Strategy:
```bash
# Move contents to config/
git mv configs/legacy_imports.yml config/
git mv configs/quotas.yaml config/
git mv configs/star_rules.json config/
git mv configs/observability config/
git mv configs/policy config/
git mv configs/runtime config/

# Remove empty configs/
rmdir configs/

# Update references
grep -r "configs/" --include="*.py" --include="*.yaml" | # find references
# Update to "config/"
```

---

## 5. MCP Server Directories

### Current State:
```
mcp-lukhas-sse/  - 8,745 files, 149MB - ChatGPT SSE connector
mcp-server/      - 26 files, 76KB - Production deployment scripts
mcp-servers/     - 36,546 files, 456MB - 5 MCP servers (consciousness, constellation, etc.)
mcp_servers/     - 26 files, 232KB - Python package for MCP servers
```

### Analysis:

#### mcp-lukhas-sse/ (ChatGPT SSE Connector):
- **Purpose**: Server-Sent Events connector for ChatGPT integration
- **Content**: Standalone SSE server with Auth0, OAuth, bearer token support
- **Status**: Production-ready ✅
- **Size**: 149MB (includes venv/, node_modules/)
- **Keep**: Yes (separate deployment)

#### mcp-server/ (Deployment Scripts):
- **Purpose**: Production deployment scripts and systemd services
- **Content**:
  - `deploy-production.sh`
  - `cloudflared-lukhas-mcp.service`
  - `mcp-fs-lukhas.service`
  - `verify-bearer-token.sh`
  - `production-status.sh`
- **Status**: Production deployment ✅
- **Keep**: Yes (deployment infrastructure)

#### mcp-servers/ (5 MCP Servers):
- **Purpose**: Collection of 5 MCP servers
- **Content**:
  - `lukhas-consciousness-mcp/` - Consciousness server
  - `lukhas-constellation-mcp/` - Constellation framework server
  - `lukhas-devtools-mcp/` - Development tools server
  - `lukhas-memory-mcp/` - Memory system server
  - `mcp-fs-lukhas/` - Filesystem server
  - `start-chatgpt-servers.sh` - Startup script
- **Status**: Production ✅
- **Size**: 456MB (includes all node_modules/)
- **Keep**: Yes (main MCP server collection)

#### mcp_servers/ (Python Package):
- **Purpose**: Python package implementing MCP server protocol
- **Content**:
  - `lukhas_mcp_server.py` - Main server implementation
  - `lukhas_consciousness/` - Consciousness integration
  - `identity/` - Identity management
  - Tests, docs, config
- **Status**: Core Python implementation
- **Keep**: Yes (Python package)

### Decision: **KEEP ALL (they serve different purposes)**

**Rationale**:
- **mcp-lukhas-sse**: Standalone SSE connector (separate deployment)
- **mcp-server**: Deployment scripts (infrastructure)
- **mcp-servers**: Collection of 5 servers (main server collection)
- **mcp_servers**: Python package (importable library)

### Alternative: Reorganize Under mcp/
```
mcp/
├── servers/           (current mcp-servers/ - 5 servers)
├── sse_connector/     (current mcp-lukhas-sse/)
├── deployment/        (current mcp-server/)
└── python_package/    (current mcp_servers/)
```

**Recommendation**: **Keep separate for now** - each has distinct purpose and deployment model.

**Future Consideration**: Consolidate under `mcp/` directory in next major refactor.

---

## 6. Eval Directories

### Current State:
```
eval_runs/ - 23 files - Evaluation run results
evals/     - (empty or minimal) - Evaluation definitions
```

### Analysis:

#### eval_runs/:
- **Purpose**: Results and outputs from evaluation runs
- **Content**: Evaluation run data, metrics, results
- **Status**: Active data directory

#### evals/:
- **Purpose**: Evaluation test definitions
- **Content**: Minimal or empty
- **Status**: Unclear

### Decision: **INVESTIGATE AND MERGE**

**Consolidation Strategy**:
```bash
# Check contents
ls -la evals/
find evals/ -type f

# If empty or minimal:
git mv eval_runs/ evaluations/
# OR
# If both have content:
mkdir -p evaluations/runs
mkdir -p evaluations/definitions
git mv eval_runs/* evaluations/runs/
git mv evals/* evaluations/definitions/
```

---

## 7. Dream Directories

### Current State:
```
dream/                      - (minimal)
dreams/                     - (minimal)
dreamweaver_helpers_bundle/ - Helper utilities
```

### Analysis:

#### dream/:
- **Purpose**: Dream synthesis module (likely empty stub)
- **Content**: Minimal or empty
- **Lane**: Consciousness research

#### dreams/:
- **Purpose**: Dream data or results
- **Content**: Minimal or empty
- **Lane**: Consciousness research

#### dreamweaver_helpers_bundle/:
- **Purpose**: Helper utilities for dream synthesis
- **Content**: Bundle of dream-related utilities
- **Lane**: Consciousness research

### Decision: **CONSOLIDATE INTO SINGLE DREAM MODULE**

**Consolidation Strategy**:
```bash
# Create unified dream module
mkdir -p labs/consciousness/dream/synthesis
mkdir -p labs/consciousness/dream/helpers
mkdir -p labs/consciousness/dream/results

# Move contents
git mv dream/* labs/consciousness/dream/synthesis/
git mv dreams/* labs/consciousness/dream/results/
git mv dreamweaver_helpers_bundle/* labs/consciousness/dream/helpers/

# Clean up old directories
rmdir dream dreams dreamweaver_helpers_bundle
```

**Rationale**:
- All dream-related functionality belongs in consciousness research
- `labs/consciousness/dream/` already exists (seen in earlier analysis)
- Consolidates scattered dream components

---

## 8. Final_Sweep Directory

### Current State:
```
final_sweep/ - 17 files - "BATCH-CODEX-CLEANUP-005" artifacts
```

### Analysis:

#### final_sweep/:
- **Purpose**: Artifacts from BATCH-CODEX-CLEANUP-005 Codex batch
- **Content**:
  - `BATCH-CODEX-CLEANUP-005.md` - Batch definition
  - README.md, claude.me, lukhas_context.md
  - config/, docs/, tests/, schema/ - All minimal/empty
- **Status**: Legacy batch artifacts
- **Lane**: Cleanup batch (completed)

### Decision: **ARCHIVE (legacy batch artifacts)**

**Rationale**:
- This appears to be artifacts from a completed Codex cleanup batch
- No production code dependencies
- Historical interest only

**Consolidation Strategy**:
```bash
git mv final_sweep/ archive/final_sweep_batch_2025-10-26/
```

---

## Consolidation Execution Plan

### Phase 1: Low-Risk Quick Wins (30 minutes)

#### 1.1 Archive doc/ stub
```bash
git mv doc/ archive/doc_stub_2025-10-26/
git commit -m "chore(structure): archive empty doc/ module stub"
```

#### 1.2 Archive final_sweep/
```bash
git mv final_sweep/ archive/final_sweep_batch_2025-10-26/
git commit -m "chore(structure): archive completed final_sweep batch artifacts"
```

#### 1.3 Merge configs/ → config/
```bash
git mv configs/legacy_imports.yml config/
git mv configs/quotas.yaml config/
git mv configs/star_rules.json config/
git mv configs/observability config/
git mv configs/policy config/
git mv configs/runtime config/
rmdir configs/
git commit -m "chore(structure): consolidate configs/ into config/"
```

### Phase 2: Eval and Dream Consolidation (30 minutes)

#### 2.1 Investigate and consolidate eval directories
```bash
# First, analyze contents
ls -laR evals/ eval_runs/

# Then consolidate based on findings
# (commands depend on what's found)
```

#### 2.2 Consolidate dream directories
```bash
mkdir -p labs/consciousness/dream/{synthesis,helpers,results}
git mv dream/* labs/consciousness/dream/synthesis/ 2>/dev/null || true
git mv dreams/* labs/consciousness/dream/results/ 2>/dev/null || true
git mv dreamweaver_helpers_bundle/* labs/consciousness/dream/helpers/ 2>/dev/null || true
rmdir dream dreams dreamweaver_helpers_bundle 2>/dev/null || true
git commit -m "chore(structure): consolidate dream modules into labs/consciousness/dream"
```

### Phase 3: MATRIZ Case-Sensitivity Fix (45 minutes)

**CRITICAL**: This requires careful handling due to case-insensitive filesystem.

#### 3.1 Prepare case fix
```bash
# Create temporary name
git mv MATRIZ MATRIZ_temp
git commit -m "temp: prepare MATRIZ for case standardization"
git push origin main
```

#### 3.2 Apply final name
```bash
# Rename to uppercase (canonical)
git mv MATRIZ_temp MATRIZ
git commit -m "fix(matriz): standardize to uppercase MATRIZ directory name

- Resolves macOS case-insensitive filesystem ambiguity
- MATRIZ and matriz were same inode (16291479)
- Standardizes to uppercase MATRIZ (official branding)
- All imports should use 'from MATRIZ.' going forward"
git push origin main
```

#### 3.3 Update import statements
```bash
# Find all lowercase matriz imports
grep -r "from matriz\." --include="*.py" . | wc -l
grep -r "import matriz" --include="*.py" . | wc -l

# Create batch update script
cat > /tmp/fix_matriz_imports.sh <<'EOF'
#!/bin/bash
find . -name "*.py" -type f -exec sed -i '' 's/from matriz\./from MATRIZ./g' {} +
find . -name "*.py" -type f -exec sed -i '' 's/import matriz /import MATRIZ /g' {} +
EOF

chmod +x /tmp/fix_matriz_imports.sh
/tmp/fix_matriz_imports.sh

git commit -am "fix(imports): update all matriz imports to MATRIZ (uppercase)"
```

### Phase 4: Update References and Documentation (30 minutes)

#### 4.1 Update Makefile references
```bash
# Check for references to old directories
grep -E "configs/|doc/|final_sweep/|^matriz" Makefile

# Update as needed
```

#### 4.2 Update test paths
```bash
# Update pytest paths
grep -r "configs/" tests/ --include="*.py"
# Update to config/
```

#### 4.3 Update documentation
```bash
# Update MODULE_INDEX.md
# Update README.md
# Update REPOSITORY_STATE_2025-10-26.md
```

#### 4.4 Regenerate module registry
```bash
python3 scripts/generate_meta_registry.py
git add artifacts/module.registry.json
git commit -m "chore(registry): update after directory consolidation"
```

---

## Testing Strategy

### Before Consolidation:
```bash
# Snapshot current test results
make smoke > /tmp/pre_consolidation_smoke.txt
python3 -m pytest tests/ --collect-only 2>&1 | tee /tmp/pre_consolidation_collection.txt
```

### After Each Phase:
```bash
# Verify smoke tests still pass
make smoke

# Check test collection
python3 -m pytest tests/ --collect-only 2>&1 | head -50

# Verify imports work
python3 -c "import MATRIZ; print('MATRIZ import OK')"
python3 -c "from MATRIZ.consciousness import *; print('MATRIZ.consciousness OK')"
```

### After All Consolidation:
```bash
# Full smoke test
make smoke

# Check test collection errors decreased
python3 -m pytest tests/ --collect-only 2>&1 | grep -c "ERROR"
# Should be < 218 (current baseline)

# Verify no new import errors
make lint | grep ImportError
```

---

## Reference Update Checklist

### Code Files:
- [ ] Update `from matriz.` → `from MATRIZ.`
- [ ] Update `import matriz` → `import MATRIZ`
- [ ] Update `configs/` → `config/`
- [ ] Update `doc/` → `docs/`

### Configuration Files:
- [ ] Update paths in `config/*.yaml`
- [ ] Update paths in `pyproject.toml`
- [ ] Update paths in `setup.py` (if exists)
- [ ] Update paths in `.gitignore`

### Test Files:
- [ ] Update test import paths
- [ ] Update test data paths
- [ ] Update conftest.py paths

### Documentation:
- [ ] Update MODULE_INDEX.md
- [ ] Update README.md
- [ ] Update architecture docs
- [ ] Update API docs
- [ ] Update claude.me context files

### CI/CD:
- [ ] Update GitHub Actions workflows
- [ ] Update Makefile targets
- [ ] Update deployment scripts
- [ ] Update Docker configurations

---

## Risk Assessment

### High Risk:
1. **MATRIZ case fix** - Could break all consciousness/cognitive imports
   - **Mitigation**: Batch update all imports, thorough testing
   - **Rollback**: Revert commits, restore lowercase imports

### Medium Risk:
2. **configs/ → config/** - Could break config loading
   - **Mitigation**: Update references before move
   - **Rollback**: Simple git revert

3. **Dream consolidation** - Could affect consciousness research
   - **Mitigation**: Check for active development first
   - **Rollback**: Restore from archive

### Low Risk:
4. **doc/ archive** - Empty stub, no dependencies
5. **final_sweep/ archive** - Completed batch, historical only

---

## Expected Outcomes

### Directory Structure After Consolidation:
```
Before: 13 directories
- governance, governance_extended (2)
- doc, docs (2)
- config, configs (2)
- MATRIZ, matriz (2 - same!)
- eval_runs, evals (2)
- dream, dreams, dreamweaver_helpers_bundle (3)

After: 6 directories
- governance, governance_extended (kept both - different purposes)
- docs (1 - doc archived)
- config (1 - configs merged)
- MATRIZ (1 - case standardized)
- evaluations (1 - evals merged)
- labs/consciousness/dream (1 - dreams consolidated)
```

### Benefits:
- ✅ Eliminated case-sensitivity confusion (MATRIZ/matriz)
- ✅ Standardized configuration location (config/)
- ✅ Cleaned up documentation (docs/ only)
- ✅ Consolidated dream research (single location)
- ✅ Archived legacy batch artifacts (final_sweep/)
- ✅ Clearer repository structure
- ✅ Reduced import ambiguity

### Metrics:
- **Space freed**: ~150MB (archive old directories)
- **Directories reduced**: 13 → 6
- **Import errors reduced**: Expected 10-20% reduction in collection errors
- **Code references updated**: ~500+ import statements

---

## Rollback Plan

If consolidation causes issues:

### Immediate Rollback (Per Phase):
```bash
# Phase 1 rollback
git revert HEAD~3..HEAD  # Revert last 3 commits

# Phase 2 rollback
git revert HEAD~2..HEAD  # Revert last 2 commits

# Phase 3 rollback (MATRIZ)
git revert HEAD~2..HEAD  # Revert case fix commits
```

### Full Rollback:
```bash
# Create rollback branch
git checkout -b rollback/consolidation-oct26
git reset --hard <commit-before-consolidation>
git push origin rollback/consolidation-oct26

# Notify team and switch back
git checkout main
git pull origin main
```

---

## Success Criteria

### Phase 1 Success:
- [ ] doc/ archived successfully
- [ ] final_sweep/ archived successfully
- [ ] configs/ merged into config/
- [ ] All references updated
- [ ] Smoke tests passing (10/10)
- [ ] No new import errors

### Phase 2 Success:
- [ ] Eval directories consolidated
- [ ] Dream directories consolidated
- [ ] All references updated
- [ ] Smoke tests passing (10/10)
- [ ] No new test collection errors

### Phase 3 Success:
- [ ] MATRIZ case standardized (uppercase)
- [ ] All matriz → MATRIZ imports updated
- [ ] No import errors for MATRIZ modules
- [ ] Smoke tests passing (10/10)
- [ ] Test collection errors reduced or unchanged

### Overall Success:
- [ ] All phases completed
- [ ] Directory count: 13 → 6
- [ ] Smoke tests: 10/10 passing ✅
- [ ] Test collection errors: ≤ 218 (baseline)
- [ ] No new import errors introduced
- [ ] Module registry updated
- [ ] Documentation updated
- [ ] All commits pushed to main

---

## Timeline

### Estimated Duration:
- **Phase 1**: 30 minutes (low-risk quick wins)
- **Phase 2**: 30 minutes (eval/dream consolidation)
- **Phase 3**: 45 minutes (MATRIZ case fix + imports)
- **Phase 4**: 30 minutes (documentation updates)
- **Testing**: 15 minutes (verification)
- **Total**: **2.5 hours**

### Recommended Schedule:
1. Morning: Phase 1 (quick wins)
2. Mid-morning: Phase 2 (consolidation)
3. After break: Phase 3 (MATRIZ case fix - needs focus)
4. Afternoon: Phase 4 (documentation)
5. End of day: Final verification

---

## Post-Consolidation Tasks

1. **Update MODULE_INDEX.md** with new directory structure
2. **Regenerate module registry** with updated paths
3. **Update context files** (claude.me, lukhas_context.md)
4. **Create migration guide** for developers
5. **Update CI/CD pipelines** with new paths
6. **Notify team** of directory changes
7. **Monitor for issues** in next 24-48 hours

---

**Document Version**: 1.0
**Created**: 2025-10-26
**Status**: Ready for execution
**Approver**: Required before Phase 3 (MATRIZ case fix)
