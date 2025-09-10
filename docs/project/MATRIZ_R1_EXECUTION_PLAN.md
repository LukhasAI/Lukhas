# 🚀 LUKHAS MATRIZ-R1 Parallel Stream Execution Plan

**WIP Policy**: Max 3 PRs in-flight across "Fix Now" bucket
**Execution Model**: 4 parallel streams (A-D) with dependency management
**Sprint Duration**: 1 week (same-day parallel execution where possible)

## Stream Dependencies

```
Stream A (Lane Integrity) ─┐
                           ├─ Stream D (Hygiene) waits for A+B
Stream B (MATRIZ Traces) ──┘

Stream C (Security/SBOM) ── Independent

Stream D (Syntax/Cycles) ── Waits for A+B merge
```

## Stream A: Lane Integrity (Critical Path)
**Issues**: #184
**Lead Time**: 2-3 days
**WIP Slot**: 1/3

### Scope
- Remove `quarantine/cross_lane` module
- Promote needed APIs to `lukhas/`
- Add importlinter rules
- Keep lane_guard CI enforcement

### Acceptance Criteria
- `make lane-guard` passes
- `.importlinter` configuration passes
- No `lukhas→candidate` imports
- All tests green

### Claude Code Prompt
```
/plan
Goal: Remove quarantine/cross_lane by promoting stable APIs into lukhas/.
Constraints: Keep lane_guard hard fail; no lukhas→candidate imports; small PRs (≤300 LOC).
Steps:
1) List import sites quarantined by cross_lane. Propose minimal API shims inside lukhas/.
2) Generate diffs: delete quarantine module; replace imports with lukhas shims.
3) Add importlinter rule preventing lukhas→candidate.
4) Run: make lane-guard && ruff check --select E9,F63,F7,F82 .
Deliverables: PR with shims, lane_guard + importlinter passing.
```

---

## Stream B: MATRIZ Trace API
**Issues**: #185, #189
**Lead Time**: 1-2 days
**WIP Slot**: 2/3

### Scope
- Implement `traces_router.py` module
- Add endpoints: `/traces/latest`, `/traces/{id}`
- Serve golden JSON from `tests/golden/tier1/`
- Add smoke tests for 200 + trace_id

### Acceptance Criteria
- GET `/traces/latest` returns 200 + JSON with trace_id
- Golden test passes for trace retrieval
- Smoke test verifies endpoint availability

### Codex CLI Prompt
```
codex: create FastAPI router traces_router with GET /traces/latest and GET /traces/{id}
- Reads JSON from reports/matriz/traces/
- Returns 404 if missing; 200 with JSON if exists
- Add pytest: test_traces_latest, test_traces_by_id using sample golden files
- Wire router in serve/main.py if present
- Run: pytest -q tests/smoke tests/golden
```

---

## Stream C: Security & SBOM
**Issues**: #186
**Lead Time**: 1 day
**WIP Slot**: 3/3

### Scope
- Reference `reports/sbom/cyclonedx.json` in `SECURITY_ARCHITECTURE.json`
- Pin high-risk deps (cryptography, transformers, aiohttp)
- Add non-blocking gitleaks CI job

### Acceptance Criteria
- SBOM linked in security documentation
- Critical dependencies pinned to secure versions
- Gitleaks job green (fail-on-findings only)

### Claude Code Prompt
```
/edit
1) Open SECURITY_ARCHITECTURE.json; add a "sbom" section linking reports/sbom/cyclonedx.json and generation command.
2) Create constraints file (constraints.txt) pinning {cryptography, transformers, aiohttp, pydantic} to secure versions.
3) Update CI to install with -c constraints.txt; add non-blocking gitleaks job (fail on findings).
4) Commit PR: "security: pin critical deps + reference SBOM"
```

---

## Stream D: Syntax & Cycle Hygiene (Later)
**Issues**: #187, #188
**Lead Time**: 2 days
**Dependencies**: Wait for Stream A+B merge

### Scope
- Fix F821 (undefined logger) in memory modules
- Break Identity↔Governance cycle behind feature flag
- Run only after A/B complete to avoid churn

### Acceptance Criteria
- No E9/F63/F7/F82 errors in changed files
- Logger error resolved or logger properly defined
- Import cycle broken without functionality loss

---

## Execution Timeline

### Day 1-2: Parallel Start
- **Stream A**: Begin quarantine removal analysis
- **Stream B**: Implement traces_router endpoints  
- **Stream C**: SBOM documentation + dependency pinning

### Day 3-4: Stream Completion
- **Stream A**: Complete lane integrity PR
- **Stream B**: Complete trace API PR
- **Stream C**: Complete security PR

### Day 5-6: Hygiene Phase
- **Stream D**: Begin syntax/cycle fixes (after A+B merge)

### Day 7: Integration
- All streams merged
- MATRIZ-R1 milestone complete
- Audit contradictions remain empty ✅

## Quality Gates

### Per-Stream Gates
- **Lane Integrity**: `make lane-guard` passes; `.importlinter` clean
- **Trace API**: `/traces/latest` returns 200 + trace_id; golden test passes  
- **Security/SBOM**: SBOM referenced in docs; critical deps pinned; gitleaks green
- **Hygiene**: No E9/F63/F7/F82 in changed files; logger defined

### Global Gates
- Max 3 PRs in-flight (WIP control)
- Each PR ≤300 LOC and green CI
- `reports/audit/merged/contradictions.json == []` (CI check)

## Emergency Procedures

### If Stream Blocks
1. **Stream A blocked**: Pause Stream D, focus on unblocking lane integrity
2. **Stream B blocked**: Deprioritize #189 (contracts), focus on core router
3. **Stream C blocked**: Defer to post-MATRIZ-R1 if needed
4. **Multiple blocks**: Escalate to architecture review

### If WIP Exceeds 3
1. Merge smallest ready PR first
2. Hold new PRs until WIP drops
3. Focus on unblocking vs. new development

---

**Last Updated**: 2025-09-10  
**Status**: Ready for execution  
**Next**: Assign Stream A to first available developer
