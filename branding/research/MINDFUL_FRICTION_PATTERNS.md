# Mindful Friction Patterns

> **⚠️ Intentional Friction for Critical Operations**

**Version**: 1.0
**Date**: 2025-11-06
**Status**: ✅ **ACTIVE GUIDELINES** (Limited Scope)
**Inspired By**: [Visionary Enhancements Research](../../docs/research/brand_philosophy/VISIONARY_ENHANCEMENTS_RESEARCH.md)
**Reconciliation**: [GONZO_RECONCILIATION.md](../../docs/research/brand_philosophy/GONZO_RECONCILIATION.md)

---

## Executive Summary

**Mindful Friction** is the deliberate introduction of interaction delays, confirmations, or cognitive steps in **critical operations only** to protect user agency and prevent irreversible mistakes. This is NOT a general UX philosophy—it is a targeted security pattern.

**Core Principle**: Friction as a feature for high-stakes operations, not a general design paradigm.

**Scope**:
- ✅ **Applied to**: Account deletion, high-value payments, constitutional changes, irreversible actions
- ❌ **NOT Applied to**: General navigation, assistive mode, onboarding, content browsing

---

## Philosophy

### Why Friction? (From Visionary Research)

The dominant "frictionless UX" paradigm optimizes for speed and convenience, but can:
- Enable impulsive, regrettable decisions (delete account, approve payment)
- Reduce user awareness of consequence severity
- Create "mindless" interaction patterns that exploit cognitive biases

**Mindful Friction** inverts this for critical operations:
- **Slows down high-stakes decisions** to ensure deliberate choice
- **Signals importance** through interaction cost
- **Protects user agency** by preventing manipulation through speed

### LUKHAS Integration

LUKHAS already uses friction patterns in existing systems:
- **Adaptive MFA**: Progressive friction based on risk assessment
- **Secure Payment Confirmation (SPC)**: Biometric approval for payments
- **Guardian interventions**: Soft blocks with user confirmation

**This document** formalizes those patterns and extends them to other critical operations.

---

## Approved Friction Patterns

### Pattern 1: Typed Confirmation

**Use Case**: Irreversible destructive actions (account deletion, data purge)

**Implementation**:
```typescript
// Pattern: User must type exact phrase to confirm
interface TypedConfirmationProps {
  action: string;              // "delete account"
  confirmationPhrase: string;  // "DELETE ACCOUNT"
  onConfirm: () => Promise<void>;
  onCancel: () => void;
}

// Example: Account deletion
<TypedConfirmation
  action="delete your LUKHAS account"
  confirmationPhrase="DELETE ACCOUNT"
  onConfirm={async () => {
    await deleteAccount(userId);
    redirect('/goodbye');
  }}
  onCancel={() => redirect('/settings')}
/>
```

**UI Pattern**:
```
┌─────────────────────────────────────────────┐
│ Delete Account                              │
├─────────────────────────────────────────────┤
│ This action is permanent and cannot be      │
│ undone. All your data, memories, and        │
│ settings will be deleted.                   │
│                                             │
│ To confirm, type: DELETE ACCOUNT            │
│ ┌─────────────────────────────────────────┐ │
│ │                                         │ │ ← Input field
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Cancel]  [Delete Account] ← Disabled until │
│                              phrase matches  │
└─────────────────────────────────────────────┘
```

**Rationale**: Typing forces deliberate engagement. Case-insensitive match acceptable for accessibility.

---

### Pattern 2: Cooling-Off Period

**Use Case**: High-value financial operations, subscription cancellations with refunds

**Implementation**:
```typescript
// Pattern: Action scheduled, user can cancel within window
interface CoolingOffConfig {
  actionName: string;
  scheduledTime: Date;     // 24-72 hours from request
  cancellationWindow: number; // milliseconds
}

// Example: Enterprise subscription cancellation
async function requestSubscriptionCancellation(
  subscriptionId: string
): Promise<CancellationToken> {
  const scheduledTime = addDays(new Date(), 3); // 72-hour window

  const token = await db.cancellationRequests.create({
    subscriptionId,
    scheduledTime,
    status: 'pending',
    requestedAt: new Date(),
  });

  // Send notification with cancellation link
  await sendEmail({
    template: 'subscription-cancellation-pending',
    scheduledTime,
    cancelLink: `/cancel/${token.id}`,
  });

  return token;
}
```

**UI Flow**:
```
Request Cancellation
    ↓
Email sent with 72-hour notice
    ↓
User can click "Cancel Cancellation" anytime before execution
    ↓
After 72 hours: Subscription cancelled (if not reversed)
```

**Rationale**: Prevents impulsive cancellations driven by temporary dissatisfaction. Protects revenue while respecting user choice.

---

### Pattern 3: Stepped Disclosure

**Use Case**: High-consequence configuration changes (Guardian constitution edits, privacy settings)

**Implementation**:
```typescript
// Pattern: Multi-step disclosure with comprehension checks
interface SteppedDisclosureStep {
  title: string;
  content: string;
  comprehensionCheck?: {
    question: string;
    correctAnswer: string;
    incorrectFeedback: string;
  };
}

// Example: Guardian constitutional rule change
const constitutionEditSteps: SteppedDisclosureStep[] = [
  {
    title: "Understanding Constitutional Changes",
    content: "You are about to edit the Guardian constitution. These rules govern AI behavior and safety enforcement.",
    comprehensionCheck: {
      question: "What do Guardian constitutional rules govern?",
      correctAnswer: "AI behavior and safety enforcement",
      incorrectFeedback: "Please review the explanation above."
    }
  },
  {
    title: "Impact & Reversibility",
    content: "Changes take effect immediately and apply to all systems. You can revert changes, but historical decisions remain.",
    comprehensionCheck: {
      question: "Can you undo the effects of past decisions made under the old rules?",
      correctAnswer: "No",
      incorrectFeedback: "Historical decisions cannot be undone, even after reverting rules."
    }
  },
  {
    title: "Confirm Edit",
    content: "Proceed with constitutional edit?",
  }
];
```

**Rationale**: Ensures user understands consequences before high-impact actions. Comprehension checks prevent "click-through" behavior.

---

### Pattern 4: Adaptive Friction (Existing System)

**Use Case**: Authentication, payment approval (already implemented via Adaptive MFA and SPC)

**How It Works**:
```typescript
// Adaptive MFA: Friction scales with risk
interface MFAConfig {
  baseRiskScore: number;      // 0-100
  locationRisk: number;       // New location = +30
  deviceRisk: number;         // New device = +50
  behaviorRisk: number;       // Unusual behavior = +20
}

function calculateMFAFriction(config: MFAConfig): MFALevel {
  const totalRisk = config.baseRiskScore
    + config.locationRisk
    + config.deviceRisk
    + config.behaviorRisk;

  if (totalRisk > 80) return 'biometric-required';
  if (totalRisk > 50) return '2fa-required';
  if (totalRisk > 20) return 'password-only';
  return 'session-token-only';
}
```

**Rationale**: Friction proportional to risk. Low-risk operations remain frictionless.

---

### Pattern 5: Irreversibility Preview

**Use Case**: Operations with cascading effects (delete workspace, revoke access)

**Implementation**:
```typescript
// Pattern: Show preview of all affected resources before action
interface ImpactPreview {
  directImpact: string[];    // Primary resources affected
  cascadingImpact: string[]; // Secondary resources affected
  affectedUsers: number;
  estimatedRecoveryTime: string | null;
}

// Example: Workspace deletion
async function getWorkspaceDeletionImpact(
  workspaceId: string
): Promise<ImpactPreview> {
  return {
    directImpact: [
      '15 projects',
      '342 files',
      '89 reasoning traces',
      '12 custom memory modules'
    ],
    cascadingImpact: [
      '3 shared collections (will become unavailable to collaborators)',
      '8 API keys (will be revoked)',
      '23 active sessions (will be terminated)'
    ],
    affectedUsers: 5,
    estimatedRecoveryTime: null // Irreversible
  };
}
```

**UI Pattern**:
```
┌─────────────────────────────────────────────┐
│ Delete Workspace: "Enterprise AI R&D"      │
├─────────────────────────────────────────────┤
│ ⚠️ This will permanently delete:           │
│                                             │
│ Direct Impact:                              │
│   • 15 projects                             │
│   • 342 files                               │
│   • 89 reasoning traces                     │
│   • 12 custom memory modules                │
│                                             │
│ Cascading Impact:                           │
│   • 3 shared collections (5 users affected) │
│   • 8 API keys will be revoked              │
│   • 23 active sessions will be terminated   │
│                                             │
│ ⚠️ This action CANNOT be undone.           │
│                                             │
│ [Show Full Impact Report]                   │
│ [Cancel]  [I Understand, Delete Workspace]  │
└─────────────────────────────────────────────┘
```

**Rationale**: Comprehensive impact preview prevents "hidden consequence" surprises.

---

## Where NOT to Apply Friction

### ❌ General Navigation
**Prohibited**: Adding delays, confirmations, or steps to:
- Page transitions
- Menu navigation
- Content browsing
- Search interactions
- Filter/sort operations

**Rationale**: General exploration should be effortless. Friction here harms usability.

---

### ❌ Assistive Mode
**Prohibited**: Any friction that increases cognitive load for users with:
- Cognitive disabilities
- Motor impairments
- Visual impairments
- Attention disorders

**Assistive Mode Override**: All friction patterns MUST have assistive-friendly alternatives:
```typescript
// Typed confirmation → Single-button confirmation
if (user.assistiveMode) {
  return <SingleButtonConfirmation
    message="Delete account? This cannot be undone."
    confirmLabel="Yes, Delete My Account"
    cancelLabel="Cancel"
  />;
}

// Cooling-off period → Immediate with extra confirmation
if (user.assistiveMode) {
  return <ImmediateActionWithDoubleConfirm
    message="Cancel subscription now?"
  />;
}
```

**Rationale**: Accessibility is non-negotiable. WCAG 2 AA compliance requires accommodations.

---

### ❌ Onboarding & Signup
**Prohibited**: Adding friction to:
- Account creation
- Initial setup wizards
- Trial activations
- First-time user experiences

**Rationale**: Acquisition friction kills conversion. Save friction for high-stakes operations.

---

### ❌ Content Creation & Creativity
**Prohibited**: Adding friction to:
- Writing/editing content
- Creative generation
- Reasoning trace exploration
- Memory module creation

**Rationale**: Creative flow requires frictionless interaction. Interruptions harm productivity.

---

## Implementation Guidelines

### Decision Tree: Should I Add Friction?

```
Is this operation:
  ├─ Irreversible? ────────────────────────┐
  ├─ High-value (>$100)? ──────────────────┤
  ├─ Affects other users? ─────────────────┤
  ├─ Has cascading effects? ───────────────┤
  └─ Changes system behavior globally? ────┤
                                           ↓
                                     YES to any?
                                           ↓
                           ┌───────────────┴───────────────┐
                           ↓                               ↓
                    Is user in                       Is this a
                    assistive mode?                  creative flow?
                           ↓                               ↓
                    YES → Use alternative          YES → No friction
                           ↓
                    NO → Apply friction pattern
```

### Friction Intensity Scale

| Risk Level | Friction Pattern | Example Use Case |
|------------|------------------|------------------|
| **Critical** | Typed Confirmation + Cooling-Off | Account deletion, workspace deletion |
| **High** | Typed Confirmation OR Cooling-Off | Subscription cancellation, payment >$1000 |
| **Medium** | Stepped Disclosure + Preview | Configuration changes, access revocation |
| **Low** | Single confirmation with preview | Payment <$100, file deletion |
| **Minimal** | No friction (trust + undo) | Settings toggle, theme change |

---

## Assistive Mode Adaptations

### Pattern 1: Typed Confirmation → Single Button
```typescript
// Standard mode: Type "DELETE ACCOUNT"
<TypedConfirmation phrase="DELETE ACCOUNT" />

// Assistive mode: Large button with clear warning
<AssistiveConfirmation
  message="Delete account? This cannot be undone."
  confirmLabel="Yes, Delete My Account"
  confirmStyle="danger-large"  // Large touch target
  cancelLabel="Cancel"
  cancelStyle="safe-large"
/>
```

### Pattern 2: Cooling-Off Period → Immediate with Double Confirm
```typescript
// Standard mode: 72-hour cooling-off
await scheduleCancellation(72hours);

// Assistive mode: Immediate with two-step confirmation
if (user.assistiveMode) {
  const firstConfirm = await confirm("Cancel subscription now?");
  if (firstConfirm) {
    const secondConfirm = await confirm(
      "Are you sure? This will end your subscription immediately."
    );
    if (secondConfirm) {
      await cancelImmediately();
    }
  }
}
```

### Pattern 3: Stepped Disclosure → Simplified Single-Page
```typescript
// Standard mode: Multi-step with comprehension checks
<SteppedDisclosure steps={[step1, step2, step3]} />

// Assistive mode: Single page, plain language, no quiz
<SimplifiedDisclosure
  content="This change affects AI behavior. You can undo it later."
  readingLevel="flesch-kincaid-8"
/>
```

---

## A/B Testing Plan

### Hypothesis
Mindful friction for critical operations will:
- Reduce regret rates by >20%
- Increase completion time by <5%
- Maintain or improve user satisfaction

### Test 1: Typed Confirmation for Account Deletion

**Control**: Single button confirmation
**Treatment**: Typed confirmation ("DELETE ACCOUNT")

**Metrics**:
- Regret rate (support tickets requesting account recovery)
- Completion rate (users who complete deletion)
- Time to complete (seconds)
- User sentiment (post-deletion survey)

**Success Criteria**:
- <20% reduction in regret rate
- <10% reduction in completion rate
- <30 seconds average time increase

**Duration**: 30 days, 1000+ deletion attempts

---

### Test 2: Cooling-Off Period for Subscription Cancellation

**Control**: Immediate cancellation
**Treatment**: 72-hour cooling-off period

**Metrics**:
- Cancellation reversal rate (users who cancel the cancellation)
- Revenue retention (MRR from reversed cancellations)
- User satisfaction (NPS after cooling-off period)

**Success Criteria**:
- >15% cancellation reversal rate
- >10% revenue retention from reversals
- No decrease in NPS

**Duration**: 60 days, 500+ cancellation requests

---

### Test 3: Impact Preview for Workspace Deletion

**Control**: Generic warning ("This will delete all data")
**Treatment**: Detailed impact preview with affected resource counts

**Metrics**:
- Cancellation rate after preview (users who abort deletion)
- Regret rate (support tickets)
- Time spent reviewing preview

**Success Criteria**:
- >10% increase in informed cancellations (users who abort)
- >30% reduction in regret rate
- <60 seconds average preview review time

**Duration**: 30 days, 500+ workspace deletions

---

## Related Documents

**Visionary Research**:
- [VISIONARY_ENHANCEMENTS_RESEARCH.md](../../docs/research/brand_philosophy/VISIONARY_ENHANCEMENTS_RESEARCH.md) - Original friction concepts

**Reconciliation**:
- [GONZO_RECONCILIATION.md](../../docs/research/brand_philosophy/GONZO_RECONCILIATION.md) - Selective adoption rationale

**Related Systems**:
- [GUARDIAN_CONSTITUTION.md](../guardian/GUARDIAN_CONSTITUTION.md) - Section 3.2: User Agency Protection
- [LUKHAS_THEMES.md](../design/LUKHAS_THEMES.md) - Assistive mode specifications
- [Adaptive MFA](../../docs/architecture/security/ADAPTIVE_MFA.md) - Existing adaptive friction system
- [Secure Payment Confirmation](../../docs/architecture/payments/SPC.md) - Payment friction patterns

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-06 | Adopt mindful friction (limited scope) | Enhances security without breaking accessibility |
| 2025-11-06 | Apply only to critical operations | Preserves frictionless UX for general navigation |
| 2025-11-06 | Require assistive mode alternatives | WCAG 2 AA compliance non-negotiable |
| 2025-11-06 | Create A/B testing plan | Validate effectiveness before full rollout |

---

**Document Owner**: @web-architect + @ux-lead
**Review Cycle**: Quarterly or after A/B test results
**Last Updated**: 2025-11-06
**Status**: Active Guidelines (Limited Scope)

---

**⚠️ Core Principle**: Friction is a tool for protection, not a general design philosophy. Use sparingly, measure rigorously, prioritize accessibility.
