# LUKHAS Batch Run: 2025-10-08

**Status**: Ready
**Created**: 2025-10-08
**Total Tasks**: 100 (4 batches × 25 tasks)

---

## Overview

This batch run implements a complete multi-agent TODO allocation system with:
- **4 agent batches** (JULES, CODEX, Claude Code, Copilot)
- **100 total tasks** allocated by capability
- **Comprehensive initiation prompts** with repo navigation
- **Root AGENTS.md** coordination document

---

## Batches

### BATCH-JULES-2025-10-08-01
**Agent**: JULES (Complex Logic & Integration)
**Tasks**: 25
**Branch**: `feat/jules/api-gov-batch01`
**Focus**: API & Governance implementation
**Modules**: bridge/api, governance/ethics, governance/security, governance/policy, governance/consent
**Risk**: HIGH (Guardian/Identity changes)
**Reviewers**: Claude Code (required)

**Task Breakdown**:
- API implementation (onboarding, QRS, explainability): 15 tasks
- Governance (ethics, security, policy, consent): 10 tasks

**Dependencies**: None (first to execute)

---

### BATCH-CODEX-2025-10-08-01
**Agent**: ChatGPT CODEX (Mechanical Fixes)
**Tasks**: 25
**Branch**: `fix/codex/voice-hygiene-batch01`
**Focus**: Import fixes, F821 removals, voice scaffolding
**Modules**: bio, core, voice, products, emotion, tools
**Risk**: LOW (mechanical changes)
**Reviewers**: GitHub Copilot (inline), Claude Code (optional)

**Task Breakdown**:
- Import/F821 fixes: 12 tasks
- Voice module scaffolding: 13 tasks

**Dependencies**: None (parallel with JULES)

---

### BATCH-CLAUDE-CODE-2025-10-08-01
**Agent**: Claude Code (Verifier & Reviewer)
**Tasks**: 25
**Branch**: `review/claude/api-gov-batch01`
**Focus**: System verification + JULES review
**Modules**: Root (verification), bridge/api (review), governance (review)
**Risk**: HIGH (review authority)
**Reviewers**: Self-review

**Task Breakdown**:
- System health verification: 4 tasks
- JULES task reviews: 20 tasks (linked via parent_task_id)
- Final verification gates: 1 task

**Dependencies**: BATCH-JULES-2025-10-08-01 (waits for completion)

---

### BATCH-COPILOT-2025-10-08-01
**Agent**: GitHub Copilot (Assistive Support)
**Tasks**: 25
**Branch**: `assist/copilot/tests-docs-batch01`
**Focus**: Test scaffolds, docstrings, documentation
**Modules**: tests/bridge, tests/governance, docs/examples, candidate/governance
**Risk**: LOW (assistive, no features)
**Reviewers**: Claude Code (if requested)

**Task Breakdown**:
- Test scaffolds: 5 tasks
- Type hints & docstrings: 6 tasks
- Documentation examples: 4 tasks
- Test coverage expansion: 6 tasks
- Code quality helpers: 4 tasks

**Dependencies**: BATCH-JULES-2025-10-08-01 (parallel with Claude Code)

---

## Execution Order

### Phase 1: Implementation (Parallel)
1. **JULES** starts immediately: API & Governance
2. **CODEX** starts immediately (parallel): Import fixes & Voice scaffolding

### Phase 2: Verification & Support (After JULES)
3. **Claude Code** waits for JULES PR, then reviews
4. **Copilot** waits for JULES implementation, then adds tests/docs

### Phase 3: Integration
5. Claude Code approves/requests changes
6. JULES addresses blockers (if any)
7. Merge JULES → Merge CODEX → Merge Copilot
8. Final system health check

---

## Initiation Prompts

Each agent has a comprehensive initiation prompt:

- **JULES_INITIATION.md**: Strategic thinking, Guardian compliance, Trinity Framework
- **CODEX_INITIATION.md**: Speed, precision, evidence-driven fixes
- **CLAUDE_CODE_INITIATION.md**: T4 skepticism, verification rigor, blocker discipline
- **COPILOT_INITIATION.md**: Context awareness, assistive support, quality focus

**Location**: `.lukhas_runs/2025-10-08/prompts/`

---

## Repository Navigation for Agents

### Primary Context Files
- `/lukhas/lukhas_context.md` - Integration layer
- `/candidate/bridge/lukhas_context.md` - API layer
- `/candidate/governance/lukhas_context.md` - Guardian systems
- `/identity/lukhas_context.md` - ΛiD authentication
- `/matriz/lukhas_context.md` - MATRIZ engine

### Architecture Docs
- `/docs/gonzo/PLANNING_TODO.md` - T4 allocation playbook
- `/docs/project_status/JULES_TODO_BATCHES.md` - Batch history
- `/agents/docs/AGENT_NAVIGATION_GUIDE.md` - Directory map
- `/AGENTS.md` - Root coordination (just created)

### Key Schemas
- `consent_tiers.json` - Canonical tier boundaries
- `pyproject.toml` - Import linter configuration
- `lukhas_config.yaml` - Main configuration

---

## Success Criteria

### Per-Batch
- ✅ All tasks addressed (completed or blocked with rationale)
- ✅ Tests pass (pytest green)
- ✅ Import health (make lane-guard passes)
- ✅ Evidence trails (grep before/after, coverage delta)

### System-Wide
- ✅ 100 tasks completed across 4 batches
- ✅ Guardian/Identity changes reviewed by Claude Code
- ✅ Test coverage increased (target: >75% for new code)
- ✅ No lane boundary violations
- ✅ No hardcoded secrets or tier values

---

## Verification Commands

### Before Starting
```bash
cd /Users/agi_dev/LOCAL-REPOS/Lukhas

# Baseline health
make smoke
pytest tests/smoke/ -v
make lane-guard
ruff check .
```

### During Execution
```bash
# Per-batch verification
pytest tests/ -q
ruff check .
make lane-guard

# Coverage tracking
pytest tests/ --cov=. --cov-report=html
```

### After Completion
```bash
# Final system health
make doctor
make smoke
make test-all

# Import health
python -c "import lukhas" && echo "✅ Import OK"

# Drift check
python real_gpt_drift_audit.py --compliance-check

# Symbolic API
python symbolic_api.py --validate
```

---

## Coordination Protocol

### Task Flow
1. User/Claude Code → Enumerate TODOs (grep + manifest)
2. Classification (mechanical vs. logic, priority, Trinity)
3. Batch Assignment (JULES/CODEX/Copilot per rules)
4. Agent Execution (atomic commits, branch per batch)
5. Self-Verification (tests, grep before/after, evidence)
6. PR Creation (template: BatchID, TaskIDs, checks, risk)
7. Review Gate (Claude Code for critical/Guardian/Identity)
8. CI Green + Coverage Check
9. Merge (squash, preserve TaskIDs)
10. Update manifest.json + AGENTS.md

### Branch Naming
- JULES: `feat/jules/{area}-batch{NN}`
- CODEX: `fix/codex/{type}-batch{NN}`
- Claude Code: `review/claude/{area}-batch{NN}`
- Copilot: `assist/copilot/{type}-batch{NN}`

### Commit Format (T4 Standard)
```
<type>(<scope>): <imperative subject ≤72>

Problem: [Context]
Solution: [Approach]
Impact: [Tests, coverage, risk]

TaskID: TODO-{PRIORITY}-{MODULE}-{HASH8}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {Agent} <noreply@anthropic.com>
```

---

## Emergency Contact

**If critically blocked**:
1. Check `/docs/gonzo/PLANNING_TODO.md` for T4 guidance
2. Escalate to Claude Code (tag in PR or create issue)
3. Document in `.lukhas_runs/2025-10-08/reports/blockers.md`

**Common Issues**:
- Import errors → `make lane-guard`, check `pyproject.toml`
- Test failures → Check `tests/conftest.py` fixtures
- Schema mismatch → Load `consent_tiers.json`, never hardcode

---

## Links

- **Root Coordination**: [/AGENTS.md](../../AGENTS.md)
- **Batches**: [batches/](batches/)
- **Initiation Prompts**: [prompts/](prompts/)
- **Planning Playbook**: [/docs/gonzo/PLANNING_TODO.md](../../docs/gonzo/PLANNING_TODO.md)

---

**Generated**: 2025-10-08
**Schema**: 2.0
**Status**: Ready for execution

*⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian*
