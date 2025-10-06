---
status: wip
type: documentation
---
# AGENTS.md — LUKHΛS T4/0.01% Task Delegation Matrix

**Mission:** Enterprise AGI system with surgical precision. Execute 62 audit-derived tasks through specialized agent delegation with explicit proofs, performance budgets, and zero-regression guarantees.

**Context Links:**
- 📋 **[AUDIT_TODO_TASKS.md](./AUDIT_TODO_TASKS.md)** - Complete 62-task breakdown from executive audit
- 📁 **[lukhas_context.md](./lukhas_context.md)** - Current system architecture (Schema v2.0.0, 692 components)
- 🗂️ **[directory_index.json](./directory_index.json)** - Live codebase mapping for navigation
- 📝 **[TODO.md](./TODO.md)** - Operational handoff prompts per agent

---

## Agent Specialization Matrix

### 🔧 CODEX (Security & Authentication Infrastructure)
**Primary:** Identity systems, authentication protocols, cryptographic implementations
**Expertise:** OIDC/JWT, WebAuthn, tiered auth, crypto operations, security hardening
**Legacy Assignments:** SG001-003, SG005, SG009, MS001, MS004-007, MP001-002, MP004-005, MP007-011, OB003, LM001, LM004, DC001-002, TP002, TP004

**LUKHAS Module TODO Assignments:**
- **I.1**: ΛiD token generation/validation (HMAC, CRC32, token rotation)
- **I.2**: T1-T5 tiered authentication system (Password, OTP, WebAuthn, Biometrics)
- **I.3**: OIDC provider and JWT system implementation
- **I.5**: Production identity API endpoints (/authenticate, /verify, /tier-check)
- **I.6**: Security hardening and penetration testing framework

**Handoff Prompt:**
```
You're building LUKHAS identity and authentication systems from scratch. Implement: ΛiD token system with HMAC security, T1-T5 tiered authentication including WebAuthn/biometrics, full OIDC provider with JWT, and production-ready security hardening. Target: <100ms auth latency, 99.99% token validation accuracy, enterprise security compliance.
```

### 📊 Jules (Consciousness & Cognitive Architecture)
**Primary:** Advanced reasoning systems, cognitive modeling, ML optimization
**Expertise:** Neural architectures, behavioral modeling, consciousness engines, advanced AI
**Legacy Assignments:** SG006-007, SG010, MP003, MP006, OB001-002, OB004-008, SC001-005, LM002, TP003, TP007-008

**LUKHAS Module TODO Assignments:**
- **C.1**: Missing ReflectionEngine and DreamEngine implementation
- **C.2**: Memory/Emotion bridges for consciousness processing
- **C.5**: Performance optimization with dynamic scaling and load balancing
- **O.3**: Advanced AI method enhancements (ML-based routing, intelligent optimization)
- **Advanced Features**: Consciousness-Guardian learning feedback loops

**Handoff Prompt:**
```
You're implementing LUKHAS advanced consciousness and cognitive systems. Build: ReflectionEngine for meta-cognitive processing, DreamEngine for background learning, Memory/Emotion bridges for context-aware consciousness, and ML-based optimization algorithms. Target: sophisticated cognitive architecture with <10ms tick processing and stable behavioral patterns.
```

### 📚 Claude Code (Guardian & Ethical Safety Systems)
**Primary:** Safety-critical systems, ethical frameworks, complex architecture, cross-module integration
**Expertise:** Async programming, ethical reasoning, safety systems, architectural coordination
**Legacy Assignments:** SG004, SG008, MS002-003, MS008, MP003, MP012, OB005-006, SC006, LM003, LM005, DC003-005, TP001, TP005-006

**LUKHAS Module TODO Assignments:**
- **G.1**: Async Guardian methods (initialize, validate_action, monitor_behavior)
- **G.2**: GuardianReflector and drift detection system (0.15 threshold)
- **C.3**: Guardian integration for consciousness processing
- **X.1**: Guardian-Memory integration for risk assessment
- **X.3**: Identity-Guardian validation for ethical compliance
- **X.4**: Orchestrator-Guardian integration for ethical AI decisions

**Handoff Prompt:**
```
You're implementing LUKHAS critical safety and ethical systems. Build: async Guardian methods with fail-safe defaults, sophisticated drift detection with remediation, Guardian integration across all modules for ethical validation. Target: 99.9% ethical compliance, <100ms response time, comprehensive cross-module safety coordination.
```

### ⚙️ Copilot (Memory & Data Infrastructure)
**Primary:** Data operations, storage systems, API implementations, standard patterns
**Expertise:** Vector databases, CRUD operations, API patterns, data flow optimization
**Legacy Assignments:** TP005 (supporting), DC001 (supporting), mechanical Trinity→Constellation edits

**LUKHAS Module TODO Assignments:**
- **M.1**: Actual memory storage/retrieval with vector database integration
- **M.2**: Memory-decision system integration (Memory→Guardian/Consciousness data flow)
- **C.4**: Consciousness API endpoint connections to actual data
- **I.4**: Consent ledger and audit trail implementation
- **Data Infrastructure**: Memory indexing, search capabilities, lifecycle management

**Handoff Prompt:**
```
You're building LUKHAS memory and data infrastructure systems. Implement: vector database integration for actual memory storage, Memory→Guardian/Consciousness data pipelines, consciousness API endpoint wiring, and consent ledger with audit trails. Target: <50ms memory retrieval, scalable data architecture, comprehensive audit compliance.
```

---

## T4/0.01% Excellence Standards

### Performance Budgets (Non-Negotiable)
- **Memory recall:** <100ms p95 for 10k items
- **Pipeline latency:** <250ms end-to-end p95
- **Guardian overhead:** <5ms DSL evaluation
- **Cascade prevention:** ≥99.7% success rate

### Quality Gates (All PRs)
- **Test coverage:** ≥90% for core/orchestrator/memory
- **Lane isolation:** Zero cross-lane imports
- **Observability:** Metrics + traces + runbooks
- **Security:** SBOM + secret scanning + pinned SHAs

### Evidence Requirements
- Performance benchmarks with flamegraphs
- Coverage diff vs baseline
- Lane violation reports (must be zero)
- Security audit results
- PromQL snapshots for SLO validation

---

## LUKHAS Module TODO Priorities (Based on Implementation Analysis)

### P0: Critical Foundation (Week 1-2)
**Guardian Safety Systems (Claude Code):**
- G.1: Async Guardian methods (initialize, validate_action, monitor_behavior)
- G.2: GuardianReflector and drift detection system

**Identity Authentication (CODEX):**
- I.1: ΛiD token generation/validation system
- I.2: T1-T5 tiered authentication framework

**Memory Storage (Copilot):**
- M.1: Actual memory storage/retrieval with vector database

### P1: Core Integration (Week 3-4)
**Cross-Module Safety (Claude Code):**
- X.1: Guardian-Memory integration for risk assessment
- X.3: Identity-Guardian validation
- C.3: Guardian integration for consciousness

**Advanced Consciousness (Jules):**
- C.1: ReflectionEngine and DreamEngine implementation
- C.2: Memory/Emotion bridges

**Data Infrastructure (Copilot):**
- M.2: Memory-decision system integration
- I.4: Consent ledger and audit trails

### P2: Advanced Features (Week 5-6)
**Identity Production (CODEX):**
- I.3: OIDC provider and JWT system
- I.5: Production API endpoints
- I.6: Security hardening

**Consciousness Performance (Jules):**
- C.5: Performance optimization and scaling
- O.3: Advanced AI method enhancements

**API Connections (Copilot):**
- C.4: Consciousness API endpoint wiring

### P3: Final Integration (Week 7-8)
**Orchestrator Safety (Claude Code):**
- X.4: Orchestrator-Guardian integration

**Legacy Task Categories (Original System):**
- **Guardian Enforcement:** SG001, SG002, SG006
- **Missing Infrastructure:** MS001, MP001, OB001
- **Security Critical:** SC003, LM001
- **LLM Guardrails:** SG003, SG008, SG009
- **Memory System:** MS002-MS004, MS007-MS008
- **Orchestration:** MP002-MP006, MP011
- **Observability:** OB002-OB005

---

## Cross-Cutting Automation

### Make Targets (All Agents)
```bash
make ci-shadow      # Counterfactual logging tests
make ci-plugin-smoke # Plugin discovery validation
make ci-import-lint  # Lane isolation checks
make sbom           # Security bill of materials
make perf           # Performance budget validation
make oneiric-drift-test # Drift dream testing CLI ✅ (PR 324)
```

### New T4/0.01% Tools (PR 324 Integration)
```bash
# LLM Guardrail Testing
python -m lukhas.core.bridge.llm_guardrail --test-mode

# Collapse Simulation (Memory cascade testing)
python -m lukhas.tools.collapse_simulator --scenarios=memory,ethics,identity

# Drift Dream Testing (Oneiric stack validation)
python -m oneiric_core.tools.drift_dream_test --symbol=test --user=testuser
```

### Global Acceptance Gates
Before any production promotion:
- ✅ E2E p95 ≤ 250ms (CI perf mode)
- ✅ Lane violations = 0
- ✅ Coverage ≥ baseline
- ✅ Security audit = green
- ✅ Dashboards + SLOs + runbooks linked

---

## Agent Coordination Workflow

### 1. Task Assignment
1. Agent receives task ID from AUDIT_TODO_TASKS.md
2. Reviews file locations, dependencies, acceptance criteria
3. Checks lukhas_context.md for current architecture
4. Uses directory_index.json for precise navigation

### 2. Implementation Standards
- **Feature flags:** All new logic behind flags (default safe)
- **Lane isolation:** Respect candidate/integration/production boundaries
- **Metrics:** Instrument all new code paths
- **Tests:** Property-based where appropriate, golden datasets

### 3. Evidence Collection
- Benchmark results with performance budgets
- Test coverage reports
- Metric cardinality validation
- Security scan results
- Flame graphs for performance analysis

### 4. Handoff Protocol
- Update task status in tracking system
- Document rollback procedures
- Link to observability dashboards
- Provide clear acceptance criteria verification

---

## Emergency Protocols

### Kill-Switch Activation
```bash
# Guardian emergency disable
touch /tmp/guardian_emergency_disable

# Feature flag rollback
export ENFORCE_ETHICS_DSL=0
export ENABLE_LLM_GUARDRAIL=0
```

### Rollback Procedures
- Canary percentage reduction (100% → 50% → 10% → 0%)
- Lane demotion (production → integration → candidate)
- Feature flag disable with monitoring
- Circuit breaker activation

---

## Success Metrics

### LUKHAS Module TODO Success Criteria
**Guardian Module (Claude Code):**
- ✅ G.1: Async methods with <100ms response time, fail-safe defaults
- ✅ G.2: Drift detection at 0.15 threshold with 99.7% prevention rate
- ✅ Cross-module integration: 100% ethical validation coverage

**Identity Module (CODEX):**
- ✅ I.1: ΛiD tokens with HMAC security, <100ms validation
- ✅ I.2: T1-T5 auth with 99.99% accuracy, biometric support
- ✅ I.3: OIDC compliance with enterprise integration

**Memory Module (Copilot):**
- ✅ M.1: Vector DB with <50ms retrieval, 1M+ memory capacity
- ✅ M.2: Real-time data flow to Guardian/Consciousness systems
- ✅ Cascade prevention: 99.7% success rate maintained

**Consciousness Module (Jules):**
- ✅ C.1: ReflectionEngine + DreamEngine with <10ms tick processing
- ✅ C.2: Memory/Emotion bridges with context-aware processing
- ✅ C.5: Dynamic scaling with stable behavioral patterns

**Cross-Module Integration (All Agents):**
- ✅ X.1-X.4: Complete ethical validation across all modules
- ✅ Data flow integrity: Guardian↔Memory↔Consciousness↔Identity
- ✅ Performance: End-to-end <250ms p95 latency maintained

### Legacy System Health KPIs
- Guardian enforcement: 100% with <5ms overhead
- Memory performance: <100ms recall at scale
- Pipeline reliability: <250ms p95 latency
- Lane isolation: Zero violations
- Test coverage: ≥90% core systems
- Security posture: All scans green
- **✅ LLM Guardrails**: Schema validation active (PR 324)
- **✅ Collapse Testing**: Memory cascade simulator operational (PR 324)
- **✅ Drift Monitoring**: Oneiric dream testing available (PR 324)

### Agent Performance Metrics
- Task completion velocity
- Defect escape rate
- Performance regression rate
- Test flake introduction rate
- Documentation coverage

---

## Benefits of This System

### For lukhas_context.md Integration
- **Architecture Awareness:** Agents understand current 692-component system
- **Lane Compliance:** Respect production/integration/candidate boundaries
- **Performance Budgets:** Know exact SLO targets from context
- **Schema Validation:** Adhere to v2.0.0 context standards

### For directory_index.json Navigation
- **Precise Targeting:** Agents find exact files without exploration
- **Dependency Mapping:** Understand module relationships
- **Change Impact:** Predict affected components
- **Efficient Execution:** No time wasted on codebase discovery

### Strategic Advantages
1. **Zero Regression:** Property-based testing with golden datasets
2. **Evidence-Based:** All decisions backed by metrics and benchmarks
3. **Surgical Precision:** Minimal scope changes with maximum impact
4. **Production Ready:** T4/0.01% reliability from day one
5. **Scalable Process:** Clear handoff protocols between agents

---

*This agent delegation matrix ensures LUKHAS achieves enterprise AGI reliability through specialized expertise, rigorous testing, and evidence-based promotion criteria.*