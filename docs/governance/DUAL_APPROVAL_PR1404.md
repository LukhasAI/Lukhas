# Dual Approval Record - PR #1404

**PR Number**: #1404
**Title**: Multi-Task Core Features (40 Tasks Across 8 Subsystems)
**Ledger ID**: `LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS`
**Branch**: `claude/multi-task-core-features-011CV2564Udonzigw5yVAjbB`
**Date Created**: 2025-11-13
**Status**: ⏳ Awaiting Dual Approval

---

## Executive Summary

PR #1404 introduces **Guardian system changes** that require **T4 Dual Approval** per LUKHAS governance policy. This document captures both required approvals and provides the justification for governance review.

**Why Dual Approval Required:**
Guardian system changes directly impact:
- User-facing security decisions
- Policy enforcement mechanisms
- Constitutional AI behavior
- Public-facing explanation strings

These changes require review by both:
1. **Technical Lead** - Validates implementation quality and system integration
2. **Governance Reviewer** - Validates policy correctness and user impact

---

## Guardian Changes Requiring Dual Approval

### 1. Guardian Policy System (`core/guardian/policies.py`)

**File**: [core/guardian/policies.py](../../core/guardian/policies.py)
**Lines**: 332 lines (new file)
**Impact**: High - Defines 22 structured reason codes for policy vetoes

**Changes Introduced:**
- New `ReasonCode` enum with 22 categorized veto reasons:
  - Safety & Security (4 codes): UNSAFE_CONTENT, SECURITY_RISK, MALICIOUS_INTENT, EXPLOIT_ATTEMPT
  - Privacy & Consent (4 codes): PRIVACY_VIOLATION, MISSING_CONSENT, GDPR_VIOLATION, DATA_RETENTION_VIOLATION
  - Ethics & Compliance (5 codes): ETHICAL_VIOLATION, BIAS_DETECTED, MANIPULATION_ATTEMPT, DECEPTION_DETECTED, HARMFUL_OUTPUT
  - Rate Limiting (2 codes): RATE_LIMIT_EXCEEDED, RESOURCE_EXHAUSTION
  - Authentication (3 codes): INSUFFICIENT_PERMISSIONS, AUTHENTICATION_REQUIRED, AUTHORIZATION_FAILED
  - Content Quality (4 codes): LOW_QUALITY_OUTPUT, FACTUAL_INACCURACY, HALLUCINATION_DETECTED, CONTEXT_VIOLATION
- New `VetoEvent` class wrapping reason codes with context, policy name, message, and timestamp

**Governance Impact:**
- Structures previously unstructured veto reasons
- Provides clear categories for audit logging
- Enables fine-grained monitoring of Guardian decisions

**Code Snippet:**
```python
class ReasonCode(str, Enum):
    """Structured reason codes for Guardian policy vetoes."""
    # Safety & Security
    UNSAFE_CONTENT = "UNSAFE_CONTENT"
    SECURITY_RISK = "SECURITY_RISK"
    MALICIOUS_INTENT = "MALICIOUS_INTENT"
    EXPLOIT_ATTEMPT = "EXPLOIT_ATTEMPT"
    # Privacy & Consent
    PRIVACY_VIOLATION = "PRIVACY_VIOLATION"
    MISSING_CONSENT = "MISSING_CONSENT"
    GDPR_VIOLATION = "GDPR_VIOLATION"
    DATA_RETENTION_VIOLATION = "DATA_RETENTION_VIOLATION"
    # ... 14 more codes

class VetoEvent:
    """Represents a Guardian veto event with structured reason code."""
    def __init__(self, reason_code: ReasonCode, policy_name: str,
                 context: Optional[Dict[str, Any]] = None,
                 message: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        self.reason_code = reason_code
        self.policy_name = policy_name
        self.context = context or {}
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
```

### 2. Guardian Explanation System (`core/guardian/explain.py`)

**File**: [core/guardian/explain.py](../../core/guardian/explain.py)
**Lines**: 105 lines (new file)
**Impact**: High - Provides user-facing explanations for veto decisions

**Changes Introduced:**
- `REASON_EXPLANATIONS` dict mapping 22 ReasonCode types to human-readable strings
- `explain_veto(event)` function generating concise explanations
- `explain_veto_detailed(event)` function generating verbose explanations with context
- `get_user_facing_message(event)` function for end-user display

**Governance Impact:**
- Users will see these explanations when their requests are blocked
- Explanations must be accurate, non-technical, and respectful
- Poor explanations could damage user trust or create confusion

**Code Snippet:**
```python
REASON_EXPLANATIONS = {
    ReasonCode.UNSAFE_CONTENT: "Content contains potentially unsafe or harmful material",
    ReasonCode.SECURITY_RISK: "Operation poses a security risk to the system",
    ReasonCode.PRIVACY_VIOLATION: "Operation would violate user privacy protections",
    ReasonCode.MISSING_CONSENT: "Required user consent has not been obtained",
    ReasonCode.GDPR_VIOLATION: "Operation would violate GDPR data protection requirements",
    # ... 17 more explanations
}

def explain_veto(event: VetoEvent) -> str:
    """Convert veto event to human-readable explanation."""
    base_explanation = REASON_EXPLANATIONS.get(
        event.reason_code,
        "Request was blocked by policy"
    )
    explanation = f"{base_explanation} (Policy: {event.policy_name})"
    if event.message:
        explanation += f" - {event.message}"
    return explanation
```

**User-Facing Example:**
```
Request Blocked:
Content contains potentially unsafe or harmful material (Policy: ContentSafetyPolicy)
Additional context: Detected potential security exploit pattern
```

### 3. Guardian UI Strings (`core/guardian/strings.py`)

**File**: [core/guardian/strings.py](../../core/guardian/strings.py)
**Lines**: 49 lines (new file)
**Impact**: Medium - Provides UI string pack for Guardian dashboard

**Changes Introduced:**
- `UI_STRINGS` dict with user-facing strings for Guardian interface
- Categories: General, Actions, Status, Errors, Accessibility
- Supports future internationalization (i18n)

**Governance Impact:**
- Strings directly displayed in user interface
- Must be clear, professional, and accessible
- Tone and wording affect user perception of system

**Code Snippet:**
```python
UI_STRINGS = {
    "general": {
        "title": "Guardian Policy Monitor",
        "description": "Real-time monitoring of ethical policy enforcement",
        "subtitle": "Constitutional AI Protection Layer",
    },
    "actions": {
        "view_details": "View Details",
        "acknowledge": "Acknowledge",
        "override": "Request Override",
        "export": "Export Report",
    },
    "status": {
        "active": "Active Monitoring",
        "paused": "Monitoring Paused",
        "error": "System Error",
    },
    "errors": {
        "veto_blocked": "Your request was blocked by Guardian policy",
        "insufficient_permissions": "You do not have permission to perform this action",
        "policy_violation": "This action violates our usage policies",
    }
}
```

---

## T4 Dual Approval Requirements

### Primary Approval (Technical Lead)

**Reviewer**: @agi_dev
**Role**: Repository Owner / Technical Lead
**Review Focus**:
- Implementation quality and code standards
- System integration and architectural fit
- Test coverage and regression risk
- Performance and scalability impact

**Approval Status**: ⏳ **Awaiting Approval**

**Approval Record:**
```yaml
Reviewer: @agi_dev
GitHub Handle: @agi_dev
Role: Technical Lead
Date: [PENDING]
Commit Reviewed: 468fe4781 (features) + d02bab95 (test fixes)
Decision: [APPROVE / REQUEST_CHANGES / COMMENT]
Comments: |
  [Technical review comments here]

Signature: ________________________
Date: ____________________________
```

### Secondary Approval (Governance Review)

**Reviewer**: [REQUIRED]
**Role**: Guardian System Stakeholder / Ethics Review
**Review Focus**:
- Policy reason code accuracy and completeness
- User-facing explanation clarity and tone
- UI string professionalism and accessibility
- GDPR and compliance implications
- Potential user confusion or misunderstanding

**Approval Status**: ⏳ **Awaiting Reviewer Assignment**

**Approval Record:**
```yaml
Reviewer: [TO BE ASSIGNED]
GitHub Handle: [TO BE ASSIGNED]
Role: Governance / Ethics Review
Date: [PENDING]
Commit Reviewed: 468fe4781 (features) + d02bab95 (test fixes)
Decision: [APPROVE / REQUEST_CHANGES / COMMENT]
Comments: |
  [Governance review comments here]

Signature: ________________________
Date: ____________________________
```

---

## Review Checklist

### Technical Review (Primary Approval)

- [ ] **Code Quality**: Implementation follows LUKHAS coding standards
- [ ] **Test Coverage**: Adequate tests for new ReasonCode enum and explanation functions
- [ ] **System Integration**: Guardian changes integrate cleanly with existing systems
- [ ] **Performance**: No performance regressions introduced
- [ ] **Security**: No security vulnerabilities in new code
- [ ] **Documentation**: Guardian changes properly documented
- [ ] **Rollback**: Rollback plan is adequate (see [ROLLBACK_PLAN_PR1404.md](../operations/ROLLBACK_PLAN_PR1404.md))

### Governance Review (Secondary Approval)

- [ ] **Reason Code Accuracy**: All 22 reason codes are accurate and well-categorized
- [ ] **Explanation Clarity**: User-facing explanations are clear and non-technical
- [ ] **Tone and Professionalism**: UI strings maintain respectful, professional tone
- [ ] **Completeness**: No missing reason codes for common veto scenarios
- [ ] **Accessibility**: Explanations are understandable by non-technical users
- [ ] **GDPR Compliance**: GDPR-related reason codes (GDPR_VIOLATION, DATA_RETENTION_VIOLATION) are accurate
- [ ] **User Trust**: Explanations build user trust rather than create confusion
- [ ] **Internationalization**: UI strings structured for future i18n support
- [ ] **Bias Check**: No biased or discriminatory language in explanations
- [ ] **Privacy**: Explanations don't leak sensitive system details

---

## Governance Impact Assessment

### User-Facing Changes

**Before PR #1404:**
- Guardian vetoes return generic "Policy violation" messages
- No structured reason codes for audit logging
- Limited visibility into veto rationale

**After PR #1404:**
- Guardian vetoes return specific, human-readable explanations
- 22 structured reason codes enable fine-grained monitoring
- Users understand why their requests were blocked
- Dashboard UI strings provide professional interface

### Example User Experience

**Scenario**: User attempts to generate content that violates safety policy

**Before:**
```
Error: Request blocked by policy
```

**After:**
```
Request Blocked
Content contains potentially unsafe or harmful material (Policy: ContentSafetyPolicy)

If you believe this was in error, please contact support.
```

### Audit and Monitoring Impact

**Observability Improvements:**
- New metric: `lukhas_guardian_veto_reasons{reason_code}` - Breakdown by reason
- Structured logging enables compliance audits
- Dashboard panels show veto reason distribution

**Example Dashboard Query:**
```promql
# Top 5 Guardian veto reasons (last 24h)
topk(5, increase(lukhas_guardian_veto_reasons[24h]))
```

---

## Risk Assessment

### Risk 1: Explanation Accuracy
**Severity**: Medium
**Description**: User-facing explanations may not match actual veto reason in all edge cases
**Mitigation**: Comprehensive mapping of 22 reason codes to explanations
**Residual Risk**: Low - Fallback to generic "Request blocked by policy" for unmapped codes

### Risk 2: User Confusion
**Severity**: Low
**Description**: Non-technical users may not understand technical terms in explanations
**Mitigation**: Explanations written in plain language, avoid technical jargon
**Residual Risk**: Very Low - UI strings support i18n for future localization

### Risk 3: Tone and Trust
**Severity**: Low
**Description**: Poorly worded explanations could damage user trust
**Mitigation**: Professional, respectful tone in all UI strings
**Residual Risk**: Very Low - Governance review validates tone

### Risk 4: GDPR Compliance
**Severity**: Medium
**Description**: GDPR-related reason codes must be legally accurate
**Mitigation**: Specific codes for GDPR violations (GDPR_VIOLATION, DATA_RETENTION_VIOLATION, MISSING_CONSENT)
**Residual Risk**: Low - Explanations reference GDPR requirements explicitly

---

## Approval Process

### Step 1: Primary Approval (Technical Lead)
1. @agi_dev reviews PR #1404 implementation
2. Validates code quality, tests, and system integration
3. Signs approval record above
4. Adds "APPROVED-TECHNICAL" label to PR

### Step 2: Secondary Approval Assignment
1. @agi_dev assigns Guardian system stakeholder as second reviewer
2. Recommended reviewers:
   - Ethics/Governance team member
   - Product owner responsible for Guardian UX
   - Legal/Compliance representative (for GDPR review)

### Step 3: Secondary Approval (Governance Review)
1. Assigned reviewer reviews Guardian changes
2. Validates policy accuracy and user-facing explanations
3. Signs approval record above
4. Adds "APPROVED-GOVERNANCE" label to PR

### Step 4: Merge Authorization
1. Both approvals must be captured in this document
2. PR description must reference this approval record
3. Merge commit message must include: `Dual-Approval: LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS`

---

## Approval Timeline

**Target Timeline**: 48 hours from PR submission

| Phase | Duration | Action | Owner |
|-------|----------|--------|-------|
| 1 | 0-8 hours | Technical review and approval | @agi_dev |
| 2 | 8-12 hours | Assign governance reviewer | @agi_dev |
| 3 | 12-36 hours | Governance review and approval | [Assigned Reviewer] |
| 4 | 36-48 hours | Final merge authorization | @agi_dev |

---

## Post-Approval Actions

After both approvals are captured:

1. **Update PR Description**: Add approval record link
2. **Apply Labels**: `APPROVED-TECHNICAL`, `APPROVED-GOVERNANCE`
3. **Update State Snapshot**: Mark approvals as completed in [STATE_SNAPSHOT_PR1404.md](../audits/STATE_SNAPSHOT_PR1404.md)
4. **Merge PR**: Use squash merge with dual-approval trailer
5. **Audit Log**: Record approval in audit log (ledger ID: `LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS`)

---

## Merge Commit Message Template

```
feat(guardian): add structured veto reasons and user explanations

Implements 22 structured ReasonCode types for Guardian policy vetoes
with human-readable explanations and UI string pack.

Changes:
- core/guardian/policies.py: ReasonCode enum and VetoEvent class
- core/guardian/explain.py: User-facing explanation system
- core/guardian/strings.py: Guardian UI string pack

Dual-Approval: LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS
Technical-Approval: @agi_dev (2025-11-13)
Governance-Approval: [Reviewer] (YYYY-MM-DD)

Closes: #1404
```

---

## Escalation Path

If approvals are delayed or blocked:

1. **Technical Issues** (8+ hours delay):
   - Escalate to: Technical Lead (@agi_dev)
   - Create incident: `INC-APPROVAL-DELAY-PR1404`

2. **Governance Concerns** (24+ hours delay):
   - Escalate to: Product Owner or Ethics Committee
   - Schedule review meeting with stakeholders

3. **Approval Deadlock**:
   - Convene: Technical Lead + Governance Reviewer + Product Owner
   - Decision: Approve with conditions, Request changes, or Defer to next sprint

---

## Document Control

**Version**: 1.0
**Created**: 2025-11-13
**Last Updated**: 2025-11-13
**Maintained By**: LUKHAS Governance Team
**Review Schedule**: After each Guardian system change

**Related Documents**:
- State Snapshot: [docs/audits/STATE_SNAPSHOT_PR1404.md](../audits/STATE_SNAPSHOT_PR1404.md)
- Rollback Plan: [docs/operations/ROLLBACK_PLAN_PR1404.md](../operations/ROLLBACK_PLAN_PR1404.md)
- T4 Checklist: PR #1404 description
- Guardian Policies: [core/guardian/policies.py](../../core/guardian/policies.py)
- Guardian Explanations: [core/guardian/explain.py](../../core/guardian/explain.py)

---

## Audit Trail

**Ledger ID**: `LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS`

```json
{
  "event": "DUAL_APPROVAL_RECORD_CREATED",
  "timestamp": "2025-11-13T01:15:00Z",
  "pr_number": 1404,
  "ledger_id": "LUKHAS-SNAPSHOT-20251113-PR1404-40TASKS",
  "guardian_changes": [
    "core/guardian/policies.py",
    "core/guardian/explain.py",
    "core/guardian/strings.py"
  ],
  "approvals_required": 2,
  "approvals_completed": 0,
  "status": "AWAITING_APPROVALS"
}
```

---

**Generated with Claude Code** (https://claude.com/claude-code)
