# Reasoning Lab - Redaction System

> **🔒 Server-Side Deterministic Redaction Implementation**

**Version**: 1.0
**Date**: 2025-11-06
**Source**: [MORE_DELIVERABLES.js](../../../docs/gonzo/MORE_DELIVERABLES.js), [STRATEGY.md](../../../docs/gonzo/STRATEGY.md)
**Status**: ✅ Canonical
**Priority**: P0 (Security Critical)

---

## Overview

The Redaction System implements **server-side, deterministic redaction** for Reasoning Lab traces. This ensures users cannot bypass privacy controls by inspecting network traffic or modifying client code.

**Key Principles**:
- ✅ **Server-side enforcement**: Redaction happens before data leaves the server
- ✅ **Deterministic**: Same inputs always produce same outputs
- ✅ **Auditable**: Redaction level logged for compliance
- ✅ **Policy-driven**: Configurable via rules, not hardcoded
- ✅ **PII-aware**: Detects and masks emails, UUIDs, paths, tickets

---

## Architecture

```
┌─────────────┐
│   Client    │
│  (Request)  │
└──────┬──────┘
       │  GET /api/trace/:id?mode=public&level=80
       ▼
┌─────────────────────────────────────────────┐
│           Server (Node/Express)             │
│                                             │
│  1. Auth: Validate user role                │
│  2. Fetch: Load trace from DB/storage       │
│  3. Redact: Apply redaction policy          │
│     - redactTrace(trace, {mode, level})     │
│     - redactNode(node, level, mode)         │
│     - redactString(str, level)              │
│  4. Log: Record audit trail                 │
│  5. Return: Send redacted JSON              │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Client    │
│  (Display)  │
└─────────────┘
```

---

## Redaction Levels

| Level | Range | Behavior | Use Case |
|-------|-------|----------|----------|
| **None** | 0-10 | Full details, all sources, complete metadata | Enterprise audit, internal development |
| **Low** | 11-39 | Emails masked, paths intact, full metadata | Developer mode, integration testing |
| **Medium** | 40-74 | Emails, UUIDs, paths, ticket IDs masked | Developer mode (default), technical docs |
| **High** | 75-100 | First sentence only, no sources, no metadata | Public mode (default), marketing demos |

---

## Implementation

### Core Module: `server/redaction.js`

**Location**: `server/redaction.js` or `lukhas/api/reasoning/redaction.py` (Python version)

#### 1. PII Detection Patterns

```javascript
// Regex patterns for PII detection
const EMAIL_RE = /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
const UUID_RE = /\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b/gi;
const PATH_RE = /(s3:\/\/|db:|feature-store:\/\/|crm:\/\/)[^\s,"]+/gi;
const TICKET_RE = /\bTCK-\d+\b/g;
const RUN_ID_RE = /\brun_[0-9a-f]+\b/gi;

function maskEmail(s) {
  return s.replace(EMAIL_RE, "[redacted-email]");
}

function maskUUID(s) {
  return s.replace(UUID_RE, "[redacted-id]");
}

function maskPaths(s) {
  return s.replace(PATH_RE, "[redacted-source]");
}

function maskTickets(s) {
  return s.replace(TICKET_RE, "[redacted-ticket]");
}

function maskRunIDs(s) {
  return s.replace(RUN_ID_RE, "[redacted-run]");
}
```

#### 2. String Redaction

```javascript
function redactString(s, level) {
  if (!s || typeof s !== "string") return s;
  let out = s;

  if (level >= 75) {
    // HIGH: Show only first sentence
    const first = out.split(".")[0];
    return first ? `${first} (redacted)` : "redacted";
  }

  if (level >= 40) {
    // MEDIUM: Mask all PII and identifiers
    out = maskEmail(out);
    out = maskUUID(out);
    out = maskPaths(out);
    out = maskTickets(out);
    out = maskRunIDs(out);
    return out;
  }

  // LOW: Minimal masking (emails only)
  out = maskEmail(out);
  return out;
}
```

#### 3. Node Redaction

```javascript
function redactNode(node, level, mode) {
  const redacted = Object.assign({}, node);

  // Redact label and detail text
  redacted.label = redactString(node.label, level);
  if (node.detail) {
    redacted.detail = redactString(node.detail, level);
  }

  // Sources: Remove entirely for public/high redaction
  if (mode === "public" || level >= 60) {
    redacted.sources = [];
  } else if (Array.isArray(node.sources)) {
    redacted.sources = node.sources.map((s) => {
      if (level >= 40) {
        return "[redacted-source]";
      }
      return s;
    });
  }

  // Metadata: Strip PII and sensitive fields
  if (node.meta) {
    const meta = Object.assign({}, node.meta);

    if (level >= 40) {
      // Mask string fields in metadata
      for (const k of Object.keys(meta)) {
        if (typeof meta[k] === "string") {
          meta[k] = redactString(meta[k], level);
        }
        // Remove PII flags
        if (k.toLowerCase().includes("pii")) {
          meta[k] = "[redacted]";
        }
      }
    }

    // Remove metadata entirely for high redaction
    if (level >= 85) {
      redacted.meta = {};
    } else {
      redacted.meta = meta;
    }
  }

  return redacted;
}
```

#### 4. Trace Redaction

```javascript
function redactTrace(trace, opts = {}) {
  const mode = opts.mode || "public";

  // Default redaction levels per mode
  let level = opts.redactionLevel;
  if (!Number.isFinite(level)) {
    level = mode === "public" ? 90 :
            mode === "developer" ? 30 : 5;
  }

  const out = {
    id: trace.id,
    nodes: trace.nodes.map((n) => redactNode(n, level, mode)),
    edges: trace.edges,
    metadata: Object.assign({}, trace.metadata || {})
  };

  // Summarize metadata for public mode
  if (mode === "public" && out.metadata) {
    out.metadata = {
      query: String(out.metadata.query || "").slice(0, 120),
      generated_at: out.metadata.generated_at
    };
  }

  return out;
}

module.exports = { redactTrace, redactNode, redactString };
```

---

## API Endpoint

### Express Route: `/api/trace/:id`

```javascript
// server/routes/trace.js
const express = require("express");
const { redactTrace } = require("../redaction");
const router = express.Router();

router.get("/:id", async (req, res) => {
  const { id } = req.params;
  const mode = req.query.mode || "public";
  const level = req.query.level ? parseInt(req.query.level, 10) : undefined;

  // 1. Validate user role
  if (mode === "enterprise" && !req.user?.roles?.includes("enterprise")) {
    return res.status(403).json({ error: "Enterprise mode requires authentication" });
  }

  if (mode === "developer" && !req.user?.roles?.includes("developer")) {
    return res.status(403).json({ error: "Developer mode requires authentication" });
  }

  // 2. Fetch trace from database
  let trace;
  try {
    trace = await traceService.getById(id);
  } catch (err) {
    return res.status(404).json({ error: "Trace not found" });
  }

  // 3. Apply redaction
  const redacted = redactTrace(trace, { mode, redactionLevel: level });

  // 4. Audit log
  await auditLog.record({
    userId: req.user?.id || "anonymous",
    action: "view_trace",
    traceId: id,
    mode,
    redactionLevel: level,
    timestamp: new Date().toISOString()
  });

  // 5. Return redacted trace
  res.json(redacted);
});

module.exports = router;
```

---

## Python Implementation

For LUKHAS API (FastAPI):

```python
# lukhas/api/reasoning/redaction.py
import re
from typing import Any, Dict, List, Optional

EMAIL_RE = re.compile(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})')
UUID_RE = re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b', re.I)
PATH_RE = re.compile(r'(s3://|db:|feature-store://|crm://)[^\s,"]+')
TICKET_RE = re.compile(r'\bTCK-\d+\b')
RUN_ID_RE = re.compile(r'\brun_[0-9a-f]+\b', re.I)

def redact_string(s: str, level: int) -> str:
    if not s or not isinstance(s, str):
        return s

    if level >= 75:
        # HIGH: First sentence only
        first = s.split(".")[0]
        return f"{first} (redacted)" if first else "redacted"

    if level >= 40:
        # MEDIUM: Mask all PII
        s = EMAIL_RE.sub("[redacted-email]", s)
        s = UUID_RE.sub("[redacted-id]", s)
        s = PATH_RE.sub("[redacted-source]", s)
        s = TICKET_RE.sub("[redacted-ticket]", s)
        s = RUN_ID_RE.sub("[redacted-run]", s)
        return s

    # LOW: Emails only
    return EMAIL_RE.sub("[redacted-email]", s)

def redact_node(node: Dict[str, Any], level: int, mode: str) -> Dict[str, Any]:
    redacted = node.copy()

    redacted["label"] = redact_string(node.get("label", ""), level)
    if "detail" in node:
        redacted["detail"] = redact_string(node["detail"], level)

    # Sources
    if mode == "public" or level >= 60:
        redacted["sources"] = []
    elif "sources" in node and isinstance(node["sources"], list):
        if level >= 40:
            redacted["sources"] = ["[redacted-source]"] * len(node["sources"])
        else:
            redacted["sources"] = node["sources"]

    # Metadata
    if "meta" in node and isinstance(node["meta"], dict):
        meta = node["meta"].copy()
        if level >= 40:
            for k, v in meta.items():
                if isinstance(v, str):
                    meta[k] = redact_string(v, level)
                if "pii" in k.lower():
                    meta[k] = "[redacted]"
        redacted["meta"] = {} if level >= 85 else meta

    return redacted

def redact_trace(trace: Dict[str, Any], mode: str = "public", redaction_level: Optional[int] = None) -> Dict[str, Any]:
    if redaction_level is None:
        redaction_level = 90 if mode == "public" else (30 if mode == "developer" else 5)

    redacted = {
        "id": trace["id"],
        "nodes": [redact_node(n, redaction_level, mode) for n in trace.get("nodes", [])],
        "edges": trace.get("edges", []),
        "metadata": trace.get("metadata", {}).copy()
    }

    if mode == "public" and redacted["metadata"]:
        redacted["metadata"] = {
            "query": str(redacted["metadata"].get("query", ""))[:120],
            "generated_at": redacted["metadata"].get("generated_at")
        }

    return redacted
```

---

## Audit Logging

Every trace view must be logged for compliance:

```javascript
// server/auditLog.js
async function recordTraceView(data) {
  await db.auditLogs.insert({
    userId: data.userId,
    action: "view_trace",
    traceId: data.traceId,
    mode: data.mode,
    redactionLevel: data.redactionLevel,
    timestamp: new Date(),
    userAgent: data.userAgent,
    ipAddress: data.ipAddress
  });
}
```

**Retention Policy**:
- Audit logs: 7 years (enterprise compliance)
- Indexed by: userId, traceId, timestamp
- Encrypted at rest

---

## Testing Redaction

### Unit Tests

```javascript
// server/__tests__/redaction.test.js
const { redactString, redactNode, redactTrace } = require("../redaction");

describe("redactString", () => {
  test("masks email at level 40+", () => {
    const input = "Contact alice@example.com";
    expect(redactString(input, 50)).not.toContain("alice@example.com");
    expect(redactString(input, 50)).toContain("[redacted-email]");
  });

  test("masks UUIDs at level 40+", () => {
    const input = "ID: 123e4567-e89b-12d3-a456-426614174000";
    expect(redactString(input, 50)).toContain("[redacted-id]");
  });

  test("shows first sentence only at level 75+", () => {
    const input = "First sentence. Second sentence.";
    const result = redactString(input, 80);
    expect(result).toContain("First sentence");
    expect(result).toContain("(redacted)");
    expect(result).not.toContain("Second sentence");
  });
});

describe("redactNode", () => {
  test("removes sources in public mode", () => {
    const node = {
      id: "n1",
      label: "Test",
      sources: ["s3://bucket/file.json"]
    };
    const result = redactNode(node, 90, "public");
    expect(result.sources).toEqual([]);
  });

  test("preserves sources in developer mode with low redaction", () => {
    const node = {
      id: "n1",
      label: "Test",
      sources: ["s3://bucket/file.json"]
    };
    const result = redactNode(node, 20, "developer");
    expect(result.sources).toHaveLength(1);
  });
});

describe("redactTrace", () => {
  test("applies public mode defaults", () => {
    const trace = {
      id: "trace-1",
      nodes: [
        { id: "n1", label: "Test node", detail: "Full details here" }
      ],
      edges: []
    };
    const result = redactTrace(trace, { mode: "public" });
    expect(result.nodes[0].detail).toContain("(redacted)");
  });
});
```

### Integration Tests

```bash
# Test API endpoint with different modes
curl 'http://localhost:4002/api/trace/trace-123?mode=public'
curl 'http://localhost:4002/api/trace/trace-123?mode=developer&level=30'
curl 'http://localhost:4002/api/trace/trace-123?mode=enterprise&level=5'
```

---

## Security Best Practices

### ✅ DO

1. **Always redact on server**: Never send full data and redact client-side
2. **Validate user roles**: Check authentication before allowing mode access
3. **Log all views**: Audit trail for compliance
4. **Use allowlists**: For known-safe fields, explicitly allow (safer than denylisting)
5. **Cache redacted traces**: Pre-compute common redaction levels
6. **Rate limit**: Prevent trace enumeration attacks

### ❌ DON'T

1. **Don't trust client**: Client can modify redaction slider, server must enforce
2. **Don't leak in errors**: Error messages must not contain PII
3. **Don't hard-code patterns**: Use configurable policy files
4. **Don't skip audit logs**: Required for enterprise compliance
5. **Don't return IDs**: Even redacted, node/source IDs can leak info

---

## Configuration

### Redaction Policy File

```yaml
# config/redaction-policy.yml
redaction:
  pii_patterns:
    - name: email
      regex: "([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})"
      replacement: "[redacted-email]"
    - name: uuid
      regex: "\\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\\b"
      replacement: "[redacted-id]"

  mode_defaults:
    public:
      redaction_level: 90
      sources_visible: false
      metadata_visible: false
    developer:
      redaction_level: 30
      sources_visible: true
      metadata_visible: true
    enterprise:
      redaction_level: 5
      sources_visible: true
      metadata_visible: true

  field_policies:
    - field: "meta.pii_present"
      action: remove
      min_level: 40
    - field: "sources"
      action: remove
      modes: ["public"]
```

---

## Performance Optimization

**Target**: <100ms redaction time, <250ms total p95

**Strategies**:
1. **Cache redacted traces**: Redis with 5-minute TTL
2. **Pre-compute levels**: 0, 25, 50, 75, 100
3. **Lazy load metadata**: Only redact when "Why?" clicked
4. **Worker threads**: Offload complex regex to background
5. **Compiled regexes**: Pre-compile all patterns at startup

```javascript
// Caching example
const cache = new Redis();

async function getRedactedTrace(id, mode, level) {
  const cacheKey = `trace:${id}:${mode}:${level}`;
  const cached = await cache.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const trace = await loadTrace(id);
  const redacted = redactTrace(trace, { mode, redactionLevel: level });
  await cache.setex(cacheKey, 300, JSON.stringify(redacted)); // 5 min TTL
  return redacted;
}
```

---

## Related Documents

- **Complete Spec**: [COMPLETE_SPEC.md](./COMPLETE_SPEC.md) - Full UX and component interface
- **Testing Strategy**: [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Test fixtures and CI
- **90-Day Roadmap**: [../../governance/strategic/90_DAY_ROADMAP.md](../../governance/strategic/90_DAY_ROADMAP.md) - W3-W4 implementation timeline

---

**Document Owner**: @backend + @security
**Review Cycle**: Weekly during implementation, quarterly post-launch
**Last Updated**: 2025-11-06
