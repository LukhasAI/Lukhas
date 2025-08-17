#!/bin/bash
# Script to organize root directory files in LUKHAS repository
# Created: 2025-08-17

set -e

echo "🧹 LUKHAS Root Directory Organization"
echo "====================================="

# Create archive directory with timestamp
ARCHIVE_DIR="$HOME/LOCAL-REPOS/lukhas-archive/2025-08-17-root-cleanup"
mkdir -p "$ARCHIVE_DIR"

# Count files before
INITIAL_COUNT=$(ls -1 *.* 2>/dev/null | wc -l | tr -d ' ')
echo "📊 Initial root files: $INITIAL_COUNT"

# Essential files that MUST stay in root
ESSENTIAL_FILES=(
    "README.md"
    "LICENSE"
    "CLAUDE.md"
    "Makefile"
    "setup.py"
    "pyproject.toml"
    "requirements.txt"
    "pytest.ini"
    "pyrightconfig.json"
    "lukhas_config.yaml"
    "main.py"
    "lukhas.py"
    ".gitignore"
    ".env"
    ".env.example"
    "docker-compose.yml"
    "Dockerfile"
    "package.json"
    "package-lock.json"
    "pip-constraints.txt"
    "CODEOWNERS"
)

# Function to check if file should stay in root
should_stay_in_root() {
    local file=$1
    for essential in "${ESSENTIAL_FILES[@]}"; do
        if [[ "$file" == "$essential" ]]; then
            return 0
        fi
    done
    return 1
}

# 1. Move Docker-related files to docker/ (except docker-compose.yml)
echo ""
echo "📦 Organizing Docker files..."
mkdir -p docker
for file in Dockerfile.*; do
    if [[ -f "$file" && "$file" != "Dockerfile" ]]; then
        echo "  Moving $file → docker/"
        git mv "$file" docker/ 2>/dev/null || mv "$file" docker/
    fi
done

# 2. Move configuration files to config/
echo ""
echo "⚙️ Organizing configuration files..."
if [[ -f "modulation_policy.yaml" ]]; then
    echo "  Moving modulation_policy.yaml → config/"
    git mv "modulation_policy.yaml" config/ 2>/dev/null || mv "modulation_policy.yaml" config/
fi

# 3. Move temporary session files to archive
echo ""
echo "📋 Archiving temporary session files..."
for pattern in "2025-08-*.txt" "DREAM*.md" "Dream*.md" "*_HANDOFF*.md"; do
    for file in $pattern; do
        if [[ -f "$file" ]]; then
            echo "  Archiving $file → $ARCHIVE_DIR/"
            mv "$file" "$ARCHIVE_DIR/"
        fi
    done
done

# 4. Move organization/consolidation reports to docs/
echo ""
echo "📄 Organizing documentation..."
mkdir -p docs/organization
for file in *ORGANIZATION*.md *CONSOLIDATION*.md *VOCABULARY*.md; do
    if [[ -f "$file" && "$file" != "README.md" ]]; then
        echo "  Moving $file → docs/organization/"
        git mv "$file" docs/organization/ 2>/dev/null || mv "$file" docs/organization/
    fi
done

# 5. Move backup directories to archive
echo ""
echo "💾 Moving backups to archive..."
for dir in *backup* *archive* *old*; do
    if [[ -d "$dir" ]]; then
        echo "  Moving $dir → $ARCHIVE_DIR/"
        mv "$dir" "$ARCHIVE_DIR/"
    fi
done

# 6. Move scattered Python scripts to appropriate locations
echo ""
echo "🐍 Organizing Python scripts..."
if [[ -f "consolidate_vocabularies_safely.py" ]]; then
    echo "  Moving consolidate_vocabularies_safely.py → scripts/"
    git mv "consolidate_vocabularies_safely.py" scripts/ 2>/dev/null || mv "consolidate_vocabularies_safely.py" scripts/
fi

# 7. Move test result files to test_results/
echo ""
echo "🧪 Organizing test results..."
mkdir -p test_results
for file in *test*.json *test*.html; do
    if [[ -f "$file" ]]; then
        echo "  Moving $file → test_results/"
        mv "$file" test_results/
    fi
done

# 8. Move workspace files to config/
echo ""
echo "🖥️ Organizing workspace files..."
if [[ -f "Lukhas.code-workspace" ]]; then
    echo "  Moving Lukhas.code-workspace → config/"
    git mv "Lukhas.code-workspace" config/ 2>/dev/null || mv "Lukhas.code-workspace" config/
fi

# 9. Move empty/stub files to archive
echo ""
echo "🗑️ Archiving empty files..."
if [[ -f "matada_node_v1.json" ]] && [[ ! -s "matada_node_v1.json" ]]; then
    echo "  Archiving empty matada_node_v1.json"
    mv "matada_node_v1.json" "$ARCHIVE_DIR/"
fi

# 10. Move API templates to docs/
echo ""
echo "📖 Moving API documentation..."
if [[ -f "OPENAI_API_TEMPLATES.md" ]]; then
    echo "  Moving OPENAI_API_TEMPLATES.md → docs/"
    git mv "OPENAI_API_TEMPLATES.md" docs/ 2>/dev/null || mv "OPENAI_API_TEMPLATES.md" docs/
fi

# 11. Clean up Icon files (macOS artifacts)
echo ""
echo "🧹 Cleaning up system artifacts..."
if [[ -f "Icon" ]]; then
    echo "  Removing Icon file (macOS artifact)"
    rm -f "Icon"
fi

# 12. Move research packages to archive (they're templates)
echo ""
echo "📚 Archiving research package templates..."
for dir in LUKHAS_Innovation_Research_Package_* RESEARCH_PACK_TEMPLATE; do
    if [[ -d "$dir" ]]; then
        echo "  Moving $dir → $ARCHIVE_DIR/"
        mv "$dir" "$ARCHIVE_DIR/"
    fi
done

# 13. Move temporary evolution directories
echo ""
echo "🔄 Moving temporary directories..."
if [[ -d "Poetic_Evolution" ]]; then
    echo "  Moving Poetic_Evolution → $ARCHIVE_DIR/"
    mv "Poetic_Evolution" "$ARCHIVE_DIR/"
fi

# Count files after
FINAL_COUNT=$(ls -1 *.* 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "✅ Organization Complete!"
echo "========================"
echo "📊 Final root files: $FINAL_COUNT (reduced from $INITIAL_COUNT)"
echo "📁 Archive location: $ARCHIVE_DIR"
echo ""
echo "Essential files remaining in root:"
for file in *.* ; do
    if [[ -f "$file" ]]; then
        echo "  - $file"
    fi
done

echo ""
echo "🎯 Next steps:"
echo "  1. Review the changes with: git status"
echo "  2. Commit the reorganization: git add -A && git commit -m 'feat: Organize root directory files'"
echo "  3. Test that everything still works: make test"