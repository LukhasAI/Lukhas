#!/bin/bash

# 🧠 LUKHAS AI Smart File Organization System - FIXED VERSION
# Interactive semantic analysis with approval workflow
# Trinity Framework compliant: ⚛️🧠🛡️

set -euo pipefail

# Clean banner in your project's style (no broken colors!)
show_banner() {
    echo
    echo "══════════════════════════════════════════════════════════════════════════════════"
    echo "║ 🧠 LUKHAS AI - SMART FILE ORGANIZATION SYSTEM"
    echo "║ Interactive semantic analysis with confidence scoring"
    echo "║ Copyright (c) 2025 LUKHAS AI. All rights reserved."
    echo "╠══════════════════════════════════════════════════════════════════════════════════"
    echo "║ Trinity Framework: ⚛️🧠🛡️"
    echo "║ Version: 2.0.0 | Interactive Smart Analysis"
    echo "║ Authors: LUKHAS AI Engineering Team"
    echo "╚══════════════════════════════════════════════════════════════════════════════════"
    echo
}

# Simple explanation of how it works
explain_system() {
    echo "🎯 How This Smart Organization System Works:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "1️⃣  SCAN: Analyzes each file in your root directory"
    echo "2️⃣  PATTERN MATCH: Uses smart patterns to suggest destinations"
    echo "3️⃣  CONFIDENCE SCORE: Rates each suggestion from 1-10"
    echo "4️⃣  INTERACTIVE APPROVAL: Shows you each suggestion"
    echo "5️⃣  SAFE MOVE: Only moves files when you approve"
    echo
    echo "🛡️ Safety Features:"
    echo "   • Never moves files without your permission"
    echo "   • Creates directories as needed"
    echo "   • Shows exact destination before moving"
    echo "   • Skip/customize options for every file"
    echo
}

# Analyze current root directory (demo mode)
analyze_current_files() {
    echo "📊 Analysis of Your Current Root Directory:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    local file_count=0
    local high_confidence=0
    local suggestions_made=0

    # Check specific files we know about
    if [ -f "AGENTS.md" ]; then
        echo "📄 AGENTS.md"
        echo "   🎯 Pattern: Agent documentation → docs/agents/"
        echo "   📊 Confidence: 9/10 ⭐⭐⭐⭐⭐"
        echo "   ❓ Action: Would ask for your approval"
        echo
        ((file_count++))
        ((high_confidence++))
        ((suggestions_made++))
    fi

    if [ -f "CLAUDE.md" ]; then
        echo "📄 CLAUDE.md"
        echo "   🎯 Pattern: Claude documentation → docs/agents/"
        echo "   📊 Confidence: 8/10 ⭐⭐⭐⭐"
        echo "   ❓ Action: Would ask for your approval"
        echo
        ((file_count++))
        ((high_confidence++))
        ((suggestions_made++))
    fi

    if [ -f "matada_node_v1.json" ]; then
        echo "📄 matada_node_v1.json"
        echo "   🎯 Pattern: MATADA schema → MATADA/"
        echo "   📊 Confidence: 10/10 ⭐⭐⭐⭐⭐ (Perfect match!)"
        echo "   ❓ Action: Would ask for your approval"
        echo
        ((file_count++))
        ((high_confidence++))
        ((suggestions_made++))
    fi

    # Count all markdown files
    local md_count
    md_count=$(find . -maxdepth 1 -name "*.md" -type f | wc -l)

    # Count all JSON files
    local json_count
    json_count=$(find . -maxdepth 1 -name "*.json" -type f | wc -l)

    # Count all script files
    local script_count
    script_count=$(find . -maxdepth 1 -name "*.sh" -type f | wc -l)

    echo "📈 Summary Statistics:"
    echo "   • Markdown files: $md_count"
    echo "   • JSON files: $json_count"
    echo "   • Shell scripts: $script_count"
    echo "   • High-confidence suggestions: $high_confidence"
    echo
}

# Interactive menu
show_options() {
    echo "🚀 What would you like to do?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "  [r] RUN    → Start interactive file organization"
    echo "  [d] DEMO   → Show detailed analysis without moving files"
    echo "  [h] HELP   → Explain the pattern matching system"
    echo "  [q] QUIT   → Exit without making changes"
    echo
}

# Pattern matching help
show_pattern_help() {
    echo "🧠 Smart Pattern Matching Explained:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "The system uses these intelligent patterns:"
    echo
    echo "📋 DOCUMENTATION PATTERNS:"
    echo "   AGENT*, CLAUDE* → docs/agents/"
    echo "   README*, GUIDE* → docs/architecture/"
    echo "   *ANALYSIS*, *REPORT* → docs/analysis/"
    echo
    echo "🧬 FRAMEWORK PATTERNS:"
    echo "   *MATADA* → MATADA/"
    echo "   *TRINITY* → branding/trinity/"
    echo "   *CONSCIOUSNESS* → consciousness/"
    echo
    echo "🔧 CODE PATTERNS:"
    echo "   *.py → python/"
    echo "   *.sh → scripts/"
    echo "   *.json → data/"
    echo
    echo "🗑️  CLEANUP PATTERNS:"
    echo "   *.log, *.tmp, coverage.* → DELETE (with approval)"
    echo
}

# Main interactive loop
main() {
    show_banner
    explain_system
    analyze_current_files

    while true; do
        show_options
        read -p "Your choice [r/d/h/q]: " choice
        echo

        case $choice in
            [Rr]|run)
                echo "🎉 Starting interactive file organization..."
                echo "   This would launch the full interactive script."
                echo "   Run: ./scripts/organize_root_files.sh --interactive"
                break
                ;;
            [Dd]|demo)
                echo "🎭 DEMO MODE - Detailed Analysis (no files moved):"
                echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                show_detailed_demo
                echo
                ;;
            [Hh]|help)
                show_pattern_help
                echo
                ;;
            [Qq]|quit)
                echo "👋 Goodbye! Your files remain unchanged."
                echo "   Come back when you're ready to organize!"
                break
                ;;
            *)
                echo "❌ Invalid choice: '$choice'"
                echo "   Please use: r (run), d (demo), h (help), or q (quit)"
                echo
                ;;
        esac
    done
}

# Detailed demo analysis
show_detailed_demo() {
    echo
    echo "Scanning your root directory..."
    echo

    # Real file analysis with actual pattern matching
    while IFS= read -r -d '' file; do
        local basename
        basename=$(basename "$file")

        echo "📄 $basename"

        # Pattern matching logic
        case $basename in
            *AGENT*|*agent*|AGENTS*|agents*)
                echo "   🔍 Pattern: Agent-related → Category: AGENTS"
                echo "   📁 Suggestion: docs/agents/"
                echo "   📊 Confidence: 9/10"
                ;;
            *CLAUDE*|*claude*)
                echo "   🔍 Pattern: Claude-related → Category: AGENTS"
                echo "   📁 Suggestion: docs/agents/"
                echo "   📊 Confidence: 8/10"
                ;;
            README*|*readme*|GUIDE*|*guide*)
                echo "   🔍 Pattern: Documentation → Category: ARCHITECTURE"
                echo "   📁 Suggestion: docs/architecture/"
                echo "   📊 Confidence: 8/10"
                ;;
            *MATADA*|*matada*)
                echo "   🔍 Pattern: MATADA framework → Category: MATADA"
                echo "   📁 Suggestion: MATADA/"
                echo "   📊 Confidence: 10/10 ⭐ PERFECT MATCH"
                ;;
            *ANALYSIS*|*analysis*|*REPORT*|*report*)
                echo "   🔍 Pattern: Analysis/Report → Category: ANALYSIS"
                echo "   📁 Suggestion: docs/analysis/"
                echo "   📊 Confidence: 7/10"
                ;;
            *.log|*.coverage|*tmp*|*temp*)
                echo "   🔍 Pattern: Temporary file → Category: CLEANUP"
                echo "   📁 Suggestion: DELETE"
                echo "   📊 Confidence: 9/10"
                ;;
            *.py)
                echo "   🔍 Pattern: Python script → Category: PYTHON"
                echo "   📁 Suggestion: python/"
                echo "   📊 Confidence: 6/10"
                ;;
            *.sh)
                echo "   🔍 Pattern: Shell script → Category: SCRIPTS"
                echo "   📁 Suggestion: scripts/"
                echo "   📊 Confidence: 8/10"
                ;;
            *.json)
                echo "   🔍 Pattern: JSON data → Category: DATA"
                echo "   📁 Suggestion: data/"
                echo "   📊 Confidence: 6/10"
                ;;
            *)
                echo "   🔍 Pattern: No strong match → Category: MISC"
                echo "   📁 Suggestion: docs/misc/"
                echo "   📊 Confidence: 3/10"
                ;;
        esac

        echo "   ❓ Interactive: Would ask [y]es/[s]kip/[c]ustom/[q]uit"
        echo

    done < <(find . -maxdepth 1 -type f -not -path '*/\.*' -print0 | head -z -n 8)

    echo "🎭 Demo complete! In real mode, you'd approve each move."
}

# Launch the system
main "$@"
