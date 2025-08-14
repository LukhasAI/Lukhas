#!/bin/bash

# 🛡️ LUKHAS Security Package Installer
# Convenient script for installing packages in the correct Python environment

echo "🧠 LUKHAS Python Environment Package Installer"
echo "⚛️ Using environment: .venv_test"
echo "🛡️ Installing packages with security focus..."

PYTHON_CMD="/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv_test/bin/python"
PIP_CMD="$PYTHON_CMD -m pip"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Current Python version:${NC}"
$PYTHON_CMD --version

echo -e "\n${BLUE}Current pip version:${NC}"
$PIP_CMD --version

# Install packages passed as arguments
if [ $# -eq 0 ]; then
    echo -e "\n${YELLOW}Usage: $0 package1 package2 ...${NC}"
    echo -e "Example: $0 'fastapi>=0.100.0' 'pydantic>=2.0.0'"
    exit 1
fi

echo -e "\n${BLUE}Installing packages:${NC}"
for package in "$@"; do
    echo -e "  ${GREEN}→${NC} $package"
done

$PIP_CMD install --upgrade "$@"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All packages installed successfully!${NC}"
    echo -e "\n${BLUE}Updated package versions:${NC}"
    for package in "$@"; do
        # Extract package name (before any version specifiers)
        pkg_name=$(echo "$package" | sed 's/[>=<].*//' | sed 's/[[].*$//')
        $PIP_CMD show "$pkg_name" 2>/dev/null | grep -E "^(Name|Version):" | tr '\n' ' ' && echo
    done
else
    echo -e "\n${YELLOW}⚠️ Some packages may have failed to install${NC}"
fi

echo -e "\n🎊 LUKHAS package installation complete!"
