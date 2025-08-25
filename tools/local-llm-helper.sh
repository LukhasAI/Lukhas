#!/usr/bin/env bash
# LUKHAS AI Local LLM Helper - Ollama-powered linting and security
# Uses deepseek-coder:6.7b for automatic code quality checks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OLLAMA_MODEL="deepseek-coder:6.7b"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[LUKHAS-LLM]${NC} $1"
}

success() {
    echo -e "${GREEN}[LUKHAS-LLM]${NC} ✅ $1"
}

warning() {
    echo -e "${YELLOW}[LUKHAS-LLM]${NC} ⚠️  $1"
}

error() {
    echo -e "${RED}[LUKHAS-LLM]${NC} ❌ $1"
}

# Check if Ollama is running
check_ollama() {
    if ! ollama list >/dev/null 2>&1; then
        error "Ollama is not running. Please start Ollama first."
        exit 1
    fi
    
    local models_output
    models_output=$(ollama list)
    if ! echo "$models_output" | grep -q "deepseek-coder"; then
        error "Model $OLLAMA_MODEL not found. Available models:"
        echo "$models_output"
        exit 1
    fi
    success "Ollama and deepseek-coder model are available"
}

# Analyze Python file with Ollama
analyze_python_file() {
    local file="$1"
    local analysis_type="${2:-security}"
    
    log "Analyzing $file for $analysis_type issues..."
    
    local prompt=""
    case "$analysis_type" in
        "security")
            prompt="Analyze this Python code for security vulnerabilities, including SQL injection, XSS, unsafe imports, hardcoded secrets, and other security issues. Provide specific line numbers and fixes:

\`\`\`python
$(cat "$file")
\`\`\`

Format your response as:
ISSUES FOUND: [number]
[Line X] SECURITY: Description of issue
[Line Y] FIX: Suggested fix

If no issues found, respond with: NO SECURITY ISSUES FOUND"
            ;;
        "lint")
            prompt="Analyze this Python code for linting issues including PEP 8 violations, unused imports, undefined variables, type hints, docstring issues, and code quality problems:

\`\`\`python
$(cat "$file")
\`\`\`

Format your response as:
ISSUES FOUND: [number]
[Line X] STYLE: Description of issue
[Line Y] FIX: Suggested fix

If no issues found, respond with: NO LINTING ISSUES FOUND"
            ;;
        "bugs")
            prompt="Analyze this Python code for potential bugs, logic errors, edge cases, exception handling issues, and runtime problems:

\`\`\`python
$(cat "$file")
\`\`\`

Format your response as:
ISSUES FOUND: [number]
[Line X] BUG: Description of potential bug
[Line Y] FIX: Suggested fix

If no bugs found, respond with: NO BUGS FOUND"
            ;;
    esac
    
    # Use Ollama to analyze the code
    local analysis_result
    analysis_result=$(ollama run "$OLLAMA_MODEL" "$prompt" 2>/dev/null || echo "ANALYSIS_FAILED")
    
    if [[ "$analysis_result" == "ANALYSIS_FAILED" ]]; then
        error "Failed to analyze $file"
        return 1
    fi
    
    # Parse results
    if echo "$analysis_result" | grep -q "NO.*ISSUES FOUND\|NO BUGS FOUND"; then
        success "$file - No $analysis_type issues found"
        return 0
    else
        warning "$file - $analysis_type issues detected:"
        echo "$analysis_result" | head -20  # Limit output
        return 1
    fi
}

# Main function
main() {
    cd "$PROJECT_ROOT"
    
    check_ollama
    
    case "${1:-analyze}" in
        "analyze")
            log "Running comprehensive analysis on changed Python files..."
            # Get list of changed Python files
            local changed_files
            changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
            
            if [[ -z "$changed_files" ]]; then
                # If no staged files, check working directory
                changed_files=$(git diff --name-only | grep '\.py$' || true)
            fi
            
            if [[ -z "$changed_files" ]]; then
                success "No Python files to analyze"
                exit 0
            fi
            
            local issues_found=0
            while IFS= read -r file; do
                if [[ -f "$file" ]]; then
                    analyze_python_file "$file" "security" || ((issues_found++))
                    analyze_python_file "$file" "lint" || ((issues_found++))
                    analyze_python_file "$file" "bugs" || ((issues_found++))
                fi
            done <<< "$changed_files"
            
            if [[ $issues_found -gt 0 ]]; then
                warning "Found issues in $issues_found analysis(es)"
                exit 1
            else
                success "All files passed analysis"
                exit 0
            fi
            ;;
        "help"|"-h"|"--help")
            echo "LUKHAS AI Local LLM Helper - Ollama-powered linting and security"
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  analyze    - Analyze changed files for security, linting, and bugs"
            echo "  help      - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 analyze    # Analyze all changed files"
            ;;
        *)
            error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"