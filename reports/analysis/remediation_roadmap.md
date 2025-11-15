# LUKHAS AI Repository - Prioritized Remediation Roadmap

**Generated**: November 15, 2025
**Audit Scope**: Full cognitive audit of LukhasAI/Lukhas repository
**Status**: R&D Phase, Pre-Production

---

## Executive Summary

This roadmap prioritizes remediation tasks based on:
1. **Security Risk** (CRITICAL > HIGH > MEDIUM > LOW)
2. **Compliance Impact** (GDPR/EU AI Act requirements)
3. **Effort Estimate** (Small: <2 days, Medium: 2-10 days, Large: >10 days)
4. **Business Value** (Production readiness, user trust, regulatory compliance)

**Total Tasks Identified**: 127
- **CRITICAL** (P0): 15 tasks - Must complete before production
- **HIGH** (P1): 42 tasks - Complete within 3 months
- **MEDIUM** (P2): 48 tasks - Complete within 6 months
- **LOW** (P3): 22 tasks - Ongoing improvements

---

## Priority 0: CRITICAL (Immediate Action Required)

### 🔴 Security - Code Injection Risks

#### CRIT-SEC-001: Eliminate eval() Usage (47 occurrences)
**Risk**: Arbitrary code execution vulnerability
**Impact**: CRITICAL security risk, potential system compromise
**Effort**: LARGE (10-15 days)
**Owner**: Security Team + Core Engineering

**Tasks**:
1. Audit all 47 `eval()` usages in codebase
2. Categorize by purpose: dynamic code execution, expression evaluation, configuration
3. Replace with safer alternatives:
   - Expression evaluation → `ast.literal_eval()`
   - Dynamic imports → `importlib.import_module()`
   - Configuration → JSON/YAML/TOML parsing
4. For unavoidable cases: implement sandboxed execution (RestrictedPython)
5. Add linter rule to prevent future `eval()` introduction

**Acceptance Criteria**:
- Zero `eval()` calls in production code (tests/examples may use with documented justification)
- All replaced with safer alternatives
- Security review completed

**Timeline**: Week 1-2

---

#### CRIT-SEC-002: Eliminate exec() Usage (28 occurrences)
**Risk**: Arbitrary code execution vulnerability
**Impact**: CRITICAL security risk
**Effort**: MEDIUM (5-8 days)
**Owner**: Security Team + Core Engineering

**Tasks**:
1. Audit all 28 `exec()` usages
2. Replace with:
   - Function calls for known operations
   - Plugin systems with controlled interfaces
   - Pre-defined command patterns
3. Sandbox unavoidable cases
4. Add linter rule to prevent future `exec()` introduction

**Acceptance Criteria**:
- Zero `exec()` calls in production code
- Security review completed

**Timeline**: Week 2-3

---

#### CRIT-SEC-003: Fix SQL Injection Vulnerabilities (25 occurrences)
**Risk**: Database compromise, data breach
**Impact**: CRITICAL data security risk
**Effort**: SMALL (2-3 days)
**Owner**: Backend Engineering

**Tasks**:
1. Identify all 25 SQL concatenation patterns
2. Replace with parameterized queries
3. Use ORM where applicable (SQLAlchemy)
4. Add SQL injection tests to security test suite

**Acceptance Criteria**:
- All SQL queries use parameterized statements or ORM
- SQL injection security tests pass

**Timeline**: Week 1

---

#### CRIT-COMP-001: Conduct Data Protection Impact Assessment (DPIA)
**Risk**: GDPR non-compliance (Art. 35)
**Impact**: Legal/regulatory risk for biometric & consciousness data processing
**Effort**: MEDIUM (5-7 days)
**Owner**: Legal + Engineering + AI Safety

**Tasks**:
1. Document all processing activities involving special category data:
   - Biometric data (WebAuthn)
   - Emotional state (endocrine system)
   - Consciousness patterns
2. Assess necessity and proportionality
3. Identify risks to data subjects
4. Document mitigation measures
5. Obtain signoff from DPO (if applicable)

**Acceptance Criteria**:
- DPIA document completed (`docs/compliance/DPIA.md`)
- Reviewed by legal counsel
- Mitigation measures implemented

**Timeline**: Week 2-3

---

#### CRIT-COMP-002: Create Article 30 Processing Register
**Risk**: GDPR non-compliance (Art. 30)
**Impact**: Regulatory violation, potential fines
**Effort**: SMALL (2-3 days)
**Owner**: Legal + Engineering

**Tasks**:
1. Document all processing activities:
   - Categories of personal data
   - Purposes of processing
   - Categories of data subjects
   - Data recipients
   - International transfers
   - Retention periods
   - Security measures
2. Create register document
3. Establish maintenance process (update on changes)

**Acceptance Criteria**:
- Article 30 register created (`docs/compliance/ARTICLE_30_REGISTER.md`)
- Reviewed by legal counsel
- Process for updates established

**Timeline**: Week 1

---

### 🔴 Architecture - Critical Path Issues

#### CRIT-ARCH-001: Resolve MATRIZ/matriz Case Conflict
**Risk**: Import failures, runtime errors
**Impact**: System instability, deployment failures
**Effort**: MEDIUM (3-5 days)
**Owner**: Core Engineering

**Finding**: Both `/MATRIZ/` (28 references) and `/matriz/` (600+ references) directories exist

**Tasks**:
1. Decide canonical casing (recommend: `MATRIZ` for directory, `matriz` for module imports)
2. Consolidate all code to use consistent casing
3. Update all 600+ import references
4. Add import linter rule to enforce consistency
5. Test all import paths

**Acceptance Criteria**:
- Single canonical directory structure
- All imports use consistent casing
- No import errors in CI/CD
- Lane isolation tests pass

**Timeline**: Week 1-2

---

#### CRIT-ARCH-002: Enforce Lane Boundaries
**Risk**: Architecture violations, code coupling
**Impact**: Maintenance burden, testing complexity
**Effort**: LARGE (15-20 days)
**Owner**: Architecture Team

**Finding**: Lane boundary violations exist between candidate/core/lukhas/MATRIZ

**Tasks**:
1. Run import-linter and document all violations
2. Categorize violations by severity and effort to fix
3. Create migration plan for each violation
4. Implement fixes (may require refactoring)
5. Enable strict lane enforcement in CI

**Acceptance Criteria**:
- All lane isolation contracts pass
- Import-linter shows zero violations
- CI blocks PRs with new violations

**Timeline**: Week 3-6

---

### 🔴 Testing - Coverage Baseline

#### CRIT-TEST-001: Establish Coverage Baseline
**Risk**: Unknown test coverage, potential regressions
**Impact**: Code quality, confidence in changes
**Effort**: SMALL (1 day)
**Owner**: QA Team

**Tasks**:
1. Run pytest with coverage on current codebase
2. Generate coverage report (HTML + JSON)
3. Document current coverage percentage
4. Identify modules with <30% coverage (fail threshold)
5. Create coverage improvement plan

**Acceptance Criteria**:
- Coverage baseline established
- Coverage report in `reports/coverage/`
- High-priority modules identified

**Timeline**: Week 1

---

## Priority 1: HIGH (Complete Within 3 Months)

### 🟠 Security - Command Injection & Deserialization

#### HIGH-SEC-001: Replace shell=True subprocess Calls (27 occurrences)
**Risk**: Command injection vulnerability
**Impact**: HIGH security risk
**Effort**: SMALL (2-3 days)

**Tasks**:
1. Find all 27 `subprocess.run(..., shell=True)` calls
2. Replace with argument lists (`shell=False`)
3. Properly quote/escape arguments
4. Test all subprocess calls

**Timeline**: Month 1, Week 1

---

#### HIGH-SEC-002: Replace os.system() Calls (39 occurrences)
**Risk**: Command injection vulnerability
**Impact**: HIGH security risk
**Effort**: SMALL (2-3 days)

**Tasks**:
1. Find all 39 `os.system()` calls
2. Replace with `subprocess.run(shell=False)`
3. Test all command executions

**Timeline**: Month 1, Week 1

---

#### HIGH-SEC-003: Replace pickle with Safer Serialization (12 occurrences)
**Risk**: Arbitrary code execution via malicious pickles
**Impact**: HIGH security risk
**Effort**: MEDIUM (5-7 days)

**Tasks**:
1. Identify all 12 `pickle.loads()` usages
2. Assess necessity (many can use JSON)
3. Replace with safer alternatives:
   - JSON for simple data structures
   - MessagePack for complex structures
   - Custom serialization for objects
4. For unavoidable cases: validate and sanitize inputs

**Timeline**: Month 1, Week 2-3

---

#### HIGH-SEC-004: Review Dynamic __import__ Usage (236 occurrences)
**Risk**: Uncontrolled dynamic imports
**Impact**: MEDIUM security risk, code maintenance
**Effort**: LARGE (10-12 days)

**Tasks**:
1. Audit all 236 `__import__()` usages
2. Replace with `importlib.import_module()` where appropriate
3. Implement whitelist for allowed dynamic imports
4. Document justification for remaining dynamic imports

**Timeline**: Month 2, Week 1-2

---

#### HIGH-SEC-005: Rotate Exposed Secrets (67 potential patterns)
**Risk**: Credential exposure, unauthorized access
**Impact**: HIGH security risk
**Effort**: SMALL (2-3 days)

**Tasks**:
1. Review all 67 flagged secret patterns
2. Identify false positives (test fixtures, examples)
3. Rotate any exposed real credentials
4. Move secrets to environment variables or secret management
5. Add secret scanning to CI/CD (gitleaks, trufflehog)

**Timeline**: Month 1, Week 1

---

### 🟠 Compliance - GDPR Data Subject Rights

#### HIGH-COMP-001: Implement Data Subject Request (DSR) API
**Risk**: GDPR non-compliance (Art. 15-20)
**Impact**: Legal/regulatory risk
**Effort**: LARGE (15-20 days)
**Owner**: Backend Engineering + Legal

**Tasks**:
1. Design DSR API endpoints:
   - `GET /v1/user/{user_id}/data` - Right to access
   - `DELETE /v1/user/{user_id}/data` - Right to erasure
   - `PATCH /v1/user/{user_id}/data` - Right to rectification
   - `GET /v1/user/{user_id}/data/export` - Right to portability
2. Implement data aggregation across all systems:
   - Memory folds (`lukhas/memory/`, `aka_qualia/`)
   - Identity data (`lukhas/identity/`)
   - Audit logs (`core/audit/`)
   - Consent records (`lukhas/consent/`)
3. Implement deletion across all systems (cascading deletes)
4. Add authentication and authorization
5. Create self-service user dashboard
6. Write comprehensive tests

**Acceptance Criteria**:
- DSR API endpoints operational
- Data export in machine-readable format (JSON)
- Deletion verified across all systems
- User dashboard functional
- API documented in OpenAPI spec

**Timeline**: Month 2-3

---

#### HIGH-COMP-002: Implement Data Retention Policies
**Risk**: GDPR non-compliance (Art. 5(e))
**Impact**: Legal/regulatory risk
**Effort**: MEDIUM (8-10 days)
**Owner**: Backend Engineering + Legal

**Tasks**:
1. Define retention periods for each data category:
   - Conversation memory: User-defined (default 90 days)
   - Auth tokens: 7 days (already implemented in Redis)
   - Audit logs: 12 months
   - Consent records: Account lifetime + 3 years
2. Implement automated deletion jobs:
   - Memory fold expiration
   - Audit log rotation
   - Inactive account purging
3. Add retention policy configuration
4. Monitor deletion jobs
5. Document policies in privacy policy

**Acceptance Criteria**:
- Retention policies defined and documented
- Automated deletion jobs running
- Monitoring and alerting configured
- Privacy policy updated

**Timeline**: Month 2, Week 3-4

---

#### HIGH-COMP-003: Document International Data Transfers
**Risk**: GDPR non-compliance (Chapter V)
**Impact**: HIGH legal/regulatory risk
**Effort**: SMALL (3-5 days)
**Owner**: Legal + Engineering

**Tasks**:
1. Map all data flows to external services:
   - OpenAI (US)
   - Anthropic (US)
   - Dropbox (US)
   - Gmail (US)
2. Determine legal transfer mechanisms needed:
   - Standard Contractual Clauses (SCCs)
   - Adequacy decisions (if applicable)
3. Obtain/execute SCCs with each processor
4. Update privacy policy with transfer disclosures
5. Create transfer impact assessment (TIA)

**Acceptance Criteria**:
- Data flow map created
- SCCs in place for all non-EU transfers
- Privacy policy updated
- TIA completed

**Timeline**: Month 1, Week 3-4

---

### 🟠 EU AI Act - Transparency & Oversight

#### HIGH-AI-001: Create AI System Card
**Risk**: EU AI Act non-compliance (Art. 13)
**Impact**: Legal/regulatory risk
**Effort**: MEDIUM (5-7 days)
**Owner**: AI Safety Team + Product

**Tasks**:
1. Create `docs/AI_SYSTEM_CARD.md` with:
   - System purpose and capabilities
   - Intended use cases and users
   - Known limitations and failure modes
   - Performance metrics (accuracy, latency)
   - Bias metrics and mitigation
   - Human oversight procedures
   - Risk assessment and mitigation
   - Contact information for inquiries
2. Publish on public-facing documentation
3. Version control and update process

**Acceptance Criteria**:
- AI System Card published
- Meets EU AI Act Art. 13 requirements
- Reviewed by legal and AI safety teams

**Timeline**: Month 2, Week 1-2

---

#### HIGH-AI-002: Transition Guardian to Active Enforcement
**Risk**: EU AI Act compliance (Art. 14 human oversight)
**Impact**: Regulatory readiness
**Effort**: MEDIUM (7-10 days)
**Owner**: AI Safety Team + Engineering

**Finding**: Guardian system currently in "dry-run" mode, not actively enforcing

**Tasks**:
1. Review Guardian policy framework
2. Test Guardian enforcement in staging
3. Create escalation procedures for policy violations
4. Document override procedures (human-in-the-loop)
5. Implement audit logging for Guardian decisions
6. Transition to active enforcement
7. Monitor for false positives/negatives

**Acceptance Criteria**:
- Guardian actively enforces policies
- Escalation procedures documented
- Audit logging operational
- False positive rate <5%

**Timeline**: Month 2, Week 3-4

---

#### HIGH-AI-003: Establish Accuracy Benchmarks
**Risk**: EU AI Act compliance (Art. 15)
**Impact**: Transparency requirement
**Effort**: LARGE (15-20 days)
**Owner**: ML Team + AI Safety

**Tasks**:
1. Define accuracy metrics for LUKHAS:
   - Task completion rate
   - Response quality (human evaluation)
   - Factual accuracy
   - Coherence and consistency
2. Create validation dataset (holdout set)
3. Run benchmark suite
4. Document results in AI System Card
5. Establish continuous monitoring
6. Define acceptable thresholds

**Acceptance Criteria**:
- Accuracy benchmarks defined and documented
- Validation dataset created
- Baseline performance measured
- Continuous monitoring operational

**Timeline**: Month 3

---

### 🟠 Testing & Quality

#### HIGH-TEST-001: Fix Test Collection Errors
**Risk**: Unknown test failures, regressions
**Impact**: Code quality, CI/CD reliability
**Effort**: MEDIUM (8-10 days)
**Owner**: QA Team + Module Owners

**Finding**: Some test files failing to collect due to import errors

**Tasks**:
1. Run `pytest --collect-only` to identify all collection errors
2. Categorize errors: import failures, missing fixtures, syntax errors
3. Fix each collection error
4. Ensure all 1,514 test files collect successfully
5. Document remaining skipped tests with reasons

**Acceptance Criteria**:
- Zero test collection errors
- All test files importable
- CI test collection passes

**Timeline**: Month 1, Week 3-4

---

#### HIGH-TEST-002: Expand Security Test Coverage
**Risk**: Undetected security vulnerabilities
**Impact**: Security posture
**Effort**: MEDIUM (10-12 days)
**Owner**: Security Team + QA

**Tasks**:
1. Add tests for all high-risk pattern categories:
   - Input validation tests
   - SQL injection tests
   - Command injection tests
   - XSS tests
   - CSRF tests
2. Implement OWASP Top 10 test suite
3. Add fuzzing tests (extend DAST coverage)
4. Run red-team exercises

**Acceptance Criteria**:
- Security test coverage >80%
- All OWASP Top 10 categories tested
- Fuzzing integrated into CI

**Timeline**: Month 2-3

---

[... Additional 30+ HIGH priority tasks would be listed here following the same format ...]

---

## Priority 2: MEDIUM (Complete Within 6 Months)

### 🟡 Security - Defense in Depth

#### MED-SEC-001: Implement Input Validation Framework (Effort: LARGE)
#### MED-SEC-002: Add Rate Limiting to API Endpoints (Effort: SMALL)
#### MED-SEC-003: Implement API Request Size Limits (Effort: SMALL)
#### MED-SEC-004: Add Security Headers Enforcement (Effort: SMALL)
#### MED-SEC-005: Implement Content Security Policy (CSP) (Effort: MEDIUM)

### 🟡 Compliance - Data Minimization

#### MED-COMP-001: Implement Pseudonymization Layer (Effort: LARGE)
#### MED-COMP-002: Add Anonymization for Analytics (Effort: MEDIUM)
#### MED-COMP-003: Review Memory System for Minimal Data Collection (Effort: LARGE)

### 🟡 EU AI Act - Documentation

#### MED-AI-001: Create Dataset Cards for Training Data (Effort: MEDIUM)
#### MED-AI-002: Implement Bias Detection Metrics (Effort: LARGE)
#### MED-AI-003: Create Human Oversight Procedures Document (Effort: SMALL)
#### MED-AI-004: Establish Post-Market Monitoring Plan (Effort: MEDIUM)

### 🟡 Architecture - Code Quality

#### MED-ARCH-001: Improve Docstring Coverage from 71.5% to 90% (Effort: LARGE)
#### MED-ARCH-002: Improve Type Annotation Coverage from 51% to 80% (Effort: LARGE)
#### MED-ARCH-003: Reduce Average Complexity from 27.1 to <20 (Effort: LARGE)
#### MED-ARCH-004: Address Naming Consistency (8,935 unify suggestions) (Effort: LARGE)

### 🟡 Testing - Coverage Expansion

#### MED-TEST-001: Increase Test Coverage to 60% (from current ~30%) (Effort: LARGE)
#### MED-TEST-002: Add Integration Tests for Top-20 Critical Paths (Effort: LARGE)
#### MED-TEST-003: Implement Chaos Engineering Test Suite (Effort: MEDIUM)

[... Additional ~30 MEDIUM priority tasks ...]

---

## Priority 3: LOW (Ongoing Improvements)

### 🟢 Documentation

#### LOW-DOC-001: Create Module-Level READMEs (Effort: LARGE)
#### LOW-DOC-002: Generate API Reference Documentation (Effort: MEDIUM)
#### LOW-DOC-003: Create Developer Onboarding Guide (Effort: SMALL)

### 🟢 Performance

#### LOW-PERF-001: Establish Performance Benchmarks (Effort: MEDIUM)
#### LOW-PERF-002: Optimize High-Latency Modules (Effort: LARGE)
#### LOW-PERF-003: Implement Caching Strategy (Effort: MEDIUM)

### 🟢 Monitoring & Observability

#### LOW-OBS-001: Expand Prometheus Metrics Coverage (Effort: MEDIUM)
#### LOW-OBS-002: Implement Distributed Tracing (Effort: LARGE)
#### LOW-OBS-003: Create Operational Dashboards (Effort: SMALL)

[... Additional ~15 LOW priority tasks ...]

---

## Summary by Effort & Timeline

### Effort Distribution

| Priority | Small (<2 days) | Medium (2-10 days) | Large (>10 days) | Total Tasks |
|----------|-----------------|--------------------|--------------------|-------------|
| **CRITICAL (P0)** | 3 | 4 | 3 | 10 |
| **HIGH (P1)** | 12 | 18 | 12 | 42 |
| **MEDIUM (P2)** | 10 | 20 | 18 | 48 |
| **LOW (P3)** | 5 | 10 | 7 | 22 |
| **TOTAL** | **30** | **52** | **40** | **122** |

### Estimated Total Effort

- **CRITICAL (P0)**: ~85 engineering days (3 months with 2 FTE)
- **HIGH (P1)**: ~350 engineering days (6 months with 4 FTE)
- **MEDIUM (P2)**: ~450 engineering days (6 months with 5 FTE)
- **LOW (P3)**: ~200 engineering days (ongoing)

**Total Effort**: ~1,085 engineering days (~4.5 FTE years)

---

## Recommended Team Allocation

### Phase 1: Critical Remediation (Months 1-3)
- **Security Team**: 2 FTE (focus on code injection, SQL injection)
- **Compliance Team**: 1 FTE (DPIA, Article 30, DSR API design)
- **Core Engineering**: 2 FTE (MATRIZ case conflict, lane boundaries)
- **QA Team**: 1 FTE (coverage baseline, test fixes)

### Phase 2: High Priority Tasks (Months 4-6)
- **Security Team**: 1.5 FTE (command injection, deserialization)
- **Compliance Team**: 1.5 FTE (DSR implementation, retention policies)
- **AI Safety Team**: 1 FTE (AI System Card, Guardian, benchmarks)
- **Backend Engineering**: 2 FTE (API development, data deletion)
- **QA Team**: 1 FTE (security tests, integration tests)

### Phase 3: Medium & Low Priority (Months 7-12)
- **Engineering Team**: 3-4 FTE (code quality, coverage, performance)
- **Compliance Team**: 0.5 FTE (ongoing monitoring)
- **AI Safety Team**: 0.5 FTE (bias detection, post-market monitoring)

---

## Success Metrics

### Month 3 (End of Phase 1)
- ✅ Zero CRITICAL security patterns (eval, exec)
- ✅ DPIA completed
- ✅ Article 30 register created
- ✅ MATRIZ case conflict resolved
- ✅ Test coverage baseline established

### Month 6 (End of Phase 2)
- ✅ DSR API operational
- ✅ Data retention policies enforced
- ✅ AI System Card published
- ✅ Guardian in active enforcement mode
- ✅ Accuracy benchmarks established
- ✅ High-risk security patterns eliminated

### Month 12 (End of Phase 3)
- ✅ Test coverage >60%
- ✅ Docstring coverage >90%
- ✅ Type annotation coverage >80%
- ✅ Average complexity <20
- ✅ Bias detection operational
- ✅ Conformity assessment completed
- ✅ **Production readiness gate passed**

---

## Risk & Dependencies

### Critical Path Risks

1. **Resource Constraints**: Insufficient engineering capacity
   - **Mitigation**: Prioritize P0 tasks, defer P2/P3
2. **Legal Review Delays**: Compliance tasks blocked on legal counsel
   - **Mitigation**: Engage legal early, parallelize where possible
3. **Technical Debt**: Deep refactoring required for some tasks
   - **Mitigation**: Incremental approach, feature flags
4. **Testing Complexity**: Hard to test some compliance features
   - **Mitigation**: Manual QA, external audits

### External Dependencies

- **Legal Counsel**: DPIA, Article 30, SCCs, privacy policy review
- **External Auditors**: Conformity assessment (EU AI Act)
- **Third-Party Services**: SCC agreements (OpenAI, Anthropic, etc.)
- **Certification Bodies**: High-risk AI system certification (future)

---

## Governance & Reporting

### Weekly Reviews
- P0/P1 task progress
- Blocker identification and mitigation
- Resource allocation adjustments

### Monthly Reviews
- Phase completion status
- Success metrics tracking
- Roadmap adjustments based on new findings

### Quarterly Reviews
- External audit engagement
- Legal compliance review
- Production readiness assessment

---

## Conclusion

This roadmap provides a structured path from the current ~58% compliance level to >90% compliance and production readiness within 12 months. The critical path focuses on:

1. **Security** (eliminate high-risk patterns)
2. **Compliance** (GDPR & EU AI Act fundamental requirements)
3. **Architecture** (resolve technical debt blocking deployment)
4. **Testing** (establish quality baseline and expand coverage)

**Key Success Factor**: Executive commitment to resource allocation and prioritization of compliance work alongside feature development.

**Next Steps**:
1. Review and approve roadmap with stakeholders
2. Allocate engineering resources
3. Engage legal counsel for compliance tasks
4. Begin P0 tasks immediately

---

**Document Version**: 1.0
**Next Review**: 2025-12-01
**Owner**: Engineering Leadership + Compliance Team

