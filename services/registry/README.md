# Registry Service

This directory contains the LUKHAS Hybrid Registry with **Post-Quantum Cryptography (PQC)** signed checkpoints.

## 🔐 Security: PQC Checkpoint Signing (MATRIZ-007)

The registry now uses **Dilithium2** (NIST PQC standard) for quantum-resistant checkpoint signatures, with automatic HMAC fallback in development environments.

### Features
- **Quantum-Resistant**: Dilithium2 signatures when liboqs available
- **Automatic Fallback**: HMAC-SHA256 in environments without PQC libraries
- **Signature Verification**: All checkpoints verified on load
- **Tampering Detection**: Corrupted signatures automatically rejected
- **Performance**: Meets SLO targets (<200ms sign p95, <10ms verify p95)

### Architecture
```
services/registry/
├── main.py                      # FastAPI app with PQC-signed checkpoints
├── pqc_signer.py               # Dilithium2/HMAC hybrid signer
├── registry_store.json         # Checkpoint data
├── checkpoint.sig              # Hex-encoded signature
└── .pqc_keys/                  # PQC keypair (auto-generated)
    ├── dilithium2_private.key
    └── dilithium2_public.key
```

## How to test PQC locally

Post-quantum signature testing uses liboqs (Dilithium2) and python-oqs bindings.

### Option 1: Install from distro packages (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y liboqs-dev
pip install python-oqs
```

### Option 2: Build from source

```bash
# Install dependencies
sudo apt-get install -y cmake ninja-build libssl-dev

# Build liboqs
git clone --depth=1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs && mkdir build && cd build
cmake -GNinja .. && ninja && sudo ninja install
sudo ldconfig

# Install Python bindings
pip install liboqs-python
```

### Option 3: Use Docker (recommended for CI)

```bash
docker build -f .github/docker/pqc-runner.Dockerfile -t lukhas-pqc-runner .
docker run -it lukhas-pqc-runner python3 -c "import oqs; print(oqs.sig.get_enabled_algorithms())"
```

### Verify PQC installation

```bash
python -c "import oqs; print('Available algorithms:', oqs.sig.get_enabled_algorithms())"
```

## Running tests

### All registry tests (24 tests)

```bash
pytest services/registry/tests -v
```

### PQC signature tests only (10 tests)

```bash
pytest services/registry/tests/test_checkpoint_signature.py -v
```

### Single integration test

```bash
pytest services/registry/tests/test_noop_guard_integration.py -v
```

### HTTP negative tests (optional)

To exercise negative tests against a live Registry API:

```bash
export REGISTRY_BASE_URL=http://localhost:8080
pytest services/registry/tests/test_registry_negative.py -v
```

Without `REGISTRY_BASE_URL`, HTTP-specific checks are skipped.

## CI/CD

The PQC check workflow is defined at `.github/workflows/pqc-sign-verify.yml`:
- **PQC Available**: Runs real Dilithium2 sign/verify with performance benchmarks
- **PQC Unavailable**: Falls back to HMAC and creates `pqc_fallback_marker.txt`
- **Performance Validation**: Enforces latency thresholds (sign <50ms, verify <10ms)

## Quickstart (local development)

### 1. Install dependencies

```bash
# Create virtual environment (optional)
python3 -m venv .venv && source .venv/bin/activate

# Install registry dependencies
pip install -r services/registry/requirements.txt

# Install PQC libraries (optional, will fallback to HMAC if unavailable)
pip install liboqs-python
```

### 2. Start the registry service

```bash
uvicorn services.registry.main:app --reload --port 8080
```

### 3. Test endpoints

```bash
# Health check
curl -s http://127.0.0.1:8080/health | jq

# Check signature scheme (Dilithium2 or HMAC fallback)
curl -s http://127.0.0.1:8080/api/v1/registry/signature_info | jq

# Register a node (creates signed checkpoint)
curl -X POST http://127.0.0.1:8080/api/v1/registry/register \
  -H "Content-Type: application/json" \
  -d @docs/schemas/examples/memory_adapter.json | jq

# Query nodes
curl -s "http://127.0.0.1:8080/api/v1/registry/query?signal=memory_stored" | jq
```

### 4. Verify checkpoint signature

```bash
# Checkpoint and signature files are created in services/registry/
ls -lh services/registry/registry_store.json services/registry/checkpoint.sig

# View signature info
cat services/registry/checkpoint.sig
```

## API Endpoints

- `POST /api/v1/registry/validate` - Validate NodeSpec against schema
- `POST /api/v1/registry/register` - Register node (requires `provenance_manifest.glymph_enabled: true`)
- `GET /api/v1/registry/query` - Query by signal or capability
- `DELETE /api/v1/registry/{registry_id}` - Deregister node
- `GET /health` - Health check
- `GET /api/v1/registry/signature_info` - Get current signature scheme info (NEW)

**Notes:**
- Endpoints accept NodeSpec JSON directly (top-level object, no wrapper)
- Registration enforces GLYMPH provenance flag (returns 403 if missing)
- All checkpoint operations are automatically signed and verified

## Security Considerations

### Key Management

**Development:**
- Keys auto-generated on first use in `.pqc_keys/`
- Private key permissions set to 0600 automatically

**Production (see `docs/security/MATRIZ_PQC_CHECKLIST.md`):**
- Store private keys in HSM/KMS (YubiHSM2 or AWS CloudHSM recommended)
- Distribute public keys via trust anchor store
- Implement key rotation with dual-signing transition period

### Signature Verification

- All checkpoints verified on load
- Tampered signatures rejected automatically
- Failed verification logged for monitoring
- System starts fresh if verification fails

### Performance Targets

| Operation | HMAC | Dilithium2 | Status |
|-----------|------|------------|--------|
| Sign (p95) | <5ms | <50ms | ✅ Met |
| Verify (p95) | <2ms | <10ms | ✅ Met |
| Checkpoint latency | <10ms | <200ms | ✅ Met |

### Emergency Procedures

1. **Signature Verification Failure**: System logs warning and starts fresh
2. **Key Compromise**: Implement key rotation procedure from PQC checklist
3. **PQC Library Unavailable**: Automatic fallback to HMAC (development only)

## Migration Status

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Prototype & CI | ✅ Complete | CI workflow + checklist created |
| Phase 2: Key Generation | ✅ Complete | Auto-generation with proper permissions |
| Phase 3: Integration | ✅ Complete | PQC signer integrated into main.py |
| Phase 4: Testing | ✅ Complete | 10 comprehensive tests, all passing |
| Phase 5: Staging | 🔄 Pending | Awaiting deployment schedule |
| Phase 6: Production | 🔄 Pending | Requires HSM/KMS setup |

## References

- [MATRIZ-007 Issue](https://github.com/LukhasAI/Lukhas/issues/490)
- [PQC Security Checklist](../../docs/security/MATRIZ_PQC_CHECKLIST.md)
- [PQC CI Workflow](../../.github/workflows/pqc-sign-verify.yml)
- [NodeSpec v1 Schema](../../docs/schemas/nodespec_schema.json)
- [TG-002 PR: Hybrid Registry Prototype](https://github.com/LukhasAI/Lukhas/pull/488)

