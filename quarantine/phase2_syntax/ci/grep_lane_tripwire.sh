#!/bin/bash
set -euo pipefail

echo "🔍 Scanning for dynamic candidate imports in lukhas/..."

# Search for importlib.import_module with candidate module strings
hits=$(grep -RIn --include="*.py" -E "importlib\.import_module\([\"']candidate" lukhas/ || true)

if [ -n "$hits" ]; then
    echo "🚨 Found dynamic imports from candidate in lukhas/:"
    echo "$hits"
    echo ""
    echo "These dynamic imports violate lane integrity. Options:"
    echo "1. Gate behind ALLOW_CANDIDATE_RUNTIME environment variable"
    echo "2. Replace with local shims/implementations"
    echo "3. Move functionality to production lukhas modules"
    exit 1
fi

echo "✅ No dynamic candidate imports found in lukhas/"
