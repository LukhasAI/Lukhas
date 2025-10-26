#!/usr/bin/env bash
#
# Config Merge Validator
# Validates configs/ → config/ merge safety
#
# Usage:
#   bash scripts/consolidation/validate_config_merge.sh

set -euo pipefail

echo "========================================"
echo "Config Merge Validation"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Check if directories exist
if [ ! -d "config" ]; then
    echo -e "${RED}❌ ERROR: config/ directory not found${NC}"
    exit 1
fi

if [ ! -d "configs" ]; then
    echo -e "${YELLOW}⚠️  WARNING: configs/ directory not found (may already be merged)${NC}"
    echo "    If merge already complete, this is OK"
    echo ""
    exit 0
fi

echo "1. Checking for filename collisions..."
echo "========================================"

COLLISION_COUNT=0
while IFS= read -r file; do
    rel_path="${file#configs/}"
    if [ -f "config/$rel_path" ]; then
        echo -e "${RED}❌ COLLISION: $rel_path${NC}"
        echo "   - configs/$rel_path"
        echo "   - config/$rel_path"
        ((COLLISION_COUNT++))
        ((ERRORS++))
    fi
done < <(find configs -type f)

if [ $COLLISION_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ No filename collisions detected${NC}"
else
    echo -e "${RED}❌ Found $COLLISION_COUNT collision(s) - manual review required${NC}"
fi
echo ""

echo "2. Validating YAML files..."
echo "========================================"

YAML_ERRORS=0
while IFS= read -r file; do
    if ! python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        echo -e "${RED}❌ Invalid YAML: $file${NC}"
        ((YAML_ERRORS++))
        ((ERRORS++))
    fi
done < <(find configs config -name "*.yaml" -o -name "*.yml" 2>/dev/null)

if [ $YAML_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All YAML files valid${NC}"
else
    echo -e "${RED}❌ Found $YAML_ERRORS invalid YAML file(s)${NC}"
fi
echo ""

echo "3. Validating JSON files..."
echo "========================================"

JSON_ERRORS=0
while IFS= read -r file; do
    if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON: $file${NC}"
        ((JSON_ERRORS++))
        ((ERRORS++))
    fi
done < <(find configs config -name "*.json" 2>/dev/null)

if [ $JSON_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All JSON files valid${NC}"
else
    echo -e "${RED}❌ Found $JSON_ERRORS invalid JSON file(s)${NC}"
fi
echo ""

echo "4. Checking for references to configs/..."
echo "========================================"

REF_COUNT=0
while IFS= read -r ref; do
    echo -e "${YELLOW}⚠️  Reference found: $ref${NC}"
    ((REF_COUNT++))
    ((WARNINGS++))
done < <(grep -r "configs/" --include="*.py" --include="*.yaml" --include="*.sh" --include="*.json" . 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v ".venv" | head -20)

if [ $REF_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ No code references to configs/ found${NC}"
else
    echo -e "${YELLOW}⚠️  Found $REF_COUNT reference(s) - will need updating after merge${NC}"
fi
echo ""

echo "5. Creating merge preview..."
echo "========================================"

PREVIEW_DIR="/tmp/config_merge_preview_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$PREVIEW_DIR"

echo "Copying files to $PREVIEW_DIR..."
cp -r config/* "$PREVIEW_DIR/" 2>/dev/null || true
cp -r configs/* "$PREVIEW_DIR/" 2>/dev/null || true

PREVIEW_FILE_COUNT=$(find "$PREVIEW_DIR" -type f | wc -l | tr -d ' ')
echo -e "${GREEN}✅ Preview created with $PREVIEW_FILE_COUNT files${NC}"
echo "   Location: $PREVIEW_DIR"
echo ""

echo "6. Size comparison..."
echo "========================================"

CONFIG_SIZE=$(du -sh config/ 2>/dev/null | awk '{print $1}')
CONFIGS_SIZE=$(du -sh configs/ 2>/dev/null | awk '{print $1}')
PREVIEW_SIZE=$(du -sh "$PREVIEW_DIR" 2>/dev/null | awk '{print $1}')

echo "config/:  $CONFIG_SIZE"
echo "configs/: $CONFIGS_SIZE"
echo "Merged:   $PREVIEW_SIZE"
echo ""

echo "========================================"
echo "Summary"
echo "========================================"
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ VALIDATION FAILED - Do not proceed with merge${NC}"
    echo ""
    echo "Actions required:"
    echo "1. Resolve filename collisions"
    echo "2. Fix invalid YAML/JSON files"
    echo "3. Re-run this script"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNINGS DETECTED - Proceed with caution${NC}"
    echo ""
    echo "Actions recommended:"
    echo "1. Review merge preview at: $PREVIEW_DIR"
    echo "2. Update code references to configs/"
    echo "3. Test configuration loading after merge"
    exit 0
else
    echo -e "${GREEN}✅ VALIDATION PASSED - Safe to proceed with merge${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review merge preview at: $PREVIEW_DIR"
    echo "2. Run merge commands from consolidation plan"
    echo "3. Test with: make smoke"
    exit 0
fi
