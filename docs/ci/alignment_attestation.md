# Alignment Attestation

This document describes the alignment attestation process, which is a part of the CI/CD pipeline.

## Overview

The alignment attestation process is designed to provide a snapshot of the alignment of our models with our internal benchmarks. It is a key part of our commitment to responsible AI development.

The process is automated and runs on every pull request that merges into our `main` or `develop` branches.

## How it works

The process is driven by the `scripts/ci/upload_alignment_attestation.py` script. This script is responsible for:

1.  Calculating drift metrics for our models.
2.  Generating an `alignment.json` file containing these metrics.
3.  Uploading the `alignment.json` file as a GitHub Actions artifact.

The `alignment.json` file is then used by other processes to track our models' alignment over time.

## The `alignment.json` file

The `alignment.json` file is a JSON file that contains the drift metrics for our models. The file has the following structure:

```json
{
  "model_a": {
    "drift": 0.05,
    "confidence": 0.95
  },
  "model_b": {
    "drift": 0.1,
    "confidence": 0.9
  }
}
```

Each key in the JSON file corresponds to a model, and the value is an object containing the drift and confidence for that model.

*   `drift`: A measure of how much the model's output has changed over time.
*   `confidence`: A measure of our confidence in the drift calculation.

## Integration with the CI/CD pipeline

The alignment attestation process is integrated into the `dream-validate.yml` workflow. The workflow is triggered on every pull request that merges into our `main` or `develop` branches.

The workflow has the following steps:

1.  Checks out the code.
2.  Sets up Python.
3.  Installs dependencies.
4.  Runs the `scripts/ci/upload_alignment_attestation.py` script.
5.  Uploads the `alignment.json` file as a GitHub Actions artifact.
