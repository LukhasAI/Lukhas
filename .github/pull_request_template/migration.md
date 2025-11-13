# MATRIZ Migration PR

## Migration Target

**Package**: `<package-name>`
**Migration Task ID**: `T20251112XXX`
**Dependencies**: (list any dependent migrations, e.g., T20251112024)

---

## Pre-Migration Checklist

Before submitting this PR, ensure ALL items are checked:

- [ ] **CI Simplification merged**: `chore/simplify-ci-pr` is on `main` and Tier1 workflows active
- [ ] **Compatibility shim validated**: `MATRIZ/__init__.py` present and `make smoke` passes
- [ ] **Local validations pass**: Both `make smoke` and `./scripts/run_lane_guard_worktree.sh` PASS locally
- [ ] **Dry-run patch attached**: See `migration_artifacts/matriz/<package>/` directory
- [ ] **Smoke log attached**: `smoke.log` file uploaded as artifact or pasted below
- [ ] **Lane guard log attached**: `lane_guard_run_localfix.log` uploaded or pasted below
- [ ] **Rollback PR exists**: Draft PR `revert/matriz-shim` is ready (link: )

---

## Migration Artifacts

### Dry-Run Patch Location
```
migration_artifacts/matriz/<package>/<package>_dry.patch
```

### Smoke Test Results
<details>
<summary>Click to expand smoke.log</summary>

```
Paste smoke test output here
```

</details>

### Lane Guard Results
<details>
<summary>Click to expand lane_guard_run_localfix.log</summary>

```
Paste lane guard output here
```

</details>

---

## Migration Commands Executed

```bash
# AST rewriter dry-run
scripts/consolidation/rewrite_matriz_imports.py --path <package> --dry-run

# Applied changes
scripts/consolidation/rewrite_matriz_imports.py --path <package> --apply

# Local validation
make smoke
./scripts/run_lane_guard_worktree.sh
```

---

## Rollback Plan

**If this migration fails or causes issues:**

```bash
# Revert this commit
git revert <commit-sha-will-be-added-after-merge>

# Re-enable compatibility shim
# (instructions in revert/matriz-shim PR)

# Verify rollback
make smoke
make lane-guard
```

**Rollback PR**: [Draft PR Link Here]

---

## Post-Merge Validation

**After merging, the following MUST pass:**

- [ ] CI Tier1 workflows all green
- [ ] `make smoke` passes on main
- [ ] No new import errors in affected modules
- [ ] Dream-validation gate passes (drift < 0.15)
- [ ] Lane-guard enforcement passes

**Monitoring Period**: 48-72 hours before proceeding to next migration

---

## Reviewer Assignment

**Required Reviewers:**
- [ ] `@owner_core` (Core team approval)
- [ ] `@security_team` (Security review)

**Migration Owner**: `@<github-username>`

---

## Additional Notes

<!-- Add any migration-specific notes, warnings, or context here -->

---

## Labels

Please apply these labels:
- `migration/matriz`
- `needs-shim-review`
- `migration/smoke-checked` (after validations pass)

---

**Migration Safety**: This PR follows the Pre-Migration Checklist and includes all required artifacts for safe, reversible MATRIZ import migration.
