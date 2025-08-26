#!/bin/bash

# 🎯 LUKHAS Smart File Organization Demo
# Shows how the semantic analysis works

echo -e "\033[0;35m"
cat << "EOF"
    ╔══════════════════════════════════════════════════════╗
    ║         🧠 Smart File Organization Demo 🧠            ║
    ║              Trinity Framework: ⚛️🧠🛡️                ║
    ╚══════════════════════════════════════════════════════╝
EOF
echo -e "\033[0m"
echo

echo -e "\033[1;37m🔍 Semantic Analysis Preview:\033[0m"
echo

# Sample files from your root directory
files=(
    "AGENTS.md"
    "CLAUDE.md"
    "COMPREHENSIVE_CODEBASE_ASSESSMENT.md"
    "MATADA_PLAN.md"
    "README.md"
    "matada_node_v1.json"
    "lukhas.log"
    ".coverage"
)

categories=(
    "AGENTS (9/10) → docs/agents 🤖"
    "AGENTS (7/10) → docs/agents 🤖"
    "REPORTS (6/10) → docs/reports 📊"
    "MATADA (10/10) → MATADA 🧠"
    "ARCHITECTURE (8/10) → docs/architecture 🏗️"
    "API (6/10) → docs/api 📡"
    "CLEANUP (9/10) → REMOVE 🗑️"
    "CLEANUP (9/10) → REMOVE 🗑️"
)

echo -e "\033[1;37m📄 Example Analysis Results:\033[0m"
echo -e "\033[1;37m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"

for i in "${!files[@]}"; do
    file="${files[$i]}"
    category="${categories[$i]}"

    echo -e "\033[0;36m📄 ${file}\033[0m"
    echo -e "   🎯 ${category}"
    echo
done

echo -e "\033[1;37m🎮 Interactive Features:\033[0m"
echo -e "  \033[0;32m[y]\033[0m Yes, move to suggested location"
echo -e "  \033[1;33m[s]\033[0m Skip this file"
echo -e "  \033[0;34m[c]\033[0m Choose different destination"
echo -e "  \033[0;31m[q]\033[0m Quit organization"
echo

echo -e "\033[1;37m🎯 Smart Features:\033[0m"
echo "  • Semantic pattern matching with confidence scores"
echo "  • Interactive approval for each file"
echo "  • Custom destination selection"
echo "  • Progress indicators and colorful output"
echo "  • Safe operation - no files moved without approval"
echo

echo -e "\033[0;35m🚀 To run the full interactive version:\033[0m"
echo -e "\033[1;37m   ./scripts/organize_root_files.sh\033[0m"
echo

echo -e "\033[0;35m✨ The script will analyze all files and ask for your approval before moving anything!\033[0m"
