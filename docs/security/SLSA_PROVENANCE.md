# SLSA Provenance & Supply Chain Security

**Version**: 1.0.0  
**Status**: Production  
**Last Updated**: 2025-01-10  
**SLSA Level**: Level 2 (targeting Level 3)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Generated Artifacts](#generated-artifacts)
- [Verification Guide](#verification-guide)
- [Key Management](#key-management)
- [Reproducibility](#reproducibility)
- [Troubleshooting](#troubleshooting)

---

## Overview

LUKHAS AI implements **SLSA (Supply-chain Levels for Software Artifacts)** provenance to provide:

- **Build Transparency**: Every build produces verifiable provenance metadata
- **Supply Chain Security**: Cryptographically signed SBOMs and attestations
- **Reproducibility**: Deterministic builds with pinned dependencies
- **Audit Trail**: Complete record of build inputs, environment, and outputs

### SLSA Level Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Source**: Version controlled | ✅ Complete | GitHub repository |
| **Build**: Scripted build | ✅ Complete | GitHub Actions workflow |
| **Provenance**: Available | ✅ Complete | JSON provenance + in-toto |
| **Provenance**: Authenticated | ✅ Complete | Cosign keyless signing |
| **Provenance**: Service generated | ✅ Complete | GitHub Actions |
| **Hermetic**: Isolated | 🟡 Partial | Ubuntu runner (not fully hermetic) |
| **Reproducible**: Deterministic | 🟡 Partial | Pinned deps, some non-determinism |

**Current Level**: **SLSA Level 2**  
**Target**: SLSA Level 3 (add hermetic builds with Nix/uv)

---

## Architecture

### Build Pipeline

```
┌──────────────────┐
│  Git Repository  │
│  (GitHub)        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GitHub Actions  │
│  Runner          │
│  (ubuntu-latest) │
└────────┬─────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌────────────────┐     ┌────────────────┐
│  Syft          │     │  Python Build  │
│  (SBOM gen)    │     │  (wheel/sdist) │
└────────┬───────┘     └────────┬───────┘
         │                      │
         ▼                      ▼
┌────────────────┐     ┌────────────────┐
│  SBOM.json     │     │  dist/*.whl    │
│  (packages)    │     │  (artifacts)   │
└────────┬───────┘     └────────┬───────┘
         │                      │
         └──────────┬───────────┘
                    ▼
         ┌────────────────────┐
         │  in-toto           │
         │  (link metadata)   │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Provenance.json   │
         │  (build metadata)  │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Cosign            │
         │  (sign artifacts)  │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  *.bundle          │
         │  (signatures)      │
         └────────────────────┘
```

### Provenance Metadata Structure

The `provenance.json` file contains:

```json
{
  "SLSA_VERSION": "1.0",
  "buildType": "https://github.com/LukhasAI/Lukhas/slsa-build@v1",
  "builder": {
    "id": "https://github.com/actions/runner"
  },
  "invocation": {
    "configSource": {
      "uri": "git+https://github.com/LukhasAI/Lukhas@refs/heads/main",
      "digest": {"sha1": "<commit-sha>"}
    },
    "parameters": {
      "workflow_ref": ".github/workflows/slsa_provenance.yml",
      "event_name": "push"
    }
  },
  "metadata": {
    "buildStartedOn": "2025-01-10T12:00:00Z",
    "buildFinishedOn": "2025-01-10T12:05:00Z",
    "reproducible": true
  },
  "materials": [
    {
      "uri": "git+https://github.com/LukhasAI/Lukhas",
      "digest": {"sha1": "<commit-sha>"}
    }
  ],
  "sbomHash": {"sha256": "<sbom-hash>"},
  "artifactChecksums": "<checksums-content>",
  "buildCommand": "python -m build --outdir dist/"
}
```

---

## Generated Artifacts

Each CI run produces these artifacts in the `slsa-provenance` artifact bundle:

| Artifact | Description | Format | Size |
|----------|-------------|--------|------|
| **sbom.json** | Software Bill of Materials (SPDX) | JSON | ~50KB |
| **sbom-cyclonedx.json** | SBOM in CycloneDX format | JSON | ~60KB |
| **sbom.txt** | Human-readable package list | Text | ~10KB |
| **provenance.json** | Build provenance metadata | JSON | ~2KB |
| **build.*.link** | in-toto link metadata | JSON | ~3KB |
| **sbom.bundle** | Cosign signature bundle for SBOM | Binary | ~5KB |
| **provenance.bundle** | Cosign signature bundle for provenance | Binary | ~5KB |
| **artifact-checksums.txt** | SHA256 checksums of build artifacts | Text | ~1KB |
| **slsa-summary.md** | Human-readable summary | Markdown | ~2KB |

---

## Verification Guide

### Prerequisites

Install verification tools:

```bash
# Install cosign
curl -sSL -o /usr/local/bin/cosign \
  https://github.com/sigstore/cosign/releases/download/v2.2.1/cosign-linux-amd64
chmod +x /usr/local/bin/cosign
cosign version

# Install syft (optional, for SBOM inspection)
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
  sh -s -- -b /usr/local/bin v0.99.0

# Install in-toto (optional, for link verification)
pip install in-toto==2.1.1

# Install GitHub CLI (for downloading artifacts)
# macOS: brew install gh
# Linux: https://cli.github.com/
```

### Download Artifacts

```bash
# List recent workflow runs
gh run list --workflow="SLSA Provenance"

# Download artifacts from a specific run
gh run download <run-id> -n slsa-provenance

# Or download latest
gh run download $(gh run list --workflow="SLSA Provenance" --limit 1 --json databaseId --jq '.[0].databaseId') \
  -n slsa-provenance
```

### Verify SBOM Signature

```bash
# Verify SBOM was signed by GitHub Actions
cosign verify-blob \
  --bundle sbom.bundle \
  --certificate-identity-regexp=".*github.com/LukhasAI/Lukhas.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  sbom.json

# Expected output:
# Verified OK
```

### Verify Provenance Signature

```bash
# Verify provenance signature
cosign verify-blob \
  --bundle provenance.bundle \
  --certificate-identity-regexp=".*github.com/LukhasAI/Lukhas.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  provenance.json

# Expected output:
# Verified OK
```

### Verify Artifact Checksums

```bash
# Verify build artifacts match recorded checksums
cd dist/
sha256sum -c ../artifact-checksums.txt

# Expected output:
# lukhas-0.1.0-py3-none-any.whl: OK
# lukhas-0.1.0.tar.gz: OK
```

### Inspect SBOM

```bash
# View SBOM summary
syft packages file:sbom.json -o table

# Search for specific package
syft packages file:sbom.json -o json | jq '.artifacts[] | select(.name == "requests")'

# Check for vulnerabilities (requires Grype)
grype sbom:sbom.json
```

### Verify Provenance Metadata

```bash
# Check provenance structure
python3 << 'PYTHON'
import json

with open('provenance.json') as f:
    prov = json.load(f)

print("Build Type:", prov['buildType'])
print("Builder:", prov['builder']['id'])
print("Git SHA:", prov['invocation']['configSource']['digest']['sha1'])
print("Build Started:", prov['metadata']['buildStartedOn'])
print("Reproducible:", prov['metadata']['reproducible'])
PYTHON
```

### Verify in-toto Link

```bash
# Verify in-toto link file
in-toto-verify \
  --layout-keys build.*.link \
  --link-dir .

# Or inspect manually
python3 << 'PYTHON'
import json
import glob

link_file = glob.glob('build.*.link')[0]
with open(link_file) as f:
    link = json.load(f)

print("Step:", link['name'])
print("Materials:", len(link['materials']))
print("Products:", len(link['products']))
PYTHON
```

---

## Key Management

### Keyless Signing (Sigstore)

LUKHAS uses **cosign keyless signing** with Sigstore for production builds:

- **No private keys** stored in repository or CI
- **OIDC tokens** from GitHub Actions authenticate the build
- **Public transparency log** (Rekor) records all signatures
- **Certificate chain** proves authenticity

### Signature Verification

Signatures can be verified by anyone without access to private keys:

```bash
# Verify using public Sigstore infrastructure
cosign verify-blob \
  --bundle sbom.bundle \
  --certificate-identity-regexp="https://github.com/LukhasAI/Lukhas/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  sbom.json
```

### Security Considerations

✅ **Strengths**:
- No key rotation needed
- Public audit trail in Rekor
- Tied to GitHub identity via OIDC
- Tamper-evident

⚠️ **Limitations**:
- Requires internet for verification (Rekor lookup)
- Trust in Sigstore infrastructure
- GitHub Actions compromise = signing compromise

### Future: Hardware Security Module (HSM)

For SLSA Level 3+, consider:

```yaml
# Example: Use cloud KMS for signing
- name: Sign with Cloud KMS
  env:
    GCP_KMS_KEY: ${{ secrets.GCP_KMS_KEY }}
  run: |
    cosign sign-blob \
      --key gcpkms://projects/PROJECT/locations/LOCATION/keyRings/RING/cryptoKeys/KEY \
      --bundle provenance.bundle \
      provenance.json
```

---

## Reproducibility

### Deterministic Build Requirements

The build is designed to be reproducible when:

1. **Same Git commit**: Identical source code
2. **Same dependencies**: Pinned versions in workflow
3. **Same build tools**: Pinned syft, cosign, in-toto versions
4. **Same Python version**: 3.11 (pinned in workflow)

### Known Non-Determinism

⚠️ **Timestamps**: Build start/finish times will differ  
⚠️ **Runner metadata**: GitHub run IDs will be different  
⚠️ **Python wheel metadata**: BUILD file may include timestamps

### Verifying Reproducibility

```bash
# Run build twice with same commit
git checkout <commit-sha>

# First build
gh workflow run "SLSA Provenance"
# Wait for completion, download artifacts to build1/

# Second build  
gh workflow run "SLSA Provenance"
# Wait for completion, download artifacts to build2/

# Compare SBOMs (should be identical)
diff build1/sbom.json build2/sbom.json

# Compare provenance (excluding timestamps)
jq 'del(.metadata.buildStartedOn, .metadata.buildFinishedOn, .invocation.environment)' \
  build1/provenance.json > build1/prov-normalized.json
jq 'del(.metadata.buildStartedOn, .metadata.buildFinishedOn, .invocation.environment)' \
  build2/provenance.json > build2/prov-normalized.json
diff build1/prov-normalized.json build2/prov-normalized.json
```

### Roadmap to Full Reproducibility

- [ ] Use Nix or uv for hermetic Python environment
- [ ] Remove timestamps from provenance (use git commit time)
- [ ] Pin all transitive dependencies with lock file
- [ ] Use deterministic wheel builder (reproducible-wheel)

---

## Troubleshooting

### Problem: Signature Verification Fails

**Symptoms**: `cosign verify-blob` returns error

**Solutions**:

1. Check certificate identity matches repository:
   ```bash
   # Should match your repo
   --certificate-identity-regexp="https://github.com/LukhasAI/Lukhas/.*"
   ```

2. Verify OIDC issuer:
   ```bash
   # Must be GitHub Actions
   --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
   ```

3. Check bundle file is not corrupted:
   ```bash
   file sbom.bundle  # Should be "data" or JSON
   ```

4. Ensure using correct cosign version:
   ```bash
   cosign version  # Should be 2.2.1+
   ```

### Problem: SBOM Contains Unexpected Packages

**Symptoms**: `syft` shows packages not in requirements.txt

**Solutions**:

1. Check if dev dependencies are included:
   ```bash
   # Filter to production deps only
   syft packages file:sbom.json -o json | \
     jq '.artifacts[] | select(.metadata.scope == "runtime")'
   ```

2. Review build environment:
   ```bash
   # Check what was installed during build
   grep "pip install" .github/workflows/slsa_provenance.yml
   ```

### Problem: Provenance Missing Fields

**Symptoms**: `test_slsa_provenance.py` fails

**Solutions**:

1. Check provenance.json structure:
   ```bash
   jq 'keys' provenance.json
   ```

2. Re-run workflow if incomplete:
   ```bash
   gh workflow run "SLSA Provenance"
   ```

3. Validate locally:
   ```bash
   python tests/test_slsa_provenance.py
   ```

### Problem: in-toto Link File Missing

**Symptoms**: `build.*.link` file not in artifacts

**Solutions**:

1. Check in-toto installation in workflow
2. Verify link file was created:
   ```bash
   # In CI logs, look for:
   in-toto-run --step-name build ...
   ```

3. Check artifact upload includes link files:
   ```yaml
   - uses: actions/upload-artifact@v4
     with:
       path: |
         reports/*.link  # Must be included
   ```

---

## Resources

**SLSA Specification**:
- https://slsa.dev/spec/v1.0/
- https://slsa.dev/spec/v1.0/levels

**Tools**:
- Syft: https://github.com/anchore/syft
- Cosign: https://github.com/sigstore/cosign
- in-toto: https://in-toto.io/

**Related Documentation**:
- [OpenAPI Drift Detection](../../tools/check_openapi_drift.py)
- [Prometheus Monitoring](../operations/PROMETHEUS_MONITORING_GUIDE.md)
- [CI/CD Best Practices](../development/T4_DEVELOPMENT_STANDARDS.md)

---

**Last Updated**: 2025-01-10  
**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**SLSA Level**: 2 (targeting 3)

🤖 Generated with Claude Code
