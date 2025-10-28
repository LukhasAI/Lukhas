# MATRIZ PQC Checklist (Dilithium2 / Kyber-768)

## Goal
Migrate registry checkpoint signing from HMAC → PQC signatures (Dilithium2) and ensure PQC KEM (Kyber-768) for envelope keys; implement CI sign/verify and key rotation.

## Steps (practical)

### 1. Prototype & CI ✅ **COMPLETE**
- Add `pqc-sign-verify` CI job (present).
- Ensure `python-oqs` or binding for liboqs available in CI image.
- **Status**: CI now runs with liboqs via Docker container (Issue #492 resolved)
- No fallback markers - CI uses real Dilithium2 or fails

### 2. Key generation (offline / secure host)
Generate long-term Dilithium2 keypair on HSM/KMS if supported:
```bash
oqs-cli genkey --alg Dilithium2 --out private.pem public.pem
```
- Store private key in hardware or KMS (recommend YubiHSM2 / AWS CloudHSM).
- Public key published in trust anchor store (signed by org root).

### 3. Checkpoint signing
- Registry `save_checkpoint()` creates a JSON payload and signs payload with Dilithium2 private key; store signature in `checkpoint.sig`.
- Publish `checkpoint.json` + `checkpoint.sig` + `meta.json` including `signer_id` and `timestamp`.

### 4. Verification
- On load, registry verifies signature against known public key(s). If verification fails, refuse to load checkpoint and alert operations.

### 5. Key rotation
- Create new keypair; sign new public key with current private (or via PKI).
- Add new public key to trust anchors BEFORE switching.
- Transition: produce dual-signed checkpoints for N periods, then retire old key.

### 6. Emergency revocation
- Revoke key in trust anchor store; nodes check revocation list every checkpoint window.
- For critical compromise, revert to HMAC-only safe mode and halt promotions until keys rotated.

### 7. Operational considerations
- Ensure timestamp freshness: require `timestamp` within configurable skew (e.g., ±5 min for planetary; ±1 hour for DTN deltas).
- For DTN/extra-planetary: use monotonic version numbers + Merkle tree + signature on tree root rather than re-signing entire payload frequently.

## Tests
- CI: sign + verify with Dilithium2 (or fallback marker if PQC libs not present).
- Integration: verify registry refuses corrupted signature.
- Load test: signing latency measured; must remain within checkpoint SLO (e.g., < 200ms for server).

## Risks & mitigations
- **Risk:** PQC libs absent on CI/runners → **RESOLVED** via Docker container with liboqs (Issue #492)
- **Risk:** private key compromise → require HSM + rotation + immediate revocation policy.

## PQC Library Setup (Local Development)

### Option 1: Install liboqs + Python bindings
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y cmake ninja-build
git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja .. && ninja && sudo ninja install

# Install Python bindings
pip install python-oqs
```

### Option 2: Use pqcrypto (pure Python, slower)
```bash
pip install pqcrypto
```

### Option 3: Docker (recommended for CI)
```bash
docker run -it openquantumsafe/liboqs-python:latest
```

## Verification Commands

### Test PQC library availability
```bash
python -c "import oqs; print('Available sig algs:', oqs.sig.algorithms())"
```

### Test Dilithium2 sign/verify
```bash
python - <<'PY'
import oqs
alg = 'Dilithium2'
with oqs.Signature(alg) as signer:
    pk = signer.generate_keypair()
    msg = b"test checkpoint"
    sig = signer.sign(msg)

with oqs.Signature(alg) as verifier:
    valid = verifier.verify(msg, sig, pk)
    print(f"Signature valid: {valid}")
PY
```

### Test registry checkpoint signing (after migration)
```bash
# Start registry
uvicorn services.registry.main:app --port 8080 &

# Register a node (creates checkpoint)
curl -X POST http://localhost:8080/api/v1/registry/register \
  -H "Content-Type: application/json" \
  -d @docs/schemas/examples/memory_adapter.json

# Verify checkpoint.sig exists and is valid
python - <<'PY'
import json, oqs
from pathlib import Path

checkpoint = json.loads(Path('services/registry/registry_store.json').read_text())
sig = Path('services/registry/checkpoint.sig').read_text()
# ... verify logic here
PY
```

## Migration Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase 1: Prototype** | 1 week | CI job, local dev setup, test vectors |
| **Phase 2: Key Generation** | 3 days | HSM setup, keygen, trust anchor |
| **Phase 3: Integration** | 1 week | Modify save_checkpoint(), verification logic |
| **Phase 4: Testing** | 3 days | Integration tests, load tests, security audit |
| **Phase 5: Staging Rollout** | 1 week | Deploy to staging, dual-sign period |
| **Phase 6: Production** | 1 week | Production rollout, monitoring |

**Total Estimate:** 5-6 weeks (conservative)

## Security Audit Checklist

- [ ] Private key never touches disk in plaintext
- [ ] HSM/KMS integration tested with failover
- [ ] Key rotation procedure documented and tested
- [ ] Emergency revocation tested in staging
- [ ] Signature verification failure triggers alerts
- [ ] Timestamp freshness enforced (±5 min tolerance)
- [ ] Dual-signing period logs analyzed for anomalies
- [ ] Old key retirement verified (no nodes use old sigs)
- [ ] PQC performance overhead measured (<10% target)
- [ ] CI fails loudly when PQC libs unavailable

## Related Documentation

- [MATRIZ-007 Issue](https://github.com/LukhasAI/Lukhas/issues/490)
- [TG-002 PR: Hybrid Registry Prototype](https://github.com/LukhasAI/Lukhas/pull/488)
- [NodeSpec v1 Schema](../schemas/nodespec_schema.json)
- [OPA Policy Stub](../governance/policies/sensitive_signal_guard.rego)
