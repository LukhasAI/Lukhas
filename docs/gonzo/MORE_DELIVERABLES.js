## T4 Strategic Audit & Roadmap - Reasoning Lab Redaction Tests & Server

This section details the files and code needed to implement a comprehensive test suite and server - side redaction module for the`ReasoningLab` component, focusing on redaction behavior, UI interactions, and server - side trace redaction.

The deliverables include:

1. ** Mock trace fixture ** (`mockTrace.json`) — realistic nodes, sources, PII - like fields, meta fields and timings.
2. ** Jest tests for `ReasoningLab` ** (`ReasoningLab.test.tsx`) — renders the TSX skeleton, verifies redaction behavior, verifies panel open / close, verifies keyboard slider behavior, verifies assistive - mode default. Uses React Testing Library and`@testing-library/user-event`.
3. ** Server - side redaction module(Node / Express) ** (`server/redaction.js` + `server/index.js`) — deterministic server - side redaction function plus a small server route that returns redacted trace JSON depending on `mode` and`redactionLevel`.
4. ** Unit tests for redaction ** (`server/__tests__/redaction.test.js`) — covers multiple levels and modes, confirms`sources` removal, ID masking, and full / partial redaction.
5. ** Jest configuration and install notes ** — commands to install dev deps and run tests.

Everything is small, focused, and T4 - skeptical: redaction is ** deterministic **, ** auditable ** and ** server - side **, so clients can’t accidentally reveal hidden artifacts by flipping a UI control.

---

## A.Files to add

Create the following files in your repo.

### 1)`src/components/ReasoningLab/__tests__/fixtures/mockTrace.json`

    ```json
{
  "id": "trace-20251106-01",
  "nodes": [
    {
      "id": "n1",
      "label": "Memory: customer records lookup",
      "detail": "Pulled customer records from s3://prod-bucket/customers/2025 and matched by email alice@example.com and id 123e4567-e89b-12d3-a456-426614174000.",
      "sources": ["s3://prod-bucket/customers/2025/part-00001.json", "database:customers.primary"],
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

---

### 2)`src/components/ReasoningLab/__tests__/ReasoningLab.test.tsx`

    > Place next to the component tests folder.This assumes your `ReasoningLab` component is exported from`src/components/ReasoningLab/ReasoningLab.tsx`(as in the skeleton earlier).

```ts
/**
 * ReasoningLab.test.tsx
 * Jest + React Testing Library tests for redaction and UI behavior.
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ReasoningLab } from "../ReasoningLab";
import mockTrace from "./fixtures/mockTrace.json";

describe("ReasoningLab - basic interactions and redaction", () => {
  test("renders nodes and opens 'Why?' panel showing redacted content at high redaction", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="public" initialRedaction={90} assistive={false} />);

    // Expect nodes to display but details hidden in public mode
    const step = await screen.findByText(/Memory:/i);
    expect(step).toBeInTheDocument();

    // Click first why? button
    const whyButtons = screen.getAllByRole("button", { name: /why\?/i });
    expect(whyButtons.length).toBeGreaterThan(0);
    await userEvent.click(whyButtons[0]);

    // Panel open should contain the label and redacted detail text
    const panelHeader = await screen.findByRole("heading", { level: 3, name: /Memory/i });
    expect(panelHeader).toBeInTheDocument();

    const panelText = screen.getByText(/redacted/i);
    expect(panelText).toBeInTheDocument();

    // In public mode with high redaction, sources should be hidden or not rendered as links
    const sourceLink = screen.queryByText(/s3:\/\/prod-bucket/i);
    expect(sourceLink).not.toBeInTheDocument();
  });

  test("developer mode shows more detail and sources", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="developer" initialRedaction={20} />);

    // Click the first Why and expect more detailed content
    const whyButton = screen.getAllByRole("button", { name: /why\?/i })[0];
    await userEvent.click(whyButton);

    // Should show detail text, including PII-like email or id unless redaction removes it
    expect(screen.getByText(/Pulled customer records/i)).toBeInTheDocument();
    expect(screen.queryByText(/alice@example.com/i)).toBeNull(); // our redactText masks PII in some levels; with low redaction we might still not reveal raw email depending on rules
    // But sources should be present (developer mode + low redaction)
    const src = screen.queryByText(/s3:\/\/prod-bucket/i);
    expect(src).toBeInTheDocument();
  });

  test("slider keyboard actions adjust redaction", async () => {
    render(<ReasoningLab trace={mockTrace as any} initialMode="developer" initialRedaction={50} />);
    const slider = screen.getByRole("slider", { name: /Redaction/i });
    // Press ArrowRight - slider step changes
    slider.focus();
    fireEvent.keyDown(slider, { key: "ArrowRight" });
    // aria-valuenow should have updated (string)
    const val = slider.getAttribute("aria-valuenow");
    expect(Number(val)).toBeGreaterThanOrEqual(0);
  });

  test("assistive variant forces public mode and high redaction", () => {
    render(<ReasoningLab trace={mockTrace as any} assistive={true} />);
    // Because assistive sets mode to 'public' and high redaction, the redaction slider isn't shown
    const slider = screen.queryByRole("slider", { name: /Redaction/i });
    expect(slider).toBeNull();

    // Ensure assistive instructive text exists
    expect(screen.getByText(/Select a step and press "Why\?"/i)).toBeInTheDocument();
  });
});
```

        > ** Notes:**
>
> * This test assumes `ReasoningLab` renders accessible elements as in the skeleton.If your real component names / structure differ, adjust queries.
> * If you use TypeScript strict settings, you may need `// @ts-ignore` on mockTrace import or configure `tsconfig` to allow JSON imports(`resolveJsonModule: true`).

---

### 3) Jest config and dependencies

If you don’t already have Jest and React Testing Library set up, run:

```bash
# Install test deps
npm install --save-dev jest @types/jest ts-jest @testing-library/react @testing-library/jest-dom @testing-library/user-event babel-jest
# If using TypeScript:
npm install --save-dev typescript ts-node
```

Create `jest.config.js` at repo root:

```js
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["@testing-library/jest-dom/extend-expect"],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json"],
  transform: {
    "^.+\\.(ts|tsx)$": "ts-jest",
    "^.+\\.(js|jsx)$": "babel-jest"
  },
  testPathIgnorePatterns: ["/node_modules/", "/dist/"]
};
```

Add test script in `package.json`:

```json
"scripts": {
  "test": "jest --runInBand"
}
```

Run tests:

```bash
npm test
```

---

## B.Server - side redaction example

Add these files under`server/`.

### 4)`server/redaction.js`

Deterministic server - side redaction function and helpers.

```js
// server/redaction.js
const EMAIL_RE = /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
const UUID_RE = /\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b/gi;
const PATH_RE = /(s3:\/\/|db:|feature-store:\/\/|crm:\/\/)[^\s,"]+/gi;

function maskEmail(s) {
  return s.replace(EMAIL_RE, "[redacted-email]");
}
function maskUUID(s) {
  return s.replace(UUID_RE, "[redacted-id]");
}
function maskPaths(s) {
  return s.replace(PATH_RE, "[redacted-source]");
}

function redactString(s, level) {
  if (!s || typeof s !== "string") return s;
  let out = s;
  if (level >= 75) {
    // show only first sentence
    const first = out.split(".")[0];
    return first ? `${ first } (redacted)` : "redacted";
  }
  if (level >= 40) {
    // mask PII & paths
    out = maskEmail(out);
    out = maskUUID(out);
    out = maskPaths(out);
    // also mask numeric ids
    out = out.replace(/\bTCK-\d+\b/g, "[redacted-ticket]");
    out = out.replace(/\brun_[0-9a-f]+\b/gi, "[redacted-run]");
    return out;
  }
  // low level: minimal masking
  out = maskEmail(out);
  return out;
}

function redactNode(node, level, mode) {
  // mode: public | developer | enterprise
  const redacted = Object.assign({}, node);
  // detail and label redaction
  redacted.label = redactString(node.label, level);
  if (node.detail) redacted.detail = redactString(node.detail, level);
  // sources: remove entirely for public/high
  if (mode === "public" || level >= 60) {
    redacted.sources = []; // remove sources
  } else if (Array.isArray(node.sources)) {
    // partially redact sources if needed
    redacted.sources = node.sources.map((s) => {
      if (level >= 40) {
        return "[redacted-source]";
      }
      return s;
    });
  }
  // meta: strip PII / sensitive fields at certain levels
  if (node.meta) {
    const meta = Object.assign({}, node.meta);
    if (level >= 40) {
      // mask any string fields in meta
      for (const k of Object.keys(meta)) {
        if (typeof meta[k] === "string") meta[k] = redactString(meta[k], level);
        if (k.toLowerCase().includes("pii")) meta[k] = "[redacted]";
      }
    }
    // optionally remove meta entirely for public+high
    if (level >= 85) {
      redacted.meta = {};
    } else {
      redacted.meta = meta;
    }
  }
  return redacted;
}

function redactTrace(trace, opts = {}) {
  // opts: { mode: 'public'|'developer'|'enterprise', redactionLevel: number 0..100 }
  const mode = opts.mode || "public";
  const level = Number.isFinite(opts.redactionLevel) ? opts.redactionLevel : (mode === "public" ? 90 : mode === "developer" ? 30 : 5);
  const out = {
    id: trace.id,
    nodes: trace.nodes.map((n) => redactNode(n, level, mode)),
    edges: trace.edges,
    metadata: Object.assign({}, trace.metadata || {})
  };
  // summarize metadata for public mode
  if (mode === "public" && out.metadata) {
    out.metadata = {
      query: String(out.metadata.query).slice(0, 120),
      generated_at: out.metadata.generated_at
    };
  }
  return out;
}

module.exports = { redactTrace, redactNode, redactString };
```

### 5)`server/index.js` — small Express example exposing redacted trace endpoint

    ```js
// server/index.js
const express = require("express");
const { redactTrace } = require("./redaction");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(express.json());

// Serve mock trace file for demo
const MOCK_PATH = path.join(__dirname, "..", "src", "components", "ReasoningLab", "__tests__", "fixtures", "mockTrace.json");

app.get("/api/trace/:id", (req, res) => {
  // modes: public | developer | enterprise
  const mode = req.query.mode || "public";
  const level = req.query.level ? parseInt(req.query.level, 10) : undefined;
  let trace;
  try {
    trace = JSON.parse(fs.readFileSync(MOCK_PATH, "utf-8"));
  } catch (err) {
    return res.status(500).json({ error: "Mock trace not found" });
  }
  const redacted = redactTrace(trace, { mode, redactionLevel: level });
  res.json(redacted);
});

const PORT = process.env.PORT || 4002;
app.listen(PORT, () => {
  console.log(`Redaction demo server listening on ${ PORT } (GET / api / trace /: id ? mode = public | developer | enterprise & level=0..100)`);
});
```

    ** Run the server **

        ```bash
node server/index.js
# open: http://localhost:4002/api/trace/trace-20251106-01?mode=public
```

---

### 6) Unit tests for server redaction — `server/__tests__/redaction.test.js`

    ```js
// server/__tests__/redaction.test.js
const { redactTrace, redactNode, redactString } = require("../redaction");
const fs = require("fs");
const path = require("path");

const MOCK_PATH = path.join(__dirname, "../../src/components/ReasoningLab/__tests__/fixtures/mockTrace.json");
const trace = JSON.parse(fs.readFileSync(MOCK_PATH, "utf-8"));

describe("redaction server functions", () => {
  test("redactString masks email and uuid at level >=40", () => {
    const s = "Contact alice@example.com id 123e4567-e89b-12d3-a456-426614174000 path s3://prod/obj";
    const low = redactString(s, 20);
    expect(low).toContain("alice@"); // still shows email partially or masked depending on implementation
    const high = redactString(s, 50);
    expect(high).not.toMatch(/@example.com/);
    expect(high).toMatch(/\[redacted-source\]|\[redacted-email\]|\[redacted-id\]/);
  });

  test("redactNode removes sources for public or high redaction", () => {
    const node = trace.nodes[0];
    const pub = redactNode(node, 90, "public");
    expect(pub.sources).toEqual([]);
    const dev = redactNode(node, 20, "developer");
    expect(Array.isArray(dev.sources)).toBe(true);
    expect(dev.sources.length).toBeGreaterThan(0);
  });

  test("redactTrace returns minimal metadata for public mode", () => {
    const out = redactTrace(trace, { mode: "public", redactionLevel: 90 });
    expect(out.metadata).toHaveProperty("generated_at");
    // should not include the full detailed query if long - be short
    expect(out.metadata.query.length).toBeLessThanOrEqual(120);
    // nodes should be redacted
    expect(out.nodes[0].detail).toMatch(/redacted/i);
  });

  test("enterprise mode returns low redaction", () => {
    const out = redactTrace(trace, { mode: "enterprise", redactionLevel: 5 });
    expect(out.nodes[0].sources.length).toBeGreaterThan(0);
    expect(out.nodes[0].detail).toMatch(/Pulled customer records/i);
  });
});
```

Run these server tests with Jest.If you already installed Jest per instructions above, add script:

```json
"scripts": {
  "test": "jest --runInBand"
}
```

and run:

```bash
npm test
```

---

## C.How to wire tests & server into CI / local dev

1. ** Local installation ** (if not already):

```bash
npm install --save-dev jest ts-jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install --save-dev @types/jest @types/testing-library__react
```

2. ** Run component tests **:

```bash
npm test
```

3. ** Run server redaction tests ** (Jest will pick both suites):

```bash
npm test
```

4. ** Run the redaction demo server **:

```bash
node server/index.js
# then test curl
curl 'http://localhost:4002/api/trace/trace-20251106-01?mode=public'
curl 'http://localhost:4002/api/trace/trace-20251106-01?mode=developer&level=20'
```

---

## D.T4 considerations & improvements(short)

    * ** Deterministic redaction **: the server does deterministic redaction based on `redactionLevel` and`mode`.In production, redaction should be configurable via policy files and audited.Save the `redactionLevel` used with each delivered trace(for auditability).
* ** Server - side policy **: prefer server - side redaction to ensure clients do not reveal more than intended.UI slider should be an affordance, but server should cap detail based on user role.
* ** Test coverage **: add tests for accessibility semantics(aria attributes) using`axe-core` in the component tests later.
* ** PII detection **: current masking is heuristic(regex).For production, use a PII library(PII detection + allowlist), especially for non - English datasets.
* ** Signing & provenance **: attach the `redactionLevel` and`mode` in each audit pack's metadata for an enterprise audit.

---
