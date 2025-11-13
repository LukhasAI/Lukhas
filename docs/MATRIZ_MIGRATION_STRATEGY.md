# MATRIZ Migration Strategy

> **Phased approach to flatten MATRIZ import surface with zero production breakage**
>
> Source: ChatGPT conversation (2025-11-12)
> Status: Planning complete, ready to execute
> Timeline: 2-6 weeks (depending on parallelism)

---

## Goal

Flatten MATRIZ into canonical modules with zero production breakage, preserve runtime compatibility via shims, and migrate tests incrementally so the test surface becomes clean and maintainable — all with fast PRs and CI validation.

---

## Core Strategy: Production-First, Test-After

**Why not "all at once":**
- Single giant codemod = high blast radius
- Even AST-safe edits can temporarily break tests, CI, or subtle runtime assumptions
- Tests are the canary - better to migrate production code first, then tests in small PRs
- Observability & rollback matter - small PRs + shims + CI gates = auditable, reversible, T4-compliant

**Why do it now:**
- Have momentum and tooling (AST rewriter, shims, CI warning jobs)
- Have credits for parallel validation
- Can get immediate small wins (production code clean, critical tests passing)
- Reduces future friction

---

## Phase Overview

### Phase 0 — Prep & Inventory (1-2 days)
**Outcome:** Authoritative inventory and automated checks; safety scaffolding ready.

**Tasks:** T20251112022-023
- Generate import inventory (`scripts/migration/matriz_inventory.sh`)
- Generate module registry and duplicate/case map (MATRIZ vs matriz)
- Confirm shims exist and tested (`MATRIZ/__init__.py`)
- Ensure tools available: AST rewriter, import health checker, lane guard
- Simplified CI activated (Tier1 workflows for cheap PR validation)
- Worktree conventions established

**Checks:** `make smoke` passes before any migration branch

---

### Phase 1 — Production Code Flatten (1-3 days, small PRs)
**Outcome:** All production code imports canonical MATRIZ, compatibility shim in place, zero import errors, smoke tests green.

**Tasks:** T20251112024-029

**Strategy:**
- One package per PR (or even smaller)
- Use AST rewriter in dry-run, inspect patch, then apply and push
- Keep PRs tiny (1-5 files)
- Add tests if any behavior depends on import names

**Priority order:**
1. `serve/` (user-facing edge)
2. `core/` (business logic)
3. `orchestrator/` (MATRIZ orchestration)
4. `lukhas_website/` (public pages)
5. `core/colonies/` (oracle/reflection)
6. `core/tags/` & `core/endocrine/` (smaller modules)

**Per-package workflow:**
```bash
# 1. Create branch
git checkout -b migration/matriz-<package>-YYYY-MM-DD

# 2. Dry-run
python3 scripts/consolidation/rewrite_matriz_imports.py \
  --path <package> --dry-run --out /tmp/dry.patch

# 3. Human review /tmp/dry.patch

# 4. Apply
python3 scripts/consolidation/rewrite_matriz_imports.py --path <package>

# 5. Validate
make smoke
./scripts/consolidation/check_import_health.py --verbose
./scripts/run_lane_guard_worktree.sh

# 6. Commit & push
git add -A <package>
git commit -m "chore(imports): migrate matriz -> MATRIZ in <package> (AST codemod)"
git push -u origin HEAD

# 7. Open PR with dry-run patch attached
gh pr create --title "..." --body "..." --base main
```

**Key safety:**
- Keep compatibility shim `MATRIZ/__init__` in place until Phase 3
- Backup with git stash not needed (PRs are atomic)
- Wait for Tier1 CI to pass before merge

**Why production-first:**
Production packages affect users and integration; cleaning them first reduces runtime risk. With production green, tests fail only because they referenced old import names; tests can be migrated safely next.

---

### Phase 2 — Tests & Infra Migration (2-7 days, iterative)
**Outcome:** Tests replaced to import canonical modules; test suite green in small steps.

**Tasks:** T20251112030-032

**Strategy:**
- Split tests into logical chunks: integration, unit, smoke, benchmarks, website tests
- Use AST rewriter for tests but apply only after production PRs merged (reduces conflicts)
- Prefer per-directory migration PRs: e.g., `tests/integration/`, `tests/unit/adapters/`

**Steps:**
1. Run test dry-run:
   ```bash
   python3 scripts/consolidation/rewrite_matriz_imports.py \
     --path tests/integration --dry-run --out /tmp/matriz_tests_integration_dryrun.patch
   ```

2. Review patches; add filters to exclude artifacts from changes

3. Apply patch, run focused tests:
   ```bash
   pytest tests/integration -q
   ```
   If failures due to API differences, add compatibility shims in test helpers or adjust mocks

4. Commit and push small PRs

**Note on flakiness:**
If migrating tests causes flakiness, isolate tests and add `@pytest.mark.xfail` with TODOs, but avoid leaving too many xfails — they obscure regressions.

---

### Phase 3 — Remove Compatibility Shims (2-4 days)
**Outcome:** Clean module graph; remove MATRIZ / matriz duality; final registry updated.

**Task:** T20251112033

**When to start:** Only after:
- All production PRs merged
- 95% active tests migrated & passing
- CI SLOs stable for 48-72 hours
- Nightly dream validation & WaveC rehearsal pass on main

**Steps:**
1. Create `chore/remove-matriz-shim` branch
2. Search for remaining references:
   ```bash
   git grep -n "MATRIZ/__init__|matriz.*compat"
   ```
3. Remove shim file and run:
   ```bash
   import-linter
   make smoke
   make test-all
   ```
4. If CI green, merge. If not, revert.

**Risk control:**
- Keep a rollback PR pre-prepared that reinstates shim in <5 lines
- Add brief REVERT note in PR for quick revert flow

---

### Phase 4 — Cleanup, Registry, Docs (1-3 days)
**Outcome:** Final cleanup: update registry, docs, deprecations, remove/archive codemod scripts.

**Tasks:** T20251112034-035

**Steps:**
1. Regenerate module registry, `docs/REPOSITORY_STATE_*.md`
2. Update migration docs: which PRs did what, test migration checklist
3. Remove temporary overrides (importlinter overrides)
4. Ensure lane-guard is green without them
5. Archive migration scripts to `migration_artifacts/`

---

## Parallelization Strategy

**Use second laptop + credits:**
- Second laptop: run test migrations and dry-runs in parallel off branches created from main or `migration/*`
- Keep them isolated from production PRs
- Use Azure credits / self-hosted runners for heavy tests in Phase 2/3
- Schedule heavy runs overnight if needed

---

## Metrics & SLOs for Success

**Before starting (baseline):**
- PR CI minutes & duration
- Number of failures per PR

**Success criteria:**
- **Production-only migrations:** Each PR passes Tier1 in < 20 minutes and smoke green
- **Tests migration PRs:** Per-PR test time < 60 minutes (split if larger)
- **After shim removal:** `make smoke` passes and entire test suite passes in rolling CI
- **Target:** Monthly minutes < 3000

---

## Concrete Scripts & CI Hooks

### 1. Inventory Script
```bash
bash scripts/migration/matriz_inventory.sh
# Outputs to /tmp/matriz_imports.lst
```

### 2. Dry-run Wrapper
```bash
bash scripts/migration/prepare_matriz_migration_prs.sh --dry-run
# Creates dry-run patches for serve/, core/, orchestrator/
```

### 3. Per-PR Checklist
Add to PR template:
- [ ] Dry-run attached
- [ ] Smoke tests run locally (link logs)
- [ ] Lane-guard run (attach artifact)
- [ ] Reviewer: @owner_core

### 4. Fast Rollback
```bash
# Revert last migration commit
git revert <commit-sha>
git push origin HEAD
```

---

## Timing Estimate (Realistic)

- **Phase 0:** 1-2 days (inventory + shims + CI setup)
- **Phase 1:** 1-2 days per major package (serve, core, orchestration) — can parallelize
  - serve/, core/, orchestrator/: 3-6 days total
  - Secondary packages: 2-4 days
- **Phase 2:** 1-2 weeks total for tests (3-4 test PRs/day with credits & parallel runners)
- **Phase 3:** 2-4 days (shim removal + stabilization)
- **Phase 4:** 1-3 days (cleanup)

**Total:** 2-6 weeks for fully flattening and cleaning tests (depending on parallelism and reviewer bandwidth)

---

## Safety & Governance

**Git Safety Protocol:**
- NEVER update git config
- NEVER run destructive/irreversible git commands (push --force, hard reset) unless explicitly requested
- NEVER skip hooks (--no-verify, --no-gpg-sign)
- NEVER force push to main/master
- Keep PRs small and auditable

**Validation Gates:**
- All PRs must pass: `make smoke`, lane-guard, Tier1 CI
- No merge without green CI
- Human review required for all migration PRs

**Rollback Plan:**
- Each PR can be reverted independently
- Shim removal has pre-prepared rollback PR
- Keep compatibility shim until Phase 3 complete

---

## T4 / 0.01% Commentary

**Start now but don't flatten everything at once:**
- Use CI simplification as ideal opportunity (Tier1 lightweight CI) so PRs are fast and not charged for noise
- Sequence: Production packages → tests → shim removal
- Keep PRs small and auditable
- Use credits to run parallel validations
- Keep GitHub Actions minutes under control (schedule heavy work off-peak or use self-hosted runners)

---

## References

- **Tasks:** TODO/MASTER_LOG.md (T20251112022-035)
- **Scripts:** 
  - `scripts/migration/prepare_matriz_migration_prs.sh`
  - `scripts/migration/matriz_inventory.sh`
- **Tools:**
  - `scripts/consolidation/rewrite_matriz_imports.py`
  - `scripts/consolidation/check_import_health.py`
  - `scripts/run_lane_guard_worktree.sh`

---

**Document Version:** 1.0  
**Created:** 2025-11-12  
**Source:** ChatGPT T4/0.01% analysis  
**Status:** Ready to execute
