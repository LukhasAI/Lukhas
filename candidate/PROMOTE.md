# PROMOTE.md — Promotion Rationale & Acceptance Criteria

> Place this file inside the module folder prior to opening the promotion PR.
> Fill all sections. Missing fields will block the review.

## 1) Metadata
- **Module name:** 
- **Owner:** @github-user
- **Proposed promotion branch:** `promote/<module>-YYYYMMDD`
- **Date:** YYYY-MM-DD
- **Risk level:** [LOW | MEDIUM | HIGH]
- **Is this model-facing?** [yes / no]

## 2) Short description
A concise (2–4 sentence) summary of what the module does and why it should be promoted.

## 3) Motivation & Benefits
- Problem this solves:
- Why candidate -> core (business/technical rationale):

## 4) Acceptance Criteria (must be satisfied before merge)
- [ ] `ruff --select E,F,W` — no new errors
- [ ] `mypy` (where applicable) — no new errors
- [ ] `python -m py_compile` — zero errors for changed files
- [ ] Formatting & import checks: `black --check`, `isort --check`, `ruff` imports
- [ ] Unit tests: **>=90% module-level coverage**
- [ ] Integration/E2E tests (if applicable): PASS
- [ ] Benchmarks included for perf-sensitive code and within regression budget
- [ ] SCA & secret scans: PASS (`pip-audit`/`safety`)
- [ ] Observability: metrics + logs + `/healthz` (if long-lived)
- [ ] Ethics Assessment attached (if model- or user-facing)
- [ ] Owner + Tech lead + Security (2) approvals signed in PR

## 5) Risks & Mitigation
Brief list of potential failure modes and how they are mitigated (canary, flags, monitoring).

## 6) Rollback plan
How to revert and mitigation steps for common failure scenarios.

## 7) Artifacts & Attachments
List links to CI artifacts, coverage results, benchmark outputs, dry-run logs, and any migration artifacts.

---

**Owner sign-off:**  
`@` (owner) — date:

**Reviewers (to sign in PR):**  
- Reviewer 1 (Tech lead): `@` — date:  
- Reviewer 2 (Security/Infra): `@` — date:  
- Ethics reviewer (if required): `@` — date:
