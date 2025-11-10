#!/bin/bash
# Reproduce CI environment locally for SLSA compliance
set -euo pipefail

echo "🐳 Running LUKHAS build in containerized environment..."

# Build image
docker build -t lukhas-reproducible:latest \
  --build-arg PYTHON_VERSION=3.11 \
  .

echo "✅ Image built successfully"

# Run tests
echo "🧪 Running tests..."
docker run --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  lukhas-reproducible:latest \
  bash -c "
    pip install --upgrade pip
    pip install -r requirements.txt -r requirements-test.txt
    pytest -q --junitxml=reports/junit.xml --cov=. --cov-report=xml
  "

echo "✅ Tests passed"

# Build wheel
echo "📦 Building distribution..."
docker run --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  lukhas-reproducible:latest \
  bash -c "
    pip install build wheel
    python -m build --wheel
  "

echo "✅ Build complete"

# Generate checksums
echo "🔒 Generating checksums..."
sha256sum dist/*.whl > dist/SHA256SUMS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Reproducible build completed successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Artifacts:"
ls -lh dist/
echo ""
echo "Checksums:"
cat dist/SHA256SUMS
