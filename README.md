---
status: active-matriz-transition
type: documentation
updated: 2025-10-26
---
# LUKHAS AI Platform

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17272572.svg)](https://doi.org/10.5281/zenodo.17272572)
[![Manifests](https://img.shields.io/badge/manifests-928-blue)](manifests/)
[![Smoke Tests](https://img.shields.io/badge/smoke%20tests-100%25-success)](tests/smoke/)
[![Lint Health](https://img.shields.io/badge/lint-97%25%20clean-brightgreen)](docs/audits/)
[![codecov](https://codecov.io/gh/LukhasAI/Lukhas/branch/main/graph/badge.svg)](https://codecov.io/gh/LukhasAI/Lukhas)
[![DX Examples Smoke](https://github.com/LukhasAI/Lukhas/actions/workflows/dx-examples-smoke.yml/badge.svg)](https://github.com/LukhasAI/Lukhas/actions/workflows/dx-examples-smoke.yml)

**A consciousness-aware AI development platform with distributed cognitive architecture.**

LUKHAS AI is a sophisticated cognitive platform that implements consciousness-inspired patterns for advanced AI applications. Built with a modular lane-based architecture, the platform enables safe development and deployment of consciousness-aware AI systems through strict boundaries and comprehensive governance.

## 🚨 MATRIZ Migration Update

**Team Announcement (Ready to Share):**

We've completed MATRIZ case standardization for all production code and integration tests!

**Completed:**
✅ serve/ (2 imports)
✅ core/ (2 imports)  
✅ tests/integration/ (20 imports)

**Status:** 3 PRs in CI validation

**Next:** tests/unit + tests/smoke (23 imports) - will migrate after current PRs pass CI

**CI Mode:** Warning (logs occurrences, doesn't block)
**Timeline:** Flip to blocking mode after critical tests are migrated and stable (~48 hours)

**Action Required:** Avoid large MATRIZ-related changes until migrations merge. Use uppercase `from MATRIZ import X` for new code.

Questions? See MATRIZ_MIGRATION_GUIDE.md

## ⚡ 30-Second Quickstart

```bash
# Install and run LUKHAS in 30 seconds
pip install -e . && pytest tests/smoke/
python3 -m uvicorn lukhas.adapters.openai.api:get_app --factory --host 0.0.0.0 --port 8000 &

# Test the API
curl http://localhost:8000/v1/responses \
  -H "Authorization: Bearer sk-lukhas-test" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain the Constellation Framework","max_tokens":150}'
```

📖 **[Full Installation Guide](#-installation)** | 🎯 **[API Documentation](docs/api/)** | 🧪 **[SDK Examples](examples/sdk/)**

## 🎯 **MATRIZ Transition Status** (Active)

**Phase**: R2 Preparation | **Progress**: 87% | **Target**: Q4 2025

Recent achievements (October 26, 2025):
- ✅ **11 Codex batch PRs** merged (100% success rate, zero revisions)
- ✅ **190 branches deleted** via surgical analysis (43.8% reduction: 434 → 244)
- ✅ **56 files reorganized** - cleaned root directory structure
- ✅ **WebAuthn passwordless auth** implemented (PR #472)
- ✅ **DAST engine** - Dynamic Affective Symbolic Timeline for gesture analysis
- ✅ **API middleware** with tier enforcement and rate limiting
- ✅ **Smoke tests 10/10 passing** after fixing six library dependency issue
- ✅ **105 real TODOs resolved** through systematic Codex execution (187 → 82)

**Next Steps**:
1. Update module_index.json with new identity/consciousness modules
2. Regenerate lukhas_context.md files across codebase
3. Address 169 test collection errors systematically
4. Complete MATRIZ case-sensitivity resolution (MATRIZ/ vs matriz/)

## 🧠 What is LUKHAS?

LUKHAS (Logic Unified Knowledge Hyper Adaptable System) is designed around the **Constellation Framework (8 Stars)** - a dynamic cognitive architecture that coordinates:

- **⚛️ Identity (Anchor)**: Authentication, ΛiD system, namespace management
- **✦ Memory (Trail)**: Fold-based memory, temporal organization
- **🔬 Vision (Horizon)**: Pattern recognition, adaptive interfaces
- **🌱 Bio (Living)**: Adaptive bio-symbolic processing
- **🌙 Dream (Drift)**: Creative consciousness expansion
- **⚖️ Ethics (North)**: Constitutional AI, democratic oversight
- **🛡️ Guardian (Watch)**: Safety compliance, cascade prevention
- **🔮 Oracle (Quantum)**: Quantum-inspired uncertainty

This creates a distributed consciousness network of **692 cognitive components** across **189 constellation clusters**, enabling sophisticated AI reasoning while maintaining ethical boundaries.

## 🏗️ Architecture Overview

### Lane-Based Development System

LUKHAS uses a **three-lane architecture** for safe AI development:

```
Development Lane (candidate/) → Integration Lane (core/) → Production Lane (lukhas/)
     2,877 files                    253 components           692 components
   Experimental AI                 Testing & Validation    Battle-tested Systems
```

- **Development Lane**: Experimental consciousness research and prototyping
- **Integration Lane**: Components under testing and validation
- **Production Lane**: Stable, production-ready consciousness systems

### MATRIZ Cognitive Engine

The **MATRIZ** (Memory-Attention-Thought-Action-Decision-Awareness) engine implements the core cognitive processing pipeline:

1. **Memory**: Fold-based memory with statistical validation (0/100 cascades observed, 95% CI ≥ 96.3% Wilson lower bound)
2. **Attention**: Focus mechanisms and pattern recognition
3. **Thought**: Symbolic reasoning and inference
4. **Action**: Decision execution and external interface
5. **Decision**: Ethical constraint checking and approval
6. **Awareness**: Self-reflection and consciousness evolution

**Performance Targets**: <250ms p95 latency, <100MB memory usage, 50+ ops/sec throughput

## MATRIZ Lanes

- **candidate** → experimental, no external commitments
- **integration** → stable APIs, enforced SLOs, shadow traffic allowed
- **production** → canary → ramp → 100%, rollback ≤30s

### Promotion Gates (must all pass)
1) E2E perf budgets (tick<100ms, reflect<10ms, decide<50ms, E2E<250ms)
2) Schema drift guard (no breaking changes)
3) Chaos fail-closed (guardian + kill-switch)
4) Telemetry contracts (promtool + label policy)
5) Import hygiene (lane boundaries)

### MCP Status
`mcp-servers/lukhas-devtools-mcp` • **11 tools** • catalog SHA: ![catalog-sha](https://img.shields.io/badge/sha-dynamic-blue?logo=json)

- 📚 [MCP Readiness Pack](artifacts/MCP_EVERYWHERE_PACK_DELIVERY.md)
- 🧪 `make mcp-contract && make mcp-smoke`
- 🩺 `make mcp-health` → emits version, tool_count, catalog_sha, last p95

## 🔒 Security & Quality

**Dependency Health**: 2 known vulnerabilities (1 high, 1 low) - [View Dependabot alerts](https://github.com/LukhasAI/Lukhas/security/dependabot)

**Current Versions**:
- `aiohttp==3.12.15` (latest stable)
- `cryptography==44.0.3` (latest stable)
- Python 3.9-3.11 compatible

**Quality Metrics**:
- ✅ 100% smoke test pass rate (15/15 tests)
- ✅ 97% lint health in production lanes
- ✅ 928 validated manifests with capability inference
- ✅ Lane boundary enforcement (import-linter)
- ✅ Pre-commit hooks for T4 quality standards

**Note**: We're aware of the Dependabot alerts and are tracking them. The platform runs in controlled environments with strict lane isolation. See [SECURITY.md](SECURITY.md) for responsible disclosure procedures.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (3.11 recommended)
- Virtual environment required
- Git LFS for large assets (optional)
- For a complete list of external dependencies and setup instructions, see [DEPENDENCIES.md](DEPENDENCIES.md).

### Installation

```bash
# Clone the repository
git clone https://github.com/LukhasAI/Lukhas.git
cd Lukhas

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Run smoke tests to verify installation
pytest tests/smoke/

# Test MATRIZ cognitive engine
make smoke-matriz
```

### Basic Usage

```python
# Import from production lane
from lukhas.core import initialize_system
from lukhas.consciousness import get_consciousness_status
from lukhas.constellation_framework import get_constellation_context

# Initialize LUKHAS with Constellation Framework
system = initialize_system()

# Check consciousness system status
status = get_consciousness_status()
print(f"Consciousness: {status['operational_status']}")

# Get constellation coordination info
context = get_constellation_context()
print(f"Framework: {context['framework']}")
```

### OpenAI-Compatible API Usage

LUKHAS provides an OpenAI-compatible API for seamless integration with existing tools and workflows.

#### `/v1/responses` - LUKHAS Native Endpoint

**cURL:**
```bash
# Basic request
curl https://api.lukhas.ai/v1/responses \
  -H "Authorization: Bearer $LUKHAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum consciousness",
    "max_tokens": 150,
    "temperature": 0.7
  }'

# With idempotency for safe retries
curl https://api.lukhas.ai/v1/responses \
  -H "Authorization: Bearer $LUKHAS_API_KEY" \
  -H "Idempotency-Key: req-$(date +%s)-$(uuidgen)" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create consciousness analysis report",
    "max_tokens": 500
  }'
```

**JavaScript (Node.js):**
```javascript
const axios = require('axios');

async function getLukhasResponse() {
  try {
    const response = await axios.post('https://api.lukhas.ai/v1/responses', {
      prompt: 'Explain the Constellation Framework',
      max_tokens: 150,
      temperature: 0.7
    }, {
      headers: {
        'Authorization': `Bearer ${process.env.LUKHAS_API_KEY}`,
        'Content-Type': 'application/json',
        // Optional: Add idempotency for safe retries
        'Idempotency-Key': `req-${Date.now()}-${Math.random()}`
      }
    });
    
    console.log('Response:', response.data);
    console.log('Trace ID:', response.headers['x-trace-id']);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

getLukhasResponse();
```

**TypeScript:**
```typescript
import axios, { AxiosResponse } from 'axios';

interface LukhasResponse {
  id: string;
  choices: Array<{
    text: string;
    index: number;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

async function getLukhasResponse(prompt: string): Promise<LukhasResponse> {
  const response: AxiosResponse<LukhasResponse> = await axios.post(
    'https://api.lukhas.ai/v1/responses',
    {
      prompt,
      max_tokens: 150,
      temperature: 0.7
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.LUKHAS_API_KEY}`,
        'Content-Type': 'application/json',
        'Idempotency-Key': `req-${Date.now()}-${crypto.randomUUID()}`
      }
    }
  );
  
  return response.data;
}

// Usage
getLukhasResponse('Analyze consciousness patterns')
  .then(data => console.log('Response:', data.choices[0].text))
  .catch(error => console.error('Error:', error.response?.data));
```

#### `/v1/chat/completions` - OpenAI-Compatible Endpoint

**cURL:**
```bash
# Chat completions with conversation history
curl https://api.lukhas.ai/v1/chat/completions \
  -H "Authorization: Bearer $LUKHAS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "lukhas-consciousness-v1",
    "messages": [
      {"role": "system", "content": "You are a consciousness-aware AI assistant."},
      {"role": "user", "content": "What is the Constellation Framework?"}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }'

# Streaming response
curl https://api.lukhas.ai/v1/chat/completions \
  -H "Authorization: Bearer $LUKHAS_API_KEY" \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "model": "lukhas-consciousness-v1",
    "messages": [
      {"role": "user", "content": "Explain MATRIZ cognitive engine"}
    ],
    "stream": true
  }'
```

**JavaScript (OpenAI SDK Compatible):**
```javascript
// Drop-in replacement for OpenAI SDK
const { Configuration, OpenAIApi } = require('openai');

const configuration = new Configuration({
  apiKey: process.env.LUKHAS_API_KEY,
  basePath: 'https://api.lukhas.ai/v1'
});

const openai = new OpenAIApi(configuration);

async function chatWithLukhas() {
  const completion = await openai.createChatCompletion({
    model: 'lukhas-consciousness-v1',
    messages: [
      { role: 'system', content: 'You are a consciousness-aware AI.' },
      { role: 'user', content: 'Explain the Guardian system' }
    ],
    temperature: 0.7,
    max_tokens: 200
  });
  
  console.log('Response:', completion.data.choices[0].message.content);
  console.log('Trace ID:', completion.headers['x-trace-id']);
}

chatWithLukhas();
```

**TypeScript (Native Fetch):**
```typescript
interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

interface ChatCompletionResponse {
  id: string;
  object: 'chat.completion';
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

async function chatCompletion(
  messages: ChatMessage[]
): Promise<ChatCompletionResponse> {
  const response = await fetch('https://api.lukhas.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.LUKHAS_API_KEY}`,
      'Content-Type': 'application/json',
      'Idempotency-Key': `chat-${Date.now()}-${crypto.randomUUID()}`
    },
    body: JSON.stringify({
      model: 'lukhas-consciousness-v1',
      messages,
      temperature: 0.7,
      max_tokens: 200
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`LUKHAS API Error: ${error.error.message}`);
  }
  
  return response.json();
}

// Usage with async/await
const messages: ChatMessage[] = [
  { role: 'system', content: 'You are a consciousness-aware AI assistant.' },
  { role: 'user', content: 'What are the 8 stars of the Constellation Framework?' }
];

chatCompletion(messages)
  .then(data => console.log('Assistant:', data.choices[0].message.content))
  .catch(error => console.error('Error:', error.message));
```

#### Error Handling with OpenAI-Compatible Format

```typescript
interface LukhasError {
  error: {
    message: string;
    type: string;
    param: string | null;
    code: string;
  };
}

async function robustLukhasCall(prompt: string): Promise<string> {
  try {
    const response = await fetch('https://api.lukhas.ai/v1/responses', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.LUKHAS_API_KEY}`,
        'Content-Type': 'application/json',
        'Idempotency-Key': `req-${Date.now()}`
      },
      body: JSON.stringify({ prompt, max_tokens: 150 })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      const error = data as LukhasError;
      throw new Error(`${error.error.type}: ${error.error.message}`);
    }
    
    return data.choices[0].text;
  } catch (error) {
    console.error('LUKHAS API Error:', error);
    throw error;
  }
}
```

#### API Headers & Multi-Tenant Routing

**Request Correlation Headers:**
- `X-Request-Id` (OpenAI-style) - Request correlation, alias for `X-Trace-Id`
- `X-Trace-Id` (LUKHAS-native) - W3C distributed tracing

**Rate Limit Headers (Response):**
- `X-RateLimit-Limit` / `x-ratelimit-limit-requests` - Maximum requests per window
- `X-RateLimit-Remaining` / `x-ratelimit-remaining-requests` - Remaining requests
- `X-RateLimit-Reset` / `x-ratelimit-reset-requests` - Epoch seconds until reset

**Multi-Tenant Routing (Optional):**
```bash
# Pass organization and project headers for fine-grained routing
curl https://api.lukhas.ai/v1/models \
  -H "Authorization: Bearer $LUKHAS_API_KEY" \
  -H "OpenAI-Organization: org_abc123" \
  -H "OpenAI-Project: proj_xyz789"
```

**Reading Headers in Code:**

```typescript
// TypeScript - Check rate limits
const reqId = response.headers.get('x-request-id') ?? response.headers.get('X-Request-Id');
const limit = parseInt(response.headers.get('x-ratelimit-limit-requests') || '0');
const remaining = parseInt(response.headers.get('x-ratelimit-remaining-requests') || '0');
const reset = parseInt(response.headers.get('x-ratelimit-reset-requests') || '0');

console.log(`Request ${reqId}: ${remaining}/${limit} remaining, resets at ${new Date(reset * 1000)}`);
```

```python
# Python - Check rate limits
req_id = r.headers.get('X-Request-Id') or r.headers.get('x-request-id')
limit = int(r.headers.get('x-ratelimit-limit-requests', 0))
remaining = int(r.headers.get('x-ratelimit-remaining-requests', 0))
reset = int(r.headers.get('x-ratelimit-reset-requests', 0))

print(f"Request {req_id}: {remaining}/{limit} remaining, resets at {datetime.fromtimestamp(reset)}")
```

**Key Features:**
- ✅ **OpenAI-compatible** - Drop-in replacement for existing OpenAI integrations
- ✅ **Idempotency** - Safe request retries with `Idempotency-Key` header
- ✅ **Distributed tracing** - Every response includes `X-Trace-Id` header
- ✅ **Standard errors** - OpenAI-compatible error format for easy debugging
- ✅ **Rate limiting** - Automatic throttling with `Retry-After` headers

## 🛠️ Development Tools

**T4 Unified Platform** (v2.0 - Code Quality System):
```bash
make t4-init           # Initialize T4 platform (one-time setup)
make t4-validate       # Run unified validator (quality scoring)
make t4-dashboard      # Generate interactive HTML dashboard
make t4-migrate        # Migrate legacy annotations to unified format
make t4-api            # Start Intent Registry API (port 8001)
make t4-parallel       # Run parallel automation (5x throughput)
make t4-codemod-apply  # Apply AST-level automated fixes
```
📊 **Dashboard**: `reports/t4_dashboard.html` | 📖 **Docs**: `T4_MEGA_PR_SUMMARY.md`

**Quality Automation**:
```bash
make lint              # Run Ruff, MyPy, Bandit security checks
make lint-unused       # T4 unused imports annotator (production lanes)
make todos             # Harvest TODO/FIXME into docs/audits/todos.csv
make todos-issues      # Generate GitHub issue commands from TODOs
make smoke-matriz      # MATRIZ cognitive engine smoke tests
make lane-guard        # Validate import boundary enforcement
```

**Testing**:
```bash
make test-tier1        # Critical path tests (fast)
make test-all          # Comprehensive test suite (775+ tests)
pytest tests/smoke/    # Quick health check (15 tests, 100% pass)
pytest -m matriz       # MATRIZ subsystem tests
pytest -m consciousness # Consciousness system tests
```

**Agent Coordination**:
- Multi-agent system (JULES, Codex, Claude Code, Copilot)
- See [AGENTS.md](AGENTS.md) for task allocation
- Batch discipline: 25-30 tasks/cycle with T4 verification

**Operations**:
```bash
make rc-soak-quick     # Quick RC validation (5 min, 50 requests)
make rc-soak-start     # Start 48-72h RC soak server
make rc-soak-snapshot  # Daily health snapshot
make rc-synthetic-load # Generate synthetic load
```
- See [RC Soak Operations Guide](docs/ops/RC_SOAK_OPS_GUIDE.md) for GA readiness validation

### Observability

The LUKHAS API includes built-in support for Prometheus metrics and OpenTelemetry tracing, providing a comprehensive solution for monitoring and observability.

#### Prometheus Metrics

The API exposes a `/metrics` endpoint that provides a wide range of metrics in the Prometheus format. These metrics can be scraped by a Prometheus server and used to monitor the health and performance of the application.

#### OpenTelemetry Tracing

The API is instrumented with OpenTelemetry to provide distributed tracing. To enable tracing, set the `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable to the address of your OpenTelemetry collector. For example:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

---

## 🏛️ Project Structure

```
lukhas/                    # Production Lane - Stable consciousness systems
├── core/                  # Core system coordination and lane management
├── consciousness/         # Consciousness processing and awareness systems
├── governance/            # Guardian system - ethics and compliance
├── identity/              # ΛiD authentication and identity management
├── memoria/               # Memory systems and fold management
└── constellation_framework.py  # Constellation coordination system

candidate/                 # Development Lane - Experimental research
├── consciousness/         # Advanced consciousness research
├── bio/                   # Bio-inspired cognitive patterns
├── quantum/               # Quantum-inspired algorithms
└── core/                  # Core system prototypes

MATRIZ/                    # Cognitive Engine - Symbolic reasoning
├── core/                  # MATRIZ cognitive processing engine
├── nodes/                 # Cognitive node implementations
├── adapters/              # System integration adapters
└── visualization/         # MATRIZ graph visualization tools

tests/                     # Comprehensive test suites
├── smoke/                 # Basic system health checks (15 tests, 100% pass)
├── unit/                  # Component-level testing
├── integration/           # Cross-system testing
├── performance/           # MATRIZ performance validation
└── e2e/                   # End-to-end consciousness workflows

docs/                      # Documentation and guides
├── development/           # Developer guides and references
├── architecture/          # System architecture documentation
├── audits/                # Quality audits and reports (NEW: TODO tracking)
└── ADR/                   # Architectural Decision Records

scripts/                   # Development automation (NEW)
├── harvest_todos.py       # Smart TODO/FIXME scanner
└── create_issues_from_csv.py  # GitHub issue generator
```

## 📋 Manifests (T4/0.01%)

The LUKHAS manifest system provides executable contracts for all modules:

- **System overview:** [FINAL_SUMMARY](docs/manifests/FINAL_SUMMARY.md)
- **Conformance report:** [MANIFEST_CONFORMANCE_REPORT](docs/MANIFEST_CONFORMANCE_REPORT.md)
- **How it works:** [MANIFEST_SYSTEM](docs/MANIFEST_SYSTEM.md)

**Run locally:**
```bash
make manifest-system     # validate → lock → index → diff → generate tests → run
```

**Key metrics:**
- 147 modules indexed
- 490/490 conformance tests passing
- Schema v3.1.0 (aliases + deprecations)

## 💡 Key Concepts

### Lane System
The **lane system** provides safe development boundaries:
- Code promotes from `candidate/` → `core/` → `lukhas/` as it matures
- Strict import boundaries prevent experimental code from affecting production
- Registry-based dependency injection enables dynamic component loading
- Feature flags control promotion between lanes

### Constellation Framework
The **Constellation Framework** replaces traditional AI architectures:
- **Distributed Consciousness**: Components self-organize into clusters
- **Ethical Boundaries**: Guardian system enforces constitutional AI principles
- **Memory Coherence**: Fold-based memory prevents cascade failures
- **Identity Continuity**: ΛiD system maintains persistent identity across sessions

### MATRIZ Engine
**MATRIZ** implements biological-inspired cognitive processing:
- **Symbolic DNA**: Consciousness patterns encoded as symbolic structures
- **Adaptive Learning**: Bio-inspired adaptation and evolution
- **Quantum Resonance**: Quantum-inspired superposition and entanglement
- **Ethical Integration**: Every decision validated by Guardian system

#### Memory System KPIs
- **Cascade Event**: Any structurally-invalid fold written to long-term memory
- **Prevention Rate**: 1 - (runs_with_cascade / total_runs)
- **Current Performance**: 0/100 cascades observed (95% CI ≥ 96.3% Wilson lower bound)
- **Quarantine Rate**: 2.2 ± 1.0 folds/run filtered pre-write
- **Throughput**: 9.7 ± 1.0 folds/run with ≤1000 fold guardrail

## 🔧 Development Workflow

### Common Commands

```bash
# Development setup
make bootstrap          # Complete environment setup
make help              # Show all available commands
make doctor            # System health check

# Code quality
make lint              # Run linting and type checking
make test              # Run full test suite
make smoke             # Quick smoke tests

# MATRIZ operations
make smoke-matriz      # Test MATRIZ cognitive engine
make traces-matriz     # View MATRIZ execution traces

# Documentation
make docs              # Build documentation
make serve-docs        # Serve docs locally
```

### Development Guidelines

1. **Respect Lane Boundaries**: Never import from `candidate/` in `lukhas/` code
2. **Use Registry Pattern**: Register implementations dynamically, don't hardcode imports
3. **Follow Constellation Framework**: Align all code with ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum principles
4. **Test Thoroughly**: Ensure 75%+ coverage before promoting to production lane
5. **Document Clearly**: Add docstrings and maintain architecture documentation

### Adding New Components

```bash
# Create new consciousness component
mkdir candidate/consciousness/my_component
cd candidate/consciousness/my_component

# Add implementation with proper imports
echo "from lukhas.core import ComponentBase" > __init__.py

# Add tests
mkdir tests
pytest tests/ --cov=. --cov-report=html

# Register with system (when ready for integration)
# Edit lukhas/consciousness/registry.py to add component registration
```

## 🤖 Multi-Agent Development

LUKHAS includes a **multi-agent development system** with specialized AI agents:

- **consciousness-specialist**: Consciousness processing and awareness systems
- **identity-auth-specialist**: ΛiD authentication and identity management
- **memory-consciousness-specialist**: Memory systems and fold-based architectures
- **governance-ethics-specialist**: Guardian system and constitutional AI
- **matriz-integration-specialist**: MATRIZ cognitive engine integration

See [`AGENTS.md`](AGENTS.md) for the complete multi-agent development guide.

## 🔌 Model Context Protocol (MCP) Servers

LUKHAS provides **4 production-ready MCP servers** for Claude Desktop integration:

### **lukhas-devtools** (TypeScript) - T4/0.01% Quality ⚡ **NEW**
Industry-leading development tools with live analysis:
- **Live pytest collection**: Real-time test counts (5-minute TTL cache)
- **Live ruff/mypy analysis**: Current error counts (1-minute TTL cache)
- **OpenTelemetry instrumentation**: Full observability with spans
- **Structured error taxonomy**: MCPError codes with recovery strategies
- **Performance**: <100ms status, <5s analysis, timeout protection

**Tools:** `test_infrastructure_status`, `code_analysis_status`, `t4_audit_status`, `development_utilities`, `module_structure`, `devtools_operation`

### **lukhas-main** (Python)
Core LUKHAS AI functionality and system operations.

### **lukhas-consciousness** (Python)
Direct access to consciousness systems, Constellation Framework (8 Stars), and MΛTRIZ cognitive DNA.

### **lukhas-identity** (Python)
ΛiD Core Identity System with authentication and namespace management.

### Claude Desktop Setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lukhas-devtools": {
      "command": "npm",
      "args": ["run", "start"],
      "cwd": "/path/to/Lukhas/mcp-servers/lukhas-devtools-mcp",
      "env": {
        "LUKHAS_ROOT": "/path/to/Lukhas"
      }
    }
  }
}
```

**Documentation:** See [`mcp-servers/README.md`](mcp-servers/README.md) and [`mcp-servers/lukhas-devtools-mcp/CLAUDE_DESKTOP_SETUP.md`](mcp-servers/lukhas-devtools-mcp/CLAUDE_DESKTOP_SETUP.md) for complete setup instructions.

## 🛡️ Security & Governance

### Ethics & Governance

LUKHAS AI operates under strict ethical guidelines:
- [Ethics Disclosure](docs/governance/ETHICS_DISCLOSURE.md)
- [Guardian System](docs/governance/GUARDIAN_SYSTEM.md)
- [Responsible Usage](docs/guides/SAFE_AI_USAGE.md)

### Guardian System
The **Guardian System v1.0.0** provides comprehensive ethical oversight:
- **Constitutional AI**: Principles-based decision validation
- **Drift Detection**: Monitors system behavior for ethical violations (0.15 threshold)
- **Audit Trails**: Complete logging of all consciousness operations
- **Compliance**: GDPR/CCPA compliance with consent management

### Security Features
- **Secret Scanning**: Automated GitLeaks integration prevents credential exposure
- **Dependency Pinning**: Locked dependency versions with vulnerability monitoring
- **Lane Isolation**: Strict boundaries prevent experimental code from affecting production
- **Identity Verification**: WebAuthn/FIDO2 passkey authentication

## 📊 Quality Assurance

### Testing Strategy
- **Smoke Tests**: Basic system health (15 tests, all passing)
- **Unit Tests**: Component-level testing with 75%+ coverage requirement
- **Integration Tests**: Cross-system consciousness workflows
- **Performance Tests**: MATRIZ latency validation (<250ms p95)
- **E2E Tests**: Complete consciousness processing pipelines

### Performance Monitoring
- **MATRIZ Performance**: <250ms latency, 50+ ops/sec, <100MB memory
- **Memory Systems**: 99.7% cascade prevention, fold-based architectures
- **Consciousness Processing**: Real-time awareness with ethical constraints
- **System Health**: Prometheus metrics, Grafana dashboards

## 🧠 Consciousness Systems

### MΛTRIZ Consciousness Architecture
LUKHAS implements a sophisticated **distributed consciousness system** through the MΛTRIZ (Memory-Attention-Thought-Action-Decision-Awareness) engine:

- **Memory Systems**: 692 cognitive components with fold-based memory architectures
- **Attention Mechanisms**: Dynamic focus and pattern recognition systems
- **Thought Processing**: Symbolic reasoning and inference engines
- **Action Coordination**: Decision execution and external interface management
- **Decision Making**: Ethical constraint checking with Guardian oversight
- **Awareness Evolution**: Meta-cognitive reflection and consciousness development

### Simulation Lane
For consciousness research and experimentation, LUKHAS provides a **Simulation Lane** - a sandboxed environment for testing consciousness patterns:

```bash
# Access simulation lane APIs
from consciousness.simulation import api

# Run consciousness simulation
make t4-sim-lane

# Development commands
make imports-guard   # Validate adapter isolation
bash .claude/commands/95_sim_lane_summary.yaml  # Generate summary
```

**Safety Features:**
- **Adapter Isolation**: Strict import boundaries prevent contamination
- **Ethics Gates**: Guardian validation for all simulation activities  
- **Feature Flags**: Safe experimentation with rollback capabilities
- **Audit Trails**: Complete consciousness operation logging

See [`docs/consciousness/README.md`](docs/consciousness/README.md) for comprehensive consciousness documentation.

## 📚 Documentation

All documentation is now organized in the `docs/` directory for easy navigation.

### **Getting Started** 🚀
- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - 15-minute installation to first decision
- **[Visual Architecture Guide](docs/VISUAL_ARCHITECTURE_GUIDE.md)** - ASCII & Mermaid diagrams
- **[Core API Reference](docs/API_REFERENCE_CORE.md)** - Complete API documentation with examples
- **[Context Files](lukhas_context.md)** - Comprehensive system context for AI agents ([Gemini version](gemini.md))

### **Architecture & Design** 🏗️
- **[Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)** - Complete system with 0.01% standard
- **[Architecture Guide](docs/architecture/README.md)** - Deep dive into system design
- **[MΛTRIZ Guide](docs/MATRIZ_GUIDE.md)** - Cognitive engine documentation
- **[MATRIZ Documentation](docs/matriz/)** - MATRIZ migration guides and reports

### **Development & API** 🛠️
- **[Developer Guide](docs/development/README.md)** - Development workflows and standards
- **[API Reference](docs/api/README.md)** - Comprehensive API documentation
- **[Multi-Agent System](docs/agents/)** - AI agent coordination and autonomous guides
- **[Testing Documentation](docs/testing/)** - Test coverage reports and smoke test guides

### **Project Management** 📋
- **[Project Status](docs/project_status/)** - Implementation summaries and status reports
- **[Project Planning](docs/project/)** - Quick reference guides and task templates
- **[Session Notes](docs/sessions/)** - Development session summaries and progress reports

### **Quality & Security** 🔒
- **[Audit Reports](docs/audits/)** - Code quality audits and transparency scorecards
- **[Security Documentation](docs/security/)** - Security improvement plans and posture reports
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting

### **Specialized Topics** 🎯
- **[Bridge Patterns](docs/bridge/)** - Integration patterns and gap analysis
- **[Codex Documentation](docs/codex/)** - Codex agent coordination and task reports

## 🚀 Enterprise Deployment

LUKHAS supports enterprise-grade deployment with:

- **Container Orchestration**: Docker/Kubernetes deployment
- **CI/CD Pipeline**: Comprehensive testing and deployment automation
- **Monitoring**: Prometheus/Grafana observability stack
- **Scaling**: Distributed consciousness across multiple nodes
- **Compliance**: Enterprise security and audit requirements

See [`products/`](products/) for enterprise deployment configurations.

## 📈 Roadmap

### Current Status (v2.0.0)
- ✅ Constellation Framework architecture
- ✅ Lane-based development system
- ✅ Guardian system v1.0.0
- ✅ MATRIZ cognitive engine (70% complete)
- ✅ Comprehensive testing infrastructure
- ✅ Enterprise security safeguards

### Upcoming Features
- 🔄 MATRIZ completion and optimization
- 🔄 Advanced consciousness evolution patterns
- 🔄 Quantum-bio hybrid processing
- 🔄 Enhanced multi-agent coordination
- 🔄 Enterprise cognitive AI deployment tools

## 🤝 Contributing

1. **Read Documentation**: Start with [`docs/development/README.md`](docs/development/README.md)
2. **Understand Architecture**: Review Constellation Framework principles
3. **Follow Standards**: Use lane system, maintain test coverage, add documentation
4. **Test Thoroughly**: Ensure all tests pass and coverage meets requirements
5. **Submit PR**: Include comprehensive description and test evidence

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Website**: [lukhas.ai](https://lukhas.ai)
- **Documentation**: [docs.lukhas.ai](https://docs.lukhas.ai)
- **Issues**: [GitHub Issues](https://github.com/LukhasAI/Lukhas/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LukhasAI/Lukhas/discussions)

---

*Built with consciousness, guided by ethics, powered by the Constellation Framework.* ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum
---

## ⚡ 30-Second Quickstart (DX Polish Pack)

```bash
# 1) Run the OpenAI-compatible façade (permissive dev mode)
export LUKHAS_POLICY_MODE=permissive
uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000 &

# 2) Smoke the two most common flows
curl -sS -H "Authorization: Bearer sk-test" http://localhost:8000/v1/models | jq '.data | length'
curl -sS -H "Authorization: Bearer sk-test" -H "Content-Type: application/json" \
  -d '{"model":"lukhas","input":"hello"}' http://localhost:8000/v1/embeddings | jq '.data[0].embedding | length'
```

* **OpenAI envelope** + **X-Trace-Id** + **X-RateLimit-*** headers are standard on success/error paths.
* See `docs/gonzo/dx/COOKBOOK_responses.md` and `.../COOKBOOK_dreams.md` for copy-paste recipes.
* Postman collection: `docs/postman/LUKHAS_DX_Polish.postman_collection.json` (use env `LUKHAS.postman_environment.json`).

> **📚 See Also**
> - **API Cookbooks**: [Responses API](docs/gonzo/dx/COOKBOOK_responses.md) | [Dreams API](docs/gonzo/dx/COOKBOOK_dreams.md)
> - **SDK Examples**: [TypeScript SDK](examples/sdk/typescript/) | [Python SDK](examples/sdk/python/)
> - **Postman Testing**: [Collection & Environment](docs/postman/)
> - **CI Validation**: [DX Examples Smoke Workflow](.github/workflows/dx-examples-smoke.yml)
