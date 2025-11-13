#!/bin/bash
set -euo pipefail
echo "=== DREAM CONSOLIDATION MOVES (REVISED) ==="

# Create destination directories
mkdir -p labs/consciousness/dream/synthesis
mkdir -p labs/consciousness/dream/helpers
mkdir -p labs/consciousness/dream/results

# Phase 1: Move dream/ core to synthesis/
# (Preserve directory structure)
git mv dream labs/consciousness/dream/synthesis_temp

# Phase 2: Archive dreams/ (already archived in earlier session - skip if done)
# mkdir -p archive/dreams_2025-10-26
# git mv dreams archive/dreams_2025-10-26/

# Phase 3: Move dreamweaver_helpers_bundle/ to helpers/
git mv dreamweaver_helpers_bundle labs/consciousness/dream/helpers_temp

# Phase 4: Rename temp directories
mv labs/consciousness/dream/synthesis_temp labs/consciousness/dream/synthesis
mv labs/consciousness/dream/helpers_temp labs/consciousness/dream/helpers

echo "=== MOVES COMPLETE ==="
echo "Next: Run 'make smoke && pytest tests/' to validate"
