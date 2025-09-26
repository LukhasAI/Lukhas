# Memory Module

**LUKHAS Memory System** - Fold-based memory architecture with cascade prevention and recall optimization.

## 📊 Matrix Tracks Status

| Track | Status | Last Result | Updated |
|-------|---------|-------------|---------|
| 🔮 **Verification** | ✅ **PASSING** | 99.74% cascade prevention (≥99.70% target) | 2025-09-26 |
| 🔗 **Provenance** | ⚠️ **PENDING** | CAR root: `bafybeipending` | 2025-09-26 |
| 🛡️ **Attestation** | ⚪ **NOT_CONFIGURED** | Attestation track not configured | 2025-09-26 |

> **Status Legend:** ✅ Passing • ⚠️ Pending • ⚪ Not Configured • ❌ Failing
> **Auto-updated by CI** - Last refresh: 2025-09-26T12:13:37Z
---

## 🧠 Architecture

The LUKHAS memory system implements a **fold-based architecture** that prevents cascade failures while maintaining high recall performance:

### Core Components
- **Memory Folds**: Hierarchical memory compression (1000-fold limit)
- **Cascade Prevention**: 99.7% prevention rate with statistical validation
- **Recall Engine**: Sub-100ms semantic search with confidence scoring
- **Storage Tiers**: Hot/warm/cold storage with automatic tiering

### Safety Guarantees
- **0/100 cascades observed** in production (95% CI ≥ 96.3% Wilson lower bound)
- **Fold limit enforcement**: Hard limit at 1000 folds before consolidation
- **Drift detection**: Statistical monitoring with 0.15 threshold

## 🚦 Quality Gates

Current gate configuration from [`matrix_memoria.json`](matrix_memoria.json):

- **Runtime Performance**: ≤20s for 10k operations
- **Drift Score**: ≥0.010 (healthy symbolic processing)
- **Security**: 0 high-severity OSV vulnerabilities
- **Attestation**: RATS verification required
- **Cascade Prevention**: ≥99.7% success rate

## 🔬 Verification Track Details

**PRISM Model**: [`models/memory/cascade.pm`](../models/memory/cascade.pm)
- **Property**: `P>=0.997 [F "no_cascade"]` (99.7% cascade prevention)
- **Model Type**: Markov Decision Process (MDP) with prevention system
- **States**: 2048 reachable states, 4096 transitions
- **Last Verification**: 99.74% ✅ (exceeds 99.70% target by +0.04%)

**Demo**: Run `make demo-verification` to see PRISM model checking locally

## 🔗 Provenance Track Details

**CAR Generation**: Content-addressed archives for audit trails
- **Tool**: [`tools/generate_car.py`](../tools/generate_car.py)
- **Format**: IPLD CAR with Lamport time ordering
- **Current CID**: `bafybeipending` (awaiting first production run)

**Demo**: Run `make demo-provenance` to generate and verify CAR locally

## 🛡️ Attestation Track Details

**RATS Evidence**: Runtime attestation with TEE support
- **Policy**: [`rats/policy-v2.1.yaml`](../rats/policy-v2.1.yaml)
- **TEE Support**: AMD SEV-SNP, Intel TDX, Arm CCA
- **Evidence Format**: JWT with RS256 signatures
- **Status**: Ready for evidence collection

**Demo**: Run `make demo-attestation` to verify policy compliance locally

## 📈 Performance Targets

- **p95 Latency**: <100ms recall operations
- **Memory Usage**: <100MB working set
- **Throughput**: 50+ ops/sec sustained
- **Cascade Rate**: <0.3% (target: 99.7% prevention)

## 🧪 Development

### Quick Start
```bash
# Run memory tests
make test-memory

# Validate matrix contract
make validate-matrix MODULE=memory

# Generate telemetry fixtures
make telemetry-fixtures MODULE=memory

# Run all Matrix Tracks demos
make demo-verification demo-provenance demo-attestation
```

### Integration Tests
```bash
# Memory cascade prevention
python3 -m pytest tests/memory/test_cascade_prevention.py -v

# Fold system validation
python3 -m pytest tests/memory/test_fold_system.py -v

# Telemetry compliance
python3 -m pytest tests/test_telemetry_semconv.py -m telemetry -v
```

## 📚 Documentation

- **[Matrix Contract](matrix_memoria.json)**: Complete module specification
- **[Architecture Docs](../docs/memory/architecture.md)**: Detailed design notes
- **[PRISM Model](../models/memory/cascade.pm)**: Formal verification model
- **[Telemetry Fixtures](../telemetry/fixtures/)**: OpenTelemetry test data

## 🔄 Track Evolution

### Verification Track Maturity
- ✅ **Report-only**: PRISM results logged to CI
- ✅ **Soft gate**: Warnings on property violation
- ⏳ **Hard gate**: Block merges on verification failure (target: Q1 2025)

### Provenance Track Roadmap
- ⏳ **Local CAR**: Generate CAR files in CI artifacts
- ⏳ **Contract Integration**: Update CID in matrix contract
- ⏳ **IPFS Pinning**: Pin CARs for permanent archival

### Attestation Track Roadmap
- ⏳ **Mock Evidence**: Development-mode attestation collection
- ⏳ **Staging TEE**: Real TEE attestation in staging environment
- ⏳ **Production Enforcement**: Hard gate on RATS verification

---

*This module is part of the [LUKHAS AI Platform](../README.md) Constellation Framework, implementing the **✦ Trail Star (Memory)** cognitive component.*