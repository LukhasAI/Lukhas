#!/bin/bash
# CI Trinity Import Warning System
# Warns about deprecated trinity imports during Constellation migration

set -e

echo "🔍 Checking for deprecated Trinity imports..."

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

DEPRECATED_IMPORTS=0
WARNING_COUNT=0

# Check for direct branding.trinity imports (deprecated)
echo -e "${YELLOW}Checking for deprecated branding.trinity imports...${NC}"
if grep -r "from branding.trinity import" --include="*.py" . 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Found deprecated branding.trinity imports${NC}"
    DEPRECATED_IMPORTS=$((DEPRECATED_IMPORTS + 1))
fi

if grep -r "import branding.trinity" --include="*.py" . 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Found deprecated branding.trinity imports${NC}"
    DEPRECATED_IMPORTS=$((DEPRECATED_IMPORTS + 1))
fi

# Check for old Trinity class references that should use Triad
echo -e "${YELLOW}Checking for Trinity class references...${NC}"
TRINITY_CLASSES=$(grep -r "class.*Trinity" --include="*.py" . 2>/dev/null | grep -v "Triad" | wc -l)
if [ "$TRINITY_CLASSES" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $TRINITY_CLASSES Trinity class definitions (consider Triad)${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
fi

# Check for trinity_ function patterns that could be triad_
echo -e "${YELLOW}Checking for trinity_ function patterns...${NC}"
TRINITY_FUNCTIONS=$(grep -r "def.*trinity_" --include="*.py" . 2>/dev/null | wc -l)
if [ "$TRINITY_FUNCTIONS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $TRINITY_FUNCTIONS trinity_ function definitions (consider triad_)${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
fi

# Check for TODO comments that need Constellation tags
echo -e "${YELLOW}Checking for TODO comments needing Constellation tags...${NC}"
UNTAGGED_TODOS=$(grep -r "# TODO.*[⚛️🧠🛡️]" --include="*.py" . 2>/dev/null | grep -v "CONSTELLATION:" | wc -l)
if [ "$UNTAGGED_TODOS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $UNTAGGED_TODOS Trinity TODOs without Constellation tags${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
fi

# Summary
echo -e "\n📊 Migration Status Summary:"
echo -e "- Deprecated imports: ${DEPRECATED_IMPORTS}"
echo -e "- Conversion warnings: ${WARNING_COUNT}"

if [ "$DEPRECATED_IMPORTS" -eq 0 ] && [ "$WARNING_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! No deprecated patterns found.${NC}"
    exit 0
elif [ "$DEPRECATED_IMPORTS" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Migration progressing: ${WARNING_COUNT} items to convert${NC}"
    exit 0
else
    echo -e "${RED}❌ Deprecated imports found: ${DEPRECATED_IMPORTS}${NC}"
    echo -e "${YELLOW}Please update deprecated imports to use constellation.triad${NC}"
    echo -e "${YELLOW}Migration guide: see PUBLIC_API.md${NC}"
    exit 1
fi
