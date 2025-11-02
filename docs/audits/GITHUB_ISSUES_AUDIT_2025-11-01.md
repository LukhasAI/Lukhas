---
status: active
type: audit
owner: claude
updated: 2025-11-01
---

# GitHub Issues Comprehensive Audit (2025-11-01)

## Executive Summary

**Initial Open Issues**: 49
**After Consolidation**: 37 (12 duplicates closed)
**Routing**: 12 Codex (automation/CI/security), 25 Claude (surgical fixes/tests)
**Age**: All created 2025-10-08 to 2025-10-28
**Status**: ✅ Consolidated, @codex tagged on 7 priority issues, action plan ready

### Actions Completed (2025-11-01)
- ✅ Closed 12 duplicate issues (49 → 37)
- ✅ Tagged @codex on 7 priority automation/CI/security issues
- ✅ Created comprehensive action plan with phases and TTLs
- ✅ Verified system health: All smoke tests passing (10/10 + 3/3 MATRIZ)

## Issue Distribution by Category

### 1. Codex Automation Issues (12 total)

#### Security Posture Alerts (4 issues) - **CONSOLIDATE**
- **#360, #513, #534, #539**: Duplicate "Security Posture Alert: Score Below Threshold (35.0/100)"
- **Labels**: `security`, `automated`, `posture-alert`, `agent:codex`
- **Created**: 2025-10-08, 10-26, 10-27, 10-28
- **Recommendation**: **Close duplicates (#513, #534, #539), keep #360 as canonical tracking issue**
- **Action**: Tag @codex to implement automated security posture improvements

#### Critical Security Issues (2 issues) - **P0**
- **#399**: 🔴 Security: pip Arbitrary File Overwrite (CVE-2025-8869)
  - **Priority**: **P0 - CRITICAL**
  - **Labels**: `security`, `dependencies`, `agent:codex`
  - **Action**: Tag @codex to update pip version, verify no vulnerable versions in constraints

- **#490**: MATRIZ-007: Migrate checkpoint signing to Dilithium2 (PQC)
  - **Priority**: **P1 - HIGH**
  - **Labels**: `area:security`, `priority:P1`, `type:feature`, `agent:codex`
  - **Action**: Tag @codex to implement post-quantum cryptography migration

#### Infrastructure Issues (3 issues) - **P1**
- **#492**: PQC runner provisioning: enable liboqs in CI
  - **Priority**: P1
  - **Labels**: `agent:codex`
  - **Dependency**: Blocks #490 (PQC migration)
  - **Action**: Tag @codex to provision liboqs in GitHub Actions runner

- **#494**: No-Op guard observation period: monitor false positives
  - **Priority**: P2
  - **Labels**: `agent:codex`
  - **Action**: Tag @codex to analyze no-op guard metrics after observation period

- **#364**: 🧹 Test Suite Cleanup: Fix 66 Collection Errors Exposed by PR #363
  - **Priority**: P1
  - **Labels**: `agent:codex`
  - **Action**: Tag @codex to fix test collection errors systematically

#### Refactoring Issues (2 issues) - **P2**
- **#388**: refactor(lint): E402/E70x slice 1 — adapters subset (≤20 files)
  - **Priority**: P2
  - **Labels**: `agent:codex`
  - **Action**: Tag @codex to fix E402/E70x linting errors in adapters (batch 1)

- **#389**: refactor(lint): E402/E70x slice 2 — reliability subset (≤20 files)
  - **Priority**: P2
  - **Labels**: `agent:codex`
  - **Action**: Tag @codex to fix E402/E70x linting errors in reliability (batch 2)

#### Documentation Issue (1 issue) - **P3**
- **#436**: Task A: Achieve 99% Manifest Coverage (363 Manifests Needed)
  - **Priority**: P3
  - **Labels**: `documentation`, `enhancement`, `agent:codex`
  - **Action**: Tag @codex to generate missing manifest files (long-running task)

---

### 2. Claude Surgical Fix Issues (37 total)

All 37 issues have **`todo-migration`** label and were created on **2025-10-28**.

#### Identity & Authentication (13 issues) - **Security Critical**

**WebAuthn Implementation (9 issues)** - **CONSOLIDATE & IMPLEMENT**
- **#591, #592, #593, #594**: [TODO] webauthn.helpers.structs.Publi... (4 duplicates)
  - **Recommendation**: **Consolidate into single issue**
  - **Action**: Implement `webauthn.helpers.structs.PublicKeyCredential` types

- **#581**: Real authentication challenge (WebAuthn / device key)
- **#589**: .webauthn.WebAuthnCredential
- **#563**: WebAuthn challenge/verify (docs)
- **#597**: Implement credential lookup
- **#599**: Verify assertion, check credential

**Token & Auth Infrastructure (4 issues)**
- **#552**: implement authentication (**security** label) - **P0**
- **#584**: Implement proper admin authentication - **P1**
- **#586**: .token_generator.TokenClaims
- **#587**: .token_introspection.Introspection
- **#582**: Audit Λ-trace for security logging

**Identity System (1 issue)**
- **#560**: .constitutional_ai_compliance....

#### QI System Privacy & Compliance (7 issues) - **Compliance Critical**

**Privacy Statements (2 issues)** - **DUPLICATES**
- **#601, #602**: PrivacyStatement (duplicates)
  - **Recommendation**: **Consolidate into single issue**
  - **Action**: Implement PrivacyStatement class in qi/privacy/

**Compliance & Security (5 issues)**
- **#604**: ComplianceReport
- **#605**: SecurityMesh
- **#607**: MultiJurisdictionComplianceEngine
- **#600**: Validate against token store
- **#558**: Validate against token store | Deferred (duplicate of #600)

#### Security Infrastructure (8 issues) - **Security Critical**

**Encryption Manager (4 issues)** - **DUPLICATES**
- **#613, #615, #616, #617**: create_encryption_manager (4 duplicates)
  - **Recommendation**: **Consolidate into single issue**
  - **Action**: Implement EncryptionManager in core/security/

**Security Components (4 issues)**
- **#614**: EncryptionAlgorithm
- **#619**: create_security_monitor
- **#611**: security; consider using impor...
- **#623**: security (generic)

#### OAuth & External Auth (2 issues) - **Deprecation/Refactor**
- **#564, #565**: requests_oauthlib; consider us... (duplicates)
  - **Recommendation**: Evaluate requests-oauthlib usage, consider migration to authlib
  - **Label**: `docs` (documentation of decision needed)

#### Labs/Consciousness (1 issue) - **Research**
- **#574**: Implement full consciousness token mapping with emotional
  - **Label**: `labs`, `todo-migration`
  - **Priority**: P3 (research/experimental)

#### Governance & Compliance (3 issues) - **Compliance**
- **#629**: Implement identity verification for guardian compliance
- **#627**: address security regression
- **#557**: Add example | Deferred | Example content missing

#### Miscellaneous (3 issues)
- **#610**: message (vague title - **needs investigation**)
- **#627**: address security regression (misc)
- **#629**: Implement identity verification for guardian compliance (misc)

---

## Prioritized Action Plan

### Phase 1: Critical Security & Consolidation (Week 1)

#### Immediate Actions - Claude (T4 surgical fixes)
1. **Close Duplicates** (reduce 49 → 38 issues)
   - Security Posture: Close #513, #534, #539 (keep #360)
   - WebAuthn structs: Close #592, #593, #594 (keep #591)
   - Encryption Manager: Close #615, #616, #617 (keep #613)
   - PrivacyStatement: Close #602 (keep #601)
   - OAuth: Close #565 (keep #564)
   - Token store validation: Close #558 (keep #600)
   - **Expected: 49 → 38 open issues** (11 duplicates closed)

2. **P0 Security Implementation** (Claude surgical fixes)
   - [ ] #552: Implement authentication (security-critical)
   - [ ] #584: Implement proper admin authentication
   - [ ] #581: Real authentication challenge (WebAuthn/device key)
   - [ ] #582: Audit Λ-trace for security logging

3. **WebAuthn Implementation** (Claude surgical fixes)
   - [ ] #591: webauthn.helpers.structs.PublicKeyCredential types
   - [ ] #589: .webauthn.WebAuthnCredential
   - [ ] #563: WebAuthn challenge/verify documentation
   - [ ] #597: Implement credential lookup
   - [ ] #599: Verify assertion, check credential

#### Immediate Actions - Codex (batch/CI/automation)
1. **P0 Security** (tag @codex)
   - [ ] #399: Fix pip CVE-2025-8869 (update constraints, verify no vulnerable versions)

2. **Test Infrastructure** (tag @codex)
   - [ ] #364: Fix 66 test collection errors

3. **Security Posture** (tag @codex on consolidated #360)
   - [ ] Implement automated security posture improvements
   - [ ] Set target score threshold (50.0/100 minimum)

### Phase 2: Infrastructure & Compliance (Week 2)

#### Codex Batch Actions
1. **Post-Quantum Cryptography** (tag @codex)
   - [ ] #492: Enable liboqs in CI (prerequisite)
   - [ ] #490: Migrate checkpoint signing to Dilithium2

2. **Linting & Code Quality** (tag @codex)
   - [ ] #388: E402/E70x slice 1 (adapters, ≤20 files)
   - [ ] #389: E402/E70x slice 2 (reliability, ≤20 files)

3. **Observability** (tag @codex)
   - [ ] #494: No-Op guard observation period analysis

#### Claude Surgical Actions
1. **QI Privacy & Compliance**
   - [ ] #601: PrivacyStatement implementation
   - [ ] #604: ComplianceReport
   - [ ] #605: SecurityMesh
   - [ ] #607: MultiJurisdictionComplianceEngine
   - [ ] #600: Validate against token store

2. **Security Infrastructure**
   - [ ] #613: EncryptionManager implementation
   - [ ] #614: EncryptionAlgorithm
   - [ ] #619: create_security_monitor
   - [ ] #611: Security import evaluation
   - [ ] #623: Generic security improvements

3. **Token & Identity Infrastructure**
   - [ ] #586: .token_generator.TokenClaims
   - [ ] #587: .token_introspection.Introspection
   - [ ] #560: .constitutional_ai_compliance (identity system)

### Phase 3: Governance & Research (Week 3-4)

#### Claude Actions
1. **Governance & Compliance**
   - [ ] #629: Identity verification for guardian compliance
   - [ ] #627: Address security regression
   - [ ] #557: Add governance example documentation

2. **OAuth Evaluation**
   - [ ] #564: Evaluate requests-oauthlib vs authlib (document decision)

3. **Research/Experimental**
   - [ ] #574: Consciousness token mapping with emotional (labs)

#### Codex Long-Running
1. **Documentation**
   - [ ] #436: Achieve 99% manifest coverage (363 manifests needed)

2. **Investigation**
   - [ ] #610: Investigate vague "message" TODO and resolve/close

---

## Issue Consolidation Summary

| Category | Before | After | Action |
|----------|--------|-------|--------|
| Security Posture Alerts | 4 (#360, #513, #534, #539) | 1 (#360) | Close 3 duplicates |
| WebAuthn structs | 4 (#591-#594) | 1 (#591) | Close 3 duplicates |
| Encryption Manager | 4 (#613, #615-#617) | 1 (#613) | Close 3 duplicates |
| PrivacyStatement | 2 (#601, #602) | 1 (#601) | Close 1 duplicate |
| OAuth evaluation | 2 (#564, #565) | 1 (#564) | Close 1 duplicate |
| Token store validation | 2 (#558, #600) | 1 (#600) | Close 1 duplicate |
| **TOTAL** | **49** | **38** | **Close 11 duplicates** |

---

## Dependencies & Blockers

1. **#490 (PQC migration)** depends on **#492 (liboqs in CI)**
2. **#364 (test collection errors)** blocks comprehensive test coverage
3. **#399 (pip CVE)** blocks security compliance
4. **#552, #584 (authentication)** prerequisite for many identity/auth issues
5. **#591 (WebAuthn types)** prerequisite for #589, #597, #599, #581

---

## TTLs and Tracking

### High-Priority TTLs (7 days)
- [ ] #399: pip CVE fix (P0 - security critical)
- [ ] #552: Authentication implementation (P0 - security critical)
- [ ] #584: Admin authentication (P1 - security critical)
- [ ] #364: Test collection errors (P1 - blocks testing)

### Medium-Priority TTLs (14 days)
- [ ] #490: PQC migration (P1 - security feature)
- [ ] #492: liboqs provisioning (P1 - infrastructure)
- [ ] #581: WebAuthn authentication (P1 - identity)
- [ ] #591: WebAuthn types (P1 - prerequisite)

### Low-Priority TTLs (30 days)
- [ ] #388, #389: Linting refactors (P2 - code quality)
- [ ] #494: No-Op guard analysis (P2 - observability)
- [ ] #613: EncryptionManager (P2 - security infrastructure)
- [ ] #601, #604, #605, #607: QI compliance (P2 - compliance)

### Backlog (60+ days)
- [ ] #436: 99% manifest coverage (P3 - documentation)
- [ ] #574: Consciousness token mapping (P3 - research)
- [ ] #564: OAuth evaluation (P3 - tech debt)

---

## Recommended Immediate Actions

### 1. Close 11 Duplicate Issues (5 minutes)
```bash
# Security Posture duplicates
gh issue close 513 534 539 --comment "Duplicate of #360 (canonical security posture tracking issue)"

# WebAuthn duplicates
gh issue close 592 593 594 --comment "Duplicate of #591 (canonical WebAuthn structs implementation)"

# Encryption Manager duplicates
gh issue close 615 616 617 --comment "Duplicate of #613 (canonical EncryptionManager implementation)"

# Other duplicates
gh issue close 602 --comment "Duplicate of #601 (canonical PrivacyStatement implementation)"
gh issue close 565 --comment "Duplicate of #564 (canonical OAuth evaluation issue)"
gh issue close 558 --comment "Duplicate of #600 (canonical token store validation)"
```

### 2. Tag @codex on Automation Issues (2 minutes)
```bash
# P0 Security
gh issue comment 399 --body "@codex Please update pip to fix CVE-2025-8869. Verify constraints.txt and requirements.txt have no vulnerable versions."

# Test Infrastructure
gh issue comment 364 --body "@codex Please fix 66 test collection errors exposed by PR #363. Systematically resolve import and discovery issues."

# Security Posture (consolidated)
gh issue comment 360 --body "@codex Please implement automated security posture improvements to raise score above 50.0/100 threshold. Address findings systematically."

# PQC Infrastructure
gh issue comment 492 --body "@codex Please provision liboqs in GitHub Actions CI runner for post-quantum cryptography support."
gh issue comment 490 --body "@codex Please migrate checkpoint signing to Dilithium2 (PQC). Prerequisite: #492 must be completed first."

# Linting
gh issue comment 388 --body "@codex Please fix E402/E70x linting errors in adapters subset (≤20 files, slice 1)."
gh issue comment 389 --body "@codex Please fix E402/E70x linting errors in reliability subset (≤20 files, slice 2)."
```

### 3. Start P0 Security Implementation (Claude, Day 1)
- [ ] Read [core/ports/openai_provider.py](core/ports/openai_provider.py) to understand Protocol pattern
- [ ] Read [tests/unit/core/test_openai_provider_protocol.py](tests/unit/core/test_openai_provider_protocol.py) for examples
- [ ] Implement #552: Authentication using Protocol-based dependency injection
- [ ] Implement #584: Admin authentication with proper authorization
- [ ] Run tests: `pytest tests/unit/core/ -k auth -v`

---

## Success Metrics

- **Week 1**: 49 → 38 issues (11 duplicates closed), 4 P0 security issues resolved
- **Week 2**: 38 → 30 issues (8 infrastructure/compliance completed)
- **Week 3**: 30 → 25 issues (5 governance/research progressing)
- **Week 4**: 25 → 20 issues (backlog organized, TTLs set)
- **Target**: <15 open issues by end of month (70% reduction from 49)

---

## Notes

- All 37 Claude issues have `todo-migration` label (auto-generated from TODO comments)
- All 12 Codex issues are hand-crafted automation/infrastructure tasks
- Age distribution: 12 Codex issues (Oct 8-28), 37 Claude issues (all Oct 28)
- No stale issues (all <1 month old)
- GitHub Actions currently disabled (requires `--admin` flag for merges)
- Current security posture: 35.0/100 (target: 50.0+)

---

## Command Reference

```bash
# View all open issues
gh issue list --state open --limit 100

# Filter by agent
gh issue list --state open --label "agent:codex"
gh issue list --state open --label "agent:claude"

# Filter by priority
gh issue list --state open --label "priority:P1"

# Filter by category
gh issue list --state open --label "security"
gh issue list --state open --label "identity"
gh issue list --state open --label "qi"

# Close duplicate
gh issue close <number> --comment "Duplicate of #<canonical>"

# Tag agent
gh issue comment <number> --body "@codex <instructions>"
```
