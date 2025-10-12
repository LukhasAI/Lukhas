# LUKHAS Multi-Agent Coordination System

**Status**: Active | **Updated**: 2025-10-08 | **Schema**: 2.0

---

## Overview

The LUKHAS Multi-Agent Coordination System orchestrates four specialized AI agents—**JULES**, **ChatGPT CODEX**, **Claude Code**, and **GitHub Copilot**—across 1,100+ pending TODOs spanning consciousness, governance, identity, and bio-symbolic systems.

**Core Principles** (T4 Lens):
- **Truth over speed**: Status verified by grep/tests/CI, not markdown claims
- **Skepticism first**: Never trust a TODO without code evidence
- **Atomic commits**: Every change traceable to TaskID with reproducible verification
- **Batch discipline**: 25–30 items/agent/cycle (40 for mechanical only)
- **No silent merges**: PRs without TaskID, scope, and checks are blocked

---

## Agent Profiles

### JULES (Complex Logic & Integration Specialist)

**Role**: Strategic implementation, cross-module integration, complex consciousness logic

**Strengths**:
- Multi-domain integration (Identity/Governance/Guardian)
- Consciousness & orchestration systems
- QI/Entropy/QRG experimental scaffolding
- Dashboard/monitoring data wiring

**Domains**:
- `candidate/governance/` - Ethics, compliance, Guardian systems
- `candidate/bridge/api/` - API implementation, onboarding, QRS
- `candidate/core/orchestration/` - Coordination logic
- `candidate/consciousness/` - Awareness protocols
- `products/intelligence/` - Intelligence systems

**Risk Level**: HIGH (complex, multi-module changes)

**Batch Size**: 25–30 tasks (20–25 for experimental)

**Expected Qualities**:
- Strategic architectural thinking
- Deep Trinity Framework understanding (⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian)
- Cross-module dependency awareness
- Guardian System compliance verification
- Clear escalation when blocked

**Review Gates**: Claude Code reviews all critical/Guardian/Identity PRs

---

### ChatGPT CODEX (Mechanical Fixes & Code Generation)

**Role**: High-velocity mechanical fixes, import corrections, template wiring

**Strengths**:
- F821/undefined name fixes
- Import path corrections
- Docstring enforcement
- Small codegen stubs
- Performance micro-tweaks
- **TODO noise cleanup** (removing auto-generated fake TODOs)

**Domains**:
- Import hygiene across all modules
- `candidate/voice/` - Audio scaffolding
- Template wiring (streamlit, edge_tts)
- Test fixture generation
- **TODO/FIXME cleanup** (mechanical removal of linter-generated noise)

**Current Assignment**:
- **MATRIZ Prep - TODO Cleanup** (Phase 1)
- Remove ~1,850 fake TODOs (syntax errors, F821 markers)
- See: `docs/gonzo/matriz_prep/CODEX_HANDOFF.md`

**Risk Level**: LOW to LOW-MEDIUM (mechanical, isolated changes)

**Batch Size**: 30–40 tasks (or bulk cleanup operations)

**Expected Qualities**:
- Speed and consistency
- Mechanical precision without creative deviations
- Evidence-based verification (grep before/after)
- No silent assumption—ask when uncertain
- Batch completion tracking

**Review Gates**: GitHub Copilot for inline nits; Claude Code for critical batches

---

### Claude Code (Allocator, Verifier, Integrator)

**Role**: Task allocation, verification, high-risk PR review, integration coordination

**Strengths**:
- Skeptical T4-lens verification
- Cross-agent coordination
- Risky change review (Guardian/Identity/Consciousness)
- Import path validation
- Drift detection integration

**Domains**:
- All modules (as reviewer)
- `.lukhas_runs/` manifest coordination
- Guardian System validation
- Symbolic API contract checks

**Risk Level**: HIGH (review gate authority)

**Batch Size**: N/A (coordination/review role, not primary owner)

**Expected Qualities**:
- Professional objectivity (truth > approval)
- T4 skepticism (challenge assumptions, verify claims)
- Clear escalation protocols
- Evidence-first mindset (grep/tests/CI)
- No merge without green CI + coverage

**Review Gates**: Self-review; escalates blockers to user

---

### GitHub Copilot (Inline Refactors & Quick Fixes)

**Role**: Assistive inline support, test scaffolds, docstring generation

**Strengths**:
- Real-time inline suggestions
- Test boilerplate generation
- Type hint additions
- README/docs examples
- Small refactors within active PRs

**Domains**:
- All modules (as support, never primary owner)
- Test generation (`tests/`)
- Documentation examples (`docs/examples/`)

**Risk Level**: LOW (assistive, never owns TaskID)

**Batch Size**: N/A (ad-hoc within PRs)

**Expected Qualities**:
- Context awareness within active changes
- Minimal disruption to flow
- No silent feature additions
- User-initiated suggestions only

**Review Gates**: N/A (support role)

---

## Routing Rules

### By Priority & Complexity

| Priority | Mechanical | Cross-Module Logic | Owner | Reviewers |
|----------|------------|-------------------|--------|-----------|
| **Critical** | Yes | No | CODEX | Claude Code |
| **Critical** | No | Yes (Guardian/Identity) | JULES | Claude Code |
| **High** | Yes | No | CODEX | Copilot |
| **High** | No | Yes | JULES | Claude Code |
| **Med** | Yes | No | CODEX | Copilot |
| **Med** | No | Yes | JULES | Claude Code |
| **Low** | Yes | Docs/UI | CODEX | Copilot |
| **Low** | No | Integration | JULES | Copilot |

### By Trinity Alignment

- **⚛️ Identity** (Guardian, auth, ΛiD): JULES (owner) + Claude Code (review)
- **🧠 Consciousness** (awareness, memory): JULES (complex) or CODEX (mechanical)
- **🛡️ Guardian** (ethics, compliance): JULES (owner) + Claude Code (mandatory review)

---

## Batch Allocation System

### Current Run: 2025-10-08

**Location**: `.lukhas_runs/2025-10-08/batches/`

**Ground Truth** (as of 2025-09-15 manifest):
- Total TODOs: 1,115
- Completed: 11
- Open: 1,104
- Priority: Critical 150, High 687, Med 159, Low 119

**Already Batched** (2025-09-15):
- JULES: 10 batches (187 tasks)
- CODEX: 10 batches (95 tasks + 60 planned)
- Remaining unbatched: ~822 tasks

### Active Batches (2025-10-08)

| Agent | Batch ID | Tasks | Branch | Status |
|-------|----------|-------|--------|--------|
| JULES | BATCH-JULES-2025-10-08-01 | 25 | `feat/jules/api-gov-batch01` | Ready |
| CODEX | BATCH-CODEX-2025-10-08-01 | 25 | `fix/codex/voice-hygiene-batch01` | Ready |
| Claude Code | BATCH-CLAUDE-CODE-2025-10-08-01 | 25 | `review/claude/api-gov-batch01` | Ready (depends on JULES) |
| Copilot | BATCH-COPILOT-2025-10-08-01 | 25 | `assist/copilot/tests-docs-batch01` | Ready (depends on JULES) |

**Batch Files**: See `.lukhas_runs/2025-10-08/batches/*.json`

**Initiation Prompts**: See `.lukhas_runs/2025-10-08/prompts/*_INITIATION.md`

---

## Coordination Protocol

### Task Flow

```
1. User Issue/Request Detection
   ↓
2. Claude Code → Enumerate TODOs (grep + manifest)
   ↓
3. Classification (mechanical vs. logic, priority, Trinity alignment)
   ↓
4. Batch Assignment (JULES/CODEX/Copilot per rules)
   ↓
5. Agent Execution (atomic commits, branch per batch)
   ↓
6. Self-Verification (tests, grep before/after, evidence)
   ↓
7. PR Creation (template: BatchID, TaskIDs, checks, risk)
   ↓
8. Review Gate (Claude Code for critical/Guardian/Identity)
   ↓
9. CI Green + Coverage Check
   ↓
10. Merge (squash, preserve TaskIDs)
   ↓
11. Update manifest.json + AGENTS.md
```

### Branch Naming

- JULES: `feat/jules{NN}/{area}-batch{NN}`
- CODEX: `fix/codex{NN}/{type}-batch{NN}`
- Claude Code: `review/claude/{area}-batch{NN}`
- Copilot: `assist/copilot/{type}-batch{NN}`

### Commit Message Format (T4 Standard)

```
<type>(<scope>): <imperative subject ≤72>

Problem: [Context/blockers/dependencies]
Solution: [Approach, changes made]
Impact: [Tests added, coverage delta, risk notes]

TaskID: TODO-{PRIORITY}-{MODULE}-{HASH8}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {Agent} <noreply@anthropic.com>
```

**Types**: feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security

**Scopes**: core|matriz|identity|memory|glyph|api|orchestration|governance|consciousness|interfaces|monitoring|tools|ops|serve|lanes|hygiene|docs

---

## Repository Navigation for Agents

### Essential Context Files (42 Distributed)

**Primary**: `/lukhas/lukhas_context.md` - Integration layer overview

**Domain-Specific**:
- `/candidate/core/lukhas_context.md` - Core development lane
- `/candidate/consciousness/lukhas_context.md` - Consciousness systems
- `/candidate/governance/lukhas_context.md` - Guardian/ethics
- `/matriz/lukhas_context.md` - MATRIZ cognitive engine
- `/identity/lukhas_context.md` - ΛiD authentication
- `/lukhas_website/lukhas_context.md` - Next.js UI

**Architecture Docs**:
- `/docs/architecture/` - System design, Trinity Framework
- `/docs/development/AGENTS.md` - Extended agent guides
- `/docs/gonzo/PLANNING_TODO.md` - T4 allocation playbook
- `/docs/project_status/JULES_TODO_BATCHES.md` - Batch history

### Lane-Based Structure

**Critical Import Rules**:
- `lukhas/` ← can import from `core/`, `matriz/`, `universal_language/` (production)
- `candidate/` ← can import from `core/`, `matriz/` ONLY (NO lukhas imports)
- Strict boundaries prevent cross-lane contamination
- Validate: `make lane-guard`

### Key Directories

```
/Users/agi_dev/LOCAL-REPOS/Lukhas/
├── lukhas/                  # Production lane (692 components)
├── candidate/              # Development lane (2,877 files)
│   ├── consciousness/     # Advanced consciousness research
│   ├── core/              # Core system prototypes
│   ├── governance/        # Guardian, ethics, compliance
│   ├── bridge/            # API, adapters, integrations
│   └── memory/            # Memory fold systems
├── matriz/                 # MATRIZ cognitive engine
├── core/                   # Integration components (253 files)
├── tests/                  # Comprehensive test suites (775+ tests)
├── .lukhas_runs/           # Batch runs, manifests, progress
└── docs/                   # Documentation (architecture, guides)
```

---

## Success Criteria

### Per-Batch

- ✅ All TODOs addressed or marked blocked with rationale
- ✅ Code compiles without errors
- ✅ Tests pass (pytest green)
- ✅ Evidence trail (grep before/after, test coverage delta)
- ✅ Feature flags for experimental code (QI/crypto/Guardian)
- ✅ Manifest updated with task status

### System-Wide

- ✅ `manifest.json` has 0 open items (or waived with rationale)
- ✅ All critical tasks: tests present, Guardian alignment verified
- ✅ Daily reports show monotonically decreasing open counts
- ✅ No "rediscovered" duplicates (task locking enforced)
- ✅ Import health: <5% circular issues, >95% files compile

---

## Guardrails

### Duplicate Work Prevention
- Tasks "locked" when added to open batch
- Allocator refuses to assign elsewhere
- Batches expire after 72h; rebase or re-plan

### Risk Gating
- QI/cryptography/Guardian code ships behind feature flags + kill switch
- Tier boundaries/consent model must use canonical schemas
- Dashboards read live stats or stubbed providers (no magic numbers)

### Verification Requirements
- TODO without acceptance test must add one or document waiver
- Guardian/Identity/Consciousness PRs require Claude Code review
- Green CI required; block on failing coverage deltas

---

## Daily Reporting

**Location**: `.lukhas_runs/<DATE>/reports/<DATE>.md`

**Contents**:
- New TODOs discovered vs. closed
- PRs merged/blocked (with reasons)
- Coverage delta, lint debt delta
- High-risk areas and mitigations
- Blocker escalations

**Progress JSON** (for dashboards):
```json
{
  "date": "2025-10-09",
  "counts": {
    "critical": {"open": 150, "wip": 40, "done": 32},
    "high": {"open": 687, "wip": 120, "done": 85}
  },
  "agents": {
    "jules": {"assigned": 25, "done": 25, "blocked": 0, "status": "completed", "batch": "BATCH-JULES-2025-10-08-01", "commit": "219dc8d0c"},
    "codex": {"assigned": 25, "done": 25, "blocked": 0, "status": "completed", "merged_in": "previous PRs"},
    "claude_code": {"assigned": 25, "done": 0, "blocked": 0, "status": "pending"},
    "copilot": {"assigned": 25, "done": 0, "blocked": 0, "status": "pending"}
  }
}
```

---

## Tools & Commands

### Enumeration
```bash
# Generate manifest from TODOs + grep
rg -n "TODO|FIXME|HACK" -g '!node_modules' > .lukhas_runs/2025-10-08/grep.txt

python tools/ci/build_manifest.py \
  --todo-md TODO/critical_todos.md TODO/high_todos.md TODO/med_todos.md TODO/low_todos.md \
  --grep .lukhas_runs/2025-10-08/grep.txt \
  --out .lukhas_runs/2025-10-08/manifest.json
```

### Batch Management
```bash
# Lock batches to prevent duplication
python tools/ci/lock_batches.py --dir .lukhas_runs/2025-10-08/batches/

# Validate allocation rules
python tools/ci/validate_allocation.py --manifest manifest.json
```

### Validation
```bash
# Lane boundaries
make lane-guard

# Import health
make imports-guard

# System health
make doctor
make smoke
make smoke-matriz

# Full test suite
pytest tests/ -v --cov=. --cov-report=html
```

---

## Emergency Response

### Alert Levels

- 🟢 **NORMAL**: Standard operations
- 🟡 **ADVISORY**: Minor issues, increased monitoring
- 🟠 **WARNING**: Significant issues, Guardian Engineer activated
- 🔴 **CRITICAL**: Major failure, full agent coordination
- 🟣 **TRINITY VIOLATION**: Framework breach, immediate escalation

### Escalation Path

1. Issue Detection (agent or monitoring)
2. Severity Assessment (Claude Code)
3. Agent Assignment (per routing rules)
4. Escalation (if needed): Claude Code → User
5. Resolution Tracking
6. Post-Incident Review

---

## Agent Initiation

### Before Starting a Batch

1. **Read Context**: Primary context file + domain-specific `lukhas_context.md`
2. **Review Batch JSON**: Understand TaskIDs, priorities, dependencies
3. **Check Dependencies**: Ensure prerequisite batches merged
4. **Create Branch**: Follow naming convention
5. **Read Initiation Prompt**: `.lukhas_runs/2025-10-08/prompts/{AGENT}_INITIATION.md`

### During Execution

1. **Atomic Commits**: One TaskID per commit
2. **Self-Verify**: Run tests, grep before/after
3. **Update Status**: Mark tasks `wip` → `completed` in batch JSON
4. **Evidence Trail**: Screenshots for UI, grep output for fixes
5. **Document Blockers**: Add to batch JSON + escalate

### After Completion

1. **PR Creation**: Use template (BatchID, TaskIDs, checks, risk)
2. **Request Review**: Tag appropriate reviewer (Claude Code for critical)
3. **CI Green**: Fix failures before requesting merge
4. **Update Manifest**: Sync task status to `manifest.json`
5. **Update AGENTS.md**: Link PR, update batch status

---

## Links & Resources

- **Batch Files**: [.lukhas_runs/2025-10-08/batches/](.lukhas_runs/2025-10-08/batches/)
- **Initiation Prompts**: [.lukhas_runs/2025-10-08/prompts/](.lukhas_runs/2025-10-08/prompts/)
- **Planning Playbook**: [docs/gonzo/PLANNING_TODO.md](docs/gonzo/PLANNING_TODO.md)
- **Batch History**: [docs/project_status/JULES_TODO_BATCHES.md](docs/project_status/JULES_TODO_BATCHES.md)
- **Navigation Guide**: [agents/docs/AGENT_NAVIGATION_GUIDE.md](agents/docs/AGENT_NAVIGATION_GUIDE.md)
- **Trinity Framework**: [branding/constellation/](branding/constellation/)

---

**The LUKHAS Multi-Agent Coordination System represents truth-first, capability-aligned AI collaboration through rigorous verification, clear ownership, and Trinity Framework principles.**

*⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian*
