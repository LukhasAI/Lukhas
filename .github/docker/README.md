# PQC Docker Runner Setup

## Overview
This directory contains Docker configurations for PQC-enabled CI runners used in MATRIZ-007 PQC migration.

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

# Interactive shell
docker run --rm -it lukhas-pqc-runner:latest bash
```

### Use in CI
Update `.github/workflows/pqc-sign-verify.yml`:

```yaml
jobs:
  pqc-test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/lukhasai/lukhas-pqc-runner:latest
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
```

> **Note:** The CI workflow now fails whenever the PQC benchmark falls back to the legacy marker file. Ensure the runner image is available to avoid breaking builds.

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

## Related Documentation

- [MATRIZ-007 PQC Migration](../../docs/ops/POST_MERGE_ACTIONS.md#matriz-007-pqc-migration-timeline)
- [Monitoring Config](../../docs/ops/monitoring_config.md)
- [liboqs Documentation](https://github.com/open-quantum-safe/liboqs)
- [python-oqs Documentation](https://github.com/open-quantum-safe/liboqs-python)
