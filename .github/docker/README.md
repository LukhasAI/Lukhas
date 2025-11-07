# PQC Docker Runner Setup

## Overview
This directory contains Docker configurations for PQC-enabled CI runners used in MATRIZ-007 PQC migration.

## GitHub Actions Runner Provisioning

The [`pqc-sign-verify`](../workflows/pqc-sign-verify.yml) workflow now provisions
`liboqs` and the Python bindings directly on the hosted Ubuntu runner. This
removes the dependency on a pre-built container image while keeping the Docker
asset available for local development.

### Installation Summary (CI)

1. Install build tooling: `build-essential`, `cmake`, `ninja-build`, `libssl-dev`,
   `pkg-config`, `jq`, and `bc`.
2. Compile `liboqs` 0.9.2 into `$GITHUB_WORKSPACE/.oqs` (cached via
   `actions/cache`).
3. Export `LD_LIBRARY_PATH`, `PKG_CONFIG_PATH`, and `CMAKE_PREFIX_PATH` so the
   runner can locate the shared library.
4. `pip install liboqs-python==0.9.0`.
5. Execute `scripts/pqc/pqc_bench.py --json` to produce `tmp/pqc_bench.json`.

> The workflow fails fast whenever the benchmark falls back to legacy behaviour
> (`pqc_fallback_marker.txt`). Resolve provisioning issues before re-running CI.

### Local Runner Reproduction

To mimic the CI environment locally:

```bash
sudo apt-get update && sudo apt-get install -y build-essential cmake ninja-build libssl-dev pkg-config jq bc
git clone --depth 1 --branch 0.9.2 https://github.com/open-quantum-safe/liboqs.git
cmake -S liboqs -B liboqs/build -GNinja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PWD/.oqs -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON -DOQS_DIST_BUILD=ON
cmake --build liboqs/build
cmake --install liboqs/build
export LD_LIBRARY_PATH=$PWD/.oqs/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=$PWD/.oqs/lib/pkgconfig:$PKG_CONFIG_PATH
python3 -m pip install --upgrade pip
python3 -m pip install liboqs-python==0.9.0
python3 scripts/pqc/pqc_bench.py --json
```

The JSON output mirrors the CI artifact and enforces the same latency budgets.

## PQC Runner Image

The Docker image remains available for reproducible builds and debugging.

### Build
```bash
docker build -f .github/docker/pqc-runner.Dockerfile -t lukhas-pqc-runner:latest .
```

### Quick Test
```bash
# Verify PQC algorithms available
docker run --rm lukhas-pqc-runner:latest

# Run performance benchmark
docker run --rm lukhas-pqc-runner:latest pqc-bench --json

# Interactive shell
docker run --rm -it lukhas-pqc-runner:latest bash
```

### Available Tools

#### `pqc-bench`
Quick performance benchmark for Dilithium2. The CLI lives at
[`scripts/pqc/pqc_bench.py`](../../scripts/pqc/pqc_bench.py) and can be invoked
directly on any runner with liboqs installed:
```bash
python3 scripts/pqc/pqc_bench.py --json

# Equivalent Docker invocation
docker run --rm lukhas-pqc-runner:latest pqc-bench --json
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
