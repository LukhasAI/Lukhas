#!/bin/bash

# LUKHAS AI Consciousness Module Consolidation Script
# This script consolidates all consciousness-related modules into a single organized structure

set -e

echo "🧠 LUKHAS AI Consciousness Module Consolidation"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "lukhas_config.yaml" ]; then
    echo "❌ Error: Must run from LUKHAS root directory"
    exit 1
fi

# Backup current state
echo "📦 Creating backup..."
BACKUP_DIR="consciousness_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# List of consciousness modules to consolidate
CONSCIOUSNESS_MODULES=(
    "consciousness_layer"
    "consciousness_platform"
    "consciousness_api"
    "consciousness_stream"
    "consciousness_quantum_bridge"
    "consciousness_expansion_engine"
    "consciousness_verification_colony"
    "core_consciousness_bridge"
    "memory_consciousness_bridge"
)

# Backup existing modules
echo "📋 Backing up existing consciousness modules..."
for module in "${CONSCIOUSNESS_MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo "  - Backing up $module"
        cp -r "$module" "$BACKUP_DIR/"
    fi
done

# Also backup main consciousness directory
if [ -d "consciousness" ]; then
    echo "  - Backing up main consciousness directory"
    cp -r "consciousness" "$BACKUP_DIR/"
fi

echo ""
echo "✅ Backup completed to $BACKUP_DIR"
echo ""

# Create new consolidated structure
echo "🏗️ Creating consolidated consciousness structure..."

# Ensure main consciousness directory exists
mkdir -p consciousness/{core,api,bridges,engines,layers,streams,colonies}

# Move/consolidate modules
echo "📁 Consolidating modules..."

# Move consciousness_api and consciousness_platform to api/
if [ -d "consciousness_api" ]; then
    echo "  - Moving consciousness_api to consciousness/api/core/"
    mkdir -p consciousness/api/core
    cp -r consciousness_api/* consciousness/api/core/ 2>/dev/null || true
fi

if [ -d "consciousness_platform" ]; then
    echo "  - Moving consciousness_platform to consciousness/api/platform/"
    mkdir -p consciousness/api/platform
    cp -r consciousness_platform/* consciousness/api/platform/ 2>/dev/null || true
fi

# Move bridges
if [ -d "core_consciousness_bridge" ]; then
    echo "  - Moving core_consciousness_bridge to consciousness/bridges/core/"
    mkdir -p consciousness/bridges/core
    cp -r core_consciousness_bridge/* consciousness/bridges/core/ 2>/dev/null || true
fi

if [ -d "memory_consciousness_bridge" ]; then
    echo "  - Moving memory_consciousness_bridge to consciousness/bridges/memory/"
    mkdir -p consciousness/bridges/memory
    cp -r memory_consciousness_bridge/* consciousness/bridges/memory/ 2>/dev/null || true
fi

if [ -d "consciousness_quantum_bridge" ]; then
    echo "  - Moving consciousness_quantum_bridge to consciousness/bridges/quantum/"
    mkdir -p consciousness/bridges/quantum
    cp -r consciousness_quantum_bridge/* consciousness/bridges/quantum/ 2>/dev/null || true
fi

# Move engines
if [ -d "consciousness_expansion_engine" ]; then
    echo "  - Moving consciousness_expansion_engine to consciousness/engines/expansion/"
    mkdir -p consciousness/engines/expansion
    cp -r consciousness_expansion_engine/* consciousness/engines/expansion/ 2>/dev/null || true
fi

# Move layers
if [ -d "consciousness_layer" ]; then
    echo "  - Moving consciousness_layer to consciousness/layers/base/"
    mkdir -p consciousness/layers/base
    cp -r consciousness_layer/* consciousness/layers/base/ 2>/dev/null || true
fi

# Move streams
if [ -d "consciousness_stream" ]; then
    echo "  - Moving consciousness_stream to consciousness/streams/base/"
    mkdir -p consciousness/streams/base
    cp -r consciousness_stream/* consciousness/streams/base/ 2>/dev/null || true
fi

# Move colonies
if [ -d "consciousness_verification_colony" ]; then
    echo "  - Moving consciousness_verification_colony to consciousness/colonies/verification/"
    mkdir -p consciousness/colonies/verification
    cp -r consciousness_verification_colony/* consciousness/colonies/verification/ 2>/dev/null || true
fi

echo ""
echo "📝 Creating unified __init__.py files..."

# Create main __init__.py
cat > consciousness/__init__.py << 'EOF'
"""
LUKHAS AI Consolidated Consciousness Module

This module consolidates all consciousness-related components:
- Core consciousness logic
- API interfaces
- Bridge modules
- Processing engines
- Consciousness layers
- Stream processors
- Colony systems
"""

from typing import Optional

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

# Import core components
try:
    from .core import ConsciousnessCore
except ImportError:
    ConsciousnessCore = None

# Import API components
try:
    from .api.core import ConsciousnessAPI
except ImportError:
    ConsciousnessAPI = None

# Import bridges
try:
    from .bridges.memory import MemoryConsciousnessBridge
    from .bridges.core import CoreConsciousnessBridge
    from .bridges.quantum import QuantumConsciousnessBridge
except ImportError:
    pass

# Import engines
try:
    from .engines.expansion import ExpansionEngine
except ImportError:
    pass

__all__ = [
    "ConsciousnessCore",
    "ConsciousnessAPI",
    "MemoryConsciousnessBridge",
    "CoreConsciousnessBridge",
    "QuantumConsciousnessBridge",
    "ExpansionEngine",
]
EOF

echo ""
echo "🔍 Checking for import updates needed..."

# Find all Python files that import from consciousness modules
echo "Files that may need import updates:"
grep -r "from consciousness_" . --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u | head -10 || true
grep -r "import consciousness_" . --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u | head -10 || true

echo ""
echo "📊 Summary of consolidation:"
echo "  - Consolidated ${#CONSCIOUSNESS_MODULES[@]} consciousness modules"
echo "  - New structure created under consciousness/"
echo "  - Backup saved to $BACKUP_DIR"

echo ""
echo "⚠️  Next steps:"
echo "  1. Review the consolidated structure in consciousness/"
echo "  2. Update imports in affected files"
echo "  3. Run tests to ensure everything works"
echo "  4. If successful, remove old directories:"
for module in "${CONSCIOUSNESS_MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo "     rm -rf $module"
    fi
done

echo ""
echo "✅ Consciousness consolidation complete!"
echo ""
echo "To revert if needed: cp -r $BACKUP_DIR/* ."
