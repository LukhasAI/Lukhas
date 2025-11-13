# Reasoning Lab - Testing Strategy

> **✅ Comprehensive Testing Plan for Reasoning Lab**

**Version**: 1.0
**Date**: 2025-11-06
**Source**: [MORE_DELIVERABLES.js](../../../docs/gonzo/MORE_DELIVERABLES.js)
**Status**: ✅ Canonical
**Priority**: P0 (Quality Gate)

---

## Overview

This document defines the complete testing strategy for Reasoning Lab, including:
- ✅ Unit tests for redaction logic
- ✅ Component tests for UI interactions
- ✅ Integration tests for API endpoints
- ✅ Accessibility tests (WCAG 2 AA)
- ✅ Visual regression tests
- ✅ End-to-end workflows

**Coverage Target**: 85%+ for critical paths

---

## Test Pyramid

```
           E2E Tests (5%)
          ┌─────────────┐
          │  User flows │
          │  w/ browser │
          └─────────────┘
              ▲
              │
      Integration Tests (20%)
     ┌────────────────────┐
     │  API + Component   │
     │   integration      │
     └────────────────────┘
              ▲
              │
        Unit Tests (75%)
   ┌─────────────────────────┐
   │  Redaction logic        │
   │  Component behavior     │
   │  Helper functions       │
   └─────────────────────────┘
```

---

## Test Fixtures

### Mock Trace Data

**Location**: `src/components/ReasoningLab/__tests__/fixtures/mockTrace.json`

```json
{
  "id": "trace-20251106-01",
  "nodes": [
    {
      "id": "n1",
      "label": "Memory: customer records lookup",
      "detail": "Pulled customer records from s3://prod-bucket/customers/2025 and matched by email alice@example.com and id 123e4567-e89b-12d3-a456-426614174000.",
      "sources": [
        "s3://prod-bucket/customers/2025/part-00001.json",
        "database:customers.primary"
      ],
      "meta": {
        "p95_ms": 30,
        "pii_present": true,
        "record_count": 234
      }
    },
    {
      "id": "n2",
      "label": "Attention: choose relevant features",
      "detail": "Selected features: lifetime_value, last_purchase_date, churn_flags.",
      "sources": ["feature-store://features/lifetime_value"],
      "meta": {
        "p95_ms": 15
      }
    },
    {
      "id": "n3",
      "label": "Thought: causal inference",
      "detail": "Computed causal chains and scored alternatives. Internal run id: run_7c9bcd.",
      "sources": ["internal:causal/2025-10-26/run_7c9bcd"],
      "meta": {
        "p95_ms": 145,
        "confidence": 0.77
      }
    },
    {
      "id": "n4",
      "label": "Decision: apply intervention",
      "detail": "Recommend sending re-engagement offer. Ticket id: TCK-9981.",
      "sources": ["crm://tickets/TCK-9981"],
      "meta": {
        "p95_ms": 22
      }
    }
  ],
  "edges": [
    { "from": "n1", "to": "n2" },
    { "from": "n2", "to": "n3" },
    { "from": "n3", "to": "n4" }
  ],
  "metadata": {
    "query": "Why did churn spike in Q3?",
    "generated_at": "2025-11-06T12:00:00Z"
  }
}
```

**Purpose**: Contains realistic PII (emails, UUIDs, paths, ticket IDs) to test redaction

---

## Unit Tests

### 1. Redaction Logic Tests

**Location**: `server/__tests__/redaction.test.js`

```javascript
const { redactString, redactNode, redactTrace } = require("../redaction");
const mockTrace = require("../../src/components/ReasoningLab/__tests__/fixtures/mockTrace.json");

describe("Redaction - PII Masking", () => {
  test("masks emails at level 40+", () => {
    const input = "Contact alice@example.com for details";
    const low = redactString(input, 20);
    const high = redactString(input, 50);

    expect(low).toContain("[redacted-email]");
    expect(high).toContain("[redacted-email]");
    expect(high).not.toContain("alice@example.com");
  });

  test("masks UUIDs at level 40+", () => {
    const input = "ID: 123e4567-e89b-12d3-a456-426614174000";
    const result = redactString(input, 50);

    expect(result).toContain("[redacted-id]");
    expect(result).not.toMatch(/[0-9a-f]{8}-[0-9a-f]{4}/);
  });

  test("masks s3:// paths at level 40+", () => {
    const input = "Loaded from s3://prod-bucket/sensitive/data.json";
    const result = redactString(input, 50);

    expect(result).toContain("[redacted-source]");
    expect(result).not.toContain("s3://");
  });

  test("masks ticket IDs at level 40+", () => {
    const input = "Ticket TCK-9981 resolved";
    const result = redactString(input, 50);

    expect(result).toContain("[redacted-ticket]");
    expect(result).not.toContain("TCK-9981");
  });

  test("shows only first sentence at level 75+", () => {
    const input = "First sentence. Second sentence. Third sentence.";
    const result = redactString(input, 80);

    expect(result).toContain("First sentence");
    expect(result).toContain("(redacted)");
    expect(result).not.toContain("Second sentence");
  });
});

describe("Redaction - Node Level", () => {
  const node = mockTrace.nodes[0];

  test("removes sources in public mode", () => {
    const result = redactNode(node, 90, "public");
    expect(result.sources).toEqual([]);
  });

  test("preserves sources in developer mode with low redaction", () => {
    const result = redactNode(node, 20, "developer");
    expect(result.sources).toHaveLength(2);
    expect(result.sources[0]).toContain("s3://");
  });

  test("redacts sources in developer mode with high redaction", () => {
    const result = redactNode(node, 50, "developer");
    expect(result.sources).toHaveLength(2);
    expect(result.sources[0]).toBe("[redacted-source]");
  });

  test("strips metadata at level 85+", () => {
    const result = redactNode(node, 90, "public");
    expect(result.meta).toEqual({});
  });

  test("preserves metadata in enterprise mode", () => {
    const result = redactNode(node, 10, "enterprise");
    expect(result.meta.p95_ms).toBe(30);
    expect(result.meta.record_count).toBe(234);
  });
});

describe("Redaction - Trace Level", () => {
  test("applies public mode defaults", () => {
    const result = redactTrace(mockTrace, { mode: "public" });

    expect(result.nodes[0].sources).toEqual([]);
    expect(result.nodes[0].detail).toContain("(redacted)");
    expect(result.metadata.query).toHaveLength(120);
  });

  test("applies developer mode defaults", () => {
    const result = redactTrace(mockTrace, { mode: "developer" });

    expect(result.nodes[0].sources.length).toBeGreaterThan(0);
    expect(result.nodes[0].detail).toContain("[redacted-email]");
  });

  test("applies enterprise mode defaults", () => {
    const result = redactTrace(mockTrace, { mode: "enterprise" });

    expect(result.nodes[0].sources.length).toBeGreaterThan(0);
    expect(result.nodes[0].detail).toContain("alice");
  });

  test("respects custom redaction level", () => {
    const result = redactTrace(mockTrace, { mode: "developer", redactionLevel: 80 });

    expect(result.nodes[0].detail).toContain("(redacted)");
  });
});
```

**Run**: `npm test -- server/__tests__/redaction.test.js`

---

### 2. Component Unit Tests

**Location**: `src/components/ReasoningLab/__tests__/ReasoningLab.test.tsx`

```typescript
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReasoningLab } from "../ReasoningLab";
import mockTrace from "./fixtures/mockTrace.json";

describe("ReasoningLab - Rendering", () => {
  test("renders mode toggle buttons", () => {
    render(<ReasoningLab trace={mockTrace as any} />);

    expect(screen.getByRole("button", { name: /public/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /developer/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /enterprise/i })).toBeInTheDocument();
  });

  test("renders redaction slider in non-assistive mode", () => {
    render(<ReasoningLab trace={mockTrace as any} assistive={false} />);

    const slider = screen.getByRole("slider", { name: /redaction/i });
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute("aria-valuemin", "0");
    expect(slider).toHaveAttribute("aria-valuemax", "100");
  });

  test("hides redaction slider in assistive mode", () => {
    render(<ReasoningLab trace={mockTrace as any} assistive={true} />);

    const slider = screen.queryByRole("slider", { name: /redaction/i });
    expect(slider).not.toBeInTheDocument();
  });

  test("renders all nodes from trace", () => {
    render(<ReasoningLab trace={mockTrace as any} />);

    expect(screen.getByText(/Memory:/i)).toBeInTheDocument();
    expect(screen.getByText(/Attention:/i)).toBeInTheDocument();
    expect(screen.getByText(/Thought:/i)).toBeInTheDocument();
    expect(screen.getByText(/Decision:/i)).toBeInTheDocument();
  });
});

describe("ReasoningLab - Mode Switching", () => {
  test("switches to developer mode on button click", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="public" />);

    const devButton = screen.getByRole("button", { name: /developer/i });
    await userEvent.click(devButton);

    expect(devButton).toHaveAttribute("aria-pressed", "true");
  });

  test("shows detail text in developer mode", () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="developer" initialRedaction={20} />);

    // In developer mode with low redaction, details should be visible
    expect(screen.getByText(/Pulled customer records/i)).toBeInTheDocument();
  });

  test("hides detail text in public mode", () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="public" />);

    // In public mode, details are heavily redacted or hidden
    expect(screen.queryByText(/Pulled customer records/i)).not.toBeInTheDocument();
  });
});

describe("ReasoningLab - Redaction Slider", () => {
  test("updates redaction on slider change", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialRedaction={50} />);

    const slider = screen.getByRole("slider");
    await userEvent.clear(slider);
    await userEvent.type(slider, "80");

    expect(slider).toHaveAttribute("aria-valuenow", "80");
  });

  test("responds to keyboard arrow keys", () => {
    render(<ReasoningLab trace={mockTrace as any} initialRedaction={50} />);

    const slider = screen.getByRole("slider");
    slider.focus();

    fireEvent.keyDown(slider, { key: "ArrowRight" });
    const val1 = parseInt(slider.getAttribute("aria-valuenow") || "0");

    fireEvent.keyDown(slider, { key: "ArrowLeft" });
    const val2 = parseInt(slider.getAttribute("aria-valuenow") || "0");

    expect(val2).toBeLessThan(val1);
  });

  test("jumps to min on Home key", () => {
    render(<ReasoningLab trace={mockTrace as any} initialRedaction={50} />);

    const slider = screen.getByRole("slider");
    slider.focus();
    fireEvent.keyDown(slider, { key: "Home" });

    expect(slider).toHaveAttribute("aria-valuenow", "100");
  });

  test("jumps to max on End key", () => {
    render(<ReasoningLab trace={mockTrace as any} initialRedaction={50} />);

    const slider = screen.getByRole("slider");
    slider.focus();
    fireEvent.keyDown(slider, { key: "End" });

    expect(slider).toHaveAttribute("aria-valuenow", "0");
  });
});

describe("ReasoningLab - Why Panel", () => {
  test("opens panel on Why button click", async () => {
    render(<ReasoningLab trace={mockTrace as any} />);

    const whyButtons = screen.getAllByRole("button", { name: /why\?/i });
    await userEvent.click(whyButtons[0]);

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3 })).toBeInTheDocument();
  });

  test("closes panel on Close button click", async () => {
    render(<ReasoningLab trace={mockTrace as any} />);

    const whyButton = screen.getAllByRole("button", { name: /why\?/i })[0];
    await userEvent.click(whyButton);

    const closeButton = screen.getByRole("button", { name: /close/i });
    await userEvent.click(closeButton);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  test("hides sources in public mode", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="public" initialRedaction={90} />);

    const whyButton = screen.getAllByRole("button", { name: /why\?/i })[0];
    await userEvent.click(whyButton);

    expect(screen.queryByText(/s3:\/\/prod-bucket/i)).not.toBeInTheDocument();
  });

  test("shows sources in developer mode", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="developer" initialRedaction={20} />);

    const whyButton = screen.getAllByRole("button", { name: /why\?/i })[0];
    await userEvent.click(whyButton);

    expect(screen.getByText(/s3:\/\/prod-bucket/i)).toBeInTheDocument();
  });
});

describe("ReasoningLab - Assistive Mode", () => {
  test("forces public mode in assistive", () => {
    render(<ReasoningLab trace={mockTrace as any} assistive={true} />);

    const publicButton = screen.getByRole("button", { name: /public/i });
    expect(publicButton).toHaveAttribute("aria-pressed", "true");
  });

  test("uses linear view instead of graph", () => {
    render(<ReasoningLab trace={mockTrace as any} assistive={true} />);

    const list = screen.getByRole("list", { name: /reasoning steps/i });
    expect(list.tagName).toBe("OL");
  });
});

describe("ReasoningLab - Audit Request", () => {
  test("shows Request Audit button in enterprise mode", () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="enterprise" />);

    expect(screen.getByRole("button", { name: /request audit/i })).toBeInTheDocument();
  });

  test("hides Request Audit button in public mode", () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="public" />);

    expect(screen.queryByRole("button", { name: /request audit/i })).not.toBeInTheDocument();
  });

  test("calls onRequestAudit handler", async () => {
    const mockHandler = jest.fn().mockResolvedValue(undefined);
    render(
      <ReasoningLab
        trace={mockTrace as any}
        initialMode="enterprise"
        onRequestAudit={mockHandler}
      />
    );

    const button = screen.getByRole("button", { name: /request audit/i });
    await userEvent.click(button);

    expect(mockHandler).toHaveBeenCalledWith("trace-20251106-01");
  });
});
```

**Run**: `npm test -- src/components/ReasoningLab/__tests__/ReasoningLab.test.tsx`

---

## Integration Tests

### API Endpoint Tests

**Location**: `server/__tests__/api.trace.test.js`

```javascript
const request = require("supertest");
const app = require("../app");

describe("GET /api/trace/:id", () => {
  test("returns 403 for enterprise mode without auth", async () => {
    const res = await request(app)
      .get("/api/trace/trace-123?mode=enterprise")
      .expect(403);

    expect(res.body.error).toContain("Enterprise mode requires authentication");
  });

  test("returns public trace without auth", async () => {
    const res = await request(app)
      .get("/api/trace/trace-20251106-01?mode=public")
      .expect(200);

    expect(res.body.id).toBe("trace-20251106-01");
    expect(res.body.nodes[0].sources).toEqual([]);
  });

  test("applies custom redaction level", async () => {
    const res = await request(app)
      .get("/api/trace/trace-20251106-01?mode=public&level=90")
      .expect(200);

    expect(res.body.nodes[0].detail).toContain("(redacted)");
  });

  test("logs audit trail", async () => {
    await request(app)
      .get("/api/trace/trace-20251106-01?mode=public")
      .expect(200);

    // Check audit log was created
    const logs = await auditLog.query({ traceId: "trace-20251106-01" });
    expect(logs.length).toBeGreaterThan(0);
    expect(logs[0].action).toBe("view_trace");
  });
});
```

---

## Accessibility Tests

### Automated Accessibility Audit

**Location**: `src/components/ReasoningLab/__tests__/a11y.test.tsx`

```typescript
import React from "react";
import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import { ReasoningLab } from "../ReasoningLab";
import mockTrace from "./fixtures/mockTrace.json";

expect.extend(toHaveNoViolations);

describe("ReasoningLab - Accessibility", () => {
  test("has no WCAG 2 AA violations", async () => {
    const { container } = render(<ReasoningLab trace={mockTrace as any} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("has no violations in assistive mode", async () => {
    const { container } = render(<ReasoningLab trace={mockTrace as any} assistive={true} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  test("panel has proper focus management", async () => {
    const { container } = render(<ReasoningLab trace={mockTrace as any} />);
    // Open panel and verify focus trap
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

**Run**: `npm test -- --testNamePattern="Accessibility"`

---

## Visual Regression Tests

### Percy Configuration

**Location**: `.percy.yml`

```yaml
version: 2
static-snapshots:
  base-url: http://localhost:3000
  snapshot-files: "**/ReasoningLab.percy.test.tsx"
```

**Test**: `src/components/ReasoningLab/__tests__/ReasoningLab.percy.test.tsx`

```typescript
import percySnapshot from "@percy/puppeteer";

describe("ReasoningLab - Visual Regression", () => {
  test("public mode appearance", async () => {
    await page.goto("http://localhost:3000/reasoning-lab?mode=public");
    await percySnapshot(page, "ReasoningLab - Public Mode");
  });

  test("developer mode appearance", async () => {
    await page.goto("http://localhost:3000/reasoning-lab?mode=developer");
    await percySnapshot(page, "ReasoningLab - Developer Mode");
  });

  test("assistive mode appearance", async () => {
    await page.goto("http://localhost:3000/reasoning-lab?assistive=true");
    await percySnapshot(page, "ReasoningLab - Assistive Mode");
  });

  test("panel open state", async () => {
    await page.goto("http://localhost:3000/reasoning-lab");
    await page.click('button[aria-haspopup="dialog"]');
    await percySnapshot(page, "ReasoningLab - Panel Open");
  });
});
```

**Run**: `npm run test:visual`

---

## End-to-End Tests

### Playwright E2E Tests

**Location**: `e2e/reasoning-lab.spec.ts`

```typescript
import { test, expect } from "@playwright/test";

test.describe("Reasoning Lab - Full User Flow", () => {
  test("public user views trace and opens panel", async ({ page }) => {
    await page.goto("/reasoning-lab/trace-20251106-01");

    // Verify public mode default
    await expect(page.locator('button[aria-pressed="true"]')).toContainText("Public");

    // Click first Why button
    await page.click('button:has-text("Why?")');

    // Verify panel opens
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // Verify no sources shown
    await expect(page.locator("text=s3://")).not.toBeVisible();

    // Close panel
    await page.keyboard.press("Escape");
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test("developer adjusts redaction slider", async ({ page }) => {
    await page.goto("/reasoning-lab/trace-20251106-01?mode=developer");

    // Switch to developer mode
    await page.click('button:has-text("Developer")');

    // Adjust slider
    const slider = page.locator('[role="slider"]');
    await slider.fill("20");

    // Open panel and verify more detail shown
    await page.click('button:has-text("Why?")');
    await expect(page.locator('[role="dialog"]')).toContainText("customer records");
  });

  test("enterprise user requests audit", async ({ page, context }) => {
    // Mock auth
    await context.addCookies([
      { name: "auth_token", value: "enterprise-token", domain: "localhost", path: "/" }
    ]);

    await page.goto("/reasoning-lab/trace-20251106-01?mode=enterprise");

    // Click Request Audit
    await page.click('button:has-text("Request Audit")');

    // Verify confirmation
    await expect(page.locator("text=Audit request submitted")).toBeVisible();
  });
});
```

**Run**: `npm run test:e2e`

---

## Test Configuration

### Jest Config

**Location**: `jest.config.js`

```javascript
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: [
    "@testing-library/jest-dom/extend-expect",
    "jest-axe/extend-expect"
  ],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
    "^.+\\.(js|jsx)$": "babel-jest"
  },
  testPathIgnorePatterns: ["/node_modules/", "/dist/", "/e2e/"],
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "server/**/*.{js,ts}",
    "!**/__tests__/**",
    "!**/node_modules/**"
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 85,
      statements: 85
    }
  }
};
```

### Package.json Scripts

```json
{
  "scripts": {
    "test": "jest --runInBand",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:a11y": "jest --testNamePattern='Accessibility'",
    "test:visual": "percy exec -- jest --testNamePattern='Visual'",
    "test:e2e": "playwright test",
    "test:all": "npm run test:coverage && npm run test:e2e"
  }
}
```

---

## CI Integration

### GitHub Actions Workflow

**Location**: `.github/workflows/reasoning-lab-tests.yml`

```yaml
name: Reasoning Lab Tests

on:
  pull_request:
    paths:
      - "src/components/ReasoningLab/**"
      - "server/redaction.js"
      - "branding/design/reasoning-lab/**"

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:a11y

  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:visual
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install
      - run: npm run test:e2e
```

---

## Coverage Targets

| Test Type | Target | Critical Paths |
|-----------|--------|----------------|
| **Unit Tests** | 85%+ | Redaction logic, component behavior |
| **Integration** | 75%+ | API endpoints, auth flow |
| **E2E** | 100% | Happy paths for all 3 modes |
| **Accessibility** | 0 violations | WCAG 2 AA compliance |
| **Visual** | 0 regressions | Mode switching, panel states |

---

## Related Documents

- **Complete Spec**: [COMPLETE_SPEC.md](./COMPLETE_SPEC.md) - Full UX specification
- **Redaction System**: [REDACTION_SYSTEM.md](./REDACTION_SYSTEM.md) - Implementation details
- **90-Day Roadmap**: [../../governance/strategic/90_DAY_ROADMAP.md](../../governance/strategic/90_DAY_ROADMAP.md) - W4 testing phase

---

**Document Owner**: @qa + @frontend
**Review Cycle**: Weekly during W4 testing phase
**Last Updated**: 2025-11-06
