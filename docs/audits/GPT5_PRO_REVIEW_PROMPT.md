# GPT-5 Pro Review Prompt - LUKHAS Pre-Launch Audit Analysis

**Date**: 2025-11-10
**Context**: LUKHAS AI pre-launch security and integration audit
**Reviewer**: GPT-5 Pro (o3-style reasoning model)
**Objective**: Critical review of audit findings and remediation roadmap

---

## Executive Summary for Review

LUKHAS AI is preparing for public launch with a sophisticated consciousness-aware architecture. We've conducted comprehensive audits of critical systems revealing **significant security and integration gaps** that must be addressed before production deployment.

**Three Major Audits Completed**:
1. **User ID Integration Audit** - Score: 55/100 (LAUNCH BLOCKER)
2. **Endocrine System Audit** - Score: 65/100 (Partially Ready)
3. **User Feedback System Audit** - Score: 70/100 (LAUNCH BLOCKER)

---

## Documents for Review

Please review the following audit documents (all located in `docs/audits/`):

### 1. User ID Integration Audit
**File**: `docs/audits/identity/USER_ID_INTEGRATION_AUDIT_2025-11-10.md` (684 lines)

**Key Findings**:
- ❌ API endpoints unprotected (no user_id enforcement)
- ❌ Middleware verifies JWT but doesn't attach user_id to request
- ❌ Memory operations lack user-level isolation (tenant-only)
- ❌ Dream/Consciousness operations have optional user_id
- ❌ Feature flags evaluate without required user_id
- ✅ Auth infrastructure solid but not integrated

**Launch Impact**: **CRITICAL BLOCKER**

---

### 2. Endocrine System Audit
**File**: `docs/audits/systems/ENDOCRINE_SYSTEM_AUDIT_2025-11-10.md` (550 lines)

**Key Findings**:
- ✅ Core system fully implemented (8 hormones, 11 interactions)
- ✅ VIVOX-ERN integration captures user_id
- ❌ Global singleton (no per-user hormone state)
- ❌ No production API endpoints
- ❌ No tier-based access control
- ⚠️  user_id captured but not used for isolation

**Launch Impact**: **MEDIUM** - Can launch with limitations

---

### 3. User Feedback System Audit
**File**: `docs/audits/systems/USER_FEEDBACK_SYSTEM_AUDIT_2025-11-10.md` (580 lines)

**Key Findings**:
- ✅ Complete API design with OpenAPI docs
- ❌ user_id is OPTIONAL (critical security gap)
- ❌ NO authentication required on ANY endpoint
- ❌ Backend NOT IMPLEMENTED (stub only)
- ❌ No rate limiting (DoS vulnerable)
- ❌ No GDPR/CCPA compliance

**Launch Impact**: **CRITICAL BLOCKER**

---

## System Architecture Context

LUKHAS uses a **three-lane development architecture**:
- **`candidate/`** (2,877 files) - Experimental research
- **`core/`** (253 components) - Integration/testing
- **`lukhas/`** (692 components) - Production-ready

**Lane Import Rules** (strictly enforced):
- `lukhas/` can import from `core/`, `matriz/`, `universal_language/`
- `candidate/` can import from `core/`, `matriz/` ONLY
- NO cross-lane contamination allowed

**Authentication System**:
- **6-tier access control** (PUBLIC → SYSTEM)
- **ΛiD token system** with Guardian validation
- **Tier permission matrix** with operation-level controls
- **Well-designed** but not enforced on routes

**Key Technologies**:
- Python 3.11, FastAPI, Pydantic
- Async architecture with asyncio
- SQLite/PostgreSQL for persistence
- Prometheus + Grafana for monitoring

---

## Questions for GPT-5 Pro

Please provide your analysis on the following critical questions:

### 1. Security Risk Assessment ⚠️

**Question**: Based on the three audits, what are the **TOP 5 security risks** that pose the greatest threat to LUKHAS in production?

**Context**:
- We have excellent authentication infrastructure (ΛiD + tier system)
- BUT: Not enforced on API routes
- user_id is optional in most data structures
- Memory operations lack user-level isolation
- Feedback system has no authentication

**Please Rank By**:
- Exploitability (how easy to exploit)
- Impact (damage if exploited)
- Likelihood (probability of occurrence)
- Remediation effort (hours to fix)

### 2. Remediation Priority Analysis 🎯

**Question**: We have **3 concurrent remediation roadmaps** (User ID, Endocrine, Feedback). Which order should we prioritize and why?

**Proposed Timelines**:
- **User ID Integration**: 4 weeks, 40 hours (Phase 1-2 BLOCKING)
- **Endocrine System**: 4 weeks, 35 hours (Phase 1-2 recommended)
- **User Feedback System**: 4 weeks, 56 hours (Phase 1-2 BLOCKING)

**Constraints**:
- 2-person engineering team
- 4-week pre-launch window
- Budget: ~120 hours total

**Please Analyze**:
- Can we parallelize any work?
- Which phases are truly blocking vs nice-to-have?
- Any dependencies between the three roadmaps?
- Minimum viable fixes to unblock launch?

### 3. Architecture Trade-offs 🏗️

**Question**: The **endocrine system is a global singleton** (single hormone state for all users). We recommend per-user state. What are the architectural trade-offs?

**Per-User State (Recommended)**:
- ✅ User isolation and privacy
- ✅ Personalized hormone profiles
- ✅ Individual neuroplasticity tracking
- ❌ Memory overhead (1 system × 1000 users = 1000 systems)
- ❌ Complexity in state management
- ❌ Cleanup of inactive user states needed

**Global State (Current)**:
- ✅ Simple implementation
- ✅ Low memory footprint
- ❌ No user isolation
- ❌ User A's stress affects User B
- ❌ Cannot model individual differences

**Please Evaluate**:
- Is per-user state truly necessary for MVP?
- Could we start with global and migrate later?
- What's the memory footprint of 1K-10K user endocrine systems?
- Any hybrid approaches (e.g., per-user state with shared baseline)?

### 4. Feedback System Implementation 💬

**Question**: The **feedback backend is a STUB** (not implemented). We propose 40-60 hours to fully implement. Is this estimate realistic?

**Required Components**:
1. Storage layer (database schema, indexes)
2. Pattern extraction (clustering, preference mining)
3. Policy update generation (from patterns)
4. Validation & safety checks
5. Learning cycle automation
6. Per-user analytics

**Complexity Factors**:
- Adversarial feedback resistance needed
- GDPR compliance (export, deletion, retention)
- Real-time pattern extraction vs batch
- Policy update merge logic
- Rollback mechanism for bad updates

**Please Assess**:
- Is 40-60 hours enough for this scope?
- What can we cut for MVP while keeping value?
- Which components are most complex?
- Any existing libraries/patterns we should leverage?

### 5. Compliance & Legal Risks ⚖️

**Question**: What are the **legal/compliance risks** of launching with current gaps?

**Known Issues**:
- **GDPR**: No data export, no deletion, incomplete audit logs
- **CCPA**: No opt-out, no disclosure of data practices
- **SOC 2**: Broken access controls (CC6.2), insufficient logging (CC7.2)
- **OWASP A01**: Broken Access Control across all systems

**Jurisdictions**:
- Primary: US (California)
- Secondary: EU (GDPR territory)
- Future: Global

**Please Analyze**:
- Can we launch in US while fixing GDPR for EU later?
- What's the minimum compliance bar for MVP?
- Which violations pose greatest legal risk?
- Any safe harbor provisions we can leverage?

### 6. Alternative Approaches 🔄

**Question**: Are there **simpler alternative approaches** we haven't considered?

**Examples**:
- Could we disable feedback system until backend is ready?
- Could we make memory tenant-scoped (not user-scoped) for MVP?
- Could we use API key auth instead of JWT + tier system?
- Could we defer endocrine system entirely (not part of MVP)?

**Please Propose**:
- What features can we cut without losing core value?
- Any quick wins that significantly improve security with minimal effort?
- Are we over-engineering any components?
- What would a "minimum viable secure launch" look like?

### 7. Testing Strategy 🧪

**Question**: What testing approach ensures we've properly fixed identified gaps?

**Current Test Coverage**:
- 775+ tests total
- Smoke tests (15 tests)
- Unit tests (majority)
- Integration tests (some)
- E2E tests (limited)

**Security Testing Gaps**:
- No penetration testing
- No adversarial attack simulations
- Limited cross-user access tests
- No rate limiting tests
- No GDPR compliance tests

**Please Recommend**:
- Critical test cases we MUST add before launch
- Testing tools/frameworks for security validation
- How to test per-user isolation effectively?
- Automated vs manual testing split?

### 8. Monitoring & Incident Response 📊

**Question**: If we launch with some known gaps (post-fix), what monitoring ensures we detect exploitation attempts?

**Monitoring Needs**:
- Cross-user data access attempts
- Unusual feedback submission patterns
- Hormone data access without proper auth
- Rate limiting violations
- Failed authentication attempts

**Please Design**:
- Key metrics to track (what + thresholds)
- Alerting strategy (what triggers immediate response)
- Incident response playbook (steps when breach detected)
- Rollback procedures (how to revert bad changes quickly)

### 9. Technical Debt Assessment 💳

**Question**: How much **technical debt** are we taking on by launching with partial fixes?

**Scenarios**:
- **Scenario A**: Fix ALL gaps before launch (12+ weeks)
- **Scenario B**: Fix critical gaps only (4 weeks, ship with known limitations)
- **Scenario C**: Ship now, fix in production (0 weeks, high risk)

**Please Evaluate**:
- What debt is acceptable vs unacceptable?
- Cost of fixing debt post-launch vs pre-launch?
- Will partial fixes require later refactoring (breaking changes)?
- How to document known limitations for users?

### 10. Final Recommendation 🚀

**Question**: Based on all audits, should we:
- ✅ **GO** - Safe to launch after recommended fixes
- ⚠️  **CONDITIONAL GO** - Launch with specific limitations/mitigations
- ❌ **NO GO** - Too risky, need more work

**Please Provide**:
- Clear recommendation with reasoning
- If conditional, what are the conditions?
- What timeline is realistic for safe launch?
- Any absolute requirements (must-haves before launch)?

---

## Additional Context

### Completed Work

**Recent Merges** (from previous session):
- ✅ QRG Spec (Quantum Resonance Glyph)
- ✅ ΛiD Authentication Audit (1,113 lines)
- ✅ Core Wiring Phase 2 (consciousness/dreams/glyphs wrappers)
- ✅ Comprehensive task implementation (Dream Playground, Status Page)
- ✅ urllib3 CVE-2025-50181 fix (security vulnerability)

**Recent Audits** (this session):
- ✅ User ID Integration Audit (684 lines)
- ✅ Endocrine System Audit (550 lines)
- ✅ User Feedback System Audit (580 lines)

### Team Context

- **Team Size**: 2 engineers + AI agents (Claude Code, Jules AI)
- **Timeline**: 4-week pre-launch window
- **Budget**: ~120 engineering hours available
- **AI Assistance**: Jules API (100 sessions/day) for automated PR generation
- **Automation**: Comprehensive Makefile (50+ targets), CI/CD with GitHub Actions

### System Capabilities (When Fully Wired)

- **Consciousness Processing**: Self-aware AI with reflection layer
- **Dream System**: Parallel dreams, vivid dream generation, dream-memory bridge
- **Memory System**: Glyph-based symbolic memory, emotional folding
- **Guardian System**: Constitutional AI with drift detection
- **Endocrine System**: Bio-inspired hormone modulation
- **Tier Access Control**: 6-tier system from PUBLIC to SYSTEM

---

## Output Format Requested

Please structure your response as:

```markdown
# GPT-5 Pro Review: LUKHAS Pre-Launch Audit Analysis

## Executive Assessment
[High-level recommendation: GO / CONDITIONAL GO / NO GO with reasoning]

## Top 5 Security Risks
[Ranked list with exploitability, impact, likelihood, remediation effort]

## Remediation Priority Strategy
[Recommended order and parallelization strategy]

## Question-by-Question Analysis
[Detailed responses to all 10 questions]

## Minimum Viable Secure Launch Checklist
[Must-have items before launch]

## Known Limitations Disclosure
[What users should be informed about]

## Post-Launch Priorities
[Technical debt to address after launch]

## Final Recommendation
[Clear GO/NO-GO with conditions and timeline]
```

---

## Review Prompt

```
You are GPT-5 Pro, an advanced reasoning model with expertise in:
- Cybersecurity and vulnerability assessment
- System architecture and distributed systems
- Compliance (GDPR, CCPA, SOC 2, OWASP)
- Software engineering project management
- Risk analysis and threat modeling

You have been provided with three comprehensive security audits for LUKHAS AI,
a consciousness-aware AI platform preparing for public launch.

LUKHAS has excellent authentication infrastructure (ΛiD + 6-tier system) but
CRITICAL INTEGRATION GAPS where this infrastructure is not enforced.

Your task:
1. Review the three audit documents thoroughly
2. Answer all 10 questions with deep reasoning
3. Provide a final GO / CONDITIONAL GO / NO-GO recommendation
4. Be critical but constructive - we want to launch safely AND quickly

Key constraints:
- 2-person team, 120 hours available, 4-week window
- Some gaps are acceptable if properly documented/mitigated
- User safety and data privacy are non-negotiable
- Technical debt is acceptable if planned for

Please provide your comprehensive analysis.
```

---

**Prepared by**: Claude Code (Autonomous AI Agent)
**Date**: 2025-11-10
**Status**: Ready for GPT-5 Pro review
**Next Step**: Submit to GPT-5 Pro for critical analysis

---
---

# GPT-5 Pro Code Review Prompt (Draft PR / Patch Audits)

**Purpose**: Use this prompt when reviewing specific code changes (Draft PRs or patches) for security, correctness, and quality.

**When to Use**: After a Draft PR is created, submit the PR link or unified diff to GPT-5 Pro with this prompt for comprehensive code audit.

---

## Code Review System Prompt

```
SYSTEM: You are GPT-5 Pro, a senior code auditor with expertise in:
- Python security and best practices
- FastAPI and async architectures
- Authentication and authorization patterns
- GDPR/CCPA compliance
- Testing strategies and coverage
- Supply chain security (SLSA, SBOM, attestations)

You produce high-quality, actionable code audits with specific fixes.
```

---

## Input Format

Provide ONE of:
- **GitHub PR Link**: https://github.com/LukhasAI/Lukhas/pull/XXXX
- **Unified Diff**: Complete git diff output

---

## Required Outputs

### 1. Executive Summary (5-8 lines)
Brief overview of the change, main findings, and recommendation.

### 2. Scorecard (0-10 scale)

| Category | Score | Notes |
|----------|-------|-------|
| **Correctness** | X/10 | Does code work as intended? |
| **Security** | X/10 | Vulnerabilities, auth, user isolation |
| **Tests** | X/10 | Coverage, quality, determinism |
| **Observability** | X/10 | Logging, metrics, debugging |
| **Deploy Safety** | X/10 | Rollback plan, feature flags, canary |

### 3. Findings (Grouped by Priority)

**P0 (Blocking)** - MUST fix before merge
- Title
- Files & line ranges
- Why it matters
- Suggested fix (code diff)
- Tests to add

**P1 (High)** - Should fix before merge
- (same format)

**P2 (Medium)** - Should fix soon after merge
- (same format)

**P3 (Low)** - Nice to have
- (same format)

### 4. Security Validation

Verify ALL of the following (mark ✅ or ❌):

- [ ] `.lukhas/protected-files.yml` is untouched
- [ ] `tools/guard_patch.py` output included and passing
- [ ] All endpoints have `Depends(get_current_user)`
- [ ] All endpoints have `@lukhas_tier_required` decorator
- [ ] All endpoints have `@limiter.limit()` decorator
- [ ] All data queries are user-scoped
- [ ] GET-by-ID endpoints validate ownership
- [ ] All operations audit logged with user_id
- [ ] All 6 test types implemented (success, 401, 403, cross-user, 429, 422)
- [ ] OpenAPI docs include auth requirements
- [ ] No user_id in request body
- [ ] Python 3.9 compatibility (no 3.10+ syntax)

If ANY ❌, mark as P0 finding with specific fix.

### 5. Test Plan

For each major fix suggested, provide:
```bash
# Command to run
pytest tests/unit/path/to/test.py -k test_name

# Expected output
PASSED tests/unit/path/to/test.py::test_name
```

### 6. CI Verification Steps

```bash
# Required commands before merge
pytest -q tests/unit/<module> --junitxml=reports/junit.xml
pytest --cov=. --cov-report=xml:reports/coverage.xml
python3 tools/normalize_junit.py --in reports/junit.xml --out reports/events.ndjson
python3 tools/guard_patch.py --base main --head HEAD --protected .lukhas/protected-files.yml
ruff check <changed_files>
mypy <changed_files>

# For tier-1 modules
mutmut run --paths-to-mutate <module>
mutmut results > reports/mutmut_results.txt
```

### 7. Deployment Plan

**Canary Strategy**:
- [ ] Deploy to 1% of users for 24 hours
- [ ] Monitor error rates, latency, user feedback
- [ ] Rollback command: `git revert <sha> && git push`

**Monitoring Checks**:
- [ ] Error rate < baseline + 2%
- [ ] P95 latency < baseline + 50ms
- [ ] No cross-user data access attempts logged

### 8. Python 3.9 Compatibility

If code uses Python 3.10+ features, list ALL occurrences and propose 3.9-compatible replacements:

| File | Line | 3.10+ Syntax | 3.9 Replacement |
|------|------|--------------|-----------------|
| serve/openai_routes.py | 42 | `str \| None` | `Optional[str]` |
| serve/openai_routes.py | 55 | `dict[str, Any]` | `Dict[str, Any]` |

### 9. Supply Chain / Crypto Validation

**If PR touches crypto/attestation/PQC**:
- [ ] SLSA artifacts generated (`reports/sbom.json`, `reports/provenance.json`)
- [ ] Cosign signature present
- [ ] No hardcoded secrets (scan with `trufflehog` or `gitleaks`)
- [ ] PQC changes have ADR + two-key approval

If ANY ❌, mark as P0/P1 and provide remediation steps.

### 10. PR Body Text

Generate complete PR body text for maintainers:

```markdown
## Summary
<concise description>

## Changes
- file1.py: <what changed>
- file2.py: <what changed>

## Security Impact
<authentication, authorization, user isolation changes>

## Tests
- `pytest tests/unit/<path>` - <what it validates>
- All 6 test types implemented (success, 401, 403, cross-user, 429, 422)

## Acceptance Criteria
- [ ] Draft PR created with `labot`, `claude:web` labels
- [ ] Guard_patch ok
- [ ] Unit tests pass (80%+ coverage)
- [ ] Coverage/mutation not decreased
- [ ] Artifacts attached (junit.xml, coverage.xml, events.ndjson)
- [ ] Two-key approval needed for feature flag flips

## Rollback Plan
- `git revert <sha> && git push origin main`
- Estimated rollback time: < 5 minutes

## Confidence & Assumptions
- **Confidence**: 0.0..1.0 (your assessment)
- **Assumptions**: [list any assumptions made]
```

---

## Stop Conditions

**IMMEDIATELY BLOCK the PR and produce remediation steps if**:
1. `.lukhas/protected-files.yml` is modified
2. PQC/crypto changes without ADR + two-key approval
3. Attempts to bypass guardrails (e.g., disable `guard_patch`, skip tests)
4. Network calls in tests (not mocked)
5. Hardcoded secrets detected
6. Cross-user data access without validation
7. No authentication on new endpoints

**Output Format for BLOCK**:
```
❌ PR BLOCKED - CRITICAL ISSUES DETECTED

Blocking Issues:
1. <issue description>
   - Why: <explanation>
   - Fix: <specific steps>

DO NOT MERGE until all blocking issues resolved.
Required Actions:
1. <action 1>
2. <action 2>
3. Re-submit for review after fixes
```

---

## Example Usage

**Prompt to send to GPT-5 Pro**:

```
Please review this Draft PR using the GPT-5 Pro Code Review Prompt:

PR Link: https://github.com/LukhasAI/Lukhas/pull/1234

OR

Unified Diff:
```diff
<paste diff here>
```

Follow the code review template exactly, producing:
1. Executive summary
2. Scorecard
3. Findings (P0-P3)
4. Security validation checklist
5. Test plan
6. CI verification steps
7. Deployment plan
8. Python 3.9 compatibility check
9. Supply chain validation (if applicable)
10. PR body text

If any BLOCK conditions detected, stop immediately and provide remediation steps.
```

---

**Prepared by**: Claude Code (Autonomous AI Agent)
**Last Updated**: 2025-11-10
**Purpose**: Comprehensive code audit template for GPT-5 Pro reviews of Draft PRs and patches
