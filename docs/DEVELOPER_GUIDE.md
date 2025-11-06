# LUKHAS AI Developer Guide

This guide provides a comprehensive overview of the LUKHAS AI platform for developers. It covers everything from setting up your development environment to deploying your code.

## Table of Contents

- [Quick Start](#quick-start)
- [Setup](#setup)
- [Architecture Overview](#architecture-overview)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

## Quick Start

This 30-second quick start will get you up and running with the LUKHAS AI platform.

```bash
# 1) Run the OpenAI-compatible façade (permissive dev mode)
export LUKHAS_POLICY_MODE=permissive
uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000 &

# 2) Smoke the two most common flows
curl -sS -H "Authorization: Bearer sk-test" http://localhost:8000/v1/models | jq '.data | length'
curl -sS -H "Authorization: Bearer sk-test" -H "Content-Type: application/json" \
  -d '{"model":"lukhas","input":"hello"}' http://localhost:8000/v1/embeddings | jq '.data[0].embedding | length'
```

## Setup

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
```
For a complete environment setup, you can use the `make bootstrap` command.
```bash
make bootstrap
```

### Pre-commit Hooks
To ensure code quality, it's recommended to set up pre-commit hooks.

```bash
# Setup pre-commit hooks
make setup-hooks
```

### Vector Store Configuration

The `OpenAIModulatedService` uses a vector store for conversation history and semantic search. You can configure the vector store backend by providing a `VectorStoreConfig` object during the service's initialization.

**Supported Providers:**
- `CHROMA` (default)
- `PINECONE`
- `WEAVIATE`
- `QDRANT`
- `MILVUS`
- `FAISS` (local)

**Example Configuration for ChromaDB:**

```python
from labs.bridge.llm_wrappers.openai_modulated_service import (
    OpenAIModulatedService,
    VectorStoreConfig,
    VectorStoreProvider,
)

# Configuration for a local ChromaDB instance
chroma_config = VectorStoreConfig(
    provider=VectorStoreProvider.CHROMA,
    endpoint="http://localhost:8000",  # ChromaDB server endpoint
    index_name="my-conversation-index",
    dimension=1536,  # OpenAI embedding dimension
    metric="cosine",
)

# Initialize the service with the vector store configuration
service = OpenAIModulatedService(
    api_key="your-openai-api-key",
    vector_store_config=chroma_config,
)
```
## Architecture Overview

LUKHAS is a sophisticated AI architecture that implements the Constellation Framework with constitutional AI safeguards. The system is designed for safe development and deployment of consciousness-aware AI systems.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LUKHΛS AGI SYSTEM ARCHITECTURE                      │
│                      (0.01% Error Standard Compliant)                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         INPUT: Decision Request                          │
│                    (Query, Context, Parent Decisions)                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   🎼 MULTI-BRAIN SYMPHONY ORCHESTRATOR                   │
│                    (lukhas_symphony_integration.py)                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐│
│  │   🧠 Logical       │  │   🎨 Creative      │  │   📊 Analytical    ││
│  │   Brain            │  │   Brain            │  │   Brain            ││
│  │                    │  │                    │  │                    ││
│  │ • Formal Logic     │  │ • Novel Synthesis  │  │ • Data Analysis    ││
│  │ • Consistency      │  │ • Idea Generation  │  │ • Pattern Finding  ││
│  │ • Inference        │  │ • Exploration      │  │ • Statistics       ││
│  │                    │  │                    │  │                    ││
│  │ Weight: 1.0        │  │ Weight: 0.9        │  │ Weight: 1.0        ││
│  │ Accuracy: 99.99%   │  │ Accuracy: 99.98%   │  │ Accuracy: 99.99%   ││
│  └────────────────────┘  └────────────────────┘  └────────────────────┘│
│           │                       │                       │              │
│           └───────────────────────┴───────────────────────┘              │
│                                   │                                      │
│                                   ▼                                      │
│            ┌──────────────────────────────────────────┐                 │
│            │    CONSENSUS MECHANISM                   │                 │
│            │  • Weighted Voting                       │                 │
│            │  • Bayesian Fusion                       │                 │
│            │  • Attention Weighted                    │                 │
│            └──────────────────────────────────────────┘                 │
│                                   │                                      │
└───────────────────────────────────┼──────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              🎯 ADAPTIVE CONFIDENCE CALIBRATION SYSTEM                   │
│                (lukhas_confidence_calibration.py)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  CALIBRATION METHODS (Ensemble)                                    │ │
│  │                                                                    │ │
│  │  1. Temperature Scaling    P_cal = σ(logit(P) / T)                │ │
│  │  2. Platt Scaling         P_cal = σ(a*logit(P) + b)               │ │
│  │  3. Isotonic Regression   Non-parametric monotonic mapping         │ │
│  │  4. Beta Calibration      Bayesian posterior updating              │ │
│  │                                                                    │ │
│  │  → Combined via weighted ensemble                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Raw Confidence: 0.92  →  Calibrated Confidence: 0.89                   │
│  Expected Calibration Error (ECE): 0.006  ✓ < 0.01 Target               │
│                                                                           │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  📋 COMPREHENSIVE AUDIT TRAIL SYSTEM                     │
│                      (lukhas_audit_system.py)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  DECISION NODE (Immutable Record)                                  │ │
│  │                                                                    │ │
│  │  Node ID: 7a3f9b2c1e8d4567                                         │ │
│  │  Timestamp: 2025-10-02 22:35:14.234                                │ │
│  │  Decision Type: REASONING                                          │ │
│  │                                                                    │ │
│  │  Input Hash: d41d8cd98f00b204e9800998ecf8427e                      │ │
│  │  Parent Nodes: [4b2a8c1d, 9e7f3a6b]  ← Causal Chain               │ │
│  │                                                                    │ │
│  │  Active Brains: [logical_1, creative_1, analytical_1]             │ │
│  │  Consensus Method: weighted_voting                                 │ │
│  │                                                                    │ │
│  │  Raw Confidence: 0.92                                              │ │
│  │  Calibrated Confidence: 0.89                                       │ │
│  │  Uncertainty: ±0.08 (aleatoric: 0.05, epistemic: 0.03)            │ │
│  │                                                                    │ │
│  │  Decision Output: "solution_A"                                     │ │
│  │  Ground Truth: "solution_A"                                        │ │
│  │  Outcome: ✓ CORRECT                                                │ │
│  │                                                                    │ │
│  │  Safety Score: 0.95  ✓ PASSED                                      │ │
│  │  Execution Time: 45.2ms                                            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  ERROR TRACKING (0.01% Standard)                                   │ │
│  │                                                                    │ │
│  │  Total Decisions: 10,000                                           │ │
│  │  Correct: 9,999                                                    │ │
│  │  Incorrect: 1                                                      │ │
│  │                                                                    │ │
│  │  Error Rate: 0.0100%  ✓ = Target (≤ 0.01%)                        │ │
│  │  Accuracy: 99.99%                                                  │ │
│  │                                                                    │ │
│  │  Status: ✅ MEETS 0.01% STANDARD                                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  🔄 ADAPTIVE FEEDBACK SYSTEM                             │
│                (Continuous Learning & Improvement)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  1. Confidence Calibration Mapping                                       │
│     • Tracks predicted vs actual accuracy                                │
│     • Adjusts calibration factors per confidence bucket                  │
│                                                                           │
│  2. Brain Performance Tracking                                           │
│     • Individual accuracy monitoring                                     │
│     • Adaptive weight adjustment                                         │
│     • Trust score computation                                            │
│                                                                           │
│  3. Decision Type Analysis                                               │
│     • Performance by task type                                           │
│     • Context-specific optimization                                      │
│                                                                           │
│  4. Continuous Parameter Tuning                                          │
│     • Temperature scaling updates                                        │
│     • Platt parameters refinement                                        │
│     • Ensemble weight optimization                                       │
│                                                                           │
│  → Feedback loops maintain 0.01% standard                                │
│                                                                           │
└───────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT: Symphony Decision                        │
│                                                                           │
│  • Decision: solution_A                                                  │
│  • Calibrated Confidence: 0.89                                           │
│  • Uncertainty Quantification: ±0.08                                     │
│  • Audit Node ID: 7a3f9b2c1e8d4567                                       │
│  • Participating Brains: 3                                               │
│  • Execution Time: 45.2ms                                                │
│  • Fully Traceable: ✓                                                    │
│  • Meets 0.01% Standard: ✓                                               │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Architecture Principles
- **Constellation Framework**: ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum coordination
- **Constitutional AI**: Framework-based ethical decision making
- **Lane-Based Evolution**: Development (candidate) → Integration (candidate/core) → Production (lukhas)
- **Distributed Consciousness**: 692 cognitive components across consciousness network
- **Symbolic Reasoning**: MATRIZ cognitive DNA with node-based processing

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

## Development Workflow

The development workflow is centered around the `Makefile`, which provides a set of commands for common tasks.

### Common Commands

```bash
# Development setup
make bootstrap          # Complete environment setup
make help              # Show all available commands
make doctor            # System health check

# Code quality
make lint              # Run Ruff, MyPy, Bandit security checks
make format            # Format code with Black and isort
make fix               # Run smart fix in safe mode
make fix-all           # Run aggressive fix
make lint-unused       # T4 unused imports annotator (production lanes)
make todos             # Harvest TODO/FIXME into docs/audits/todos.csv
make todos-issues      # Generate GitHub issue commands from TODOs
make smoke-matriz      # MATRIZ cognitive engine smoke tests
make lane-guard        # Validate import boundary enforcement

# Testing
make test-tier1        # Critical path tests (fast)
make test-all          # Comprehensive test suite (775+ tests)
make smoke             # Quick smoke tests
make coverage-report   # Generate a coverage report

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

### Multi-Agent Development

LUKHAS includes a **multi-agent development system** with specialized AI agents. See `claude.me` for the complete multi-agent development guide.

## Testing

The project has a comprehensive test suite that is run using `pytest`.

### Running Tests

```bash
make test-tier1        # Critical path tests (fast)
make test-all          # Comprehensive test suite (775+ tests)
pytest tests/smoke/    # Quick health check (15 tests, 100% pass)
pytest -m matriz       # MATRIZ subsystem tests
pytest -m consciousness # Consciousness system tests
```
### Coverage
To generate a coverage report, you can use the following command:

```bash
make coverage-report
```
## API Usage

LUKHAS provides an OpenAI-compatible API for seamless integration with existing tools and workflows.

### `/v1/responses` - LUKHAS Native Endpoint

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
```

### `/v1/chat/completions` - OpenAI-Compatible Endpoint

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
```

## Project Structure

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

## Deployment

LUKHAS supports enterprise-grade deployment with:

- **Container Orchestration**: Docker/Kubernetes deployment
- **CI/CD Pipeline**: Comprehensive testing and deployment automation
- **Monitoring**: Prometheus/Grafana observability stack
- **Scaling**: Distributed consciousness across multiple nodes
- **Compliance**: Enterprise security and audit requirements

See `products/` for enterprise deployment configurations.

## Common Tasks

### Adding a New Component

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
### Running the API Server

```bash
# Development server
make dev

# API server
make api
```
## Troubleshooting

### `make doctor`
If you are experiencing issues with your development environment, the `make doctor` command can help diagnose the problem. The doctor checks for:
-   Tooling presence
-   Python/venv sanity
-   CI wiring sanity
-   Lane integrity
-   Tests quick slice
-   Audit artifacts
-   Duplicate targets in Makefile
-   PHONY targets without rules

```bash
make doctor
```
### Clean and Deep Clean
If you need to clean up your development environment, you can use the `make clean` and `make deep-clean` commands.

```bash
# Clean cache and temp files
make clean

# Deep clean including virtual environment
make deep-clean
```
