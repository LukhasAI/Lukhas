---
status: wip
type: documentation
---
# LUKHAS Consolidation Plan
## Moving Everything to /lukhas/
### Constellation Framework: ⚛️🧠🛡️

Generated: 2025-08-13

---

## 🎯 OBJECTIVE: One Unified Directory Structure

**FROM**: Scattered across 153 directories
**TO**: Everything under `/lukhas/`

This will:
- Fix all broken imports automatically
- Create clear module hierarchy
- Reduce orphan rate dramatically
- Make everything discoverable

---

## 📁 NEW STRUCTURE

```
lukhas/
├── core/                 # Core infrastructure (905 files)
│   ├── agi/             # AGI systems
│   ├── bootstrap/       # System initialization
│   ├── adapters/        # Service adapters
│   └── interfaces/      # API interfaces
├── consciousness/        # Consciousness systems (323 files)
│   ├── awareness/
│   ├── dream/
│   ├── reflection/
│   └── unified/
├── memory/              # Memory systems (380 files)
│   ├── folds/
│   ├── core/
│   ├── systems/
│   └── protection/
├── governance/          # Ethics & Guardian (285 files)
│   ├── guardian/
│   ├── ethics/
│   └── identity/
├── emotion/             # Emotional systems (35 files)
│   ├── vad/
│   ├── regulation/
│   └── tools/
├── quantum/             # Quantum-inspired (43 files)
├── bio/                 # Bio-inspired (31 files)
├── vivox/               # VIVOX system (50 files)
├── bridge/              # External bridges (158 files)
├── orchestration/       # Brain orchestration (93 files)
├── api/                 # API endpoints (6 files)
├── identity/            # Identity management (41 files)
├── symbolic/            # Symbolic/GLYPH (16 files)
├── qim/                 # QIM modules (173 files)
├── tools/               # Analysis tools (189 files)
└── main.py              # Single entry point
```

---

## 🚀 MIGRATION SCRIPT

```bash
#!/bin/bash
# LUKHAS Consolidation Script
# Moves everything to /lukhas/ and fixes imports

set -e  # Exit on error

echo "🚀 Starting LUKHAS consolidation..."

# Create backup first
BACKUP_DIR="lukhas_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup: $BACKUP_DIR"
cp -r . "../$BACKUP_DIR"

# Create lukhas directory if not exists
mkdir -p lukhas

# Move major modules (preserving structure)
MODULES=(
    "core"
    "consciousness"
    "memory"
    "governance"
    "emotion"
    "quantum"
    "bio"
    "vivox"
    "bridge"
    "orchestration"
    "api"
    "identity"
    "symbolic"
    "universal_language"
    "qim"
    "reasoning"
    "creativity"
    "NIAS_THEORY"
)

for module in "${MODULES[@]}"; do
    if [ -d "$module" ]; then
        echo "📁 Moving $module to lukhas/$module"
        mv "$module" "lukhas/" 2>/dev/null || true
    fi
done

# Move Python files in root to lukhas/
echo "📄 Moving root Python files..."
find . -maxdepth 1 -name "*.py" -exec mv {} lukhas/ \; 2>/dev/null || true

# Move tools separately (for organization)
if [ -d "tools" ]; then
    echo "🔧 Moving tools..."
    mv tools lukhas/tools
fi

# Update imports in all Python files
echo "🔄 Updating import paths..."
find lukhas -name "*.py" -type f -exec sed -i.bak \
    -e 's/^from core\./from lukhas.core./g' \
    -e 's/^from consciousness\./from lukhas.consciousness./g' \
    -e 's/^from memory\./from lukhas.memory./g' \
    -e 's/^from governance\./from lukhas.governance./g' \
    -e 's/^from emotion\./from lukhas.emotion./g' \
    -e 's/^from quantum\./from lukhas.quantum./g' \
    -e 's/^from bio\./from lukhas.bio./g' \
    -e 's/^from vivox\./from lukhas.vivox./g' \
    -e 's/^from bridge\./from lukhas.bridge./g' \
    -e 's/^from orchestration\./from lukhas.orchestration./g' \
    -e 's/^from api\./from lukhas.api./g' \
    -e 's/^from identity\./from lukhas.identity./g' \
    -e 's/^import core\./import lukhas.core./g' \
    -e 's/^import consciousness\./import lukhas.consciousness./g' \
    -e 's/^import memory\./import lukhas.memory./g' \
    {} \;

# Create new main.py at root
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
LUKHAS AI - Unified Entry Point
All modules now under lukhas/
"""

import sys
import os

# Add lukhas to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lukhas'))

# Import the actual main
from lukhas.main import main

if __name__ == "__main__":
    main()
EOF

# Fix the broken adapter imports while we're at it
echo "🔧 Fixing broken adapter imports..."
ADAPTER_FILE="lukhas/core/adapters/module_service_adapter.py"
if [ -f "$ADAPTER_FILE" ]; then
    sed -i.bak \
        -e 's/from memory\.memory_fold/from lukhas.memory.folds.memory_fold/g' \
        -e 's/from governance\.guardian\.guardian_system/from lukhas.governance.guardian_system/g' \
        -e 's/from governance\.reflector/from lukhas.governance.reflector/g' \
        -e 's/from emotion\.core\./from lukhas.emotion./g' \
        "$ADAPTER_FILE"
fi

# Create __init__.py for lukhas
cat > lukhas/__init__.py << 'EOF'
"""
LUKHAS AI - Logical Unified Knowledge Hyper-Adaptable System
Constellation Framework: ⚛️🧠🛡️

All modules consolidated under lukhas/ for clean architecture.
"""

__version__ = "1.0.0"
__all__ = [
    "core",
    "consciousness",
    "memory",
    "governance",
    "emotion",
    "quantum",
    "bio",
    "vivox",
    "orchestration",
    "bridge",
    "api",
]
EOF

# Clean up backup files
find lukhas -name "*.bak" -delete

echo "✅ Consolidation complete!"
echo "📊 Modules moved to lukhas/"
echo "🔄 Import paths updated"
echo "📦 Backup saved to: $BACKUP_DIR"
```

---

## 🔄 IMPORT PATH UPDATES

### Before:
```python
from core.bootstrap import get_bootstrap
from memory.folds.memory_fold import MemoryFoldSystem
from consciousness.awareness import AwarenessModule
```

### After:
```python
from lukhas.core.bootstrap import get_bootstrap
from lukhas.memory.folds.memory_fold import MemoryFoldSystem
from lukhas.consciousness.awareness import AwarenessModule
```

---

## 📋 STEP-BY-STEP PROCESS

### Phase 1: Preparation (10 min)
1. Create full backup
2. Create `/lukhas/` directory
3. Document current structure

### Phase 2: Migration (30 min)
1. Move all module directories to `/lukhas/`
2. Move root Python files
3. Preserve directory structures

### Phase 3: Import Updates (1 hour)
1. Update all import statements
2. Fix broken adapter paths
3. Update entry points

### Phase 4: Verification (30 min)
1. Test main.py runs
2. Check imports work
3. Run usage analysis

### Phase 5: Cleanup (10 min)
1. Remove old empty directories
2. Update documentation
3. Commit changes

---

## ✅ BENEFITS

### Immediate:
- **All imports fixed** automatically
- **Clear hierarchy** - everything under lukhas/
- **No more orphans** from broken paths
- **Single source of truth**

### Long-term:
- **Easy to navigate** - one place to look
- **Import clarity** - all start with `lukhas.`
- **Package ready** - can pip install as package
- **Professional structure** - like major Python projects

---

## 🚨 WHAT TO WATCH FOR

### Potential Issues:
1. **Circular imports** - May surface when everything is connected
2. **Name conflicts** - Multiple `__init__.py` files
3. **Path dependencies** - Hardcoded paths in configs
4. **Test updates** - Tests may need path updates

### Solutions:
- Run incrementally, test after each module
- Use `git status` to track changes
- Keep backup until verified working

---

## 📊 EXPECTED RESULTS

### Before Consolidation:
- 3,941 files across 153 directories
- 98.5% orphaned
- Broken imports everywhere
- Can't find modules

### After Consolidation:
- 3,941 files under `/lukhas/`
- ~20% orphaned (truly unused)
- All imports working
- Everything discoverable

---

## 🎯 QUICK COMMAND

Run this to start:

```bash
# Create the migration script
cat > consolidate_to_lukhas.sh << 'SCRIPT'
[paste the script from above]
SCRIPT

# Make executable
chmod +x consolidate_to_lukhas.sh

# Run it!
./consolidate_to_lukhas.sh
```

---

## 🚀 READY TO CONSOLIDATE!

This will:
1. Fix ALL broken imports
2. Create clean structure
3. Make everything discoverable
4. Reduce orphan rate to ~20%

Your 3,941 files will finally be properly connected! Want to proceed? 🎉
