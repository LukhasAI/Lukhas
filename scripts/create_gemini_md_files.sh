#!/bin/bash

# Script to create gemini.md files by copying from claude.me files
# This helps Gemini AI navigate the LUKHAS repository structure

echo "🤖 Creating gemini.md files for Gemini AI navigation..."

# Counter for tracking progress
count=0
total=$(find . -name "claude.me" | wc -l)

# Find all claude.me files and create corresponding gemini.md files
find . -name "claude.me" | while read claude_file; do
    # Get the directory of the claude.me file
    dir=$(dirname "$claude_file")
    
    # Create gemini.md in the same directory
    gemini_file="$dir/gemini.md"
    
    # Skip if gemini.md already exists and is newer than claude.me
    if [[ -f "$gemini_file" && "$gemini_file" -nt "$claude_file" ]]; then
        echo "⏭️  Skipping $gemini_file (already up to date)"
        continue
    fi
    
    # Copy claude.me to gemini.md with some modifications
    echo "📝 Creating $gemini_file from $claude_file"
    
    # Copy the file and make Gemini-specific modifications
    sed -e 's/slug: claude\.me/slug: gemini.md/' \
        -e 's/title: me/title: gemini/' \
        -e '1i# Gemini AI Navigation Context' \
        -e '2i*This file is optimized for Gemini AI navigation and understanding*' \
        -e '3i' \
        -e 's/claude\.me/gemini.md/g' \
        -e 's/Claude-specific/Gemini-optimized/g' \
        "$claude_file" > "$gemini_file"
    
    count=$((count + 1))
    echo "✅ Created $gemini_file ($count/$total)"
done

echo ""
echo "🎉 Completed creating gemini.md files!"
echo "📊 Processed $total claude.me files"
echo ""
echo "🚀 Next: Creating gemini.md files from lukhas_context.md files..."

# Also create gemini.md files from lukhas_context.md where claude.me doesn't exist
find . -name "lukhas_context.md" | while read context_file; do
    dir=$(dirname "$context_file")
    claude_file="$dir/claude.me"
    gemini_file="$dir/gemini.md"
    
    # Only create gemini.md if there's no claude.me and no gemini.md
    if [[ ! -f "$claude_file" && ! -f "$gemini_file" ]]; then
        echo "📝 Creating $gemini_file from $context_file (no claude.me found)"
        
        # Copy lukhas_context.md to gemini.md with modifications
        {
            echo "# Gemini AI Navigation Context"
            echo "*This file is optimized for Gemini AI navigation and understanding*"
            echo ""
            echo "---"
            echo "title: gemini"
            echo "slug: gemini.md"
            echo "source: lukhas_context.md"
            echo "optimized_for: gemini_ai"
            echo "last_updated: $(date '+%Y-%m-%d')"
            echo "---"
            echo ""
            sed -e 's/lukhas_context\.md/gemini.md/g' \
                -e 's/Claude Desktop/Gemini AI/g' \
                "$context_file"
        } > "$gemini_file"
        
        echo "✅ Created $gemini_file from lukhas_context.md"
    fi
done

echo ""
echo "🎯 Summary:"
echo "   📁 Found $total claude.me files"
echo "   🤖 Created corresponding gemini.md files"
echo "   📋 Also processed lukhas_context.md files where needed"
echo ""
echo "🧭 Gemini AI can now navigate LUKHAS using gemini.md files!"