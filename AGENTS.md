# 🤖 LUKHAS AI Agent System

**Multi-Agent Development Platform for MATRIZ-R1 Execution**

Welcome to the LUKHAS Agent System - a comprehensive multi-agent architecture designed to execute complex development tasks through specialized AI agents. This document serves as the central hub for all agent-related operations in the LUKHAS AI platform.

## 🎯 Current Mission: Test Suite Development via Jules Agents

**📋 Test Development Hub:** [`docs/testing/JULES_AGENT_TEST_ALLOCATION.md`](docs/testing/JULES_AGENT_TEST_ALLOCATION.md)

After T4 framework implementation and test consolidation (~450 working tests from 1,497 duplicates), we've identified **~150+ missing test modules** across 6 core architectural domains. The Jules agent allocation system provides systematic test development through 10 specialized agents.

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

**⚠️ IMPORTANT: Claude.me Configuration Distribution**
Multiple `claude.me` files exist throughout the workspace providing context-specific instructions:
- **Root**: [`.claude/claude.me`](.claude/claude.me) - Global project context
- **Distributed**: Specialized context files in various modules and domains
- **Integration**: These files provide essential project understanding for all agent interactions

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
---