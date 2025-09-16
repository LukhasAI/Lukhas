#!/bin/bash
# LUKHAS Context File Generation Script
# Creates vendor-neutral lukhas_context.md files alongside claude.me files
# Maintains Claude Desktop compatibility while adding vendor neutrality

set -e

echo "🤖 LUKHAS Context File Generation Script"
echo "========================================"
echo ""
echo "Purpose: Create vendor-neutral lukhas_context.md files alongside claude.me files"
echo "Strategy: Hybrid approach maintaining Claude compatibility + vendor neutrality"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
processed=0
created=0
skipped=0
errors=0

echo -e "${BLUE}Phase 1: Discovering claude.me files...${NC}"
claude_files=$(find . -name "claude.me" -type f | sort)
total_files=$(echo "$claude_files" | wc -l | tr -d ' ')

echo "Found $total_files claude.me files to process"
echo ""

echo -e "${BLUE}Phase 2: Creating lukhas_context.md files...${NC}"
echo ""

while IFS= read -r claude_file; do
    if [ -z "$claude_file" ]; then
        continue
    fi

    processed=$((processed + 1))
    dir=$(dirname "$claude_file")
    lukhas_file="$dir/lukhas_context.md"

    echo -n "[$processed/$total_files] Processing: $claude_file -> $lukhas_file ... "

    if [ -f "$lukhas_file" ]; then
        echo -e "${YELLOW}SKIPPED (exists)${NC}"
        skipped=$((skipped + 1))
    else
        if cp "$claude_file" "$lukhas_file"; then
            echo -e "${GREEN}CREATED${NC}"
            created=$((created + 1))
        else
            echo -e "${RED}ERROR${NC}"
            errors=$((errors + 1))
        fi
    fi
done <<< "$claude_files"

echo ""
echo -e "${BLUE}Phase 3: Adding vendor-neutral header to new files...${NC}"
echo ""

# Add header to distinguish lukhas_context.md files
header="# LUKHAS AI Context - Vendor-Neutral AI Guidance
*This file provides domain-specific context for any AI development tool*
*Also available as claude.me for Claude Desktop compatibility*

---

"

processed_headers=0
while IFS= read -r claude_file; do
    if [ -z "$claude_file" ]; then
        continue
    fi

    dir=$(dirname "$claude_file")
    lukhas_file="$dir/lukhas_context.md"

    if [ -f "$lukhas_file" ]; then
        # Check if header already exists
        if ! grep -q "LUKHAS AI Context - Vendor-Neutral AI Guidance" "$lukhas_file"; then
            echo -n "Adding header to: $lukhas_file ... "
            temp_file=$(mktemp)
            echo "$header" > "$temp_file"
            cat "$lukhas_file" >> "$temp_file"
            mv "$temp_file" "$lukhas_file"
            echo -e "${GREEN}DONE${NC}"
            processed_headers=$((processed_headers + 1))
        fi
    fi
done <<< "$claude_files"

echo ""
echo -e "${BLUE}Phase 4: Results Summary${NC}"
echo "========================="
echo "Total claude.me files found: $total_files"
echo "lukhas_context.md files created: $created"
echo "Files skipped (already exist): $skipped"
echo "Headers added: $processed_headers"
echo "Errors: $errors"
echo ""

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ SUCCESS: All lukhas_context.md files generated successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Update .github/copilot-instructions.md to reference both file types"
    echo "2. Configure other AI tools to read lukhas_context.md files"
    echo "3. Consider using lukhas_context.md for new context content"
    echo ""
    echo "Benefits achieved:"
    echo "✅ Vendor neutrality for any AI tool"
    echo "✅ Maintained Claude Desktop compatibility"
    echo "✅ Clear LUKHAS branding and ownership"
    echo "✅ Future-proof documentation strategy"
else
    echo -e "${RED}❌ ERRORS ENCOUNTERED: $errors files failed to process${NC}"
    echo "Please review and fix errors before proceeding."
    exit 1
fi
