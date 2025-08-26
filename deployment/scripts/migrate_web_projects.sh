#!/bin/bash

# LUKHAS Web Projects Migration Script
# Purpose: Safely copy additional website projects into main workspace
# Date: August 18, 2025

echo "🚀 LUKHAS Web Projects Migration Starting..."

# Create backup timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/Users/Gonz/lukhas/.migration_backup_$TIMESTAMP"

echo "📦 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Define source and target directories
DOWNLOADS_DIR="/Users/Gonz/Downloads"
WORKSPACE_DIR="/Users/Gonz/lukhas/web_projects"

echo "📁 Migration targets:"
echo "  - LUKHAS Studio (Visual Studio Clean)"
echo "  - LUKHAS ID Website"
echo "  - Team Dashboards"
echo "  - Additional Web Interfaces"

# 1. Copy LUKHAS Studio (Visual Studio Clean)
echo "🎨 Copying LUKHAS Studio..."
if [ -d "$DOWNLOADS_DIR/lukhas_visual_studio_clean" ]; then
    cp -R "$DOWNLOADS_DIR/lukhas_visual_studio_clean" "$WORKSPACE_DIR/lukhas_studio/visual_studio_clean"
    echo "✅ LUKHAS Studio copied successfully"
else
    echo "⚠️  LUKHAS Studio not found in Downloads"
fi

# 2. Copy LUKHAS Studio V2
if [ -d "$DOWNLOADS_DIR/lukhas_visual_studio_clean 2" ]; then
    cp -R "$DOWNLOADS_DIR/lukhas_visual_studio_clean 2" "$WORKSPACE_DIR/lukhas_studio/visual_studio_clean_v2"
    echo "✅ LUKHAS Studio V2 copied successfully"
fi

# 3. Copy from Lukhas folder
if [ -d "$DOWNLOADS_DIR/Lukhas" ]; then
    echo "📂 Processing Lukhas folder contents..."

    # Copy web interfaces
    find "$DOWNLOADS_DIR/Lukhas" -name "*web*" -type d | head -5 | while read dir; do
        basename_dir=$(basename "$dir")
        cp -R "$dir" "$WORKSPACE_DIR/additional_interfaces/$basename_dir"
        echo "✅ Copied: $basename_dir"
    done

    # Copy studio projects
    find "$DOWNLOADS_DIR/Lukhas" -name "*studio*" -type d | head -3 | while read dir; do
        basename_dir=$(basename "$dir")
        cp -R "$dir" "$WORKSPACE_DIR/lukhas_studio/$basename_dir"
        echo "✅ Copied: $basename_dir"
    done
fi

echo "🎉 Migration completed!"
echo "📍 New projects available in: $WORKSPACE_DIR"
echo "💾 Backup created at: $BACKUP_DIR"
