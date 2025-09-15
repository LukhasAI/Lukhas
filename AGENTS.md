# 🤖 LUKHAS AI Agent System

**Multi-Agent Development Platform for MATRIZ-R1 Execution**

Welcome to the LUKHAS Agent System - a comprehensive multi-agent architecture designed to execute complex development tasks through specialized AI agents. This document serves as the central hub for all agent-related operations in the LUKHAS AI platform.

## 🎯 Current Mission: Test Suite Development via Jules Agents

**📋 Test Development Hub:** [`docs/testing/JULES_AGENT_TEST_ALLOCATION.md`](docs/testing/JULES_AGENT_TEST_ALLOCATION.md)

After T4 framework implementation and test consolidation (~450 working tests from 1,497 duplicates), we've identified **~150+ missing test modules** across 6 core architectural domains. The Jules agent allocation system provides systematic test development through 10 specialized agents.

### 🗺️ Jules 0x Navigation Guide - ESSENTIAL CONTEXT FILES

**📍 claude.me Files - Domain-Specific Context (40+ files throughout codebase)**

The `claude.me` files provide critical domain-specific context for Jules agents. These files contain architecture overviews, component relationships, and domain-specific instructions that help agents understand the codebase structure.

**Core Navigation Contexts:**
- **Root Overview**: [`claude.me`](claude.me) - Master architecture (7,000+ files, Trinity Framework)
- **MATRIZ Engine**: [`matriz/claude.me`](matriz/claude.me) - Cognitive DNA processing
- **Candidate Workspace**: [`candidate/claude.me`](candidate/claude.me) - Primary development domain

**Trinity Framework Contexts (⚛️🧠🛡️):**
- **⚛️ Identity Systems**:
  - [`identity/claude.me`](identity/claude.me) - Lambda ID foundation
  - [`candidate/core/identity/claude.me`](candidate/core/identity/claude.me) - Identity development
  - [`lukhas/identity/claude.me`](lukhas/identity/claude.me) - Identity integration
- **🧠 Consciousness Systems**:
  - [`consciousness/claude.me`](consciousness/claude.me) - Research foundations
  - [`candidate/consciousness/claude.me`](candidate/consciousness/claude.me) - 52+ components workspace
  - [`lukhas/consciousness/claude.me`](lukhas/consciousness/claude.me) - Trinity activation
- **🛡️ Guardian/Ethics Systems**:
  - [`ethics/claude.me`](ethics/claude.me) - Ethical frameworks
  - [`governance/claude.me`](governance/claude.me) - Governance systems
  - [`candidate/governance/claude.me`](candidate/governance/claude.me) - Guardian development

**Specialized Domain Contexts:**
- **Memory Systems**: [`memory/claude.me`](memory/claude.me), [`candidate/memory/claude.me`](candidate/memory/claude.me)
- **Bio/Quantum**: [`bio/claude.me`](bio/claude.me), [`quantum/claude.me`](quantum/claude.me)
- **Bridge/API**: [`candidate/bridge/claude.me`](candidate/bridge/claude.me), [`lukhas/api/claude.me`](lukhas/api/claude.me)
- **Products**: [`products/claude.me`](products/claude.me), [`products/enterprise/claude.me`](products/enterprise/claude.me)
- **Tools**: [`tools/claude.me`](tools/claude.me) - Development utilities

### 📌 TODO/JULES Markers - Priority Fixes

**Active TODO[JULES-X] markers requiring immediate attention:**
- `candidate/orchestration/openai_modulated_service.py` - TODO[JULES-1]: Service integration patterns
- `candidate/governance/compliance_dashboard_visual.py` - TODO[JULES-2]: Dashboard visualization fixes
- `candidate/governance/drift_dashboard_visual.py` - TODO[JULES-2]: Drift dashboard visualization
- `candidate/qi/qi_entanglement.py` - TODO[JULES-3]: QI/quantum entanglement fixes
- `candidate/core/framework_integration.py` - TODO[JULES-1]: Framework integration fixes

**TODO Resources:**
- [`TODO/raw_todos_20250912_201633.txt`](TODO/raw_todos_20250912_201633.txt) - Comprehensive TODO list
- [`agents_external/AGENT_QUICK_REFERENCE.md`](agents_external/AGENT_QUICK_REFERENCE.md) - Jules TODO batches

## 🚀 Quickstart for Jules Agents

To get started with Jules agents for test development, follow these steps:

- Review the test assignments and details at [`docs/testing/JULES_AGENT_TEST_ALLOCATION.md`](docs/testing/JULES_AGENT_TEST_ALLOCATION.md)
- Clone the repository and set up your environment:
  ```bash
  git clone <repo-url>
  cd <repo-directory>
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
- Run tests locally with:
  ```bash
  pytest tests/
  ```

### Jules Agent Test Assignment Reference
- **Jules-01**: Identity & Authentication (25 tests, CRITICAL, tier1)
- **Jules-02**: Consciousness & Awareness (30 tests, CRITICAL, tier1)
- **Jules-03**: Memory Systems (20 tests, CRITICAL, tier1)
- **Jules-04**: Governance & Ethics (18 tests, HIGH, tier2)
- **Jules-05**: Orchestration & Workflows (22 tests, HIGH, tier2)
- **Jules-06**: API Gateway & External Services (15 tests, MEDIUM, tier3)
- **Jules-07**: Bio-Quantum Systems (12 tests, MEDIUM, tier3)
- **Jules-08**: Performance & Monitoring (10 tests, MEDIUM, tier3)
- **Jules-09**: Integration & E2E Testing (16 tests, HIGH, tier2)
- **Jules-10**: Specialized & Legacy Systems (8 tests, LOW-MEDIUM, tier4)

**Target**: 176 new tests for 95%+ system coverage with T4 quality gates

> ⚠️ NOTE — Jules tasks are currently happening: Do NOT delete or remove any Jules-related sections or files while this work is in progress. Preserve all Jules assignments, configs, and docs until the Jules program is explicitly closed.

## 🏗️ Agent System Architecture

LUKHAS employs a multi-layered agent system with different specializations and deployment methods:

### 1. External Agent Configurations (`agents_external/`)

**Primary Location:** [`agents_external/`](agents_external/) - Dedicated directory for all external agent configurations

#### Current External Agents:
- **Guardian System Commander** - Supreme oversight and safety protocols
- **Advanced Systems Colonel** - Complex system coordination
- **Security Compliance Colonel** - Security and compliance validation
- **Consciousness RRU Lieutenant** - Rapid response for consciousness issues
- **QI Emergency Lieutenant** - Quantum intelligence emergency response

📁 **Configuration Summary:** [`agents_external/AGENT_CONFIGURATION_SUMMARY.md`](agents_external/AGENT_CONFIGURATION_SUMMARY.md)

### 2. Claude Code UI Specialists (`.claude/agents/`)

**Purpose:** Specialized agents accessible via `/agents` command in Claude Code UI

**⚠️ IMPORTANT: claude.me Configuration Distribution**
40+ `claude.me` files exist throughout the workspace providing context-specific instructions that help both Claude Code and Jules agents understand domain architecture:
- **Root**: [`claude.me`](claude.me) - Master architecture overview (7,000+ files, Trinity Framework)
- **Distributed**: Domain-specific context files in candidate/, lukhas/, products/, ethics/, governance/, etc.
- **Integration**: These files provide essential project understanding for all agent interactions
- **Navigation Aid**: Each `claude.me` file contains domain-specific architecture, component relationships, and integration patterns

#### Available Specialists:
- `adapter-integration-specialist` - External service integrations & OAuth
- `api-bridge-specialist` - API design and multi-AI orchestration
- `consciousness-content-strategist` - Content strategy for consciousness tech
- `consent-compliance-specialist` - Privacy, GDPR/CCPA compliance
- `context-orchestrator-specialist` - Multi-model workflow orchestration
- `coordination-metrics-monitor` - Success metrics & phase completion
- `governance-ethics-specialist` - AI ethics & Guardian System
- `identity-auth-specialist` - LUKHAS ΛID authentication systems
- `interactive-web-designer` - Premium web interfaces & particle systems
- `legacy-integration-specialist` - Legacy code modernization & cleanup
- `memory-consciousness-specialist` - Memory systems & consciousness architecture
- `quantum-bio-specialist` - Quantum-inspired & bio-inspired algorithms
- `testing-devops-specialist` - QA, CI/CD, testing frameworks
- `ux-feedback-specialist` - User experience & feedback systems

### 3. Claude Desktop YAML Agents (`agents/configs/`)

**Purpose:** Command-line development agents for specialized workflows

#### Core Development Team:
- `consciousness-architect.yaml` - Chief Consciousness Architect (⚛️ Identity)
- `guardian-engineer.yaml` - Guardian System Engineer (🛡️ Guardian)
- `consciousness-dev.yaml` - Full-Stack Consciousness Developer (⚛️🧠🛡️)
- `velocity-lead.yaml` - Innovation Velocity Lead (🧠 Consciousness)
- `devops-guardian.yaml` - DevOps Consciousness Guardian (🛡️ Guardian)
- `docs-specialist.yaml` - Sacred Documentation Specialist (⚛️ Identity)

## 🚀 MATRIZ-R1 Agent Deployment

### For MATRIZ-R1 Task Execution:

1. **Review Task Assignment**: Check [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](docs/project/MATRIZ_R1_EXECUTION_PLAN.md) for your assigned stream and tasks
2. **Select Agent Type**: Choose appropriate agent based on task complexity:
   - **Simple fixes**: Claude Code UI specialists
   - **Multi-file changes**: Claude Code with `/agents` command
   - **Shell/CI work**: Codex specialist
   - **Complex architecture**: Claude Desktop YAML agents

3. **Follow Stream Dependencies**:
   ```
   Stream A (Lane Integrity) ─┐
                              ├─ Stream D waits for A+B
   Stream B (MATRIZ Traces) ──┘

   Stream C (Security/SBOM) ── Independent
   ```

### Agent Selection Guide for MATRIZ-R1:

#### Stream A (Lane Integrity):
- `legacy-integration-specialist` - For quarantine analysis
- `api-bridge-specialist` - For import boundary design
- `testing-devops-specialist` - For CI validation

#### Stream B (MATRIZ Traces):
- `api-bridge-specialist` - For FastAPI router implementation
- `testing-devops-specialist` - For golden test creation
- `context-orchestrator-specialist` - For trace data orchestration

#### Stream C (Security/SBOM):
- `consent-compliance-specialist` - For security documentation
- `governance-ethics-specialist` - For dependency compliance
- `testing-devops-specialist` - For CI security integration

#### Stream D (Hygiene):
- `legacy-integration-specialist` - For syntax cleanup
- `testing-devops-specialist` - For cycle breaking
- `coordination-metrics-monitor` - For audit validation

## 🛠️ Usage Instructions

### Using Claude Code UI Agents
```bash
# In Claude Code interface:
/agents
# Select specialist from list
# Provide task context from MATRIZ-R1 plan
```

### Using Claude Desktop Agents
```bash
# Deploy agents:
./agents_external/CLAUDE_ARMY/deploy_claude_6_agents.sh

# Use specific agent:
claude-code agent create consciousness-architect --config agents/configs/consciousness-architect.yaml
```

### Using External Configurations
```bash
# Access configurations:
cd agents_external/

# Review agent summaries:
cat AGENT_CONFIGURATION_SUMMARY.md

# Deploy specific configurations as needed
```

## 📊 Quality Gates & Validation

Each MATRIZ-R1 stream has specific acceptance criteria defined in the execution plan:

- **Lane Integrity**: `make lane-guard` passes; `.importlinter` clean
- **Trace API**: `/traces/latest` returns 200 + trace_id; golden test passes
- **Security/SBOM**: SBOM referenced in docs; critical deps pinned; gitleaks green
- **Hygiene**: No E9/F63/F7/F82 in changed files; logger defined

### Global Constraints:
- Max 3 PRs in-flight (WIP control)
- Each PR ≤300 LOC and green CI
- `reports/audit/merged/contradictions.json == []`

## 🔄 Agent Coordination Protocol

1. **Task Claim**: Add `Took: <ID>` to PR description
2. **Branch Creation**: Use suggested naming from execution plan
3. **Local Validation**: Run gates before PR creation
4. **Handover Protocol**: Tag next agent if blocked >2h
5. **Completion**: Paste evidence in PR under Acceptance Criteria

## 📚 Documentation Cross-References

- **Main Execution Plan**: [`docs/project/MATRIZ_R1_EXECUTION_PLAN.md`](docs/project/MATRIZ_R1_EXECUTION_PLAN.md) ⭐
- **Agent Configurations**: [`agents_external/AGENT_CONFIGURATION_SUMMARY.md`](agents_external/AGENT_CONFIGURATION_SUMMARY.md)
- **Architecture Overview**: [`README.md`](README.md)
- **Lane System**: [`ops/matriz.yaml`](ops/matriz.yaml)
- **Audit Reports**: [`reports/deep_search/README_FOR_AUDITOR.md`](reports/deep_search/README_FOR_AUDITOR.md)

## 🧪 Jules Agent Execution Protocol

Each Jules agent MUST follow this standardized workflow for every assigned module:

1. **Read Assignment**
   - Open your allocation in [`docs/testing/JULES_AGENT_TEST_ALLOCATION.md`](docs/testing/JULES_AGENT_TEST_ALLOCATION.md).
   - Check your `.yaml` spec file in `tests/specs/`.

2. **Setup Environment**
   ```bash
   git fetch origin
   git checkout -b feat/tests/Jules-0X-<module>
   make bootstrap
   ```

3. **Create Tests**
   - Place tests under `tests/unit/` or `tests/integration/` following spec.
   - Use T4 markers (`tier1`, `tier2`, etc).
   - Annotate edge cases and goldens.

4. **Local Validation**
   ```bash
   pytest -m tier1 --tb=short
   pytest --cov=lukhas --cov-report=term-missing
   ```

5. **Commit with Branding**
   - Follow [`commit_standard_format.yaml`](commit_standard_format.yaml).
   - Example:
     ```
     test(identity): add MFA login + token expiry tests (tier1)
     ```

6. **PR Creation**
   - Title: `test(Jules-0X): <module summary>`
   - Body: include acceptance checklist + coverage diff.
   - Add label: `tests-only`.

## 📚 Jules 0x Complete Navigation Reference

### claude.me Context Files Directory
Jules agents should refer to these `claude.me` files for domain-specific understanding:

**Core System Contexts:**
| Domain | Path | Purpose |
|--------|------|---------|
| Root Architecture | `claude.me` | Master system overview (7,000+ files, Trinity Framework) |
| MATRIZ Engine | `matriz/claude.me`, `matriz/core/claude.me` | Cognitive DNA processing |
| Candidate Development | `candidate/claude.me` | Primary development workspace (2,877 files) |
| LUKHAS Integration | `lukhas/claude.me` | Integration layer (148 files) |
| Products Deployment | `products/claude.me` | Production systems (4,093 files) |

**Trinity Framework Domains:**
| Component | Development | Integration | Foundation |
|-----------|------------|-------------|------------|
| ⚛️ Identity | `candidate/core/identity/claude.me` | `lukhas/identity/claude.me` | `identity/claude.me` |
| 🧠 Consciousness | `candidate/consciousness/claude.me` | `lukhas/consciousness/claude.me` | `consciousness/claude.me` |
| 🛡️ Guardian | `candidate/governance/claude.me` | `lukhas/governance/claude.me` | `governance/claude.me`, `ethics/claude.me` |

**Specialized Systems:**
| System | Paths | Focus Area |
|--------|-------|------------|
| Memory | `memory/claude.me`, `candidate/memory/claude.me`, `lukhas/memory/claude.me` | Fold-based memory architecture |
| Bio/Quantum | `bio/claude.me`, `quantum/claude.me` | Bio-inspired & quantum algorithms |
| Bridge/API | `candidate/bridge/claude.me`, `lukhas/api/claude.me`, `lukhas/orchestration/claude.me` | External integrations |
| Dream | `candidate/dream/claude.me` | Dream state processing |
| Ethics | `ethics/compliance/claude.me`, `ethics/drift_detection/claude.me`, `ethics/guardian/claude.me` | Ethical frameworks |
| Enterprise | `products/enterprise/claude.me`, `products/enterprise/compliance/claude.me` | Enterprise features |
| Experience | `products/experience/claude.me`, `products/experience/dashboard/claude.me` | User experience |
| Intelligence | `products/intelligence/claude.me`, `products/intelligence/dast/claude.me`, `products/intelligence/lens/claude.me` | AI intelligence |
| Tools | `tools/claude.me` | Development utilities |
| Visualization | `matriz/visualization/claude.me` | System visualization |

### Active TODO/JULES Tracking
- **Priority Files**: Check TODO[JULES-X] markers in candidate/ directory
- **TODO Archive**: `TODO/raw_todos_20250912_201633.txt`
- **Quick Reference**: `agents_external/AGENT_QUICK_REFERENCE.md`
- **Test Allocations**: `docs/testing/JULES_AGENT_TEST_ALLOCATION.md`

### Navigation Tips for Jules Agents
1. **Start with root `claude.me`** for system overview
2. **Check domain-specific `claude.me`** before working in any directory
3. **Refer to Trinity Framework contexts** for architectural alignment
4. **Use TODO[JULES-X] markers** to identify priority work
5. **Follow test allocation assignments** in docs/testing/

---

# 🎯 T4-COMPLIANT TODO COORDINATION SYSTEM

**Implementation Date**: September 15, 2025
**Ground Truth Source**: `.lukhas_runs/2025-09-15/manifest.json`
**Methodology**: Evidence-based verification per PLANNING_TODO.md

## 📊 Current TODO Ground Truth (Evidence-Based)

### **Reality Check Results**
- **Total TODOs**: 1,115 (verified via manifest)
- **Completed**: 11 (evidence-verified)
- **Open**: 1,104 requiring assignment
- **Previous Claims**: 100/100 completion claims CORRECTED to 2/100 actual evidence

### **Priority Distribution**
- **Critical**: 150 TODOs (Security, core infrastructure, blocking issues)
- **High**: 687 TODOs (T4 framework, specialist assignments, core functionality)
- **Medium**: 159 TODOs (Feature enhancements, optimization, documentation)
- **Low**: 119 TODOs (Cleanup, refactoring, nice-to-have features)

## 🤖 T4 Agent Coordination Matrix

### **Operating Principles (T4 Lens)**
- **Skepticism First**: Never trust TODO without checking codebase and git history
- **Evidence-Based**: Status = proven by grep/tests/CI, not wishful comments
- **Atomic Commits**: Every change traceable to TaskID with reproducible verification
- **Batch Discipline**: 25-30 items/agent/cycle (40 for mechanical edits only)
- **No Silent Merges**: PRs require TaskID, scope, and checks

### **Agent Capability Matrix**

#### **Jules Agents (01-10): Complex Logic & Cross-Module Work**
- **Jules-01..03**: Identity/Governance/Guardian (complex, cross-module)
- **Jules-04..05**: Orchestration/Consciousness (complex logic)
- **Jules-06..08**: QI/Entropy/QRG scaffolding (experimental, guarded)
- **Jules-09..10**: Dashboards/Monitoring/Docs wiring
- **Batch Size**: 25-30 tasks (20-25 for experimental work)
- **Risk Level**: HIGH for consciousness/quantum, requires Claude Code review

#### **Codex Agents (01-10): Mechanical Fixes & Code Generation**
- **Codex-01..06**: Mechanical fixes (imports, F821, renames, docstrings)
- **Codex-07..10**: Codegen stubs, template wiring, perf micro-tweaks
- **Batch Size**: 30-40 tasks (mechanical work allows larger batches)
- **Risk Level**: LOW - Mechanical changes with automated verification

#### **Support Agents**
- **Copilot**: Inline refactors & quick fix-ups (never primary owner)
- **Claude Code**: Allocator, verifier, integrator, reviewer of risky changes

### **TaskID Format**: `TODO-{PRIORITY}-{MODULE}-{HASH8}`
Example: `TODO-CRIT-IDENTITY-1a2b3c4d`

### **Batch Management**
- **File Format**: `BATCH-{AGENT}-{DATE}-{SEQ}.json`
- **Branch Naming**: `feat/jules03/identity-trace-batch01`
- **Expiration**: 72 hours (rebase or re-plan)
- **Location**: `.lukhas_runs/2025-09-15/batches/`

## 🛡️ Risk Gating & Safety Protocols

### **High-Risk Areas (Require Claude Code Review)**
- QI/cryptography/Guardian safety code
- Consciousness engines and awareness systems
- Identity and authentication systems
- Trinity Framework boundary changes

### **Feature Flag Requirements**
- All QI/Entropy/QRG work behind feature flags + kill switch
- Experimental consciousness features gated by default
- Risk assessment documented in TaskID metadata

### **Verification Requirements**
- Every TODO completion requires grep/test evidence
- Integration tests for cross-module changes
- No TODO marked complete without verifiable implementation
- T4 principle: "If a TODO can't be verified in code or tests, it's not done"

## 📋 T4 Workflow Protocol

### **1. Enumeration (Ground Truth)**
```bash
# Generate current state
rg -n "TODO|FIXME|HACK" --type py > .lukhas_runs/2025-09-15/grep.txt
python3 tools/ci/build_manifest.py \
  --todo-md TODO/critical_todos.md TODO/high_todos.md TODO/med_todos.md TODO/low_todos.md \
  --grep .lukhas_runs/2025-09-15/grep.txt \
  --out .lukhas_runs/2025-09-15/manifest.json
```

### **2. Batch Allocation**
```bash
# Split into agent batches
python3 tools/ci/split_batches.py \
  --manifest .lukhas_runs/2025-09-15/manifest.json \
  --strategy rules/allocation_rules.yaml \
  --out .lukhas_runs/2025-09-15/batches/

# Lock tasks to prevent duplication
python3 tools/ci/lock_batches.py --dir .lukhas_runs/2025-09-15/batches/
```

### **3. Execution Protocol**
For each batch:
1. **Pre-flight**: Sync main → create branch → run checks
2. **Atomic commits**: One commit per TaskID with evidence
3. **Self-verification**: Re-run checks, update manifest
4. **PR creation**: Include BatchID, TaskIDs, test reports
5. **Review gates**: Claude Code reviews critical/Guardian/Identity PRs
6. **Merge discipline**: Squash with TaskID preservation

### **4. Completion Verification**
- Grep evidence required for every completion claim
- Test coverage validation where applicable
- Git history verification of actual implementation
- Update manifest.json with evidence before marking complete

## 📊 Success Metrics & Reporting

### **Daily Reports** (`.lukhas_runs/2025-09-15/reports/`)
- New TODOs discovered vs. closed
- PRs merged/blocked with reasons
- Coverage delta, lint debt delta
- High-risk areas and mitigations

### **Progress JSON** (Real-time dashboard data)
```json
{
  "date": "2025-09-15",
  "counts": {
    "critical": {"open": 150, "wip": 0, "done": 0},
    "high": {"open": 687, "wip": 0, "done": 0},
    "med": {"open": 159, "wip": 0, "done": 0},
    "low": {"open": 119, "wip": 0, "done": 0}
  },
  "agents": {
    "jules01": {"assigned": 0, "done": 0},
    "codex01": {"assigned": 0, "done": 0}
  }
}
```

### **Completion Criteria**
- Manifest shows 0 open items (all done or consciously waived)
- All critical tasks have tests and appropriate feature flags
- Governance alignment verified for Guardian/Identity changes
- No silent inconsistencies or unverified completions

## 🔄 Integration with Existing Jules System

### **Coordination Protocol**
- **T4 System**: Provides systematic TODO allocation and verification
- **Jules Agents**: Continue test development as assigned in existing docs
- **Handover**: No conflicts - T4 handles TODO management, Jules handles test development
- **Verification**: Both systems use evidence-based completion verification

### **Priority Integration**
1. **Continue Jules test development** per existing allocations
2. **Apply T4 verification** to any TODO-related work
3. **Use T4 batching** for systematic TODO cleanup
4. **Maintain Jules protocols** for test-specific work

---

**Next Actions**: Ready to begin T4-compliant systematic TODO allocation with evidence-based verification while maintaining compatibility with existing Jules agent test development workflows.
