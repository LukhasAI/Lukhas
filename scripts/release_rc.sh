#!/usr/bin/env bash
set -euo pipefail
VER="${1:?usage: $0 vX.Y.Z-rc}"
cz changelog
python3 scripts/sbom.py
gh release create "$VER" --notes "RC $VER" build/sbom.cyclonedx.json || true
echo "RC $VER prepared."
