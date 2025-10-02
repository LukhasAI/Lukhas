# LUKHAS AI Platform

**A consciousness-aware AI development platform with distributed cognitive architecture.**

LUKHAS AI is a sophisticated cognitive platform that implements consciousness-inspired patterns for advanced AI applications. Built with a modular lane-based architecture, the platform enables safe development and deployment of consciousness-aware AI systems through strict boundaries and comprehensive governance.

## 🧠 What is LUKHAS?

LUKHAS (Logic Unified Knowledge Hyper Adaptable System) is designed around the **Constellation Framework** - a dynamic cognitive architecture that coordinates:

- **⚛️ Anchor Star (Identity)**: Authentication, ΛiD system, secure access
- **✦ Trail Star (Memory)**: Experience patterns, fold-based memory systems
- **🔬 Horizon Star (Vision)**: Natural language interface, pattern recognition
- **🛡️ Watch Star (Guardian)**: Ethics oversight, security, compliance

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

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended

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
├── smoke/                 # Basic system health checks
├── unit/                  # Component-level testing
├── integration/           # Cross-system testing
├── performance/           # MATRIZ performance validation
└── e2e/                   # End-to-end consciousness workflows

docs/                      # Documentation and guides
├── development/           # Developer guides and references
├── architecture/          # System architecture documentation
└── ADR/                   # Architectural Decision Records
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
3. **Follow Constellation Framework**: Align all code with ⚛️✦🔬🛡️ principles
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
Direct access to consciousness systems, Trinity Framework, and MΛTRIZ cognitive DNA.

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

- **[Architecture Guide](docs/architecture/README.md)** - Complete system architecture
- **[Developer Guide](docs/development/README.md)** - Development workflows and standards
- **[MATRIZ Guide](docs/MATRIZ_GUIDE.md)** - Cognitive engine documentation
- **[API Reference](docs/api/README.md)** - Complete API documentation
- **[Multi-Agent System](AGENTS.md)** - AI agent coordination platform

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

*Built with consciousness, guided by ethics, powered by the Constellation Framework.* ⚛️✦🔬🛡️