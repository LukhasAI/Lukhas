# Phase 2 OpenAI Alignment - Planning Package

**Status**: ✅ Complete and ready for execution
**Created**: 2025-10-12
**Package Version**: 1.0

---

## 📑 Document Index

### 1. START HERE: Artifacts Summary
**File**: [PHASE_2_ARTIFACTS_SUMMARY.md](PHASE_2_ARTIFACTS_SUMMARY.md)

**What it contains**:
- Complete inventory of all 60+ artifacts created
- Task allocation summary (Claude Code vs Copilot)
- Artifact statistics and locations
- Next steps and quick smoke test
- Important notes and common pitfalls

**Read this first** to understand what's been created and how to proceed.

---

### 2. Master Planning Document
**File**: [PHASE_2_TASK_PLANNING.md](PHASE_2_TASK_PLANNING.md)

**What it contains**:
- Complete task breakdown organized by track (A-H)
- Execution strategy with 4 phases
- Acceptance gates per track
- Risk register and mitigation strategies
- Post-merge verification runbook
- Evidence pack checklist
- Go/No-Go gate criteria

**Use this** for overall project coordination and tracking.

---

### 3. Claude Code Task Briefs
**File**: [CLAUDE_CODE_TASKS.md](CLAUDE_CODE_TASKS.md)

**What it contains**:
- Detailed briefs for 11 complex implementation tasks
- Integration points with MATRIZ/Memory/Guardian
- Code templates and implementation guidance
- Verification steps for each task
- Troubleshooting tips
- Total time: 43-56 hours

**Tasks covered**:
- A1-A5: OpenAI Alignment Surface
- C16-C17: Observability & Ops
- C21-C22: Release Engineering
- H25, H27: Productization (Dreams/Guardian)

**Give this to Claude Code** when starting implementation work.

---

### 4. GitHub Copilot Task Briefs
**File**: [GITHUB_COPILOT_TASKS.md](GITHUB_COPILOT_TASKS.md)

**What it contains**:
- Detailed briefs for 15 mechanical/docs/config tasks
- Script templates and CI workflow snippets
- Documentation standards and examples
- Commit format guidelines (T4 standard)
- Total time: 26-27 hours

**Tasks covered**:
- B6-B12: Mechanical & Docs
- C13-C15: Security & Supply Chain
- E19-E20: Performance & Load
- G23-G24: Docs & DX
- H26: Memory Index Endpoints

**Give this to GitHub Copilot** for implementation work.

---

### 5. Source Document (Reference Only)
**File**: [claude_copilot.md](claude_copilot.md)

**What it contains**:
- Original source material from Phase 2 planning
- All code artifacts in raw form
- Command paste-packs
- Batch status templates

**Use this** as a reference if you need to check the original source.

---

## 🎯 Quick Navigation

### By Role

**I'm the Project Lead**:
1. Read [PHASE_2_ARTIFACTS_SUMMARY.md](PHASE_2_ARTIFACTS_SUMMARY.md)
2. Review [PHASE_2_TASK_PLANNING.md](PHASE_2_TASK_PLANNING.md)
3. Assign tasks from briefs to agents

**I'm Claude Code**:
1. Read [CLAUDE_CODE_TASKS.md](CLAUDE_CODE_TASKS.md)
2. Check acceptance criteria for each task
3. Start with A1 (critical path)

**I'm GitHub Copilot**:
1. Read [GITHUB_COPILOT_TASKS.md](GITHUB_COPILOT_TASKS.md)
2. Start with quick wins (B6, B8, B9, B12)
3. Follow T4 commit standards

---

## 📊 At a Glance

### Task Distribution
- **Claude Code**: 11 tasks (high complexity, integration)
- **GitHub Copilot**: 15 tasks (mechanical, docs, config)
- **Total**: 26 tasks across 8 tracks

### Time Estimates
- **Claude Code**: 43-56 hours
- **Copilot**: 26-27 hours
- **Total**: 69-83 hours (~2-3 weeks with 1-2 people)

### Critical Path
1. A1 (OpenAI Façade) - BLOCKS: A2, A3, C16, H25, H27
2. A4 (Structured Logging) - BLOCKS: C17
3. C13 (SBOM) - BLOCKS: C21
4. Batch 3 (lane rename) - BLOCKS: B11

### Quick Wins (Start Here)
- B6: Fix manifest stats (1 hour)
- B8: Star canon updates (1 hour)
- B9: PR template (30 min)
- B12: Add gitleaks (30 min)

---

## 📁 Artifact Locations

### Planning & Docs
```
docs/gonzo/matriz_prep/
├── README.md                          ← You are here
├── PHASE_2_ARTIFACTS_SUMMARY.md       ← Start here
├── PHASE_2_TASK_PLANNING.md           ← Master plan
├── CLAUDE_CODE_TASKS.md               ← Claude Code briefs
├── GITHUB_COPILOT_TASKS.md            ← Copilot briefs
├── claude_copilot.md                  ← Original source
├── CODEX_START_PHASE_2.md             ← (existing)
└── PHASE_2_CODEX_BRIEF.md             ← (existing)
```

### Code Artifacts
```
lukhas/
├── adapters/openai/
│   ├── api.py              ✅ Stub ready
│   ├── auth.py             ✅ Stub ready
│   └── __init__.py         ✅
├── observability/
│   └── filters.py          ✅ Ready
└── core/reliability/
    ├── backoff.py          ✅ Ready
    ├── ratelimit.py        ✅ Ready
    └── __init__.py         ✅
```

### Test Artifacts
```
tests/
├── smoke/
│   ├── test_healthz.py             ✅ Ready
│   ├── test_openai_facade.py       ✅ Ready
│   ├── test_dreams_api.py          ✅ Ready
│   ├── test_tracing.py             ✅ Ready
│   └── test_evals_runner.py        ✅ Ready
├── logging/
│   └── test_redaction.py           ✅ Ready
├── reliability/
│   └── test_backoff.py             ✅ Ready
├── tools/
│   └── test_openai_tools_export.py ✅ Ready
├── memory/
│   └── test_indexes_api.py         📝 Planned
└── guardian/
    └── test_policy_hooks.py        📝 Planned
```

### Scripts
```
scripts/
├── export_openai_tools.py  ✅ Ready
├── sbom.py                 ✅ Ready
└── release_rc.sh           ✅ Ready
```

### Evals
```
evals/
├── run_evals.py            ✅ Ready
├── README.md               ✅ Ready
└── cases/
    ├── echo.jsonl          ✅ Ready
    └── openai_shapes.jsonl ✅ Ready
```

### Config
```
configs/
├── runtime/
│   └── reliability.yaml    ✅ Ready
└── observability/
    └── slo_budgets.yaml    ✅ Ready
```

### Documentation
```
docs/
├── openai/
│   └── QUICKSTART.md       ✅ Ready
├── ops/
│   └── SLOs.md             ✅ Ready
├── matriz/
│   └── WHY_MATRIZ.md       ✅ Ready
├── openapi/
│   └── lukhas-openai.yaml  ✅ Ready
└── API_ERRORS.md           ✅ Ready
```

---

## 🚦 Execution Checklist

### Phase 0: Setup (You are here ✅)
- [x] All artifacts created
- [x] Planning documents written
- [x] Task briefs prepared
- [ ] Artifacts verified (run smoke test)
- [ ] Tasks assigned to agents

### Phase 1: Foundation (Week 1)
**Claude Code**:
- [ ] A1 - OpenAI Façade (CRITICAL)
- [ ] A4 - Structured Logging
- [ ] A5 - Rate Limiting

**Copilot**:
- [ ] B6 - Fix manifest stats
- [ ] B8 - Star canon updates
- [ ] B9 - PR template
- [ ] C13 - SBOM generation

### Phase 2: Observability & Testing (Week 1-2)
**Claude Code**:
- [ ] A2 - Tool schema bridge
- [ ] A3 - Eval harness
- [ ] C16 - Health endpoints

**Copilot**:
- [ ] B7 - OpenAI quickstart
- [ ] B10 - Nightly coverage
- [ ] B12 - Gitleaks
- [ ] C14 - Dependency scanning

### Phase 3: Advanced Features (Week 2)
**Claude Code**:
- [ ] C17 - OTEL tracing
- [ ] H25 - Dreams API
- [ ] H27 - Guardian hooks

**Copilot**:
- [ ] E19 - Load testing
- [ ] E20 - Reliability knobs
- [ ] G23 - Postman collection
- [ ] G24 - Why MATRIZ

### Phase 4: Release Readiness (Week 2-3)
**Claude Code**:
- [ ] C21 - RC automation
- [ ] C22 - PR previews

**Copilot**:
- [ ] B11 - Link fixer (after Batch 3)
- [ ] C15 - License hygiene
- [ ] H26 - Memory indexes

---

## 📞 Support & Questions

### Technical Questions
- Check relevant `claude.me` files in working directory
- See [MATRIZ_GUIDE.md](../../MATRIZ_GUIDE.md) for cognitive engine details
- See [docs/architecture/](../../architecture/) for system design

### Task Clarification
- Claude Code: Refer to [CLAUDE_CODE_TASKS.md](CLAUDE_CODE_TASKS.md)
- Copilot: Refer to [GITHUB_COPILOT_TASKS.md](GITHUB_COPILOT_TASKS.md)
- Both: Check [PHASE_2_TASK_PLANNING.md](PHASE_2_TASK_PLANNING.md) for acceptance criteria

### Coordination
- Use Go/No-Go gate in planning doc
- Run post-merge verification after each major task
- Track evidence pack artifacts

---

## 🎉 Success Criteria

Phase 2 is **complete** when:

✅ **Core Façade**:
- [ ] All 7 endpoints functional and tested
- [ ] OpenAPI spec validates in CI
- [ ] Health/metrics exposed

✅ **Quality**:
- [ ] Mini-evals ≥ 70% accuracy
- [ ] All smoke tests passing
- [ ] Link checker clean

✅ **Security**:
- [ ] Secrets scanners running (warn-only)
- [ ] SBOM generated
- [ ] License hygiene enforced

✅ **Operations**:
- [ ] SLO budgets committed
- [ ] Observability stack functional
- [ ] Load tests baseline established

---

**Last Updated**: 2025-10-12
**Package Version**: 1.0
**Ready for Implementation**: ✅ YES
