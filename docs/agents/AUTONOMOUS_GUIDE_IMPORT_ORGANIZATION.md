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
