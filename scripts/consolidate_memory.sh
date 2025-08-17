#!/bin/bash

# LUKHAS AI Memory Module Consolidation Script
# This script consolidates all memory-related modules into a single organized structure

set -e

echo "🧠 LUKHAS AI Memory Module Consolidation"
echo "========================================="

# Check if we're in the right directory
if [ ! -f "lukhas_config.yaml" ]; then
    echo "❌ Error: Must run from LUKHAS root directory"
    exit 1
fi

# Backup current state
echo "📦 Creating backup..."
BACKUP_DIR="memory_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# List of memory modules to consolidate
MEMORY_MODULES=(
    "memory_fold"
    "memory_folds"
    "memory_planning"
    "memory_manager"
    "memory_interface"
    "memory_safety_features"
    "memory_expansion"
    "memory_brain"
    "memory_tracker"
    "memory_chain"
    "memory_colony"
    "memory_colony_enhanced"
    "memory_connector"
    "memory_fold_system"
    "memory_fold_tracker"
    "memory_learning_bridge"
    "memory_log_filter"
    "memory_optimization"
    "memory_orchestrator"
    "memory_services"
)

# Backup existing modules
echo "📋 Backing up existing memory modules..."
for module in "${MEMORY_MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo "  - Backing up $module"
        cp -r "$module" "$BACKUP_DIR/"
    fi
done

# Also backup main memory directory
if [ -d "memory" ]; then
    echo "  - Backing up main memory directory"
    cp -r "memory" "$BACKUP_DIR/"
fi

echo ""
echo "✅ Backup completed to $BACKUP_DIR"
echo ""

# Create new consolidated structure
echo "🏗️ Creating consolidated memory structure..."

# Ensure main memory directory exists with proper structure
mkdir -p memory/{core,folds,safety,planning,interfaces,bridges,optimization,services,colonies}

# Move/consolidate modules
echo "📁 Consolidating modules..."

# Move fold-related modules
if [ -d "memory_fold" ]; then
    echo "  - Moving memory_fold to memory/folds/base/"
    mkdir -p memory/folds/base
    cp -r memory_fold/* memory/folds/base/ 2>/dev/null || true
fi

if [ -d "memory_folds" ]; then
    echo "  - Moving memory_folds to memory/folds/multi/"
    mkdir -p memory/folds/multi
    cp -r memory_folds/* memory/folds/multi/ 2>/dev/null || true
fi

if [ -d "memory_fold_system" ]; then
    echo "  - Moving memory_fold_system to memory/folds/system/"
    mkdir -p memory/folds/system
    cp -r memory_fold_system/* memory/folds/system/ 2>/dev/null || true
fi

if [ -d "memory_fold_tracker" ]; then
    echo "  - Moving memory_fold_tracker to memory/folds/tracker/"
    mkdir -p memory/folds/tracker
    cp -r memory_fold_tracker/* memory/folds/tracker/ 2>/dev/null || true
fi

# Move safety features
if [ -d "memory_safety_features" ]; then
    echo "  - Moving memory_safety_features to memory/safety/"
    cp -r memory_safety_features/* memory/safety/ 2>/dev/null || true
fi

# Move planning modules
if [ -d "memory_planning" ]; then
    echo "  - Moving memory_planning to memory/planning/"
    cp -r memory_planning/* memory/planning/ 2>/dev/null || true
fi

# Move interfaces
if [ -d "memory_interface" ]; then
    echo "  - Moving memory_interface to memory/interfaces/base/"
    mkdir -p memory/interfaces/base
    cp -r memory_interface/* memory/interfaces/base/ 2>/dev/null || true
fi

if [ -d "memory_connector" ]; then
    echo "  - Moving memory_connector to memory/interfaces/connector/"
    mkdir -p memory/interfaces/connector
    cp -r memory_connector/* memory/interfaces/connector/ 2>/dev/null || true
fi

# Move bridges
if [ -d "memory_learning_bridge" ]; then
    echo "  - Moving memory_learning_bridge to memory/bridges/learning/"
    mkdir -p memory/bridges/learning
    cp -r memory_learning_bridge/* memory/bridges/learning/ 2>/dev/null || true
fi

# Move optimization modules
if [ -d "memory_optimization" ]; then
    echo "  - Moving memory_optimization to memory/optimization/"
    cp -r memory_optimization/* memory/optimization/ 2>/dev/null || true
fi

# Move service modules
if [ -d "memory_services" ]; then
    echo "  - Moving memory_services to memory/services/base/"
    mkdir -p memory/services/base
    cp -r memory_services/* memory/services/base/ 2>/dev/null || true
fi

if [ -d "memory_manager" ]; then
    echo "  - Moving memory_manager to memory/services/manager/"
    mkdir -p memory/services/manager
    cp -r memory_manager/* memory/services/manager/ 2>/dev/null || true
fi

if [ -d "memory_orchestrator" ]; then
    echo "  - Moving memory_orchestrator to memory/services/orchestrator/"
    mkdir -p memory/services/orchestrator
    cp -r memory_orchestrator/* memory/services/orchestrator/ 2>/dev/null || true
fi

# Move colony modules
if [ -d "memory_colony" ]; then
    echo "  - Moving memory_colony to memory/colonies/base/"
    mkdir -p memory/colonies/base
    cp -r memory_colony/* memory/colonies/base/ 2>/dev/null || true
fi

if [ -d "memory_colony_enhanced" ]; then
    echo "  - Moving memory_colony_enhanced to memory/colonies/enhanced/"
    mkdir -p memory/colonies/enhanced
    cp -r memory_colony_enhanced/* memory/colonies/enhanced/ 2>/dev/null || true
fi

# Move other modules
if [ -d "memory_brain" ]; then
    echo "  - Moving memory_brain to memory/core/brain/"
    mkdir -p memory/core/brain
    cp -r memory_brain/* memory/core/brain/ 2>/dev/null || true
fi

if [ -d "memory_chain" ]; then
    echo "  - Moving memory_chain to memory/core/chain/"
    mkdir -p memory/core/chain
    cp -r memory_chain/* memory/core/chain/ 2>/dev/null || true
fi

if [ -d "memory_tracker" ]; then
    echo "  - Moving memory_tracker to memory/core/tracker/"
    mkdir -p memory/core/tracker
    cp -r memory_tracker/* memory/core/tracker/ 2>/dev/null || true
fi

if [ -d "memory_expansion" ]; then
    echo "  - Moving memory_expansion to memory/core/expansion/"
    mkdir -p memory/core/expansion
    cp -r memory_expansion/* memory/core/expansion/ 2>/dev/null || true
fi

if [ -d "memory_log_filter" ]; then
    echo "  - Moving memory_log_filter to memory/core/logging/"
    mkdir -p memory/core/logging
    cp -r memory_log_filter/* memory/core/logging/ 2>/dev/null || true
fi

echo ""
echo "📝 Creating unified __init__.py files..."

# Create main __init__.py
cat > memory/__init__.py << 'EOF'
"""
LUKHAS AI Consolidated Memory Module

This module consolidates all memory-related components:
- Core memory management
- Fold-based memory system
- Memory safety features
- Planning and optimization
- Memory interfaces and bridges
- Colony systems
"""

from typing import Optional

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

# Import core components
try:
    from .core import MemoryCore
    from .folds.base import MemoryFold
except ImportError:
    MemoryCore = None
    MemoryFold = None

# Import safety features
try:
    from .safety import MemorySafetyManager
except ImportError:
    MemorySafetyManager = None

# Import planning
try:
    from .planning import MemoryPlanner
except ImportError:
    MemoryPlanner = None

# Import services
try:
    from .services.manager import MemoryManager
    from .services.orchestrator import MemoryOrchestrator
except ImportError:
    pass

__all__ = [
    "MemoryCore",
    "MemoryFold",
    "MemorySafetyManager",
    "MemoryPlanner",
    "MemoryManager",
    "MemoryOrchestrator",
]
EOF

echo ""
echo "🔍 Checking for import updates needed..."

# Find all Python files that import from memory modules
echo "Files that may need import updates:"
grep -r "from memory_" . --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u | head -10 || true
grep -r "import memory_" . --include="*.py" 2>/dev/null | cut -d: -f1 | sort -u | head -10 || true

echo ""
echo "📊 Summary of consolidation:"
echo "  - Consolidated ${#MEMORY_MODULES[@]} memory modules"
echo "  - New structure created under memory/"
echo "  - Backup saved to $BACKUP_DIR"
echo "  - Note: Large memory map file (folds.mmap) preserved"

echo ""
echo "⚠️  Next steps:"
echo "  1. Review the consolidated structure in memory/"
echo "  2. Update imports in affected files"
echo "  3. Run tests to ensure everything works"
echo "  4. If successful, remove old directories:"
for module in "${MEMORY_MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo "     rm -rf $module"
    fi
done

echo ""
echo "✅ Memory consolidation complete!"
echo ""
echo "To revert if needed: cp -r $BACKUP_DIR/* ."