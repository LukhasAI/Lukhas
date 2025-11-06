#!/bin/bash
# Codex Readiness Verification Script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verifying Codex Readiness..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check documentation files
echo "📋 Checking Documentation Files..."
for file in CODEX_INITIATION_PROMPT.md ARTIFACTS_LOCATIONS.md CODEX_QUICK_START.txt CODEX_PARALLEL_SETUP.md; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file MISSING"
    exit 1
  fi
done
echo

# Check artifacts
echo "�� Checking Artifacts..."
for file in artifacts/todo_to_issue_map.json artifacts/replace_todos_log.json; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file MISSING"
    exit 1
  fi
done
echo

# Check scripts
echo "🔧 Checking Scripts..."
if [ -f scripts/todo_migration/replace_todos_with_issues.py ]; then
  echo "  ✅ scripts/todo_migration/replace_todos_with_issues.py"
else
  echo "  ❌ scripts/todo_migration/replace_todos_with_issues.py MISSING"
  exit 1
fi
echo

# Validate JSON files
echo "🧪 Validating JSON Files..."
if python3 -c "import json; json.load(open('artifacts/todo_to_issue_map.json'))" 2>/dev/null; then
  MAPPINGS=$(python3 -c "import json; print(len(json.load(open('artifacts/todo_to_issue_map.json'))))")
  echo "  ✅ todo_to_issue_map.json valid ($MAPPINGS mappings)"
else
  echo "  ❌ todo_to_issue_map.json INVALID"
  exit 1
fi

if python3 -c "import json; json.load(open('artifacts/replace_todos_log.json'))" 2>/dev/null; then
  FILES=$(python3 -c "import json; print(len(json.load(open('artifacts/replace_todos_log.json'))))")
  echo "  ✅ replace_todos_log.json valid ($FILES files)"
else
  echo "  ❌ replace_todos_log.json INVALID"
  exit 1
fi
echo

# Check Python environment
echo "🐍 Checking Python Environment..."
if [ -d .venv311 ]; then
  echo "  ✅ .venv311 exists"
else
  echo "  ⚠️  .venv311 not found (may need to activate)"
fi
echo

# Check git status
echo "📦 Checking Git Status..."
if git diff --quiet && git diff --cached --quiet; then
  echo "  ✅ Working directory clean"
else
  echo "  ⚠️  Uncommitted changes present"
fi

BRANCH=$(git branch --show-current)
echo "  📍 Current branch: $BRANCH"
echo

# Check GitHub CLI
echo "🔐 Checking GitHub CLI..."
if command -v gh &> /dev/null; then
  AUTH_STATUS=$(gh auth status 2>&1 | grep "Logged in" || echo "Not logged in")
  echo "  ✅ gh CLI available"
  echo "  📍 $AUTH_STATUS"
else
  echo "  ❌ gh CLI not found"
  exit 1
fi
echo

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CODEX READY FOR SPAWN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "📋 Next Steps:"
echo "  1. Spawn Codex with: CODEX_INITIATION_PROMPT.md"
echo "  2. Codex will execute TODO replacement (1-2h)"
echo "  3. Expected result: 38 files, 78 issue links"
echo "  4. Cost: \$0 (no CI)"
echo
