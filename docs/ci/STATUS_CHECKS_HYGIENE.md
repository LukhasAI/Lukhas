# Status Checks Hygiene

This repo keeps PR CI fast and truthful by running only four gates on pull requests while moving heavy suites to nightly, main, or the merge queue.

## PR (Pull Requests)
- CI / 🧪 Critical Path Tests: deterministic smoke + unit selection (≤ 8 min target)
- CI / 🔌 Optional Deps (PR light): light shards for optional extras (e.g., `mcp`, `s3`)
- 🏢 Enterprise CI/CD Pipeline / 🛡️ Quality Gates (Fast Feedback)
- Trinity to Constellation Migration Check (soft on PR)

Notes:
- Deprecations/FutureWarnings fail CI (PYTEST_ADDOPTS set to `-W error`).
- Artifacts on failure: `junit.xml`, `coverage.xml`, `.pytest_cache/`, `logs/`.
- Slowest tests (top 10) are surfaced in the job summary for quick triage.

## Merge Queue (main)
- Batch size = 1 (strict serializability) until promotion criteria are met.
- Same checks as PR, plus hard Trinity gate.

## Nightly (scheduled)
- Advanced Testing (0.001%): mutation/chaos/perf/property-based.
- Repo audit, syntax guardian, f821 audits, pip-audit.

## Quarantine Policy
- Any failure not reproducible in ≤ 15 minutes is quarantined to `tests/quarantine/` and tagged with `@pytest.mark.flaky`.
- PRs that quarantine a test must include an Owner `@username` and an SLA `YYYY-MM-DD` in the PR body.

## Ownership & Escalation
- Workflows: `/.github/workflows/*` → `@ci-owners`
- Quarantine tests: `/tests/quarantine/*` → `@qa-owners`
- Auto-labelers:
  - `flake:quarantined` when PR body references `@pytest.mark.flaky` (requires Owner + SLA).
  - `ci:fail` automatically added to PRs when the CI workflow fails.

## Promotion Criteria (to merge queue batch = 2)
Promote only after 10 consecutive queued merges meet all:
- Critical Path p95 ≤ 8:30, zero flakes.
- Optional (PR light) 100% pass; slowest shard ≤ 5:00.
- Nightly advanced: zero new failures for 3 nights.
- Deprecations/FutureWarnings = 0.

Rollback: If any criterion fails for 2 consecutive days, revert to batch = 1.

## Why only four checks on PRs?
PRs are for iteration; strict gates run where it matters (merge queue/main, nightly). This keeps PR signal clean, speeds iteration, and enforces safety at the boundary.
