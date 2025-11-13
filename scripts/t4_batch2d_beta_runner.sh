#!/usr/bin/env bash
set -euo pipefail

# T4 Batch 2D-Beta Runner: Convert try/except ImportError to importlib.util.find_spec
# Usage: 
#   ./scripts/t4_batch2d_beta_runner.sh               # dry-run
#   ./scripts/t4_batch2d_beta_runner.sh --apply      # apply changes

FILES_LIST=${1:-/tmp/t4_batch2d_top20.txt}
DRY_RUN=true
APPLY=false

# if user passed --apply, enable apply
for arg in "$@"; do
  if [[ "$arg" == "--apply" ]]; then
    APPLY=true
    DRY_RUN=false
  fi
done

echo "🔍 T4 Batch 2D-Beta: Converting try/except ImportError patterns"
echo ""

# gather files from list
if [[ ! -f "$FILES_LIST" ]]; then
  echo "❌ Error: File list not found: $FILES_LIST"
  echo "Run: ./scripts/t4_batch2d_runner.sh first to generate candidates"
  exit 1
fi

FILES=()
while IFS= read -r f; do 
  if [[ -f "$f" ]]; then
    FILES+=("$f")
  fi
done < "$FILES_LIST"

echo "📋 Total candidates from list: ${#FILES[@]}"

# Filter to those containing try: in first 120 lines (import region)
TRY_FILES=()
for f in "${FILES[@]}"; do
  if head -n 120 "$f" 2>/dev/null | grep -q "try:"; then
    TRY_FILES+=("$f")
  fi
done

echo "✅ Files with try-except in import region: ${#TRY_FILES[@]}"
echo ""

if [[ ${#TRY_FILES[@]} -eq 0 ]]; then
  echo "No try-except files to process. Exiting."
  exit 0
fi

# Create backup directory
mkdir -p codemod_backups

# Back up files
echo "💾 Creating backups..."
for f in "${TRY_FILES[@]}"; do
  BASENAME=$(basename "$f")
  cp "$f" "codemod_backups/${BASENAME}.bak.$(date +%s)"
done
echo "✅ Backed up ${#TRY_FILES[@]} files to codemod_backups/"
echo ""

# Run codemod dry-run producing diffs
echo "🔬 Running LibCST codemod (dry-run mode)..."
python3 tools/ci/codemods/convert_try_except_imports.py \
  --files "${TRY_FILES[@]}" \
  --dry-run > /tmp/t4_batch2d_beta_codemod_results.json 2>&1 || {
    echo "⚠️  Codemod had issues, checking results..."
  }

# Show summary of changes
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Codemod Results Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 - <<'PY'
import json
import sys

try:
    d = json.load(open('/tmp/t4_batch2d_beta_codemod_results.json'))
except Exception as e:
    print(f"Error loading results: {e}")
    sys.exit(1)

changed_count = 0
no_change_count = 0
error_count = 0

for k, v in d.items():
    filename = k.split('/')[-1]
    if 'ERROR' in str(v.get('output', '')):
        print(f"❌ ERROR: {filename}")
        error_count += 1
    elif v['changed']:
        print(f"✅ CHANGED: {filename}")
        changed_count += 1
    else:
        print(f"⚪ NO CHANGE: {filename}")
        no_change_count += 1

print(f"\n📈 Summary: {changed_count} changed, {no_change_count} unchanged, {error_count} errors")
PY

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show first few diffs for review
echo "🔍 Sample diffs (first 100 lines):"
echo ""
cat /tmp/t4_batch2d_beta_codemod_results.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for k, v in list(d.items())[:3]:  # first 3 files
    if v['changed'] and v['output'] and 'ERROR' not in v['output']:
        print(f'=== {k.split(\"/\")[-1]} ===')
        lines = v['output'].split('\\n')[:40]
        print('\\n'.join(lines))
        print()
" || echo "No diffs to show"

# If applying
if [ "$APPLY" = true ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "⚡ APPLYING TRANSFORMATIONS"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Apply codemod
  echo "🔧 Applying codemod to files..."
  python3 tools/ci/codemods/convert_try_except_imports.py --files "${TRY_FILES[@]}"
  
  # Run ruff to clean up
  echo "🧹 Running ruff cleanup..."
  python3 -m ruff check --fix --select F401 "${TRY_FILES[@]}" || true
  
  # Run autoflake if available
  if command -v autoflake &> /dev/null; then
    echo "🧹 Running autoflake cleanup..."
    autoflake --in-place --remove-all-unused-imports --remove-unused-variables "${TRY_FILES[@]}" || true
  fi
  
  # Verify syntax
  echo "✔️  Verifying Python syntax..."
  python3 -m py_compile "${TRY_FILES[@]}" || {
    echo "❌ Syntax errors detected! Rolling back..."
    for f in "${TRY_FILES[@]}"; do
      BASENAME=$(basename "$f")
      LATEST_BACKUP=$(ls -t codemod_backups/${BASENAME}.bak.* 2>/dev/null | head -1)
      if [[ -f "$LATEST_BACKUP" ]]; then
        cp "$LATEST_BACKUP" "$f"
        echo "  Restored: $f"
      fi
    done
    exit 1
  }
  
  # Check for remaining F401s
  echo "🔍 Checking F401 status..."
  REMAINING=$(python3 -m ruff check --select F401 "${TRY_FILES[@]}" 2>&1 | grep -c "F401" || echo "0")
  echo "  Remaining F401 errors in modified files: $REMAINING"
  
  # Git operations
  echo ""
  echo "📦 Committing changes..."
  git add -A "${TRY_FILES[@]}"
  git commit -m "fix(t4): Batch2D-Beta - Convert try/except imports to importlib.util.find_spec

Applied LibCST codemod to convert optional import patterns:
- try/except ImportError → if importlib.util.find_spec()
- Conservative transformation: only simple patterns in import region
- Files modified: ${#TRY_FILES[@]}

Safety verification:
✅ All files compile successfully
✅ Ruff cleanup applied
✅ Backups created in codemod_backups/

Part of: Batch 2D systematic cleanup (try-except pattern conversions)
Strategy: Conservative AST transformation with manual review"
  
  echo "📤 Pushing to remote..."
  git push -u origin HEAD || {
    echo "⚠️  Push failed, but changes are committed locally"
  }
  
  echo "🎯 Creating draft PR..."
  gh pr create \
    --title "fix(t4): Batch2D-Beta - Convert try-except imports (${#TRY_FILES[@]} files)" \
    --body "## Summary
Applied LibCST codemod to convert try/except ImportError patterns to importlib.util.find_spec guards.

## Pattern Conversion
\`\`\`python
# Before
try:
    import optional_module
except ImportError:
    optional_module = None

# After
import importlib.util
if importlib.util.find_spec('optional_module'):
    import optional_module
else:
    optional_module = None
\`\`\`

## Files Modified
${#TRY_FILES[@]} files with try-except patterns in import region

## Safety Verification
✅ Conservative AST transformation (only simple patterns)
✅ All files compile successfully
✅ Ruff cleanup applied
✅ Backups available in codemod_backups/

## Review Required
⚠️  Manual testing of optional dependency paths recommended
⚠️  Check imports are still functional in test environment

Part of T4 Batch 2D-Beta: systematic try-except pattern cleanup.
Ref: LibCST codemod with dry-run validation" \
    --draft \
    --label "t4/codemod" || {
      echo "⚠️  PR creation failed, but changes are pushed"
    }
  
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Batch 2D-Beta: COMPLETE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
else
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Dry-run complete"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📋 Review results:"
  echo "  - Full results: /tmp/t4_batch2d_beta_codemod_results.json"
  echo "  - Backups created: codemod_backups/"
  echo ""
  echo "🚀 To apply changes, run:"
  echo "  ./scripts/t4_batch2d_beta_runner.sh --apply"
  echo ""
fi
