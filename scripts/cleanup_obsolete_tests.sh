#!/bin/bash
# LUKHAS Test Cleanup Script
# Generated: 2025-08-17

set -e

echo "🧹 Cleaning up obsolete tests..."
echo "================================"

# Archive directory for obsolete tests
ARCHIVE_DIR="$HOME/LOCAL-REPOS/lukhas-archive/2025-08-17-obsolete-tests"
mkdir -p "$ARCHIVE_DIR"


# Archive tests/consciousness/__init__.py
echo "  Archiving: tests/consciousness/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/consciousness/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/e2e/__init__.py
echo "  Archiving: tests/e2e/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/e2e/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/unit/test_STUB_consciousness.py
echo "  Archiving: tests/unit/test_STUB_consciousness.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/test_STUB_consciousness.py" "$ARCHIVE_DIR/"

# Archive tests/test_ops_backup_health.py
echo "  Archiving: tests/test_ops_backup_health.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/test_ops_backup_health.py" "$ARCHIVE_DIR/"

# Archive tests/identity/__init__.py
echo "  Archiving: tests/identity/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/identity/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/vivox/__init__.py
echo "  Archiving: tests/vivox/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/vivox/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/test_backup_manifest.py
echo "  Archiving: tests/test_backup_manifest.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/test_backup_manifest.py" "$ARCHIVE_DIR/"

# Archive tests/security/__init__.py
echo "  Archiving: tests/security/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/security/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/unit/test_STUB_symbolic.py
echo "  Archiving: tests/unit/test_STUB_symbolic.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/test_STUB_symbolic.py" "$ARCHIVE_DIR/"

# Archive tests/core/__init__.py
echo "  Archiving: tests/core/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/core/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/api/__init__.py
echo "  Archiving: tests/api/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/api/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/unit/test_STUB_memory.py
echo "  Archiving: tests/unit/test_STUB_memory.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/test_STUB_memory.py" "$ARCHIVE_DIR/"

# Archive tests/memory/__init__.py
echo "  Archiving: tests/memory/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/memory/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/branding/__init__.py
echo "  Archiving: tests/branding/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/branding/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/bridge/__init__.py
echo "  Archiving: tests/bridge/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/bridge/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/integration/__init__.py
echo "  Archiving: tests/integration/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/integration/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/simulation/__init__.py
echo "  Archiving: tests/simulation/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/simulation/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/unit/__init__.py
echo "  Archiving: tests/unit/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/governance/__init__.py
echo "  Archiving: tests/governance/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/governance/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/unit/test_STUB_guardian.py
echo "  Archiving: tests/unit/test_STUB_guardian.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/unit/test_STUB_guardian.py" "$ARCHIVE_DIR/"

# Archive tests/canary/__init__.py
echo "  Archiving: tests/canary/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/canary/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/test_STUB_framework.py
echo "  Archiving: tests/test_STUB_framework.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/test_STUB_framework.py" "$ARCHIVE_DIR/"

# Archive tests/api/test_STUB_enhanced_api.py
echo "  Archiving: tests/api/test_STUB_enhanced_api.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/api/test_STUB_enhanced_api.py" "$ARCHIVE_DIR/"

# Archive tests/serve/__init__.py
echo "  Archiving: tests/serve/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/serve/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/stress/__init__.py
echo "  Archiving: tests/stress/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/stress/__init__.py" "$ARCHIVE_DIR/"

# Archive tests/tools/__init__.py
echo "  Archiving: tests/tools/__init__.py"
mv "/Users/agi_dev/LOCAL-REPOS/Lukhas/tests/tools/__init__.py" "$ARCHIVE_DIR/"

echo ""
echo "✅ Cleanup complete!"
echo f"  Archived {len(obsolete)} obsolete test files"
echo "  Location: $ARCHIVE_DIR"
