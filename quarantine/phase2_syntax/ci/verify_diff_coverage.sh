#!/usr/bin/env bash
set -euo pipefail
pytest --maxfail=1 --disable-warnings --cov=lukhas --cov=candidate --cov-report xml:coverage.xml -q
pip install --quiet diff-cover
diff-cover coverage.xml --compare-branch origin/main --fail-under=80
echo "✅ Diff coverage OK (>=80%)"
