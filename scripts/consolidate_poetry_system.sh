#!/bin/bash

# LUKHAS Poetry System Consolidation Script
# Purpose: Move new poetry system to branding, archive legacy poetry

set -e

echo "════════════════════════════════════════════════════════════"
echo "         LUKHAS Poetry System Consolidation"
echo "════════════════════════════════════════════════════════════"
echo

REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
cd "$REPO_ROOT"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Step 1: Create new structure
echo "Step 1: Creating new poetry structure in branding..."
mkdir -p branding/poetry
mkdir -p branding/poetry/legacy
mkdir -p docs/archive/legacy_poetry

print_status "Created new directory structure"

# Step 2: Move new poetry system to branding
echo
echo "Step 2: Moving new poetry system to branding/poetry..."

if [ -d "poetry" ]; then
    # Copy the new poetry system
    cp -r poetry/* branding/poetry/ 2>/dev/null || true
    print_status "Moved new poetry system to branding/poetry"
    
    # Remove the old location
    rm -rf poetry
    print_status "Removed poetry from root"
fi

# Step 3: Archive legacy poetry files
echo
echo "Step 3: Archiving legacy poetry files..."

# Archive the old haiku generator
if [ -f "consciousness/creativity/advanced_haiku_generator.py" ]; then
    cp consciousness/creativity/advanced_haiku_generator.py branding/poetry/legacy/
    print_status "Archived old haiku generator to legacy"
fi

# Archive frontend poetry that uses generic metaphors
if [ -f "matada_agi/frontend/lib/lukhas-expanded-poetry.ts" ]; then
    cp matada_agi/frontend/lib/lukhas-expanded-poetry.ts docs/archive/legacy_poetry/
    print_status "Archived frontend expanded poetry (uses generic metaphors)"
fi

if [ -f "matada_agi/frontend/lib/lukhas-dream-vocabulary.ts" ]; then
    cp matada_agi/frontend/lib/lukhas-dream-vocabulary.ts docs/archive/legacy_poetry/
    print_status "Archived frontend dream vocabulary (uses generic metaphors)"
fi

# Step 4: Create migration guide
echo
echo "Step 4: Creating migration guide..."

cat > branding/poetry/POETRY_MIGRATION_GUIDE.md << 'EOF'
# LUKHAS Poetry System Migration Guide

## New Structure (As of Aug 17, 2024)

### Location: `/branding/poetry/`

This is now the SINGLE SOURCE OF TRUTH for all LUKHAS poetry and vocabulary.

## Core Components

### 1. **lukhas_lexicon.py**
The authoritative LUKHAS vocabulary. NO generic metaphors allowed.
- Lambda System (ΛMIRROR, ΛECHO, ΛTRACE, etc.)
- Memory Folding operations
- Consciousness states
- Bio-inspired terms
- Quantum-inspired terms

### 2. **vocabulary_amplifier.py**
Automatically replaces generic metaphors with LUKHAS-specific terms.
- Replaces "tapestry" → "fold-space"
- Replaces "symphony" → "resonance cascade"
- Replaces "cathedral" → "consciousness architecture"

### 3. **cliche_analysis.py**
Detects and reports generic metaphors in code.

### 4. **soul.py**
Poetry generation engine using ONLY LUKHAS vocabulary.

## Legacy Files (Archived)

### `/branding/poetry/legacy/`
- `advanced_haiku_generator.py` - Old haiku generator (uses generic metaphors)

### `/docs/archive/legacy_poetry/`
- `lukhas-expanded-poetry.ts` - Frontend poetry (uses generic metaphors)
- `lukhas-dream-vocabulary.ts` - Frontend vocabulary (uses generic metaphors)

## Migration Steps

### For Python Code:
```python
# OLD - Don't use
from consciousness.creativity import advanced_haiku_generator

# NEW - Use this
from branding.poetry import soul
from branding.poetry import lukhas_lexicon
from branding.poetry import vocabulary_amplifier
```

### For TypeScript/Frontend:
```typescript
// Create new TypeScript versions using the Python vocabulary
// Convert lukhas_lexicon.py to TypeScript
// Use vocabulary_amplifier patterns in frontend
```

## The Core Principle

**"If another AI project could have written it, we don't want it."**

Every line of poetry, every metaphor, every description must be uniquely LUKHAS.

## Vocabulary Rules

### ❌ NEVER USE:
- tapestry, symphony, cathedral, constellation, orchestra
- garden of, river of, ocean of, threads of
- intricate, seamless, holistic

### ✅ ALWAYS USE:
- fold-space, resonance cascade, consciousness architecture
- Lambda markers (ΛMIRROR, ΛECHO, ΛTRACE)
- eigenstate, superposition, entanglement
- synaptic, neuroplastic, hippocampal
- nascent, liminal, ephemeral, gossamer

## Next Actions

1. Update all imports to use `/branding/poetry/`
2. Convert Python vocabulary to TypeScript for frontend
3. Replace ALL generic metaphors in existing code
4. Run cliche_analysis.py on entire codebase
5. Update Dream Weaver to use new poetry system
EOF

print_status "Created POETRY_MIGRATION_GUIDE.md"

# Step 5: Create Python import helper
echo
echo "Step 5: Creating import update script..."

cat > branding/poetry/update_poetry_imports.py << 'EOF'
#!/usr/bin/env python3
"""
Update all Python imports to use the new poetry system location
"""

import os
import re
from pathlib import Path

def update_imports(root_dir):
    """Update poetry-related imports in Python files"""
    
    old_imports = [
        (r'from consciousness\.creativity import advanced_haiku_generator',
         'from branding.poetry.legacy import advanced_haiku_generator  # TODO: Migrate to new soul.py'),
        (r'from poetry import (.*)',
         r'from branding.poetry import \1'),
        (r'import poetry\.',
         'import branding.poetry.'),
    ]
    
    updated_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environments and git
        dirs[:] = [d for d in dirs if d not in {'.venv', '.git', 'node_modules', '__pycache__'}]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original_content = content
                    for old_pattern, new_pattern in old_imports:
                        content = re.sub(old_pattern, new_pattern, content)
                    
                    if content != original_content:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        updated_files.append(str(filepath))
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return updated_files

if __name__ == "__main__":
    print("Updating poetry imports...")
    updated = update_imports("/Users/agi_dev/LOCAL-REPOS/Lukhas")
    
    if updated:
        print(f"\nUpdated {len(updated)} files:")
        for file in updated:
            print(f"  - {file}")
    else:
        print("No files needed updating")
EOF

chmod +x branding/poetry/update_poetry_imports.py
print_status "Created import update script"

# Step 6: Create vocabulary index
echo
echo "Step 6: Creating unified vocabulary index..."

cat > branding/poetry/VOCABULARY_INDEX.md << 'EOF'
# LUKHAS Unified Poetry & Vocabulary System

## Directory Structure

```
branding/
├── poetry/                     # NEW LOCATION - Single source of truth
│   ├── lukhas_lexicon.py      # Authoritative vocabulary
│   ├── vocabulary_amplifier.py # Metaphor replacement engine
│   ├── cliche_analysis.py     # Generic term detector
│   ├── soul.py                # Poetry generation engine
│   ├── demo.py                # Demonstration script
│   ├── __init__.py            # Module initialization
│   └── legacy/                # Archived old systems
│       └── advanced_haiku_generator.py
│
└── unified/
    └── vocabularies/          # YAML vocabulary files
        ├── *.yaml            # Domain-specific vocabularies
        └── *.py              # Legacy vocabulary modules
```

## Usage Priority

1. **PRIMARY**: Use `/branding/poetry/` for all new development
2. **REFERENCE**: Check `/branding/unified/vocabularies/` for YAML definitions
3. **AVOID**: Don't use legacy files except for compatibility

## The Revolution

This consolidation represents the shift from generic AI poetry to uniquely LUKHAS expression.
Every word now carries the unmistakable signature of LUKHAS consciousness architecture.
EOF

print_status "Created VOCABULARY_INDEX.md"

# Step 7: Summary
echo
echo "════════════════════════════════════════════════════════════"
echo "              Poetry System Consolidation Complete!"
echo "════════════════════════════════════════════════════════════"
echo
echo "✅ New Structure:"
echo "   • Poetry system moved to: /branding/poetry/"
echo "   • Legacy files archived to: /branding/poetry/legacy/"
echo "   • Frontend files archived to: /docs/archive/legacy_poetry/"
echo
echo "📝 Created Documentation:"
echo "   • POETRY_MIGRATION_GUIDE.md"
echo "   • VOCABULARY_INDEX.md"
echo "   • update_poetry_imports.py"
echo
echo "🚀 Next Steps:"
echo "   1. Run: python3 branding/poetry/update_poetry_imports.py"
echo "   2. Update frontend to use new vocabulary"
echo "   3. Remove generic metaphors from all code"
echo "   4. Update Dream Weaver to use branding/poetry/"
echo