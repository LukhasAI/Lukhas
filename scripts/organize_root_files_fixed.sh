#!/bin/bash

# 🧠 LUKHAS AI Smart File Organization System
# Interactive semantic analysis with approval workflow
# Trinity Framework compliant: ⚛️🧠🛡️

# Use simple error checking (compatible with older bash)
set -e

# Color codes (simple, compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Clean banner in project style
show_banner() {
    echo
    echo "══════════════════════════════════════════════════════════════════════════════════"
    echo "║ 🧠 LUKHAS AI - SMART FILE ORGANIZATION SYSTEM"
    echo "║ Interactive semantic analysis with confidence scoring"
    echo "║ Copyright (c) 2025 LUKHAS AI. All rights reserved."
    echo "╠══════════════════════════════════════════════════════════════════════════════════"
    echo "║ Trinity Framework: ⚛️🧠🛡️"
    echo "║ Version: 2.1.0 | Fixed Interactive Analysis"
    echo "║ Authors: LUKHAS AI Engineering Team"
    echo "╚══════════════════════════════════════════════════════════════════════════════════"
    echo
}

# Initialize arrays safely (compatible with bash 3.2+)
declare -a file_patterns_keys
declare -a file_patterns_values
declare -a destination_keys
declare -a destination_values

# Pattern definitions (safe initialization)
init_patterns() {
    # Architecture & Framework (High Priority)
    file_patterns["ARCHITECTURE"]="README_NEXT_GEN.md:10,README_TRINITY.md:10,UNIVERSAL_SYMBOL.*BLUEPRINT.md:9"
    file_patterns["MATADA"]="MATADA.*:10,matada.*:9"
    file_patterns["TRINITY"]=".*TRINITY.*:9,.*trinity.*:8"

    # Executive & Strategy
    file_patterns["EXECUTIVE"]="CEO_.*:10,INVESTOR.*:9,PROFESSIONAL_DEVELOPMENT.*:8"
    file_patterns["ROADMAP"]="ROADMAP.*:9,.*ROADMAP.*:8,.*2026.*:7,.*2030.*:7"
    file_patterns["OPENAI_COLLAB"]="OPENAI.*COLLABORATION.*:10,.*OPENAI.*VISION.*:9"

    # Development & Implementation
    file_patterns["AGENTS"]="AGENT.*:9,.*AGENT.*:8,CLAUDE.*:7"
    file_patterns["IMPLEMENTATION"]="IMPLEMENTATION.*:8,.*IMPLEMENTATION.*:7"
    file_patterns["INTEGRATION"]="INTEGRATION.*:8,.*INTEGRATION.*:7,live_.*test.*:6"
    file_patterns["API"]="API.*:8,.*API.*:7"
    file_patterns["PLANNING"]="PLANNING.*:7,.*PLAN.*:6,TODO.*:5"
    file_patterns["REPORTS"]="REPORT.*:8,.*REPORT.*:7,ANALYSIS.*:7,.*ANALYSIS.*:6"

    # Technical & Testing
    file_patterns["TESTING"]="test.*:8,.*test.*:7,pytest.*:6"
    file_patterns["SCRIPTS"]=".*sh:8,.*py:6,.*js:5"
    file_patterns["CONFIG"]=".*config.*:7,.*\.yaml:6,.*\.json:5,.*\.toml:5"
    file_patterns["DOCS"]=".*\.md:6,.*\.txt:4,LICENSE:8"
    file_patterns["UTILITIES"]=".*setup.*:5,.*install.*:5,.*format.*:5"

    # Administrative & Cleanup
    file_patterns["BACKUPS"]=".*backup.*:9,.*bkup:8"
    file_patterns["CLEANUP"]=".*tmp:10,.*temp:9,.DS_Store:10,.coverage:9,.*\.log:8"
}

# Destination directories
init_destinations() {
    destination_dirs["ARCHITECTURE"]="docs/architecture"
    destination_dirs["MATADA"]="MATADA"
    destination_dirs["TRINITY"]="docs/architecture"
    destination_dirs["EXECUTIVE"]="docs/executive"
    destination_dirs["ROADMAP"]="docs/roadmap"
    destination_dirs["OPENAI_COLLAB"]="docs/openai"
    destination_dirs["AGENTS"]="docs/agents"
    destination_dirs["IMPLEMENTATION"]="docs/implementation"
    destination_dirs["INTEGRATION"]="docs/integration"
    destination_dirs["API"]="docs/api"
    destination_dirs["PLANNING"]="docs/planning"
    destination_dirs["REPORTS"]="docs/reports"
    destination_dirs["TESTING"]="tests"
    destination_dirs["SCRIPTS"]="scripts"
    destination_dirs["CONFIG"]="config"
    destination_dirs["DOCS"]="docs"
    destination_dirs["UTILITIES"]="tools"
    destination_dirs["BACKUPS"]="archive"
    destination_dirs["CLEANUP"]="DELETE"
}

# Analyze a single file
analyze_file() {
    local file="$1"
    local max_score=0
    local best_category=""

    # Check against all patterns
    for category in "${!file_patterns[@]}"; do
        local patterns="${file_patterns[$category]}"
        IFS=',' read -ra pattern_list <<< "$patterns"

        for pattern_score in "${pattern_list[@]}"; do
            IFS=':' read -ra ps <<< "$pattern_score"
            local pattern="${ps[0]}"
            local score="${ps[1]:-3}"

            if [[ "$file" =~ $pattern ]]; then
                if (( score > max_score )); then
                    max_score=$score
                    best_category="$category"
                fi
            fi
        done
    done

    # Return results
    echo "$best_category:$max_score"
}

# Interactive file processing
process_file_interactively() {
    local file="$1"
    local analysis_result
    analysis_result=$(analyze_file "$file")

    IFS=':' read -ra result_parts <<< "$analysis_result"
    local category="${result_parts[0]}"
    local score="${result_parts[1]:-3}"

    # Get destination
    local destination=""
    if [[ -n "$category" && -n "${destination_dirs[$category]:-}" ]]; then
        destination="${destination_dirs[$category]}"
    else
        destination="docs/misc"
        category="MISC"
        score=3
    fi

    echo -e "${WHITE}📄 File:${NC} ${CYAN}$file${NC}"
    echo -e "${WHITE}🎯 Category:${NC} ${YELLOW}$category${NC} (confidence: ${score}/10)"

    if [[ "$destination" == "DELETE" ]]; then
        echo -e "${WHITE}🗑️  Action:${NC} ${RED}DELETE${NC} - Temporary/cleanup file"
    else
        echo -e "${WHITE}📁 Destination:${NC} ${GREEN}$destination/${NC}"
    fi
    echo

    # Interactive prompt
    while true; do
        echo -e "${WHITE}What would you like to do?${NC}"
        echo "  [y] Yes - proceed with suggestion"
        echo "  [s] Skip this file"
        echo "  [c] Choose custom destination"
        echo "  [q] Quit organization"
        echo

        read -p "Your choice [y/s/c/q]: " choice

        case $choice in
            [Yy]|yes)
                if [[ "$destination" == "DELETE" ]]; then
                    echo -e "${GREEN}✅ Would DELETE: $file${NC}"
                else
                    echo -e "${GREEN}✅ Would MOVE: $file → $destination/${NC}"
                fi
                echo
                return 0
                ;;
            [Ss]|skip)
                echo -e "${YELLOW}⏭️  SKIPPED: $file${NC}"
                echo
                return 0
                ;;
            [Cc]|custom)
                read -p "Enter custom destination: " custom_dest
                echo -e "${GREEN}✅ Would MOVE: $file → $custom_dest/${NC}"
                echo
                return 0
                ;;
            [Qq]|quit)
                echo -e "${RED}❌ Organization cancelled by user${NC}"
                return 1
                ;;
            *)
                echo -e "${RED}Invalid choice: '$choice'. Please use y/s/c/q${NC}"
                echo
                ;;
        esac
    done
}

# Main interactive loop
main() {
    # Initialize
    init_patterns
    init_destinations

    show_banner

    echo "🎯 Starting Interactive File Organization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "🔍 Scanning root directory for files to organize..."
    echo

    # Get list of files to process
    local files=()
    while IFS= read -r -d '' file; do
        local basename
        basename=$(basename "$file")
        # Skip hidden files and directories
        if [[ ! "$basename" =~ ^\. ]]; then
            files+=("$basename")
        fi
    done < <(find . -maxdepth 1 -type f -print0)

    echo "📊 Found ${#files[@]} files to analyze"
    echo

    # Process each file interactively
    local processed=0
    for file in "${files[@]}"; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "${WHITE}Processing:${NC} $((processed + 1))/${#files[@]}"
        echo

        if ! process_file_interactively "$file"; then
            break
        fi

        ((processed++))
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Interactive organization complete!"
    echo "   Processed: $processed/${#files[@]} files"
    echo
}

# Handle command line arguments
if [[ "${1:-}" == "--interactive" ]]; then
    main
else
    echo "Usage: $0 --interactive"
    echo "This script requires --interactive flag for safety"
    exit 1
fi
