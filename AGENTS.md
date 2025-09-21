# AGENTS.md — LUKHΛS T4/0.01% Task Delegation Matrix

**Mission:** Enterprise AGI system with surgical precision. Execute 62 audit-derived tasks through specialized agent delegation with explicit proofs, performance budgets, and zero-regression guarantees.

**Context Links:**
- 📋 **[AUDIT_TODO_TASKS.md](./AUDIT_TODO_TASKS.md)** - Complete 62-task breakdown from executive audit
- 📁 **[lukhas_context.md](./lukhas_context.md)** - Current system architecture (Schema v2.0.0, 692 components)
- 🗂️ **[directory_index.json](./directory_index.json)** - Live codebase mapping for navigation
- 📝 **[TODO.md](./TODO.md)** - Operational handoff prompts per agent

---

## Agent Specialization Matrix

### 🔧 CODEX (Deep System Infrastructure)
**Primary:** Performance-critical refactors, Python infrastructure, orchestrator hardening
**Expertise:** Registry systems, memory management, async orchestration, lane isolation
**Assignments:** SG001-003, SG005, SG009, MS001, MS004-007, MP001-002, MP004-005, MP007-011, OB003, LM001, LM004, DC001-002, TP002, TP004

**Handoff Prompt:**
```
You're inheriting production-ready LUKHAS AI infrastructure. Focus on: registry auto-discovery, orchestrator timeouts, memory cascade prevention, and lane isolation enforcement. Prioritize performance budgets and robust error handling. All changes must maintain <250ms p95 latency and 99.7% cascade prevention rates.
```

### 📊 Jules (DevOps/Observability)
**Primary:** CI/CD pipelines, monitoring, security scanning, infrastructure automation
**Expertise:** Prometheus/Grafana, OpenTelemetry, GitHub Actions, SBOM generation
**Assignments:** SG006-007, SG010, MP003, MP006, OB001-002, OB004-008, SC001-005, LM002, TP003, TP007-008

**Handoff Prompt:**
```
You're enhancing LUKHAS CI/CD and observability stack. Implement: Prometheus metrics, OpenTelemetry tracing, Grafana dashboards, SBOM generation, and security scanning. Target: complete observability with runbook-linked alerts and evidence bundles per PR.
```

### 📚 Claude Code (Testing/Documentation)
**Primary:** Test authoring, DSL validation, documentation, edge-case reasoning
**Expertise:** Property-based testing, runbooks, API documentation, compliance
**Assignments:** SG004, SG008, MS002-003, MS008, MP003, MP012, OB005-006, SC006, LM003, LM005, DC003-005, TP001, TP005-006

**Handoff Prompt:**
```
You're ensuring LUKHAS production readiness through comprehensive testing and clear documentation. Create: property-based tests, DSL validation, golden datasets, runbooks, and API docs. Goal: 90% coverage with zero-regression test strategy.
```

### ⚙️ Copilot (Mechanical Refactoring)
**Primary:** Systematic edits, migration scripts, repetitive patterns
**Expertise:** Find/replace operations, docstring updates, import cleanup
**Assignments:** TP005 (supporting), DC001 (supporting), mechanical Trinity→Constellation edits

**Handoff Prompt:**
```
You're supporting LUKHAS modernization through systematic refactoring. Handle: Trinity→Constellation migration, docstring updates, repetitive test patterns, and import cleanup. Maintain consistency across the codebase.
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

## Task Categories & Priorities

### P0: Production Blockers (Week 1)
**Guardian Enforcement:** SG001, SG002, SG006
**Missing Infrastructure:** MS001, MP001, OB001
**Security Critical:** SC003, LM001

### P1: Safety & Performance (Week 2)
**LLM Guardrails:** SG003, SG008, SG009
**Memory System:** MS002-MS004, MS007-MS008
**Orchestration:** MP002-MP006, MP011
**Observability:** OB002-OB005

### P2: Feature Completion (Week 3)
**Documentation:** SG004, DC003-DC005
**Testing:** TP001-TP003, TP006-TP007
**Supply Chain:** SC001-SC002, SC004-SC006

### P3: Polish & Optimization (Week 4)
**Performance Tuning:** MP008-MP010
**Comprehensive Testing:** TP004-TP005, TP008
**Final Documentation:** DC001-DC002

---

## Cross-Cutting Automation

### Make Targets (All Agents)
```bash
make ci-shadow      # Counterfactual logging tests
make ci-plugin-smoke # Plugin discovery validation
make ci-import-lint  # Lane isolation checks
make sbom           # Security bill of materials
make perf           # Performance budget validation
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

### System Health KPIs
- Guardian enforcement: 100% with <5ms overhead
- Memory performance: <100ms recall at scale
- Pipeline reliability: <250ms p95 latency
- Lane isolation: Zero violations
- Test coverage: ≥90% core systems
- Security posture: All scans green

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