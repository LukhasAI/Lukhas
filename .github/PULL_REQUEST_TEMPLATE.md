# Summary
<!-- What changed and why -->

## Artifact Discipline Checks

- [ ] Manifests updated if packages/modules moved or capabilities changed
- [ ] `lukhas_context.md` present/updated with YAML front-matter (star, tier, matriz, owner)
- [ ] Contracts references valid (`scripts/validate_contract_refs.py`)
- [ ] Link checker passes (`docs/check_links.py`)
- [ ] Context front-matter validates (`scripts/validate_context_front_matter.py`)

## Testing & Quality

- [ ] Smoke suite passes locally: `pytest -q -m matriz_smoke` (<120s)
- [ ] Unit tests updated and passing
- [ ] T1/T2: owner set, latency_target_p95 set or explicitly n/a
- [ ] No policy violations (`scripts/policy_guard.py` passes for T1 modules)

## Lane/Module Promotion (if applicable)

- [ ] Candidate smoke: `tests/smoke/test_<MODULE>_candidate_smoke.py` passes
- [ ] Lukhas smoke: `tests/smoke/test_<MODULE>_lukhas_smoke.py` passes
- [ ] Imports updated only in promoted files (core.* → lukhas.core.*)
- [ ] TEMP shim added? (Y/N) — if Y, list dependents
- [ ] Lane boundaries validated (`make lane-guard`)

## Governance

- [ ] Release freeze notes updated if relevant (`release/FREEZE.md`)
- [ ] Guardian/North policy implications documented (if security-sensitive)
- [ ] Breaking changes flagged and versioned

## 🧊 FREEZE Checklist (for RC/release PRs ONLY)

**Only required for release candidate and release PRs. Skip for feature PRs.**

- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Version bumped in `pyproject.toml` and `lukhas/__init__.py`
- [ ] SBOM generated (`build/sbom.cyclonedx.json` present)
- [ ] All CI checks passing (including security scans)
- [ ] Smoke tests passing locally (`pytest tests/smoke/ -v`)
- [ ] Evals accuracy ≥ 0.70 (if eval framework available)
- [ ] No breaking changes without migration guide in docs
- [ ] Documentation updated for new features
- [ ] Release notes reviewed and approved by maintainer

**RC Release Command:**
```bash
./scripts/release_rc.sh v0.X.Y-rc
```

## Notes for Reviewers
<!-- Risks, follow-ups, perf/observability considerations, module deletions -->
