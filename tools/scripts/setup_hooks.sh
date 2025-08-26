#!/bin/bash
# Setup  Git Hooks

echo "🔧 Setting up  Git hooks..."

# Set git hooks path
git config core.hooksPath .githooks

echo "✅ Git hooks configured!"
echo ""
echo "The pre-commit hook will now check file organization before each commit."
echo "Files must be placed in proper directories according to CLAUDE.md guidelines."
echo ""
echo "To run the hook manually:"
echo "  .githooks/pre-commit"
echo ""
echo "To bypass the hook (not recommended):"
echo "  git commit --no-verify"
