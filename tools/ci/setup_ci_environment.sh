#!/bin/bash
# LUKHAS AI CI Environment Setup Script

set -euo pipefail

echo "🚀 Setting up LUKHAS AI CI environment..."

# Update system packages
sudo apt-get update -y
sudo apt-get install -y build-essential curl git jq

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip setuptools wheel

# Install CI requirements
if [ -f "requirements-ci.txt" ]; then
    pip install -r requirements-ci.txt
else
    pip install -e .[dev]
fi

# Install additional tools
pip install pytest-xdist pytest-timeout hypothesis mutmut

# Setup environment variables
export PYTHONPATH="."
export PYTHONHASHSEED="0"
export TZ="UTC"

# Verify installation
echo "🔍 Verifying installation..."
python --version
pytest --version
ruff --version
black --version

echo "✅ CI environment setup complete!"
