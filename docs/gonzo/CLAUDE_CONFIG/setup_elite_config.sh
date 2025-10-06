#!/bin/bash
# LUKHAS Elite Claude Code Configuration Setup
# T4/0.01% Implementation

set -e

echo "🌌 LUKHAS Elite Configuration Setup"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "lukhas_context.md" ]; then
    echo "❌ Error: Must run from ~/Lukhas root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ Running from LUKHAS root directory"
echo ""

# Backup existing .claudecode if it exists
if [ -d ".claudecode" ]; then
    echo "📦 Backing up existing .claudecode configuration..."
    mv .claudecode .claudecode.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
    echo ""
fi

# Copy elite configuration
echo "📁 Installing elite configuration..."
cp -r "$(dirname "$0")/../.claudecode" .
echo "✅ Configuration files copied"
echo ""

# Set permissions
echo "🔒 Setting permissions..."
chmod +x .claudecode/tools/*.sh 2>/dev/null || true
chmod +x .claudecode/workflows/*.py 2>/dev/null || true
echo "✅ Permissions set"
echo ""

# Create cache directory
echo "💾 Creating cache directory..."
mkdir -p .claudecode/cache
echo "✅ Cache directory created"
echo ""

# Add to .gitignore if not already there
echo "📝 Updating .gitignore..."
if [ -f ".gitignore" ]; then
    if ! grep -q ".claudecode/cache" .gitignore; then
        echo "" >> .gitignore
        echo "# Claude Code Elite Configuration Cache" >> .gitignore
        echo ".claudecode/cache/" >> .gitignore
        echo "✅ .gitignore updated"
    else
        echo "✅ .gitignore already configured"
    fi
else
    echo ".claudecode/cache/" > .gitignore
    echo "✅ .gitignore created"
fi
echo ""

# Verify critical files exist
echo "🔍 Verifying installation..."
REQUIRED_FILES=(
    ".claudecode/context.md"
    ".claudecode/constellation.yaml"
)

ALL_FOUND=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ALL_FOUND=false
    fi
done
echo ""

if [ "$ALL_FOUND" = false ]; then
    echo "❌ Installation incomplete - some files are missing"
    exit 1
fi

# Count constellation contexts
CONTEXT_COUNT=$(find . -name "lukhas_context.md" 2>/dev/null | wc -l)
echo "📚 Context Intelligence:"
echo "  Found $CONTEXT_COUNT lukhas_context.md files"
echo "  Auto-discovery enabled: YES"
echo ""

# Display configuration summary
echo "🎯 Configuration Summary:"
echo "  Framework: Constellation (8 stars)"
echo "  Architecture: MATRIZ Pipeline"
echo "  Files: 43,503 Python files"
echo "  Directories: 173 root directories"
echo "  Context files: $CONTEXT_COUNT"
echo "  Mode: Elite/T4 Implementation"
echo ""

echo "✨ Elite configuration installed successfully!"
echo ""
echo "📖 Next Steps:"
echo "  1. Run: python scripts/validate_configuration.py"
echo "  2. Review: .claudecode/README.md"
echo "  3. Read: T4_ELITE_STRATEGY.md for what to do next"
echo ""
echo "🚀 Ready to develop with constellation awareness!"
echo ""
echo "Start Claude Code with:"
echo "  claude code --config .claudecode/constellation.yaml"
echo ""
