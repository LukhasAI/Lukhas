# 🚀 LUKHAS MATRIZ-R1 Parallel Stream Execution Plan

**🤖 Agent System**: [`../../AGENTS.md`](../../AGENTS.md) - Complete guide to the multi-agent platform

**External Configurations**: [`../../agents_external/`](../../agents_external/) - External agent deployment hub

---

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

## Multi‑Agent Task Matrix (Assignable IDs)

### Task Types:
- **Jules Tasks (A1-A6, B1-B5, C1-C3, D1-D3)**: Individual implementation tasks for human-like agents
- **Claude Code Tasks (A-CC1, C-CC1)**: Multi-file planning and documentation tasks  
- **Codex Tasks (B-CX1)**: API implementation and automation tasks

### Agent Roster:
- **Jules01…Jules10**: Generalist agents for focused implementation tasks
- **Codex**: Shell scripting, API implementation, CI automation
- **Claude Code**: Multi-file planning, security updates, documentation

**WIP**: Max 3 PRs open at once. Prefer ≤300 LOC per PR.
**Branching**: `fix/…` (A), `feat/…` (B), `sec/…` (C), `chore/…` (D).

### Stream A — Lane Integrity (Critical Path)
**Issues**: #184 | **Lead**: Jules01

#### Jules Implementation Tasks:
| ID  | Task                                                                                  | Default Assignee | Branch                          | Acceptance Criteria |
|-----|----------------------------------------------------------------------------------------|------------------|----------------------------------|---------------------|
| A1  | Inventory all imports using `quarantine/cross_lane`; produce call‑site list           | Jules01          | fix/stream-a-a1-inventory        | List committed in `reports/audit/lane/cross_lane_calls.txt` |
| A2  | Create minimal shims under `lukhas/shims/…` matching used symbols                     | Jules02          | fix/stream-a-a2-shims            | API parity for used symbols; unit stub tests pass |
| A3  | Replace cross‑lane imports with shims across `lukhas/**`                               | Jules01          | fix/stream-a-a3-rewire           | `make lane-guard` green; `lint-imports` green |
| A4  | Add/verify `.importlinter` contracts incl. `root_packages = lukhas, matriz`           | Jules03          | fix/stream-a-a4-archlint         | Deliberate bad import turns CI red; then removed |
| A5  | Add runtime guard + tripwire (already present) — prove it fails without flag          | Jules03          | fix/stream-a-a5-runtime-guard    | `runtime_lane_guard.py` fails when ALLOW flag unset on synthetic leak |
| A6  | Delete `quarantine/cross_lane` and dead aliases                                       | Jules02          | fix/stream-a-a6-remove-quarantine| Grep shows 0 refs; tests & guards green |

#### AI Agent Planning Task:

**Runbook**: `PYTHONPATH=. python3 tools/ci/runtime_lane_guard.py && PYTHONPATH=. lint-imports -v && ruff check --select E9,F63,F7,F82 lukhas`

---

### Stream B — MATRIZ Trace API
**Issues**: #185, #189 | **Lead**: Jules04

#### Jules Implementation Tasks:
| ID  | Task                                                                 | Default Assignee | Branch                         | Acceptance Criteria |
|-----|----------------------------------------------------------------------|------------------|-------------------------------|---------------------|
| B1  | Implement `matriz.traces_router`: `/traces/latest`, `/traces/{id}`   | Jules04          | feat/stream-b-b1-router       | 200 + JSON with `trace_id` for golden file |
| B2  | List endpoint `/traces/` (merge LIVE `reports/matriz/traces` + GOLD) | Jules05          | feat/stream-b-b2-list         | Returns `{traces:[…], count:n}` |
| B3  | Wire router in `serve/main.py` (conditional include)                 | Jules05          | feat/stream-b-b3-wire         | Smoke GET passes in CI |
| B4  | Golden tests: `tests/smoke/test_traces_router.py`                    | Jules04          | feat/stream-b-b4-tests        | Tests pass in CI; no network |
| B5  | Contracts: ensure Tier‑1 has at least one MATRIZ golden trace        | Jules05          | feat/stream-b-b5-contracts    | Contracts & goldens validated by `contracts-smoke` job |

#### AI Agent Implementation Task:

Env override: `MATRIZ_TRACES_DIR` for runtime; default GOLD=`tests/golden/tier1`, LIVE=`reports/matriz/traces`.

---

### Stream C — Security & SBOM
**Issue**: #186 | **Lead**: Jules06

#### Jules Implementation Tasks:
| ID  | Task                                                               | Default Assignee | Branch                        | Acceptance Criteria |
|-----|--------------------------------------------------------------------|------------------|------------------------------|---------------------|
| C1  | Reference CycloneDX at `reports/sbom/cyclonedx.json` in security doc | Jules06        | sec/stream-c-c1-sbom-doc     | Path + generation command present in `SECURITY_ARCHITECTURE.json` |
| C2  | Add/refresh `constraints.txt` for critical deps                     | Jules06          | sec/stream-c-c2-constraints  | CI installs with `-c constraints.txt` |
| C3  | Add non‑blocking `gitleaks` scan step                               | Jules06          | sec/stream-c-c3-gitleaks     | Report artifact; fails only on findings |

#### AI Agent Documentation Task:

---

### Stream D — Syntax & Cycle Hygiene (post A+B)
**Issues**: #187, #188 | **Lead**: Jules07

#### Jules Implementation Tasks:
| ID  | Task                                                                     | Default Assignee | Branch                         | Acceptance Criteria |
|-----|--------------------------------------------------------------------------|------------------|-------------------------------|---------------------|
| D1  | Fix F821 logger references in `memory/**` (scoped)                       | Jules07          | chore/stream-d-d1-logger      | `ruff --select E9,F63,F7,F82` clean on touched files |
| D2  | Break Identity↔Governance cycle via small interface module               | Jules08          | chore/stream-d-d2-cycle       | `lint-imports` shows cycle removed; tests green |
| D3  | normalize scoreboard keys & add CI sanity for contradictions artifact    | Jules09          | chore/stream-d-d3-auditdash   | `scoreboard.json` normalized; contradictions check present |

*Note: Stream D has only Jules tasks - no AI agent tasks currently assigned.*

---

## Agent Assignment & Handover Protocol

**🤖 For Agent Selection Help**: See [`../../AGENTS.md`](../../AGENTS.md) - Agent selection guide by stream

1. **Claim** a task by adding a checklist item to the PR description: `Took: <ID>`.
2. **Create branch** with the suggested name, keep PR ≤300 LOC.
3. **Run gates locally**: runtime guard → tripwire → import‑linter → smoke tests.
4. **Handover**: on block >2h, push WIP, tag next Jules by ID, and note blockers in PR.
5. **Close** the task by pasting evidence (commands output) into the PR under **Acceptance Criteria**.

## Current Default Assignments

### Jules Implementation Tasks (Individual PRs):
- **Stream A**: A1/A3 → Jules01, A2/A6 → Jules02, A4/A5 → Jules03
- **Stream B**: B1/B4 → Jules04, B2/B3/B5 → Jules05  
- **Stream C**: C1/C2/C3 → Jules06
- **Stream D**: D1 → Jules07, D2 → Jules08, D3 → Jules09

### AI Agent Tasks (Specialized):
- **A-CC1** → Claude Code (Multi-file planning for lane integrity)
- **B-CX1** → Codex (FastAPI router implementation)  
- **C-CC1** → Claude Code (Security documentation & dependency management)

### Agent Specializations:
- **Jules01-Jules10**: Focused implementation tasks, single-file changes, specific fixes
- **Claude Code**: Multi-file planning, documentation updates, security configurations
- **Codex**: API implementation, shell scripts, CI automation, code generation

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

### A-CC1: Claude Code Planning Task
**Assignable ID**: A-CC1  
**Assignee**: Claude Code  
**Branch**: `fix/stream-a-cc1-planning`

**Task Instructions**:
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

**Acceptance Criteria**: Multi-file execution plan ready for Stream A tasks A1-A6

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

### B-CX1: Codex Implementation Task
**Assignable ID**: B-CX1  
**Assignee**: Codex  
**Branch**: `feat/stream-b-cx1-router`

**Task Instructions**:
```
codex: create FastAPI router traces_router with GET /traces/latest and GET /traces/{id}
- Reads JSON from reports/matriz/traces/
- Returns 404 if missing; 200 with JSON if exists
- Add pytest: test_traces_latest, test_traces_by_id using sample golden files
- Wire router in serve/main.py if present
- Run: pytest -q tests/smoke tests/golden
```

**Acceptance Criteria**: FastAPI router implemented with tests passing

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

### C-CC1: Claude Code Security Task
**Assignable ID**: C-CC1  
**Assignee**: Claude Code  
**Branch**: `sec/stream-c-cc1-security`

**Task Instructions**:
```
/edit
1) Open SECURITY_ARCHITECTURE.json; add a "sbom" section linking reports/sbom/cyclonedx.json and generation command.
2) Create constraints file (constraints.txt) pinning {cryptography, transformers, aiohttp, pydantic} to secure versions.
3) Update CI to install with -c constraints.txt; add non-blocking gitleaks job (fail on findings).
4) Commit PR: "security: pin critical deps + reference SBOM"
```

**Acceptance Criteria**: Security docs updated, dependencies pinned, gitleaks CI added

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
