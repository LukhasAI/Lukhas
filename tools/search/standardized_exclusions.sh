#!/bin/bash
# standardized_exclusions.sh - Standard exclusion patterns for all search commands
# Source this file in your shell profile or use directly in scripts

# Global exclusion patterns for find, grep, ripgrep, etc.
VENV_EXCLUDE_FIND='-not -path "*/.venv*" -not -path "*/venv*" -not -path "*/env*" -not -path "*/*_venv*" -not -path "*/*venv*" -not -path "*/.virtualenv*" -not -path "*/virtualenv*" -not -path "*/.conda*" -not -path "*/conda-env*" -not -path "*/python-env*" -not -path "*/site-packages*" -not -path "*/lib/python*"'

VENV_EXCLUDE_GREP='--exclude-dir=.venv --exclude-dir=venv --exclude-dir=env --exclude-dir=.virtualenv --exclude-dir=virtualenv --exclude-dir=.conda --exclude-dir=conda-env --exclude-dir=python-env --exclude-dir=site-packages --exclude-dir=lib'

CACHE_EXCLUDE_FIND='-not -path "*/__pycache__*" -not -path "*/.pytest_cache*" -not -path "*/.mypy_cache*" -not -path "*/.ruff_cache*" -not -path "*/node_modules*" -not -path "*/.git*"'

CACHE_EXCLUDE_GREP='--exclude-dir=__pycache__ --exclude-dir=.pytest_cache --exclude-dir=.mypy_cache --exclude-dir=.ruff_cache --exclude-dir=node_modules --exclude-dir=.git'

BUILD_EXCLUDE_FIND='-not -path "*/build*" -not -path "*/dist*" -not -path "*/*.egg-info*" -not -path "*/archive*" -not -path "*/quarantine*" -not -path "*/backup*"'

BUILD_EXCLUDE_GREP='--exclude-dir=build --exclude-dir=dist --exclude-dir=archive --exclude-dir=quarantine --exclude-dir=backup'

# Combined exclusions
ALL_EXCLUDE_FIND="$VENV_EXCLUDE_FIND $CACHE_EXCLUDE_FIND $BUILD_EXCLUDE_FIND"
ALL_EXCLUDE_GREP="$VENV_EXCLUDE_GREP $CACHE_EXCLUDE_GREP $BUILD_EXCLUDE_GREP"

# Export for use in other scripts
export VENV_EXCLUDE_FIND VENV_EXCLUDE_GREP CACHE_EXCLUDE_FIND CACHE_EXCLUDE_GREP BUILD_EXCLUDE_FIND BUILD_EXCLUDE_GREP ALL_EXCLUDE_FIND ALL_EXCLUDE_GREP

# Utility functions
clean_find() {
    eval "find . $ALL_EXCLUDE_FIND \"\$@\""
}

clean_grep() {
    eval "grep -r $ALL_EXCLUDE_GREP \"\$@\""
}

clean_count_py() {
    eval "find . -name \"*.py\" $ALL_EXCLUDE_FIND | wc -l"
}

clean_count_todos() {
    eval "grep -r \"TODO\" $ALL_EXCLUDE_GREP --include=\"*.py\" | grep -v \"# noqa.*TODO\" | wc -l"
}

clean_syntax_check() {
    eval "find . -name \"*.py\" $ALL_EXCLUDE_FIND -exec python3 -m py_compile {} \\; 2>&1 | grep -c \"Sorry:\""
}

# Examples of usage:
# clean_find -name "*.py"
# clean_grep "TODO" --include="*.py"
# clean_count_py
# clean_count_todos

# Create functions for easy access to TODO system
lukhas_todos() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    "$PROJECT_ROOT/TODO/scripts/todo_status.sh" "$@"
}

lukhas_todo_update() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    "$PROJECT_ROOT/TODO/scripts/update_todos.sh" "$@"
}

lukhas_search() {
    source "$SCRIPT_DIR/standardized_exclusions.sh"
}

echo "🧹 Standardized exclusions loaded. Available functions:"
echo "  clean_find, clean_grep, clean_count_py, clean_count_todos, clean_syntax_check"
echo "🧹 TODO system functions: lukhas_todos, lukhas_todo_update"