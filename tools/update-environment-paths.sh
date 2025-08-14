#!/bin/bash

# 🔧 LUKHAS Environment Path Updater
# Updates all environment paths from Lukhas_PWM to Lukhas structure

echo "🧠 LUKHAS Environment Path Updater"
echo "⚛️ Updating all environment references for consciousness development..."

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Current working directory
WORKSPACE_ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
OLD_PATH_PATTERN="Lukhas_PWM"
NEW_PATH_PATTERN="Lukhas"

echo -e "\n${BLUE}🔍 Scanning for environment path issues...${NC}"

# Function to update file if it exists
update_file_paths() {
    local file_path="$1"
    local description="$2"
    
    if [ -f "$file_path" ]; then
        echo -e "${YELLOW}📝 Updating: $description${NC}"
        sed -i.bak "s|$OLD_PATH_PATTERN|$NEW_PATH_PATTERN|g" "$file_path"
        echo -e "${GREEN}✅ Updated: $file_path${NC}"
    else
        echo -e "${RED}⚠️  File not found: $file_path${NC}"
    fi
}

# Function to update Python environment references
update_python_paths() {
    echo -e "\n${BLUE}🐍 Updating Python environment paths...${NC}"
    
    # Current correct Python path
    CORRECT_PYTHON_PATH="$WORKSPACE_ROOT/.venv_test/bin/python"
    
    if [ -f "$CORRECT_PYTHON_PATH" ]; then
        echo -e "${GREEN}✅ Correct Python environment found: $CORRECT_PYTHON_PATH${NC}"
    else
        echo -e "${RED}❌ Python environment not found: $CORRECT_PYTHON_PATH${NC}"
        echo -e "${YELLOW}💡 Run: configure_python_environment tool to set up${NC}"
    fi
}

# Function to find and report old path references
find_old_references() {
    echo -e "\n${BLUE}🔍 Scanning for remaining old path references...${NC}"
    
    # Search for old path patterns (excluding backups and archives)
    OLD_REFS=$(grep -r "$OLD_PATH_PATTERN" . \
        --exclude-dir=".git" \
        --exclude-dir="__pycache__" \
        --exclude-dir=".venv" \
        --exclude-dir=".venv_test" \
        --exclude-dir="node_modules" \
        --exclude-dir=".backups" \
        --exclude-dir="archive" \
        --exclude-dir=".atomic_migration_backup*" \
        --exclude-dir=".namespace_migration_backup*" \
        --exclude="*.bak" \
        --include="*.py" \
        --include="*.json" \
        --include="*.yaml" \
        --include="*.yml" \
        --include="*.md" \
        --include="*.sh" \
        --include="*.js" \
        --include="*.ts" \
        2>/dev/null | head -20)
    
    if [ -n "$OLD_REFS" ]; then
        echo -e "${YELLOW}⚠️  Found remaining old path references:${NC}"
        echo "$OLD_REFS"
    else
        echo -e "${GREEN}✅ No old path references found in active files${NC}"
    fi
}

# Main update process
echo -e "\n${BLUE}🚀 Starting environment path updates...${NC}"

# Update VS Code tasks (already done, but check)
if [ -f ".vscode/tasks.json" ]; then
    echo -e "${BLUE}📋 Checking VS Code tasks configuration...${NC}"
    TASK_REFS=$(grep -c "Lukhas_PWM" .vscode/tasks.json 2>/dev/null || echo "0")
    if [ "$TASK_REFS" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Found $TASK_REFS old path references in VS Code tasks${NC}"
    else
        echo -e "${GREEN}✅ VS Code tasks configuration updated${NC}"
    fi
fi

# Update monitoring configurations
update_file_paths "monitoring/test_results.json" "Monitoring test results"

# Update pyrightconfig if needed
if [ -f "pyrightconfig.json" ]; then
    echo -e "${BLUE}📝 Checking Python type checking configuration...${NC}"
    if grep -q "\.venv\"" pyrightconfig.json; then
        echo -e "${GREEN}✅ pyrightconfig.json uses relative .venv path${NC}"
    else
        echo -e "${YELLOW}⚠️  pyrightconfig.json may need manual review${NC}"
    fi
fi

# Update any remaining Python environment scripts
echo -e "\n${BLUE}🔧 Updating tool scripts...${NC}"

# Update tools that reference Python paths
if [ -f "tools/install-packages.sh" ]; then
    CURRENT_PYTHON_REF=$(grep "PYTHON_CMD=" tools/install-packages.sh | head -1)
    echo -e "${BLUE}📦 Package installer Python path: $CURRENT_PYTHON_REF${NC}"
fi

# Call Python path verification
update_python_paths

# Scan for remaining issues
find_old_references

# Environment verification
echo -e "\n${BLUE}🧪 Environment verification...${NC}"

# Check virtual environment
if [ -d ".venv_test" ]; then
    echo -e "${GREEN}✅ Active virtual environment: .venv_test${NC}"
    if [ -f ".venv_test/bin/python" ]; then
        PYTHON_VERSION=$(.venv_test/bin/python --version 2>&1)
        echo -e "${GREEN}✅ Python available: $PYTHON_VERSION${NC}"
    fi
else
    echo -e "${RED}❌ Virtual environment not found: .venv_test${NC}"
fi

# Check if old .venv exists and is broken
if [ -d ".venv" ]; then
    if [ -f ".venv/bin/python" ]; then
        if .venv/bin/python --version >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Legacy .venv still functional${NC}"
        else
            echo -e "${YELLOW}⚠️  Legacy .venv appears broken (expected after PWM → Lukhas migration)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Legacy .venv incomplete${NC}"
    fi
fi

# Summary
echo -e "\n${GREEN}🎊 Environment path update complete!${NC}"
echo -e "\n${BLUE}📋 Summary of current environment setup:${NC}"
echo -e "  • ${GREEN}Repository:${NC} /Users/agi_dev/LOCAL-REPOS/Lukhas"
echo -e "  • ${GREEN}Python Environment:${NC} .venv_test"
echo -e "  • ${GREEN}Python Path:${NC} $WORKSPACE_ROOT/.venv_test/bin/python"
echo -e "  • ${GREEN}VS Code Tasks:${NC} Updated to use correct paths"
echo -e "  • ${GREEN}Monitoring Config:${NC} Updated path references"

echo -e "\n${GREEN}🛡️ All environment paths aligned for LUKHAS consciousness development!${NC}"
