#!/bin/bash

# 🧠 LUKHAS AI Smart File Organization System - SIMPLE VERSION
# Interactive semantic analysis with approval workflow  
# Trinity Framework compliant: ⚛️🧠🛡️

set -e

# Clean banner in project style
show_banner() {
    echo
    echo "══════════════════════════════════════════════════════════════════════════════════"
    echo "║ 🧠 LUKHAS AI - SMART FILE ORGANIZATION SYSTEM"
    echo "║ Interactive semantic analysis with confidence scoring"
    echo "║ Copyright (c) 2025 LUKHAS AI. All rights reserved."
    echo "╠══════════════════════════════════════════════════════════════════════════════════"
    echo "║ Trinity Framework: ⚛️🧠🛡️"
    echo "║ Version: 2.2.0 | Simple Compatible Version"
    echo "║ Authors: LUKHAS AI Engineering Team"
    echo "╚══════════════════════════════════════════════════════════════════════════════════"
    echo
}

# Simple pattern matching function
analyze_file() {
    local file="$1"
    local category="MISC"
    local score=3
    local destination="docs/misc"
    
    # Simple pattern matching with confidence scores
    case "$file" in
        *MATADA*|*matada*)
            category="MATADA"
            score=10
            destination="MATADA"
            ;;
        README*|*README*)
            category="ARCHITECTURE"
            score=8
            destination="docs/architecture"
            ;;
        AGENT*|*AGENT*|CLAUDE*|*claude*)
            category="AGENTS"
            score=9
            destination="docs/agents"
            ;;
        *TRINITY*|*trinity*)
            category="TRINITY"
            score=9
            destination="docs/architecture"
            ;;
        *IMPLEMENTATION*|*implementation*)
            category="IMPLEMENTATION"
            score=8
            destination="docs/implementation"
            ;;
        *ANALYSIS*|*analysis*|*REPORT*|*report*)
            category="REPORTS"
            score=7
            destination="docs/reports"
            ;;
        *test*|*TEST*|pytest*)
            category="TESTING"
            score=8
            destination="tests"
            ;;
        *.sh)
            category="SCRIPTS"
            score=8
            destination="scripts"
            ;;
        *.py)
            category="PYTHON"
            score=6
            destination="python"
            ;;
        *.json|*.yaml|*.toml)
            category="CONFIG"
            score=6
            destination="config"
            ;;
        *.md|*.txt)
            category="DOCS"
            score=5
            destination="docs"
            ;;
        *.log|*.tmp|*temp*|.DS_Store|.coverage*)
            category="CLEANUP"
            score=10
            destination="DELETE"
            ;;
        *backup*|*bkup*)
            category="BACKUPS"
            score=9
            destination="archive"
            ;;
    esac
    
    echo "$category:$score:$destination"
}

# Interactive file processing
process_file_interactively() {
    local file="$1"
    local analysis_result
    analysis_result=$(analyze_file "$file")
    
    IFS=':' read -ra result_parts <<< "$analysis_result"
    local category="${result_parts[0]}"
    local score="${result_parts[1]}"
    local destination="${result_parts[2]}"
    
    echo "📄 File: $file"
    echo "🎯 Category: $category (confidence: ${score}/10)"
    
    if [[ "$destination" == "DELETE" ]]; then
        echo "🗑️  Action: DELETE - Temporary/cleanup file"
    else
        echo "📁 Destination: $destination/"
    fi
    echo
    
    # Interactive prompt
    while true; do
        echo "What would you like to do?"
        echo "  [y] Yes - proceed with suggestion"
        echo "  [s] Skip this file"
        echo "  [c] Choose custom destination"
        echo "  [q] Quit organization"
        echo
        
        read -p "Your choice [y/s/c/q]: " choice
        
        case $choice in
            [Yy]|yes)
                if [[ "$destination" == "DELETE" ]]; then
                    echo "✅ Would DELETE: $file"
                else
                    echo "✅ Would MOVE: $file → $destination/"
                fi
                echo
                return 0
                ;;
            [Ss]|skip)
                echo "⏭️  SKIPPED: $file"
                echo
                return 0
                ;;
            [Cc]|custom)
                read -p "Enter custom destination: " custom_dest
                echo "✅ Would MOVE: $file → $custom_dest/"
                echo
                return 0
                ;;
            [Qq]|quit)
                echo "❌ Organization cancelled by user"
                return 1
                ;;
            *)
                echo "Invalid choice: '$choice'. Please use y/s/c/q"
                echo
                ;;
        esac
    done
}

# Main interactive loop
main() {
    show_banner
    
    echo "🎯 Starting Interactive File Organization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "🔍 Scanning root directory for files to organize..."
    echo
    
    # Get list of files to process (simple approach)
    local files
    files=$(find . -maxdepth 1 -type f ! -name ".*" -exec basename {} \; | head -10)
    
    if [[ -z "$files" ]]; then
        echo "No files found to organize."
        return 0
    fi
    
    local file_count
    file_count=$(echo "$files" | wc -l)
    echo "📊 Found $file_count files to analyze (showing first 10)"
    echo
    
    # Process each file interactively
    local processed=0
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Processing: $((processed + 1))/$file_count"
            echo
            
            if ! process_file_interactively "$file"; then
                break
            fi
            
            ((processed++))
        fi
    done <<< "$files"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Interactive organization complete!"
    echo "   Processed: $processed/$file_count files"
    echo
}

# Handle command line arguments
if [[ "${1:-}" == "--interactive" ]]; then
    main
else
    echo "Usage: $0 --interactive"
    echo "This script requires --interactive flag for safety"
    echo
    echo "🎯 What this script does:"
    echo "  1. Scans your root directory for files"
    echo "  2. Analyzes each file using smart patterns"
    echo "  3. Suggests where to move each file"
    echo "  4. Asks for your approval before any action"
    echo "  5. Shows confidence scores for each suggestion"
    echo
    echo "🛡️ Safety: Never moves files without your permission!"
    exit 1
fi
