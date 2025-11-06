# Reasoning Lab - Complete Specification

> **🔬 UX & Implementation Spec for Reasoning Lab Privacy Controls**

**Version**: 1.0
**Date**: 2025-11-06
**Source**: [STRATEGY.md](../../../docs/gonzo/STRATEGY.md)
**Status**: ✅ Canonical
**Priority**: P0 (Critical - Enterprise Readiness)

---

## Overview

The Reasoning Lab is LUKHAS's interactive reasoning trace visualization that demonstrates explainability and provenance. This spec defines the privacy and redaction controls required to safely demo reasoning systems without exposing sensitive data.

**Key Features**:
- ✅ 3-mode system (Public, Developer, Enterprise)
- ✅ Dynamic redaction slider (0-100)
- ✅ "Why?" side panel for node details
- ✅ Assistive Mode support (linear view)
- ✅ Keyboard + screen-reader accessible
- ✅ Server-side redaction enforcement

---

## Core Behaviors

### Modes

The Reasoning Lab supports 3 operational modes controlling what data is visible:

#### Public Mode (Default)
**Purpose**: Safe public demos without data exposure

**Characteristics**:
- **High redaction** (80-100 default)
- Nodes show **short labels only**
- **No raw sources** displayed
- "Why?" panel shows **explanation without artifacts**
- **Export disabled**
- Metadata heavily filtered

**Use Cases**:
- Marketing demos
- Conference presentations
- Public documentation
- lukhas.ai hero demos

#### Developer Mode
**Purpose**: Technical evaluation and integration testing

**Characteristics**:
- **Medium redaction** (20-50 default)
- Nodes include **technical IDs and performance metrics**
- Sources visible with **redacted paths**
- Developers can **run queries and export small traces**
- Performance data (p95 latency) shown

**Use Cases**:
- Developer onboarding
- Integration testing
- lukhas.dev documentation
- Technical blog posts

#### Enterprise Mode
**Purpose**: Full access for audit and compliance

**Characteristics**:
- **Low redaction** (0-20 default)
- **Full node metadata** visible
- **Signed artifacts view** enabled
- **"Request Audit" button** visible
- Requires **role-based authentication**

**Use Cases**:
- Enterprise customer demos
- Audit and compliance reviews
- Internal development
- Signed audit pack generation

---

### Redaction Slider

**Range**: 0 (no redaction) → 100 (maximum redaction)

**Mapping**:
| Level | Range | Visibility | Available In |
|-------|-------|------------|-------------|
| **Full** | 0-10 | Complete node details, all sources, full metadata | Developer, Enterprise |
| **Partial** | 11-50 | Technical IDs visible, sources partially redacted | Developer, Enterprise |
| **High** | 51-100 | Labels only, no sources, summary text | Public, Developer, Enterprise |

**Keyboard Controls**:
- **Left/Right Arrow**: Step ±1
- **Shift + Arrow**: Step ±10
- **Home**: Jump to 100 (max redaction)
- **End**: Jump to 0 (no redaction)
- **Page Up/Down**: Step ±10

**Accessibility**:
```html
<input
  id="redaction-slider"
  type="range"
  min="0"
  max="100"
  value={redaction}
  aria-label="Redaction level"
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow={redaction}
  aria-valuetext="`${redaction}% redaction`"
/>
```

---

### "Why?" Side Panel

**Purpose**: Show detailed explanation for each reasoning step

**Triggers**:
- Click "Why?" button on any node
- Keyboard: Focus node, press Enter/Space on "Why?"

**Content** (mode-dependent):

**Public Mode**:
```
[Node Name]
Short narrative (1-2 sentences)
No sources displayed
No performance metrics
```

**Developer Mode**:
```
[Node Name]
Detailed narrative
Sources: [redacted paths]
Performance: p95 = 30ms
```

**Enterprise Mode**:
```
[Node Name]
Full narrative
Sources: [complete artifact links]
Performance: p95 = 30ms, p99 = 45ms
Metadata: [full JSON]
```

**Accessibility**:
- **Role**: `dialog`
- **Focus trap**: Tab cycles within panel
- **Escape**: Closes panel
- **Close button**: Labeled "Close panel"
- **Aria-label**: "Details for [Node Name]"

---

### Assistive Mode Behavior

When Assistive Mode is enabled:

**Visual Changes**:
- Default to **Public mode** (high redaction)
- **Linear view** instead of graph visualization
- Each reasoning step as **numbered list**
- **1-2 sentence descriptions**
- **Slider hidden** (not necessary in linear view)

**UI Structure**:
```html
<ol aria-label="Reasoning steps">
  <li>
    <strong>1. Memory: customer records lookup</strong>
    <p>Retrieved customer data from secure storage (redacted)</p>
    <button>Why?</button>
  </li>
  <li>
    <strong>2. Attention: choose relevant features</strong>
    <p>Selected lifetime value and purchase history features</p>
    <button>Why?</button>
  </li>
  ...
</ol>
```

**Accessibility**:
- `prefers-reduced-motion`: Disable all animations
- High contrast compatible
- Screen reader optimized
- Keyboard-only navigation
- "Explain step-by-step" toggle for additional context

---

## Component Interface

### React Component Props

```typescript
export interface Props {
  trace: Trace | null;
  initialMode?: Mode;           // default: "public"
  initialRedaction?: number;    // 0-100, default: 80
  onRequestAudit?: (traceId: string) => Promise<void>;
  assistive?: boolean;          // default: false
}

export type Mode = "public" | "developer" | "enterprise";

export interface Node {
  id: string;
  label: string;
  detail?: string;
  sources?: string[];
  meta?: {
    p95_ms?: number;
    p99_ms?: number;
    confidence?: number;
    [key: string]: any;
  };
}

export interface Trace {
  id: string;
  nodes: Node[];
  edges: Array<{ from: string; to: string }>;
  metadata?: {
    query?: string;
    generated_at?: string;
    [key: string]: any;
  };
}
```

### Usage Example

```tsx
import { ReasoningLab } from "./components/ReasoningLab";

function App() {
  const handleAuditRequest = async (traceId: string) => {
    const response = await fetch("/api/audit-requests", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ traceId })
    });
    if (!response.ok) throw new Error("Audit request failed");
  };

  return (
    <ReasoningLab
      trace={traceData}
      initialMode="developer"
      initialRedaction={30}
      onRequestAudit={handleAuditRequest}
      assistive={false}
    />
  );
}
```

---

## Audit Request Flow

**Enterprise Mode Only**

**Button**: "Request Audit" (visible when `mode="enterprise"`)

**Flow**:
1. User clicks "Request Audit"
2. POST to `/api/audit-requests` with:
   ```json
   {
     "traceId": "trace-20251106-01",
     "userId": "user-123",
     "projectId": "proj-456",
     "notes": "Q3 compliance audit"
   }
   ```
3. Server validates:
   - User has `enterprise` role
   - Trace exists and user has access
4. Server triggers audit pack builder:
   - Snapshots current trace artifacts
   - Runs `tools/build_audit_pack.py`
   - Signs with GPG
5. Server responds with:
   ```json
   {
     "status": "queued",
     "auditId": "audit-789",
     "estimatedTime": "10 minutes",
     "notificationEmail": "user@company.com"
   }
   ```
6. User receives email with secure download link

---

## Accessibility Requirements

### WCAG 2 AA Compliance

**Keyboard Navigation**:
- ✅ All controls focusable via Tab
- ✅ Mode toggle: Arrow keys + Enter/Space
- ✅ Slider: Arrow keys + Home/End/PgUp/PgDn
- ✅ Node selection: Tab to "Why?" buttons
- ✅ Panel: Focus trap with Escape to close

**Screen Reader Support**:
- ✅ `role="application"` on container
- ✅ `aria-label="Reasoning Lab"` on container
- ✅ `role="tablist"` on mode toggle
- ✅ `aria-pressed` on mode buttons
- ✅ `aria-live="polite"` updates on node selection
- ✅ `aria-valuetext` on slider
- ✅ `role="dialog"` on side panel
- ✅ `aria-haspopup="dialog"` on "Why?" buttons

**Reduced Motion**:
```css
@media (prefers-reduced-motion: reduce) {
  .reasoning-lab * {
    animation: none !important;
    transition: none !important;
  }
}
```

---

## Implementation Checklist

### Phase 1: Core Component (W3)
- [ ] Create `src/components/ReasoningLab/` directory
- [ ] Implement 3-mode toggle (Public/Developer/Enterprise)
- [ ] Add redaction slider with keyboard controls
- [ ] Build "Why?" side panel with focus trap
- [ ] Add Assistive Mode linear view
- [ ] Implement accessibility attributes (ARIA)

### Phase 2: Server Integration (W3)
- [ ] Create `/api/trace/:id` endpoint with mode/level params
- [ ] Implement server-side redaction (see [REDACTION_SYSTEM.md](./REDACTION_SYSTEM.md))
- [ ] Add role-based authentication for modes
- [ ] Create `/api/audit-requests` endpoint
- [ ] Integrate with audit pack builder

### Phase 3: Testing (W4)
- [ ] Write Jest tests for redaction behavior
- [ ] Add React Testing Library tests for UI interactions
- [ ] Test keyboard navigation
- [ ] Run axe-core accessibility audit
- [ ] Test with screen reader (NVDA/JAWS)
- [ ] Visual regression tests (Percy/Chromatic)

### Phase 4: Integration (W4)
- [ ] Replace simple list with graph visualization (D3/React-Flow)
- [ ] Add network diagram with zoom/pan
- [ ] Integrate with production trace API
- [ ] Add export functionality (Developer/Enterprise only)
- [ ] Add share trace link (with redaction preserved)

---

## Related Documents

- **Redaction Implementation**: [REDACTION_SYSTEM.md](./REDACTION_SYSTEM.md) - Server-side redaction details
- **Testing Strategy**: [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Test fixtures, Jest setup, CI
- **Design System**: [../LUKHAS_THEMES.md](../LUKHAS_THEMES.md) - Visual design tokens
- **90-Day Roadmap**: [../../governance/strategic/90_DAY_ROADMAP.md](../../governance/strategic/90_DAY_ROADMAP.md) - W3-W4 timeline

---

## T4 Warnings & Best Practices

### ⚠️ Security

> **CRITICAL**: Redaction must be **server-side and deterministic**. Client-side redaction is for UX only - the server must enforce access control and never send unreacted data that the client "hides".

**Correct Approach**:
1. Client requests trace with `?mode=public&level=80`
2. Server checks user role
3. Server applies redaction **before sending response**
4. Client displays pre-redacted data

**Incorrect Approach** ❌:
1. Server sends full trace
2. Client applies redaction via JavaScript
3. User can bypass by inspecting network tab

### ⚠️ Audit Trail

Every trace view should log:
- User ID
- Mode used
- Redaction level
- Timestamp
- Trace ID viewed

This audit trail is required for enterprise compliance.

### ⚠️ Performance

Redaction adds latency. Optimize:
- Cache redacted traces (5-minute TTL)
- Pre-compute redaction levels (0, 25, 50, 75, 100)
- Use worker threads for complex redaction
- Target: <100ms redaction time, <250ms total p95

---

**Document Owner**: @product + @frontend
**Review Cycle**: Weekly during W3-W4 implementation
**Last Updated**: 2025-11-06
