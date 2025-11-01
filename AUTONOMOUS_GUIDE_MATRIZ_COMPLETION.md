# Autonomous Guide: Candidate Lane Cleanup — T4 / 0.01% Standard

**Goal (refined):** Elevate candidate -> core promotions so that promoted modules consistently meet a top-tier "0.01%" production-readiness bar. Ensure promotions are auditable, reversible, and aligned with OpenAI-style safety and governance principles.

**Scope:** This guide governs *promotion* of modules from `candidate/` to `core/` or `lukhas/`. Candidate remains an experimental sandbox; this document **only** defines the safe, repeatable promotion pathway.

**Principles (T4 lens):**
- **Skeptical-by-default.** Assume candidate code has hidden failure modes. Promotion requires independent verification. 
- **Human-in-the-loop.** Automation assists but does not approve promotions. A named owner and two reviewers (one security/infra) must sign off for every promotion.
- **Auditability & Reproducibility.** Every step must be reproducible from CI logs, test artifacts, and an automated changelog.
- **Least privilege & safety.** No secrets, keys, or destructive infra changes in candidate code. Any such change requires a dedicated security review.
- **OpenAI alignment.** Changes that affect content generation, safety checks, ethical evaluation, or user-facing behavior require an explicit ethical compliance check and documentation of risk mitigation.

---

## Success Criteria (must all be satisfied before merge)
1. **Static Analysis:** `ruff --select E,F,W` and `mypy` (where typing is present) pass with zero new errors.
2. **Syntax:** `python -m py_compile` has 0 errors for changed files.
3. **Formatting & Import Hygiene:** `black --check`, `isort --check`, and `ruff` import checks pass.
4. **Tests:** Unit tests covering the module(s) at **>=90% coverage** (module-level). Integration/E2E tests where applicable must pass.
5. **Performance:** Any performance-sensitive module must include benchmarks and not regress beyond a defined threshold (e.g., 5% latency/regression budget) in CI runs.
6. **Security & Supply Chain:** SCA scan (e.g., `pip-audit` or GitHub Dependabot) and secret-scan pass. No unpinned or high-risk dependencies introduced.
7. **Ethics & Policy:** For modules touching model outputs, safety, or user data, the **Ethics Gate** checklist is completed and signed by the Ethics reviewer.
8. **Documentation & UX:** Docstring, README, and `usage` examples present and validated. Public APIs must include stable contracts and changelog notes.
9. **Observability:** Logging, metrics (Prometheus), and a health check `/healthz` implemented for long-lived services.
10. **Owner & Reviewers:** PR must list a named owner and two reviewers (one security/infra).

---

## Promotion Workflow (detailed)

### Phase 0 — Pre-Promotion Triage (owner)
- Create a promotion branch: `git checkout -b promote/<module>-YYYYMMDD`.
- Add a short `PROMOTE.md` in the module folder describing why the module should be promoted, acceptance criteria, and risks.
- Run lint and tests locally. Attach artifacts to PR.

### Phase 1 — Automated Validation (CI Gate 1)
CI runs the following pipeline stages (ordered):
1. `checkout` + `setup` (pinned python version, venv).
2. `static-analysis` — `ruff --fix` in fix-mode only for style; any remaining issues fail the build.
3. `type-check` — `mypy --strict` (or configured subset). Failures block promotion.
4. `format` — `black --check`, `isort --check`.
5. `unit-tests` — `pytest -q --maxfail=1 --junitxml=report_unit.xml` (fail on any test failure).
6. `coverage` — compute module-level coverage and fail if <90%.
7. `integration` — if integration tests exist for the module; otherwise stage skipped.
8. `security-scans` — `pip-audit`, `safety`, secret scanning.
9. `benchmarks` — if `benchmarks/` exists, run and compare to baseline; fail if regression exceeds budget.
10. `artifact-collection` — store test reports, coverage, lints, and benchmark results as CI artifacts.

**CI gating rule:** No automatic merge. Pipeline success *unlocks* manual human review.

### Phase 2 — Human Review & Sign-off (Gate 2)
- **Reviewer 1 (tech lead):** checks design, API stability, tests.
- **Reviewer 2 (security/infra):** checks runtime safety, secrets, dependency health.
- **Ethics reviewer (if applicable):** confirms alignment with policy for any model-facing changes.
- **Owner:** addresses review comments; when satisfied, adds approvals.

Sign-off requires two approvals (tech lead + security) and ethics approval if applicable.

### Phase 3 — Promotion Execution
Once approved:
- Move files: `git mv candidate/... core/...` in promotion branch.
- Run `make smoke` and selected CI stages again on the promotion branch.
- Create PR to `main` with explicit changelog and `PROMOTE.md` attached.
- PR merge is performed by the owner or release manager after final validation.

### Phase 4 — Post-Merge Validation & Monitoring
- CI runs nightly smoke tests for 48 hours, and a canary deployment (if service) for 24–72 hours.
- Metrics monitored for regressions; automated rollback triggers if key signals exceed thresholds.
- Maintain a `promotion-audit.log` linking PR, artifacts, reviewers, and results.

---

## Automation snippets & helpful commands
- Lint & compile check:
```bash
python -m py_compile candidate/consciousness/dream_engine.py
python -m ruff check candidate/consciousness/dream_engine.py --select E,F,W
mypy --config-file mypy.ini candidate/consciousness/dream_engine.py
```
- Run smoke: `make smoke`
- Create promotion branch: `git checkout -b promote/dream-engine-$(date +%F)`

---

## Risk & Rollback
- **Risk:** Promotion may expose unstable APIs or increase CPU/ram usage.
- **Mitigation:** Canary, metrics, and automated rollback. Feature-flag runtime changes.

**Rollback:** If post-merge issues detected, revert commit immediately and open a hotfix branch: 
```bash
git revert <merge-commit-sha>
git push origin main
# Open hotfix PR and re-run full validation
```

---

## Governance & Compliance (OpenAI alignment)
- Every promoted module that interacts with models, user data, or safety controls must include an **Ethics Assessment**: objectives, threat model, mitigations, dataset provenance, privacy safeguards, and fallback behaviors.
- Maintain a public/internal `TRANSPARENCY_SCORECARD.md` entry for each promotion recording validation status and outstanding risks.
- No autopromotion: human sign-offs are mandatory. Automated helpers may prepare prospective PRs but cannot merge.

---

## Appendix: Quick Promotion Checklist (to paste into PR body)
```
- [ ] PROMOTE.md attached and complete
- [ ] Static analysis: PASS
- [ ] Type checks: PASS
- [ ] Formatting: PASS
- [ ] Unit tests: PASS (>=90% coverage)
- [ ] Integration tests: PASS
- [ ] Benchmarks: PASS (within budget)
- [ ] Security scans: PASS
- [ ] Ethics gate (if applicable): Signed
- [ ] Two approvals (tech + security)
- [ ] Owner sign-off
- [ ] Promotion-audit.log updated
```

**Last updated:** 2025-10-28
```
# Autonomous Guide: Fix Import Organization (E402 Violations) — T4 / 0.01% Standard

**Goal (refined):** Reduce E402 violations to near-zero in production lanes and enforce import hygiene by CI. Use AST-safe codemods, deterministic formatting (`isort`), and a documented policy for legitimate runtime imports.

**Scope:** Production lanes only (`lukhas/`, `core/`, `serve/`). Candidate/experimental lanes remain exempt except when promoting.

**Principles:**
- **Deterministic transformations.** Prefer AST-based rewrites over regex.
- **Explainable exceptions.** Any legitimate mid-file import must include a `# noqa: E402 -- reason` comment referencing a short justification and an associated issue/PR.
- **CI enforcement with escape hatch.** Block legacy imports by default in CI; allow temporary bypass via documented, time-limited exceptions.

---

## Success Criteria
- **E402 count <= 1** for production directories (the remaining 1 for justified exception).
- **PRs that touch imports include an automated dry-run report** showing AST changes and smoke tests passing.
- **Automated audit** recorded in `IMPORT_MIGRATION_AUDIT.md` with list of exceptions and reasons.

---

## Recommended Toolchain & Steps
1. `isort` — canonical import ordering and groups.
2. `ruff --select E402,I001` — detect and help autofix import-related issues.
3. `libcst` or `bowler`/AST-codemod — for safe import rewrite.
4. `pytest`, `make smoke` — validate runtime behavior after migrations.

### Phase 1 — Safe Auto-fix & Dry-run
- Run auto-fix on production lanes only:
```bash
python3 -m ruff check lukhas/ core/ serve/ --select E402,I001 --fix
isort --profile black --atomic $(git ls-files 'lukhas/**/*.py' 'core/**/*.py' 'serve/**/*.py')
``` 
- Run an AST dry-run rewriter for tricky patterns and generate a `dryrun_report.md` listing files & AST diffs.

### Phase 2 — Manual Review for Runtime Imports
- Search for:
  - `sys.path.insert`, `sys.path.append`
  - `importlib`, `__import__`, `eval`, `exec`
  - Conditional imports behind `if`/`os.environ`
- For each file where runtime import is truly required, add:
```python
# noqa: E402 -- runtime import required for plugin bootstrap, see ISSUE-XXXX for context
```
- Link to an issue explaining the runtime requirement and mitigation.

### Phase 3 — CI & Pre-Commit
- Add pre-commit hooks for `ruff`, `isort`, and `black`.
- Add CI job `import-health` that runs nightly and on PRs that change imports. Fail PRs that increase E402 count.

### Phase 4 — Documentation & Exceptions
- Add `IMPORT_MIGRATION_AUDIT.md` listing migrations and `noqa` exceptions.
- Limit long-lived exceptions: tag them with `EXCEPTION-YYYYMMDD` and a TTL (e.g., 90 days). Auto-remind owners before expiry.

---

## Sample CI Snippet (GitHub Actions)
```yaml
name: Import Health
on: [pull_request, schedule]
schedule:
  - cron: '0 2 * * *' # nightly
jobs:
  import-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install
        run: pip install ruff isort
      - name: Run Ruff E402 check
        run: python3 -m ruff check lukhas/ core/ serve/ --select E402 --statistics
      - name: Fail on increase
        run: |
          # fail if count > baseline (baseline stored in repo)
          python scripts/import_health/fail_on_delta.py
```

---

## Governance (OpenAI alignment)
- Any import change affecting model-serving code must undergo security & ethics review.
- Justified `noqa: E402` comments must include a link to a public/internal issue documenting the runtime need and mitigation.

---

## Quick checklist
- [ ] Run `ruff` fix on production lanes
- [ ] Run `isort` with black profile
- [ ] Run AST dry-run for remaining files
- [ ] Add `noqa` with justification where needed
- [ ] CI import-health job added and passing
- [ ] Update `IMPORT_MIGRATION_AUDIT.md`

**Last updated:** 2025-10-28
```
# Autonomous Guide: TODO Cleanup Campaign — T4 / 0.01% Standard

**Goal (refined):** Reduce actionable TODO/FIXME debt in production lanes to <1,000 with a verifiable trail linking each removed TODO to either: 1) deletion rationale, 2) GitHub issue, or 3) completed code change. Ensure machine-readable TODOs that support autonomous tooling and governance.

**Key changes vs. previous:**
- Introduce a **machine-readable TODO format**.
- Require **issue creation** for non-trivial TODOs and replace inline TODO with an issue reference.
- Maintain **audit log** of automated deletions and migrations.
- Enforce human review for bulk changes.

---

## Machine-readable TODO format (MANDATORY for new TODOs)
All new TODOs must follow this pattern:
```python
# TODO[YYYY-MM-DD][PRIORITY:HIGH|MED|LOW][OWNER:@github-user][SCOPE:PROD|CANDIDATE|DOCS][ISSUE:optional-number] : Brief message
```
Example:
```python
# See: https://github.com/LukhasAI/Lukhas/issues/553
```
> ✅ **Input validation guardrail:** The TODO inventory generator enforces the allowed
> scope values above and defaults unknown entries to `UNKNOWN`, preventing stray
> metadata such as `SCOPE:X` from polluting production analytics.
This enables scripts to parse, prioritize, and auto-migrate TODOs.

---

## Success Criteria
- **Production TODOs < 1,000** (excluding `candidate/`).
- **All TODO-HIGH** items either implemented, converted to issues, or properly scheduled.
- **Audit trail**: every removed TODO has an entry in `/tmp/todo_cleanup_report.md` and `TODO_CLEANUP_AUDIT.md`.

---

## Strategy (phased & audited)

### Phase 1 — Inventory & Classification (automated)
- Generate `todo_inventory.csv` with fields: `file,line,kind,priority,owner,scope,message`
- Tools: `rg 'TODO\[' --line-number --hidden --glob '!**/.git/**'`

### Phase 2 — Automated deletions (safe low-risk)
- Script identifies obsolete TODOs (files deleted, TODOs referencing deprecated modules) and proposes deletions.
- Produce `obsolete_todos_proposal.md` and create a PR with deletions. PR must be reviewed by one maintainer.

### Phase 3 — Convert to issues (medium-risk)
- For TODO-HIGH & complex TODOs, create GitHub issues using `gh issue create`.
- Replace TODO with `# See: https://github.com/<org>/<repo>/issues/<n>` and add metadata fields.

Automation snippet (pseudo):
```bash
python scripts/todo_migration/create_issues.py --input /tmp/todo_inventory.csv --priority HIGH
# This script returns mapping file: todo_to_issue_map.json
python scripts/todo_migration/replace_todos_with_issues.py --map todo_to_issue_map.json
```

**Human gate:** A maintainer reviews the replacements and merges the PR.

### Phase 4 — Fix simple TODOs (low-risk)
- Batch small fixes (docstrings, typing, small refactors) with tests. Each batch limited to 20 files and validated with `make smoke`.

### Phase 5 — Archive candidate TODOs
- Candidate lane TODOs are archived to `ARCHIVE/candidate_todos/` and excluded from production metrics. This must be a tracked operation with a PR describing scope.

---

## Audit & Metrics
- Maintain `TODO_CLEANUP_AUDIT.md` with:
  - Counts before/after
  - Number of TODOs deleted, converted, fixed
  - List of created issues with links
- Expose `TODO_DEBT_SCORE` in `TRANSPARENCY_SCORECARD.md` computed as weighted sum: HIGH=10, MED=3, LOW=1.

---

## Governance & Safety
- Bulk automated edits (delete/replace > 100 TODOs) **require** two human approvals.
- Any use of `gh issue create` automation must be done under a bot account with an audit trail.
- Do not delete TODOs that reference security, privacy, or model-safety issues — convert to issues instead.

---

## Quick checklist
- [ ] `todo_inventory.csv` generated
- [ ] `obsolete_todos_proposal.md` PR opened
- [ ] High-priority TODOs converted to issues
- [ ] Simple TODOs fixed in batches
- [ ] Candidate TODOs archived
- [ ] `TODO_CLEANUP_AUDIT.md` updated

**Last updated:** 2025-10-28
```
# Autonomous Guide: Complete MATRIZ Migration (Remaining Imports) — T4 / 0.01% Standard

**Goal (refined):** Complete the migration of legacy `matriz` imports to canonical `MATRIZ` across production and test suites with AST-safe tooling, narrow PRs, and CI enforcement. Verify correctness with smoke tests, benchmarks, and a nightly audit.

**Key additions:**
- Add AST dry-run artifact for each PR.
- Require per-PR `migration-summary.md` with import delta and risk statement.
- Enforce 0 legacy imports in production after merge via CI with a 48h observation window before enabling blocking enforcement.

---

## Success Criteria
- 0 legacy `matriz` imports in production/test code (exceptions only in archived/legacy folders).
- Smoke tests passing 10/10 after each grouped migration PR.
- Migration PRs limited to a single directory and a small set of files.

---

## Execution (robust)

### Phase 0 — Baseline & Tools
- Baseline: record current grep count to `MATRIZ_MIGRATION_BASELINE.md`.
- Tooling: `scripts/consolidation/rewrite_matriz_imports.py` using `libcst` or `bowler` for AST accuracy.
- Tests: `make smoke`, full test subset for affected tests.

### Phase 1 — Grouped Migrations (1 directory per PR)
For each directory (e.g., `tests/benchmarks/`):
1. Branch: `migration/matriz-<group>-YYYYMMDD`.
2. Dry run: `--dry-run --verbose` producing `dryrun_<group>.json` and `dryrun_<group>.html` (AST diffs).
3. CI: Attach dry-run artifacts to PR and run `make smoke` and `pytest` for the group.
4. Commit: AST rewriter applied; run `isort`, `ruff --fix` and `black` post-rewrite.
5. PR: Include `migration-summary.md`:
   - Files changed
   - Imports updated
   - Test outcomes
   - Risk statement
6. Merge after 2 reviewers sign off and smoke tests pass.

Limit scope to <200 lines changed per PR when possible.

### Phase 2 — Final Verification
- Run global grep check for legacy imports and fail if >0 in production dirs.
- Run `python3 scripts/generate_meta_registry.py` and `python3 scripts/consolidation/check_import_health.py`.

### Phase 3 — Enable CI Enforcement
- After 48h of stable main, flip CI `BLOCK_LEGACY` to `1` and publish a release note.

---

## Rollback & Hotfix
- Revert the migration PR or revert main if migration causes regressions.
- Maintain rollback instructions in `MATRIZ_MIGRATION_BASELINE.md`.

---

## Checklist
- [ ] Baseline recorded
- [ ] Tools verified (AST rewriter)
- [ ] One PR per group created
- [ ] Dry-run artifacts attached
- [ ] Migration-summary.md included
- [ ] Smoke tests passed
- [ ] Post-merge nightly audit green
- [ ] CI BLOCK_LEGACY flip scheduled after 48h

**Last updated:** 2025-10-28
```

# Autonomous Guide: Complete MATRIZ Migration (Remaining Imports) — T4 / 0.01% Standard

**Goal (refined):** Complete the migration of legacy `matriz` imports to canonical `MATRIZ` across production and test suites with AST-safe tooling, narrow PRs, and CI enforcement. Verify correctness with smoke tests, benchmarks, and a nightly audit.

**Key additions:**
- Add AST dry-run artifact for each PR.
- Require per-PR `migration-summary.md` with import delta and risk statement.
- Enforce 0 legacy imports in production after merge via CI with a 48h observation window before enabling blocking enforcement.

---

## Agent Assignment (Primary / Secondary)

- **Primary Agent:** **Codex** — ideal for writing AST codemods, producing per-file unified-diff patches, and orchestrating `git-apply` flows. Use Codex to generate `rewrite_matriz_imports.py` and patch artifacts.
- **Secondary Agents:**
  - **Claude HaikuGPT-5 / GPT-5 Preview** — high-level risk & ethics review; produce canary plans and threat models.
  - **Grok Code Fast** — fast parsing of CI logs and benchmark outputs; validates regression budgets.
  - **Claude Conner 4.5** — final policy and security sign-off.

**Autonomy & Safety:** Use **dry-run** by default. Codex generates per-file patches and aggregated patch. Human reviewers must inspect `dryrun` artifacts and migration-summary before `--git-apply`. Enable CI blocking only after 48h of stable main.

---

## Success Criteria
- 0 legacy `matriz` imports in production/test code (exceptions only in archived/legacy folders).
- Smoke tests passing 10/10 after each grouped migration PR.
- Migration PRs limited to a single directory and a small set of files.

---

## Execution (robust)

### Phase 0 — Baseline & Tools
- Baseline: record current grep count to `MATRIZ_MIGRATION_BASELINE.md`.
- Tooling: `scripts/consolidation/rewrite_matriz_imports.py` using `libcst` or `bowler` for AST accuracy.
- Tests: `make smoke`, full test subset for affected tests.

### Phase 1 — Grouped Migrations (1 directory per PR)
For each directory (e.g., `tests/benchmarks/`):
1. Branch: `migration/matriz-<group>-YYYYMMDD`.
2. Dry run: `--dry-run --verbose` producing `dryrun_<group>.json` and `dryrun_<group>.html` (AST diffs).
3. CI: Attach dry-run artifacts to PR and run `make smoke` and `pytest` for the group.
4. Commit: AST rewriter applied; run `isort`, `ruff --fix` and `black` post-rewrite.
5. PR: Include `migration-summary.md`:
   - Files changed
   - Imports updated
   - Test outcomes
   - Risk statement
6. Merge after 2 reviewers sign off and smoke tests pass.

Limit scope to <200 lines changed per PR when possible.

### Phase 2 — Final Verification
- Run global grep check for legacy imports and fail if >0 in production dirs.
- Run `python3 scripts/generate_meta_registry.py` and `python3 scripts/consolidation/check_import_health.py`.

### Phase 3 — Enable CI Enforcement
- After 48h of stable main, flip CI `BLOCK_LEGACY` to `1` and publish a release note.

---

## Rollback & Hotfix
- Revert the migration PR or revert main if migration causes regressions.
- Maintain rollback instructions in `MATRIZ_MIGRATION_BASELINE.md`.

---

## Checklist
- [ ] Baseline recorded
- [ ] Tools verified (AST rewriter)
- [ ] One PR per group created
- [ ] Dry-run artifacts attached
- [ ] Migration-summary.md included
- [ ] Smoke tests passed
- [ ] Post-merge nightly audit green
- [ ] CI BLOCK_LEGACY flip scheduled after 48h

**Last updated:** 2025-10-28