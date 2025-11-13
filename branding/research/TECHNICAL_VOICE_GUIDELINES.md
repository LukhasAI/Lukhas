# Technical Voice Guidelines

> **🔧 Mechanical Clarity for Developer-Facing Content**

**Version**: 1.0
**Date**: 2025-11-06
**Status**: ✅ **ACTIVE GUIDELINES** (Developer Content Only)
**Inspired By**: [Visionary Enhancements Research](../../docs/research/brand_philosophy/VISIONARY_ENHANCEMENTS_RESEARCH.md)
**Reconciliation**: [GONZO_RECONCILIATION.md](../../docs/research/brand_philosophy/GONZO_RECONCILIATION.md)

---

## Executive Summary

**Technical Voice** is a variant of the [3-Layer Tone System](../tone/LUKHAS_3_LAYER_TONE_SYSTEM.md) optimized for **developer-facing content only**. It adjusts the Academic layer to prioritize mechanical clarity, precision, and reduced anthropomorphism in technical contexts.

**Core Principle**: Technical content should be clear, precise, and action-oriented—not emotionally expressive.

**Scope**:
- ✅ **Applied to**: API documentation, error messages, system logs, developer guides, technical status messages
- ❌ **NOT Applied to**: Marketing content, general user UX, assistive mode content, product descriptions

---

## Philosophy

### Why Technical Voice?

The standard LUKHAS voice uses:
- First-person pronouns ("I", "we")
- Emotional expressions ("I'm excited to help")
- Poetic metaphors ("Neural Gardens", "Constellation Framework")

This works well for general users but can feel inappropriate in technical contexts where developers need:
- **Precision**: Exact terminology, no ambiguity
- **Actionability**: Clear next steps, no fluff
- **Consistency**: Predictable patterns, no personality variation
- **Scannability**: Dense information, minimal prose

**Technical Voice** reduces anthropomorphism and emotional expression in technical contexts without abandoning the LUKHAS brand entirely.

---

## Voice Transformation Table

This table shows how to transform standard LUKHAS voice into technical voice for developer contexts.

### API Error Messages

| Scenario | Standard Voice | Technical Voice |
|----------|----------------|-----------------|
| **Authentication failure** | "I'm sorry, I couldn't verify your identity. Please check your credentials and try again." | "Authentication failed. Verify `api_key` and `namespace` parameters. Status: 401" |
| **Rate limit exceeded** | "Whoa, you're moving fast! We need to slow down a bit. Please wait 60 seconds before trying again." | "Rate limit exceeded. Retry after 60 seconds. Current limit: 100 req/min. Header: `Retry-After`" |
| **Invalid parameter** | "Hmm, I don't understand the value you provided for 'temperature'. It should be between 0 and 1." | "Invalid parameter: `temperature=1.5`. Expected: float in range [0.0, 1.0]. Provided: 1.5" |
| **Resource not found** | "I couldn't find the memory module you're looking for. Double-check the ID?" | "Resource not found: `memory_module_id=abc123`. Status: 404. Verify resource exists in namespace." |
| **Server error** | "Oops! Something went wrong on my end. I've logged the error and we'll look into it. Please try again in a moment." | "Internal server error. Request ID: `req_abc123`. Logged. Retry with exponential backoff. Status: 500" |

### System Status Messages

| Scenario | Standard Voice | Technical Voice |
|----------|----------------|-----------------|
| **Deployment starting** | "I'm deploying your new configuration now. This might take a minute." | "Deployment initiated. Estimated duration: 60-90 seconds. Status: `in_progress`" |
| **Backup completed** | "Great news! Your backup finished successfully. All your data is safe." | "Backup completed. Size: 2.4 GB. Duration: 45s. Checksum: `sha256:abc...`. Status: `success`" |
| **Service degradation** | "I'm experiencing some slowness right now. Performance might be impacted for the next 15 minutes." | "Service degradation detected. P95 latency: 850ms (baseline: 200ms). ETA resolution: 15 min. Incident: `INC-2025-123`" |
| **Maintenance scheduled** | "Heads up: I'll be down for scheduled maintenance tomorrow from 2-4 AM UTC." | "Scheduled maintenance: 2025-11-07 02:00-04:00 UTC. Expected downtime: 2 hours. Notification: 24h advance." |

### Developer Documentation

| Scenario | Standard Voice | Technical Voice |
|----------|----------------|-----------------|
| **SDK installation** | "Let's get you started! Install the LUKHAS SDK with pip." | "Install via pip: `pip install lukhas-sdk>=2.0.0`. Verify installation: `lukhas --version`" |
| **Configuration guide** | "Now we'll configure your API key. This tells me who you are." | "Configure API key in environment: `export LUKHAS_API_KEY=your_key`. Alternative: pass to `LukhasClient(api_key='...')`" |
| **Best practices** | "I recommend using exponential backoff when retrying failed requests. It's kinder to both of us!" | "Implement exponential backoff for retries. Formula: `delay = base_delay * (2 ** attempt)`. Max attempts: 5. Example implementation below." |
| **Deprecation notice** | "Just a heads-up: the `/v1/analyze` endpoint is being retired in 90 days. Please migrate to `/v2/analyze`." | "Deprecation: `/v1/analyze` EOL 2026-02-06 (90 days). Migrate to `/v2/analyze`. Breaking changes: `model` param now required. Migration guide: [link]" |

### Code Comments

| Scenario | Standard Voice | Technical Voice |
|----------|----------------|-----------------|
| **Function docstring** | "This function helps me understand your query and figure out the best way to respond." | "Parses user query and selects optimal response strategy based on intent classification and context." |
| **Warning comment** | "Be careful here! If you change this value, things might break in unexpected ways." | "Critical: Modifying `MAX_CONTEXT_SIZE` affects memory allocation. Values >8192 may cause OOM errors." |
| **TODO comment** | "I'd love to add support for streaming responses here eventually." | "TODO: Implement streaming support for large responses. Requires chunked transfer encoding." |

---

## Application Guidelines

### Where to Apply Technical Voice

#### 1. API Documentation (lukhas.dev)

**Full technical voice** for:
- API reference pages
- Endpoint specifications
- Request/response schemas
- Error code tables
- Rate limiting documentation

**Example API Reference Entry**:

```markdown
## POST /v2/reasoning/analyze

Analyzes user query and generates reasoning trace.

**Authentication**: Required (Bearer token or API key)

**Request Body**:
```json
{
  "query": "string (required, max 10000 chars)",
  "model": "string (required, one of: 'gpt-4', 'claude-2')",
  "temperature": "float (optional, default: 0.7, range: [0.0, 1.0])",
  "max_tokens": "integer (optional, default: 2000, range: [1, 8000])"
}
```

**Response**: 200 OK
```json
{
  "reasoning_trace_id": "string",
  "status": "completed",
  "nodes": [...],
  "metadata": {...}
}
```

**Errors**:
- 400: Invalid parameters
- 401: Authentication failed
- 429: Rate limit exceeded
- 500: Internal server error

**Rate Limits**: 100 requests/minute (burst: 120)
```

---

#### 2. Error Messages & Logs

**System logs** (internal):
```
[2025-11-06 14:32:18] ERROR: Authentication failed for namespace=prod-acme, reason=invalid_signature
[2025-11-06 14:32:19] WARN: Rate limit approaching threshold: 95/100 req/min, namespace=prod-acme
[2025-11-06 14:32:20] INFO: Reasoning trace completed: trace_id=abc123, duration=234ms, nodes=12
```

**User-facing error messages** (API responses):
```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Invalid parameter: 'temperature'. Expected: float in range [0.0, 1.0]. Provided: 1.5",
    "param": "temperature",
    "provided": 1.5,
    "expected": "float [0.0, 1.0]",
    "request_id": "req_abc123"
  }
}
```

---

#### 3. Developer Guides & Tutorials

**Introduction sections**: Use standard LUKHAS voice (poetic/user-friendly) to welcome developers

**Technical sections**: Switch to technical voice for code examples, configurations, troubleshooting

**Example Structure**:

```markdown
# Getting Started with LUKHAS Reasoning API

Welcome to the LUKHAS Reasoning API! This guide will help you integrate
explainable AI reasoning into your applications. [← Poetic/User-Friendly]

## Prerequisites

- Python 3.9+
- pip package manager
- LUKHAS API key (obtain from dashboard)

[← Technical Voice starts here]

## Installation

Install via pip:

\`\`\`bash
pip install lukhas-sdk>=2.0.0
\`\`\`

Verify installation:

\`\`\`bash
lukhas --version
# Expected output: lukhas-sdk 2.0.0
\`\`\`

## Configuration

Set API key in environment:

\`\`\`bash
export LUKHAS_API_KEY=your_key_here
export LUKHAS_NAMESPACE=your_namespace
\`\`\`

Alternative: Pass directly to client:

\`\`\`python
from lukhas import LukhasClient

client = LukhasClient(
    api_key="your_key_here",
    namespace="your_namespace"
)
\`\`\`
```

---

#### 4. System Status & Monitoring

**Status page** (status.lukhas.ai):
```
┌─────────────────────────────────────────────┐
│ LUKHAS System Status                        │
├─────────────────────────────────────────────┤
│ ✅ API Endpoints         Operational        │
│ ✅ Reasoning Engine      Operational        │
│ ⚠️  Authentication       Degraded           │
│    P95 latency: 850ms (baseline: 200ms)    │
│    Incident: INC-2025-123                   │
│    ETA resolution: 15 minutes               │
│ ✅ Memory Storage        Operational        │
└─────────────────────────────────────────────┘
```

**Incident updates** (clear, factual, no emotion):
```
Incident: INC-2025-123
Status: Investigating
Started: 2025-11-06 14:30 UTC

14:30 UTC: Authentication service degraded. P95 latency: 850ms. Investigating.
14:35 UTC: Root cause identified: database connection pool exhaustion.
14:40 UTC: Deploying fix: increased pool size from 50 to 100 connections.
14:45 UTC: Fix deployed. Monitoring for stability.
14:50 UTC: Latency recovered. P95: 210ms. Incident resolved.
```

---

### Where NOT to Apply Technical Voice

#### ❌ Marketing Content
- Website landing pages (lukhas.ai)
- Product descriptions
- Feature announcements
- Blog posts
- Social media

**Keep standard voice**: Poetic, emotional, engaging

---

#### ❌ General User-Facing UX
- Application UI (buttons, menus, tooltips)
- Onboarding flows
- Settings pages
- Dashboard
- In-app messaging

**Keep standard voice**: User-friendly, first-person, helpful

---

#### ❌ Assistive Mode Content
- Simplified language (Flesch-Kincaid ≤8)
- Reduced jargon
- Emotional support for users with cognitive disabilities

**Keep standard voice**: Warm, patient, clear (but not technical)

---

#### ❌ Support Documentation (End Users)
- Help center articles for non-technical users
- Video tutorials
- FAQs for general audience

**Keep standard voice**: User-friendly, empathetic

---

## 3-Layer Tone System Integration

Technical Voice is a **variant of the Academic layer** for developer contexts. It does NOT replace the 3-Layer Tone System.

### Standard 3-Layer Distribution
- **Poetic (Accessible)**: 25-30%
- **User-Friendly (Artisan)**: 35-40%
- **Academic (Technical)**: 30-35%

### Developer Content Distribution
- **Poetic**: 10-15% (introductions, conclusions)
- **User-Friendly**: 20-25% (explanations, context)
- **Technical Voice**: 60-70% (code, specs, errors)

### Example: API Documentation Page

```markdown
# LUKHAS Reasoning API

[Poetic - 15%]
The Reasoning API brings transparency to AI decision-making, transforming
opaque predictions into crystal-clear reasoning traces you can audit,
debug, and trust.

## Quick Start

[User-Friendly - 25%]
This guide walks you through your first API call. You'll learn how to
authenticate, send a query, and receive a reasoning trace.

## Authentication

[Technical Voice - 60%]
Authentication requires Bearer token or API key in header:

\`\`\`http
POST /v2/reasoning/analyze
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
\`\`\`

### API Key Management

API keys are scoped to namespaces. Each key has:
- Read/write permissions
- Rate limits (default: 100 req/min)
- Expiration (optional, default: no expiration)

Obtain key from dashboard: https://lukhas.ai/dashboard/api-keys

[...]
```

---

## Voice Reduction Checklist

When converting standard voice to technical voice, apply these transformations:

### ✅ DO

1. **Remove first-person pronouns**
   - ❌ "I'm processing your request"
   - ✅ "Processing request"

2. **Remove emotional expressions**
   - ❌ "Great job! Your API key is valid."
   - ✅ "API key validated. Status: 200 OK"

3. **Use imperative verbs**
   - ❌ "You should probably set a timeout"
   - ✅ "Set timeout to prevent blocking"

4. **Include specific values**
   - ❌ "The request took too long"
   - ✅ "Request timeout: 30s (limit: 10s)"

5. **Provide actionable steps**
   - ❌ "Something went wrong with your request"
   - ✅ "Fix error: Set `model` parameter. Example: `model='gpt-4'`"

6. **Use technical terminology**
   - ❌ "I couldn't connect to the database"
   - ✅ "Database connection failed: Connection refused (ECONNREFUSED)"

### ❌ DON'T

1. **Don't eliminate ALL personality**
   - Still maintain LUKHAS brand identity
   - Use Constellation symbols (⚛️ 🛡️) sparingly in headers
   - Maintain professional, helpful tone

2. **Don't be unnecessarily cold**
   - ❌ "RTFM" or dismissive language
   - ✅ "See documentation: [link]"

3. **Don't abandon clarity**
   - ❌ Overuse jargon without explanation
   - ✅ Define terms on first use

4. **Don't skip context**
   - ❌ "Error 500"
   - ✅ "Internal server error (500). Request ID: abc123. Contact support if persists."

---

## Implementation Examples

### Example 1: SDK Error Handler

**Standard Voice** (user-facing application):
```python
class LukhasClient:
    def analyze(self, query: str) -> ReasoningTrace:
        try:
            response = self._api_call(query)
            return response.trace
        except AuthError:
            raise Exception(
                "I couldn't verify your API key. "
                "Please check that it's correct and try again."
            )
```

**Technical Voice** (developer-facing SDK):
```python
class LukhasClient:
    def analyze(self, query: str) -> ReasoningTrace:
        """
        Analyzes query and returns reasoning trace.

        Args:
            query: User query string (max 10000 chars)

        Returns:
            ReasoningTrace object with nodes and metadata

        Raises:
            AuthenticationError: Invalid or expired API key
            RateLimitError: Rate limit exceeded (100 req/min)
            ValidationError: Invalid query parameter
            APIError: Server error (status 5xx)
        """
        try:
            response = self._api_call(query)
            return response.trace
        except AuthError as e:
            raise AuthenticationError(
                "Authentication failed. Verify API key and namespace. "
                f"Status: 401. Request ID: {e.request_id}"
            )
```

---

### Example 2: API Error Response

**Standard Voice** (general users):
```json
{
  "error": {
    "message": "I'm sorry, but I couldn't process your request. The 'model' parameter is missing. Please specify which AI model you'd like me to use (like 'gpt-4' or 'claude-2')."
  }
}
```

**Technical Voice** (developers):
```json
{
  "error": {
    "code": "missing_required_parameter",
    "message": "Missing required parameter: 'model'",
    "param": "model",
    "type": "invalid_request_error",
    "expected": "string, one of: ['gpt-4', 'claude-2', 'gpt-3.5-turbo']",
    "documentation": "https://lukhas.dev/api/models",
    "request_id": "req_abc123"
  }
}
```

---

### Example 3: Configuration Validation

**Standard Voice** (settings UI):
```
⚠️ Oops! The timeout you entered (5 seconds) might be too short
for complex reasoning tasks. I recommend at least 30 seconds
to give me enough time to think things through.

[Use 30 seconds] [Keep 5 seconds]
```

**Technical Voice** (config file validation):
```
Config validation error: reasoning_timeout=5

Reasoning timeout too low. Minimum recommended: 30s.
Current: 5s may cause premature timeouts for complex traces.

Set in config:
  reasoning_timeout: 30  # seconds

Or via environment:
  export LUKHAS_REASONING_TIMEOUT=30
```

---

## Related Documents

**Visionary Research**:
- [VISIONARY_ENHANCEMENTS_RESEARCH.md](../../docs/research/brand_philosophy/VISIONARY_ENHANCEMENTS_RESEARCH.md) - Original mechanical clarity concepts

**Reconciliation**:
- [GONZO_RECONCILIATION.md](../../docs/research/brand_philosophy/GONZO_RECONCILIATION.md) - Selective adoption rationale

**Brand System**:
- [LUKHAS_3_LAYER_TONE_SYSTEM.md](../tone/LUKHAS_3_LAYER_TONE_SYSTEM.md) - Standard voice system
- [BRAND_GUIDELINES.md](../BRAND_GUIDELINES.md) - Overall brand guidelines
- [VOICE_PERSONALITY.md](../tone/VOICE_PERSONALITY.md) - Voice personality parameters

**Developer Resources**:
- [API_REFERENCE.md](../../docs/api/API_REFERENCE.md) - Technical API documentation
- [DEVELOPER_BRANDING.md](../developer/DEVELOPER_BRANDING.md) - Developer-specific brand guidelines

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-06 | Adopt technical voice (developer content only) | Improves developer experience without affecting general users |
| 2025-11-06 | Apply to API docs, errors, logs only | Bounded scope prevents brand fragmentation |
| 2025-11-06 | Maintain poetic layer in introductions | Preserves LUKHAS brand identity even in technical content |
| 2025-11-06 | Create voice transformation table | Provides clear conversion guidelines for content writers |

---

**Document Owner**: @web-architect + @developer-experience
**Review Cycle**: Quarterly or when updating API documentation
**Last Updated**: 2025-11-06
**Status**: Active Guidelines (Developer Content)

---

**🔧 Core Principle**: Technical clarity without abandoning LUKHAS identity. Reduce anthropomorphism in code, not in brand.
