#!/usr/bin/env bash
# Phase 2: Batch CI Optimization Script
# Applies standardized optimizations to all GitHub Actions workflows

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

WORKFLOWS_DIR=".github/workflows"
DRY_RUN="${DRY_RUN:-false}"
BACKUP_DIR=".github/workflows_backup_$(date +%Y%m%d_%H%M%S)"

echo "=== Phase 2: Batch CI Optimization ==="
echo "Mode: $([ "$DRY_RUN" = "true" ] && echo "DRY RUN" || echo "LIVE")"
echo "Workflows directory: $WORKFLOWS_DIR"
echo ""

# Create backup
if [ "$DRY_RUN" = "false" ]; then
    echo "📦 Creating backup..."
    mkdir -p "$BACKUP_DIR"
    cp "$WORKFLOWS_DIR"/*.yml "$BACKUP_DIR/" 2>/dev/null || true
    echo "✅ Backup created at $BACKUP_DIR"
    echo ""
fi

# Workflows missing concurrency controls
WORKFLOWS_NEEDING_CONCURRENCY=(
    "api_drift_check.yml"
    "canary-deployment.yml"
    "dependency-check.yml"
    "label-automation.yml"
    "license-check.yml"
    "lint-ratchet.yml"
    "log-forwarding.yml"
    "pr-approval-check.yml"
    "reasoning-lab-safety.yml"
    "sbom-generation.yml"
    "secret-scan.yml"
    "slsa-attest.yml"
    "slsa_provenance.yml"
    "workflow-security-scan.yml"
)

echo "📊 Processing ${#WORKFLOWS_NEEDING_CONCURRENCY[@]} workflows..."
echo ""

for workflow in "${WORKFLOWS_NEEDING_CONCURRENCY[@]}"; do
    file="$WORKFLOWS_DIR/$workflow"

    if [ ! -f "$file" ]; then
        echo "⚠️  Skipping $workflow (not found)"
        continue
    fi

    echo "🔧 Processing: $workflow"

    # Check if already has concurrency
    if grep -q "concurrency:" "$file"; then
        echo "  ✅ Already has concurrency controls"
        continue
    fi

    # Add concurrency block after 'on:' section
    if [ "$DRY_RUN" = "false" ]; then
        # Create temp file with concurrency added
        python3 - <<'PYTHON' "$file"
import sys
import yaml

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    content = f.read()

# Parse YAML
try:
    data = yaml.safe_load(content)
except Exception as e:
    print(f"  ❌ YAML parse error: {e}")
    sys.exit(0)

# Check if already has concurrency
if 'concurrency' in data:
    print("  ✅ Already has concurrency")
    sys.exit(0)

# Find position to insert concurrency (after 'on:' section)
lines = content.split('\n')
insert_pos = -1

for i, line in enumerate(lines):
    if line.startswith('on:'):
        # Find the end of the 'on:' block
        indent_level = len(line) - len(line.lstrip())
        for j in range(i+1, len(lines)):
            if lines[j].strip() and not lines[j].startswith(' '):
                insert_pos = j
                break
            elif lines[j].strip() and lines[j].startswith(' ') and len(lines[j]) - len(lines[j].lstrip()) <= indent_level:
                continue
            elif lines[j].strip() == '':
                continue
            elif j < len(lines) - 1 and not lines[j].startswith('  '):
                insert_pos = j
                break
        break

if insert_pos == -1:
    print("  ⚠️  Could not find insertion point")
    sys.exit(0)

# Insert concurrency block
concurrency_block = [
    "",
    "concurrency:",
    "  group: ${{ github.workflow }}-${{ github.ref }}",
    "  cancel-in-progress: true",
]

new_lines = lines[:insert_pos] + concurrency_block + lines[insert_pos:]
new_content = '\n'.join(new_lines)

# Validate YAML
try:
    yaml.safe_load(new_content)
except Exception as e:
    print(f"  ❌ Validation failed: {e}")
    sys.exit(0)

# Write back
with open(file_path, 'w') as f:
    f.write(new_content)

print("  ✅ Added concurrency controls")
PYTHON
    else
        echo "  📝 Would add concurrency controls (dry run)"
    fi

    echo ""
done

# Summary
echo "=== Summary ==="
if [ "$DRY_RUN" = "true" ]; then
    echo "Dry run complete. Set DRY_RUN=false to apply changes."
else
    echo "✅ Batch optimization complete!"
    echo "📦 Backup saved at: $BACKUP_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git diff .github/workflows/"
    echo "2. Validate workflows: for f in .github/workflows/*.yml; do python3 -c \"import yaml; yaml.safe_load(open('\$f'))\" && echo \"✅ \$f\" || echo \"❌ \$f\"; done"
    echo "3. Commit changes: git add .github/workflows/ && git commit -m 'chore(ci): Phase 2 batch optimization'"
fi
