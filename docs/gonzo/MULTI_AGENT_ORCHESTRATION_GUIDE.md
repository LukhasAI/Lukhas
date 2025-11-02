---
status: active
type: orchestration-guide
owner: claude
updated: 2025-11-01
---

# Multi-Agent Orchestration Guide

This guide shows which tasks from our 37 open GitHub issues are best suited for each AI agent platform. Based on successful parallel execution of 3 prerequisite tasks with Claude Code agents.

---

## 🎯 Parallel Execution Results (Just Completed)

### ✅ Claude Code Agents - SUCCESSFUL

We just ran **3 agents in parallel** with excellent results:

1. **identity-auth-specialist** → #591 WebAuthn types
   - **Result**: ✅ Complete (220 lines types + 538 lines tests)
   - **Time**: ~2 hours
   - **Quality**: 30 tests, 100% pass, W3C spec compliant
   - **Unblocked**: 4 dependent issues (#581, #589, #597, #599)

2. **agent-lukhas-specialist** → #614 EncryptionAlgorithm enum
   - **Result**: ✅ Complete (343 lines + 656 lines tests)
   - **Time**: ~1 hour
   - **Quality**: 48 tests, 100% pass, 5 algorithms with metadata
   - **Unblocked**: #613 EncryptionManager implementation

3. **general-purpose** (haiku) → #610 Vague TODO investigation
   - **Result**: ✅ Complete (documentation fix)
   - **Time**: ~30 minutes
   - **Quality**: Root cause found, proper fix applied
   - **Closed**: Issue #610 resolved

**Total Impact**: 3 issues resolved, 5 issues unblocked, ~1,800 lines of production code + tests in <3 hours parallel execution.

---

## 🤖 Agent Capability Matrix

### GitHub Copilot (Workspace/Chat/Edits)

**Best Models**:
- **GPT-5-Codex (Preview)** - Best for complex implementations
- **Claude Sonnet 4.5** - Best for architecture and type safety
- **GPT-5** - Best for creative problem solving
- **Gemini 2.5 Pro** - Best for multi-file refactoring

**Ideal Tasks**:
✅ Boilerplate generation (DTOs, models, interfaces)
✅ Test case generation (happy path + edge cases)
✅ Refactoring within single file
✅ Code completion and small edits
✅ Documentation generation

**Recommended Issues from Our Backlog**:

#### 1. Token Infrastructure (#586, #587) - **GPT-5-Codex**
- **Why**: Straightforward DTOs and validation logic
- **Scope**: Create TypedDict definitions for TokenClaims and Introspection
- **Estimate**: 1-2 hours
- **Files**: 2-3 files (types, validation, tests)

```prompt
@workspace I need to implement TokenClaims and TokenIntrospection TypedDicts following the pattern in core/ports/openai_provider.py. These should match OAuth 2.0 RFC 7662 structure for token introspection. Include validation functions and comprehensive tests.
```

#### 2. OAuth Library Evaluation (#564) - **Claude Sonnet 4.5**
- **Why**: Requires architectural analysis and comparison
- **Scope**: Compare requests-oauthlib vs authlib with migration plan
- **Estimate**: 2-3 hours
- **Files**: 1 ADR document + analysis

```prompt
@workspace Analyze our current usage of requests-oauthlib across the codebase. Compare it with authlib in terms of: security, maintenance, features, and OAuth 2.1 compliance. Create an ADR (Architecture Decision Record) recommending whether to migrate, with effort estimate and migration plan.
```

#### 3. Governance Example (#557) - **GPT-5**
- **Why**: Creative example generation with explanation
- **Scope**: Working governance example with Guardian integration
- **Estimate**: 2-3 hours
- **Files**: 1 markdown doc + example code + tests

```prompt
Create a comprehensive governance example showing how to use the Guardian system for consent management and policy enforcement. Include: setup, policy definition, consent flow, enforcement, and audit trail. Add working code in examples/governance/ with tests.
```

#### 4. WebAuthn Documentation (#563) - **Gemini 2.5 Pro**
- **Why**: Multi-file analysis and comprehensive documentation
- **Scope**: Complete developer guide for WebAuthn in LUKHAS
- **Estimate**: 2-3 hours
- **Files**: 1 guide + API reference

```prompt
@workspace Create a comprehensive WebAuthn developer guide based on our implementation in lukhas/identity/. Cover: setup, registration flow, authentication flow, credential management, and troubleshooting. Include code examples from actual implementation and link to W3C spec.
```

---

### Agent Jules (AI Coding Agent)

**Capabilities**:
- Autonomous multi-step workflows
- File creation and modification
- Git operations (commit, branch, PR)
- Test execution and debugging
- Iterative problem solving

**Best Models** (if configurable):
- **GPT-4o** - Best balance of speed and capability
- **Claude Sonnet 4** - Best for complex logic
- **Grok Code Fast 1** - Best for speed on simple tasks

**Ideal Tasks**:
✅ End-to-end feature implementation
✅ Multi-file refactoring with tests
✅ Bug fixing with reproduction
✅ Integration work across modules
✅ Autonomous problem solving

**Recommended Issues from Our Backlog**:

#### 1. Admin Authentication (#584) - **Claude Sonnet 4**
- **Why**: Requires middleware implementation + integration testing
- **Scope**: Create admin auth middleware and integrate with routing
- **Estimate**: 3-4 hours
- **Files**: 3-5 files (middleware, decorators, tests, routing updates)
- **Dependency**: #552 (core auth) must be complete first

```jules-prompt
Implement admin authentication for lukhas/api/routing_admin.py using role-based access control. Create middleware in lukhas/api/middleware/admin_auth.py that:
1. Verifies admin/superadmin roles
2. Returns 401/403 appropriately
3. Integrates with ΛiD identity system
Include integration tests that verify the full auth flow. Follow the Protocol pattern from core/ports/openai_provider.py.
```

#### 2. WebAuthn Challenge/Verify (#581) - **GPT-4o**
- **Why**: Multi-component implementation (backend + frontend)
- **Scope**: Generate challenge endpoint + verify endpoint + update TSX component
- **Estimate**: 4-5 hours
- **Files**: 5-7 files (endpoints, validation, frontend component, E2E tests)
- **Dependency**: #591 (types) - ✅ COMPLETED

```jules-prompt
Implement WebAuthn challenge generation and verification in lukhas/identity/webauthn_challenge.py. Create two endpoints:
1. POST /api/webauthn/challenge - Generate cryptographically secure challenge
2. POST /api/webauthn/verify - Verify WebAuthn signature

Update lukhas_website/components/qrg-envelope.tsx to use real WebAuthn API instead of placeholder. Include E2E tests covering registration + authentication flow using the WebAuthn types from lukhas/identity/webauthn_types.py.
```

#### 3. SecurityMesh (#605) - **Claude Sonnet 4**
- **Why**: Complex multi-layer coordination requiring deep integration
- **Scope**: Security mesh for policy enforcement across layers
- **Estimate**: 5-6 hours
- **Files**: 4-6 files (mesh core, integrations, policy engine, tests)

```jules-prompt
Implement SecurityMesh in qi/security/security_mesh.py for multi-layer security coordination. Requirements:
1. Coordinate security across Guardian, QI, and Identity systems
2. Implement policy enforcement mesh with distributed trust verification
3. Performance target: <10ms overhead per request
4. Integration with existing security systems

Include comprehensive unit and integration tests. Follow the pattern from qi/privacy/ for QI system integration.
```

#### 4. ComplianceReport (#604) - **GPT-4o**
- **Why**: Data aggregation + report generation across multiple systems
- **Scope**: Multi-jurisdiction compliance reporting
- **Estimate**: 4-5 hours
- **Files**: 4-5 files (report generator, exporters, templates, tests)

```jules-prompt
Implement ComplianceReport in qi/compliance/compliance_report.py for GDPR/CCPA/HIPAA reporting. Requirements:
1. Track consent, data access, retention across all systems
2. Generate compliance reports (JSON/PDF export)
3. Integration with Guardian audit trail
4. Preserve complete audit trail

Include tests for each jurisdiction's requirements and export formats.
```

---

### Codex (ChatGPT Multi-Agent System)

**Capabilities**:
- Autonomous task execution
- Multi-file operations
- CI/CD integration
- Bulk refactoring
- Systematic code improvements
- PR creation and management

**Best For**:
✅ Batch operations (linting, formatting)
✅ Security vulnerability fixes
✅ Systematic refactoring
✅ CI/CD pipeline work
✅ Infrastructure as code

**Already Assigned** (7 issues):
- #399 (P0): pip CVE-2025-8869 fix
- #364 (P1): Fix 66 test collection errors
- #360 (P1): Security posture improvements
- #492, #490 (P1): PQC infrastructure + Dilithium2
- #388, #389 (P2): E402/E70x linting refactors

**Additional Recommended Issues**:

#### 1. EncryptionManager Implementation (#613) - **Codex**
- **Why**: Well-defined interface, systematic implementation
- **Scope**: Centralized encryption with multiple algorithms
- **Estimate**: 4-5 hours
- **Files**: 3-4 files (manager, tests, integration)
- **Dependency**: #614 - ✅ COMPLETED

```codex-comment
@codex Please implement EncryptionManager in core/security/encryption_manager.py using the EncryptionAlgorithm enum from core/security/encryption_types.py (already implemented).

Requirements:
1. Support AES-256-GCM and ChaCha20-Poly1305 (minimum)
2. Methods: encrypt(), decrypt(), generate_key()
3. Key rotation support
4. Authenticated encryption (AEAD) only
5. 100% test coverage including error cases
6. No keys in code/logs

Reference pattern: The EncryptionAlgorithm enum and metadata are in core/security/encryption_types.py. Use get_algorithm_metadata() to get correct key/nonce/tag sizes.

See Task 5 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md for full specification.
```

#### 2. SecurityMonitor Implementation (#619) - **Codex**
- **Why**: Systematic monitoring with metrics integration
- **Scope**: Real-time security event monitoring
- **Estimate**: 3-4 hours
- **Files**: 3-4 files (monitor, metrics, tests, integration)

```codex-comment
@codex Please implement SecurityMonitor in core/security/security_monitor.py for runtime security monitoring.

Requirements:
1. Monitor: auth failures, rate limit violations, anomalous behavior
2. Export Prometheus metrics (integrate with observability/ system)
3. Configurable alert thresholds
4. Performance: <5ms p95 overhead
5. Hook into authentication flow

See Task 7 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md for full specification.
```

#### 3. MultiJurisdictionComplianceEngine (#607) - **Codex**
- **Why**: Systematic rule engine with well-defined requirements
- **Scope**: Cross-jurisdiction compliance automation
- **Estimate**: 6-8 hours
- **Files**: 5-6 files (engine, rules, jurisdiction configs, tests)

```codex-comment
@codex Please implement MultiJurisdictionComplianceEngine in qi/compliance/multi_jurisdiction_engine.py.

Requirements:
1. Support GDPR, CCPA, PIPEDA, LGPD (4+ jurisdictions)
2. Automatic jurisdiction detection from user data
3. Apply most restrictive applicable rules
4. Configurable policy overrides
5. Rule engine for compliance policies
6. Tests covering all major jurisdictions

See Task 11 in docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md for full specification.
```

---

## 📊 Recommended Agent Assignment Summary

### Quick Wins (<2 hours) - **GitHub Copilot**
- #586, #587: Token infrastructure (TypedDicts)
- #610: ✅ COMPLETED (vague TODO investigation)

### Medium Tasks (2-4 hours) - **GitHub Copilot or Jules**
- #564: OAuth library evaluation (Copilot)
- #557: Governance example (Copilot)
- #563: WebAuthn documentation (Copilot)
- #601: PrivacyStatement (Jules)
- #600: Token store validation (Jules)

### Complex Tasks (4-8 hours) - **Jules or Codex**
- #584: Admin authentication (Jules)
- #581: WebAuthn challenge/verify (Jules)
- #613: EncryptionManager (Codex)
- #619: SecurityMonitor (Codex)
- #604: ComplianceReport (Jules)
- #605: SecurityMesh (Jules)
- #607: MultiJurisdictionEngine (Codex)

### Systematic/Infrastructure - **Codex** (Already Assigned)
- #399: pip CVE fix
- #364: Test collection errors
- #360: Security posture
- #492, #490: PQC migration
- #388, #389: Linting refactors

---

## 🎭 Agent Selection Decision Tree

```
Is the task < 2 hours and mostly boilerplate?
├─ YES → GitHub Copilot (GPT-5-Codex or Claude Sonnet 4.5)
└─ NO → Continue...

Does it require multi-file coordination and integration testing?
├─ YES → Agent Jules (Claude Sonnet 4 or GPT-4o)
└─ NO → Continue...

Is it systematic refactoring, CI/CD, or infrastructure work?
├─ YES → Codex (batch operations)
└─ NO → Continue...

Is it research/experimental work?
├─ YES → Claude Code labs-research agent
└─ NO → Claude Code specialized agent (identity/security/QI/docs)
```

---

## 🚀 Execution Strategy

### Phase 1 (This Week) - Prerequisites Complete ✅
- [x] #591: WebAuthn types (Claude identity-auth-specialist) - ✅ DONE
- [x] #614: EncryptionAlgorithm (Claude agent-lukhas-specialist) - ✅ DONE
- [x] #610: Vague TODO (Claude general-purpose) - ✅ DONE

**Unblocked**: 5 dependent issues ready to start

### Phase 2 (Next 2-3 Days) - Parallel Execution
**GitHub Copilot** (assign immediately):
- #586, #587: Token infrastructure (GPT-5-Codex, 2 hours)
- #564: OAuth evaluation (Claude Sonnet 4.5, 3 hours)

**Agent Jules** (assign immediately):
- #581: WebAuthn challenge/verify (GPT-4o, 5 hours) - dependency ✅ met
- #584: Admin authentication (Claude Sonnet 4, 4 hours)
- #601: PrivacyStatement (GPT-4o, 3 hours)

**Codex** (already tagged, monitor):
- #613: EncryptionManager (4 hours) - dependency ✅ met
- #619: SecurityMonitor (4 hours)

**Estimated Impact**: 7 issues resolved, 20-24 hours of parallel work completed in 2-3 days

### Phase 3 (Next Week) - Compliance & Docs
**GitHub Copilot**:
- #557: Governance example (GPT-5, 3 hours)
- #563: WebAuthn docs (Gemini 2.5 Pro, 3 hours)

**Agent Jules**:
- #604: ComplianceReport (GPT-4o, 5 hours)
- #605: SecurityMesh (Claude Sonnet 4, 6 hours)
- #600: Token store validation (GPT-4o, 4 hours)

**Codex**:
- #607: MultiJurisdictionEngine (8 hours)

**Estimated Impact**: 6 issues resolved

---

## 📈 Projected Results

**After 3 Weeks**:
- **Issues Resolved**: 16/37 Claude issues (43%)
- **Combined with Codex**: 16 + 12 = 28/49 total (57%)
- **Remaining**: 21 open issues
- **On Track**: Target <15 issues by month end (70% reduction)

**Quality Metrics** (based on successful parallel run):
- All implementations follow T4 standards
- 100% test coverage requirement
- Type safety with mypy/pyright
- Security review before merge
- Documented patterns and examples

---

## 🔧 Practical Commands

### GitHub Copilot Chat
```
# In VS Code, open Copilot Chat and reference the delegation plan
@workspace /ref docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md
Implement Task [N]: [Issue Title]
```

### Agent Jules
```bash
# If Jules supports issue references
jules --issue 584 --plan docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md#task-2

# Or via natural language
jules "Implement admin authentication following Task 2 in the delegation plan"
```

### Codex (via GitHub Issues)
```bash
# Already done - we tagged 7 issues earlier
gh issue view 613  # Check if Codex has started work
```

---

## ✅ Success Criteria

For each agent/task:
- [ ] Implementation follows T4 standards
- [ ] Tests included and passing
- [ ] Type checking passes (mypy/pyright)
- [ ] Security review for security-related tasks
- [ ] Documentation updated
- [ ] GitHub issue updated with progress
- [ ] PR created or code committed

---

## 🎓 Lessons Learned from Parallel Run

1. **Claude Code agents excel at**:
   - Well-defined interfaces (TypedDicts, Protocols, Enums)
   - Type-safe implementations
   - Comprehensive test generation
   - T4 standards compliance

2. **Prerequisites matter**:
   - Completing #591 and #614 first unblocked 5+ dependent tasks
   - Identify and prioritize prerequisite work

3. **Parallel execution works**:
   - 3 agents ran simultaneously without conflicts
   - Different specializations (identity, security, general) work well in parallel
   - Clear task boundaries prevent merge conflicts

4. **Model selection**:
   - Sonnet for complex type systems and architecture
   - Haiku for quick investigations (<1 hour)
   - Opus for research/exploration (not used yet)

---

## 📚 References

- Main Issue Audit: [docs/audits/GITHUB_ISSUES_AUDIT_2025-11-01.md](../audits/GITHUB_ISSUES_AUDIT_2025-11-01.md)
- Delegation Plan: [docs/gonzo/AGENT_DELEGATION_PLAN_2025-11-01.md](AGENT_DELEGATION_PLAN_2025-11-01.md)
- MATRIZ Audit: [docs/audits/MATRIZ_SYSTEM_AUDIT_2025-11-01.md](../audits/MATRIZ_SYSTEM_AUDIT_2025-11-01.md)
- T4 Standards: See CLAUDE.md and global .claude/CLAUDE.md
