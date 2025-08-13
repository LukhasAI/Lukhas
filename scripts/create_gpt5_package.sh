#!/bin/bash

echo "Creating selective GPT-5 package (source code only)..."

# Create temporary directory for selective copying
temp_dir="lukhas_gpt5_temp"
rm -rf "$temp_dir"
mkdir "$temp_dir"

# Copy only essential source files and directories
echo "Copying core source files..."

# Main project files
cp *.py "$temp_dir/" 2>/dev/null || true
cp *.md "$temp_dir/" 2>/dev/null || true
cp *.yml "$temp_dir/" 2>/dev/null || true
cp *.yaml "$temp_dir/" 2>/dev/null || true
cp *.json "$temp_dir/" 2>/dev/null || true
cp *.txt "$temp_dir/" 2>/dev/null || true
cp Dockerfile* "$temp_dir/" 2>/dev/null || true
cp Makefile "$temp_dir/" 2>/dev/null || true
cp *.sh "$temp_dir/" 2>/dev/null || true

# Copy source directories (excluding heavy ones)
for dir in agents api bio consciousness core identity memory quantum branding governance monitoring modulation; do
    if [ -d "$dir" ]; then
        echo "Copying $dir..."
        cp -r "$dir" "$temp_dir/"
        # Remove any __pycache__ directories
        find "$temp_dir/$dir" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$temp_dir/$dir" -name "*.pyc" -delete 2>/dev/null || true
    fi
done

# Copy essential config directories
for dir in .github .copilot_notes configs; do
    if [ -d "$dir" ]; then
        echo "Copying $dir..."
        cp -r "$dir" "$temp_dir/"
    fi
done

# Create the zip file from the temp directory
echo "Creating zip file..."
cd "$temp_dir"
zip -r "../lukhas_gpt5_clean.zip" . -x "*.pyc" "*/__pycache__/*"
cd ..

# Clean up
rm -rf "$temp_dir"

# Show results
echo "Package created: lukhas_gpt5_clean.zip"
ls -lh lukhas_gpt5_clean.zip
echo "Done!"
