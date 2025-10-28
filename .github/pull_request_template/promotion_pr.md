---
name: Promote candidate -> core
about: PR template for promoting a module from candidate/ to core/ or lukhas/
---

## PR: Promote `candidate/...` -> `core/...` or `lukhas/...`

**Promotion branch:**  
**Module / path:**  
**Owner:** @

### Attachments
- [ ] `PROMOTE.md` present in module folder and complete
- [ ] PROMOTE.md link: 

### CI Artifacts (attach links)
- Unit test report: 
- Coverage report: 
- Lint and static analysis report:
- Benchmark report (if applicable):
- Security scans (pip-audit / safety) artifacts:

### Checklist (required before merge)
- [ ] Static analysis: `ruff` / `mypy` pass
- [ ] Formatting: `black`, `isort` pass
- [ ] Unit tests: PASS (>=90% module-level coverage)
- [ ] Integration/E2E: PASS (if applicable)
- [ ] Benchmarks: PASS (within regression budget)
- [ ] Security & supply chain: PASS
- [ ] Observability: metrics/logs/healthcheck added
- [ ] Ethics Assessment: attached & signed (if model-facing)
- [ ] Owner sign-off
- [ ] Reviewer 1 (Tech) approval
- [ ] Reviewer 2 (Security/Infra) approval
- [ ] Promotion-audit.log updated with PR + artifacts

### Risk & Rollback
- Short risk summary:
- Rollback steps:

---

**PR body:** include a one-paragraph summary of the change and link to PROMOTE.md
