---
status: wip
type: documentation
owner: unknown
module: root
redirect: false
moved_to: null
---

# MATRIX TRACKS: Evolutionary Verification Paths

Matrix Contracts v3+ are not a single upgrade. They are **parallel tracks of verifiability**, allowing each module to adopt defenses suited to its risk profile.
This avoids "big bang" migrations while compounding system resilience.

---

## 🌱 Foundation (v1–v2)

Every module gets:
- ✅ **JSON Schema validation** (Draft 2020-12)
- ✅ **Quality gates** (deterministic + CI enforced)
- ✅ **OSV scanning** with graceful fallback
- ✅ **Telemetry semconv compliance** (OpenTelemetry v1.37.0)

This is the **non-negotiable baseline**. All tracks build on this foundation.

---

## 🔮 Verification Track (v3a): Probabilistic Guarantees

**Focus:** Modules with cascading risk (memory, consciousness, orchestration)
**Maturity Path:** Report-only → Soft gate → Hard gate

### What You Get
- **PRISM model checking** for stochastic properties
- **Statistical confidence bounds** on safety invariants
- **Drift detection** with probabilistic thresholds

### Quick Start: Memory Cascade Prevention

```prism
// models/memory/cascade.pm
mdp

module memory
  folds : [0..1000] init 0;
  cascaded : bool init false;

  // Fold accumulation
  [] !cascaded & folds < 1000 -> 0.99:(folds'=folds+1) + 0.01:(cascaded'=true);
  [] !cascaded & folds = 1000 -> (cascaded'=true);
  [] cascaded -> true;
endmodule

// Property: cascade prevention ≥ 99.7%
label "no_cascade" = !cascaded;
```

### Gate Configuration

```json
// memory/matrix_memoria.json
"gates": [
  {
    "metric": "formal.probabilistic.cascade_prevention",
    "op": ">=",
    "value": 0.997,
    "mode": "report",  // Start with report-only
    "prism_property": "P>=0.997 [F \"no_cascade\"]"
  }
]
```

### CI Integration

```yaml
# .github/workflows/prism-verification.yml
- name: PRISM Model Check (Report Mode)
  run: |
    prism models/memory/cascade.pm \
      -pf 'P>=0.997 [F "no_cascade"]' \
      -exportresults artifacts/prism_memory.json

    # Parse result but don't fail CI yet
    python tools/matrix_gate.py --prism artifacts/prism_memory.json --report-only
```

### Adoption Checklist
- [ ] Create PRISM model for your safety property
- [ ] Add to gates with `"mode": "report"`
- [ ] Collect 30 days of data
- [ ] Graduate to `"mode": "soft"` (log warnings)
- [ ] After 90 days, move to `"mode": "hard"` (block merges)

---

## 🔗 Provenance Track (v3b): Cryptographic Truth

**Focus:** Modules needing forensic auditability (governance, API gateway, identity)
**Maturity Path:** Local CAR → CI artifacts → IPFS pinning

### What You Get
- **IPLD CAR files** for tamper-evident history
- **Merkle proofs** of gate evaluations
- **CRDT consensus** across module boundaries

### Quick Start: Generate CAR for Gate Results

```python
# tools/generate_car.py
import json
import ipld
from car import CAR

def generate_provenance_car(module: str, gate_results: dict) -> str:
    """Generate IPLD CAR for gate evaluation results."""

    # Create IPLD block with gate results
    block = {
        "module": module,
        "timestamp": datetime.utcnow().isoformat(),
        "gates": gate_results,
        "schema_version": "1.0.0"
    }

    # Generate CAR file
    car_path = f"artifacts/{module}_provenance.car"
    with CAR.create(car_path) as car:
        cid = car.add_block(ipld.encode(block))

    return cid

# Usage in matrix_gate.py
cid = generate_provenance_car("memory", gate_results)
print(f"Provenance CID: {cid}")
```

### Contract Update

```json
// memory/matrix_memoria.json
"causal_provenance": {
  "ipld_root_cid": "bafybeig6xv5nwphfmvcnektpnojts33jrhpxmifzfhwb56gzkb2wb2zwy",
  "car_uri": "ipfs://bafybeig6xv5nwphfmvcnektpnojts33jrhpxmifzfhwb56gzkb2wb2zwy",
  "lamport_time": 42,
  "vector_clock": {"memory": 15, "identity": 8, "consciousness": 23}
}
```

### Verification Script

```bash
#!/bin/bash
# Verify CAR integrity
ipld-car verify artifacts/memory_provenance.car

# Extract and verify specific block
ipld-car get bafybeig6xv5nwphfmvcnektpnojts33jrhpxmifzfhwb56gzkb2wb2zwy \
  --from artifacts/memory_provenance.car | jq .

# Pin to IPFS (optional)
ipfs add artifacts/memory_provenance.car
ipfs pin add bafybeig6xv5nwphfmvcnektpnojts33jrhpxmifzfhwb56gzkb2wb2zwy
```

### Adoption Checklist
- [ ] Install IPLD/CAR tooling (`npm install -g @ipld/car`)
- [ ] Generate CAR on gate evaluation
- [ ] Store CID in contract's `causal_provenance`
- [ ] Archive CARs with releases
- [ ] Optional: Pin to IPFS for permanence

---

## 🛡️ Attestation Track (v3c): Runtime Trust

**Focus:** Modules facing runtime adversaries (identity, API edge, adapters)
**Maturity Path:** Dev attestation → Staging TEE → Production enclave

### What You Get
- **RATS/EAT verification** (RFC 9334)
- **TEE measurements** (AMD SEV-SNP, Intel TDX, Arm CCA)
- **eBPF enforcement** for runtime policies

### Quick Start: RATS Evidence Collection

```python
# tools/collect_attestation.py
import jwt
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def collect_rats_evidence(module: str, measurements: dict) -> str:
    """Collect RATS evidence for module execution."""

    evidence = {
        "module": module,
        "timestamp": datetime.utcnow().isoformat(),
        "measurements": {
            "code_hash": hashlib.sha256(open(f"{module}/__init__.py", "rb").read()).hexdigest(),
            "config_hash": measurements.get("config_hash"),
            "runtime": measurements.get("runtime", "python3.11")
        },
        "tee": {
            "type": "amd-sev-snp",
            "report": measurements.get("sev_report"),
            "measurement": measurements.get("sev_measurement")
        }
    }

    # Sign evidence (simplified - use real key management)
    evidence_jwt = jwt.encode(evidence, "secret", algorithm="RS256")
    return evidence_jwt
```

### Verification Policy

```yaml
# rats/policy-v2.1.yaml
version: "2.1"
policies:
  - module: identity
    required_claims:
      - tee.type: "amd-sev-snp"
      - measurements.code_hash:
          operator: "equals"
          expected: "sha256:abc123..."
    optional_claims:
      - tee.tcb_version:
          operator: "gte"
          expected: "1.0.0"
```

### Runtime Integration

```python
# In module initialization
def verify_runtime_attestation():
    """Verify runtime attestation before module start."""

    evidence_jwt = collect_rats_evidence("identity", get_measurements())

    # Verify against policy
    verifier = RATSVerifier(policy_path="rats/policy-v2.1.yaml")
    result = verifier.verify(evidence_jwt)

    if not result.valid:
        raise SecurityError(f"Attestation failed: {result.reason}")

    # Update run report
    update_run_report({
        "attestation": {
            "rats_verified": 1,
            "evidence_jwt": evidence_jwt[:50] + "...",  # Store prefix only
            "verification_time": datetime.utcnow().isoformat()
        }
    })
```

### TEE Quick Reference

| Platform | Command | Output |
|----------|---------|--------|
| AWS Nitro | `nitro-cli describe-enclaves` | PCR measurements |
| Azure CVM | `az attestation show` | SEV-SNP report |
| GCP Confidential | `gcloud compute instances get-shielded-identity` | vTPM state |

### Adoption Checklist
- [ ] Define attestation policy YAML
- [ ] Integrate evidence collection in module init
- [ ] Test in dev with mock attestation
- [ ] Deploy to staging with real TEE
- [ ] Enable hard gates in production

---

## 🧭 Track Selection Matrix

| Module | Recommended Track(s) | Rationale |
|--------|---------------------|-----------|
| **memory** | Verification | Cascade prevention is probabilistic |
| **identity** | Attestation | WebAuthn keys need runtime protection |
| **consciousness** | Verification + Provenance | Drift safety + emergence auditability |
| **api_gateway** | Attestation + Provenance | Edge trust + request forensics |
| **governance** | All three | Maximum verifiability for ethics engine |
| **adapters** | Attestation | External service credentials at risk |

---

## 🔄 Track Synergy Patterns

### Verification + Provenance
```python
# Prove stochastic properties with tamper-evident history
result = prism_check("P>=0.99 [F goal]")
cid = generate_car({"prism_result": result, "property": "safety"})
```

### Provenance + Attestation
```python
# Runtime events with cryptographic audit trail
evidence = collect_attestation()
cid = generate_car({"evidence": evidence, "timestamp": now()})
```

### All Three Tracks
```python
# Military-grade verifiability
prism_result = verify_probabilistic_safety()
attestation = verify_runtime_integrity()
cid = generate_car({
    "prism": prism_result,
    "attestation": attestation,
    "gates": gate_results
})
```

---

## 🚫 Migration Antipatterns

### ❌ Big Bang Adoption
**Wrong:** "All modules must adopt all tracks by Q2"
**Right:** Let each module evolve at its own pace

### ❌ Flaky CI Gates
**Wrong:** Hard-fail on PRISM timeout
**Right:** Report-only → Soft gate → Hard gate progression

### ❌ Hidden Optionality
**Wrong:** Secret env var to bypass attestation
**Right:** Explicit `"mode": "report"` in contracts

### ❌ Tool Lock-in
**Wrong:** Require specific IPFS node
**Right:** CAR files work with any IPLD implementation

---

## 📈 Cultural Evolution Path

### Year 1: Foundation (Current)
- ✅ All modules on v2 baseline
- ✅ OSV scanning with fallback
- ✅ Telemetry smoke tests passing

### Year 2: Early Adopters
- Memory adopts **Verification** track
- Identity adopts **Attestation** track
- API Gateway experiments with **Provenance**

### Year 3: Cross-Track Integration
- Verification + Provenance for consciousness
- Attestation + Provenance for governance
- Track synergy patterns emerge

### Year 4: Full Mesh
- Every module has applicable tracks
- Cross-module verification via shared CARs
- Runtime attestation in production

---

## 🛠️ Implementation Tools

### PRISM
```bash
# Install
brew install prism-model-checker  # macOS
apt-get install prism             # Linux

# Verify
prism -version
```

### IPLD/CAR
```bash
# Install
npm install -g @ipld/car
cargo install ipld-cli

# Verify
ipld-car --version
```

### RATS/EAT
```python
# Install
pip install eat-python
pip install python-sev  # For AMD SEV-SNP

# Verify
python -c "import eat; print(eat.__version__)"
```

---

## 🎯 Success Metrics

### Track Adoption
- Number of modules per track
- Time from report → soft → hard gate
- Gate failure rate by track

### System Resilience
- Cascades prevented (Verification)
- Audit trails verified (Provenance)
- Runtime compromises blocked (Attestation)

### Cultural Health
- PR velocity maintained
- Developer NPS stable or increasing
- Security incidents decreasing

---

## 🔮 The Secret Sauce

**The 99% ship v3 as a single fragile migration.**
**The 0.01% ship evolutionary tracks that compose.**

Each track is a **superpower** your modules can acquire when ready:
- **Verification** = Mathematical confidence
- **Provenance** = Forensic truth
- **Attestation** = Runtime trust

Choose your verification adventure. The system gets stronger with every choice.

---

## 📚 References

### Standards
- [PRISM Model Checker](https://www.prismmodelchecker.org/)
- [IPLD Specification](https://ipld.io/)
- [RATS Architecture (RFC 9334)](https://datatracker.ietf.org/doc/rfc9334/)
- [AMD SEV-SNP ABI](https://www.amd.com/system/files/TechDocs/56860.pdf)

### Example Repositories
- [PRISM Examples](https://github.com/prismmodelchecker/prism-examples)
- [IPLD CAR Examples](https://github.com/ipld/js-car/tree/master/examples)
- [EAT Python](https://github.com/ietf-rats-wg/eat-python)

### Next Steps
1. Pick a track for your module
2. Start in report-only mode
3. Gather data for 30 days
4. Graduate to enforcement
5. Share learnings with the team

---

**Remember:** Tracks are not destinations, they're evolutionary paths. Start small, prove value, then compound.