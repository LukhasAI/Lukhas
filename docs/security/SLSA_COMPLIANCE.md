# SLSA Compliance

This document outlines the SLSA (Supply-chain Levels for Software Artifacts) compliance for the LUKHAS project.

## Overview

We have implemented a GitHub Actions workflow to generate SLSA provenance for our critical modules. This helps us secure our software supply chain by providing a verifiable record of how our artifacts were built.

## Workflow

The SLSA provenance generation is handled by the `.github/workflows/slsa-provenance.yml` workflow. This workflow is triggered on pushes to the `main` branch and on the creation of a new release.

The workflow performs the following steps:

1.  **Builds the software artifacts**: It builds the Python wheels for the specified modules.
2.  **Generates provenance**: It uses the `scripts/slsa/generate_provenance.py` script to generate a detailed SLSA provenance file in the in-toto format.
3.  **Signs the provenance**: It uses Cosign and GitHub's OIDC to sign the provenance file, creating a verifiable and tamper-proof attestation.
4.  **Uploads the provenance**: The signed provenance is uploaded as a build artifact, allowing for later verification.

## SLSA Level

Our current implementation meets the requirements for **SLSA Level 2**.

-   **Provenance**: The build process generates provenance that describes the build process, top-level inputs, and the builder.
-   **Verifiable**: The provenance is signed by the build service in a way that is verifiable by consumers.
-   **Non-forgeable**: The provenance is generated in a trusted build environment and cannot be tampered with by the user running the build.

We are actively working towards achieving SLSA Level 3, which will require further hardening of our build process to prevent unauthorized modifications.
