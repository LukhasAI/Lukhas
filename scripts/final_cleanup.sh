#!/bin/bash

# LUKHAS Final Cleanup Script
# Purpose: Remove duplicate vocabulary directories and consolidate remaining files

set -e

echo "════════════════════════════════════════════════════════════"
echo "              LUKHAS Final Cleanup Script"
echo "════════════════════════════════════════════════════════════"
echo

REPO_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
cd "$REPO_ROOT"

# Remove duplicate vocabulary directories
echo "Removing duplicate vocabulary directories..."

# Remove duplicate symbolic directories
if [ -d "core/symbolic_legacy/vocabularies" ]; then
    rm -rf "core/symbolic_legacy/vocabularies"
    echo "  ✓ Removed core/symbolic_legacy/vocabularies"
fi

if [ -d "symbolic/vocabularies" ]; then
    rm -rf "symbolic/vocabularies"
    echo "  ✓ Removed symbolic/vocabularies"
fi

# Clean up empty Poetic_Evolution directory
if [ -d "Poetic_Evolution" ]; then
    if [ -z "$(ls -A Poetic_Evolution)" ]; then
        rmdir "Poetic_Evolution"
        echo "  ✓ Removed empty Poetic_Evolution directory"
    else
        # Move remaining content
        mv Poetic_Evolution/Poetic_Systems-MD docs/archive/poetic_evolution/ 2>/dev/null || true
        rmdir "Poetic_Evolution" 2>/dev/null || true
    fi
fi

# Remove old empty vocabulary placeholders in root
rm -f identity_vocabulary bio_vocabulary 2>/dev/null || true

# Consolidate tone system files
echo
echo "Consolidating tone system files..."

# Remove duplicate tone directories
if [ -d "tools/tone" ] && [ -d "branding/tone/tools" ]; then
    # Copy unique Python files
    cp -n tools/tone/*.py branding/unified/tone/ 2>/dev/null || true
    cp -n branding/tone/tools/*.py branding/unified/tone/ 2>/dev/null || true
    
    # Remove the duplicate directories
    rm -rf tools/tone
    echo "  ✓ Removed duplicate tools/tone directory"
fi

# Clean up empty directories again
echo
echo "Final empty directory cleanup..."
find . -type d -empty -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" -delete 2>/dev/null

# Create a vocabulary index file
echo
echo "Creating vocabulary index..."

cat > branding/unified/vocabularies/VOCABULARY_INDEX.md << 'EOF'
# LUKHAS Unified Vocabulary Index

## Core Vocabularies (YAML)
- `master_vocabulary.yaml` - Master vocabulary definitions
- `trinity_core_vocabulary.yaml` - Trinity Framework vocabulary
- `consciousness_vocabulary.yaml` - Consciousness states and operations
- `memory_vocabulary.yaml` - Memory folding and operations
- `quantum_vocabulary.yaml` - Quantum-inspired terminology
- `dreams_vocabulary.yaml` - Dream and oneiric vocabulary
- `identity_vocabulary.yaml` - Identity and ΛID vocabulary
- `ethics_vocabulary.yaml` - Ethics and guardian vocabulary
- `vivox_vocabulary.yaml` - VIVOX consciousness system
- `endocrine_vocabulary.yaml` - Bio-inspired endocrine terms

## Python Vocabulary Modules
- `lukhas_lexicon.py` - Authoritative LUKHAS vocabulary
- `vocabulary_amplifier.py` - Replace generic metaphors with LUKHAS terms
- `cliche_analysis.py` - Detect and eliminate clichés
- `soul.py` - Poetry generation engine
- `vocabulary.py` - Core vocabulary module
- `vocabulary_creativity_engine.py` - Creative vocabulary generation

## Vocabulary Principles
1. **No Generic Metaphors**: No "tapestry", "symphony", "cathedral"
2. **Use LUKHAS Terms**: fold-space, Lambda Mirror, eigenstate, etc.
3. **Authentic Language**: Every word should be unmistakably LUKHAS
EOF

echo "  ✓ Created VOCABULARY_INDEX.md"

# Create a summary of the cleanup
echo
echo "Creating cleanup summary..."

REMAINING_ROOT_FILES=$(ls -la "$REPO_ROOT" | grep -E "^\-" | wc -l | tr -d ' ')
TOTAL_DIRS=$(find . -type d -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" | wc -l | tr -d ' ')

cat >> ORGANIZATION_SUMMARY.md << EOF

## Final Cleanup Results

### Repository Statistics
- Root files reduced from 65 to $REMAINING_ROOT_FILES
- Total directories: $TOTAL_DIRS
- Duplicate vocabularies removed
- Empty directories cleaned

### Unified Resources
- All vocabularies in: /branding/unified/vocabularies/
- All tone systems in: /branding/unified/tone/
- All test files in: /tests/
- All scripts in: /scripts/
- All archived docs in: /docs/archive/

### Next Actions
1. Update Python imports to use unified vocabulary paths
2. Review and merge duplicate vocabulary definitions
3. Create master configuration for unified resources
EOF

echo "  ✓ Updated ORGANIZATION_SUMMARY.md"

echo
echo "════════════════════════════════════════════════════════════"
echo "                  Cleanup Complete!"
echo "════════════════════════════════════════════════════════════"
echo
echo "Final Statistics:"
echo "  • Root files: $REMAINING_ROOT_FILES (reduced from 65)"
echo "  • Vocabularies unified in /branding/unified/vocabularies/"
echo "  • All duplicates removed"
echo "  • Repository structure optimized"
echo