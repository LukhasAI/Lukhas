#!/bin/bash
# extract_todos.sh - Extract and categorize TODOs from the LUKHAS codebase
# Uses standardized exclusions to avoid virtual environment contamination

set -e

# Load standardized exclusions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$PROJECT_ROOT/tools/search/standardized_exclusions.sh"

echo "🔍 Extracting TODOs from LUKHAS codebase..."
echo "📊 Using clean search (excluding .venv, cache, build directories)"

# Extract all TODOs with context
OUTPUT_FILE="$PROJECT_ROOT/TODO/raw_todos_$(date +%Y%m%d_%H%M%S).txt"

echo "📝 Extracting TODOs to: $OUTPUT_FILE"

# Extract TODOs with file, line number, and context
eval "grep -r -n \"TODO\" $ALL_EXCLUDE_GREP --include=\"*.py\" -A2 -B1" > "$OUTPUT_FILE" 2>/dev/null || true

# Filter out annotation TODOs (# noqa.*TODO)
grep -v "# noqa.*TODO" "$OUTPUT_FILE" > "${OUTPUT_FILE}.filtered" || true
mv "${OUTPUT_FILE}.filtered" "$OUTPUT_FILE"

# Count and summarize
TOTAL_TODOS=$(wc -l < "$OUTPUT_FILE" | xargs)
echo "✅ Extracted $TOTAL_TODOS TODO entries"

echo ""
echo "🎯 TODO Distribution Analysis:"

# Analyze by directory
echo ""
echo "📁 By Directory:"
grep -o "^\./[^/]*" "$OUTPUT_FILE" | sort | uniq -c | sort -nr | head -10

echo ""
echo "🧠 By Module Type:"
# Consciousness-related
CONSCIOUSNESS=$(grep -c -i "consciousness\|memory\|identity\|quantum\|bio" "$OUTPUT_FILE" || echo "0")
echo "  Consciousness/Memory/Identity: $CONSCIOUSNESS"

# Core infrastructure
CORE=$(grep -c -E "^\./core|^\./api|^\./lukhas" "$OUTPUT_FILE" || echo "0")
echo "  Core/API/Main: $CORE"

# Candidate modules
CANDIDATE=$(grep -c "^\./candidate" "$OUTPUT_FILE" || echo "0")
echo "  Candidate modules: $CANDIDATE"

# Tools and testing
TOOLS=$(grep -c -E "^\./tools|^\./tests" "$OUTPUT_FILE" || echo "0")
echo "  Tools/Testing: $TOOLS"

echo ""
echo "🏷️ Priority Keywords Analysis:"
CRITICAL=$(grep -c -i "critical\|security\|fix\|bug\|error\|fail\|corruption\|vulnerable" "$OUTPUT_FILE" || echo "0")
HIGH=$(grep -c -i "important\|performance\|optimize\|integration\|core\|essential" "$OUTPUT_FILE" || echo "0")
MED=$(grep -c -i "enhance\|improve\|feature\|document\|refactor" "$OUTPUT_FILE" || echo "0")
LOW=$(grep -c -i "cleanup\|style\|cosmetic\|nice.*to.*have\|minor" "$OUTPUT_FILE" || echo "0")

echo "  🚨 CRITICAL indicators: $CRITICAL"
echo "  ⭐ HIGH indicators: $HIGH"
echo "  📋 MED indicators: $MED"
echo "  🔧 LOW indicators: $LOW"

echo ""
echo "📋 Raw TODO file saved to: $OUTPUT_FILE"
echo "🔄 Next: Run categorize_todos.py to classify by priority"

echo ""
echo "📊 Sample TODOs:"
head -20 "$OUTPUT_FILE"