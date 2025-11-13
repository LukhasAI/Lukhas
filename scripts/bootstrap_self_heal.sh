#!/usr/bin/env bash
set -euo pipefail

mkdir -p .lukhas tools .github/workflows reports scripts

# Install test infra
python -m pip install --upgrade pip
pip install \
  pytest pytest-xdist pytest-randomly pytest-timeout pytest-rerunfailures \
  coverage[toml] mutmut ruff mypy \
  lz4 fakeredis aioresponses mcp dropbox slowapi typing_extensions freezegun

echo "✅ Ready. Run: make test && make heal"
