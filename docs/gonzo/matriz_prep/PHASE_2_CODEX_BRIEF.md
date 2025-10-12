<file name=docs/gonzo/matriz_prep/CODEX_START_PHASE_2.md># Phase 2: Legacy Import Codemod - Start Guide

...

## Important Reminders

- ⚠️ **Update manifests (JSON) in Batch 3**: use the updater script (do **not** sed JSON)
   - Command: `python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/`
   - Then: `python3 scripts/gen_rules_coverage.py` and `python3 docs/check_links.py --root .`
   - Goal: zero `"candidate/"` paths under `manifests/`, updated coverage & links artifacts
- ⚠️ **Update OWNERS.toml patterns in Batch 3**: `candidate.*` → `labs.*`
- ⚠️ **Rename candidate/ → labs/ before applying Batch 3 codemod**

...

## Quick Command Reference

```bash
# Preview changes
make codemod-dry

# Apply changes (commit first!)
make codemod-apply

# Check for legacy imports
make check-legacy-imports

# Lane boundary check
make lane-guard

# Smoke tests
pytest tests/smoke/ -q

# Full test suite
pytest tests/ --maxfail=20 -q

# Update JSON manifest paths safely
python3 scripts/update_manifest_paths.py --root manifests --from candidate/ --to labs/

# Compat alias hits (report)
python3 scripts/check_alias_hits.py
```

...

## Success Criteria

### Before creating PR:

- [ ] All batches applied successfully
- [ ] `pytest tests/ --maxfail=20` passes
- [ ] `make lane-guard` clean
- [ ] `make check-legacy-imports` returns exit 0
- [ ] No unexpected errors in test output
- [ ] Compat layer hits documented
- [ ] JSON manifests updated via script (no "candidate/" under manifests)
- [ ] Compat alias hits reported and trending down (`docs/audits/compat_alias_hits.json`)

...
