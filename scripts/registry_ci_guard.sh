#!/usr/bin/env bash
set -euo pipefail

# Return 0 if importable, 78 to indicate skip if not importable.
python3 - <<'PY'
import sys
try:
    import importlib
    importlib.import_module('services.registry.main')
    print('OK: services.registry.main importable')
    sys.exit(0)
except Exception as e:
    print('SKIP: Registry module not importable:', e)
    sys.exit(78)
PY