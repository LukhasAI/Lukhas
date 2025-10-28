# PQC Docker Runner Setup

## Overview
This directory contains Docker configurations for PQC-enabled CI runners used in MATRIZ-007 PQC migration.

**Status**: ✅ **ENABLED IN CI** - liboqs provisioned via Docker container (Issue #492)

## PQC Runner Image

### Build
```bash
docker build -f .github/docker/pqc-runner.Dockerfile -t lukhas-pqc-runner:latest .
```

### Quick Test
```bash
# Verify PQC algorithms available
docker run --rm lukhas-pqc-runner:latest

# Run performance benchmark
docker run --rm lukhas-pqc-runner:latest pqc-bench

# Run PQC tests
docker run --rm -v $(pwd):/workspace -w /workspace \
  lukhas-pqc-runner:latest \
  pytest tests/unit/services/registry/test_pqc_signer.py -v

# Interactive shell
docker run --rm -it lukhas-pqc-runner:latest bash
```

### CI Integration

The `pqc-sign-verify.yml` workflow now runs tests inside the PQC Docker container:

```yaml
jobs:
  build_pqc_image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and Export PQC Runner Image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: .github/docker/pqc-runner.Dockerfile
          tags: lukhas-pqc-runner:ci
          cache-from: type=gha
          cache-to: type=gha,mode=max
  
  pqc_tests:
    needs: build_pqc_image
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run PQC Unit Tests
        run: |
          docker run --rm \
            -v $(pwd):/workspace -w /workspace \
            lukhas-pqc-runner:ci \
            pytest tests/unit/services/registry/test_pqc_signer.py -v
```

**Key Benefits**:
- ✅ No fallback markers - tests run with real Dilithium2
- ✅ Docker build cache for fast CI runs
- ✅ Isolated PQC environment matches production
- ✅ Easy to reproduce locally

### Available Tools

#### `pqc-bench`
Quick performance benchmark for Dilithium2:
```bash
docker run --rm lukhas-pqc-runner:latest pqc-bench
```

Expected output:
```
Benchmarking Dilithium2 (100 iterations)...
  Sign   - p50: 0.45ms, p95: 0.58ms
  Verify - p50: 0.15ms, p95: 0.22ms

  Target compliance:
    Sign p95 < 50ms:   ✓ (0.58ms)
    Verify p95 < 10ms: ✓ (0.22ms)
```

#### Python OQS Library
```python
import oqs

# List available algorithms
print(oqs.sig.get_enabled_algorithms())

# Sign and verify
with oqs.Signature('Dilithium2') as sig:
    public_key = sig.generate_keypair()
    message = b"data"
    signature = sig.sign(message)
    is_valid = sig.verify(message, signature, public_key)
```

## Image Specifications

- **Base**: python:3.11-slim
- **liboqs**: 0.9.2 (Open Quantum Safe)
- **python-oqs**: 0.9.0 (liboqs-python)
- **Algorithms**: Dilithium2, Dilithium3, Dilithium5, Falcon-512, Falcon-1024, and more

## Performance Targets

| Operation | p50 Target | p95 Target | Typical |
|-----------|------------|------------|---------|
| Sign      | < 1ms      | < 50ms     | ~0.5ms  |
| Verify    | < 0.5ms    | < 10ms     | ~0.2ms  |

## GitHub Container Registry

### Publish
```bash
# Tag for GHCR
docker tag lukhas-pqc-runner:latest ghcr.io/lukhasai/lukhas-pqc-runner:latest

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push
docker push ghcr.io/lukhasai/lukhas-pqc-runner:latest
```

### Use in Actions
```yaml
container:
  image: ghcr.io/lukhasai/lukhas-pqc-runner:latest
  credentials:
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

## Local Development

### Run LUKHAS tests with PQC
```bash
docker run --rm -v $(pwd):/workspace \
  lukhas-pqc-runner:latest \
  bash -c "cd /workspace && pytest tests/pqc -v"
```

### Interactive development
```bash
docker run --rm -it -v $(pwd):/workspace \
  lukhas-pqc-runner:latest bash
```

## Troubleshooting

### liboqs not found
```bash
# Verify installation
docker run --rm lukhas-pqc-runner:latest ldconfig -p | grep liboqs
```

### Python import errors
```bash
# Check python-oqs installation
docker run --rm lukhas-pqc-runner:latest python3 -c "import oqs; print(oqs.__version__)"
```

### Performance issues
```bash
# Run detailed benchmark
docker run --rm lukhas-pqc-runner:latest python3 -c "
import oqs
import time

with oqs.Signature('Dilithium2') as sig:
    pk = sig.generate_keypair()
    msg = b'test'

    # Warmup
    for _ in range(10):
        sig.sign(msg)

    # Benchmark
    start = time.perf_counter()
    for _ in range(1000):
        sig.sign(msg)
    elapsed = time.perf_counter() - start
    print(f'Sign: {elapsed/1000*1000:.2f}ms per operation')
"
```

## Security Notes

- Private keys should NEVER be included in container images
- Use secret management (Vault, KMS) for production keys
- Container runs as root by default - consider adding USER directive for production
- Image includes build tools - create slim production variant if needed

## Issue Resolution

**Issue #492: PQC runner provisioning - enable liboqs in CI** - ✅ **RESOLVED**

**Solution**: CI now runs all PQC tests inside the liboqs-enabled Docker container instead of attempting to install libraries on the base runner.

**Changes Made**:
1. Refactored `.github/workflows/pqc-sign-verify.yml` to run tests in Docker container
2. Split into build and test jobs for efficient caching
3. Removed fallback marker generation - tests now require real PQC or fail
4. Added explicit verification that no fallback occurs

**Result**:
- ✅ CI has liboqs provisioned via Docker
- ✅ No `pqc_fallback_marker.txt` artifacts in successful runs  
- ✅ Dilithium2 signatures work in CI (not HMAC fallback)
- ✅ Performance targets validated: sign <50ms, verify <10ms

## Related Documentation

- [MATRIZ-007 PQC Migration](../../docs/ops/POST_MERGE_ACTIONS.md#matriz-007-pqc-migration-timeline)
- [Issue #492: PQC runner provisioning](https://github.com/LukhasAI/Lukhas/issues/492)
- [Monitoring Config](../../docs/ops/monitoring_config.md)
- [liboqs Documentation](https://github.com/open-quantum-safe/liboqs)
- [python-oqs Documentation](https://github.com/open-quantum-safe/liboqs-python)
