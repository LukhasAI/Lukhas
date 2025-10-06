---
status: wip
type: documentation
---
# Matrix Contracts System

## Overview

Matrix Contracts are rich, verifiable module manifests that define interfaces, quality gates, and operational requirements for LUKHAS AI modules. Each contract is a JSON document validated against JSON Schema 2020-12 that provides:

- **Interface definitions** with stability guarantees
- **Quality gates** enforced in CI/CD
- **Telemetry specifications** aligned with OpenTelemetry semconv
- **Supply chain metadata** via CycloneDX SBOM
- **Attestation requirements** following RATS/EAT standards
- **Energy tracking** through CodeCarbon integration

## Standards Compliance

| Standard | Version | Purpose | Reference |
|----------|---------|---------|-----------|
| JSON Schema | **2020-12** | Contract validation | [json-schema.org](https://json-schema.org/draft/2020-12/schema) |
| CycloneDX | **1.5** | SBOM format | [ECMA-424](https://cyclonedx.org/) |
| OpenTelemetry | **1.37.0** | Telemetry semconv | [opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/) |
| OpenLineage | **1.0.0** | Data lineage | [openlineage.io](https://openlineage.io/) |
| RATS/EAT | **RFC 9334** | Attestation | [RFC 9334](https://datatracker.ietf.org/doc/rfc9334/) |
| SLSA | **v1.0** | Supply chain | [slsa.dev](https://slsa.dev/) |
| CodeCarbon | **latest** | Energy metrics | [codecarbon.io](https://codecarbon.io/) |

**Version Tracking**: Bold versions are currently pinned in contracts. OpenLineage events store only IDs/URIs in contracts; rich facets are handled at runtime following the [OpenLineage JSON Schema](https://openlineage.io/spec).

## Quick Start

### 1. Creating a New Module Contract

Create `<module>/matrix_<module>.json`:

```json
{
  "$schema": "../schemas/matrix.schema.json",
  "schema_version": "1.0.0",
  "module": "your.module.name",
  "owner": {
    "team": "YourTeam",
    "codeowners": ["@username"]
  },
  "interface": {
    "public_api": [
      {"fn": "process(input: str) -> str", "stability": "stable"}
    ],
    "contracts": [
      {"name": "invariant_name", "type": "invariant", "desc": "Description"}
    ]
  },
  "gates": [
    {"metric": "latency.p99_ms", "op": "<=", "value": 100}
  ]
}
```

### 2. Creating Run Reports

Generate `<module>/runs/<timestamp>.json` after each test/benchmark:

```json
{
  "run_id": "run-2025-09-26-001",
  "module": "your.module.name",
  "timestamp": "2025-09-26T00:00:00Z",
  "metrics": {
    "latency.p99_ms": 85,
    "security.osv_high": 0
  },
  "attestation": {
    "rats_verified": 1
  }
}
```

### 3. Validate Contracts

```bash
# Using Makefile
make validate-matrix

# Direct Python
python tools/matrix_gate.py --verbose

# CI/CD (automatic on PR)
# Triggered by .github/workflows/matrix-contract.yml
```

## Contract Structure

### Required Fields

- `$schema`: Reference to matrix.schema.json
- `schema_version`: SemVer of contract format
- `module`: Module identifier
- `owner`: Team and codeowners

### Key Sections

#### Interface Definition
```json
"interface": {
  "public_api": [
    {
      "fn": "function_signature",
      "stability": "stable|experimental|internal",
      "doc": "Description"
    }
  ],
  "contracts": [
    {
      "name": "contract_name",
      "type": "invariant|precondition|postcondition",
      "desc": "What this contract guarantees"
    }
  ]
}
```

#### Quality Gates
```json
"gates": [
  {
    "metric": "metric.path",
    "op": "<=|<|>=|>|==|!=",
    "value": 123,
    "desc": "Human-readable description"
  }
]
```

Common gate metrics:
- `latency.runtime_s_10k`: 10k operation latency
- `symbolic.DriftScore`: Symbolic drift detection
- `security.osv_high`: High-severity CVE count
- `attestation.rats_verified`: RATS attestation status
- `memory.cascade_prevention_rate`: Module-specific metrics

#### Telemetry (OpenTelemetry)
```json
"telemetry": {
  "opentelemetry_semconv_version": "1.37.0",
  "spans": [
    {
      "name": "module.operation",
      "attrs": ["code.function", "lukhas.module"]
    }
  ],
  "metrics": [
    {
      "name": "lukhas.module.metric",
      "unit": "s",
      "type": "histogram|gauge|counter"
    }
  ]
}
```

**Version Pinning**: The `opentelemetry_semconv_version` field tracks the [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) version (currently 1.37.0). Update this field when adopting newer semconv versions to maintain traceability.

#### Supply Chain
```json
"supply_chain": {
  "sbom_ref": "../sbom/module.cdx.json",
  "licenses": ["Apache-2.0"],
  "attestations": [
    {
      "type": "slsa.provenance",
      "uri": "oci://registry/path",
      "predicateType": "https://slsa.dev/provenance/v1"
    }
  ]
}
```

## Gate Enforcement

Gates are enforced by comparing contract requirements against the latest run report:

1. **CI/CD**: Automatic on every PR touching contracts
2. **Local**: `make validate-matrix` or `python tools/matrix_gate.py`
3. **Strict Mode**: `python tools/matrix_gate.py --strict` (fails on any gate violation)

### Gate Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `<=` | Less than or equal | `latency <= 100ms` |
| `<` | Less than | `errors < 5` |
| `>=` | Greater than or equal | `uptime >= 99.9%` |
| `>` | Greater than | `throughput > 1000` |
| `==` | Equal | `security.osv_high == 0` |
| `!=` | Not equal | `status != "failed"` |

## SBOM Integration

Each module should have a CycloneDX SBOM at `sbom/<module>.cdx.json`:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "components": [
    {
      "type": "library",
      "name": "dependency",
      "version": "1.0.0",
      "purl": "pkg:pypi/dependency@1.0.0"
    }
  ]
}
```

Validate with:
```bash
cyclonedx validate --input sbom/module.cdx.json
```

## Temporal & Consensus Fields

For distributed systems coordination:

```json
"causal_provenance": {
  "lamport_time": 42,
  "vector_clock": {"node1": 10, "node2": 15},
  "bft": {
    "algorithm": "hotstuff",
    "view": 3,
    "qc_hash": "0xabc123..."
  },
  "crdt": {
    "type": "or-set",
    "last_join_cid": "bafybeiabc..."
  }
}
```

## Energy Tracking

Enable CodeCarbon for sustainability metrics:

```json
"energy": {
  "tool": "codecarbon",
  "last_kwh_10k": 0.042,
  "last_emissions_kg": 0.0021,
  "location": "US-CA",
  "pue": 1.2
}
```

## Attestation

Support for runtime attestation following **IETF RATS (RFC 9334)** standards:

```json
"attestation": {
  "rats": {
    "evidence_jwt": "pending",
    "verifier_policy": "rats/policy-v2.1.json"
  },
  "tee": [{
    "type": "amd-sev-snp",
    "report_sha256": "sha256:pending",
    "vlek_chain": "pem://pending"
  }]
}
```

**Note**: The `evidence_jwt` field stores placeholder values until the RATS verifier is implemented. The verifier policy version tracks compliance with RFC 9334. TEE entries are minimal but schema-valid, following AMD SEV-SNP attestation format.

## Best Practices

1. **Start Simple**: Begin with basic fields, add advanced features incrementally
2. **Automate Run Reports**: Generate from test/benchmark suites
3. **Version Everything**: Use semantic versioning for contracts
4. **Gate Thoughtfully**: Set realistic thresholds based on baseline measurements
5. **Document Changes**: Update contract when interfaces change
6. **Monitor Trends**: Track gate metrics over time
7. **Energy Awareness**: Include energy metrics for sustainability

## Troubleshooting

### Schema Validation Errors

```bash
# Validate specific contract
jsonschema -i memory/matrix_memoria.json schemas/matrix.schema.json

# Debug with Python
python -c "
import json
from jsonschema import validate, Draft202012Validator
schema = json.load(open('schemas/matrix.schema.json'))
contract = json.load(open('memory/matrix_memoria.json'))
validator = Draft202012Validator(schema)
errors = list(validator.iter_errors(contract))
for e in errors:
    print(f'{e.path}: {e.message}')
"
```

### Gate Failures

1. Check latest run report exists: `ls -la <module>/runs/`
2. Verify metrics match gate expectations
3. Use verbose mode: `python tools/matrix_gate.py --verbose`

### Missing SBOM

1. Generate with your build tool or manually create
2. Validate format: `cyclonedx validate --input sbom/module.cdx.json`
3. Update `supply_chain.sbom_ref` in contract

## Future Enhancements (v2)

- **PRISM Integration**: Stochastic model checking
- **IPLD/CAR**: Content-addressed provenance
- **OSV Scanning**: Automated vulnerability detection
- **Full RATS Verifier**: Complete attestation verification
- **Quantum Readiness**: PQC algorithm tracking

## References

- [JSON Schema 2020-12 Spec](https://json-schema.org/draft/2020-12/schema)
- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OpenLineage Spec](https://openlineage.io/spec)
- [RATS Architecture (RFC 9334)](https://datatracker.ietf.org/doc/rfc9334/)
- [SLSA Framework](https://slsa.dev/)
- [CodeCarbon Docs](https://mlco2.github.io/codecarbon/)
- [PRISM Model Checker](https://www.prismmodelchecker.org/)

## Support

For questions or issues:
- Create an issue in the LUKHAS repository
- Contact the Core Team via codeowners
- Check CI logs for validation details