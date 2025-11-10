# SLSA Build Provenance for LUKHAS AI

Supply Chain Levels for Software Artifacts (SLSA) compliance documentation

## Overview

LUKHAS AI implements **SLSA Level 1** provenance to ensure build transparency and supply chain security.

## SLSA Level 1 Requirements

✅ **Build Provenance** - All builds generate provenance metadata
✅ **Source Tracking** - Git commit SHA recorded for every build
✅ **Builder Identity** - CI/CD system identity included
✅ **Reproducible Builds** - Builds can be reproduced with same inputs

## Build Information Template

```json
{
  "builder": {
    "id": "https://github.com/LukhasAI/Lukhas/actions/runs/XXXXXX"
  },
  "buildType": "https://github.com/LukhasAI/Lukhas/.github/workflows/slsa-build.yml@refs/heads/main",
  "invocation": {
    "configSource": {
      "uri": "git+https://github.com/LukhasAI/Lukhas@refs/heads/main",
      "digest": {
        "sha1": "<commit-sha>"
      }
    }
  },
  "metadata": {
    "buildStartedOn": "2025-01-08T12:00:00Z",
    "buildFinishedOn": "2025-01-08T12:15:00Z",
    "completeness": {
      "parameters": true,
      "environment": true,
      "materials": true
    },
    "reproducible": true
  },
  "materials": [
    {
      "uri": "git+https://github.com/LukhasAI/Lukhas",
      "digest": {
        "sha1": "<commit-sha>"
      }
    }
  ]
}
```

## Reproducibility Guide

To reproduce a build:

```bash
# 1. Checkout exact commit
git checkout <commit-sha>

# 2. Use containerized build
docker build -t lukhas-api:reproducible .

# 3. Run tests
docker run --rm lukhas-api:reproducible python -m pytest

# 4. Generate wheel
docker run --rm -v $(pwd)/dist:/dist lukhas-api:reproducible \
  python -m build --wheel
```

## Verification

Verify build artifacts:

```bash
# Verify wheel hash
sha256sum dist/lukhas-*.whl

# Compare with provenance record
cat .slsa/provenance/<version>.json | jq '.materials[0].digest.sha256'
```

## CI Integration

See `.github/workflows/slsa-build.yml` for automated provenance generation.

## Supply Chain Security

### Dependency Pinning

All dependencies are pinned in:
- `requirements.txt` - Runtime dependencies with exact versions
- `requirements-test.txt` - Test dependencies
- `requirements-dev.txt` - Development dependencies

### Vulnerability Scanning

```bash
# Scan dependencies
pip-audit

# Scan containers
trivy image lukhas-api:latest

# SBOM generation
syft packages dir:. -o spdx-json > sbom.json
```

## Compliance Checklist

- [x] Build provenance generated for all releases
- [x] Source code tracked with Git commit SHA
- [x] CI/CD builder identity recorded
- [x] Dependencies pinned with exact versions
- [x] Vulnerability scanning enabled
- [x] Reproducible builds documented
- [ ] SLSA Level 2 (future): Build service isolation
- [ ] SLSA Level 3 (future): Hermetic builds

## References

- [SLSA Specification](https://slsa.dev/)
- [GitHub Actions SLSA](https://github.com/slsa-framework/slsa-github-generator)
- [Supply Chain Security Best Practices](https://github.com/ossf/scorecard)
