#!/bin/bash

# GPT-5 Package Creation Script for LUKHAS_PWM
# Removes Python cache, logs, and rebuildable files while preserving core architecture

set -e

echo "Creating GPT-5 LUKHAS_PWM package..."

# Create temporary directory for clean copy
TEMP_DIR="/tmp/lukhas_gpt5_package"
PACKAGE_NAME="LUKHAS_PWM_GPT5_$(date +%Y%m%d_%H%M%S)"
FINAL_ZIP="${PACKAGE_NAME}.zip"

# Remove existing temp directory
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo "Copying repository to temporary location..."
cp -r . "$TEMP_DIR/"

cd "$TEMP_DIR"

# Remove Python cache and compiled files
echo "Removing Python cache files..."
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove virtual environments
echo "Removing virtual environments..."
rm -rf .venv/
rm -rf venv/
rm -rf env/

# Remove Docker build artifacts
echo "Removing Docker artifacts..."
rm -f .dockerignore

# Remove large log files and test outputs
echo "Removing logs and test outputs..."
find . -type f -name "*.log" -size +1M -delete
find . -type f -name "test_results_*.txt" -delete
find . -type f -name "*.enc" -delete
rm -rf logs/
rm -rf test_metadata/
rm -rf test_results/
rm -rf transmission_bundle/

# Remove IDE and OS files
echo "Removing IDE and OS files..."
find . -name ".DS_Store" -delete
find . -name "Thumbs.db" -delete
find . -name ".vscode" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf .idea/

# Remove large dependencies that can be rebuilt
echo "Removing rebuildable dependencies..."
rm -rf node_modules/
rm -f package-lock.json

# Remove large data files but keep structure
echo "Cleaning data directories..."
find data/ -type f -size +10M -delete 2>/dev/null || true
find data_legacy/ -type f -size +10M -delete 2>/dev/null || true

# Remove large binary files
echo "Removing large binary files..."
find . -type f -size +50M -delete 2>/dev/null || true

# Keep important documentation and configs
echo "Preserving core architecture files..."
# All .md files are preserved
# All .yaml/.yml files are preserved
# All .json config files are preserved
# All Python source files are preserved
# All shell scripts are preserved

# Clean git objects but keep .git for version info
echo "Cleaning git objects..."
git gc --aggressive --prune=now 2>/dev/null || true

# Create the ZIP package
echo "Creating ZIP package..."
cd ..
zip -r "$FINAL_ZIP" lukhas_gpt5_package/ -x "*.git/objects/*" "*.git/logs/*" 2>/dev/null

# Move to original directory
mv "$FINAL_ZIP" "/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM/"

# Cleanup
rm -rf "$TEMP_DIR"

echo "GPT-5 package created: $FINAL_ZIP"
echo "Package location: /Users/agi_dev/LOCAL-REPOS/Lukhas_PWM/$FINAL_ZIP"

# Show size comparison
cd "/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM"
echo ""
echo "Size comparison:"
echo "Original repo: $(du -sh . | cut -f1)"
echo "GPT-5 package: $(du -sh $FINAL_ZIP | cut -f1)"

echo ""
echo "Package contents summary:"
unzip -l "$FINAL_ZIP" | tail -n 5

echo ""
echo "Ready for GPT-5 upload!"
