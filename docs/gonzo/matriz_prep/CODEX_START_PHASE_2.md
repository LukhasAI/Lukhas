# 🚀 Codex: Start Phase 2 - Import Codemod

**Status**: ✅ **READY TO START**
**Date**: 2025-10-12
**Prerequisite**: PR 375 merged ✅

---

## Quick Start

PR 375 has successfully merged! You can now begin Phase 2.

### Step 1: Setup Branch

```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git checkout main
git pull origin main
git checkout -b codex/phase-2-import-codemod
```

### Step 2: Follow Your Brief

📋 **Your detailed instructions**: [`docs/gonzo/matriz_prep/PHASE_2_CODEX_BRIEF.md`](PHASE_2_CODEX_BRIEF.md)

**Execution Order**:
1. **Stage A**: Preview (dry-run) - `make codemod-dry`
2. **Stage B**: Batch Application
   - Batch 1: Tests
   - Batch 2: lukhas/
   - Batch 3: candidate/ → labs/ (directory rename!)
   - Batch 4: core/, packages/, tools/
3. **Stage C**: Verification & PR

---

## Phase 1 Results ✅

**PR #375 Merged**: [`chore(cleanup): remove fake TODO noise from candidate lane`](https://github.com/LukhasAI/Lukhas/pull/375)

**Achievements**:
- ✅ Removed 1,980+ fake TODO/FIXME comments
- ✅ Fixed 1,977 orphaned noqa comments
- ✅ 351 files changed
- ✅ Preserved real TODOs (~397 items with owner hints)

**Files Created**:
- `docs/audits/todos_clean.csv` (397 real TODOs)
- `docs/audits/todos_final.csv` (final inventory)
- Orphaned noqa remediation infrastructure

---

## What Phase 2 Will Do

**Mission**: Migrate legacy imports to canonical namespaces

**Major Changes**:
- `candidate/` → `labs/` (directory rename)
- `candidate.*` → `labs.*` (imports)
- `tools.*` → `lukhas.tools.*`
- `lucas.*` → `lukhas.*`

**Estimated Time**: 2-3 hours
**Risk Level**: Medium (import changes require testing)

---

## Your Tools

All tools are ready and waiting on main:

| Tool | Purpose | Command |
|------|---------|---------|
| **Preview** | Dry-run all changes | `make codemod-dry` |
| **Apply** | Execute rewrites | `make codemod-apply` |
| **Verify** | Check no legacy imports | `make check-legacy-imports` |
| **Config** | Import mappings | `configs/legacy_imports.yml` |

---

## Communication Protocol

**After Stage A (Preview)**:
Report findings in commit message or tag @claude-code

**After Each Batch**:
- Commit with clear message
- Note any issues encountered

**If Blocked**:
Tag @claude-code immediately with:
- Error messages
- Which batch/step failed
- Attempted fixes

---

## Success Criteria

Before creating PR:
- [ ] All 4 batches complete
- [ ] `pytest tests/ --maxfail=20` passes
- [ ] `make lane-guard` clean
- [ ] `make check-legacy-imports` returns exit 0
- [ ] No unexpected test failures
- [ ] JSON manifests updated via script (no "candidate/" under manifests)
- [ ] Compat alias hits reported and trending down (`docs/audits/compat_alias_hits.json`)

---

## Quick Command Reference

```bash
# Preview all changes
make codemod-dry

# Apply to specific directory
python3 scripts/codemod_imports.py --apply --roots tests

# Verify no legacy imports
make check-legacy-imports

# Lane boundaries
make lane-guard

# Smoke tests
pytest tests/smoke/ -q

# Full tests
pytest tests/ --maxfail=20 -q

# Update JSON manifest paths safely
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/

# Compat alias hits (report)
python3 scripts/check_alias_hits.py
```

---

## Important Reminders

⚠️ **Batch 3 includes directory rename**: `git mv candidate labs`

⚠️ **Commit between batches**: Easy rollback if needed

⚠️ **Test after each batch**: Don't skip verification

⚠️ **Update manifests (JSON) in Batch 3**: use the updater script (do **not** sed JSON)
   - Command: `python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/`
   - Then: `python3 scripts/gen_rules_coverage.py` and `python3 docs/check_links.py --root .`
   - Goal: zero `"candidate/"` paths under `manifests/`, updated coverage & links artifacts

---

## Next Steps for You

1. ✅ Verify main is up-to-date
2. ✅ Create Phase 2 branch
3. 📋 Read full brief: [`PHASE_2_CODEX_BRIEF.md`](PHASE_2_CODEX_BRIEF.md)
4. 🔍 Execute Stage A (Preview)
5. 📊 Report findings
6. 🚀 Execute Stage B (Batches)
7. ✅ Create PR

---

**Good luck, Codex! Phase 1 was excellent work. Let's finish Phase 2! 🚀**

---

## Reference Links

- **Full Brief**: [`PHASE_2_CODEX_BRIEF.md`](PHASE_2_CODEX_BRIEF.md) (comprehensive guide)
- **Phase 1 PR**: [#375](https://github.com/LukhasAI/Lukhas/pull/375) (merged ✅)
- **Original Plan**: [`TODO_brief.md`](TODO_brief.md)
- **Codex Handoff**: [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md)
