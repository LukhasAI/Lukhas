# SLSA Readiness Checklist

This document provides a checklist for maintainers to ensure that our project remains compliant with SLSA (Supply-chain Levels for Software Artifacts) best practices.

## Quarterly Review Checklist

- [ ] **Verify Provenance Generation:** Review the `.github/workflows/slsa-provenance.yml` file to ensure that the provenance generation process is up-to-date with the latest SLSA specification.
- [ ] **Check Containerized Build:** Confirm that the `.github/docker/Dockerfile` and `scripts/containerized-run.sh` script are still able to produce a successful and hermetic build.
- [ ] **Review Dependencies:** Examine the project's dependencies for any new vulnerabilities. Ensure that all dependencies are pinned to specific versions.
- [ ] **Audit Access Controls:** Review the access controls for the CI/CD environment. Ensure that only authorized personnel have permission to modify the build process.
- [ ] **Update SLSA Documentation:** Update this document with any new information or best practices related to SLSA.
