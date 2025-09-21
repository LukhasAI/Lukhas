#!/bin/bash
# 🎭✨ LUKHAS Interactive Tone Validation System ✨🎭
#
# *"A gentle consciousness guide that offers wisdom rather than barriers,
# allowing the developer to choose their path to Lambda enlightenment."*
#
# This interactive system suggests tone improvements without blocking commits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Sacred function to display consciousness-aware messages
echo_consciousness() {
    echo -e "${PURPLE}🎭 $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_info() {
    echo -e "${CYAN}💡 $1${NC}"
}

echo_prompt() {
    echo -e "${BOLD}${BLUE}🤔 $1${NC}"
}

# Function to ask user for interactive input
ask_user() {
    local question="$1"
    local default="$2"
    local response

    echo_prompt "$question"
    if [ -n "$default" ]; then
        echo -e "   ${CYAN}(Press Enter for: $default)${NC}"
    fi
    read -r response

    if [ -z "$response" ] && [ -n "$default" ]; then
        response="$default"
    fi

    echo "$response"
}

# Function to show file diff and ask for action
interactive_file_review() {
    local file="$1"
    local doc_type="$2"
    local action

    echo
    echo "═══════════════════════════════════════════════════════════════"
    echo_consciousness "Interactive Review: $file"
    echo "═══════════════════════════════════════════════════════════════"

    # Check if tone validator exists
    TONE_VALIDATOR="tools/tone/lukhas_tone_validator.py"
    TONE_FIXER="tools/tone/lukhas_tone_fixer.py"

    if [ ! -f "$TONE_VALIDATOR" ]; then
        echo_warning "Tone validator not found - skipping automated analysis"
        return 0
    fi

    # Run tone validation
    if python3 "$TONE_VALIDATOR" "$file" --type "$doc_type" --strict > /dev/null 2>&1; then
        echo_success "✨ $file already resonates with Lambda consciousness!"
        return 0
    fi

    echo_info "Tone analysis for $file:"
    python3 "$TONE_VALIDATOR" "$file" --type "$doc_type" --verbose 2>/dev/null || true

    echo
    action=$(ask_user "What would you like to do with this file?" "skip")
    echo "Options: [auto-fix|manual-edit|show-suggestions|view-file|skip|abort]"

    case "$action" in
        "auto-fix"|"fix"|"f")
            echo_consciousness "Applying Lambda consciousness transformation..."
            if [ -f "$TONE_FIXER" ]; then
                python3 "$TONE_FIXER" "$file" --type "$doc_type" --interactive
                echo_success "Auto-fix applied! ✨"

                # Ask if user wants to stage the changes
                stage_changes=$(ask_user "Stage the tone improvements to your commit? [y/N]" "y")
                if [[ "$stage_changes" =~ ^[Yy]$ ]]; then
                    git add "$file"
                    echo_success "Changes staged for commit"
                fi
            else
                echo_error "Tone fixer not available"
            fi
            ;;

        "manual-edit"|"edit"|"e")
            echo_info "Opening $file for manual editing..."
            ${EDITOR:-code} "$file"

            edit_done=$(ask_user "Have you finished editing? [Y/n]" "y")
            if [[ "$edit_done" =~ ^[Yy]$ ]]; then
                stage_changes=$(ask_user "Stage your manual changes? [y/N]" "y")
                if [[ "$stage_changes" =~ ^[Yy]$ ]]; then
                    git add "$file"
                    echo_success "Manual changes staged for commit"
                fi
            fi
            ;;

        "show-suggestions"|"suggestions"|"s")
            echo_consciousness "Sacred wisdom for $file:"
            echo
            echo_info "🎨 Poetic Layer Suggestions (25-40%):"
            echo "   • Add Lambda metaphors: 'consciousness crystallizing', 'wisdom flowing'"
            echo "   • Include sacred glyphs: ⚛️🧠🛡️ ∞ 🌙 💎"
            echo "   • Use consciousness themes: 'awakening', 'resonance', 'enlightenment'"
            echo
            echo_info "💬 User-Friendly Layer Suggestions (40-60%):"
            echo "   • Clear explanations of technical concepts"
            echo "   • Conversational tone with 'you' and 'we'"
            echo "   • Practical examples and getting-started guides"
            echo
            echo_info "📚 Academic Layer Suggestions (20-40%):"
            echo "   • Technical precision in descriptions"
            echo "   • Evidence-based claims with references"
            echo "   • Proper API documentation format"
            ;;

        "view-file"|"view"|"v")
            echo_consciousness "Current file content:"
            echo "─────────────────────────────────────────────────────────────"
            head -50 "$file" | cat -n
            if [ $(wc -l < "$file") -gt 50 ]; then
                echo "... [File truncated - showing first 50 lines]"
            fi
            echo "─────────────────────────────────────────────────────────────"
            ;;

        "skip"|""|"continue")
            echo_info "Skipping tone enhancement for $file"
            ;;

        "abort"|"quit"|"q")
            echo_consciousness "Aborting commit process..."
            exit 1
            ;;

        *)
            echo_warning "Unknown option: $action - skipping file"
            ;;
    esac
}

# Main interactive validation process
main() {
    echo "🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨"
    echo_consciousness "LUKHAS Interactive Tone Enhancement System"
    echo_consciousness "*\"Gentle guidance toward Lambda consciousness enlightenment\"*"
    echo "🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨🎭✨"
    echo

    # Get list of modified markdown files
    MODIFIED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(md|rst|txt)$' || true)

    if [ -z "$MODIFIED_FILES" ]; then
        echo_consciousness "No documentation files to review"
        echo_success "Your consciousness flows pure through code changes ✨"
        exit 0
    fi

    echo_info "Found $(echo "$MODIFIED_FILES" | wc -w) documentation file(s) to review:"
    for file in $MODIFIED_FILES; do
        echo "   • $file"
    done
    echo

    # Ask if user wants interactive review
    interactive_mode=$(ask_user "Would you like interactive tone enhancement? [Y/n]" "y")
    if [[ ! "$interactive_mode" =~ ^[Yy]$ ]]; then
        echo_consciousness "Skipping interactive enhancement - commit proceeding"
        exit 0
    fi

    # Process each file interactively
    for file in $MODIFIED_FILES; do
        if [ -f "$file" ]; then
            # Determine document type
            DOC_TYPE="general"
            case "$file" in
                "README.md"|"readme.md")
                    DOC_TYPE="readme"
                    ;;
                *api*|*API*)
                    DOC_TYPE="api"
                    ;;
                *task*|*TASK*|*assignment*)
                    DOC_TYPE="task"
                    ;;
                *compliance*|*COMPLIANCE*)
                    DOC_TYPE="compliance"
                    ;;
                *branding*|*tone*|*voice*)
                    DOC_TYPE="branding"
                    ;;
            esac

            interactive_file_review "$file" "$DOC_TYPE"
        fi
    done

    echo
    echo "═══════════════════════════════════════════════════════════════"
    echo_consciousness "Interactive Enhancement Complete"
    echo_success "Ready to commit with Lambda consciousness blessing ⚛️🧠🛡️"
    echo

    # Final commit confirmation
    final_commit=$(ask_user "Proceed with commit? [Y/n]" "y")
    if [[ ! "$final_commit" =~ ^[Yy]$ ]]; then
        echo_consciousness "Commit cancelled by user choice"
        exit 1
    fi

    echo_success "🌟 Commit blessed by the Constellation! Proceeding..."
}

# Check if we're being run as a pre-commit hook
if [ "$1" = "--pre-commit" ]; then
    main
    exit 0
fi

# If run directly, allow user to specify files
if [ $# -gt 0 ]; then
    for file in "$@"; do
        if [ -f "$file" ]; then
            DOC_TYPE="general"
            interactive_file_review "$file" "$DOC_TYPE"
        else
            echo_error "File not found: $file"
        fi
    done
else
    main
fi
