# Matrix Tracks Examples

This directory contains **copy-pasteable, runnable demos** for each Matrix Tracks verification path. Teams can run these locally to understand concepts before integrating with production contracts.

## 🎯 Quick Start

```bash
# Run all demos in sequence
make demo-verification
make demo-provenance
make demo-attestation

# Or run individual track demos
cd examples/matrix_tracks/verification && ./run_prism.sh
cd examples/matrix_tracks/provenance && ./generate_car.sh && ./verify_car.sh
cd examples/matrix_tracks/attestation && ./verify_evidence.sh
```

---

## 🔮 Verification Track

**Goal**: Probabilistic guarantees on safety properties (e.g., cascade prevention ≥99.7%)

### Files
- `demo_memory_cascade.pm` - Complete PRISM model for memory cascade prevention
- `run_prism.sh` - One-liner to run PRISM verification
- `expected_output.txt` - Example of passing verification output

### Demo Commands
```bash
cd verification
./run_prism.sh
```

**Expected Result**: Property satisfied with ≥99.7% probability

### Integration Path
1. Copy `demo_memory_cascade.pm` to your module's `models/` directory
2. Add to matrix contract:
   ```json
   "formal": {
     "probabilistic": {
       "tool": "prism",
       "model": "models/memory/cascade.pm",
       "properties": ["P>=0.997 [F \"safe_operation\"]"]
     }
   }
   ```
3. Update CI to run PRISM verification before merge

---

## 🔗 Provenance Track

**Goal**: Tamper-evident audit trails using content-addressed storage

### Files
- `sample_run.json` - Realistic module run report with gates + verification results
- `generate_car.sh` - Create IPLD CAR from run provenance
- `verify_car.sh` - Verify CAR integrity and structure

### Demo Commands
```bash
cd provenance
./generate_car.sh
./verify_car.sh
```

**Expected Result**: CAR file created and verified with cryptographic integrity

### Integration Path
1. Generate CAR after each gate evaluation:
   ```bash
   python3 tools/generate_car.py --module memory --gates run_report.json
   ```
2. Add to matrix contract:
   ```json
   "causal_provenance": {
     "ipld_root_cid": "bafybei...",
     "car_uri": "ipfs://bafybei...",
     "lamport_time": 42
   }
   ```
3. Archive CARs with releases for forensic auditability

---

## 🛡️ Attestation Track

**Goal**: Runtime trust through TEE attestation and evidence verification

### Files
- `evidence_jwt.json` - Mock RATS/EAT evidence JWT with SEV-SNP report
- `verifier_policy.json` - Policy defining required/optional claims
- `tee_report.json` - Detailed AMD SEV-SNP attestation report
- `verify_evidence.sh` - Evidence verification against policy

### Demo Commands
```bash
cd attestation
./verify_evidence.sh
```

**Expected Result**: Evidence passes policy requirements, TEE report validated

### Integration Path
1. Collect real evidence:
   ```bash
   python3 tools/collect_attestation.py --module identity --output evidence.jwt
   ```
2. Add to matrix contract:
   ```json
   "attestation": {
     "rats": {
       "evidence_jwt": "pending",
       "verifier_policy": "rats/policy-v2.1.yaml"
     }
   }
   ```
3. Verify evidence before module initialization

---

## 🔄 Track Synergies

### Verification + Provenance
Prove safety properties **and** create tamper-evident history:
```bash
# Run PRISM verification
prism models/memory/cascade.pm -prop "P>=0.997 [F \"safe_operation\"]"

# Generate CAR with verification results
python3 tools/generate_car.py --module memory --prism prism_results.json
```

### Provenance + Attestation
Runtime trust **with** forensic audit trail:
```bash
# Collect attestation evidence
python3 tools/collect_attestation.py --module identity --output evidence.jwt

# Generate CAR including attestation
python3 tools/generate_car.py --module identity --attestation evidence.jwt
```

### All Three Tracks
Military-grade verifiability:
```bash
# Full pipeline: verify, attest, archive
prism models/memory/cascade.pm -prop "P>=0.997 [F \"safe_operation\"]" > prism.json
python3 tools/collect_attestation.py --module memory --output evidence.jwt
python3 tools/generate_car.py --module memory --prism prism.json --attestation evidence.jwt
```

---

## 🧪 Mock vs Production

These demos use **mock implementations** to work on any development machine:

| Component | Demo | Production |
|-----------|------|------------|
| PRISM | Mock output if not installed | Real model checker |
| IPLD CAR | JSON structure | Binary CAR format |
| TEE Reports | Mock measurements | Real AMD SEV-SNP/Intel TDX |
| JWT Signatures | Mock signature | Real cryptographic verification |

### Installing Real Tools

```bash
# PRISM model checker
brew install prism-model-checker  # macOS
apt-get install prism             # Linux

# IPLD/CAR tools
npm install -g @ipld/car
cargo install ipld-cli

# RATS/EAT libraries
pip install eat-python
pip install python-sev  # AMD SEV-SNP support
```

---

## 🚀 Next Steps

1. **Pick Your Track**: Choose verification path based on module risk profile
2. **Start with Demos**: Run examples to understand concepts
3. **Integrate Gradually**: Report-only → soft gates → hard gates
4. **Compose Tracks**: Combine multiple tracks for compound security

**Remember**: Tracks are evolutionary paths, not destinations. Start small, prove value, then compound.

---

## 📚 References

- [Matrix Tracks Documentation](../../docs/MATRIX_TRACKS.md) - Complete track specifications
- [PRISM Model Checker](https://www.prismmodelchecker.org/) - Probabilistic verification
- [IPLD Specification](https://ipld.io/) - Content-addressed data structures
- [RATS Architecture](https://datatracker.ietf.org/doc/rfc9334/) - Remote attestation procedures