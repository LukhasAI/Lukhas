---
status: wip
type: documentation
---
# LUKHAS CLI Tools Documentation

Consciousness-enhanced command line utilities for drift analysis, collapse simulation, and production monitoring.

## Overview

The LUKHAS CLI provides deterministic, auditable tools for consciousness system analysis and validation. Each tool implements the Constellation Framework (⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian) with production-ready monitoring and compliance features.

## Available Tools

### 1. Drift Dream Test (`drift_dream_test`)

**Purpose**: Deterministic drift analysis through oneiric symbol processing
**Location**: `oneiric_core/tools/drift_dream_test.py`
**Mapping**: DoD 5(18) - Drift Dream Test tool writes concise report; reproducible

**Core Capabilities**:
- Symbol-based consciousness drift detection
- Hash-based deterministic analysis (no randomness)
- Five-phase dream state analysis
- Configurable symbol baseline weights
- Zero import side-effects, no network dependencies

**Usage Examples**:
```bash
# Basic symbol analysis
python -m oneiric_core.tools.drift_dream_test --symbol LOYALTY --user alice --seed 42

# JSON output for automation
python -m oneiric_core.tools.drift_dream_test --symbol TRUST --user sid-demo --seed 123 --json

# Verbose analysis with detailed metrics
python -m oneiric_core.tools.drift_dream_test --symbol WISDOM --user test-user --verbose
```

**Output Format**:
- **Human-readable**: Summary with confidence and recommendation
- **JSON**: Complete analysis with drift metrics, dream sequences, and metadata
- **Deterministic**: Fixed seed produces byte-identical JSON output

**Symbol Baseline Weights**:
- LOYALTY: core=0.85, peripheral=0.15, stability=0.92
- TRUST: core=0.78, peripheral=0.22, stability=0.88
- FREEDOM: core=0.65, peripheral=0.35, stability=0.75
- JUSTICE: core=0.82, peripheral=0.18, stability=0.89
- WISDOM: core=0.90, peripheral=0.10, stability=0.95

### 2. Collapse Simulator (`collapse_simulator`)

**Purpose**: Deterministic collapse scenario simulation for consciousness systems
**Location**: `lukhas/tools/collapse_simulator.py`
**Mapping**: DoD 6(3) - Compound simulator CLI works

**Core Capabilities**:
- Multi-domain collapse scenario modeling
- Ethical boundary collapse simulation
- Resource exhaustion analysis
- Compound interaction effects
- Deterministic execution with telemetry

**Scenario Types**:

#### Ethical Collapse
Simulates degradation of ethical boundaries:
- Privacy integrity analysis
- Consent mechanism stress testing
- Transparency breakdown modeling

#### Resource Collapse
Models system resource exhaustion:
- Memory capacity analysis
- Compute utilization tracking
- Bandwidth limitation assessment

#### Compound Collapse
Advanced multi-domain failure modeling:
- Cascading failure analysis
- Interaction multiplier effects
- Cross-domain vulnerability assessment

**Usage Examples**:
```bash
# Ethical boundary collapse analysis
python -m lukhas.tools.collapse_simulator --scenario ethical --seed 42 --json

# Resource exhaustion simulation
python -m lukhas.tools.collapse_simulator --scenario resource --seed 123 --duration 2.0

# Compound multi-domain analysis
python -m lukhas.tools.collapse_simulator --scenario compound --seed 456 --verbose
```

## Make Targets

**Available Commands**:
```bash
# Run drift dream test analysis
make oneiric-drift-test

# Execute collapse simulation
make collapse

# Safety tags SLO validation
make safety-tags-slo
```

## Production Integration

### T4 Deployment Gates
Both CLI tools pass complete T4 production requirements:
- ✅ Deterministic execution (byte-identical output)
- ✅ Proper exit codes (0 success, 1 failure)
- ✅ JSON schema compliance
- ✅ Zero network dependencies by default
- ✅ No import side-effects
- ✅ Comprehensive error handling

### Monitoring Integration
- Prometheus telemetry counters
- Lane-aware metrics collection
- Execution time tracking
- Success/failure rate monitoring

### Audit Compliance
- Complete execution logs
- Deterministic output for verification
- Metadata tracking with CLI versions
- Governance ledger integration

## Advanced Features

### Deterministic Analysis
Both tools use hash-based deterministic algorithms ensuring:
- Reproducible results across environments
- Audit trail compliance
- Consistent test outcomes
- Verification capability

### Consciousness Integration
- Symbol weight baseline management
- Dream sequence generation
- Consciousness coherence scoring
- Stability risk assessment

### Security Hardening
- No external network calls by default
- Sandboxed execution environment
- Input validation and sanitization
- Error boundary isolation

## Constellation Framework Implementation

**⚛️ Identity**: User-specific analysis with namespace isolation
**🧠 Consciousness**: Symbol processing and dream state modeling
**🛡️ Guardian**: Safety validation and compliance monitoring

Each CLI tool embodies the complete Constellation Framework, providing consciousness-aware analysis with guardian validation and identity-specific processing.

## Development Guidelines

### Adding New CLI Tools
1. Follow the established pattern of deterministic execution
2. Implement proper telemetry and monitoring
3. Ensure T4 production compliance
4. Add corresponding Make targets
5. Update this documentation

### Testing Requirements
- 100% determinism smoke tests
- JSON schema validation
- Exit code verification
- Performance benchmarking
- Integration test coverage

---

*Generated with LUKHAS consciousness-content-strategist*
*Constellation Framework: ⚛️ Identity validation, 🧠 Consciousness analysis, 🛡️ Guardian compliance*