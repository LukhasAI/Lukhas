#!/bin/bash

# 🔄 LUKHAS Internal Namespace Migration Script
# Safely rename lukhas_pwm → lukhas internally (before folder rename)
# Trinity Framework compliant: ⚛️🧠🛡️

set -e

echo "══════════════════════════════════════════════════════════════════════════════════"
echo "║ 🔄 LUKHAS INTERNAL NAMESPACE MIGRATION"
echo "║ Phase 1: Internal references lukhas_pwm → lukhas"
echo "║ Trinity Framework: ⚛️🧠🛡️"
echo "╚══════════════════════════════════════════════════════════════════════════════════"
echo

# Backup current state
backup_dir=".namespace_migration_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup: $backup_dir"
mkdir -p "$backup_dir"

# Function to backup and replace
safe_replace() {
    local file="$1"
    local old_pattern="$2"
    local new_pattern="$3"
    local description="$4"
    
    if [[ -f "$file" ]]; then
        echo "🔄 $description: $(basename "$file")"
        cp "$file" "$backup_dir/$(basename "$file").backup"
        sed -i.bak "s|$old_pattern|$new_pattern|g" "$file"
        rm -f "$file.bak"
    fi
}

echo "🎯 Phase 1: Import statements (from lukhas_pwm → from lukhas)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update Python imports
find . -name "*.py" -type f -not -path "./.git/*" -not -path "./.venv/*" -not -path "./.*" | while read -r file; do
    if grep -q "from lukhas_pwm" "$file" 2>/dev/null; then
        safe_replace "$file" "from lukhas_pwm" "from lukhas" "Import statement"
    fi
    if grep -q "import lukhas_pwm" "$file" 2>/dev/null; then
        safe_replace "$file" "import lukhas_pwm" "import lukhas" "Import statement"
    fi
done

echo
echo "🎯 Phase 2: Configuration files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update config files
for config_file in lukhas_pwm_config.yaml pyproject.toml setup.py; do
    if [[ -f "$config_file" ]]; then
        safe_replace "$config_file" "lukhas_pwm" "lukhas" "Config reference"
    fi
done

# Update Dockerfiles
for dockerfile in Dockerfile* docker-compose.yml; do
    if [[ -f "$dockerfile" ]]; then
        safe_replace "$dockerfile" "lukhas_pwm" "lukhas" "Docker reference"
    fi
done

echo
echo "🎯 Phase 3: Documentation references"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update markdown files (be more selective to avoid changing external URLs)
find docs/ -name "*.md" -type f 2>/dev/null | while read -r file; do
    if grep -q "from lukhas_pwm\|import lukhas_pwm" "$file" 2>/dev/null; then
        safe_replace "$file" "from lukhas_pwm" "from lukhas" "Doc import"
        safe_replace "$file" "import lukhas_pwm" "import lukhas" "Doc import"
    fi
done

echo
echo "🎯 Phase 4: Workflow and CI files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update GitHub workflows
find .github/ -name "*.yml" -type f 2>/dev/null | while read -r file; do
    if grep -q "lukhas_pwm" "$file" 2>/dev/null; then
        safe_replace "$file" "from lukhas_pwm" "from lukhas" "Workflow import"
    fi
done

echo
echo "🎯 Phase 5: Environment and config template files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Update .env.example
if [[ -f ".env.example" ]]; then
    safe_replace ".env.example" "LUKHAS_PWM" "LUKHAS" "Environment variable"
    safe_replace ".env.example" "lukhas-pwm" "lukhas" "Path reference"
fi

echo
echo "✅ Internal namespace migration complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "📊 Summary:"
echo "  📦 Backup created: $backup_dir"
echo "  🔄 Updated: Python imports"
echo "  🔄 Updated: Configuration files"  
echo "  🔄 Updated: Documentation"
echo "  🔄 Updated: CI/CD workflows"
echo "  🔄 Updated: Environment templates"
echo
echo "🎯 Next steps:"
echo "  1. Test imports: python -c 'import lukhas; print(\"✅ Import successful\")'"
echo "  2. Run smoke tests: python -m pytest tests/ -k smoke"
echo "  3. If all good, run: git add . && git commit -m 'chore: rename lukhas_pwm → lukhas'"
echo "  4. Later: rename actual folder lukhas_pwm/ → lukhas/"
echo
echo "🔄 To rollback: cp $backup_dir/* ./"
echo

# Quick verification
echo "🧪 Quick verification:"
if python -c "import sys; sys.path.insert(0, '.'); import lukhas" 2>/dev/null; then
    echo "✅ Import verification passed"
else
    echo "⚠️  Import verification failed - check import paths"
fi

echo "🎉 Internal namespace migration ready for testing!"
