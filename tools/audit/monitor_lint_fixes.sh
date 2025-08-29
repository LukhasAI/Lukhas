#!/bin/bash

# LUKHAS Repository Audit Monitoring Script
# Monitors lint-fix workflow completion and generates comparison reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIT_DIR="$REPO_ROOT/reports/audit"
BASELINE_FILE="$REPO_ROOT/REPOSITORY_AUDIT_BASELINE.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Create audit directory
mkdir -p "$AUDIT_DIR"

# Function to run ruff statistics
run_ruff_audit() {
    local output_file="$1"
    local label="$2"
    
    log "Running Ruff audit ($label)..."
    
    # Get statistics
    ruff check --statistics . > "$output_file" 2>&1 || true
    
    # Extract total errors
    local total_errors=$(grep -E "Found [0-9]+ errors" "$output_file" | grep -oE "[0-9]+" || echo "0")
    local fixable_errors=$(grep -E "\[.*\] [0-9]+ fixable" "$output_file" | grep -oE "[0-9]+ fixable" | grep -oE "[0-9]+" || echo "0")
    
    echo "TOTAL_ERRORS=$total_errors" >> "$output_file.summary"
    echo "FIXABLE_ERRORS=$fixable_errors" >> "$output_file.summary"
    
    success "Ruff audit complete: $total_errors total errors, $fixable_errors fixable"
}

# Function to run MyPy audit
run_mypy_audit() {
    local output_file="$1"
    local label="$2"
    
    log "Running MyPy audit ($label)..."
    
    # Run MyPy on lukhas directory (most stable)
    mypy lukhas/ --show-error-codes --ignore-missing-imports > "$output_file" 2>&1 || true
    
    # Count error types
    local total_errors=$(grep -c "error:" "$output_file" || echo "0")
    local operator_errors=$(grep -c "\[operator\]" "$output_file" || echo "0")
    local assignment_errors=$(grep -c "\[assignment\]" "$output_file" || echo "0")
    local union_attr_errors=$(grep -c "\[union-attr\]" "$output_file" || echo "0")
    
    echo "TOTAL_ERRORS=$total_errors" >> "$output_file.summary"
    echo "OPERATOR_ERRORS=$operator_errors" >> "$output_file.summary"
    echo "ASSIGNMENT_ERRORS=$assignment_errors" >> "$output_file.summary"
    echo "UNION_ATTR_ERRORS=$union_attr_errors" >> "$output_file.summary"
    
    success "MyPy audit complete: $total_errors total errors"
}

# Function to run syntax validation
run_syntax_audit() {
    local output_file="$1"
    local label="$2"
    
    log "Running syntax validation ($label)..."
    
    # Find all Python files and try to compile them
    local syntax_errors=0
    local total_files=0
    
    while IFS= read -r -d '' file; do
        ((total_files++))
        if ! python -m py_compile "$file" 2>>"$output_file"; then
            ((syntax_errors++))
            echo "SYNTAX_ERROR: $file" >> "$output_file"
        fi
    done < <(find lukhas/ candidate/ -name "*.py" -print0 2>/dev/null || true)
    
    echo "TOTAL_FILES=$total_files" >> "$output_file.summary"
    echo "SYNTAX_ERRORS=$syntax_errors" >> "$output_file.summary"
    
    if [ "$syntax_errors" -eq 0 ]; then
        success "Syntax validation complete: All $total_files files compile successfully"
    else
        warning "Syntax validation complete: $syntax_errors files have syntax errors"
    fi
}

# Function to generate comparison report
generate_comparison() {
    local pre_ruff="$AUDIT_DIR/pre_fix_ruff.txt.summary"
    local post_ruff="$AUDIT_DIR/post_fix_ruff.txt.summary"
    local pre_mypy="$AUDIT_DIR/pre_fix_mypy.txt.summary"
    local post_mypy="$AUDIT_DIR/post_fix_mypy.txt.summary"
    
    if [[ -f "$pre_ruff" && -f "$post_ruff" ]]; then
        log "Generating before/after comparison..."
        
        # Read values
        local pre_total=$(grep "TOTAL_ERRORS" "$pre_ruff" | cut -d'=' -f2)
        local post_total=$(grep "TOTAL_ERRORS" "$post_ruff" | cut -d'=' -f2)
        local pre_fixable=$(grep "FIXABLE_ERRORS" "$pre_ruff" | cut -d'=' -f2)
        local post_fixable=$(grep "FIXABLE_ERRORS" "$post_ruff" | cut -d'=' -f2)
        
        # Calculate improvements
        local total_improvement=$((pre_total - post_total))
        local fixable_improvement=$((pre_fixable - post_fixable))
        local improvement_percentage=$(( (total_improvement * 100) / pre_total ))
        
        # Generate report
        cat > "$AUDIT_DIR/comparison_report.md" << EOF
# 📊 LUKHAS Repository Audit - Before/After Comparison

**Date**: $(date)
**Audit Type**: Post lint-fix workflow comparison

## 🎯 Overall Improvement

### Ruff Lint Results
- **Before**: ${pre_total:=0} total errors
- **After**: ${post_total:=0} total errors  
- **Improvement**: ${total_improvement:=0} errors fixed (${improvement_percentage:=0}% reduction)

### Auto-Fix Results
- **Before**: ${pre_fixable:=0} fixable errors
- **After**: ${post_fixable:=0} fixable errors
- **Fixed**: ${fixable_improvement:=0} auto-fixes applied

## 📈 Quality Metrics

### Success Rate
- **Error Reduction**: ${improvement_percentage:=0}%
- **Fix Efficiency**: $((fixable_improvement * 100 / pre_fixable))% of fixable errors resolved

### Remaining Work
- **Manual Review Needed**: ${post_total:=0} remaining errors
- **Focus Areas**: $(head -10 "$AUDIT_DIR/post_fix_ruff.txt" | grep -oE "^[[:space:]]*[0-9]+" | head -5 | tr '\n' ',' | sed 's/,$//')

EOF
        
        success "Comparison report generated: $AUDIT_DIR/comparison_report.md"
        cat "$AUDIT_DIR/comparison_report.md"
    else
        warning "Cannot generate comparison - missing baseline or post-fix data"
    fi
}

# Main execution
main() {
    log "Starting LUKHAS Repository Audit Monitor"
    
    case "${1:-baseline}" in
        "baseline"|"pre")
            log "Running baseline audit..."
            run_ruff_audit "$AUDIT_DIR/pre_fix_ruff.txt" "baseline"
            run_mypy_audit "$AUDIT_DIR/pre_fix_mypy.txt" "baseline"  
            run_syntax_audit "$AUDIT_DIR/pre_fix_syntax.txt" "baseline"
            success "Baseline audit complete"
            ;;
            
        "post"|"after")
            log "Running post-fix audit..."
            run_ruff_audit "$AUDIT_DIR/post_fix_ruff.txt" "post-fix"
            run_mypy_audit "$AUDIT_DIR/post_fix_mypy.txt" "post-fix"
            run_syntax_audit "$AUDIT_DIR/post_fix_syntax.txt" "post-fix"
            generate_comparison
            success "Post-fix audit complete"
            ;;
            
        "compare"|"comparison")
            generate_comparison
            ;;
            
        *)
            echo "Usage: $0 [baseline|post|compare]"
            echo "  baseline  - Run pre-fix audit"
            echo "  post      - Run post-fix audit and generate comparison"
            echo "  compare   - Generate comparison from existing data"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
