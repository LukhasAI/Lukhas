#!/bin/bash
# Quick access script for LUKHAS TODO system
# Place this in your PATH or source it for easy access

# Get to project root
if [[ -f "pyproject.toml" && -d "TODO" ]]; then
    PROJECT_ROOT="$(pwd)"
elif [[ -f "../pyproject.toml" && -d "../TODO" ]]; then
    PROJECT_ROOT="$(cd .. && pwd)"
elif [[ -f "../../pyproject.toml" && -d "../../TODO" ]]; then
    PROJECT_ROOT="$(cd ../.. && pwd)"
else
    echo "❌ Error: Cannot find LUKHAS project root"
    return 1 2>/dev/null || exit 1
fi

# TODO status functions
lukhas_todo_status() {
    "$PROJECT_ROOT/TODO/scripts/todo_status.sh" "$@"
}

lukhas_todo_update() {
    "$PROJECT_ROOT/TODO/scripts/update_todos.sh" "$@"
}

# Convenient shortcuts
lukhas_critical() {
    lukhas_todo_status --critical
}

lukhas_summary() {
    lukhas_todo_status --summary
}

lukhas_distribution() {
    lukhas_todo_status --distribution
}

# Export functions if being sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    export -f lukhas_todo_status lukhas_todo_update lukhas_critical lukhas_summary lukhas_distribution
    echo "🎯 LUKHAS TODO functions loaded: lukhas_todo_status, lukhas_todo_update, lukhas_critical, lukhas_summary, lukhas_distribution"
fi

# If run directly, show status
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    lukhas_todo_status "$@"
fi